import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from app.models.schemas import TicketProposal

class TicketingMock:
    """Mock système de ticketing qui lit/écrit depuis data/tickets/"""
    
    def __init__(self, data_path: str = "data/tickets/tickets_seed.json"):
        self.data_path = Path(data_path)
        self.tickets = self._load_tickets()
    
    def _load_tickets(self) -> dict:
        """Charge les tickets depuis le fichier JSON"""
        if self.data_path.exists():
            with open(self.data_path, "r") as f:
                tickets = json.load(f)
                return {t["ticket_id"]: t for t in tickets}
        return {}
    
    def create_ticket(self, proposal: TicketProposal) -> dict:
        """Crée un ticket dans le système"""
        ticket_id = f"TCK-2026-{len(self.tickets) + 1:04d}"
        
        ticket = {
            "ticket_id": ticket_id,
            "customer_id": proposal.customer_id,
            "channel": proposal.channel,
            "type": proposal.ticket_type,
            "priority": proposal.priority,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "tracking_number": proposal.tracking_number,
            "incident_date": proposal.incident_date,
            "audit_log": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": "created",
                    "by": "langgraph_agent",
                    "detail": "Ticket créé automatiquement par agent"
                }
            ]
        }
        
        self.tickets[ticket_id] = ticket
        self._persist()
        return ticket
    
    def get_ticket(self, ticket_id: str) -> Optional[dict]:
        """Récupère un ticket"""
        return self.tickets.get(ticket_id)
    
    def update_ticket_status(self, ticket_id: str, new_status: str, comment: str = "") -> dict:
        """Met à jour le statut d'un ticket"""
        if ticket_id in self.tickets:
            ticket = self.tickets[ticket_id]
            ticket["status"] = new_status
            ticket["audit_log"].append({
                "timestamp": datetime.now().isoformat(),
                "action": f"status_changed_to_{new_status}",
                "by": "advisor",
                "detail": comment
            })
            self._persist()
            return ticket
        return {}
    
    def add_internal_note(self, ticket_id: str, note: str, source: str = "agent") -> dict:
        """Ajoute une note interne au ticket"""
        if ticket_id in self.tickets:
            ticket = self.tickets[ticket_id]
            if "internal_notes" not in ticket:
                ticket["internal_notes"] = []
            ticket["internal_notes"].append({
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "text": note
            })
            self._persist()
            return ticket
        return {}
    
    def _persist(self):
        """Persiste les tickets dans le fichier JSON"""
        with open(self.data_path, "w") as f:
            json.dump(list(self.tickets.values()), f, indent=2)