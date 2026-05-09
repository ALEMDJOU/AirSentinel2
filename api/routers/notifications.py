# api/routers/notifications.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from api.core.database import get_db
from api.auth.dependencies import get_current_user
from api.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class FCMTokenUpdate(BaseModel):
    fcm_token: str


@router.post("/update-token")
async def update_fcm_token(
    data: FCMTokenUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Enregistre ou met à jour le token FCM de l'utilisateur actuel.
    """
    if not data.fcm_token.strip():
        raise HTTPException(status_code=400, detail="Le token FCM ne peut pas être vide.")

    current_user.fcm_token = data.fcm_token.strip()
    await db.commit()
    await db.refresh(current_user)  # FIX: sync ORM object after commit
    return {"message": "Token FCM mis à jour avec succès."}


@router.delete("/token")
async def delete_fcm_token(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Supprime le token FCM (utile lors de la déconnexion pour désabonner l'appareil).
    """
    current_user.fcm_token = None
    await db.commit()
    return {"message": "Token FCM supprimé."}
