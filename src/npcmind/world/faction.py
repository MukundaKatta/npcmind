"""Faction system with reputation tracking."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Faction(BaseModel):
    """A faction or organization in the game world."""

    id: str
    name: str
    description: str = ""
    leader: Optional[str] = None
    values: list[str] = Field(default_factory=list)
    allies: list[str] = Field(default_factory=list, description="Faction IDs of allies")
    enemies: list[str] = Field(default_factory=list, description="Faction IDs of enemies")
    # Player reputation with this faction: -1.0 (hated) to 1.0 (revered)
    reputation: dict[str, float] = Field(
        default_factory=dict,
        description="Map of entity_id -> reputation score",
    )

    def get_reputation(self, entity_id: str) -> float:
        return self.reputation.get(entity_id, 0.0)

    def modify_reputation(self, entity_id: str, delta: float) -> float:
        current = self.reputation.get(entity_id, 0.0)
        new_val = max(-1.0, min(1.0, current + delta))
        self.reputation[entity_id] = new_val
        return new_val

    def reputation_tier(self, entity_id: str) -> str:
        score = self.get_reputation(entity_id)
        if score >= 0.75:
            return "revered"
        if score >= 0.4:
            return "honored"
        if score >= 0.1:
            return "friendly"
        if score >= -0.1:
            return "neutral"
        if score >= -0.4:
            return "unfriendly"
        if score >= -0.75:
            return "hostile"
        return "hated"

    def is_allied_with(self, faction_id: str) -> bool:
        return faction_id in self.allies

    def is_enemy_of(self, faction_id: str) -> bool:
        return faction_id in self.enemies


class FactionRegistry:
    """Central registry of all factions in the game world."""

    def __init__(self) -> None:
        self._factions: dict[str, Faction] = {}

    def register(self, faction: Faction) -> None:
        self._factions[faction.id] = faction

    def get(self, faction_id: str) -> Optional[Faction]:
        return self._factions.get(faction_id)

    def all(self) -> list[Faction]:
        return list(self._factions.values())

    def modify_reputation(self, faction_id: str, entity_id: str, delta: float) -> Optional[float]:
        """Modify reputation and propagate to allies/enemies."""
        faction = self.get(faction_id)
        if not faction:
            return None
        new_rep = faction.modify_reputation(entity_id, delta)
        # Allied factions gain a fraction of the reputation change
        for ally_id in faction.allies:
            ally = self.get(ally_id)
            if ally:
                ally.modify_reputation(entity_id, delta * 0.3)
        # Enemy factions get the opposite
        for enemy_id in faction.enemies:
            enemy = self.get(enemy_id)
            if enemy:
                enemy.modify_reputation(entity_id, -delta * 0.3)
        return new_rep

    def remove(self, faction_id: str) -> bool:
        if faction_id in self._factions:
            del self._factions[faction_id]
            return True
        return False
