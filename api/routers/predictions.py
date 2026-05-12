"""
api/routers/predictions.py

Endpoints de prédiction ML AirSentinel.
"""

import pandas as pd
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request
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

    df_sorted = df.sort_values(date_col)
    
    if df_sorted.empty:
        logger.warning("Dataset filtré vide pour les prédictions.")
        return []

    # Définir aujourd'hui comme point de bascule
    today_now = pd.Timestamp.now().normalize()
    last_date_val = today_now.date()

    all_dates = sorted(df_sorted[date_col].dt.date.unique())
    try:
        today_idx = all_dates.index(last_date_val)
    except ValueError:
        today_idx = len(all_dates) - 1

    # 1. Préparer l'historique (les 20 derniers points disponibles)
    history_points = []
    from api.services.prediction_service import predict_pm25
    import math

    # On prend les 20 derniers jours présents dans le dataset
    recent_dates = all_dates[max(0, today_idx - 19) : today_idx + 1]
    
    for day in recent_dates:
        try:
            day_data = df_sorted[df_sorted[date_col].dt.date == day].iloc[-1]
            raw_dict = day_data.to_dict()
            feat_dict = {
                "dust": float(raw_dict.get("dust_moyen", 0)),
                "co": float(raw_dict.get("co_moyen", 0)),
                "uv": float(raw_dict.get("uv_moyen", 0)),
                "ozone": float(raw_dict.get("ozone_moyen", 0)),
                "temp": float(raw_dict.get("temperature_2m_mean", 0)),
                "humidity": float(raw_dict.get("humidity_moyen", 0))
            }
            history_points.append(PredictionPoint(
                date=str(day),
                pm25=round(float(raw_dict.get(pm25_col, 25.0)), 2),
                is_prediction=False,
                features=feat_dict
            ))
        except Exception:
            continue

    # 2. Préparer les prédictions (Aujourd'hui, J+1, J+2)
    prediction_points = []
    last_row = df_sorted.iloc[-1].to_dict()
    last_data_date = pd.to_datetime(last_row[date_col]).date()
    target_dates = [last_date_val, last_date_val + timedelta(days=1), last_date_val + timedelta(days=2)]
    
    for target_day in target_dates:
        if any(p.date == str(target_day) for p in history_points):
            continue
            
        gap_days = (target_day - last_data_date).days
        if gap_days < 1: gap_days = 1

        try:
            region_name = str(last_row.get("region", "Centre"))
            pred_val = predict_pm25(last_row, region=region_name, steps=gap_days)
            if pred_val <= 0 or math.isnan(pred_val): pred_val = 25.0
        except Exception:
            pred_val = 25.0

        feat_dict = {
            "dust": float(last_row.get("dust_moyen", 0)),
            "co": float(last_row.get("co_moyen", 0)),
            "uv": float(last_row.get("uv_moyen", 0)),
            "ozone": float(last_row.get("ozone_moyen", 0)),
            "temp": float(last_row.get("temperature_2m_mean", 0)),
            "humidity": float(last_row.get("humidity_moyen", 0))
        }

        prediction_points.append(PredictionPoint(
            date=str(target_day),
            pm25=round(float(pred_val), 2),
            is_prediction=True,
            features=feat_dict
        ))

    return history_points + prediction_points


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
def compute_interactive(payload: ComputeInput, request: Request):
    """
    Simulateur Interactif : Calcule le PM2.5 prédit selon la ville et les features.
    Utilise le modèle ML réel AirSentinel si disponible.
    """
    logger.info(f"Simulation PM2.5 demandée pour la ville: {payload.city}")
    
    # Détection de la langue
    accept_lang = request.headers.get("accept-language", "fr")
    lang = "en" if "en" in accept_lang.lower() else "fr"
    # 1. Charger les données réelles les plus récentes pour cette ville (pour les lags et métadonnées)
    f = {}
    try:
        df = get_dataframe()
        city_col = _find_col(df, ["ville", "city", "City", "Ville"])
        if city_col:
            city_data = df[df[city_col].str.lower() == payload.city.lower()]
            if not city_data.empty:
                # Prendre la ligne la plus récente pour avoir les vrais lags
                f = city_data.sort_values("date", ascending=False).iloc[0].to_dict()
    except Exception as e:
        logger.warning(f"Impossible de charger les données réelles pour la simulation: {e}")

    # 2. Fusionner avec les features du payload (les jauges de l'utilisateur gagnent)
    payload_f = payload.features.copy()
    
    # Mapper les noms courts du payload vers les noms longs du modèle
    mapping = {
        "temp": "temperature_2m_mean",
        "humidity": "humidity_moyen",
        "dust": "dust_moyen",
        "co": "co_moyen",
        "uv": "uv_moyen",
        "ozone": "ozone_moyen"
    }
    for short_name, long_name in mapping.items():
        if short_name in payload_f:
            f[long_name] = payload_f[short_name]

    # 3. Ajouter les métadonnées temporelles et géographiques si toujours absentes
    now = datetime.now()
    if "mois" not in f: f["mois"] = now.month
    if "jour_annee" not in f: f["jour_annee"] = now.timetuple().tm_yday
    
    # Baselines lat/lon pour les villes principales
    city_coords = {
        "douala": (4.05, 9.70), "yaoundé": (3.87, 11.52), "yaounde": (3.87, 11.52),
        "bafoussam": (5.48, 10.42), "garoua": (9.30, 13.40), "bamenda": (5.96, 10.15)
    }
    if "latitude" not in f or "longitude" not in f:
        lat, lon = city_coords.get(payload.city.lower(), (4.0, 11.0))
        f["latitude"] = f.get("latitude", lat)
        f["longitude"] = f.get("longitude", lon)

    try:
        from api.services.prediction_service import predict_pm25
        region_name = str(f.get("region", "Centre"))
        predicted = predict_pm25(f, region=region_name)
        # Si le modèle retourne une valeur aberrante (ex: 0.0 suite à erreur), utiliser une fallback
        if predicted <= 0:
             # Fallback sur l'ancienne logique de baseline simplifiée
             baselines = {"douala": 35.0, "yaoundé": 28.0, "bafoussam": 22.0}
             predicted = baselines.get(payload.city.lower(), 30.0)
    except Exception as e:
        logger.error(f"Erreur modèle ML : {e}")
        predicted = 30.0

    # MODIFICATION DE LA SIGNATURE (ajout de request)
    return _generate_compute_response(predicted, lang)

def _generate_compute_response(predicted: float, lang: str = "fr"):
    translations = {
        "fr": {
            "EXCELLENT": ("EXCELLENT", "#008000", "Qualité de l'air exceptionnelle. Idéal pour toutes les activités."),
            "BON": ("BON", "#4CAF50", "Qualité de l'air satisfaisante selon les normes OMS 2021."),
            "MODERE": ("MODÉRÉ", "#FFC107", "Qualité acceptable. Les personnes ultra-sensibles devraient limiter les efforts."),
            "DEGRADE": ("DÉGRADÉ", "#FF9800", "Qualité médiocre. Réduisez les activités physiques prolongées en extérieur."),
            "MAUVAIS": ("MAUVAIS", "#FF5722", "Air pollué. Risques sanitaires accrus pour toute la population."),
            "CRITIQUE": ("CRITIQUE", "#B71C1C", "Urgence sanitaire. Évitez toute sortie. Port du masque obligatoire.")
        },
        "en": {
            "EXCELLENT": ("EXCELLENT", "#008000", "Exceptional air quality. Ideal for all activities."),
            "BON": ("GOOD", "#4CAF50", "Satisfactory air quality according to WHO 2021 standards."),
            "MODERE": ("MODERATE", "#FFC107", "Acceptable quality. Sensitive groups should limit prolonged exertion."),
            "DEGRADE": ("DEGRADED", "#FF9800", "Poor quality. Reduce prolonged outdoor physical activities."),
            "MAUVAIS": ("UNHEALTHY", "#FF5722", "Polluted air. Increased health risks for the general population."),
            "CRITIQUE": ("CRITICAL", "#B71C1C", "Health emergency. Avoid unnecessary outings. Mask mandatory.")
        }
    }
    
    t = translations.get(lang, translations["fr"])
    
    if predicted <= 5: key = "EXCELLENT"
    elif predicted <= 15: key = "BON"
    elif predicted <= 25: key = "MODERE"
    elif predicted <= 50: key = "DEGRADE"
    elif predicted <= 100: key = "MAUVAIS"
    else: key = "CRITIQUE"
    
    level, color, desc = t[key]

    return ComputeResponse(
        predicted_pm25=round(predicted, 2),
        level=level,
        color=color,
        description=desc
    )
