"""Tests for BehaviorTree system."""

from npcmind.npc.behavior import (
    ActionNode,
    BehaviorTree,
    ConditionNode,
    InverterNode,
    NodeStatus,
    SelectorNode,
    SequenceNode,
)


class TestActionNode:
    def test_success(self):
        node = ActionNode("do_thing", lambda ctx: NodeStatus.SUCCESS)
        assert node.tick({}) == NodeStatus.SUCCESS

    def test_failure(self):
        node = ActionNode("fail_thing", lambda ctx: NodeStatus.FAILURE)
        assert node.tick({}) == NodeStatus.FAILURE

    def test_modifies_context(self):
        def action(ctx):
            ctx["done"] = True
            return NodeStatus.SUCCESS

        ctx = {}
        ActionNode("setter", action).tick(ctx)
        assert ctx["done"] is True


class TestConditionNode:
    def test_true(self):
        node = ConditionNode("check", lambda ctx: ctx.get("health", 0) > 50)
        assert node.tick({"health": 100}) == NodeStatus.SUCCESS

    def test_false(self):
        node = ConditionNode("check", lambda ctx: ctx.get("health", 0) > 50)
        assert node.tick({"health": 10}) == NodeStatus.FAILURE


class TestSequenceNode:
    def test_all_succeed(self):
        children = [
            ActionNode("a", lambda ctx: NodeStatus.SUCCESS),
            ActionNode("b", lambda ctx: NodeStatus.SUCCESS),
        ]
        seq = SequenceNode("seq", children)
        assert seq.tick({}) == NodeStatus.SUCCESS

    def test_one_fails(self):
        children = [
            ActionNode("a", lambda ctx: NodeStatus.SUCCESS),
            ActionNode("b", lambda ctx: NodeStatus.FAILURE),
            ActionNode("c", lambda ctx: NodeStatus.SUCCESS),
        ]
        seq = SequenceNode("seq", children)
        assert seq.tick({}) == NodeStatus.FAILURE

    def test_running(self):
        call_count = {"n": 0}

        def running_action(ctx):
            call_count["n"] += 1
            if call_count["n"] < 3:
                return NodeStatus.RUNNING
            return NodeStatus.SUCCESS

        children = [
            ActionNode("a", lambda ctx: NodeStatus.SUCCESS),
            ActionNode("b", running_action),
        ]
        seq = SequenceNode("seq", children)
        assert seq.tick({}) == NodeStatus.RUNNING
        assert seq.tick({}) == NodeStatus.RUNNING
        assert seq.tick({}) == NodeStatus.SUCCESS


class TestSelectorNode:
    def test_first_succeeds(self):
        children = [
            ActionNode("a", lambda ctx: NodeStatus.SUCCESS),
            ActionNode("b", lambda ctx: NodeStatus.FAILURE),
        ]
        sel = SelectorNode("sel", children)
        assert sel.tick({}) == NodeStatus.SUCCESS

    def test_all_fail(self):
        children = [
            ActionNode("a", lambda ctx: NodeStatus.FAILURE),
            ActionNode("b", lambda ctx: NodeStatus.FAILURE),
        ]
        sel = SelectorNode("sel", children)
        assert sel.tick({}) == NodeStatus.FAILURE

    def test_fallback_to_second(self):
        children = [
            ActionNode("a", lambda ctx: NodeStatus.FAILURE),
            ActionNode("b", lambda ctx: NodeStatus.SUCCESS),
        ]
        sel = SelectorNode("sel", children)
        assert sel.tick({}) == NodeStatus.SUCCESS


class TestInverterNode:
    def test_inverts_success(self):
        child = ActionNode("a", lambda ctx: NodeStatus.SUCCESS)
        node = InverterNode("inv", child)
        assert node.tick({}) == NodeStatus.FAILURE

    def test_inverts_failure(self):
        child = ActionNode("a", lambda ctx: NodeStatus.FAILURE)
        node = InverterNode("inv", child)
        assert node.tick({}) == NodeStatus.SUCCESS

    def test_passes_running(self):
        child = ActionNode("a", lambda ctx: NodeStatus.RUNNING)
        node = InverterNode("inv", child)
        assert node.tick({}) == NodeStatus.RUNNING


class TestBehaviorTree:
    def test_simple_tree(self):
        root = SequenceNode("root", [
            ConditionNode("alive", lambda ctx: ctx.get("alive", False)),
            ActionNode("act", lambda ctx: NodeStatus.SUCCESS),
        ])
        bt = BehaviorTree(root)
        assert bt.tick({"alive": True}) == NodeStatus.SUCCESS
        assert bt.tick({"alive": False}) == NodeStatus.FAILURE

    def test_reset(self):
        root = SequenceNode("root", [
            ActionNode("a", lambda ctx: NodeStatus.RUNNING),
        ])
        bt = BehaviorTree(root)
        bt.tick({})
        bt.reset()
        # After reset, internal index should be 0
        assert root._running_index == 0
