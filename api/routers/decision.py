"""
api/routers/decision.py

Endpoint GET /decision/real — Recommandations santé par profil selon qualité de l'air.
"""

import pandas as pd
from fastapi import APIRouter, HTTPException
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


# Recommandations statiques par niveau IRS × profil
RECOMMANDATIONS = {
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
            "actions": ["Réduire les activités sportives intenses", "Aérer les locaux en dehors des heures de pointe"]
        },
        "adulte": {
            "message": "Léger risque pour les personnes sensibles. Réduisez les expositions prolongées.",
            "actions": ["Limiter les activités physiques prolongées", "Éviter les zones à fort trafic"]
        },
        "personne_agee": {
            "message": "Prudence conseillée. Privilégiez les activités en intérieur.",
            "actions": ["Rester à l'intérieur si possible", "Consulter un médecin si gêne respiratoire"]
        },
        "asthmatique": {
            "message": "Risque modéré. Portez masque FFP2 en extérieur et ayez votre traitement.",
            "actions": ["Porter un masque FFP2", "Éviter les efforts physiques", "Avoir bronchodilatateur à portée"]
        },
    },
    "ÉLEVÉ": {
        "enfant": {
            "message": "Qualité d'air dégradée. Restez à l'intérieur autant que possible.",
            "actions": ["Annuler les sorties scolaires", "Fermer les fenêtres", "Purificateur d'air si disponible"]
        },
        "adulte": {
            "message": "Air de mauvaise qualité. Limitez toute activité extérieure.",
            "actions": ["Télétravail si possible", "Porter masque FFP2", "Éviter tout effort en extérieur"]
        },
        "personne_agee": {
            "message": "Danger pour les personnes vulnérables. Restez en intérieur.",
            "actions": ["Ne pas sortir", "Fermer portes et fenêtres", "Contacter les services médicaux si symptômes"]
        },
        "asthmatique": {
            "message": "Risque élevé. Activation du plan d'action asthme recommandée.",
            "actions": ["Rester en intérieur obligatoirement", "Augmenter traitement préventif si prescrit", "Alerter un médecin"]
        },
    },
    "CRITIQUE": {
        "enfant": {
            "message": "🚨 Urgence sanitaire. Ne pas exposer les enfants à l'extérieur.",
            "actions": ["Évacuation des zones les plus exposées si possible", "Fermer hermétiquement", "Appeler le 115 si détresse"]
        },
        "adulte": {
            "message": "🚨 Pollution critique. Confinement recommandé.",
            "actions": ["Rester confiné", "Masque FFP3 si sortie indispensable", "Rester près d'un téléphone"]
        },
        "personne_agee": {
            "message": "🚨 Risque vital. Alerte rouge pour les personnes âgées.",
            "actions": ["Confinement total", "Contact famille/services sociaux", "Assistance médicale immédiate si symptômes"]
        },
        "asthmatique": {
            "message": "🚨 Situation critique. Protocole d'urgence asthme à activer.",
            "actions": ["Appeler le 115", "Utilisation immédiate des bronchodilatateurs", "Ne pas sortir sous aucun prétexte"]
        },
    },
}

PROFIL_META = {
    "enfant": {"icone": "👶", "label": "Enfant (< 12 ans)"},
    "adulte": {"icone": "🧑", "label": "Adulte"},
    "personne_agee": {"icone": "👴", "label": "Personne âgée"},
    "asthmatique": {"icone": "🫁", "label": "Personne asthmatique"},
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
def get_recommandations(ville: Optional[str] = None):
    """
    Retourne les recommandations de santé pour les 4 profils selon le niveau IRS actuel.
    Le niveau est calculé dynamiquement depuis les dernières données du dataset.
    Si une ville est spécifiée, le niveau est calculé uniquement pour cette ville.
    """
    try:
        df = get_dataframe()
        
        city_col = _find_col(df, ["ville", "city"])
        if ville and city_col:
            filtered = df[df[city_col] == ville]
            if filtered.empty:
                raise HTTPException(status_code=404, detail=f"Aucune donnée trouvée pour la ville: {ville}")
        
        niveau = _get_niveau_actuel(df, ville)
    except FileNotFoundError:
        niveau = "MODÉRÉ"  # Valeur par défaut si dataset absent

    result = []
    for profil, meta in PROFIL_META.items():
        reco = RECOMMANDATIONS[niveau][profil]
        result.append(ProfilRecommandation(
            profil=meta["label"],
            icone=meta["icone"],
            niveau_risque=niveau,
            couleur=NIVEAU_COULEUR[niveau],
            message=reco["message"],
            actions=reco["actions"],
        ))
    return result
