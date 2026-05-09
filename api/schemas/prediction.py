from pydantic import BaseModel
from typing import Optional

class IRSInput(BaseModel):
    """Variables météo/pollution réelles pour la simulation IRS (basé sur cols_irs.pkl)."""
    pm2_5_moyen: float
    dust_moyen: float
    co_moyen: float
    uv_moyen: float
    ozone_moyen: float

    class Config:
        extra = "allow"

class IRSResponse(BaseModel):
    """Réponse du calcul IRS."""
    irs_value: float
    irs_level: str
    irs_color: str

class PredictionPoint(BaseModel):
    """Un point de série temporelle (observation ou prédiction)."""
    date: str
    pm25: float
    is_prediction: bool = False

class ComputeInput(BaseModel):
    """Entrée pour le simulateur interactif."""
    city: str
    features: dict[str, float]

class ComputeResponse(BaseModel):
    """Réponse du calcul interactif de PM2.5."""
    predicted_pm25: float
    level: str
    color: str
    description: str
