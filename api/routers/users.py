import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import create_client, Client

from api.core.database import get_db
from api.core.config import get_settings
from api.models.user import User
from api.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

settings = get_settings()

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/test")
async def test_users_router():
    return {"status": "ok", "message": "Users router is working and reachable."}


# Initialisation du client Supabase pour le stockage
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Télécharge un avatar vers Supabase Storage et met à jour l'URL de profil de l'utilisateur.
    - Types autorisés : JPEG, PNG, WEBP
    - Taille max : 2 Mo
    """
    # 1. Validation du type de fichier
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de fichier non supporté. Types autorisés : {', '.join(ALLOWED_TYPES)}"
        )
    
    # 2. Validation de la taille (2 Mo = 2 * 1024 * 1024 octets)
    file_size = 0
    contents = await file.read()
    file_size = len(contents)
    if file_size > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier est trop volumineux (max 2 Mo)."
        )
    # Re-pointer vers le début pour d'éventuelles autres lectures
    await file.seek(0)
    
    # 3. Préparation du nom de fichier unique
    file_ext = file.filename.split(".")[-1]
    file_name = f"{current_user.id}_{uuid.uuid4().hex}.{file_ext}"
    path_on_supabase = f"avatars/{file_name}"
    
    # 4. Upload vers Supabase Storage (Tentatives sur plusieurs buckets)
    bucket_name = "profile-pictures" # Nom initial
    buckets_to_try = [bucket_name, "avatars", "profile"]
    last_error = ""
    upload_success = False
    final_bucket = bucket_name
    
    try:
        for b in buckets_to_try:
            try:
                supabase.storage.from_(b).upload(
                    path=path_on_supabase,
                    file=contents,
                    file_options={"content-type": file.content_type}
                )
                upload_success = True
                final_bucket = b
                break
            except Exception as e:
                last_error = str(e)
                continue
        
        if not upload_success:
            # Gérer les erreurs Supabase de façon plus explicite
            error_msg = last_error
            if "bucket_not_found" in error_msg.lower() or "bucket not found" in error_msg.lower():
                error_msg = f"Aucun bucket valide trouvé (tentés : {', '.join(buckets_to_try)}). Veuillez en créer un dans Supabase."
            elif "policy" in error_msg.lower():
                error_msg = "Erreur de permissions (RLS Policy) sur Supabase. L'accès en écriture est refusé."

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur Supabase : {error_msg}"
            )

        # 5. Récupération de l'URL publique
        public_url = str(supabase.storage.from_(final_bucket).get_public_url(path_on_supabase))
        
        # 6. Mise à jour de l'utilisateur dans la base de données
        current_user.avatar_url = public_url
        await db.commit()
        await db.refresh(current_user)
        
        return {"avatar_url": public_url}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors de l'upload : {str(e)}"
        )
class SubscriptionUpdate(BaseModel):
    subscribed_city: Optional[str] = None
    is_alerts_enabled: Optional[bool] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    subscribed_city: Optional[str] = None
    is_alerts_enabled: Optional[bool] = None

@router.patch("/me")
async def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Met à jour les informations de profil de l'utilisateur.
    """
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    
    if payload.email is not None:
        # Vérifier si l'email est déjà pris
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == payload.email, User.id != current_user.id))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")
        current_user.email = payload.email
        
    if payload.subscribed_city is not None:
        current_user.subscribed_city = payload.subscribed_city
        # Si on définit une ville, on active généralement les alertes par défaut
        if payload.is_alerts_enabled is None:
             current_user.is_alerts_enabled = True
             
    if payload.is_alerts_enabled is not None:
        current_user.is_alerts_enabled = payload.is_alerts_enabled
        
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.put("/me/subscription")
async def update_subscription(
    payload: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Met à jour les préférences d'alertes (activation/désactivation et ville).
    """
    if payload.subscribed_city is not None:
        current_user.subscribed_city = payload.subscribed_city
        
    if payload.is_alerts_enabled is not None:
        current_user.is_alerts_enabled = payload.is_alerts_enabled
    else:
        # Si is_alerts_enabled n'est pas fourni, on suppose qu'on veut basculer
        # ou garder l'état actuel selon si subscribed_city est vide ou pas
        # (compatibilité avec l'ancien comportement)
        if payload.subscribed_city == "":
            current_user.is_alerts_enabled = False
        elif payload.subscribed_city:
            current_user.is_alerts_enabled = True

    # Réinitialiser le cool-down si on réactive les alertes
    if current_user.is_alerts_enabled:
        current_user.last_alert_sent = None
    
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "status": "success",
        "is_alerts_enabled": current_user.is_alerts_enabled,
        "subscribed_city": current_user.subscribed_city,
        "message": "Préférences d'alertes mises à jour."
    }
