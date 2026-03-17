"""Tests for NPCMemory."""

import pytest
from npcmind.models import Archetype, NPC
from npcmind.npc.memory import NPCMemory


class TestNPCMemory:
    def _make_npc(self):
        return NPC(name="Mira", archetype=Archetype.HEALER)

    def test_record(self):
        npc = self._make_npc()
        mem = NPCMemory(npc)
        entry = mem.record("Saw a dragon", category="event", importance=0.9)
        assert entry.summary == "Saw a dragon"
        assert len(npc.memories) == 1

    def test_record_interaction(self):
        npc = self._make_npc()
        mem = NPCMemory(npc)
        mem.record_interaction("Player", "Player asked for healing", emotional_valence=0.3)
        assert len(npc.memories) == 1
        assert "Player" in npc.relationships
        assert npc.relationships["Player"].interaction_count == 1
        assert npc.relationships["Player"].affinity > 0

    def test_recall_filters(self):
        npc = self._make_npc()
        mem = NPCMemory(npc)
        mem.record("Event A", category="event", importance=0.8)
        mem.record("Chat B", category="interaction", importance=0.3)
        mem.record("Event C", category="event", importance=0.9)

        events = mem.recall(category="event")
        assert len(events) == 2
        assert all(e.category == "event" for e in events)

    def test_recall_about(self):
        npc = self._make_npc()
        mem = NPCMemory(npc)
        mem.record("Met Player", related_entities=["Player"])
        mem.record("Met Goblin", related_entities=["Goblin"])
        mem.record("Traded with Player", related_entities=["Player"])

        player_memories = mem.recall_about("Player")
        assert len(player_memories) == 2

    def test_recall_min_importance(self):
        npc = self._make_npc()
        mem = NPCMemory(npc)
        mem.record("Trivial", importance=0.1)
        mem.record("Important", importance=0.8)
        result = mem.recall(min_importance=0.5)
        assert len(result) == 1
        assert result[0].summary == "Important"

    def test_forget_least_important(self):
        npc = self._make_npc()
        mem = NPCMemory(npc)
        for i in range(10):
            mem.record(f"Memory {i}", importance=i / 10)
        removed = mem.forget_least_important(5)
        assert removed == 5
        assert len(npc.memories) == 5
        # The remaining should be the more important ones
        assert all(m.importance >= 0.5 for m in npc.memories)

    def test_memory_limit(self):
        npc = self._make_npc()
        mem = NPCMemory(npc, max_memories=5)
        for i in range(10):
            mem.record(f"Memory {i}", importance=i / 10)
        assert len(npc.memories) <= 5

    def test_update_relationship(self):
        npc = self._make_npc()
        mem = NPCMemory(npc)
        rel = mem.update_relationship("Player", affinity_delta=0.3, trust_delta=0.2)
        assert rel.affinity == pytest.approx(0.3)
        assert rel.trust == pytest.approx(0.2)
        # Second update
        rel = mem.update_relationship("Player", affinity_delta=0.1)
        assert rel.affinity == pytest.approx(0.4)

    def test_list_relationships(self):
        npc = self._make_npc()
        mem = NPCMemory(npc)
        mem.update_relationship("A", affinity_delta=0.1)
        mem.update_relationship("B", affinity_delta=0.2)
        assert len(mem.list_relationships()) == 2
