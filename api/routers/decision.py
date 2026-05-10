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


# Recommandations statiques par niveau IRS × profil (Optimisé OMS 2021)
RECOMMANDATIONS = {
    "EXCELLENT": {
        "enfant": {
            "message": "Air d'une pureté exceptionnelle. Activités extérieures vivement encouragées.",
            "actions": ["Sport intense sans limite", "Aération maximale"]
        },
        "adulte": {
            "message": "Qualité d'air idéale. Aucune restriction pour les activités sportives.",
            "actions": ["Activités de plein air", "Ventilation naturelle"]
        },
        "personne_agee": {
            "message": "Conditions parfaites. Sorties conseillées pour la santé.",
            "actions": ["Promenade", "Aération des chambres"]
        },
        "asthmatique": {
            "message": "Air très pur. Profitez du plein air sereinement.",
            "actions": ["Activités normales", "Surveillance habituelle"]
        },
    },
    "BON": {
        "enfant": {
            "message": "Qualité de l'air satisfaisante. Les activités extérieures sont conseillées.",
            "actions": ["Activités sportives possibles", "Pas de restriction"]
        },
        "adulte": {
            "message": "Air sain. Profitez des activités en plein air sans restriction.",
            "actions": ["Activités normales", "Ventilation recommandée"]
        },
        "personne_agee": {
            "message": "Conditions favorables. Sortie possible sans précaution.",
            "actions": ["Promenade conseillée", "Pas de masque"]
        },
        "asthmatique": {
            "message": "Risque faible. Gardez votre inhalateur par précaution.",
            "actions": ["Sortie possible", "Surveiller les symptômes"]
        },
    },
    "MODERE": {
        "enfant": {
            "message": "Qualité d'air modérée. Limitez les efforts intenses prolongés.",
            "actions": ["Réduire le sport intense", "Aérer hors heures de pointe"]
        },
        "adulte": {
            "message": "Léger risque pour les sensibles. Réduisez les expositions prolongées.",
            "actions": ["Limiter les efforts physiques", "Éviter les zones de trafic"]
        },
        "personne_agee": {
            "message": "Prudence conseillée. Privilégiez les activités calmes.",
            "actions": ["Limiter les sorties longues", "Aération filtrée"]
        },
        "asthmatique": {
            "message": "Risque modéré. Portez un masque FFP2 par précaution.",
            "actions": ["Porter un masque FFP2", "Avoir bronchodilatateur à portée"]
        },
    },
    "DEGRADE": {
        "enfant": {
            "message": "Air pollué. Réduisez significativement les sorties.",
            "actions": ["Activités en intérieur", "Fermer les fenêtres", "Pas de sport extérieur"]
        },
        "adulte": {
            "message": "Qualité médiocre. Évitez les efforts physiques en extérieur.",
            "actions": ["Porter un masque", "Privilégier le sport en salle", "Limiter les déplacements"]
        },
        "personne_agee": {
            "message": "Vulnérabilité accrue. Restez à l'intérieur autant que possible.",
            "actions": ["Sorties brèves uniquement", "Vérifier la ventilation", "Surveiller le pouls"]
        },
        "asthmatique": {
            "message": "Alerte dégradation. Risque de crise accru.",
            "actions": ["Rester en intérieur", "Doubler de vigilance", "Traitement de fond rigoureux"]
        },
    },
    "MAUVAIS": {
        "enfant": {
            "message": "Air de mauvaise qualité. Interdiction de sport en extérieur.",
            "actions": ["Annuler sorties scolaires", "Fermer fenêtres", "Purificateur d'air"]
        },
        "adulte": {
            "message": "Pollution marquée. Limitez toute activité extérieure.",
            "actions": ["Télétravail conseillé", "Masque FFP2 obligatoire", "Éviter tout effort"]
        },
        "personne_agee": {
            "message": "Danger pour les vulnérables. Restez confiné.",
            "actions": ["Ne pas sortir", "Fermer tout accès", "Contact médical si besoin"]
        },
        "asthmatique": {
            "message": "Risque élevé. Activation du plan d'action asthme.",
            "actions": ["Confinement strict", "Prévenir un proche", "Inhalateur à portée de main"]
        },
    },
    "CRITIQUE": {
        "enfant": {
            "message": "🚨 Urgence sanitaire. Ne pas exposer les enfants à l'extérieur.",
            "actions": ["Évacuation si possible", "Fermer hermétiquement", "Appeler urgences si détresse"]
        },
        "adulte": {
            "message": "🚨 Pollution critique. Confinement obligatoire.",
            "actions": ["Rester confiné", "Masque FFP3 impératif", "Rester près d'un téléphone"]
        },
        "personne_agee": {
            "message": "🚨 Risque vital. Alerte rouge absolue.",
            "actions": ["Confinement total", "Surveillance médicale constante", "Oxygène si besoin"]
        },
        "asthmatique": {
            "message": "🚨 Situation critique. Protocole d'urgence vitale.",
            "actions": ["Appeler secours", "Utilisation bronchodilatateurs", "Confinement hermétique"]
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
    "EXCELLENT": "#008000",
    "BON": "#4CAF50",
    "MODERE": "#FFC107",
    "DEGRADE": "#FF9800",
    "MAUVAIS": "#FF5722",
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
