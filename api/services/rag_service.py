import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class RAGService:
    """
    Service simple de Retrieval Augmented Generation (RAG).
    Recherche des informations pertinentes dans la base de connaissances locale.
    """
    _knowledge_base: Dict[str, Any] = {}

    @classmethod
    def load_kb(cls):
        """Charge la base de connaissances depuis le fichier JSON."""
        kb_path = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"
        if not kb_path.exists():
            logger.warning(f"Base de connaissances introuvable : {kb_path}")
            return
        
        try:
            with open(kb_path, "r", encoding="utf-8") as f:
                cls._knowledge_base = json.load(f)
            logger.info("Base de connaissances RAG chargée.")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la KB : {e}")

    @classmethod
    def get_relevant_context(cls, query: str) -> str:
        """
        Recherche rudimentaire par mots-clés dans la base de connaissances.
        Retourne une chaîne de contexte à injecter dans le prompt.
        """
        if not cls._knowledge_base:
            cls.load_kb()
        
        query = query.lower()
        context_parts = []

        # Recherche dans les infos générales
        for key, val in cls._knowledge_base.get("general_cameroon", {}).items():
            if key in query or any(word in query for word in key.split("_")):
                context_parts.append(val)

        # Recherche technique
        for key, val in cls._knowledge_base.get("technical_details", {}).items():
            if key in query:
                context_parts.append(f"TECHNIQUE: {val}")

        # Recherche dans les villes
        for city, info in cls._knowledge_base.get("city_specific", {}).items():
            if city.lower() in query:
                context_parts.append(f"VVILLE {city}: {info}")

        # Recherche dans les recos santé
        for target, info in cls._knowledge_base.get("health_tips_pro", {}).items():
            if target in query:
                context_parts.append(f"CONSEIL SANTÉ: {info}")
        
        for target, info in cls._knowledge_base.get("health_recommendations_cameroon", {}).items():
            if target in query:
                context_parts.append(info)

        if not context_parts:
            return "Aucune source locale spécifique trouvée pour cette requête."

        return "SOURCES LOCALES CAMEROUNAISES :\n" + "\n".join(context_parts)

    @classmethod
    def is_query_allowed(cls, query: str) -> bool:
        """
        Vérifie si la question concerne l'Afrique, le Cameroun ou les villes surveillées.
        """
        query = query.lower()
        allowed_keywords = ["cameroun", "cameroon", "afrique", "africa", "air", "pollution", "pm25", "irs", "santé", "health"]
        
        # Vérification des villes
        cities = cls._knowledge_base.get("eligible_cities", [])
        if any(city.lower() in query for city in cities):
            return True
        
        # Vérification des mots-clés généraux
        if any(kw in query for kw in allowed_keywords):
            return True
            
        return False
