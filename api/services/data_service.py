import pandas as pd
from pathlib import Path
from api.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

# Variable globale pour stocker le DataFrame en mémoire (Singleton)
_df = None

def get_dataframe() -> pd.DataFrame:
    """
    Charge le dataset Parquet en mémoire une seule fois et retourne le DataFrame.
    Gère le cas où le fichier n'existe pas.
    """
    global _df
    if _df is not None:
        return _df
        
    settings = get_settings()
    # On part de la racine du projet pour s'assurer que 'data/' est toujours trouvé
    project_root = Path(__file__).resolve().parent.parent.parent
    dataset_path = project_root / settings.DATASET_PATH
    
    if not dataset_path.exists():
        logger.error(f"Fichier introuvable: {dataset_path}")
        raise FileNotFoundError(f"Le fichier de données '{dataset_path}' n'existe pas.")
        
    try:
        try:
            _df = pd.read_parquet(dataset_path, engine='fastparquet')
        except Exception:
            # Fallback: certains envs n'ont pas fastparquet, on essaie pyarrow
            _df = pd.read_parquet(dataset_path, engine='pyarrow')

        # ─── VIRTUAL TIME SHIFT (Live Demo Mode) ───
        # Pour que l'app paraisse "Live", on décale les dates pour que le dataset finisse AUJOURD'HUI.
        if 'date' in _df.columns:
            max_date = _df['date'].max()
            today = pd.Timestamp.now().normalize()
            if not pd.isna(max_date):
                delta = today - max_date
                _df['date'] = _df['date'] + delta
                logger.info(f"Dataset décalé de {delta.days} jours pour correspondre à la date actuelle ({today.date()})")

        logger.info(f"Dataset chargé avec succès depuis {dataset_path}")
    except Exception as e:
        logger.error(f"Erreur lors du chargement du Parquet : {e}")
        raise
    
    return _df
    
def _find_col(df: pd.DataFrame, candidates: list[str]):
    """Cherche la première colonne disponible dans le DataFrame parmi une liste de candidats."""
    for col in candidates:
        if col in df.columns:
            return col
    return None

def apply_filters(df: pd.DataFrame, villes=None, regions=None, annee_min=2020, annee_max=2025) -> pd.DataFrame:
    """
    Applique des filtres géographiques et temporels sur le DataFrame.
    """
    filtered_df = df.copy()
    
    if villes:
        city_col = _find_col(df, ["ville", "city", "City", "Ville"])
        if city_col:
            # Filtrer par ville(s)
            if isinstance(villes, str): villes = [villes]
            filtered_df = filtered_df[filtered_df[city_col].str.lower().isin([v.lower() for v in villes])]
        
    if regions:
        region_col = _find_col(df, ["region", "Region", "Area"])
        if region_col:
            # Filtrer par région(s)
            if isinstance(regions, str): regions = [regions]
            filtered_df = filtered_df[filtered_df[region_col].str.lower().isin([r.lower() for r in regions])]
        
    # Filtrer par date (année) si la colonne date est bien présente et au format datetime
    if 'date' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['date'].dt.year >= annee_min) & 
            (filtered_df['date'].dt.year <= annee_max)
        ]
        
    return filtered_df
