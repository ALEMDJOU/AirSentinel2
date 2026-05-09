# api/routers/chat.py
# AirSentinel — Routeur chatbot IA (Groq - Llama 3.3)

import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from groq import Groq

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chatbot IA"])

# ──────────────────────────────────────────────
# Initialisation Groq
# ──────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = None

if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        logger.info("[Chat] SDK Groq configuré.")
    except Exception as e:
        logger.error(f"[Chat] Erreur lors de la configuration de Groq : {e}")
else:
    logger.warning("[Chat] GROQ_API_KEY manquante. Le chatbot sera en mode dégradé.")

# ──────────────────────────────────────────────
# Prompt système AirSentinel
# ──────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es **SentinelIA**, l'assistant IA expert de la plateforme **AirSentinel**, développée par **DPA Green Tech**. 

## Ton Contexte Spécifique (AirSentinel)
AirSentinel est la première plateforme de surveillance intelligente de la qualité de l'air au Cameroun. Elle combine capteurs IoT, données satellites et intelligence artificielle pour protéger la santé des populations.

### Tes connaissances clés sur la plateforme :
1. **L'IRS (Indice de Risque Sanitaire)** : C'est un indicateur unique qui croise la concentration de polluants (PM2.5, PM10) avec la vulnérabilité des zones. Niveaux : BON, MODÉRÉ, DÉGRADÉ, MAUVAIS.
2. **Couverture Géographique** : Priorité sur les zones urbaines denses (Yaoundé, Douala) et les zones touchées par l'harmattan (Maroua, Nord).
3. **Fonctionnalités** : Carte interactive en temps réel, prévisions à 24h, notifications push d'alerte pollution, et conseils personnalisés pour les personnes sensibles (asthmatiques, enfants).
4. **L'Objectif** : Réduire l'impact des maladies respiratoires et aider les mairies à prendre des décisions (circulation, zones vertes).

## Ton rôle
Répondre avec expertise, empathie et précision aux utilisateurs. Tu dois :
- Expliquer pourquoi l'air est pollué (ex: Harmattan entre décembre et mars, émissions de véhicules à Douala).
- Donner des conseils de protection **immédiats** (porter un masque, éviter le sport en extérieur).
- Valoriser l'utilisation de l'application (ex: "Activez vos notifications pour être alerté dès que le seuil PM2.5 est dépassé à Yaoundé").

## Format de réponses
- Style **professionnel et moderne**.
- Utilise des **listes à puces** pour la clarté.
- Termine par une note d'encouragement ou de prévention.

## Avertissement obligatoire
Si la question concerne un diagnostic médical, ajoute : *"⚕️ SentinelIA fournit des recommandations environnementales. Consultez un médecin pour tout avis médical."*
"""


# ──────────────────────────────────────────────
# Schémas Pydantic
# ──────────────────────────────────────────────
class ChatHistoryItem(BaseModel):
    role: str   # "user" ou "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatHistoryItem]] = []


class ChatResponse(BaseModel):
    reply: str
    model: str = "llama-3.3-70b-versatile"


# ──────────────────────────────────────────────
# Endpoint principal
# ──────────────────────────────────────────────
@router.post("/ask", response_model=ChatResponse)
async def chat_ask(req: ChatRequest):
    """
    Envoie un message à Groq (Llama 3.3) avec le contexte de l'historique.
    Retourne la réponse de l'assistant SentinelIA.
    """
    if not client:
        raise HTTPException(
            status_code=503,
            detail="Service IA Groq non configuré. Contactez l'administrateur."
        )

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide.")

    if len(req.message) > 2000:
        raise HTTPException(status_code=400, detail="Message trop long (max 2000 caractères).")

    try:
        # Construction des messages pour Groq (format OpenAI)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Ajout de l'historique (limité aux 10 derniers messages pour éviter de dépasser les tokens)
        history_context = (req.history or [])[-10:]
        for item in history_context:
            role = "assistant" if item.role == "assistant" else "user"
            messages.append({"role": role, "content": item.content})
            
        # Ajout du message actuel
        messages.append({"role": "user", "content": req.message})

        # Appel à l'API Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        reply_text = completion.choices[0].message.content

        logger.info(f"[Chat] Réponse Groq générée ({len(reply_text)} caractères).")
        return ChatResponse(reply=reply_text)

    except Exception as e:
        logger.error(f"[Chat] Erreur Groq : {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de la réponse IA : {str(e)}"
        )
