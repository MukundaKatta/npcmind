"""NPCMemory - tracks interactions, relationships, and significant events."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from npcmind.models import MemoryEntry, NPC, Relationship


class NPCMemory:
    """Manages an NPC's episodic memory and relationship tracking."""

    def __init__(self, npc: NPC, max_memories: int = 200) -> None:
        self.npc = npc
        self.max_memories = max_memories

    # ── Memory management ─────────────────────────────────────────────────

    def record(
        self,
        summary: str,
        category: str = "general",
        importance: float = 0.5,
        related_entities: Optional[list[str]] = None,
        emotional_valence: float = 0.0,
        tags: Optional[list[str]] = None,
    ) -> MemoryEntry:
        """Record a new memory and return it."""
        entry = MemoryEntry(
            summary=summary,
            category=category,
            importance=importance,
            related_entities=related_entities or [],
            emotional_valence=emotional_valence,
            tags=tags or [],
        )
        self.npc.memories.append(entry)
        self._enforce_limit()
        return entry

    def record_interaction(
        self,
        target_name: str,
        summary: str,
        importance: float = 0.5,
        emotional_valence: float = 0.0,
    ) -> MemoryEntry:
        """Convenience: record an interaction memory and update the relationship."""
        entry = self.record(
            summary=summary,
            category="interaction",
            importance=importance,
            related_entities=[target_name],
            emotional_valence=emotional_valence,
        )
        # Update relationship
        rel = self._get_or_create_relationship(target_name)
        rel.interaction_count += 1
        rel.last_interaction = datetime.now()
        # Nudge affinity based on valence
        rel.affinity = _clamp(rel.affinity + emotional_valence * 0.1, -1.0, 1.0)
        return entry

    def recall(
        self,
        category: Optional[str] = None,
        entity: Optional[str] = None,
        min_importance: float = 0.0,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the given filters, most recent first."""
        results = self.npc.memories
        if category:
            results = [m for m in results if m.category == category]
        if entity:
            results = [m for m in results if entity in m.related_entities]
        if min_importance > 0:
            results = [m for m in results if m.importance >= min_importance]
        return sorted(results, key=lambda m: m.timestamp, reverse=True)[:limit]

    def recall_about(self, entity_name: str, limit: int = 10) -> list[MemoryEntry]:
        """Retrieve all memories related to a specific entity."""
        return self.recall(entity=entity_name, limit=limit)

    def forget_least_important(self, count: int = 10) -> int:
        """Remove the N least important memories. Returns count actually removed."""
        if not self.npc.memories:
            return 0
        sorted_mem = sorted(self.npc.memories, key=lambda m: m.importance)
        to_remove = sorted_mem[:count]
        ids_to_remove = {m.id for m in to_remove}
        before = len(self.npc.memories)
        self.npc.memories = [m for m in self.npc.memories if m.id not in ids_to_remove]
        return before - len(self.npc.memories)

    # ── Relationship management ───────────────────────────────────────────

    def get_relationship(self, target_name: str) -> Optional[Relationship]:
        return self.npc.relationships.get(target_name)

    def update_relationship(
        self,
        target_name: str,
        affinity_delta: float = 0.0,
        trust_delta: float = 0.0,
        fear_delta: float = 0.0,
        respect_delta: float = 0.0,
    ) -> Relationship:
        """Adjust relationship scores by the given deltas."""
        rel = self._get_or_create_relationship(target_name)
        rel.affinity = _clamp(rel.affinity + affinity_delta, -1.0, 1.0)
        rel.trust = _clamp(rel.trust + trust_delta, -1.0, 1.0)
        rel.fear = _clamp(rel.fear + fear_delta, 0.0, 1.0)
        rel.respect = _clamp(rel.respect + respect_delta, -1.0, 1.0)
        return rel

    def list_relationships(self) -> list[Relationship]:
        return list(self.npc.relationships.values())

    # ── Internal ──────────────────────────────────────────────────────────

    def _get_or_create_relationship(self, target_name: str) -> Relationship:
        if target_name not in self.npc.relationships:
            self.npc.relationships[target_name] = Relationship(
                target_id=target_name.lower().replace(" ", "_"),
                target_name=target_name,
            )
        return self.npc.relationships[target_name]

    def _enforce_limit(self) -> None:
        if len(self.npc.memories) > self.max_memories:
            self.forget_least_important(len(self.npc.memories) - self.max_memories)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))
