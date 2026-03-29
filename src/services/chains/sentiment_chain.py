import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from schemas.chains_output_schemas import Sentiment
from .utils import format_segments

logger = logging.getLogger(__name__)

sentiment_parser = PydanticOutputParser(pydantic_object=Sentiment)

SENTIMENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
Analyze overall sentiment from meeting segments.

Rules:
- Use ONLY provided segments
- Output MUST be valid JSON
{format_instructions}
"""),
    ("human", """
Segments:
{segments}

Extract sentiment with:
- overall
- confidence
- highlights
- segment_ids
"""
    )
])

def build_sentiment_chain(llm: LCOpenAI):
    def prepare_input(inputs: dict):
        segments = inputs["segments"]
        return {
            "segments": format_segments(segments),
            "format_instructions": sentiment_parser.get_format_instructions()
        }

    return RunnableLambda(prepare_input) | SENTIMENT_PROMPT | llm | sentiment_parser