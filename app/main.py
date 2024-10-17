from fastapi import FastAPI
from . import models
from .database import async_engine
from .routes import router
from strawberry.fastapi import GraphQLRouter
from . graphql import schema
from .auth import Context

app = FastAPI()
# models.Base.metadata.create_all(async_engine) 
app.include_router(router)


async def get_context() -> Context:
    return Context()

graphql_app = GraphQLRouter(schema=schema, context_getter=get_context)  # 'schema' is the instance of your Strawberry schema

# Include the GraphQL router in your FastAPI app
app.include_router(graphql_app, prefix="/graphql")