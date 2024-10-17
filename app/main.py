from fastapi import FastAPI
from . import models
from .database import engine
from .routes import router
from strawberry.fastapi import GraphQLRouter
from . types import schema

app = FastAPI()
models.Base.metadata.create_all(engine) 
app.include_router(router)


graphql_app = GraphQLRouter(schema=schema)  # 'schema' is the instance of your Strawberry schema

# Include the GraphQL router in your FastAPI app
app.include_router(graphql_app, prefix="/graphql")