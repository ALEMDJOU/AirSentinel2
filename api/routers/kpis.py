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

    city_col = _find_col(df, ["city", "ville", "Ville", "City"])
    
    # ─── EXTRACTION DES DONNÉES RÉCENTES POUR S'ALIGNER AVEC LA CARTE ───
    if city_col and "date" in df.columns:
        latest_df = df.sort_values(by="date", ascending=False).drop_duplicates(subset=[city_col]).copy()
    else:
        latest_df = df.drop_duplicates(subset=[city_col]).copy() if city_col else df.copy()

    # Application du modèle ML pour aligner les KPIs avec la carte
    from api.services.prediction_service import predict_pm25
    pm25_col = _find_col(latest_df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5", "PM25"])
    region_col = _find_col(latest_df, ["region", "Region", "Area"])
    
    import math
    if pm25_col:
        for idx, row in latest_df.iterrows():
            clean_features = {}
            for k, v in row.to_dict().items():
                try:
                    val = float(v)
                    clean_features[k] = 0.0 if math.isnan(val) else val
                except (ValueError, TypeError):
                    pass
            region_name = "Centre"
            if region_col and region_col in row:
                region_name = str(row[region_col])
            
            try:
                ml_pm25 = predict_pm25(clean_features, region=region_name)
                if ml_pm25 > 0 and not math.isnan(ml_pm25):
                    latest_df.at[idx, pm25_col] = round(ml_pm25, 2)
            except Exception:
                pass

    # --- PM2.5 moyen ---
    pm25_col = _find_col(latest_df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5", "PM25"])
    pm25_moyen = float(latest_df[pm25_col].mean()) if pm25_col else 0.0

    # --- IRS moyen ---
    irs_col = _find_col(latest_df, ["IRS", "irs", "irs_value"])
    irs_moyen = float(latest_df[irs_col].mean()) if irs_col else None

    # --- Villes dépassant le seuil OMS (PM2.5 > 15 µg/m³) ---
    if city_col and pm25_col:
        city_latest_vals = latest_df.groupby(city_col)[pm25_col].mean()
        villes_depassant_oms = int((city_latest_vals > 15).sum())
    else:
        villes_depassant_oms = 0

    # --- Polluant dominant ---
    polluant_cols = {
        "PM2.5": pm25_col,
        "PM10": _find_col(latest_df, ["pm10", "PM10"]),
        "NO2": _find_col(latest_df, ["no2", "NO2"]),
        "O3": _find_col(latest_df, ["o3", "O3"]),
        "SO2": _find_col(latest_df, ["so2", "SO2"]),
    }
    # FIX: Logique de polluant dominant correcte
    available_polluants = {k: float(latest_df[v].mean()) for k, v in polluant_cols.items() if v}
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
