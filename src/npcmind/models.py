"""Pydantic models for NPCMIND entities."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MoodState(str, Enum):
    """Emotional state of an NPC."""

    JOYFUL = "joyful"
    CONTENT = "content"
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    ANGRY = "angry"
    SAD = "sad"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    SURPRISED = "surprised"


class Motivation(str, Enum):
    """Core motivations that drive NPC behavior."""

    WEALTH = "wealth"
    POWER = "power"
    KNOWLEDGE = "knowledge"
    SAFETY = "safety"
    SOCIAL = "social"
    DUTY = "duty"
    FREEDOM = "freedom"
    REVENGE = "revenge"
    LOVE = "love"
    FAITH = "faith"


class Archetype(str, Enum):
    """Predefined NPC archetypes."""

    MERCHANT = "merchant"
    GUARD = "guard"
    SAGE = "sage"
    THIEF = "thief"
    HEALER = "healer"
    BLACKSMITH = "blacksmith"
    INNKEEPER = "innkeeper"
    NOBLE = "noble"
    FARMER = "farmer"
    BARD = "bard"
    PRIEST = "priest"
    RANGER = "ranger"


class BigFiveTraits(BaseModel):
    """Big Five personality traits, each on a 0.0-1.0 scale."""

    openness: float = Field(0.5, ge=0.0, le=1.0, description="Openness to experience")
    conscientiousness: float = Field(0.5, ge=0.0, le=1.0, description="Organization and dependability")
    extraversion: float = Field(0.5, ge=0.0, le=1.0, description="Sociability and assertiveness")
    agreeableness: float = Field(0.5, ge=0.0, le=1.0, description="Cooperation and trust")
    neuroticism: float = Field(0.5, ge=0.0, le=1.0, description="Emotional instability and anxiety")


class Personality(BaseModel):
    """Full personality profile for an NPC."""

    traits: BigFiveTraits = Field(default_factory=BigFiveTraits)
    mood: MoodState = MoodState.NEUTRAL
    mood_intensity: float = Field(0.5, ge=0.0, le=1.0)
    motivations: list[Motivation] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list, description="Personal values like 'honesty', 'loyalty'")
    fears: list[str] = Field(default_factory=list)
    speech_style: str = Field("neutral", description="e.g. 'formal', 'gruff', 'flowery', 'terse'")


class Relationship(BaseModel):
    """Tracks the relationship between two entities."""

    target_id: str
    target_name: str
    affinity: float = Field(0.0, ge=-1.0, le=1.0, description="How much the NPC likes the target")
    trust: float = Field(0.0, ge=-1.0, le=1.0)
    fear: float = Field(0.0, ge=0.0, le=1.0)
    respect: float = Field(0.0, ge=-1.0, le=1.0)
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list, description="e.g. 'enemy', 'friend', 'customer'")

    @property
    def disposition(self) -> str:
        """Summarize the overall disposition toward the target."""
        score = (self.affinity + self.trust + self.respect) / 3
        if score > 0.5:
            return "ally"
        if score > 0.15:
            return "friendly"
        if score > -0.15:
            return "neutral"
        if score > -0.5:
            return "unfriendly"
        return "hostile"


class DialogueLine(BaseModel):
    """A single line of dialogue."""

    speaker_id: str
    speaker_name: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)
    emotion: MoodState = MoodState.NEUTRAL
    tags: list[str] = Field(default_factory=list)


class MemoryEntry(BaseModel):
    """A single memory recorded by an NPC."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: datetime = Field(default_factory=datetime.now)
    category: str = Field("general", description="e.g. 'interaction', 'event', 'observation'")
    summary: str
    importance: float = Field(0.5, ge=0.0, le=1.0)
    related_entities: list[str] = Field(default_factory=list)
    emotional_valence: float = Field(0.0, ge=-1.0, le=1.0, description="Negative = bad memory, positive = good")
    tags: list[str] = Field(default_factory=list)


class NPC(BaseModel):
    """Top-level NPC entity combining all subsystems."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str
    archetype: Archetype
    title: Optional[str] = None
    description: str = ""
    personality: Personality = Field(default_factory=Personality)
    faction_id: Optional[str] = None
    location: str = "unknown"
    relationships: dict[str, Relationship] = Field(default_factory=dict)
    memories: list[MemoryEntry] = Field(default_factory=list)
    inventory: list[str] = Field(default_factory=list)
    stats: dict[str, float] = Field(default_factory=dict)
    alive: bool = True
    tags: list[str] = Field(default_factory=list)
