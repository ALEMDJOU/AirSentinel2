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


# Recommandations statiques par niveau IRS × profil × langue
RECOMMANDATIONS_BILINGUE = {
    "fr": {
        "FAIBLE": {
            "enfant": {
                "message": "Qualité de l'air satisfaisante. Les activités extérieures sont conseillées.",
                "actions": ["Activités sportives possibles", "Pas de restriction"]
            },
            "adulte": {
                "message": "Air sain. Profitez des activités en plein air sans restriction.",
                "actions": ["Activités normales", "Ventilation naturelle recommandée"]
            },
            "personne_agee": {
                "message": "Conditions favorables. Sortie possible sans précaution particulière.",
                "actions": ["Promenade conseillée", "Pas de masque nécessaire"]
            },
            "asthmatique": {
                "message": "Risque faible. Gardez votre inhalateur par précaution.",
                "actions": ["Sortie possible", "Surveiller vos symptômes"]
            },
        },
        "MODÉRÉ": {
            "enfant": {
                "message": "Qualité d'air modérée. Limitez les efforts intenses prolongés en extérieur.",
                "actions": ["Réduire les activités sportives intenses", "Aérer les locaux"]
            },
            "adulte": {
                "message": "Léger risque pour les personnes sensibles. Réduisez les expositions prolongées.",
                "actions": ["Limiter les activités physiques", "Éviter les zones à fort trafic"]
            },
            "personne_agee": {
                "message": "Prudence conseillée. Privilégiez les activités en intérieur.",
                "actions": ["Rester à l'intérieur si possible", "Consulter si gêne respiratoire"]
            },
            "asthmatique": {
                "message": "Risque modéré. Portez masque FFP2 en extérieur.",
                "actions": ["Porter un masque FFP2", "Éviter les efforts physiques"]
            },
        },
        "ÉLEVÉ": {
            "enfant": {
                "message": "Qualité d'air dégradée. Restez à l'intérieur autant que possible.",
                "actions": ["Annuler les sorties", "Fermer les fenêtres"]
            },
            "adulte": {
                "message": "Air de mauvaise qualité. Limitez toute activité extérieure.",
                "actions": ["Télétravail si possible", "Porter masque FFP2"]
            },
            "personne_agee": {
                "message": "Danger pour les personnes vulnérables. Restez en intérieur.",
                "actions": ["Ne pas sortir", "Fermer portes et fenêtres"]
            },
            "asthmatique": {
                "message": "Risque élevé. Activation du plan d'action asthme recommandée.",
                "actions": ["Rester en intérieur", "Augmenter traitement préventif si prescrit"]
            },
        },
        "CRITIQUE": {
            "enfant": {
                "message": "🚨 Urgence sanitaire. Ne pas exposer les enfants à l'extérieur.",
                "actions": ["Fermer hermétiquement", "Appeler les secours si détresse"]
            },
            "adulte": {
                "message": "🚨 Pollution critique. Confinement recommandé.",
                "actions": ["Rester confiné", "Masque FFP3 si sortie indispensable"]
            },
            "personne_agee": {
                "message": "🚨 Risque vital. Alerte rouge pour les personnes âgées.",
                "actions": ["Confinement total", "Assistance médicale immédiate"]
            },
            "asthmatique": {
                "message": "🚨 Situation critique. Protocole d'urgence asthme à activer.",
                "actions": ["Appeler les secours", "Utilisation immédiate des bronchodilatateurs"]
            },
        },
    },
    "en": {
        "FAIBLE": {
            "enfant": {
                "message": "Satisfactory air quality. Outdoor activities are encouraged.",
                "actions": ["Sports activities possible", "No restrictions"]
            },
            "adulte": {
                "message": "Clean air. Enjoy outdoor activities without restriction.",
                "actions": ["Normal activities", "Natural ventilation recommended"]
            },
            "personne_agee": {
                "message": "Favorable conditions. Outdoor walks possible without special precautions.",
                "actions": ["Recommended walk", "No mask needed"]
            },
            "asthmatique": {
                "message": "Low risk. Keep your inhaler with you as a precaution.",
                "actions": ["Going out possible", "Monitor your symptoms"]
            },
        },
        "MODÉRÉ": {
            "enfant": {
                "message": "Moderate air quality. Limit prolonged intense outdoor exertion.",
                "actions": ["Reduce intense sports", "Ventilate indoor spaces"]
            },
            "adulte": {
                "message": "Light risk for sensitive people. Reduce prolonged exposure.",
                "actions": ["Limit physical activities", "Avoid high traffic areas"]
            },
            "personne_agee": {
                "message": "Prudence advised. Prioritize indoor activities.",
                "actions": ["Stay indoors if possible", "Consult doctor if breathing issues"]
            },
            "asthmatique": {
                "message": "Moderate risk. Wear FFP2 mask outdoors.",
                "actions": ["Wear FFP2 mask", "Avoid physical exertion"]
            },
        },
        "ÉLEVÉ": {
            "enfant": {
                "message": "Degraded air quality. Stay indoors as much as possible.",
                "actions": ["Cancel outings", "Close windows"]
            },
            "adulte": {
                "message": "Poor air quality. Limit all outdoor activity.",
                "actions": ["Telework if possible", "Wear FFP2 mask"]
            },
            "personne_agee": {
                "message": "Danger for vulnerable people. Stay indoors.",
                "actions": ["Do not go out", "Close doors and windows"]
            },
            "asthmatique": {
                "message": "High risk. Asthma action plan activation recommended.",
                "actions": ["Stay indoors mandatory", "Increase preventive treatment if prescribed"]
            },
        },
        "CRITIQUE": {
            "enfant": {
                "message": "🚨 Health emergency. Do not expose children outdoors.",
                "actions": ["Seal windows", "Call emergency services if distress"]
            },
            "adulte": {
                "message": "🚨 Critical pollution. Lockdown recommended.",
                "actions": ["Stay confined", "FFP3 mask if outing is essential"]
            },
            "personne_agee": {
                "message": "🚨 Vital risk. Red alert for the elderly.",
                "actions": ["Total confinement", "Immediate medical assistance"]
            },
            "asthmatique": {
                "message": "🚨 Critical situation. Emergency asthma protocol to activate.",
                "actions": ["Call emergency services", "Immediate use of bronchodilators"]
            },
        },
    }
}

PROFIL_META_BILINGUE = {
    "fr": {
        "enfant": {"icone": "👶", "label": "Enfant (< 12 ans)"},
        "adulte": {"icone": "🧑", "label": "Adulte"},
        "personne_agee": {"icone": "👴", "label": "Personne âgée"},
        "asthmatique": {"icone": "🫁", "label": "Personne asthmatique"},
    },
    "en": {
        "enfant": {"icone": "👶", "label": "Child (< 12 years)"},
        "adulte": {"icone": "🧑", "label": "Adult"},
        "personne_agee": {"icone": "👴", "label": "Senior citizen"},
        "asthmatique": {"icone": "🫁", "label": "Asthmatic person"},
    }
}

NIVEAU_COULEUR = {
    "FAIBLE": "#4CAF50",
    "MODÉRÉ": "#FFC107",
    "ÉLEVÉ": "#FF5722",
    "CRITIQUE": "#B71C1C",
}

def _find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _get_niveau_actuel(df, ville: Optional[str] = None) -> str:
    """Calcule le niveau IRS actuel à partir des dernières données disponibles."""
    niveau_col = _find_col(df, ["niveau_sanitaire", "niveau_alerte", "label"])
    pm25_col = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5", "PM25"])
    
    if not pm25_col:
        return "MODÉRÉ"
    
    filtered_df = df
    city_col = _find_col(df, ["ville", "city"])
    if ville and city_col:
        filtered_df = df[df[city_col] == ville]
    
    if filtered_df.empty:
        return "MODÉRÉ"
    
    if "date" in filtered_df.columns:
        filtered_df = filtered_df.sort_values("date")
    
    if niveau_col and niveau_col in filtered_df.columns:
        last_row = filtered_df.tail(1).iloc[0]
        niveau_str = str(last_row[niveau_col])
        if "FAIBLE" in niveau_str:
            return "FAIBLE"
        elif "MODÉRÉ" in niveau_str or "MOYEN" in niveau_str:
            return "MODÉRÉ"
        elif "ÉLEVÉ" in niveau_str or "TRÈS" in niveau_str:
            return "ÉLEVÉ"
        elif "CRITIQUE" in niveau_str or "MAUVAIS" in niveau_str:
            return "CRITIQUE"
    
    last_val = filtered_df.tail(1)[pm25_col].values[0] if pm25_col in filtered_df.columns else filtered_df[pm25_col].mean()

    if last_val <= 10:
        return "FAIBLE"
    elif last_val <= 25:
        return "MODÉRÉ"
    elif last_val <= 50:
        return "ÉLEVÉ"
    else:
        return "CRITIQUE"


@router.get("/real", response_model=list[ProfilRecommandation])
def get_recommandations(request: Request, ville: Optional[str] = None):
    """
    Retourne les recommandations de santé pour les 4 profils selon le niveau IRS actuel.
    Supporte l'anglais et le français via le header Accept-Language.
    """
    # Détection de la langue
    accept_lang = request.headers.get("accept-language", "fr")
    lang = "en" if "en" in accept_lang.lower() else "fr"
    
    try:
        df = get_dataframe()
        
        city_col = _find_col(df, ["ville", "city"])
        if ville and city_col:
            filtered = df[df[city_col] == ville]
            if filtered.empty:
                raise HTTPException(status_code=404, detail=f"Aucune donnée trouvée pour la ville: {ville}")
        
        niveau = _get_niveau_actuel(df, ville)
    except Exception as e:
        # En cas d'erreur ou dataset absent, on reste sur MODÉRÉ
        niveau = "MODÉRÉ"

    result = []
    # On récupère les dictionnaires pour la langue choisie
    meta_dict = PROFIL_META_BILINGUE.get(lang, PROFIL_META_BILINGUE["fr"])
    reco_dict = RECOMMANDATIONS_BILINGUE.get(lang, RECOMMANDATIONS_BILINGUE["fr"])

    for profil, meta in meta_dict.items():
        reco = reco_dict[niveau][profil]
        result.append(ProfilRecommandation(
            profil=meta["label"],
            icone=meta["icone"],
            niveau_risque=niveau,
            couleur=NIVEAU_COULEUR[niveau],
            message=reco["message"],
            actions=reco["actions"],
        ))
    return result
