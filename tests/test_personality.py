"""Tests for PersonalityEngine."""

import pytest
from npcmind.models import Archetype, MoodState, NPC
from npcmind.npc.personality import PersonalityEngine, ARCHETYPE_PROFILES


class TestArchetypeProfiles:
    def test_all_archetypes_defined(self):
        for arch in Archetype:
            assert arch in ARCHETYPE_PROFILES, f"Missing profile for {arch.value}"

    def test_twelve_archetypes(self):
        assert len(ARCHETYPE_PROFILES) >= 12

    def test_from_archetype_returns_personality(self):
        p = PersonalityEngine.from_archetype(Archetype.MERCHANT)
        assert 0.0 <= p.traits.openness <= 1.0
        assert len(p.motivations) > 0
        assert p.speech_style == "persuasive"

    def test_jitter_varies_traits(self):
        results = set()
        for _ in range(20):
            p = PersonalityEngine.from_archetype(Archetype.GUARD, jitter=0.1)
            results.add(round(p.traits.openness, 4))
        # With jitter, we should get some variation
        assert len(results) > 1


class TestMoodSystem:
    def test_apply_stimulus(self):
        npc = NPC(name="T", archetype=Archetype.FARMER)
        engine = PersonalityEngine(npc)
        engine.apply_mood_stimulus(MoodState.JOYFUL, 0.8)
        assert npc.personality.mood == MoodState.JOYFUL

    def test_neuroticism_amplifies(self):
        npc = NPC(name="T", archetype=Archetype.FARMER)
        npc.personality.traits.neuroticism = 0.9
        engine = PersonalityEngine(npc)
        engine.apply_mood_stimulus(MoodState.ANGRY, 0.4)
        assert npc.personality.mood_intensity > 0.4

    def test_tick_decays_mood(self):
        npc = NPC(name="T", archetype=Archetype.FARMER)
        npc.personality.mood = MoodState.ANGRY
        npc.personality.mood_intensity = 0.9
        engine = PersonalityEngine(npc)
        for _ in range(50):
            engine.tick_mood()
        assert npc.personality.mood == MoodState.NEUTRAL


class TestTraitQueries:
    def test_introverted(self):
        npc = NPC(name="T", archetype=Archetype.SAGE)
        npc.personality.traits.extraversion = 0.2
        engine = PersonalityEngine(npc)
        assert engine.is_introverted()

    def test_describe(self):
        npc = NPC(name="T", archetype=Archetype.BARD)
        npc.personality = PersonalityEngine.from_archetype(Archetype.BARD, jitter=0.0)
        engine = PersonalityEngine(npc)
        desc = engine.describe()
        assert isinstance(desc, str)
        assert len(desc) > 0
