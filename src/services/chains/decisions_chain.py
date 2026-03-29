import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from .output_models import Decision
from .utils import format_segments

logger = logging.getLogger(__name__)

decision_parser = PydanticOutputParser(pydantic_object=Decision)

DECISION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
Extract decisions from meeting segments.

Rules:
- Use ONLY provided segments and context
- Do NOT hallucinate
- Output MUST be valid JSON

{format_instructions}
"""),
    ("human", """
Segments:
{segments}

Context:
{context}

Extract decisions with:
- id
- title
- description
- type
- priority
- constraints
- pricing
- confidence
- segment_id
"""
    )
])

def build_decisions_chain(llm: LCOpenAI):
    def prepare_input(inputs: dict):
        segments = inputs["segments"]
        context = inputs["context"]
        return {
            "segments": format_segments(segments),
            "context": context.json(),
            "format_instructions": decision_parser.get_format_instructions()
        }

    return RunnableLambda(prepare_input) | DECISION_PROMPT | llm | decision_parser