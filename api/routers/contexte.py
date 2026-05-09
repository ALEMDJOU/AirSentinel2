"""
api/routers/contexte.py

Endpoint GET /contexte — Données contextuelles (donut, comparaison N-1, UV/Ozone).
"""

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from api.services.data_service import get_dataframe

router = APIRouter(prefix="/contexte", tags=["Contexte"])


class DonutEntry(BaseModel):
    label: str
    valeur: float
    couleur: str

class ComparaisonAnnuelle(BaseModel):
    annee_courante: int
    pm25_an_courant: float
    annee_precedente: int
    pm25_an_precedent: float
    evolution_pct: float

class UVOzone(BaseModel):
    uv_index: Optional[float] = None
    ozone_ppb: Optional[float] = None
    source: str = "Données statiques (intégrer API météo pour données temps réel)"

class ContexteResponse(BaseModel):
    donut_niveaux: list[DonutEntry]
    donut_polluants: list[DonutEntry]
    comparaison_annuelle: Optional[ComparaisonAnnuelle] = None
    uv_ozone: UVOzone


def _find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


@router.get("", response_model=ContexteResponse)
def get_contexte(city: Optional[str] = None):
    """
    Retourne les données contextuelles :
    - Donut répartition des niveaux IRS (FAIBLE / MODÉRÉ / ÉLEVÉ / CRITIQUE)
    - Donut top polluants (si multi-polluants disponibles)
    - Comparaison PM2.5 de l'année N vs N-1
    - Indice UV et Ozone (statiques ou issus du CSV si disponibles)
    """
    try:
        df = get_dataframe()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # Filtre par ville si spécifiée (et différente de CAMEROON)
    if city and city.upper() != "CAMEROON":
        from api.services.data_service import apply_filters
        df = apply_filters(df, villes=[city])
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Aucune donnée pour la ville '{city}'.")

    pm25_col = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5", "PM25"])

    # ─── 1. Donut niveaux IRS ────────────────────────────────────────
    def classify_pm25(val):
        if val <= 10:   return "FAIBLE"
        elif val <= 25: return "MODÉRÉ"
        elif val <= 50: return "ÉLEVÉ"
        else:           return "CRITIQUE"

    niveau_couleurs = {
        "FAIBLE": "#4CAF50",
        "MODÉRÉ": "#FFC107",
        "ÉLEVÉ": "#FF5722",
        "CRITIQUE": "#B71C1C",
    }

    donut_niveaux = []
    if pm25_col:
        niveaux = df[pm25_col].dropna().apply(classify_pm25).value_counts(normalize=True) * 100
        for niveau, pct in niveaux.items():
            donut_niveaux.append(DonutEntry(
                label=niveau,
                valeur=round(float(pct), 2),
                couleur=niveau_couleurs.get(niveau, "#999"),
            ))

    # ─── 2. Donut polluants ─────────────────────────────────────────
    polluant_cols = {
        "PM2.5": pm25_col,
        "PM10":  _find_col(df, ["pm10_moyen", "pm10"]),
        "NO2":   _find_col(df, ["no2_moyen", "no2"]),
        "O3":    _find_col(df, ["o3_moyen", "ozone_moyen", "o3"]),
        "SO2":   _find_col(df, ["so2_moyen", "so2"]),
    }
    polluant_couleurs = {
        "PM2.5": "#2196F3",
        "PM10":  "#9C27B0",
        "NO2":   "#FF9800",
        "O3":    "#00BCD4",
        "SO2":   "#F44336",
    }
    available = {k: float(df[v].mean()) for k, v in polluant_cols.items() if v}
    total_pol = sum(available.values()) or 1
    donut_polluants = [
        DonutEntry(
            label=k,
            valeur=round(v / total_pol * 100, 2),
            couleur=polluant_couleurs.get(k, "#999"),
        )
        for k, v in sorted(available.items(), key=lambda x: x[1], reverse=True)
    ]

    # ─── 3. Comparaison annuelle N vs N-1 ───────────────────────────
    comparaison = None
    if pm25_col and "date" in df.columns:
        annee_max = int(df["date"].dt.year.max())
        annee_prec = annee_max - 1
        pm25_an_courant = df[df["date"].dt.year == annee_max][pm25_col].mean()
        pm25_an_precedent = df[df["date"].dt.year == annee_prec][pm25_col].mean()

        if not pd.isna(pm25_an_courant) and not pd.isna(pm25_an_precedent) and pm25_an_precedent > 0:
            evolution = (pm25_an_courant - pm25_an_precedent) / pm25_an_precedent * 100
            comparaison = ComparaisonAnnuelle(
                annee_courante=annee_max,
                pm25_an_courant=round(float(pm25_an_courant), 2),
                annee_precedente=annee_prec,
                pm25_an_precedent=round(float(pm25_an_precedent), 2),
                evolution_pct=round(float(evolution), 2),
            )

    # ─── 4. UV / Ozone (statiques ou CSV) ───────────────────────────
    uv_col    = _find_col(df, ["uv", "uv_index", "UV"])
    ozone_col = _find_col(df, ["o3", "ozone", "O3"])
    uv_ozone = UVOzone(
        uv_index=round(float(df[uv_col].mean()), 2) if uv_col else 6.2,      # Valeur typique Cameroun
        ozone_ppb=round(float(df[ozone_col].mean()), 2) if ozone_col else 38.0,
        source="CSV dataset" if (uv_col or ozone_col) else "Valeurs de référence (Cameroun, 2024)",
    )

    return ContexteResponse(
        donut_niveaux=donut_niveaux,
        donut_polluants=donut_polluants,
        comparaison_annuelle=comparaison,
        uv_ozone=uv_ozone,
    )
