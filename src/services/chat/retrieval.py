from helpers.logger import get_logger
from core import Settings
from integrations.llm import LLMInterface
from integrations.vector_db import VectorDBInterface
import asyncio
from typing import List
logger = get_logger(__name__)


class Retrieval:
    def __init__(self, embedding_client: LLMInterface,vdb_client: VectorDBInterface):
        self.embedding_client = embedding_client
        self.vdb_client = vdb_client
    
        
    async def retrieve_multi_query(self, queries: List[str], collection_name: str, top_k: int = 30):
        tasks = []
        
        logger.info(f"Processing {len(queries)} queries...")
        for q in queries:
            tasks.append(self._process_single_query(q, collection_name, top_k//len(queries)))

        all_results = await asyncio.gather(*tasks)


        return all_results
    
    async def _process_single_query(self,query, collection_name,top_k):
        emb = await self.embedding_client.embed_text(query)

        semantic_task = asyncio.to_thread(self.vdb_client.search_by_vector, collection_name, emb, top_k)

        keyword_task = self.vdb_client.search_by_keyword(collection_name=collection_name,query_text= query,limit= top_k)

        semantic_results, keyword_results = await asyncio.gather(
            semantic_task,
            keyword_task
        )
        logger.info(f"Retrieved {len(semantic_results)} semantic results and {len(keyword_results)} keyword results for query: {query}")
        fused = self._reciprocal_rank_fusion([
            semantic_results,
            keyword_results,
            
        ],top_k = top_k)

        return fused

    def _reciprocal_rank_fusion(self, result_lists, top_k):
        fused_scores = {}

        weights = [0.7, 0.3]  

        for weight, results in zip(weights, result_lists):
            for rank, item in enumerate(results, start=1):
                doc_id = item["id"]

                score = weight * (1 / (60 + rank))

                if doc_id not in fused_scores:
                    fused_scores[doc_id] = {
                        "score": 0,
                        "doc": item
                    }

                fused_scores[doc_id]["score"] += score

        reranked = sorted(
            fused_scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )

        return [item["doc"] for item in reranked[:top_k]]