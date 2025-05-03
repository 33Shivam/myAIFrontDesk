from dataclasses import dataclass
from typing import Optional
import yaml

@dataclass
class CustomerInformation:
    customer_name: Optional[str] = None
    reservation_time: Optional[str] = None
    reservation_date: Optional[str] = None
    query: Optional[str] = None

    def summarize(self):
        data = {
            "customer_name": self.customer_name or "Not provided",
            "reservation_time": self.reservation_time or "Not provided",
            "reservation_date": self.reservation_date or "Not provided",
            "query": self.query or "Not provided",
        }
        return yaml.dump(data)