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
        "seuils": "seuils_irs.pkl"
    }
    
    for key, filename in files_to_load.items():
        file_path = models_path / filename
        
        if not file_path.exists():
            logger.error(f"Le fichier de modèle '{file_path}' est introuvable.")
            raise FileNotFoundError(f"Erreur critique: Le modèle requis '{file_path}' n'existe pas.")
        
        try:
            _models[key] = joblib.load(file_path)
            logger.info(f"Modèle '{key}' chargé avec succès depuis {filename}.")
        except Exception as e:
            logger.error(f"Erreur inattendue lors du chargement du modèle {filename}: {e}")
            raise

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
