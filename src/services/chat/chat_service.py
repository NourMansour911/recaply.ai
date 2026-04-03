import logging
from typing import List, Dict
from core import Settings
from langchain_core.runnables import RunnablePassthrough
from langsmith import traceable
from integrations.llm import LCOpenAI
from .retrieval import Retrieval
from integrations.vector_db import VectorDBInterface
from integrations.llm import LLMInterface
from .reranker import Reranker
from .query_rewrite import build_requery_chain


logger = logging.getLogger(__name__)

class ChatService:

    def __init__(self,embedding_client:LLMInterface ,vdb_client: VectorDBInterface,lc_openai_client: LCOpenAI, settings: Settings):
        self.llm_factory = lc_openai_client
        self.settings = settings
        self.rerarker = Reranker(api_key=settings.COHERE_API_KEY)
        self.retrieval = Retrieval(embedding_client=embedding_client,vdb_client=vdb_client)
        self.llms: Dict[str, LCOpenAI] = {
            "requeries": lc_openai_client.get_langchain_llm(model=settings.GENERATION_MODEL_ID,temperature=0.5),
        }

        self._pipeline = None  

    async def run(self,message,vdb_collection_name,history):
        try:
            pipeline = self._get_pipeline()
            result = await pipeline.ainvoke({"query": message,"history": history})
            raw_retrieved = await self.retrieval.retrieve_multi_query(result["requeries"],collection_name=vdb_collection_name)
            reranked = await self.rerarker.rerank(query=message,documents=raw_retrieved,top_k=self.settings.TOP_K_DOCS)
            return {
                "requeries": result["requeries"],
                "raw_retrieved": raw_retrieved,
                "reranked": reranked
            }
        except Exception:
            logger.exception("Generate pipeline failed")
            raise
    
    @traceable(name="chat_pipeline")
    def _build_pipeline(self):

        requery_chain = build_requery_chain(self.llms["requeries"])
        pipeline =  RunnablePassthrough.assign(
                requeries= requery_chain
                )
        logger.info(f"Pipeline built {pipeline}")
        return pipeline

    def _get_pipeline(self):
        if self._pipeline is None:
            self._pipeline = self._build_pipeline()
        return self._pipeline