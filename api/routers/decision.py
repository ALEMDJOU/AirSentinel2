"""
api/routers/decision.py

Endpoint GET /decision/real — Recommandations santé par profil selon qualité de l'air.
"""

import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from api.services.data_service import get_dataframe

router = APIRouter(prefix="/decision", tags=["Décision"])


class ProfilRecommandation(BaseModel):
    profil: str
    icone: str
    niveau_risque: str
    couleur: str
    message: str
    actions: list[str]


# Structure unifiée des recommandations (Français/Anglais)
RECOMMANDATIONS = {
    "fr": {
        "BON": {
            "label": "BON", "color": "#4CAF50",
            "enfant": {"msg": "Air sain. Idéal pour jouer dehors.", "acts": ["Activités normales", "Aération maximale"]},
            "adulte": {"msg": "Qualité optimale. Profitez du plein air.", "acts": ["Sport possible", "Aucune restriction"]},
            "senior": {"msg": "Conditions idéales. Sortie recommandée.", "acts": ["Promenade", "Aération des pièces"]},
            "asthmatique": {"msg": "Air pur. Risque d'irritation minimal.", "acts": ["Activités normales", "Précaution habituelle"]}
        },
        "MODERE": {
            "label": "MODÉRÉ", "color": "#FFC107",
            "enfant": {"msg": "Air acceptable. Évitez les jeux trop intenses.", "acts": ["Jeux calmes", "Aération ponctuelle"]},
            "adulte": {"msg": "Léger voile de pollution. Prudence pour les sensibles.", "acts": ["Réduire cardio intense", "Éviter les grands axes"]},
            "senior": {"msg": "Prudence conseillée. Sorties brèves.", "acts": ["Limiter exposition", "Rester hydraté"]},
            "asthmatique": {"msg": "Sensibilité accrue. Gardez vos médicaments.", "acts": ["Masque recommandé", "Surveiller le souffle"]}
        },
        "SEVERE": {
            "label": "SÉVÈRE", "color": "#FF9800",
            "enfant": {"msg": "Air dégradé. Privilégiez les jeux en intérieur.", "acts": ["Pas de sport dehors", "Fenêtres fermées"]},
            "adulte": {"msg": "Pollution marquée. Limitez vos efforts.", "acts": ["Télétravail conseillé", "Masque FFP2 dehors"]},
            "senior": {"msg": "Danger potentiel. Restez à l'intérieur.", "acts": ["Éviter les sorties", "Suivi médical si besoin"]},
            "asthmatique": {"msg": "Risque d'essoufflement. Traitement préventif.", "acts": ["Confinement partiel", "Masque FFP2 obligatoire"]}
        },
        "DANGEREUX": {
            "label": "DANGEREUX", "color": "#FF5722",
            "enfant": {"msg": "🚨 Risque élevé. Interdiction de sortie.", "acts": ["Rester confiné", "Purificateur d'air", "Suivi respiratoire"]},
            "adulte": {"msg": "🚨 Air toxique. Masque FFP2/FFP3 obligatoire.", "acts": ["Zéro sport extérieur", "Limiter tout trajet"]},
            "senior": {"msg": "🚨 Danger grave. Ne sortez sous aucun prétexte.", "acts": ["Confinement total", "Contact famille"]},
            "asthmatique": {"msg": "🚨 Crise probable. Préparez l'urgence.", "acts": ["Confinement strict", "Appeler médecin si gêne"]}
        },
        "CRITIQUE": {
            "label": "CRITIQUE", "color": "#B71C1C",
            "enfant": {"msg": "💀 Urgence vitale. Confinement hermétique.", "acts": ["Évacuation si possible", "Appeler le 115 si toux"]},
            "adulte": {"msg": "💀 Pollution extrême. Danger immédiat.", "acts": ["Zéro sortie", "Masque FFP3 si urgence"]},
            "senior": {"msg": "💀 Alerte rouge. Assistance médicale requise.", "acts": ["Vigilance absolue", "Aide à domicile"]},
            "asthmatique": {"msg": "💀 Risque de crise majeure. Urgence.", "acts": ["Utiliser inhalateur", "Appeler secours si crise"]}
        }
    },
    "en": {
        "BON": {
            "label": "GOOD", "color": "#4CAF50",
            "enfant": {"msg": "Healthy air. Perfect for playing outside.", "acts": ["Normal activities", "Maximum ventilation"]},
            "adulte": {"msg": "Optimal quality. Enjoy the outdoors.", "acts": ["Exercise possible", "No restrictions"]},
            "senior": {"msg": "Ideal conditions. Outing recommended.", "acts": ["Walk outside", "Ventilate rooms"]},
            "asthmatique": {"msg": "Pure air. Minimal irritation risk.", "acts": ["Normal activities", "Standard precaution"]}
        },
        "MODERE": {
            "label": "MODERATE", "color": "#FFC107",
            "enfant": {"msg": "Moderate air. Avoid very intense games.", "acts": ["Calm play", "Occasional ventilation"]},
            "adulte": {"msg": "Light haze. Caution for sensitive people.", "acts": ["Reduce intense cardio", "Avoid busy roads"]},
            "senior": {"msg": "Caution advised. Short outings only.", "acts": ["Limit exposure", "Stay hydrated"]},
            "asthmatique": {"msg": "Increased sensitivity. Keep your meds.", "acts": ["Mask recommended", "Monitor breathing"]}
        },
        "SEVERE": {
            "label": "SEVERE", "color": "#FF9800",
            "enfant": {"msg": "Poor air. Prefer indoor activities.", "acts": ["No outdoor sports", "Keep windows closed"]},
            "adulte": {"msg": "Marked pollution. Limit your efforts.", "acts": ["Remote work advised", "FFP2 mask outdoors"]},
            "senior": {"msg": "Potential danger. Stay indoors.", "acts": ["Avoid going out", "Medical follow-up if needed"]},
            "asthmatique": {"msg": "Shortness of breath risk. Preventive treatment.", "acts": ["Partial confinement", "FFP2 mask mandatory"]}
        },
        "DANGEREUX": {
            "label": "DANGEROUS", "color": "#FF5722",
            "enfant": {"msg": "🚨 High risk. No outdoor activities allowed.", "acts": ["Stay indoors", "Air purifier", "Breathing check"]},
            "adulte": {"msg": "🚨 Toxic air. FFP2/FFP3 mask mandatory.", "acts": ["Zero outdoor sports", "Limit all travel"]},
            "senior": {"msg": "🚨 Serious danger. Do not go out for any reason.", "acts": ["Total confinement", "Contact family"]},
            "asthmatique": {"msg": "🚨 Probable attack. Prepare emergency plan.", "acts": ["Strict confinement", "Call doctor if tight"]}
        },
        "CRITIQUE": {
            "label": "CRITICAL", "color": "#B71C1C",
            "enfant": {"msg": "💀 Life threatening. Hermetic confinement.", "acts": ["Evacuate if possible", "Call 115 if coughing"]},
            "adulte": {"msg": "💀 Extreme pollution. Immediate danger.", "acts": ["Zero outing", "FFP3 mask if emergency"]},
            "senior": {"msg": "💀 Red alert. Medical assistance required.", "acts": ["Absolute vigilance", "Home assistance"]},
            "asthmatique": {"msg": "💀 Major attack risk. Emergency.", "acts": ["Use inhaler", "Call help if attack starts"]}
        }
    }
}

PROFIL_META = {
    "enfant": {"icone": "👶", "label_fr": "Enfant (< 12 ans)", "label_en": "Child (< 12 years)"},
    "adulte": {"icone": "🧑", "label_fr": "Adulte", "label_en": "Adult"},
    "senior": {"icone": "👴", "label_fr": "Personne âgée", "label_en": "Senior"},
    "asthmatique": {"icone": "🫁", "label_fr": "Asthmatique", "label_en": "Asthmatic"},
}

def _find_col(df, candidates):
    for c in candidates:
        if c in df.columns: return c
    return None

def _get_niveau_actuel(df, ville: Optional[str] = None) -> str:
    pm25_col = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25"])
    if not pm25_col: return "MODERE"
    
    filtered_df = df
    city_col = _find_col(df, ["ville", "city"])
    if ville and city_col:
        filtered_df = df[df[city_col].str.lower() == ville.lower()]
    
    if filtered_df.empty: return "MODERE"
    
    if "date" in filtered_df.columns:
        filtered_df = filtered_df.sort_values("date", ascending=False)
    
    last_val = filtered_df.iloc[0][pm25_col]
    
    # Seuils unifiés (update_daily.py)
    if last_val <= 12: return "BON"
    elif last_val <= 35.4: return "MODERE"
    elif last_val <= 55.4: return "SEVERE"
    elif last_val <= 150.4: return "DANGEREUX"
    else: return "CRITIQUE"

@router.get("/real", response_model=list[ProfilRecommandation])
def get_recommandations(request: Request, ville: Optional[str] = None):
    # Détection langue
    accept_lang = request.headers.get("accept-language", "fr")
    lang = "en" if "en" in accept_lang.lower() else "fr"
    
    try:
        df = get_dataframe()
        niveau = _get_niveau_actuel(df, ville)
    except Exception:
        niveau = "MODERE"

    t = RECOMMANDATIONS[lang][niveau]
    result = []
    
    for key, meta in PROFIL_META.items():
        reco = t[key]
        result.append(ProfilRecommandation(
            profil=meta[f"label_{lang}"],
            icone=meta["icone"],
            niveau_risque=t["label"],
            couleur=t["color"],
            message=reco["msg"],
            actions=reco["acts"],
        ))
    return result
