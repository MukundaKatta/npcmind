"""Tests for pydantic models."""

import pytest
from npcmind.models import (
    Archetype,
    BigFiveTraits,
    DialogueLine,
    MemoryEntry,
    MoodState,
    Motivation,
    NPC,
    Personality,
    Relationship,
)


class TestBigFiveTraits:
    def test_defaults(self):
        t = BigFiveTraits()
        assert t.openness == 0.5
        assert t.conscientiousness == 0.5
        assert t.extraversion == 0.5
        assert t.agreeableness == 0.5
        assert t.neuroticism == 0.5

    def test_custom_values(self):
        t = BigFiveTraits(openness=0.9, neuroticism=0.1)
        assert t.openness == 0.9
        assert t.neuroticism == 0.1

    def test_validation_bounds(self):
        with pytest.raises(Exception):
            BigFiveTraits(openness=1.5)
        with pytest.raises(Exception):
            BigFiveTraits(neuroticism=-0.1)


class TestRelationship:
    def test_disposition_ally(self):
        r = Relationship(target_id="a", target_name="A", affinity=0.8, trust=0.7, respect=0.6)
        assert r.disposition == "ally"

    def test_disposition_hostile(self):
        r = Relationship(target_id="b", target_name="B", affinity=-0.8, trust=-0.7, respect=-0.6)
        assert r.disposition == "hostile"

    def test_disposition_neutral(self):
        r = Relationship(target_id="c", target_name="C")
        assert r.disposition == "neutral"


class TestNPC:
    def test_create_basic(self):
        npc = NPC(name="Test", archetype=Archetype.MERCHANT)
        assert npc.name == "Test"
        assert npc.archetype == Archetype.MERCHANT
        assert npc.alive is True
        assert len(npc.id) == 12

    def test_personality_defaults(self):
        npc = NPC(name="X", archetype=Archetype.GUARD)
        assert npc.personality.mood == MoodState.NEUTRAL

    def test_with_relationships(self):
        rel = Relationship(target_id="p", target_name="Player", affinity=0.5)
        npc = NPC(name="Y", archetype=Archetype.SAGE, relationships={"Player": rel})
        assert npc.relationships["Player"].affinity == 0.5


class TestDialogueLine:
    def test_create(self):
        line = DialogueLine(speaker_id="npc1", speaker_name="Bob", text="Hello!")
        assert line.text == "Hello!"
        assert line.emotion == MoodState.NEUTRAL


class TestMemoryEntry:
    def test_defaults(self):
        m = MemoryEntry(summary="Something happened")
        assert m.importance == 0.5
        assert m.category == "general"
        assert len(m.id) == 12
