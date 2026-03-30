
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from core import app_exception_handler,get_settings
from core.app_exceptions import AppException
from contextlib import asynccontextmanager
from routers import files_router,projects_router,vectordb_router,workspace_router
from helpers.logger import get_logger
from integrations import get_whisper_provider
from integrations.vector_db import VectorDBFactory
from integrations.llm import LLMFactory,LCOpenAI
from services.chains import ChainsService
import langsmith
import os
settings = get_settings()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
os.environ["LANGCHAIN_PROJECT"] = settings.APP_NAME

OPENAI_API_KEYS = settings.OPENAI_API_KEY.split(",")
logger = get_logger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
  # Exception handler
  app.add_exception_handler(AppException, app_exception_handler)
  logger.info("Loading Whisper model")
  logger.info("Whisper model loaded successfully")
  
  # MongoDB client
  app.state.connection = AsyncIOMotorClient(settings.MONGODB_URL)
  app.state.db_client = app.state.connection[settings.MONGODB_DATABASE]
  
  # LLM clients
  llm_provider_factory = LLMFactory()
  app.state.embedding_client = llm_provider_factory.create(api_key="ss",provider=settings.EMBEDDING_BACKEND)
  app.state.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)
  
  
  app.state.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND,api_key=OPENAI_API_KEYS[0],api_url=settings.OPENAI_API_URL)
  app.state.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)
  
  # LangChain
  app.state.langchain_client = LCOpenAI(api_key=OPENAI_API_KEYS[0],api_url=settings.OPENAI_API_URL)
  app.state.chains = ChainsService(app.state.langchain_client,settings=settings)
  
  logger.info("LangChain client loaded successfully")

  vdb_provider_factory = VectorDBFactory(settings)
  app.state.vdb_client = vdb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
  app.state.vdb_client.connect()
  

  whisper_provider = get_whisper_provider()
  whisper_provider.load()
  
  
  yield
  
  
  
  

  
  

app = FastAPI(lifespan=lifespan)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(workspace_router.workspace_route)
app.include_router(files_router.files_route)
app.include_router(projects_router.projects_route)
app.include_router(vectordb_router.vectordb_route)