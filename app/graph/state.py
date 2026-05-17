from typing import TypedDict, Optional, List
from app.models.schemas import CustomerContext, DraftResponse

class AgentState(TypedDict):
    """État unique du workflow LangGraph"""
    
    # Métadonnées
    event_id: str
    timestamp: str
    channel: str
    current_step: str
    
    # Événement brut
    customer_email: str
    subject: str
    body: str
    
    # Contexte client
    customer_context: Optional[CustomerContext]
    customer_history: Optional[dict]
    
    # Décision ticket
    should_create_ticket: bool
    ticket_creation_reason: str
    
    # Contexte RAG
    rag_documents: List[str]
    rag_sources: List[str]
    
    # Proposition réponse
    draft_response: Optional[DraftResponse]
    request_subject: Optional[str]
    
    # Décision escalade
    should_escalate: bool
    escalate_reason: str
    escalate_to: Optional[str]  # back_office, direction, superviseur
    
    # Audit et logs
    audit_log: List[dict]
    errors: List[str]