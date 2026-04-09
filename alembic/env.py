# alembic/env.py — conecta Alembic con tus modelos
# Este archivo lo genera alembic init pero debes modificarlo
# para que conozca tu Base y tus modelos
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Agrega la carpeta raíz del proyecto al path de Python
# para que Alembic pueda importar tus módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa tu Base y TODOS los modelos
# Es crítico importar todos los modelos aquí para que Alembic
# los detecte al comparar con la DB
from database import Base
from models import Usuario, Tag, Categoria, Prediccion   # todos los modelos

# configuración de Alembic desde alembic.ini
config = context.config

# configura los logs
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Esta es la línea más importante:
# le dice a Alembic qué tablas debe rastrear
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Modo offline: genera el SQL sin conectarse a la DB.
    Útil para revisar qué va a hacer antes de ejecutar.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url               = url,
        target_metadata   = target_metadata,
        literal_binds     = True,
        dialect_opts      = {"paramstyle": "named"},
        compare_type      = True,   # detecta cambios de tipo de columna
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Modo online: se conecta a la DB y aplica los cambios.
    Es el modo que usamos normalmente.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix    = "sqlalchemy.",
        poolclass = pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection      = connection,
            target_metadata = target_metadata,
            compare_type    = True,   # detecta cambios de tipo de columna
        )

        with context.begin_transaction():
            context.run_migrations()


# decide qué modo usar según el contexto
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()