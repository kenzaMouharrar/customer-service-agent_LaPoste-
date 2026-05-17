from langgraph.graph import StateGraph
from datetime import datetime
from pathlib import Path
import re
from app.graph.state import AgentState
from app.models.schemas import DraftResponse
from app.services.crm_mock import CRMMock

crm = CRMMock()


def _is_email_channel(channel: str) -> bool:
    return channel in ["email_claim", "email_general"]


def _has_tracking_or_reference(text: str) -> bool:
    lowered = text.lower()
    has_keyword = any(
        keyword in lowered
        for keyword in ["numero", "numéro", "suivi", "reference", "référence", "colis", "courrier"]
    )
    has_id_pattern = re.search(r"\b[a-zA-Z0-9]{10,20}\b", text) is not None
    return has_keyword and has_id_pattern


def _has_context_details(text: str) -> bool:
    lowered = text.lower()
    has_date = re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text) is not None
    has_place = any(keyword in lowered for keyword in ["adresse", "ville", "bureau", "agence"])
    return has_date or has_place


def _compute_missing_data(channel: str, request_subject: str, body: str) -> bool:
    if not _is_email_channel(channel):
        return False

    subject = (request_subject or "").lower()
    body_lower = (body or "").lower()
    related_to_tracking = subject in [
        "suivi de colis",
        "perte de colis",
        "suivi de courrier",
        "perte de courrier",
    ] or any(keyword in body_lower for keyword in ["colis", "courrier", "suivi", "perdu", "perte"])

    if not related_to_tracking:
        return False

    enough_identifiers = _has_tracking_or_reference(body)
    enough_context = _has_context_details(body)
    return not (enough_identifiers and enough_context)

def node_ingest(state: AgentState) -> AgentState:
    """Ingestion: normalise l'événement entrant + calcul retard"""
    from datetime import datetime
    
    state["current_step"] = "ingest"
    
    # Calcul du retard (différence en heures)
    try:
        event_time = datetime.fromisoformat(state["timestamp"].replace("Z", "+00:00"))
        now = datetime.now(event_time.tzinfo) if event_time.tzinfo else datetime.now()
        elapsed = (now - event_time).total_seconds() / 3600  # en heures
        state["time_elapsed_hours"] = round(elapsed, 2)
        state["retard"] = elapsed > 24  # Seuil = 24 heures
    except Exception as e:
        state["errors"].append(f"Erreur calcul retard: {e}")
        state["time_elapsed_hours"] = 0.0
        state["retard"] = False
    
    state["audit_log"].append({
        "step": "ingest",
        "timestamp": datetime.now().isoformat(),
        "detail": f"Événement reçu: {state['event_id']}",
        "time_elapsed_hours": state["time_elapsed_hours"],
        "retard": state["retard"],
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
    """RAG hybride: BM25 + FAISS sur les documents .md La Poste"""
    state["current_step"] = "retrieve_rag"

    query = f"{state['subject']}\n{state['body']}"

    try:
        from app.rag.retriever import retriever
        docs = retriever.retrieve(query=query, top_k=3)
        state["rag_documents"] = [doc["text"] for doc in docs]
        state["rag_sources"] = list(
            dict.fromkeys(doc["metadata"]["source"] for doc in docs)
        )
    except RuntimeError as e:
        # Index pas encore construit → fallback sur lecture brute
        state["errors"].append(f"RAG non indexé: {e}")
        rag_path = Path("data/rag_docs/procedures_colis.md")
        if rag_path.exists():
            state["rag_documents"] = [rag_path.read_text(encoding="utf-8")]
            state["rag_sources"] = ["procedures_colis.md"]

    state["audit_log"].append({
        "step": "retrieve_rag",
        "timestamp": datetime.now().isoformat(),
        "documents_retrieved": len(state["rag_documents"]),
        "sources": state["rag_sources"],
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

    state["missing_data"] = _compute_missing_data(
        state["channel"],
        request_subject,
        state["body"],
    )
    
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
        "llm_used": "mistral-small",
        "missing_data": state["missing_data"],
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