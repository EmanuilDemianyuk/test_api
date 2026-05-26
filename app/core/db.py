from app.database.session import AsyncSessionLocal, async_session, engine


async def get_db():
    async with async_session() as session:
        yield session