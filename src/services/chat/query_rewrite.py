import logging
from typing import Dict, Any, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, Runnable
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class MultiQueryOutput(BaseModel):

    queries: List[str] = Field(description="Exactly 2 rewritten queries optimized for retrieval")



MULTI_QUERY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a query rewriting assistant for a RAG system.

Your job:
- Understand the user query and chat history
- Clarify the query if needed
- Generate EXACTLY 2 different search queries

Rules:
- Queries must be optimized for retrieval
- Each query should cover a different semantic angle
- Keep original intent
- Do NOT answer the question
- Keep queries concise and keyword-rich
"""
    ),
    (
        "human",
        """
Chat History:
{history}

User Query:
{query}

Generate exactly 2 optimized search queries.
"""
    )
])




def build_multi_query_chain(llm: ChatOpenAI) -> Runnable:

    structured_llm = llm.with_structured_output(MultiQueryOutput)

    def prepare_input(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize inputs for the prompt.
        """
        return {
            "query": inputs["query"],
            "history": inputs.get("history", "")
        }

    def post_process(output: MultiQueryOutput) -> List[str]:

        queries = [q.strip() for q in output.queries if q.strip()]

        
        seen = set()
        deduped = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                deduped.append(q)

        
        final_queries = deduped[:2]

        logger.info(f"Generated queries: {final_queries}")

        return final_queries

    
    chain = (
        RunnableLambda(prepare_input)
        | MULTI_QUERY_PROMPT
        | structured_llm
        | RunnableLambda(post_process)
    )

    return chain