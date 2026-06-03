from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.app.infrastructure.config.settings import settings

# base for orm model
Base = declarative_base()

# engine (connection pool)
engine = create_async_engine( # creating connection pool
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

# session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# dependency fastapi (for repo/service)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
