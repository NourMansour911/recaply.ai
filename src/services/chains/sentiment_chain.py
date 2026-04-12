import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from services.chains.chains_output_schemas import Sentiment
from .utils import format_segments

logger = logging.getLogger(__name__)

sentiment_parser = PydanticOutputParser(pydantic_object=Sentiment)

SENTIMENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You analyze overall meeting sentiment from transcript segments.

Output rules:
- Use only provided segments.
- Keep labels grounded in evidence from transcript tone/content.
- If uncertain, prefer neutral with lower confidence.
- Return JSON only, no markdown and no commentary.
- The JSON must strictly follow this schema guidance:

{format_instructions}
"""),
    ("human", """
Transcript segments:
{segments}

Extract sentiment with:
- overall
- confidence
- highlights
- segment_ids

segment_ids should reference segments that most influenced the sentiment.
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

    def ensure_sentiment(data):
        """Normalize: if list of sentiments, take first; otherwise return as-is."""
        if isinstance(data, list):
            return data[0] if data else {}
        return data

    return RunnableLambda(prepare_input) | SENTIMENT_PROMPT | llm | RunnableLambda(ensure_sentiment) | sentiment_parser