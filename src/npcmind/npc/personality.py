"""PersonalityEngine - Big Five traits, mood dynamics, and motivation system."""

from __future__ import annotations

import random
from typing import Optional

from npcmind.models import (
    Archetype,
    BigFiveTraits,
    MoodState,
    Motivation,
    NPC,
    Personality,
)

# ── Archetype templates ──────────────────────────────────────────────────────

ARCHETYPE_PROFILES: dict[Archetype, dict] = {
    Archetype.MERCHANT: {
        "traits": BigFiveTraits(openness=0.6, conscientiousness=0.8, extraversion=0.7, agreeableness=0.6, neuroticism=0.3),
        "motivations": [Motivation.WEALTH, Motivation.SOCIAL],
        "values": ["fairness", "profit", "reputation"],
        "fears": ["bankruptcy", "theft"],
        "speech_style": "persuasive",
    },
    Archetype.GUARD: {
        "traits": BigFiveTraits(openness=0.3, conscientiousness=0.8, extraversion=0.4, agreeableness=0.4, neuroticism=0.3),
        "motivations": [Motivation.DUTY, Motivation.SAFETY],
        "values": ["order", "loyalty", "discipline"],
        "fears": ["failure", "chaos"],
        "speech_style": "curt",
    },
    Archetype.SAGE: {
        "traits": BigFiveTraits(openness=0.95, conscientiousness=0.7, extraversion=0.3, agreeableness=0.6, neuroticism=0.2),
        "motivations": [Motivation.KNOWLEDGE, Motivation.DUTY],
        "values": ["truth", "wisdom", "patience"],
        "fears": ["ignorance", "lost knowledge"],
        "speech_style": "scholarly",
    },
    Archetype.THIEF: {
        "traits": BigFiveTraits(openness=0.7, conscientiousness=0.3, extraversion=0.5, agreeableness=0.2, neuroticism=0.5),
        "motivations": [Motivation.WEALTH, Motivation.FREEDOM],
        "values": ["cunning", "survival", "independence"],
        "fears": ["imprisonment", "exposure"],
        "speech_style": "sly",
    },
    Archetype.HEALER: {
        "traits": BigFiveTraits(openness=0.7, conscientiousness=0.8, extraversion=0.5, agreeableness=0.9, neuroticism=0.4),
        "motivations": [Motivation.DUTY, Motivation.LOVE],
        "values": ["compassion", "life", "service"],
        "fears": ["plague", "helplessness"],
        "speech_style": "gentle",
    },
    Archetype.BLACKSMITH: {
        "traits": BigFiveTraits(openness=0.4, conscientiousness=0.9, extraversion=0.4, agreeableness=0.5, neuroticism=0.2),
        "motivations": [Motivation.WEALTH, Motivation.DUTY],
        "values": ["craftsmanship", "hard work", "quality"],
        "fears": ["losing skill", "poverty"],
        "speech_style": "gruff",
    },
    Archetype.INNKEEPER: {
        "traits": BigFiveTraits(openness=0.6, conscientiousness=0.7, extraversion=0.85, agreeableness=0.7, neuroticism=0.3),
        "motivations": [Motivation.SOCIAL, Motivation.WEALTH],
        "values": ["hospitality", "community", "stories"],
        "fears": ["empty tavern", "bad reputation"],
        "speech_style": "warm",
    },
    Archetype.NOBLE: {
        "traits": BigFiveTraits(openness=0.5, conscientiousness=0.6, extraversion=0.7, agreeableness=0.3, neuroticism=0.4),
        "motivations": [Motivation.POWER, Motivation.SOCIAL],
        "values": ["honor", "legacy", "authority"],
        "fears": ["disgrace", "losing status"],
        "speech_style": "formal",
    },
    Archetype.FARMER: {
        "traits": BigFiveTraits(openness=0.3, conscientiousness=0.8, extraversion=0.4, agreeableness=0.7, neuroticism=0.3),
        "motivations": [Motivation.SAFETY, Motivation.DUTY],
        "values": ["hard work", "family", "land"],
        "fears": ["famine", "war"],
        "speech_style": "plain",
    },
    Archetype.BARD: {
        "traits": BigFiveTraits(openness=0.95, conscientiousness=0.3, extraversion=0.9, agreeableness=0.6, neuroticism=0.4),
        "motivations": [Motivation.SOCIAL, Motivation.FREEDOM],
        "values": ["art", "stories", "joy"],
        "fears": ["silence", "being forgotten"],
        "speech_style": "flowery",
    },
    Archetype.PRIEST: {
        "traits": BigFiveTraits(openness=0.5, conscientiousness=0.8, extraversion=0.5, agreeableness=0.8, neuroticism=0.3),
        "motivations": [Motivation.FAITH, Motivation.DUTY],
        "values": ["devotion", "mercy", "tradition"],
        "fears": ["heresy", "losing faith"],
        "speech_style": "serene",
    },
    Archetype.RANGER: {
        "traits": BigFiveTraits(openness=0.7, conscientiousness=0.6, extraversion=0.2, agreeableness=0.5, neuroticism=0.3),
        "motivations": [Motivation.FREEDOM, Motivation.SAFETY],
        "values": ["nature", "independence", "vigilance"],
        "fears": ["captivity", "destruction of wilderness"],
        "speech_style": "terse",
    },
}


class PersonalityEngine:
    """Manages NPC personality: trait resolution, mood transitions, and motivation ranking."""

    # Mood transition probabilities influenced by neuroticism
    _MOOD_DECAY_RATE = 0.05  # How fast mood drifts back toward baseline per tick

    def __init__(self, npc: NPC) -> None:
        self.npc = npc

    # ── Factory helpers ───────────────────────────────────────────────────

    @classmethod
    def from_archetype(cls, archetype: Archetype, jitter: float = 0.05) -> Personality:
        """Build a Personality from an archetype template with optional random jitter."""
        profile = ARCHETYPE_PROFILES[archetype]
        base_traits = profile["traits"]
        traits = BigFiveTraits(
            openness=_clamp(base_traits.openness + _jitter(jitter)),
            conscientiousness=_clamp(base_traits.conscientiousness + _jitter(jitter)),
            extraversion=_clamp(base_traits.extraversion + _jitter(jitter)),
            agreeableness=_clamp(base_traits.agreeableness + _jitter(jitter)),
            neuroticism=_clamp(base_traits.neuroticism + _jitter(jitter)),
        )
        return Personality(
            traits=traits,
            motivations=list(profile["motivations"]),
            values=list(profile["values"]),
            fears=list(profile["fears"]),
            speech_style=profile["speech_style"],
        )

    # ── Mood system ───────────────────────────────────────────────────────

    def apply_mood_stimulus(self, mood: MoodState, intensity: float = 0.5) -> None:
        """Apply an external mood stimulus. High neuroticism amplifies the effect."""
        amplifier = 1.0 + self.npc.personality.traits.neuroticism * 0.5
        effective_intensity = min(1.0, intensity * amplifier)
        # If stimulus is strong enough, change mood outright
        if effective_intensity > self.npc.personality.mood_intensity:
            self.npc.personality.mood = mood
            self.npc.personality.mood_intensity = effective_intensity

    def tick_mood(self) -> None:
        """Decay mood intensity toward neutral over time."""
        decay = self._MOOD_DECAY_RATE * (1.0 - self.npc.personality.traits.neuroticism * 0.5)
        self.npc.personality.mood_intensity = max(0.0, self.npc.personality.mood_intensity - decay)
        if self.npc.personality.mood_intensity < 0.1:
            self.npc.personality.mood = MoodState.NEUTRAL
            self.npc.personality.mood_intensity = 0.1

    # ── Trait queries ─────────────────────────────────────────────────────

    def is_introverted(self) -> bool:
        return self.npc.personality.traits.extraversion < 0.4

    def is_agreeable(self) -> bool:
        return self.npc.personality.traits.agreeableness > 0.6

    def is_neurotic(self) -> bool:
        return self.npc.personality.traits.neuroticism > 0.6

    def dominant_motivation(self) -> Optional[Motivation]:
        """Return the NPC's primary motivation, or None if empty."""
        if self.npc.personality.motivations:
            return self.npc.personality.motivations[0]
        return None

    def describe(self) -> str:
        """Return a human-readable personality summary."""
        t = self.npc.personality.traits
        parts = []
        if t.openness > 0.7:
            parts.append("curious and imaginative")
        elif t.openness < 0.3:
            parts.append("practical and conventional")
        if t.conscientiousness > 0.7:
            parts.append("disciplined")
        elif t.conscientiousness < 0.3:
            parts.append("spontaneous")
        if t.extraversion > 0.7:
            parts.append("outgoing")
        elif t.extraversion < 0.3:
            parts.append("reserved")
        if t.agreeableness > 0.7:
            parts.append("compassionate")
        elif t.agreeableness < 0.3:
            parts.append("competitive")
        if t.neuroticism > 0.7:
            parts.append("emotionally volatile")
        elif t.neuroticism < 0.3:
            parts.append("emotionally stable")
        return ", ".join(parts) if parts else "unremarkable"


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def _jitter(magnitude: float) -> float:
    return random.uniform(-magnitude, magnitude)
