"""DialogueSystem - context-aware NPC conversation with optional LLM backend."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Protocol

from npcmind.models import DialogueLine, MoodState, NPC, Relationship


class LLMBackend(Protocol):
    """Protocol for pluggable LLM providers."""

    def generate(self, system_prompt: str, user_message: str) -> str: ...


class _FallbackLLM:
    """Rule-based fallback when no LLM is configured."""

    def generate(self, system_prompt: str, user_message: str) -> str:
        # Extremely simple keyword matching; real usage should plug in an LLM
        lower = user_message.lower()
        if any(w in lower for w in ("hello", "hi", "greetings", "hey")):
            return "Well met, traveler."
        if any(w in lower for w in ("buy", "sell", "trade", "price", "wares")):
            return "Let me show you what I have."
        if any(w in lower for w in ("help", "quest", "task", "job")):
            return "I might have something for you. Listen closely."
        if any(w in lower for w in ("goodbye", "bye", "farewell")):
            return "Safe travels."
        if any(w in lower for w in ("threat", "fight", "attack", "kill")):
            return "I would not advise that."
        return "Hmm, interesting."


class DialogueSystem:
    """Manages conversation context and generates NPC dialogue lines."""

    def __init__(self, npc: NPC, llm: Optional[LLMBackend] = None, max_history: int = 20) -> None:
        self.npc = npc
        self.llm: LLMBackend = llm or _FallbackLLM()
        self.history: list[DialogueLine] = []
        self.max_history = max_history

    # ── Public API ────────────────────────────────────────────────────────

    def say(self, player_message: str, player_name: str = "Player") -> DialogueLine:
        """Generate an NPC response to the player's message."""
        # Record player line
        player_line = DialogueLine(
            speaker_id="player",
            speaker_name=player_name,
            text=player_message,
        )
        self._add_to_history(player_line)

        # Build context-aware prompt
        system_prompt = self._build_system_prompt(player_name)
        response_text = self.llm.generate(system_prompt, player_message)

        npc_line = DialogueLine(
            speaker_id=self.npc.id,
            speaker_name=self.npc.name,
            text=response_text,
            emotion=self.npc.personality.mood,
        )
        self._add_to_history(npc_line)
        return npc_line

    def get_greeting(self, target_name: str = "Player") -> DialogueLine:
        """Generate a context-appropriate greeting."""
        rel = self.npc.relationships.get(target_name)
        mood = self.npc.personality.mood

        if rel and rel.affinity > 0.5:
            text = f"Ah, {target_name}! Good to see you again, my friend."
        elif rel and rel.affinity < -0.3:
            text = f"Oh. It's you, {target_name}."
        elif mood == MoodState.JOYFUL:
            text = f"Welcome, welcome! What a fine day, {target_name}!"
        elif mood in (MoodState.ANGRY, MoodState.DISGUSTED):
            text = "What do you want?"
        elif mood == MoodState.FEARFUL:
            text = "W-who's there? Oh... it's you."
        else:
            text = f"Greetings, {target_name}."

        line = DialogueLine(
            speaker_id=self.npc.id,
            speaker_name=self.npc.name,
            text=text,
            emotion=mood,
        )
        self._add_to_history(line)
        return line

    def clear_history(self) -> None:
        self.history.clear()

    # ── Internals ─────────────────────────────────────────────────────────

    def _build_system_prompt(self, player_name: str) -> str:
        p = self.npc.personality
        parts = [
            f"You are {self.npc.name}, a {self.npc.archetype.value}.",
        ]
        if self.npc.title:
            parts.append(f"Title: {self.npc.title}.")
        if self.npc.description:
            parts.append(self.npc.description)
        parts.append(f"Speech style: {p.speech_style}.")
        parts.append(f"Current mood: {p.mood.value} (intensity {p.mood_intensity:.1f}).")
        if p.motivations:
            parts.append(f"Motivations: {', '.join(m.value for m in p.motivations)}.")
        if p.values:
            parts.append(f"Values: {', '.join(p.values)}.")

        rel = self.npc.relationships.get(player_name)
        if rel:
            parts.append(
                f"Relationship with {player_name}: {rel.disposition} "
                f"(affinity={rel.affinity:.1f}, trust={rel.trust:.1f})."
            )

        # Recent memory context
        recent = self.npc.memories[-5:] if self.npc.memories else []
        if recent:
            parts.append("Recent memories: " + "; ".join(m.summary for m in recent))

        # Dialogue history snippet
        if self.history:
            recent_lines = self.history[-6:]
            convo = " | ".join(f"{l.speaker_name}: {l.text}" for l in recent_lines)
            parts.append(f"Recent conversation: {convo}")

        parts.append("Stay in character. Keep responses concise (1-3 sentences).")
        return "\n".join(parts)

    def _add_to_history(self, line: DialogueLine) -> None:
        self.history.append(line)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
