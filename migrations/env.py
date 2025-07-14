
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Debug: Print the path to help diagnose import issues
print(f"Project root added to sys.path: {project_root}")
print(f"Current sys.path: {sys.path[:3]}...")  # Show first 3 paths

# Import after path is set
from app.core.database import Base
from app.core.config import settings

# Import all models to ensure they're registered with SQLAlchemy
from app.models import user, role, permission, user_role, role_permission
from app.models import application, audit_log, base_organization
from app.models import branch, department, employee, position

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    # Use database URL from settings instead of alembic.ini
    url = settings.database_url
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # Override the URL with the one from settings
    configuration = config.get_section(config.config_ini_section) or {}
    configuration['sqlalchemy.url'] = settings.database_url
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
