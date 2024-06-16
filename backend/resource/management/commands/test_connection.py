import asyncio
import logging
from django.core.management.base import BaseCommand
import asyncpg

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test database connection using asyncpg'

    def handle(self, *args, **kwargs):
        try:
            asyncio.run(self.test_connection())
        except Exception as e:
            logger.error(f"Error testing database connection: {e}")

    async def test_connection(self):
        try:
            pool = await asyncpg.create_pool(
                user='postgres',
                password='password123',
                database='digital',
                host='localhost'
            )
            async with pool.acquire() as connection:
                result = await connection.fetch('SELECT 1')
                logger.info(f"Database connection test result: {result}")
                print(result)
        except Exception as e:
            logger.error(f"Error during database connection test: {e}")
            raise
