"""
api/routers/carte.py

Endpoints GET /carte et GET /carte/analyses.
Données géolocalisées par ville + 6 analyses enrichies.
"""

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.services.data_service import get_dataframe
from api.services.prediction_service import get_model
from api.services.irs_service import classify_irs_score

router = APIRouter(prefix="/carte", tags=["Carte"])


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

def _irs_label_color(irs_val, status_label=None):
    """
    Détermine le label et la couleur en utilisant les seuils du modèle (ACP).
    """
    try:
        seuils = get_model("seuils")
    except Exception:
        # Fallback si les modèles ne sont pas chargés
        seuils = {"p50": 0.2, "p75": 0.5, "p90": 0.8}

    if status_label:
        l = status_label.upper()
        if "FAIBLE" in l or "🟢" in l:
            return "FAIBLE", "#4CAF50"
        if "MODÉRÉ" in l or "🟡" in l:
            return "MODÉRÉ", "#FFC107"
        if "ÉLEVÉ" in l or "🟠" in l:
            return "ÉLEVÉ", "#FF5722"
        if "CRITIQUE" in l or "🔴" in l:
            return "CRITIQUE", "#B71C1C"

    # Utilisation de la logique de classification centralisée
    if irs_val is None:
        return "N/A", "#9E9E9E"
    
    return classify_irs_score(irs_val, seuils)


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

    result = []
    for _, row in latest_df.iterrows():
        irs_val = float(row[irs_col]) if irs_col else None
        status_text = str(row[status_col]) if status_col else None

        # Utiliser le modèle ML pour le PM2.5 (cohérent avec les alertes)
        city_name = str(row[city_col])
        ml_pm25 = None
        try:
            from api.routers.predictions import compute_interactive
            from api.schemas.prediction import ComputeInput
            features = {
                "dust":     float(row.get("dust_moyen", 50.0)),
                "co":       float(row.get("co_moyen", 15.0)),
                "uv":       float(row.get("uv_moyen", 6.0)),
                "temp":     float(row.get("temperature_2m_mean", 25.0)),
                "humidity": float(row.get("humidity_moyen", row.get("precipitation_sum", 60.0))),
                "ozone":    float(row.get("ozone_moyen", 40.0)),
            }
            pred = compute_interactive(ComputeInput(city=city_name, features=features))
            ml_pm25 = pred.predicted_pm25
        except Exception:
            ml_pm25 = round(float(row[pm25_col]), 2) if pm25_col else 0.0

        label, color = _irs_label_color(irs_val, status_text)

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
        latest_df = df.sort_values(by="date", ascending=False).drop_duplicates(subset=[city_col])
    else:
        latest_df = df.drop_duplicates(subset=[city_col]) if city_col else df

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
