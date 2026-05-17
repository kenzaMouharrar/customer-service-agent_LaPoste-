from langgraph.graph import StateGraph
from datetime import datetime
from pathlib import Path
from app.graph.state import AgentState
from app.models.schemas import DraftResponse
from app.services.crm_mock import CRMMock

crm = CRMMock()

def node_ingest(state: AgentState) -> AgentState:
    """Ingestion: normalise l'événement entrant"""
    state["current_step"] = "ingest"
    state["audit_log"].append({
        "step": "ingest",
        "timestamp": datetime.now().isoformat(),
        "detail": f"Événement reçu: {state['event_id']}"
    })
    return state

def node_decide_ticket_creation(state: AgentState) -> AgentState:
    """Décision: doit-on créer un ticket?"""
    state["current_step"] = "decide_ticket_creation"
    
    if state["channel"] == "email_claim":
        state["should_create_ticket"] = True
        state["ticket_creation_reason"] = "Canal réclamation: ticket systématique"
    elif any(keyword in state["body"].lower() for keyword in ["perdu", "avarie", "réclamation"]):
        state["should_create_ticket"] = True
        state["ticket_creation_reason"] = "Mots-clés sensibles détectés"
    else:
        state["should_create_ticket"] = False
        state["ticket_creation_reason"] = "Email simple, pas de ticket"
    
    state["audit_log"].append({
        "step": "decide_ticket_creation",
        "timestamp": datetime.now().isoformat(),
        "decision": state["should_create_ticket"],
        "reason": state["ticket_creation_reason"]
    })
    return state

def node_load_crm_context(state: AgentState) -> AgentState:
    """Enrichissement: charge le contexte CRM du client"""
    state["current_step"] = "load_crm_context"
    
    customer = crm.get_customer_by_email(state["customer_email"])
    state["customer_context"] = customer
    
    if customer:
        history = crm.get_customer_history(customer.customer_id)
        state["customer_history"] = history
    
    state["audit_log"].append({
        "step": "load_crm_context",
        "timestamp": datetime.now().isoformat(),
        "customer_found": customer is not None
    })
    return state

def node_retrieve_rag(state: AgentState) -> AgentState:
    """RAG: récupère les procédures pertinentes"""
    state["current_step"] = "retrieve_rag"
    
    rag_path = Path("data/rag_docs/procedures_colis.md")
    if rag_path.exists():
        with open(rag_path, "r") as f:
            content = f.read()
            state["rag_documents"].append(content)
            state["rag_sources"].append("procedures_colis.md")
    
    state["audit_log"].append({
        "step": "retrieve_rag",
        "timestamp": datetime.now().isoformat(),
        "documents_retrieved": len(state["rag_documents"])
    })
    return state

def node_check_escalation(state: AgentState) -> AgentState:
    """Décision d'escalade: ce cas nécessite-t-il une escalade?"""
    state["current_step"] = "check_escalation"
    
    # Logique d'escalade simple
    state["should_escalate"] = False
    state["escalate_reason"] = ""
    state["escalate_to"] = None
    
    # Escalade si client premium + problème complexe
    if state["customer_context"] and state["customer_context"].segment == "premium":
        if state["customer_context"].known_issues_count > 2:
            state["should_escalate"] = True
            state["escalate_reason"] = "Client premium avec historique problématique"
            state["escalate_to"] = "superviseur"
    
    # Escalade si sentiment très négatif
    if any(keyword in state["body"].lower() for keyword in ["urgent", "tribunal", "avocat", "scandale"]):
        state["should_escalate"] = True
        state["escalate_reason"] = "Langage juridique ou très critique détecté"
        state["escalate_to"] = "direction"
    
    state["audit_log"].append({
        "step": "check_escalation",
        "timestamp": datetime.now().isoformat(),
        "escalate": state["should_escalate"],
        "reason": state["escalate_reason"],
        "escalate_to": state["escalate_to"]
    })
    return state

def node_draft_response(state: AgentState) -> AgentState:
    """Rédaction: génère un brouillon de réponse via Mistral"""
    from app.core.llm import llm
    
    state["current_step"] = "draft_response"
    
    customer_name = state["customer_context"].name if state["customer_context"] else "Cher client"
    rag_context = "\n".join(state["rag_documents"]) if state["rag_documents"] else "Pas de context"
    
    # Construit le prompt pour Mistral
    prompt = f"""Tu es un agent service client La Poste. Génère un brouillon de réponse professionnel.

CLIENT: {customer_name}
EMAIL CLIENT: {state["body"]}

CONTEXTE CRM:
- Segment: {state["customer_context"].segment if state["customer_context"] else "Inconnu"}
- Tickets passés: {state["customer_history"].get('total_tickets', 0) if state["customer_history"] else 0}

PROCÉDURES APPLICABLES:
{rag_context}

ESCALADE: {"OUI - traitement prioritaire" if state["should_escalate"] else "NON"}

Tu dois aussi classifier la demande du client dans une seule des catégories suivantes:
- suivi de colis
- perte de colis
- suivi de courrier
- perte de courrier
- demande de renseignement
- achat de produit de la poste

Retourne exactement ce format:

SUJET_DEMANDE: <une seule valeur parmi: suivi de colis, perte de colis, suivi de courrier, perte de courrier, demande de renseignement, achat de produit de la poste>
REPONSE: <brouillon de réponse professionnel>

"""
    # Valeurs par défaut robustes: utilisées si le LLM échoue
    request_subject = "inconnu"
    draft_subject = "Nous traitons votre demande"
    draft_body = (
        f"Bonjour {customer_name},\n\n"
        "Nous avons bien reçu votre demande et nous la traitons."
    )

    try:
        llm_output = llm.generate_response(prompt).strip()

        lines = llm_output.splitlines()
        draft_body_lines = []
        capture_response = False

        for line in lines:
            normalized = line.strip()
            upper = normalized.upper()
            if upper.startswith("SUJET_DEMANDE:"):
                request_subject = normalized.split(":", 1)[1].strip() or "inconnu"
            elif upper.startswith("REPONSE:"):
                capture_response = True
                # Capture le reste de la ligne après "REPONSE:"
                remainder = normalized.split(":", 1)[1].strip()
                if remainder:
                    draft_body_lines.append(remainder)
            elif capture_response:
                # Continue à capturer les lignes suivantes
                draft_body_lines.append(line.rstrip())

        if draft_body_lines:
            draft_body = "\n".join(draft_body_lines).strip()

    except Exception as e:
        state["errors"].append(f"Erreur LLM: {str(e)}")
    
    state["draft_response"] = DraftResponse(
        subject=draft_subject,
        body=draft_body,
        sources=state["rag_sources"],
        confidence=0.85,
    )
        
    state["request_subject"] = request_subject

    state["audit_log"].append({
        "step": "draft_response",
        "timestamp": datetime.now().isoformat(),
        "confidence": 0.85,
        "llm_used": "mistral-small"
    })
    
    return state

def build_workflow():
    """Graphe avec escalade"""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("ingest", node_ingest)
    workflow.add_node("decide_ticket_creation", node_decide_ticket_creation)
    workflow.add_node("load_crm_context", node_load_crm_context)
    workflow.add_node("retrieve_rag", node_retrieve_rag)
    workflow.add_node("check_escalation", node_check_escalation)
    workflow.add_node("draft_response", node_draft_response)
    
    workflow.add_edge("ingest", "decide_ticket_creation")
    workflow.add_edge("decide_ticket_creation", "load_crm_context")
    workflow.add_edge("load_crm_context", "retrieve_rag")
    workflow.add_edge("retrieve_rag", "check_escalation")
    workflow.add_edge("check_escalation", "draft_response")
    
    workflow.set_entry_point("ingest")
    workflow.set_finish_point("draft_response")
    
    return workflow.compile()

graph = build_workflow()