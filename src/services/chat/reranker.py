from typing import List, Dict, Any
from helpers.logger import get_logger
import cohere

logger = get_logger(__name__, level="info")


class Reranker:
    def __init__(self, api_key: str, model: str = "rerank-english-v3.0"):
        self.client = cohere.AsyncClient(api_key)
        self.model = model

    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int 
    ) -> List[Dict[str, Any]]:


        if not documents:
            return []

        try:
            
            texts = [doc["text"] for doc in documents]

            doc_map = {i: doc for i, doc in enumerate(documents)}

            logger.info(f"Reranking {len(texts)} documents with Cohere...")


            response = await self.client.rerank(
                model=self.model,
                query=query,
                documents=texts,
                top_n=min(top_k, len(documents))
            )

            reranked_docs = []
            for item in response.results:
                idx = item.index
                score = item.relevance_score


                doc = doc_map[idx].copy()
                doc["rerank_score"] = score

                doc["snippet"] = doc["text"][:200]

                reranked_docs.append(doc)

            return reranked_docs

        except Exception as e:
            logger.error(f"Cohere Reranker failed: {str(e)}")
            return documents[:top_k]

