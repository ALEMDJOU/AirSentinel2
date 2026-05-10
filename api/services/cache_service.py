import time
import functools
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class CacheService:
    """
    Service de cache en mémoire simple pour optimiser les performances de l'API.
    Évite de recalculer les agrégations lourdes (stats, cartes) à chaque requête.
    """
    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """Récupère une valeur du cache si elle n'est pas expirée."""
        if key in cls._cache:
            entry = cls._cache[key]
            if time.time() < entry['expires_at']:
                return entry['value']
            else:
                del cls._cache[key]
        return None

    @classmethod
    def set(cls, key: str, value: Any, ttl: int = 300):
        """Stocke une valeur dans le cache avec une durée de vie (TTL) en secondes."""
        cls._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }

    @classmethod
    def clear(cls):
        """Vide l'intégralité du cache."""
        cls._cache.clear()

def cached_endpoint(ttl: int = 300):
    """
    Décorateur pour mettre en cache le résultat d'un endpoint FastAPI.
    Utilise le nom de la fonction et ses arguments comme clé de cache.
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Construction d'une clé de cache basée sur le nom et les arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_val = CacheService.get(key)
            if cached_val is not None:
                logger.info(f"Cache HIT for {key}")
                return cached_val
            
            # Appel de la fonction originale
            result = await func(*args, **kwargs)
            CacheService.set(key, result, ttl)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_val = CacheService.get(key)
            if cached_val is not None:
                logger.info(f"Cache HIT for {key}")
                return cached_val
            
            result = func(*args, **kwargs)
            CacheService.set(key, result, ttl)
            return result

        import asyncio
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
