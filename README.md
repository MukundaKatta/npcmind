# NPCMIND

AI Game NPC Engine -- intelligent non-player characters with personality, memory, and behavior trees.

## Features

- **Big Five Personality Model**: Each NPC has traits for openness, conscientiousness, extraversion, agreeableness, and neuroticism that shape behavior and dialogue.
- **Mood System**: Dynamic mood states with intensity decay, amplified by neuroticism.
- **12 NPC Archetypes**: Merchant, Guard, Sage, Thief, Healer, Blacksmith, Innkeeper, Noble, Farmer, Bard, Priest, Ranger -- each with unique personality profiles, motivations, and speech styles.
- **Context-Aware Dialogue**: Conversation system that incorporates personality, mood, relationships, and memory into responses. Pluggable LLM backend with a rule-based fallback.
- **Behavior Trees**: Composable decision-making with Action, Condition, Sequence, Selector, and Inverter nodes.
- **Episodic Memory**: NPCs remember interactions, events, and observations with importance-based pruning.
- **Relationship Tracking**: Affinity, trust, fear, and respect scores per entity, updated through interactions.
- **Faction & Reputation System**: Factions with allied/enemy relationships and reputation propagation.
- **Daily Schedules**: Time-based NPC routines with interruptibility flags.
- **Rich CLI**: Interactive NPC creation, chat, and reporting via the terminal.

## Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

```bash
# List all archetypes
npcmind archetypes

# Create and inspect an NPC
npcmind create "Gareth" --archetype merchant --title "Master Trader"

# Chat with an NPC
npcmind chat "Elara" --archetype sage

# Run a demo
npcmind demo
```

## Project Structure

```
src/npcmind/
  models.py          # Pydantic models: NPC, Personality, Relationship, etc.
  cli.py             # Click CLI commands
  report.py          # Rich-formatted NPC reports
  npc/
    personality.py   # PersonalityEngine, Big Five, mood, archetypes
    dialogue.py      # DialogueSystem with LLM backend protocol
    behavior.py      # BehaviorTree, Action/Condition/Sequence/Selector nodes
    memory.py        # NPCMemory: episodic memory + relationship tracking
  world/
    faction.py       # Faction registry with reputation propagation
    schedule.py      # DailySchedule for NPC routines
tests/               # Pytest test suite
```

## Using with an LLM

The `DialogueSystem` accepts any object implementing the `LLMBackend` protocol:

```python
class LLMBackend(Protocol):
    def generate(self, system_prompt: str, user_message: str) -> str: ...
```

Without an LLM, the system uses a keyword-based fallback for dialogue generation.

## Running Tests

```bash
pytest
```

## License

MIT
