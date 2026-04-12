
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from core import app_exception_handler,get_settings
from core.app_exceptions import AppException
from contextlib import asynccontextmanager
from routers import files_router,projects_router,vectordb_router,workspace_router,home_router
from helpers.logger import get_logger
from integrations import get_whisper_provider
from integrations.vector_db import VectorDBFactory
from integrations.llm import LLMFactory,LCOpenAI
from integrations.redis_provider import RedisProvider
from services.chains import ChainsService
from services.chat import ChatService
from helpers.metrics import setup_metrics
import os

settings = get_settings()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
os.environ["LANGCHAIN_PROJECT"] = settings.APP_NAME

OPENAI_API_KEYS = settings.OPENAI_API_KEY.split(",")
logger = get_logger(__name__,level="debug")


def _get_whisper_device() -> str:
  try:
    import torch
    if torch.cuda.is_available():
      return "cuda"
  except ImportError:
    logger.warning("Torch is not installed; loading Whisper on CPU")
  except Exception as exc:
    logger.warning(f"Unable to detect CUDA availability; loading Whisper on CPU: {exc}")
  return "cpu"


@asynccontextmanager
async def lifespan(app: FastAPI):
  # Exception handler
  app.add_exception_handler(AppException, app_exception_handler)
  
  
  
  # MongoDB client
  app.state.db_connection = AsyncIOMotorClient( settings.MONGODB_URI)
  app.state.db_client = app.state.db_connection[settings.MONGODB_DATABASE]
  logger.info("MongoDB client loaded successfully")
  
  # VectorDB client
  vdb_provider_factory = VectorDBFactory(settings)
  app.state.vdb_client = vdb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
  app.state.vdb_client.connect()
  collections = app.state.vdb_client.list_all_collections()
  logger.info(f"VectorDB client loaded successfully")
  logger.info(f"VectorDB Collections: {collections}")


  # LLM clients
  llm_provider_factory = LLMFactory()
  app.state.embedding_client = llm_provider_factory.create(api_key="hf",provider=settings.EMBEDDING_BACKEND)
  app.state.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)
  logger.info("Embedding client loaded successfully")
  
  # Redis client
  app.state.redis = RedisProvider(url=settings.REDIS_URL)
  await app.state.redis.connect()
  redis_collections = await app.state.redis.list_collections()
  logger.info("Redis Collections: " + str(redis_collections))
  logger.info("Redis client loaded successfully")
  
  


  app.state.langchain_client = LCOpenAI(api_key=OPENAI_API_KEYS[3],api_url=settings.OPENAI_API_URL)
  app.state.chains = ChainsService(app.state.langchain_client,settings=settings)
  app.state.chat = ChatService(redis_provider=app.state.redis ,embedding_client=app.state.embedding_client,lc_openai_client=app.state.langchain_client,vdb_client=app.state.vdb_client,settings=settings)
  logger.info("LangChain client loaded successfully")
  
  whisper_provider = get_whisper_provider(device=_get_whisper_device())
  whisper_provider.load()
  logger.info("Whisper model loaded successfully")
  
  
  yield
  app.state.vdb_client.disconnect()
  app.state.db_connection.close()
  await app.state.redis.disconnect()
  
  
  
  

  
  

app = FastAPI(lifespan=lifespan)
setup_metrics(app)
app.add_exception_handler(AppException, app_exception_handler)

app.include_router(workspace_router.workspace_route)
app.include_router(files_router.files_route)
app.include_router(projects_router.projects_route)
app.include_router(vectordb_router.vectordb_route)
app.include_router(vectordb_router.vectordb_route)
app.include_router(home_router.home_route)