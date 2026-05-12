# api/services/notification_service.py

import asyncio
import firebase_admin
from firebase_admin import credentials, messaging
import os
import logging

logger = logging.getLogger(__name__)

# Initialisation de Firebase (guard contre double initialisation)
try:
    if not firebase_admin._apps:
        cred = None
        # Priorité 1 : Fichier local (dev)
        cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase-service-account.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            logger.info("[Firebase] Initialisation via fichier JSON local.")
        
        # Priorité 2 : Variable d'environnement (Production / Render)
        else:
            firebase_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
            if firebase_json:
                import json
                try:
                    # Nettoyage des caractères d'échappement potentiels si collé brute
                    cleaned_json = firebase_json.strip()
                    if cleaned_json.startswith("'") or cleaned_json.startswith('"'):
                        cleaned_json = cleaned_json[1:-1]
                    
                    cred_dict = json.loads(cleaned_json)
                    cred = credentials.Certificate(cred_dict)
                    logger.info("[Firebase] Initialisation via variable d'environnement.")
                except Exception as e:
                    logger.error(f"[Firebase] Erreur lors du parsing de FIREBASE_SERVICE_ACCOUNT : {e}")

        if cred:
            firebase_admin.initialize_app(cred)
            logger.info("[Firebase] SDK initialisé avec succès.")
        else:
            logger.warning("[Firebase] Aucune configuration trouvée (ni fichier ni variable ENV).")
    else:
        logger.info("[Firebase] SDK déjà initialisé.")
except Exception as e:
    logger.error(f"[Firebase] Erreur d'initialisation : {e}")


class NotificationService:
    @staticmethod
    async def send_push_notification(token: str, title: str, body: str, data: dict = None):
        """
        Envoie une notification push via Firebase Cloud Messaging.
        Retourne True si succès, None si échec.
        """
        if not token:
            logger.warning("[Firebase] Token FCM vide, notification annulée.")
            return None

        if not firebase_admin._apps:
            logger.warning("[Firebase] Aucune application Firebase initialisée. Notification simulée.")
            return "simulated_success_id"

        # Les valeurs dans data doivent être des strings (exigence FCM)
        sanitized_data = {str(k): str(v) for k, v in (data or {}).items()}

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=sanitized_data,
            token=token,
        )

        try:
            # messaging.send() est bloquant — on l'exécute dans un thread séparé
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, lambda: messaging.send(message))
            logger.info(f"[Firebase] Notification envoyée avec succès : {response}")
            return response
        except firebase_admin.exceptions.InvalidArgumentError as e:
            logger.error(f"[Firebase] Token FCM invalide pour token={token[:20]}... : {e}")
            return None
        except Exception as e:
            logger.error(f"[Firebase] Échec de l'envoi de la notification : {e}")
            return None

    @classmethod
    async def send_air_quality_alert(cls, token: str, city: str, pm25: float, level: str):
        """
        Envoie une alerte spécifique à la qualité de l'air.
        """
        title = f"🚨 Alerte Qualité de l'Air : {level}"
        body = f"La concentration de PM2.5 à {city} est de {pm25} µg/m³. Prenez vos précautions."

        return await cls.send_push_notification(
            token=token,
            title=title,
            body=body,
            data={
                "city": city,
                "pm25": str(pm25),
                "level": level,
                "type": "air_quality_alert",
            },
        )
