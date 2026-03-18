# from routers import base,files
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from core.settings import settings
from core import app_exception_handler
from core.exceptions import AppException
from contextlib import asynccontextmanager
from routers import routers


@asynccontextmanager
async def lifespan(app: FastAPI):
  
  # Exception handler
  app.add_exception_handler(AppException, app_exception_handler)
  
  # MongoDB client
  app.client = AsyncIOMotorClient(settings.MONGODB_URL)
  app.db_client = app.client[settings.MONGODB_DATABASE]

#   # Vector DB client
#   vdb_provider_factory = VectorDBFactory(settings)
#   app.vdb_client = vdb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
#   app.vdb_client.connect()
  
  
#   # Generation client
#   llm_provider_factory = LLMFactory(settings)
  
#   app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
#   app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

#   # Embedding client
#   app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
#   app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
#                                            embedding_size=settings.EMBEDDING_MODEL_SIZE)
  
  
  
#   yield
  

  
  

app = FastAPI(lifespan=lifespan)

for router in routers:
    app.include_router(router)