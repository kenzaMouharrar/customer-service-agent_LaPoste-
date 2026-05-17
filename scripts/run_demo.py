import json
import sys
from pathlib import Path

from app.graph.workflow import graph


EVENTS = [
    Path("data/events/email_claim/event_001.json"),
    Path("data/events/email_claim/event_002_simple.json"),
    Path("data/events/email_claim/event_003_critical.json"),
    Path("data/events/email_general/event_004_general.json"),
    Path("data/events/forms/event_005_ticket.json"),
    Path("data/events/calls/event_006_call.json"),
    Path("data/events/email_general/event_007_info.json"),
]


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


def infer_event_type(event: dict) -> str:
    if event.get("event_type"):
        return event["event_type"]

    channel = event.get("channel", "")
    body = (event.get("body") or "").lower()

    if channel == "call":
        return "appel"
    if channel == "email_claim":
        return "mail_reclamation"
    if channel == "email_general":
        if "horaire" in body or "information" in body or "renseignement" in body:
            return "demande_info"
        return "mail_general"
    if channel == "form":
        return "ticket"
    return "inconnu"


def run_one(event_path: Path, verbose: bool = True) -> tuple[dict, dict]:
    if not event_path.exists():
        raise FileNotFoundError(f"Fichier evenement introuvable: {event_path}")

    print(f"DEBUG: lecture de {event_path}", flush=True)

    with event_path.open("r", encoding="utf-8") as f:
        event = json.load(f)

    print("DEBUG: avant graph.invoke", flush=True)
    result = graph.invoke(build_initial_state(event))
    print("DEBUG: apres graph.invoke", flush=True)

    event_type = infer_event_type(event)

    if verbose:
        print("\n====================================", flush=True)
        print(f"Scenario: {event_path.name}", flush=True)
        print("====================================", flush=True)
        print(f"Type evenement: {event_type}", flush=True)
        print(f"Decision ticket: {result['should_create_ticket']}", flush=True)
        print(f"Raison ticket: {result['ticket_creation_reason']}", flush=True)
        print(f"Escalade: {result['should_escalate']} -> {result['escalate_to']}", flush=True)
        print(f"Motif escalade: {result['escalate_reason']}", flush=True)

        print("\n--- Brouillon sujet ---", flush=True)
        print(result["draft_response"].subject if result["draft_response"] else "Aucun", flush=True)

        print("\n--- Brouillon corps ---", flush=True)
        print(result["draft_response"].body if result["draft_response"] else "Aucun", flush=True)

        print("\n--- Sources RAG ---", flush=True)
        print(result["rag_sources"], flush=True)

        print("\n--- Audit ---", flush=True)
        for step in result["audit_log"]:
            print(step, flush=True)

        if result["errors"]:
            print("\n--- Erreurs ---", flush=True)
            for err in result["errors"]:
                print(err, flush=True)

    event["event_type_resolved"] = event_type
    return result, event


def print_summary_table(rows: list[dict]) -> None:
    headers = [
        "scenario",
        "type_evenement",
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

    print("\n=== SUMMARY ===", flush=True)
    print(line("-"), flush=True)
    print("| " + " | ".join(h.ljust(widths[h]) for h in headers) + " |", flush=True)
    print(line("-"), flush=True)
    for row in rows:
        print("| " + " | ".join(str(row[h]).ljust(widths[h]) for h in headers) + " |", flush=True)
    print(line("-"), flush=True)


def run_batch(files: list[Path], verbose: bool) -> None:
    rows = []
    for event_path in files:
        result, event = run_one(event_path, verbose=verbose)
        rows.append(
            {
                "scenario": event_path.name,
                "type_evenement": event.get("event_type_resolved", "inconnu"),
                "ticket": "YES" if result["should_create_ticket"] else "NO",
                "escalade": "YES" if result["should_escalate"] else "NO",
                "vers": result["escalate_to"] or "-",
                "source_rag": ",".join(result["rag_sources"]) if result["rag_sources"] else "-",
                "steps": len(result["audit_log"]),
                "errors": len(result["errors"]),
            }
        )

    print_summary_table(rows)


def resolve_event_path(arg: str) -> Path:
    direct_path = Path(arg)
    if direct_path.exists():
        return direct_path

    search_roots = [
        Path("data/events/email_claim"),
        Path("data/events/email_general"),
        Path("data/events/forms"),
        Path("data/events/calls"),
    ]
    for root in search_roots:
        candidate = root / arg
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"Evenement introuvable: {arg}. "
        f"Essaye un chemin complet ou l'un des fichiers connus."
    )


def main() -> None:
    if len(sys.argv) == 1:
        run_one(EVENTS[0], verbose=True)
        return

    arg = sys.argv[1]

    if arg == "--all":
        run_batch(EVENTS, verbose=True)
        return

    if arg == "--summary":
        run_batch(EVENTS, verbose=False)
        return

    run_one(resolve_event_path(arg), verbose=True)


if __name__ == "__main__":
    main()