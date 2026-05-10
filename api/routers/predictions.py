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
def get_short_term(city: Optional[str] = None):
    """
    Retourne l'historique et les prédictions PM2.5 pour une ville donnée.
    """
    try:
        df = get_dataframe()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if not city:
        city = "Douala" # Ville par défaut si non spécifiée

    # Filtrer par ville (case-insensitive)
    city_col = _find_col(df, ["ville", "city", "City", "Ville"])
    if city_col:
        df = df[df[city_col].str.lower() == city.lower()]
    
    if df.empty:
        logger.warning(f"Aucune donnée trouvée pour la ville: {city}")
        return []

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

    # Préparation des points (Historique + Futur)
    # On prend les 21 jours passés + les 3 jours futurs disponibles
    all_dates = sorted(df_sorted[date_col].dt.date.unique())
    try:
        today_idx = all_dates.index(last_date.date())
    except ValueError:
        today_idx = len(all_dates) - 1

    start_idx = max(0, today_idx - 20)
    selected_dates = all_dates[start_idx : today_idx + 4] # 21 jours passés (incluant aujourd'hui) + 3 futurs

    result = []
    from api.services.prediction_service import predict_pm25
    
    for day in selected_dates:
        # Prendre la première ligne pour ce jour
        day_data = df_sorted[df_sorted[date_col].dt.date == day].iloc[0]
        is_future = day > last_date.date()
        
        try:
            # On passe toutes les caractéristiques du jour au modèle ML
            pred_val = predict_pm25(day_data.to_dict())
            if pred_val <= 0: raise ValueError
        except Exception:
            # Fallback sur la valeur brute si le modèle échoue
            pred_val = float(day_data[pm25_col]) if pm25_col in day_data else 25.0
            
        result.append(PredictionPoint(
            date=str(day),
            pm25=round(float(pred_val), 2),
            is_prediction=is_future
        ))

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
    Simulateur Interactif : Calcule le PM2.5 prédit selon la ville et les features.
    Utilise le modèle ML réel AirSentinel si disponible.
    """
    logger.info(f"Simulation PM2.5 demandée pour la ville: {payload.city}")
    f = payload.features.copy()
    
    # Ajouter les métadonnées temporelles et géographiques si absentes
    now = datetime.now()
    if "mois" not in f: f["mois"] = now.month
    if "jour_annee" not in f: f["jour_annee"] = now.timetuple().tm_yday
    
    # Baselines lat/lon pour les villes principales si non fournies
    city_coords = {
        "douala": (4.05, 9.70), "yaoundé": (3.87, 11.52), "yaounde": (3.87, 11.52),
        "bafoussam": (5.48, 10.42), "garoua": (9.30, 13.40), "bamenda": (5.96, 10.15)
    }
    if "latitude" not in f or "longitude" not in f:
        lat, lon = city_coords.get(payload.city.lower(), (4.0, 11.0))
        f["latitude"] = f.get("latitude", lat)
        f["longitude"] = f.get("longitude", lon)

    # Mapper les noms des colonnes du payload vers ceux attendus par le modèle (si nécessaire)
    mapping = {
        "temp": "temperature_2m_mean",
        "humidity": "humidity_moyen",
        "dust": "dust_moyen",
        "co": "co_moyen",
        "uv": "uv_moyen",
        "ozone": "ozone_moyen"
    }
    for k, v in mapping.items():
        if k in f: f[v] = f.get(v, f[k])

    try:
        from api.services.prediction_service import predict_pm25
        predicted = predict_pm25(f)
        # Si le modèle retourne une valeur aberrante (ex: 0.0 suite à erreur), utiliser une fallback
        if predicted <= 0:
             # Fallback sur l'ancienne logique de baseline simplifiée
             baselines = {"douala": 35.0, "yaoundé": 28.0, "bafoussam": 22.0}
             predicted = baselines.get(payload.city.lower(), 30.0)
    except Exception as e:
        logger.error(f"Erreur modèle ML : {e}")
        predicted = 30.0

    # Classification (seuils OMS/AirSentinel)
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
