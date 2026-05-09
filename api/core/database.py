import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from api.core.config import settings

# --- Configuration Robuste pour Supabase / PgBouncer ---
# Pour éviter l'erreur 'DuplicatePreparedStatementError' sur PgBouncer (mode transaction),
# on désactive le cache ET on force des noms de statements uniques via un UUID.
database_url = settings.DATABASE_URL
if "prepared_statement_cache_size" not in database_url:
    separator = "&" if "?" in database_url else "?"
    database_url += f"{separator}prepared_statement_cache_size=0"

engine = create_async_engine(
    database_url, 
    echo=settings.DEBUG,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
    },
    poolclass=NullPool
)

# Session
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
class Base(DeclarativeBase):
    pass

# Dependency to get session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
