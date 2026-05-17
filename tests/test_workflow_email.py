from app.graph.workflow import graph


def test_email_claim_flow_generates_decision_and_draft():
    initial_state = {
        "event_id": "evt_test_001",
        "timestamp": "2026-05-17T10:00:00Z",
        "channel": "email_claim",
        "current_step": "start",
        "customer_email": "nadia.martin@email.fr",
        "subject": "Reclamation colis",
        "body": "Bonjour, mon colis est perdu et c'est urgent.",
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

    result = graph.invoke(initial_state)

    assert result["should_create_ticket"] is True
    assert result["ticket_creation_reason"] != ""
    assert result["customer_context"] is not None
    assert len(result["rag_sources"]) >= 0
    assert result["draft_response"] is not None
    assert result["draft_response"].body is not None
    assert len(result["draft_response"].body.strip()) > 0
    assert len(result["audit_log"]) > 0
    assert result["current_step"] == "draft_response"