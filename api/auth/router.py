from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from api.core.database import get_db
from api.core.config import get_settings
from api.models.user import User
from api.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserRegisterResponse
from api.auth.service import hash_password, verify_password, create_access_token
from api.auth.dependencies import get_current_user
from api.services.mail_service import EmailService
from api.services.alert_service import AlertService

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Auth"])



@router.post("/register", response_model=UserRegisterResponse)
async def register(
    user_in: UserCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Enregistre un nouvel utilisateur et renvoie un token immédiatement.
    """
    # Vérification de l'existence de l'utilisateur
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé."
        )
    
    # Création du nouvel utilisateur
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        subscribed_city=user_in.subscribed_city,
        is_active=True,
        is_alerts_enabled=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Envoi du mail de bienvenue en arrière-plan
    background_tasks.add_task(
        EmailService.send_welcome_email, 
        new_user.email, 
        new_user.full_name or "Sentinel", 
        new_user.subscribed_city or "votre région"
    )
    
    # Vérification immédiate de la pollution pour envoyer une alerte si besoin
    # FIX BUG 4 : on ne peut pas passer `db` (session liée à la requête HTTP) à une
    # background task, car la session est fermée avant que la tâche s'exécute.
    # On passe plutôt l'ID de l'utilisateur et on crée une nouvelle session dans la tâche.
    user_id = new_user.id
    async def _trigger_alert_with_new_session():
        from api.core.database import AsyncSessionLocal
        from sqlalchemy import select
        from api.models.user import User as UserModel
        async with AsyncSessionLocal() as fresh_db:
            result_u = await fresh_db.execute(select(UserModel).where(UserModel.id == user_id))
            fresh_user = result_u.scalars().first()
            if fresh_user:
                await AlertService.trigger_immediate_alert(fresh_user, fresh_db)

    background_tasks.add_task(_trigger_alert_with_new_session)
    
    # Génération du token immédiat (pour éviter un second appel /login)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user.id)}, 
        expires_delta=access_token_expires
    )
    
    return {
        "user": new_user,
        "token": {
            "access_token": access_token, 
            "token_type": "bearer"
        }
    }


@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin, 
    db: AsyncSession = Depends(get_db)
):
    """
    Authentifie l'utilisateur via JSON et génère un token d'accès.
    """
    # Recherche de l'utilisateur
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()
    
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisateur inactif."
        )

    # Génération du token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Récupère les informations de l'utilisateur actuellement connecté.
    """
    return current_user
