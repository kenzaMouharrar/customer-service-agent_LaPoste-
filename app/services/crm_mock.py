import json
from pathlib import Path
from typing import Optional
from app.models.schemas import CustomerContext

class CRMMock:
    """Mock CRM qui lit depuis data/crm/customers.json"""
    
    def __init__(self, data_path: str = "data/crm/customers.json"):
        self.data_path = Path(data_path)
        self.customers = self._load_customers()
    
    def _load_customers(self) -> dict:
        """Charge les clients depuis le fichier JSON"""
        if self.data_path.exists():
            with open(self.data_path, "r") as f:
                customers = json.load(f)
                return {c["email"]: c for c in customers}
        return {}
    
    def get_customer_by_email(self, email: str) -> Optional[CustomerContext]:
        """Retrouve un client par email"""
        if email in self.customers:
            c = self.customers[email]
            return CustomerContext(
                customer_id=c["customer_id"],
                name=c["name"],
                email=c["email"],
                phone=c["phone"],
                segment=c["segment"],
                city=c["city"],
                known_issues_count=c.get("known_issues_count", 0)
            )
        return None
    
    def get_customer_history(self, customer_id: str) -> dict:
        """Récupère historique d'un client (tickets passés, etc.)"""
        return {
            "total_tickets": 2,
            "open_tickets": 0,
            "last_ticket_date": "2026-04-10",
            "is_premium": False,  # À enrichir selon segment
            "known_issues": []
        }