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

    start_idx = max(0, today_idx - 20)
    selected_dates = all_dates[start_idx : today_idx + 3]

    result = []
    from api.services.prediction_service import predict_pm25
    
    for day in selected_dates:
        day_data = df_sorted[df_sorted[date_col].dt.date == day].iloc[0]
        is_future = day > last_date_val
        
        try:
            # On passe toutes les caractéristiques du jour au modèle ML
            pred_val = predict_pm25(day_data.to_dict())
            if pred_val <= 0: raise ValueError
        except Exception:
            # Fallback sur la valeur brute si le modèle échoue
            pred_val = float(day_data[pm25_col]) if pm25_col in day_data else 25.0
            
        # Préparer les features pour le frontend
        raw_f = day_data.to_dict()
        feat_dict = {
            "dust": float(raw_f.get("dust_moyen", 0)),
            "co": float(raw_f.get("co_moyen", 0)),
            "uv": float(raw_f.get("uv_moyen", 0)),
            "ozone": float(raw_f.get("ozone_moyen", 0)),
            "temp": float(raw_f.get("temperature_2m_mean", 0)),
            "humidity": float(raw_f.get("humidity_moyen", 0))
        }

        result.append(PredictionPoint(
            date=str(day),
            pm25=round(float(pred_val), 2),
            is_prediction=is_future,
            features=feat_dict
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
        predicted = predict_pm25(f)
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
            "BON": ("BON", "#4CAF50", "Qualité de l'air optimale. Aucune restriction pour les activités en extérieur."),
            "MODERE": ("MODÉRÉ", "#FFC107", "Qualité acceptable. Les personnes ultra-sensibles devraient limiter les efforts."),
            "SEVERE": ("SÉVÈRE", "#FF9800", "Effets possibles sur la santé. Réduisez les activités physiques en plein air."),
            "DANGEREUX": ("DANGEREUX", "#FF5722", "Risques sanitaires accrus. Port du masque recommandé."),
            "CRITIQUE": ("CRITIQUE", "#B71C1C", "Urgence sanitaire. Évitez toute sortie. Port du masque obligatoire.")
        },
        "en": {
            "BON": ("GOOD", "#4CAF50", "Optimal air quality. No restrictions for outdoor activities."),
            "MODERE": ("MODERATE", "#FFC107", "Acceptable quality. Sensitive groups should limit prolonged exertion."),
            "SEVERE": ("SEVERE", "#FF9800", "Possible health effects. Reduce intense outdoor physical activities."),
            "DANGEREUX": ("DANGEROUS", "#FF5722", "Increased health risks. Mask recommended for sensitive groups."),
            "CRITIQUE": ("CRITICAL", "#B71C1C", "Health emergency. Avoid unnecessary outings. Mask mandatory.")
        }
    }
    
    t = translations.get(lang, translations["fr"])
    
    if predicted <= 12: key = "BON"
    elif predicted <= 35.4: key = "MODERE"
    elif predicted <= 55.4: key = "SEVERE"
    elif predicted <= 150.4: key = "DANGEREUX"
    else: key = "CRITIQUE"
    
    level, color, desc = t[key]

    return ComputeResponse(
        predicted_pm25=round(predicted, 2),
        level=level,
        color=color,
        description=desc
    )
