from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
import os

load_dotenv()

# Importe la Base et tous les modeles
# Chaque modele importe ici sera detecte et migre automatiquement
from api.core.database import Base
from api.models.user import User

config = context.config

# Injecte DATABASE_URL_SYNC depuis le .env (avec échappement du % pour configparser)
url_sync = os.getenv("DATABASE_URL_SYNC")
if url_sync:
    url_sync = url_sync.replace("%", "%%")
config.set_main_option(
    "sqlalchemy.url",
    url_sync
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
