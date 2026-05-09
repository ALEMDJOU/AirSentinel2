from pydantic import BaseModel
from typing import Optional

class FilterParams(BaseModel):
    """Paramètres de filtrage communs pour les endpoints."""
    villes: Optional[list[str]] = None
    regions: Optional[list[str]] = None
    annee_min: int = 2020
    annee_max: int = 2025
