import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from services.chains.chains_output_schemas import DecisionsOutput
from .utils import format_segments

logger = logging.getLogger(__name__)

decision_parser = PydanticOutputParser(pydantic_object=DecisionsOutput)

DECISION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You extract decisions from transcript segments.

Output rules:
- Use only provided segments and context.
- Do not infer decisions that are not grounded in text.
- Keep each decision atomic and non-duplicated.
- If a field is unknown, set it to null.
- Return JSON only, without markdown or prose.
- The JSON must strictly follow this schema guidance:

{format_instructions}
"""),
    ("human", """
Transcript segments:
{segments}

Context:
{context}

Extract decisions with fields:
- id
- title
- description
- type
- priority
- constraints
- pricing
- confidence
- segment_id

Set segment_id to the best supporting segment id when available.
"""
    )
])

def build_decisions_chain(llm: LCOpenAI):
    def prepare_input(inputs: dict):
        segments = inputs["segments"]
        context = inputs["context"]
        return {
            "segments": format_segments(segments),
            "context": context,
            "format_instructions": decision_parser.get_format_instructions()
        }

    def ensure_decisions_dict(data):
        """Normalize LLM output: wrap bare array in dict if needed."""
        if isinstance(data, list):
            return {"decisions": data}
        return data

    return RunnableLambda(prepare_input) | DECISION_PROMPT | llm | RunnableLambda(ensure_decisions_dict) | decision_parser | RunnableLambda(lambda x: x.decisions)