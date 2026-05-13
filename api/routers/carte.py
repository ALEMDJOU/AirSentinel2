"""
api/routers/carte.py

Endpoints GET /carte et GET /carte/analyses.
Données géolocalisées par ville + 6 analyses enrichies.
"""

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from api.services.data_service import get_dataframe

router = APIRouter(prefix="/carte", tags=["Carte"])
logger = logging.getLogger(__name__)


# ─── Schémas inline ────────────────────────────────────────────────
class VillePoint(BaseModel):
    city: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    pm25_moyen: float
    irs_moyen: Optional[float] = None
    irs_label: Optional[str] = None
    irs_color: Optional[str] = None

class CarteAnalyses(BaseModel):
    pm25_par_region: dict
    tendance_12_mois: dict
    top_3_polluants: list[dict]
    top_5_villes_critiques: list[dict]
    episodes_pollution: int
    pct_depassement_oms: float


# ─── Helpers ───────────────────────────────────────────────────────
def _find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _pm25_level(pm25: float):
    """Classifie le PM2.5 selon les seuils OMS 2021."""
    if pm25 <= 5:   return "EXCELLENT", "#008000"
    if pm25 <= 15:  return "BON",       "#4CAF50"
    if pm25 <= 25:  return "MODERE",    "#FFC107"
    if pm25 <= 50:  return "DEGRADE",   "#FF9800"
    if pm25 <= 100: return "MAUVAIS",   "#FF5722"
    return "CRITIQUE", "#B71C1C"


# ─── Endpoints ─────────────────────────────────────────────────────
@router.get("", response_model=list[VillePoint])
def get_carte():
    """
    Retourne une liste de points géolocalisés par ville avec PM2.5 et IRS.
    """
    try:
        df = get_dataframe()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    city_col   = _find_col(df, ["ville", "city"])
    pm25_col   = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5"])
    lat_col    = _find_col(df, ["latitude", "lat"])
    lon_col    = _find_col(df, ["longitude", "lon", "lng"])
    irs_col    = _find_col(df, ["IRS", "irs", "irs_value"])
    status_col = _find_col(df, ["niveau_sanitaire", "niveau_alerte", "label"])
    region_col = _find_col(df, ["region", "Region", "Area"])

    if not city_col:
        raise HTTPException(status_code=500, detail="Colonne ville introuvable.")

    # On ne garde que la DERNIÈRE observation par ville (Real-Time feel)
    # On s'assure que la colonne date existe
    if "date" in df.columns:
        # Tri par date décroissante puis suppression des doublons sur la ville
        latest_df = df.sort_values(by="date", ascending=False).drop_duplicates(subset=[city_col])
    else:
        # Fallback si pas de date : on garde la première occurrence
        latest_df = df.drop_duplicates(subset=[city_col])

    # Import du service ML (meilleur_modele.pkl) — appel direct, pas via le simulateur
    from api.services.prediction_service import predict_pm25
    import math

    result = []
    for _, row in latest_df.iterrows():
        irs_val    = float(row[irs_col]) if irs_col else None
        city_name  = str(row[city_col])

        # ── Prédiction ML directe (meilleur_modele.pkl + scaler.pkl) ──────────
        # On passe le dict complet de la ligne : predict_pm25 sélectionne
        # lui-même les colonnes attendues par le modèle via features.pkl.
        raw_dict = row.to_dict()
        # Nettoyage : seules les valeurs numériques sont utilisables par le modèle
        clean_features = {}
        for k, v in raw_dict.items():
            try:
                val = float(v)
                clean_features[k] = 0.0 if math.isnan(val) else val
            except (ValueError, TypeError):
                pass

        # Gestion sécurisée du nom de la région
        region_name = "Centre"
        try:
            if region_col and region_col in row:
                region_name = str(row[region_col])
        except Exception:
            pass

        try:
            ml_pm25 = predict_pm25(clean_features, region=region_name)
            # Sanity check : si le modèle retourne une valeur aberrante, fallback
            if ml_pm25 <= 0 or math.isnan(ml_pm25):
                raise ValueError(f"Valeur ML aberrante : {ml_pm25}")
            ml_pm25 = round(ml_pm25, 2)
        except Exception as e:
            logger.warning(f"[Carte ML] Fallback dataset pour {city_name} : {e}")
            ml_pm25 = round(float(raw_dict[pm25_col]), 2) if pm25_col and pm25_col in raw_dict else 25.0

        label, color = _pm25_level(ml_pm25)

        result.append(VillePoint(
            city=city_name,
            lat=float(row[lat_col]) if lat_col else None,
            lon=float(row[lon_col]) if lon_col else None,
            pm25_moyen=ml_pm25,
            irs_moyen=round(irs_val, 4) if irs_val is not None else None,
            irs_label=label,
            irs_color=color,
        ))
    return result


@router.get("/analyses", response_model=CarteAnalyses)
def get_analyses(city: Optional[str] = None):
    """
    Retourne 6 analyses enrichies :
    1. PM2.5 moyen par région
    2. Tendance 12 mois (nationale)
    3. Top 3 polluants disponibles dans le dataset
    4. Top 5 villes critiques (PM2.5 le plus élevé)
    5. Nombre d'épisodes de pollution (jours > seuil)
    6. % de jours dépassant les normes OMS (PM2.5 > 10 µg/m³)
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

    pm25_col   = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5", "PM25"])
    region_col = _find_col(df, ["region", "Region", "Area"])
    city_col   = _find_col(df, ["ville", "city", "Ville", "City"])

    # ─── EXTRACTION DES DONNÉES RÉCENTES POUR S'ALIGNER AVEC LA CARTE ───
    if city_col and "date" in df.columns:
        latest_df = df.sort_values(by="date", ascending=False).drop_duplicates(subset=[city_col]).copy()
    else:
        latest_df = df.drop_duplicates(subset=[city_col]).copy() if city_col else df.copy()

    # Application du modèle ML pour aligner les stats avec la carte
    from api.services.prediction_service import predict_pm25
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

    # 1. PM2.5 par région
    pm25_par_region = {}
    if region_col and pm25_col:
        pm25_par_region = latest_df.groupby(region_col)[pm25_col].mean().round(2).to_dict()

    # 2. Tendance 12 mois
    tendance_12_mois = {}
    if "date" in df.columns and pm25_col:
        df_s = df.sort_values("date")
        last12 = df_s[df_s["date"] >= df_s["date"].max() - pd.DateOffset(months=12)]
        monthly = last12.resample("ME", on="date")[pm25_col].mean().round(2).dropna()
        # FIX: les valeurs NaN brisent la sérialisation JSON — on les exclut via dropna()
        tendance_12_mois = {str(k.date()): float(v) for k, v in monthly.items()}

    # 3. Top 3 polluants
    polluant_cols = {
        "PM2.5": _find_col(latest_df, ["pm2_5", "pm25"]),
        "PM10":  _find_col(latest_df, ["pm10"]),
        "NO2":   _find_col(latest_df, ["no2"]),
        "O3":    _find_col(latest_df, ["o3"]),
        "SO2":   _find_col(latest_df, ["so2"]),
    }
    available = {
        k: round(float(latest_df[v].mean()), 2)
        for k, v in polluant_cols.items()
        if v and not latest_df[v].isna().all()  # FIX: skip columns that are all-NaN
    }
    top_3 = sorted(available.items(), key=lambda x: x[1], reverse=True)[:3]
    top_3_polluants = [{"polluant": k, "moyenne": v} for k, v in top_3]

    # 4. Top 5 villes critiques
    top_5_villes = []
    if city_col and pm25_col:
        city_means = latest_df.groupby(city_col)[pm25_col].mean().sort_values(ascending=False)
        top_5 = city_means.head(5)
        top_5_villes = [{"city": c, "pm25_moyen": round(v, 2)} for c, v in top_5.items()]

    # 5. Épisodes de pollution (journées > OMS de 25 µg/m³)
    seuil_episode = 25.0
    episodes = 0
    if pm25_col and "date" in df.columns:
        daily = df.resample("D", on="date")[pm25_col].mean()
        episodes = int((daily > seuil_episode).sum())

    # 6. % dépassement OMS (15 µg/m³ - cible 2021)
    pct_oms = 0.0
    if pm25_col:
        pct_oms = round(float((latest_df[pm25_col] > 15).mean() * 100), 2)

    return CarteAnalyses(
        pm25_par_region=pm25_par_region,
        tendance_12_mois=tendance_12_mois,
        top_3_polluants=top_3_polluants,
        top_5_villes_critiques=top_5_villes,
        episodes_pollution=episodes,
        pct_depassement_oms=pct_oms,
    )
