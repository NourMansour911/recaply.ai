# from routers import base,files
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from core import app_exception_handler,get_settings
from core.exceptions.app_exceptions import AppException
from contextlib import asynccontextmanager
from routers import files_router,projects_router
from faster_whisper import WhisperModel


settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
  
  # Exception handler
  app.add_exception_handler(AppException, app_exception_handler)
  
  # Whisper model
  app.state.whisper =  WhisperModel("base", device="cuda")
  
  # MongoDB client
  app.state.connection = AsyncIOMotorClient(settings.MONGODB_URL)
  app.state.db_client = app.state.connection[settings.MONGODB_DATABASE]

  yield
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
  
  
  
  

  
  

app = FastAPI(lifespan=lifespan)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(files_router.files_route)
app.include_router(projects_router.projects_route)