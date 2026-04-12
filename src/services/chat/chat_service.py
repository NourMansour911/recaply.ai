import logging
from typing import Dict

from core import Settings
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langsmith import traceable

from integrations.llm import LCOpenAI, LLMInterface
from integrations.vector_db import VectorDBInterface
from services.service_exceptions import ServiceException
from .retrieval import Retrieval
from .reranker import Reranker
from .query_rewrite import build_requery_chain
from .generation import build_generation_chain
from .memory import MemoryService
from integrations.redis_provider import RedisProvider
logger = logging.getLogger(__name__)


class ChatService:

    def __init__(
        self,
        embedding_client: LLMInterface,
        vdb_client: VectorDBInterface,
        lc_openai_client: LCOpenAI,
        settings: Settings,
        redis_provider: RedisProvider,
        ):
        self.llm_factory = lc_openai_client
        self.settings = settings
        self.memory = MemoryService(redis_provider)

        self.rerarker = Reranker(api_key=settings.COHERE_API_KEY)
        self.retrieval = Retrieval(
            embedding_client=embedding_client,
            vdb_client=vdb_client
        )

        self.llms: Dict[str, LCOpenAI] = {
            "requery": lc_openai_client.get_langchain_llm(
                model=settings.GENERATION_MODEL_ID,
                temperature=0.5
            ),
            "generation": lc_openai_client.get_langchain_llm(
                model=settings.GENERATION_MODEL_ID,
                temperature=0.1
            ),
        }

        self._pipeline = None

    async def run(
        self,
        message,
        vdb_collection_name,
        tenant_id,
        project_id,
        user_id,
        session_id
    ):
        try:
            history = await self.memory.get_history(
                tenant_id,
                project_id,
                user_id,
                session_id
            )

            pipeline = self._get_pipeline()
            trimmed_history = self._trim_history(history, 3)

            run_config = {
                "run_name": "chat_run",
                "tags": ["chat", "api", "rag"],
                "metadata": {
                    "tenant_id": tenant_id,
                    "project_id": project_id,
                    "user_id": user_id,
                    "session_id": session_id,
                    "vdb_collection_name": vdb_collection_name,
                    "history_size": len(trimmed_history),
                    "top_k_docs": self.settings.TOP_K_DOCS,
                    "generation_model_id": self.settings.GENERATION_MODEL_ID,
                    "query_length": len(message or ""),
                },
            }

            result = await pipeline.ainvoke({
                "collection_name": vdb_collection_name,
                "query": message,
                "history": trimmed_history,
            }, config=run_config)

            await self.memory.append_user_message(
                tenant_id, project_id, user_id, session_id, message
            )

            await self.memory.append_ai_message(
                tenant_id, project_id, user_id, session_id, result["generation"]["answer"]
            )

            return result["generation"]

        except Exception as e:
            logger.exception("Generate pipeline failed")
            raise ServiceException(message="Generate response failed", details={"error": str(e)},)

    def _build_pipeline(self):

        requery_chain = build_requery_chain(self.llms["requery"])
        retrieving = self._build_retriever_runnable()
        reranking = self._build_reranker_runnable()
        generation_chain = build_generation_chain(self.llms["generation"])

        pipeline = (
            RunnablePassthrough.assign(requeries=requery_chain)
            | retrieving
            | reranking
            | RunnablePassthrough.assign(generation=generation_chain)
        )

        logger.info(f"Pipeline built {pipeline}")
        return pipeline

    def _get_pipeline(self):
        if self._pipeline is None:
            self._pipeline = self._build_pipeline()
        return self._pipeline

    def _build_retriever_runnable(self):
        async def retrieve_fn(inputs):
            docs = await self.retrieval.retrieve_multi_query(
                inputs["requeries"],
                collection_name=inputs["collection_name"]
            )

            return {
                **inputs,
                "retrieved_docs": docs
            }

        return RunnableLambda(retrieve_fn)

    def _build_reranker_runnable(self):
        async def rerank_fn(inputs):
            reranked = await self.rerarker.rerank(
                query=inputs["query"],
                documents=inputs["retrieved_docs"],
                top_k=self.settings.TOP_K_DOCS
            )

            return {
                **inputs,
                "reranked_docs": reranked
            }

        return RunnableLambda(rerank_fn)
    
    def _trim_history(self, history, max_size):
        if len(history) > max_size:
            history = history[-max_size:]

        return history