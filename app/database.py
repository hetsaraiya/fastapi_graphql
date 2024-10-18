# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.asyncio import (
#     AsyncEngine as SQLAlchemyAsyEng,
#     create_async_engine as create_sql_alq,
#     AsyncSession as SQLalAsySess,
#     async_sessionmaker
# )

# SQLALCHAMY_DATABASE_URL = 'sqlite:///data.db'

# engine = create_engine(SQLALCHAMY_DATABASE_URL, connect_args={
#                        "check_same_thread": False})

# async_engine = create_sql_alq(
#     url="sqlite:///data.db",

# )

# SessionLocal = async_sessionmaker(bind=async_engine, autocommit=False, autoflush=False,)

# Base = declarative_base()

# async def get_db():   
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
# Use a URI that specifies the use of the aiqlite driver
SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///data.db'

async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
)

SessionLocal = async_sessionmaker(bind=async_engine, autocommit=False, autoflush=False)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db