import logging
from motor.motor_asyncio import AsyncIOMotorClient
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from beanie import init_beanie

from app.models import User, Item
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1

DATABASE_URL = settings.MONGODB_DATABASE_URI  # Ensure this is set in your config


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init_db() -> None:
    try:
        client = AsyncIOMotorClient(DATABASE_URL)
        db = client.get_database()  # Connect to the database
        await init_beanie(database=db, document_models=[User, Item])  # Initialize Beanie
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise e


async def main() -> None:
    logger.info("Initializing service")
    await init_db()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
