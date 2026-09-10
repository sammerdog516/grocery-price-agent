from pydantic import BaseModel
from typing import Optional

class DiscoveredStore(BaseModel):
    retailer_name: str
    address: str
    external_place_id: str

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_hours: Optional[dict] = None