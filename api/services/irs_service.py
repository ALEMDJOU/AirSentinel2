"""
api/services/irs_service.py

Calcul de l'Indice de Risque Sanitaire (IRS) en utilisant l'ACP pré-entraînée
et les seuils (percentiles) stockés via joblib.
"""

import numpy as np
import pandas as pd
from api.services.prediction_service import get_model

# Correspondance seuils → niveaux IRS
IRS_LEVELS = [
    (0.50, "FAIBLE", "#4CAF50"),
    (0.75, "MODÉRÉ", "#FFC107"),
    (0.90, "ÉLEVÉ", "#FF5722"),
    (1.00, "CRITIQUE", "#B71C1C"),
]


def compute_irs(features: dict) -> dict:
    """
    Calcule l'IRS à partir de variables météo/pollution.

    Paramètres attendus dans `features` :
        - Les noms des colonnes doivent correspondre exactement à ceux
          stockés dans cols_irs.joblib (chargés via get_model("cols")).
        - Ex : {"temperature": 32.5, "humidite": 78, "vent": 1.2, ...}

    Retourne :
        dict avec irs_value (float), irs_level (str), irs_color (str)

    TODO: Ajuster le calcul exact selon le notebook 05_irs_episodes.ipynb
    """

    # 1. Récupérer les colonnes attendues par le scaler/PCA
    cols = get_model("cols")        # list[str]
    scaler = get_model("scaler")    # sklearn StandardScaler
    pca = get_model("pca")          # sklearn PCA
    seuils = get_model("seuils")    # dict avec percentiles : {"p50": ..., "p75": ..., "p90": ...}

    # 2. Construire le DataFrame dans le bon ordre de colonnes
    try:
        X = pd.DataFrame([features])[cols]
    except KeyError as e:
        raise ValueError(
            f"La variable {e} est absente des features fournis. "
            f"Colonnes attendues : {cols}"
        )

    # 3. Standardisation
    X_scaled = scaler.transform(X)

    # 4. Réduction de dimension (ACP)
    X_pca = pca.transform(X_scaled)

    # 5. Score IRS = première composante principale
    # TODO: si l'IRS est une combinaison de plusieurs composantes, ajuster ici
    irs_score = float(X_pca[0, 0])

    # 6. Déterminer le niveau selon les seuils (percentiles)
    #    Valeurs par défaut si le modèle n'est pas chargé (basé sur une distribution standard)
    p50 = seuils.get("p50", 0.0)
    p75 = seuils.get("p75", 1.0)
    p90 = seuils.get("p90", 2.0)

    if irs_score <= p50:
        level, color = "FAIBLE", "#4CAF50"
    elif irs_score <= p75:
        level, color = "MODÉRÉ", "#FFC107"
    elif irs_score <= p90:
        level, color = "ÉLEVÉ", "#FF5722"
    else:
        level, color = "CRITIQUE", "#B71C1C"

    return {
        "irs_value": round(irs_score, 4),
        "irs_level": level,
        "irs_color": color,
    }


def classify_irs_score(irs_score: float, seuils: dict) -> tuple[str, str]:
    """
    Ré-utilisable partout : classifie un score IRS numérique.
    """
    p50 = seuils.get("p50", 0)
    p75 = seuils.get("p75", 1)
    p90 = seuils.get("p90", 2)

    if irs_score <= p50:
        return "FAIBLE", "#4CAF50"
    elif irs_score <= p75:
        return "MODÉRÉ", "#FFC107"
    elif irs_score <= p90:
        return "ÉLEVÉ", "#FF5722"
    else:
        return "CRITIQUE", "#B71C1C"
