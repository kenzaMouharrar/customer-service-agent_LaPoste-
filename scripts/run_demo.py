import json
import sys
from pathlib import Path

from app.graph.workflow import graph


def build_initial_state(event: dict) -> dict:
    return {
        "event_id": event.get("event_id", "evt_manual_001"),
        "timestamp": event.get("timestamp", "2026-05-17T10:00:00Z"),
        "channel": event.get("channel", "email_claim"),
        "current_step": "start",
        "customer_email": event.get("customer_email", ""),
        "subject": event.get("subject", ""),
        "body": event.get("body", ""),
        "customer_context": None,
        "customer_history": None,
        "should_create_ticket": False,
        "ticket_creation_reason": "",
        "rag_documents": [],
        "rag_sources": [],
        "draft_response": None,
        "should_escalate": False,
        "escalate_reason": "",
        "escalate_to": None,
        "audit_log": [],
        "errors": [],
    }


def run_one(event_path: Path, verbose: bool = True) -> dict:
    if not event_path.exists():
        raise FileNotFoundError(f"Fichier evenement introuvable: {event_path}")

    with event_path.open("r", encoding="utf-8") as f:
        event = json.load(f)

    result = graph.invoke(build_initial_state(event))

    if verbose:
        print("\n====================================")
        print(f"Scenario: {event_path.name}")
        print("====================================")
        print(f"Decision ticket: {result['should_create_ticket']}")
        print(f"Raison ticket: {result['ticket_creation_reason']}")
        print(f"Escalade: {result['should_escalate']} -> {result['escalate_to']}")
        print(f"Motif escalade: {result['escalate_reason']}")

        print("\n--- Brouillon sujet ---")
        print(result["draft_response"].subject if result["draft_response"] else "Aucun")

        print("\n--- Brouillon corps ---")
        print(result["draft_response"].body if result["draft_response"] else "Aucun")

        print("\n--- Sources RAG ---")
        print(result["rag_sources"])

        print("\n--- Audit ---")
        for step in result["audit_log"]:
            print(step)

        if result["errors"]:
            print("\n--- Erreurs ---")
            for err in result["errors"]:
                print(err)

    return result


def print_summary_table(rows: list[dict]) -> None:
    headers = [
        "scenario",
        "ticket",
        "escalade",
        "vers",
        "source_rag",
        "steps",
        "errors",
    ]

    widths = {h: len(h) for h in headers}
    for row in rows:
        for h in headers:
            widths[h] = max(widths[h], len(str(row[h])))

    def line(sep: str = "-") -> str:
        return "+" + "+".join(sep * (widths[h] + 2) for h in headers) + "+"

    print("\n=== SUMMARY ===")
    print(line("-"))
    print(
        "| "
        + " | ".join(h.ljust(widths[h]) for h in headers)
        + " |"
    )
    print(line("-"))
    for row in rows:
        print(
            "| "
            + " | ".join(str(row[h]).ljust(widths[h]) for h in headers)
            + " |"
        )
    print(line("-"))


def run_batch(base: Path, files: list[str], verbose: bool) -> None:
    rows = []
    for name in files:
        event_path = base / name
        result = run_one(event_path, verbose=verbose)
        rows.append(
            {
                "scenario": name,
                "ticket": "YES" if result["should_create_ticket"] else "NO",
                "escalade": "YES" if result["should_escalate"] else "NO",
                "vers": result["escalate_to"] or "-",
                "source_rag": ",".join(result["rag_sources"]) if result["rag_sources"] else "-",
                "steps": len(result["audit_log"]),
                "errors": len(result["errors"]),
            }
        )

    print_summary_table(rows)


def main() -> None:
    base = Path("data/events/email_claim")
    scenario_files = [
        "event_001.json",
        "event_002_simple.json",
        "event_003_critical.json",
    ]

    # Usage:
    # uv run scripts/run_demo.py
    # uv run scripts/run_demo.py event_002_simple.json
    # uv run scripts/run_demo.py --all
    # uv run scripts/run_demo.py --summary
    if len(sys.argv) == 1:
        run_one(base / "event_001.json", verbose=True)
        return

    arg = sys.argv[1]

    if arg == "--all":
        run_batch(base, scenario_files, verbose=True)
        return

    if arg == "--summary":
        run_batch(base, scenario_files, verbose=False)
        return

    run_one(base / arg, verbose=True)


if __name__ == "__main__":
    main()