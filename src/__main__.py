"""CLI for npcmind."""
import sys, json, argparse
from .core import Npcmind

def main():
    parser = argparse.ArgumentParser(description="NPCMind — AI Game NPC Engine. Dynamic NPC behavior, dialogue, and personality for game developers.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Npcmind()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.process(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"npcmind v0.1.0 — NPCMind — AI Game NPC Engine. Dynamic NPC behavior, dialogue, and personality for game developers.")

if __name__ == "__main__":
    main()
