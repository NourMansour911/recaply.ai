import logging
from typing import Dict, Any, List

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, Runnable
from langchain_core.output_parsers import PydanticOutputParser
from .utils import to_lc_messages

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class MultiQueryOutput(BaseModel):
    queries: List[str] = Field(..., description="Exactly 2 rewritten queries optimized for retrieval")


MULTI_QUERY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a query rewriting assistant for a RAG system.

Your job:
- Understand the user query and chat history
- Clarify the query if needed
- Generate EXACTLY 2 distinct search queries

Rules:
- Queries must be concise, keyword-rich, and optimized for retrieval
- Each query must cover a different semantic angle
- Keep the original intent intact
- Do NOT answer the question
- Output MUST be valid JSON:
{format_instructions}
"""
    ),
    MessagesPlaceholder(variable_name="history"),

    (
        "human",
        """
User Query:
{query}

Generate exactly 2 optimized search queries.
"""
    )
])


parser = PydanticOutputParser(pydantic_object=MultiQueryOutput)


def build_requery_chain(llm: ChatOpenAI) -> Runnable:

    def prepare_input(inputs: Dict[str, Any]) -> Dict[str, Any]:
        history = inputs.get("history", [])

        return {
            "query": inputs["query"],
            "history": to_lc_messages(history), 
            "format_instructions": parser.get_format_instructions()
        }

    chain = (
        RunnableLambda(prepare_input)
        | MULTI_QUERY_PROMPT
        | llm
        | parser
        | RunnableLambda(lambda x: x.queries)
    )

    return chain