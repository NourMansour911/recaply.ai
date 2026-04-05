import logging
from typing import Dict, Any, List

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, Runnable, RunnablePassthrough
from langchain_core.output_parsers import PydanticOutputParser
from .utils import to_lc_messages
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


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
You are Recaply, a professional AI meeting assistant specialized in analyzing meeting data using Retrieval-Augmented Generation (RAG).

Your role:
- Help users answer questions about meetings
- Provide accurate, grounded responses based ONLY on retrieved context
- Assist with understanding discussions, decisions, and key insights from meetings

Strict Rules:
- Answer ONLY from the provided context
- Do NOT use prior knowledge
- Do NOT guess or infer missing information
- If the answer is not explicitly found in the context, respond EXACTLY with:
  "I couldn't find this information in the meeting documents I have. It might not have been discussed or captured in the provided context."

Response Format:
- You MUST return a valid JSON object
- Follow the exact schema:
{format_instructions}

Citation Rules:
- You MUST cite sources using ONLY document indices (doc_index)
- Do NOT invent or assume indices
- Every answer MUST include at least one valid citation
- If multiple sources are used, include all relevant doc_index values

Behavior Guidelines:
- Be concise and precise
- Focus on extracting factual information from the context
- Do not add explanations outside the scope of the context
- Do not include any text outside the JSON response
"""
    ),

    MessagesPlaceholder(variable_name="history"),

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
        history = inputs.get("history", [])

        return {
            "query": inputs["query"],
            "context": format_docs(docs),
            "format_instructions": parser.get_format_instructions(),
            "docs": docs,
            "history": to_lc_messages(history)
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