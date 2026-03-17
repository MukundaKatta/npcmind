"""BehaviorTree - composable AI decision-making with action, condition, sequence, and selector nodes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Optional


class NodeStatus(str, Enum):
    """Result of ticking a behavior tree node."""

    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"


class BTNode(ABC):
    """Base class for all behavior tree nodes."""

    def __init__(self, name: str = "") -> None:
        self.name = name or self.__class__.__name__

    @abstractmethod
    def tick(self, context: dict[str, Any]) -> NodeStatus:
        """Execute this node and return a status."""
        ...

    def reset(self) -> None:
        """Reset any internal state (override in subclasses)."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"


class ActionNode(BTNode):
    """Leaf node that executes a callable action.

    The action receives the shared context dict and must return a NodeStatus.
    """

    def __init__(self, name: str, action: Callable[[dict[str, Any]], NodeStatus]) -> None:
        super().__init__(name)
        self.action = action

    def tick(self, context: dict[str, Any]) -> NodeStatus:
        return self.action(context)


class ConditionNode(BTNode):
    """Leaf node that tests a boolean predicate.

    Returns SUCCESS if the predicate is True, FAILURE otherwise.
    """

    def __init__(self, name: str, predicate: Callable[[dict[str, Any]], bool]) -> None:
        super().__init__(name)
        self.predicate = predicate

    def tick(self, context: dict[str, Any]) -> NodeStatus:
        return NodeStatus.SUCCESS if self.predicate(context) else NodeStatus.FAILURE


class SequenceNode(BTNode):
    """Composite that ticks children left-to-right.

    - Returns FAILURE immediately if any child fails.
    - Returns RUNNING if a child is running (resumes from that child next tick).
    - Returns SUCCESS only if all children succeed.
    """

    def __init__(self, name: str, children: Optional[list[BTNode]] = None) -> None:
        super().__init__(name)
        self.children: list[BTNode] = children or []
        self._running_index: int = 0

    def tick(self, context: dict[str, Any]) -> NodeStatus:
        for i in range(self._running_index, len(self.children)):
            status = self.children[i].tick(context)
            if status == NodeStatus.FAILURE:
                self._running_index = 0
                return NodeStatus.FAILURE
            if status == NodeStatus.RUNNING:
                self._running_index = i
                return NodeStatus.RUNNING
        self._running_index = 0
        return NodeStatus.SUCCESS

    def reset(self) -> None:
        self._running_index = 0
        for child in self.children:
            child.reset()


class SelectorNode(BTNode):
    """Composite that ticks children left-to-right.

    - Returns SUCCESS immediately if any child succeeds.
    - Returns RUNNING if a child is running (resumes from that child next tick).
    - Returns FAILURE only if all children fail.
    """

    def __init__(self, name: str, children: Optional[list[BTNode]] = None) -> None:
        super().__init__(name)
        self.children: list[BTNode] = children or []
        self._running_index: int = 0

    def tick(self, context: dict[str, Any]) -> NodeStatus:
        for i in range(self._running_index, len(self.children)):
            status = self.children[i].tick(context)
            if status == NodeStatus.SUCCESS:
                self._running_index = 0
                return NodeStatus.SUCCESS
            if status == NodeStatus.RUNNING:
                self._running_index = i
                return NodeStatus.RUNNING
        self._running_index = 0
        return NodeStatus.FAILURE

    def reset(self) -> None:
        self._running_index = 0
        for child in self.children:
            child.reset()


class InverterNode(BTNode):
    """Decorator that inverts SUCCESS <-> FAILURE. RUNNING passes through."""

    def __init__(self, name: str, child: BTNode) -> None:
        super().__init__(name)
        self.child = child

    def tick(self, context: dict[str, Any]) -> NodeStatus:
        status = self.child.tick(context)
        if status == NodeStatus.SUCCESS:
            return NodeStatus.FAILURE
        if status == NodeStatus.FAILURE:
            return NodeStatus.SUCCESS
        return NodeStatus.RUNNING

    def reset(self) -> None:
        self.child.reset()


class BehaviorTree:
    """Top-level wrapper that drives a root node."""

    def __init__(self, root: BTNode) -> None:
        self.root = root

    def tick(self, context: Optional[dict[str, Any]] = None) -> NodeStatus:
        return self.root.tick(context or {})

    def reset(self) -> None:
        self.root.reset()

    def __repr__(self) -> str:
        return f"BehaviorTree(root={self.root!r})"
