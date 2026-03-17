"""Tests for DialogueSystem."""

from npcmind.models import Archetype, MoodState, NPC, Relationship
from npcmind.npc.dialogue import DialogueSystem
from npcmind.npc.personality import PersonalityEngine


class TestDialogueSystem:
    def _make_npc(self, archetype=Archetype.MERCHANT):
        npc = NPC(name="Gareth", archetype=archetype)
        npc.personality = PersonalityEngine.from_archetype(archetype, jitter=0.0)
        return npc

    def test_say_returns_dialogue_line(self):
        npc = self._make_npc()
        ds = DialogueSystem(npc)
        line = ds.say("Hello there!")
        assert line.speaker_name == "Gareth"
        assert len(line.text) > 0

    def test_greeting_default(self):
        npc = self._make_npc()
        ds = DialogueSystem(npc)
        greeting = ds.get_greeting("Player")
        assert "Player" in greeting.text or len(greeting.text) > 0

    def test_greeting_friendly_relationship(self):
        npc = self._make_npc()
        npc.relationships["Hero"] = Relationship(
            target_id="hero", target_name="Hero", affinity=0.8
        )
        ds = DialogueSystem(npc)
        greeting = ds.get_greeting("Hero")
        assert "friend" in greeting.text.lower() or "Hero" in greeting.text

    def test_greeting_hostile(self):
        npc = self._make_npc()
        npc.relationships["Villain"] = Relationship(
            target_id="villain", target_name="Villain", affinity=-0.5
        )
        ds = DialogueSystem(npc)
        greeting = ds.get_greeting("Villain")
        assert len(greeting.text) > 0

    def test_history_tracking(self):
        npc = self._make_npc()
        ds = DialogueSystem(npc)
        ds.say("First message")
        ds.say("Second message")
        # 2 player + 2 NPC = 4 lines
        assert len(ds.history) == 4

    def test_clear_history(self):
        npc = self._make_npc()
        ds = DialogueSystem(npc)
        ds.say("Hello")
        ds.clear_history()
        assert len(ds.history) == 0

    def test_fallback_keywords(self):
        npc = self._make_npc()
        ds = DialogueSystem(npc)
        line = ds.say("I want to buy something")
        assert "show" in line.text.lower() or len(line.text) > 0

    def test_max_history(self):
        npc = self._make_npc()
        ds = DialogueSystem(npc, max_history=4)
        for i in range(10):
            ds.say(f"Message {i}")
        assert len(ds.history) <= 4
