import os
import asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

LOCAL_DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", "sqlite+aiosqlite:///./interviewai_dev.db")
USE_REMOTE_DATABASE = os.getenv("USE_REMOTE_DATABASE", "").lower() in {"1", "true", "yes"}
RAW_URL = os.getenv("DATABASE_URL", LOCAL_DATABASE_URL) if USE_REMOTE_DATABASE else LOCAL_DATABASE_URL


def _normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgresql+asyncpg://"):
        return raw_url.split("?")[0] + "?ssl=require"
    if raw_url.startswith("postgresql://"):
        async_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return async_url.split("?")[0] + "?ssl=require"
    return raw_url


def _create_engine(database_url: str):
    if database_url.startswith("sqlite"):
        return create_async_engine(database_url, echo=False)
    return create_async_engine(
        database_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
        connect_args={"timeout": 8},
    )


DATABASE_URL = _normalize_database_url(RAW_URL)
print(f"[DB] Configured database at: {DATABASE_URL[:60]}...")

engine = _create_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    global engine, async_session, DATABASE_URL
    try:
        await asyncio.wait_for(_create_tables(), timeout=10)
        await migrate_schema()
    except Exception as exc:
        if DATABASE_URL == LOCAL_DATABASE_URL:
            raise
        print(f"[DB] Remote database unavailable ({exc}). Falling back to local SQLite.")
        await engine.dispose()
        DATABASE_URL = LOCAL_DATABASE_URL
        engine = _create_engine(DATABASE_URL)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        await _create_tables()
        await migrate_schema()


async def _create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"[DB] Tables created/verified using {DATABASE_URL}")

async def migrate_schema():
    """Add any columns defined in models but missing from existing DB tables."""
    if DATABASE_URL.startswith("sqlite"):
        return
    type_map = {
        sa.String: "VARCHAR(255)",
        sa.Text: "TEXT",
        sa.Integer: "INTEGER",
        sa.DateTime: "TIMESTAMP WITH TIME ZONE",
        sa.JSON: "JSONB",
    }
    from sqlalchemy import inspect as sa_inspect

    # Use a separate connection for inspection (read-only)
    async with engine.connect() as conn:
        existing_tables = await conn.run_sync(
            lambda sync_conn: sa_inspect(sync_conn).get_table_names()
        )
        missing = []
        for table_name, table in Base.metadata.tables.items():
            if table_name not in existing_tables:
                continue
            existing_cols = set(await conn.run_sync(
                lambda sync_conn: [c["name"] for c in sa_inspect(sync_conn).get_columns(table_name)]
            ))
            for column in table.columns:
                if column.name in existing_cols:
                    continue
                sa_type = type(column.type)
                pg_type = type_map.get(sa_type, "VARCHAR(255)")
                if isinstance(column.type, sa.String):
                    pg_type = f"VARCHAR({column.type.length or 255})"
                missing.append((table_name, column.name, pg_type))

    # Each ALTER TABLE in its own transaction so partial failures don't block others
    for table_name, col_name, pg_type in missing:
        try:
            async with engine.begin() as conn:
                await conn.execute(
                    sa.text(f'ALTER TABLE {table_name} ADD COLUMN "{col_name}" {pg_type}')
                )
            print(f"[DB] Added column {table_name}.{col_name} ({pg_type})")
        except Exception as e:
            err = str(e)[:100]
            if "already exists" in err.lower():
                print(f"[DB] Column {table_name}.{col_name} already exists")
            else:
                print(f"[DB] Could not add {table_name}.{col_name}: {err}")


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def close_db():
    await engine.dispose()
