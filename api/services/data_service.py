import pandas as pd
from pathlib import Path
from api.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

# Variables globales pour stocker le DataFrame et le timestamp du fichier
_df = None
_last_mtime = 0

def get_dataframe() -> pd.DataFrame:
    """
    Charge le dataset Parquet en mémoire.
    Recharge automatiquement si le fichier sur le disque a été modifié.
    """
    global _df, _last_mtime
    
    settings = get_settings()
    project_root = Path(__file__).resolve().parent.parent.parent
    dataset_path = project_root / settings.DATASET_PATH
    
    if not dataset_path.exists():
        logger.error(f"Fichier introuvable: {dataset_path}")
        raise FileNotFoundError(f"Le fichier de données '{dataset_path}' n'existe pas.")
        
    # Vérification de la date de modification
    current_mtime = dataset_path.stat().st_mtime
    
    if _df is not None and current_mtime <= _last_mtime:
        return _df

    logger.info(f"Chargement (ou rechargement) du dataset depuis {dataset_path}...")
    try:
        try:
            new_df = pd.read_parquet(dataset_path, engine='fastparquet')
        except Exception:
            new_df = pd.read_parquet(dataset_path, engine='pyarrow')

        # ─── VIRTUAL TIME SHIFT (Live Demo Mode) ───
        if 'date' in new_df.columns:
            max_date = new_df['date'].max()
            today = pd.Timestamp.now().normalize()
            if not pd.isna(max_date) and max_date < today:
                delta = today - max_date
                new_df['date'] = new_df['date'] + delta
                logger.info(f"Dataset décalé de {delta.days} jours pour correspondre à la date actuelle")

        _df = new_df
        _last_mtime = current_mtime
        logger.info(f"Dataset chargé avec succès. Taille: {len(_df)} lignes")
    except Exception as e:
        logger.error(f"Erreur lors du chargement du Parquet : {e}")
        if _df is not None:
            logger.warning("Utilisation de l'ancienne version en mémoire suite à l'erreur.")
            return _df
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
