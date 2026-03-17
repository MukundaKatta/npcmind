"""NPCMIND CLI - interactive NPC engine powered by Click and Rich."""

from __future__ import annotations

import click
from rich.console import Console

from npcmind.models import Archetype, NPC
from npcmind.npc.personality import PersonalityEngine
from npcmind.npc.dialogue import DialogueSystem
from npcmind.npc.memory import NPCMemory
from npcmind.report import npc_report

console = Console()


@click.group()
@click.version_option(package_name="npcmind")
def cli() -> None:
    """NPCMIND - AI Game NPC Engine."""
    pass


@cli.command()
@click.argument("name")
@click.option(
    "--archetype", "-a",
    type=click.Choice([a.value for a in Archetype], case_sensitive=False),
    default="merchant",
    help="NPC archetype",
)
@click.option("--title", "-t", default=None, help="NPC title (e.g. 'Master Blacksmith')")
@click.option("--location", "-l", default="town square", help="Starting location")
def create(name: str, archetype: str, title: str | None, location: str) -> None:
    """Create an NPC and display their profile."""
    arch = Archetype(archetype)
    personality = PersonalityEngine.from_archetype(arch)
    npc = NPC(
        name=name,
        archetype=arch,
        title=title,
        personality=personality,
        location=location,
    )
    npc_report(npc, console)


@cli.command()
def archetypes() -> None:
    """List all available NPC archetypes."""
    from rich.table import Table

    table = Table(title="NPC Archetypes", show_header=True, header_style="bold blue")
    table.add_column("Archetype")
    table.add_column("Speech Style")
    table.add_column("Motivations")
    table.add_column("Values")

    from npcmind.npc.personality import ARCHETYPE_PROFILES
    for arch, profile in ARCHETYPE_PROFILES.items():
        table.add_row(
            arch.value,
            profile["speech_style"],
            ", ".join(m.value for m in profile["motivations"]),
            ", ".join(profile["values"]),
        )
    console.print(table)


@cli.command()
@click.argument("name")
@click.option(
    "--archetype", "-a",
    type=click.Choice([a.value for a in Archetype], case_sensitive=False),
    default="merchant",
)
def chat(name: str, archetype: str) -> None:
    """Start an interactive conversation with an NPC."""
    arch = Archetype(archetype)
    personality = PersonalityEngine.from_archetype(arch)
    npc = NPC(name=name, archetype=arch, personality=personality)
    dialogue = DialogueSystem(npc)
    memory = NPCMemory(npc)

    greeting = dialogue.get_greeting()
    console.print(f"\n[bold green]{npc.name}[/]: {greeting.text}\n")

    while True:
        try:
            user_input = click.prompt(click.style("You", fg="cyan"), prompt_suffix=": ")
        except (click.Abort, EOFError):
            console.print("\n[dim]Conversation ended.[/dim]")
            break

        if user_input.lower() in ("quit", "exit", "bye"):
            farewell = dialogue.say(user_input)
            console.print(f"[bold green]{npc.name}[/]: {farewell.text}")
            memory.record_interaction("Player", f"Conversation ended. Player said: {user_input}")
            break

        response = dialogue.say(user_input)
        console.print(f"[bold green]{npc.name}[/]: {response.text}")
        memory.record_interaction("Player", f"Player said: {user_input}. NPC replied: {response.text}")

    # Show summary
    console.print()
    npc_report(npc, console)


@cli.command()
def demo() -> None:
    """Run a quick demo showing NPC creation and interaction."""
    console.print("[bold]NPCMIND Demo[/bold]\n")

    # Create NPCs
    npcs: list[NPC] = []
    for arch in [Archetype.MERCHANT, Archetype.GUARD, Archetype.SAGE, Archetype.THIEF, Archetype.BARD]:
        personality = PersonalityEngine.from_archetype(arch)
        npc = NPC(
            name=f"Demo {arch.value.title()}",
            archetype=arch,
            personality=personality,
            location="demo_town",
        )
        npcs.append(npc)

    # Show each NPC
    for npc in npcs:
        npc_report(npc, console)

    # Demonstrate dialogue
    console.print("\n[bold]--- Dialogue Demo ---[/bold]\n")
    merchant = npcs[0]
    ds = DialogueSystem(merchant)
    mem = NPCMemory(merchant)

    greeting = ds.get_greeting("Hero")
    console.print(f"[green]{merchant.name}[/]: {greeting.text}")

    for msg in ["Hello there!", "What do you have for sale?", "Goodbye!"]:
        console.print(f"[cyan]Hero[/]: {msg}")
        reply = ds.say(msg, "Hero")
        console.print(f"[green]{merchant.name}[/]: {reply.text}")
        mem.record_interaction("Hero", f"{msg} -> {reply.text}")

    console.print("\n[bold]--- Final State ---[/bold]")
    npc_report(merchant, console)


if __name__ == "__main__":
    cli()
