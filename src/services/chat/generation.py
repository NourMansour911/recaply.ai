import logging
from typing import Dict, Any, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, Runnable, RunnablePassthrough
from langchain_core.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


# =========================
# Output Schema
# =========================

class Citation(BaseModel):
    doc_index: int = Field(..., description="Index of the document used")


class GenerationOutput(BaseModel):
    answer: str = Field(..., description="Final grounded answer")
    citations: List[Citation] = Field(..., description="List of used document indices")


parser = PydanticOutputParser(pydantic_object=GenerationOutput)



GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a strict RAG assistant.

Rules:
- Answer ONLY from the provided context
- Do NOT use prior knowledge
- Do NOT guess
- If answer is not found in context → say:
  "I don't know based on the provided documents"

- You MUST return valid JSON:
{format_instructions}

Citation Rules:
- Use ONLY document indices (doc_index)
- Do NOT invent indices
- If you provide an answer → you MUST include at least one citation
"""
    ),
    (
        "human",
        """
User Question:
{query}

Context:
{context}
"""
    )
])




def format_docs(docs: List[Dict[str, Any]]) -> str:
    formatted = []

    for i, doc in enumerate(docs):
        formatted.append(
            f"[DOC {i}]\n\n{doc['text']}"
        )

    return "\n\n".join(formatted)


def map_citations(indices: List[int], docs: List[Dict[str, Any]]):
    results = []

    for i in indices:
        if 0 <= i < len(docs):
            results.append(docs[i]["metadata"])

    return results


def build_generation_chain(llm: ChatOpenAI) -> Runnable:

    def prepare_input(inputs: Dict[str, Any]) -> Dict[str, Any]:
        docs = inputs["reranked_docs"]

        return {
            "query": inputs["query"],
            "context": format_docs(docs),
            "format_instructions": parser.get_format_instructions(),
            "docs": docs
        }

    chain = (
        RunnableLambda(prepare_input)

        | RunnablePassthrough.assign(
            llm_output=GENERATION_PROMPT | llm
        )
        | RunnableLambda(lambda x: _parse_and_map(x))
    )

    return chain



def _parse_and_map(x: Dict[str, Any]) -> Dict[str, Any]:
    try:
        parsed = parser.parse(x["llm_output"].content)
    except Exception as e:
        logger.exception(f"Failed to parse LLM output :{e}")
        return {
            "answer": "Failed to parse response",
            "citations": []
        }

    indices = [c.doc_index for c in parsed.citations]

    return {
        "answer": parsed.answer,
        "citations": map_citations(indices, x["docs"])
    }