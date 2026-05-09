"""
api/routers/kpis.py

Endpoint GET /kpis — Retourne les 6 KPIs nationaux AirSentinel.
"""

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from api.services.data_service import get_dataframe, apply_filters
from api.schemas.pollution import KPIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kpis", tags=["KPIs"])


def _find_col(df: pd.DataFrame, candidates: list[str]):
    """Cherche la première colonne disponible dans le DataFrame parmi une liste de candidats."""
    for col in candidates:
        if col in df.columns:
            return col
    return None


@router.get("", response_model=KPIResponse)
def get_kpis(city: Optional[str] = None):
    """
    Retourne les 6 indicateurs clés nationaux :
    - PM2.5 moyen
    - IRS moyen (si la colonne existe)
    - Nombre de villes dépassant le seuil OMS (PM2.5 > 10 µg/m³)
    - Polluant dominant
    - Tendance (calculée sur les 12 derniers mois via régression linéaire)
    - Nombre total d'observations
    """
    try:
        df = get_dataframe()
        if city:
            df = apply_filters(df, villes=[city])
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Aucune donnée pour la ville '{city}'.")

    # --- PM2.5 moyen ---
    pm25_col = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5", "PM25"])
    pm25_moyen = float(df[pm25_col].mean()) if pm25_col else 0.0

    # --- IRS moyen ---
    irs_col = _find_col(df, ["IRS", "irs", "irs_value"])
    irs_moyen = float(df[irs_col].mean()) if irs_col else None

    # --- Villes dépassant le seuil OMS (PM2.5 > 10 µg/m³) ---
    city_col = _find_col(df, ["city", "ville", "Ville", "City"])
    if city_col and pm25_col:
        city_means = df.groupby(city_col)[pm25_col].mean()
        villes_depassant_oms = int((city_means > 10).sum())
    else:
        villes_depassant_oms = 0

    # --- Polluant dominant ---
    polluant_cols = {
        "PM2.5": pm25_col,
        "PM10": _find_col(df, ["pm10", "PM10"]),
        "NO2": _find_col(df, ["no2", "NO2"]),
        "O3": _find_col(df, ["o3", "O3"]),
        "SO2": _find_col(df, ["so2", "SO2"]),
    }
    # FIX: Logique de polluant dominant correcte (ancienne version était redondante et cassée)
    available_polluants = {k: float(df[v].mean()) for k, v in polluant_cols.items() if v}
    polluant_dominant = max(available_polluants, key=available_polluants.get) if available_polluants else "PM2.5"

    # --- Tendance nationale sur les 12 derniers mois ---
    tendance = "stable"
    if pm25_col and "date" in df.columns:
        try:
            from scipy import stats
            df_sorted = df.sort_values("date")
            last_12 = df_sorted[df_sorted["date"] >= df_sorted["date"].max() - pd.DateOffset(months=12)]
            if len(last_12) > 2:
                x = np.arange(len(last_12))
                # FIX: méthode 'ffill' dépréciée depuis pandas 2.x, remplacée par ffill()
                y_values = last_12[pm25_col].ffill().values
                slope, _, _, p_value, _ = stats.linregress(x, y_values)
                if p_value < 0.05:
                    tendance = "croissant" if slope > 0 else "décroissant"
        except Exception as e:
            logger.warning(f"[KPIs] Impossible de calculer la tendance : {e}")

    return KPIResponse(
        pm25_moyen=round(pm25_moyen, 2),
        irs_moyen=round(irs_moyen, 4) if irs_moyen is not None else None,
        villes_depassant_oms=villes_depassant_oms,
        polluant_dominant=polluant_dominant,
        tendance=tendance,
        total_observations=len(df),
    )
