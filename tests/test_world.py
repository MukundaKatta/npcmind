"""Tests for world systems: factions and schedules."""

import pytest
from npcmind.world.faction import Faction, FactionRegistry
from npcmind.world.schedule import DailySchedule, ScheduleEntry


class TestFaction:
    def test_reputation_modify(self):
        f = Faction(id="guild", name="Merchants Guild")
        new_rep = f.modify_reputation("player", 0.5)
        assert new_rep == 0.5
        assert f.get_reputation("player") == 0.5

    def test_reputation_clamped(self):
        f = Faction(id="guild", name="Guild")
        f.modify_reputation("player", 2.0)
        assert f.get_reputation("player") == 1.0

    def test_reputation_tiers(self):
        f = Faction(id="guild", name="Guild")
        f.reputation["a"] = 0.8
        f.reputation["b"] = 0.0
        f.reputation["c"] = -0.8
        assert f.reputation_tier("a") == "revered"
        assert f.reputation_tier("b") == "neutral"
        assert f.reputation_tier("c") == "hated"

    def test_allies_enemies(self):
        f = Faction(id="guild", name="Guild", allies=["temple"], enemies=["thieves"])
        assert f.is_allied_with("temple")
        assert f.is_enemy_of("thieves")
        assert not f.is_allied_with("thieves")


class TestFactionRegistry:
    def test_register_and_get(self):
        reg = FactionRegistry()
        f = Faction(id="guild", name="Guild")
        reg.register(f)
        assert reg.get("guild") is f

    def test_propagation(self):
        reg = FactionRegistry()
        guild = Faction(id="guild", name="Guild", allies=["temple"], enemies=["thieves"])
        temple = Faction(id="temple", name="Temple")
        thieves = Faction(id="thieves", name="Thieves")
        reg.register(guild)
        reg.register(temple)
        reg.register(thieves)

        reg.modify_reputation("guild", "player", 0.5)
        # Ally gets 30% of the change
        assert temple.get_reputation("player") == pytest.approx(0.15)
        # Enemy gets -30%
        assert thieves.get_reputation("player") == pytest.approx(-0.15)

    def test_remove(self):
        reg = FactionRegistry()
        reg.register(Faction(id="guild", name="Guild"))
        assert reg.remove("guild") is True
        assert reg.get("guild") is None
        assert reg.remove("nonexistent") is False


class TestSchedule:
    def test_current_activity(self):
        sched = DailySchedule.merchant_default()
        entry = sched.current_activity(10)
        assert entry is not None
        assert entry.activity == "trading"
        assert entry.location == "market"

    def test_location_at(self):
        sched = DailySchedule.guard_default()
        assert sched.location_at(12) == "streets"

    def test_is_busy(self):
        sched = DailySchedule.guard_default()
        assert sched.is_busy(15) is True  # report is not interruptible
        assert sched.is_busy(10) is False  # patrol is interruptible

    def test_add_and_remove(self):
        sched = DailySchedule()
        sched.add(ScheduleEntry(hour_start=8, hour_end=12, activity="work", location="shop"))
        assert sched.current_activity(10) is not None
        sched.remove_at(10)
        assert sched.current_activity(10) is None

    def test_unknown_hour(self):
        sched = DailySchedule()
        assert sched.location_at(5) == "unknown"
