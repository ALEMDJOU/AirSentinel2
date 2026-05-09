"""
api/routers/predictions.py

Endpoints de prédiction ML AirSentinel.
"""

import pandas as pd
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.services.data_service import get_dataframe
from api.services.irs_service import compute_irs
from api.schemas.prediction import IRSInput, IRSResponse, PredictionPoint, ComputeInput, ComputeResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictions", tags=["Prédictions"])


class MonthlyPM25(BaseModel):
    annee: int
    mois: int
    pm25_moyen: float


# ─── Helpers ───────────────────────────────────────────────────────
def _find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


# ─── Endpoints ─────────────────────────────────────────────────────
@router.get("/short-term", response_model=list[PredictionPoint])
def get_short_term():
    """
    Retourne l'historique et les prédictions PM2.5.
    """
    try:
        df = get_dataframe()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    pm25_col = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5"])
    date_col = "date" if "date" in df.columns else None

    if not pm25_col or not date_col:
        logger.error(f"Colonnes requises absentes: pm25={pm25_col}, date={date_col}")
        return [] # Retourner une liste vide plutôt que de crasher

    df_sorted = df.sort_values(date_col).dropna(subset=[pm25_col])
    
    if df_sorted.empty:
        logger.warning("Dataset filtré vide pour les prédictions.")
        return []

    last_date = df_sorted[date_col].max()

    # Historique : 21 derniers jours
    start_hist = last_date - timedelta(days=21)
    hist_df = df_sorted[df_sorted[date_col] >= start_hist]
    
    if hist_df.empty:
        return []

    hist = (
        hist_df.resample("D", on=date_col)[pm25_col]
        .mean()
        .dropna()
        .reset_index()
    )
    
    result = [
        PredictionPoint(date=str(row[date_col].date()), pm25=round(float(row[pm25_col]), 2))
        for _, row in hist.iterrows()
    ]

    # Prédiction simulée
    if not hist.empty:
        pm25_base = hist[pm25_col].tail(7).mean() if len(hist) >= 7 else hist[pm25_col].mean()
    else:
        pm25_base = 25.0
        
    for i in range(1, 4):
        pred_date = last_date + timedelta(days=i)
        pred_val = round(float(pm25_base) * (1 + 0.01 * i), 2)
        result.append(PredictionPoint(date=str(pred_date.date()), pm25=pred_val, is_prediction=True))

    return result


@router.get("/monthly", response_model=list[MonthlyPM25])
def get_monthly():
    """
    PM2.5 mensuel moyen par année et mois.
    """
    try:
        df = get_dataframe()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    pm25_col = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5"])
    if not pm25_col or "date" not in df.columns:
        raise HTTPException(status_code=500, detail="Colonnes 'pm25' ou 'date' absentes du dataset.")

    df["_annee"] = df["date"].dt.year
    df["_mois"] = df["date"].dt.month

    grouped = (
        df.groupby(["_annee", "_mois"])[pm25_col]
        .mean()
        .reset_index()
        .rename(columns={"_annee": "annee", "_mois": "mois", pm25_col: "pm25_moyen"})
        .sort_values(["annee", "mois"])
    )

    return [
        MonthlyPM25(annee=int(r.annee), mois=int(r.mois), pm25_moyen=round(float(r.pm25_moyen), 2))
        for _, r in grouped.iterrows()
    ]


@router.post("/simulate-irs", response_model=IRSResponse)
def simulate_irs(payload: IRSInput):
    """
    Reçoit des paramètres météo et retourne l'IRS simulé via irs_service.compute_irs().
    """
    try:
        result = compute_irs(payload.model_dump(exclude_none=True))
    except (ValueError, FileNotFoundError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    return IRSResponse(**result)


@router.post("/compute", response_model=ComputeResponse)
def compute_interactive(payload: ComputeInput):
    """
    Simulateur Interactif : Calcule le PM2.5 prédit selon la ville et les features ajustées par les jauges.
    """
    logger.info(f"Simulation PM2.5 demandée pour la ville: {payload.city}")
    city = payload.city.lower()
    f = payload.features
    
    # Baselines par ville (µg/m³) - Basé sur les moyennes IndabaX
    baselines = {
        "douala": 35.0,
        "yaoundé": 28.0,
        "yaounde": 28.0,
        "bafoussam": 22.0,
        "garoua": 45.0,
        "bamenda": 25.0,
        "maroua": 50.0,
        "kribi": 15.0,
        "bertoua": 32.0,
        "ebolowa": 20.0,
        "ngaoundéré": 38.0,
        "ngaoundere": 38.0,
        "buéa": 18.0,
        "buea": 18.0,
        "touboro": 42.0,
    }
    
    baseline = baselines.get(city, 30.0)
    
    # Poids des features (Simule l'impact physique)
    # PM2.5 = Baseline + sum(feature * weight)
    # Les valeurs en entrée sont supposées être "normalisées" ou dans des ranges standards
    weights = {
        "dust": 0.15,       # Impact fort des particules sahariennes
        "co": 1.5,          # Impact fort du trafic urbain
        "uv": 0.3,          # Impact photochimique
        "ozone": 0.2,       # Corrélation forte
        "temp": 0.1,        # La chaleur peut augmenter la suspension
        "humidity": -0.05,  # L'humidité peut faire tomber les particules
    }
    
    adjustment = sum(f.get(k, 0) * w for k, w in weights.items())
    predicted = max(2.0, baseline + adjustment)
    
    # Classification
    if predicted <= 12:
        level, color = "BON", "#10b981"
        desc = "La qualité de l'air est jugée satisfaisante."
    elif predicted <= 35:
        level, color = "MODÉRÉ", "#f59e0b"
        desc = "La qualité de l'air est acceptable."
    elif predicted <= 55:
        level, color = "DÉGRADÉ", "#f97316"
        desc = "Les membres des groupes sensibles peuvent ressentir des effets sur la santé."
    elif predicted <= 150:
        level, color = "MAUVAIS", "#ef4444"
        desc = "Tout le monde peut commencer à ressentir des effets sur la santé."
    else:
        level, color = "TRÈS MAUVAIS", "#7f1d1d"
        desc = "Avertissements sanitaires de conditions d'urgence."

    return ComputeResponse(
        predicted_pm25=round(predicted, 2),
        level=level,
        color=color,
        description=desc
    )
