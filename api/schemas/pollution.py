from pydantic import BaseModel
from typing import Optional

class PollutionPoint(BaseModel):
    """Un point de données pollution sur la carte."""
    city: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    pm25_moyen: float
    irs_moyen: Optional[float] = None
    irs_label: Optional[str] = None
    irs_color: Optional[str] = None

class KPIResponse(BaseModel):
    """Réponse des 6 KPIs nationaux."""
    pm25_moyen: float
    irs_moyen: Optional[float] = None
    villes_depassant_oms: int
    polluant_dominant: str
    tendance: str
    total_observations: int
