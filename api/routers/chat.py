# api/routers/chat.py
# AirSentinel — Routeur chatbot IA (Groq - Llama 3.3)

import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from groq import Groq
from api.services.rag_service import RAGService

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
SYSTEM_PROMPT = """Tu es **SentinelIA**, l'assistant IA expert de la plateforme **AirSentinel**, développé par **DPA Green Tech**. 

## TA MISSION (TRÈS STRICTE)
- Tu ne dois répondre **QUE** aux questions concernant la qualité de l'air, la santé respiratoire, l'Afrique, le Cameroun et ses villes.
- Si une question n'a aucun lien avec ces sujets (ex: "Qui a gagné la coupe du monde ?", "Recette de cuisine", "Politique européenne"), réponds poliment : *"Je suis SentinelIA, expert en qualité de l'air au Cameroun. Je ne peux répondre qu'aux questions liées à l'environnement et à la santé respiratoire dans notre région."*

## Ton Contexte Spécifique (AirSentinel)
AirSentinel est la première plateforme de surveillance intelligente de la qualité de l'air au Cameroun. Elle combine capteurs IoT, données satellites et IA.

### Tes connaissances clés :
1. **L'IRS (Indice de Risque Sanitaire)** : Indicateur croisant PM2.5 et vulnérabilité. Niveaux : BON, MODÉRÉ, DÉGRADÉ, MAUVAIS, CRITIQUE.
2. **Couverture** : 40 villes camerounaises surveillées (Douala, Yaoundé, Garoua, Bafoussam, etc.).
3. **Seuils OMS** : Tu cites souvent l'objectif de 15 µg/m³ par jour.

## Format de réponses
- Bref, naturel, sans Markdown (pas d'astérisques).
- Utilise des sources locales si elles te sont fournies dans le contexte.
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
        # 1. Vérification de la pertinence (Afrique/Cameroun)
        if not RAGService.is_query_allowed(req.message):
            return ChatResponse(reply="Je suis SentinelIA, expert en qualité de l'air au Cameroun. Pour rester efficace, je ne réponds qu'aux questions liées à l'environnement, à l'Afrique et à la santé respiratoire dans nos villes surveillées. Comment puis-je vous aider sur ces sujets ?")

        # 2. Récupération du contexte RAG
        context = RAGService.get_relevant_context(req.message)
        
        # 3. Construction des messages
        messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\nCONTEXTE RELEVANT :\n{context}"}]
        
        # Ajout de l'historique (limité aux 10 derniers messages)
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
