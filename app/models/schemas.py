from typing import Literal, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class CustomerContext:
    """Contexte client depuis CRM"""
    customer_id: str
    name: str
    email: str
    phone: str
    segment: str
    city: str
    known_issues_count: int

@dataclass
class IncomingEvent:
    """Événement entrant depuis Power Automate simulé"""
    event_id: str
    channel: Literal["email_general", "email_claim", "form", "call"]
    customer_email: str
    subject: str
    body: str
    attachments: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class TicketProposal:
    """Proposition de ticket créée par l'agent"""
    ticket_id: str
    customer_id: str
    channel: str
    ticket_type: str  # colis_perdu, colis_avarie, retard, courrier_non_recu, etc.
    priority: Literal["low", "normal", "high", "critical"]
    status: str = "proposed"
    tracking_number: Optional[str] = None
    incident_date: Optional[str] = None

@dataclass
class DraftResponse:
    """Brouillon de réponse généré par agent"""
    subject: str
    body: str
    sources: List[str]  # Quels documents RAG ont été utilisés
    confidence: float  # Score de confiance 0-1

@dataclass
class AdvisorDecision:
    """Décision du conseiller"""
    action: Literal["send", "modify", "escalate", "request_info", "reject"]
    modified_body: Optional[str] = None
    escalate_to: Optional[str] = None
    comment: str = ""
