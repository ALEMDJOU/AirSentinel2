import joblib
from pathlib import Path
from api.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

# Dictionnaire global pour stocker les modèles chargés
_models = {}

def load_all_models() -> None:
    """
    Charge tous les modèles .joblib présents dans le dossier models/ au démarrage.
    Ces modèles sont utilisés pour le calcul de l'IRS et les prédictions.
    """
    global _models
    settings = get_settings()
    # On part de la racine du projet pour s'assurer que 'models/' est toujours trouvé
    project_root = Path(__file__).resolve().parent.parent.parent
    models_path = project_root / settings.ML_MODELS_PATH
    
    files_to_load = {
        "modele": "meilleur_modele.pkl",
        "scaler": "scaler_acp_irs.pkl",
        "pca": "pca_irs.pkl",
        "cols": "cols_irs.pkl",
        "seuils": "seuils_irs.pkl",
        "scaler_pm25": "scaler.pkl",
        "features_list": "features.pkl",
        "arima": "arima_par_zone.pkl"
    }
    
    for key, filename in files_to_load.items():
        file_path = models_path / filename
        
        if not file_path.exists():
            logger.error(f"Le fichier de modèle '{file_path}' est introuvable.")
            continue # Ne pas bloquer tout le chargement si un fichier manque
        
        try:
            _models[key] = joblib.load(file_path)
            logger.info(f"Modèle '{key}' chargé avec succès depuis {filename}.")
        except Exception as e:
            logger.error(f"Erreur inattendue lors du chargement du modèle {filename}: {e}")

def get_model(name: str):
    """
    Retourne l'objet modèle correspondant à la clé demandée.
    Charge les modèles s'ils ne l'ont pas encore été.
    """
    if not _models:
        logger.warning("Les modèles n'ont pas encore été chargés... Chargement automatique en cours.")
        load_all_models()
        
    if name not in _models:
        raise KeyError(
            f"Le modèle '{name}' n'est pas disponible. "
            f"Modèles disponibles : {list(_models.keys())}"
        )
        
    return _models[name]

def _get_zone(region: str) -> str:
    """
    Zones INS Cameroun (2019) pour le modèle ARIMA.
    """
    ZONES_REGIONS = {
        'Zone équatoriale':        ['Centre', 'Est', 'Sud', 'Littoral', 'Sud-Ouest', 'Ouest', 'Nord-Ouest'],
        'Zone soudanienne':        ['Adamaoua', 'Nord'],
        'Zone soudano-sahélienne': ['Extreme-Nord'],
    }
    for zone, regions in ZONES_REGIONS.items():
        if region in regions:
            return zone
    return 'Zone équatoriale'

def predict_pm25(features_dict: dict, region: str = "Centre", steps: int = 1) -> float:
    """
    Effectue une prédiction PM2.5 hybride (RL + ARIMA) en utilisant les modèles joblib.
    """
    try:
        model = get_model("modele")
        scaler = get_model("scaler_pm25")
        features_list = get_model("features_list")
        arima_models = get_model("arima")
        
        import pandas as pd
        import numpy as np
        
        # 1. Partie Régression (RL)
        input_data = {}
        for col in features_list:
            input_data[col] = float(features_dict.get(col, 0.0))
            
        X = pd.DataFrame([input_data])[features_list]
        X_scaled = scaler.transform(X)
        p_rl = float(model.predict(X_scaled)[0])
        
        # 2. Partie Temporelle (ARIMA)
        zone = _get_zone(region)
        try:
            # On récupère la prédiction ARIMA pour l'horizon 'steps'
            # steps=1 -> Aujourd'hui/Dernier relevé
            p_arima = float(arima_models[zone].forecast(steps=steps).iloc[-1])
        except Exception as arima_err:
            logger.warning(f"Erreur ARIMA pour la zone {zone}, fallback à 0: {arima_err}")
            p_arima = 0.0
            
        # 3. Combinaison Hybride
        prediction = max(0, p_rl + p_arima)
        
        return float(prediction)
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction PM2.5 hybride : {e}")
        # Fallback sur une valeur par défaut cohérente
        return 25.0
