# AirSentinel Cameroun — API FastAPI
# Auteur : Henri Joël — ENSP Yaoundé
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.core.config import get_settings
from api.routers import kpis, carte, predictions, alertes, decision, contexte, users, notifications, chat
from api.auth.router import router as auth_router
import asyncio
from api.services.alert_service import AlertService
from api.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Chargement des ressources lourdes au démarrage de l'API."""
    logger.info("Chargement des modèles ML...")
    try:
        from api.services.prediction_service import load_all_models
        load_all_models()
        logger.info("Modèles ML chargés avec succès.")
    except FileNotFoundError as e:
        logger.warning(f"Modèles ML non disponibles (mode dégradé) : {e}")

    # Lancement du planificateur d'alertes en arrière-plan
    async def alert_scheduler():
        logger.info("Planificateur d'alertes démarré (Fréquence : 1 heure).")
        while True:
            try:
                async with AsyncSessionLocal() as db:
                    await AlertService.process_alerts(db)
            except Exception as e:
                logger.error(f"Erreur critique dans le scheduler d'alertes : {e}")
            await asyncio.sleep(3600)

    alert_task = asyncio.create_task(alert_scheduler())

    yield

    logger.info("Arrêt de l'API AirSentinel.")
    alert_task.cancel()
    try:
        await alert_task  # FIX: attendre la fin propre pour éviter les warnings asyncio
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="AirSentinel API",
    description="Prédiction et surveillance de la qualité de l'air au Cameroun — IndabaX 2026",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────
origins = settings.ALLOWED_ORIGINS
# FIX: avec allow_origins=["*"], allow_credentials=True est invalide (erreur navigateur).
# En DEBUG on autorise tout mais on désactive les credentials
if settings.DEBUG:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False if "*" in origins else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routeurs ─────────────────────────────────────────────────────
app.include_router(auth_router,        prefix=settings.API_PREFIX)
app.include_router(users.router,       prefix=settings.API_PREFIX)
app.include_router(kpis.router,        prefix=settings.API_PREFIX)
app.include_router(carte.router,       prefix=settings.API_PREFIX)
app.include_router(predictions.router, prefix=settings.API_PREFIX)
app.include_router(alertes.router,     prefix=settings.API_PREFIX)
app.include_router(decision.router,    prefix=settings.API_PREFIX)
app.include_router(contexte.router,    prefix=settings.API_PREFIX)
app.include_router(notifications.router, prefix=settings.API_PREFIX)
app.include_router(chat.router,          prefix=settings.API_PREFIX)


# ─── Endpoints de base ────────────────────────────────────────────
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse, tags=["Général"])
def accueil():
    """Page d'accueil riche pour l'API AirSentinel."""
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AirSentinel API — Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #10b981;
                --primary-dark: #059669;
                --dark: #0f172a;
                --light: #f8fafc;
            }}
            body {{
                font-family: 'Outfit', sans-serif;
                background-color: var(--dark);
                color: var(--light);
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                overflow: hidden;
            }}
            .container {{
                text-align: center;
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                padding: 3rem;
                border-radius: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                max-width: 600px;
                animation: fadeIn 0.8s ease-out;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            h1 {{
                font-size: 3rem;
                margin-bottom: 0.5rem;
                background: linear-gradient(to right, #10b981, #3b82f6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            p {{
                font-size: 1.1rem;
                color: #94a3b8;
                line-height: 1.6;
            }}
            .badge {{
                display: inline-block;
                padding: 0.5rem 1rem;
                background: rgba(16, 185, 129, 0.1);
                color: var(--primary);
                border-radius: 2rem;
                font-weight: 600;
                margin-bottom: 2rem;
            }}
            .btn-group {{
                display: flex;
                gap: 1rem;
                justify-content: center;
                margin-top: 2rem;
            }}
            .btn {{
                padding: 0.8rem 2rem;
                border-radius: 0.75rem;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            .btn-primary {{
                background-color: var(--primary);
                color: white;
            }}
            .btn-primary:hover {{
                background-color: var(--primary-dark);
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.4);
            }}
            .btn-secondary {{
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }}
            .btn-secondary:hover {{
                background: rgba(255, 255, 255, 0.2);
            }}
            .footer {{
                margin-top: 3rem;
                font-size: 0.8rem;
                color: #64748b;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="badge">IndabaX Cameroon 2026</div>
            <h1>🌍 AirSentinel</h1>
            <p>Système intelligent de surveillance et de prédiction de la qualité de l'air au Cameroun par <b>DPA Green Tech</b>.</p>
            
            <div class="btn-group">
                <a href="{settings.API_PREFIX}/docs" class="btn btn-primary">🚀 Tester l'API (Swagger)</a>
                <a href="/health" class="btn btn-secondary">⚡ Santé</a>
            </div>

            <div class="footer">
                Version 1.0.0 • Développé par Henri Joël — ENSPY Yaoundé 2026
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health", tags=["Santé"])
def health():
    """Endpoint de vérification de l'état de l'API."""
    return {"status": "healthy", "version": "1.0.0"}

