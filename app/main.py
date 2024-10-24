from fastapi import FastAPI, Request, HTTPException
from . import models
from .database import async_engine
from .routes import router
from strawberry.fastapi import GraphQLRouter
from . graphql import schema
from .auth import Context
from typing import AsyncGenerator
from .database import get_db
app = FastAPI()
# models.Base.metadata.create_all(async_engine) 
app.include_router(router)


def custom_exception_formatter(error: Exception, debug: bool) -> dict:
    if isinstance(error, HTTPException):
        return {
            "message": error.detail
        }
    return {
        "message": "An unknown error occurred."
    }


async def get_context(request: Request) -> AsyncGenerator[Context, None]:
    async for db in get_db():
        yield Context(db=db, request=request)

graphql_app = GraphQLRouter(schema=schema, context_getter=get_context)

app.include_router(graphql_app, prefix="/graphql")