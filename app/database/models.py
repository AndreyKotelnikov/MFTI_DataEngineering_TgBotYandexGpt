from datetime import datetime
from sqlalchemy import func
from sqlalchemy import ForeignKey, String, BigInteger, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy import text
import config




engine = create_async_engine(config.DATABASE_URL + config.DATABASE_NAME, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    sex: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    history: Mapped[list["UserHistory"]] = relationship(back_populates="user")


class UserHistory(Base):
    __tablename__ = "user_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="history")


async def create_database_if_not_exists():
    # Создаем движок с уровнем изоляции AUTOCOMMIT
    engine_default = create_async_engine(config.DATABASE_URL + config.DEFAULT_DATABASE_NAME, isolation_level="AUTOCOMMIT", echo=True)

    async with engine_default.begin() as conn:
        # Проверяем, существует ли база данных
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{config.DATABASE_NAME}'")
        )
        exists = result.scalar() is not None

        if not exists:
            # Создаем базу данных, если ее не существует
            await conn.execute(text(f"CREATE DATABASE {config.DATABASE_NAME}"))
            print(f"База данных '{config.DATABASE_NAME}' успешно создана.")
        else:
            print(f"База данных '{config.DATABASE_NAME}' уже существует.")

    await engine.dispose()

async def async_main():
    await create_database_if_not_exists()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)