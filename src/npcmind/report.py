"""Rich-formatted NPC reports and summaries."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from npcmind.models import NPC
from npcmind.npc.personality import PersonalityEngine
from npcmind.npc.memory import NPCMemory
from npcmind.world.faction import Faction, FactionRegistry


def npc_report(npc: NPC, console: Console | None = None) -> None:
    """Print a detailed NPC report to the console."""
    c = console or Console()
    engine = PersonalityEngine(npc)

    # Header
    title = f"{npc.name}"
    if npc.title:
        title += f" - {npc.title}"
    title += f"  [{npc.archetype.value}]"

    # Personality panel
    t = npc.personality.traits
    trait_lines = [
        f"  Openness:          [cyan]{_bar(t.openness)}[/] {t.openness:.2f}",
        f"  Conscientiousness: [cyan]{_bar(t.conscientiousness)}[/] {t.conscientiousness:.2f}",
        f"  Extraversion:      [cyan]{_bar(t.extraversion)}[/] {t.extraversion:.2f}",
        f"  Agreeableness:     [cyan]{_bar(t.agreeableness)}[/] {t.agreeableness:.2f}",
        f"  Neuroticism:       [cyan]{_bar(t.neuroticism)}[/] {t.neuroticism:.2f}",
    ]
    personality_text = "\n".join(trait_lines)
    personality_text += f"\n\n  Mood: {npc.personality.mood.value} (intensity {npc.personality.mood_intensity:.1f})"
    personality_text += f"\n  Style: {npc.personality.speech_style}"
    personality_text += f"\n  Summary: {engine.describe()}"
    if npc.personality.motivations:
        personality_text += f"\n  Motivations: {', '.join(m.value for m in npc.personality.motivations)}"
    if npc.personality.values:
        personality_text += f"\n  Values: {', '.join(npc.personality.values)}"
    if npc.personality.fears:
        personality_text += f"\n  Fears: {', '.join(npc.personality.fears)}"

    c.print(Panel(personality_text, title=title, border_style="blue"))

    # Relationships table
    if npc.relationships:
        rel_table = Table(title="Relationships", show_header=True, header_style="bold magenta")
        rel_table.add_column("Name")
        rel_table.add_column("Disposition")
        rel_table.add_column("Affinity", justify="right")
        rel_table.add_column("Trust", justify="right")
        rel_table.add_column("Interactions", justify="right")
        for rel in npc.relationships.values():
            rel_table.add_row(
                rel.target_name,
                rel.disposition,
                f"{rel.affinity:+.2f}",
                f"{rel.trust:+.2f}",
                str(rel.interaction_count),
            )
        c.print(rel_table)

    # Recent memories
    if npc.memories:
        mem_table = Table(title="Recent Memories", show_header=True, header_style="bold green")
        mem_table.add_column("Time")
        mem_table.add_column("Category")
        mem_table.add_column("Summary")
        mem_table.add_column("Importance", justify="right")
        for mem in npc.memories[-10:]:
            mem_table.add_row(
                mem.timestamp.strftime("%H:%M"),
                mem.category,
                mem.summary[:60],
                f"{mem.importance:.1f}",
            )
        c.print(mem_table)

    # Status line
    status = f"Location: {npc.location} | Alive: {npc.alive}"
    if npc.faction_id:
        status += f" | Faction: {npc.faction_id}"
    c.print(f"\n  [dim]{status}[/dim]\n")


def faction_report(faction: Faction, console: Console | None = None) -> None:
    """Print a faction summary."""
    c = console or Console()
    lines = [f"  {faction.description}" if faction.description else ""]
    if faction.leader:
        lines.append(f"  Leader: {faction.leader}")
    if faction.values:
        lines.append(f"  Values: {', '.join(faction.values)}")
    if faction.allies:
        lines.append(f"  Allies: {', '.join(faction.allies)}")
    if faction.enemies:
        lines.append(f"  Enemies: {', '.join(faction.enemies)}")

    c.print(Panel("\n".join(lines), title=f"Faction: {faction.name}", border_style="yellow"))

    if faction.reputation:
        rep_table = Table(title="Reputation", show_header=True)
        rep_table.add_column("Entity")
        rep_table.add_column("Score", justify="right")
        rep_table.add_column("Tier")
        for eid, score in faction.reputation.items():
            rep_table.add_row(eid, f"{score:+.2f}", faction.reputation_tier(eid))
        c.print(rep_table)


def _bar(value: float, width: int = 20) -> str:
    filled = int(value * width)
    return "#" * filled + "-" * (width - filled)
