# api/services/notification_service.py

import asyncio
import firebase_admin
from firebase_admin import credentials, messaging
import os
import logging

logger = logging.getLogger(__name__)

# Initialisation de Firebase (guard contre double initialisation)
try:
    cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase-service-account.json")
    if os.path.exists(cred_path):
        # Évite l'erreur "app already exists" si le module est rechargé
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("[Firebase] SDK initialisé avec succès.")
        else:
            logger.info("[Firebase] SDK déjà initialisé, skip.")
    else:
        logger.warning("[Firebase] Fichier de clé non trouvé. Les notifications seront simulées.")
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
