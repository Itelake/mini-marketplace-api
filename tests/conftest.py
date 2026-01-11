import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

from app.auth import get_current_user
from app.main import app
from app.models import Base
from app.database import get_db  # зависимость для override
from app.models import User

# ---------------- Конфиг тестовой БД ----------------
TEST_DATABASE_URL = "postgresql+asyncpg://fastapi_user:12345@localhost:5432/taskdb_test"

# ---------------- Engine Fixture ----------------
@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        future=True,
        echo=False,
        poolclass=NullPool,
    )

    # Создаем все таблицы перед тестами
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # После тестов — удаляем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# ---------------- DB Session Fixture ----------------
@pytest.fixture
async def db_session(engine):
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()  # откат изменений после каждого теста


# ---------------- HTTP Client Fixture ----------------
@pytest.fixture
async def async_client(db_session):
    # Override зависимости get_db
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Используем ASGITransport для httpx >= 0.28
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        yield client

# ---------------- Admin Client User Fixture ----------------
@pytest.fixture
async def admin_user(db_session):
    admin = User(
        email="admin@test.com",
        hashed_password="fake",
        role="admin"
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin

@pytest.fixture
async def admin_client(async_client, admin_user):
    async def override_get_current_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield async_client
    app.dependency_overrides.pop(get_current_user, None)
    
# ---------------- Public Client User Fixture ----------------
@pytest.fixture
async def user(db_session):
    user = User(
        email="user@test.com",
        hashed_password="fake",
        role="user"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

from app.auth import get_current_user

@pytest.fixture
async def authorized_client(async_client, user):
    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield async_client
    app.dependency_overrides.pop(get_current_user, None)
