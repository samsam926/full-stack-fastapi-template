import logging

from app.core.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    try:
        # Initialize the database
        await init_db()
        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise e


async def main() -> None:
    logger.info("Creating initial data")
    await init()
    logger.info("Initial data created")


import asyncio

if __name__ == "__main__":
    asyncio.run(main())
