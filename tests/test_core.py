"""Tests for Npcmind."""
from src.core import Npcmind
def test_init(): assert Npcmind().get_stats()["ops"] == 0
def test_op(): c = Npcmind(); c.process(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Npcmind(); [c.process() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Npcmind(); c.process(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Npcmind(); r = c.process(); assert r["service"] == "npcmind"
