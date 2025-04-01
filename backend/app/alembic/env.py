import os
from logging.config import fileConfig

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# MongoDB and Beanie setup
from app.models import Item  # noqa
from app.core.config import settings  # noqa

# For MongoDB, you don't need to set target_metadata for Alembic
# because we are not using relational models with SQLAlchemy.
target_metadata = None

def get_url():
    # MongoDB does not require the same URL format as SQLAlchemy, adjust accordingly
    return str(settings.MONGODB_DATABASE_URI)  # Define this in your settings

def run_migrations_offline():
    """Run migrations in 'offline' mode.
    
    Since MongoDB uses flexible schema, here you might run a custom script
    to check or update the documents based on your schema changes.
    """
    url = get_url()
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        # No automatic migrations; you would call custom migration logic here
        # e.g., apply changes to existing MongoDB documents.
        print("Running MongoDB migration script manually...")
        # Custom migration code for MongoDB could go here.


async def run_migrations_online():
    """Run migrations in 'online' mode.
    
    In the online mode, you'd be working with Beanie or manually applying migration logic.
    """
    # You can also connect to MongoDB manually for migration purposes
    # but Beanie and MongoDB migrations are generally handled differently.
    # configuration = config.get_section(config.config_ini_section)
    # configuration["sqlalchemy.url"] = get_url()
    
    # For MongoDB, you don’t use SQLAlchemy's engine, just connect using Beanie
    from beanie import init_beanie
    from motor.motor_asyncio import AsyncIOMotorClient

    client = AsyncIOMotorClient(settings.MONGODB_DATABASE_URI)
    database = client.get_database()

    # Initialize Beanie models
    await init_beanie(database, document_models=[Item])

    # Here, you would have custom migration scripts for MongoDB updates
    print("Running MongoDB migration manually...")

    # Custom migration logic to alter the database schema or documents
    # Beanie does not provide auto-migrations, so this is a manual process.


import asyncio  # Add this import at the top of the file

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
