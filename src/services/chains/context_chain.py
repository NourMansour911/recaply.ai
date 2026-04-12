import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from services.chains.chains_output_schemas import MeetingContextModel
from .utils import format_segments

logger = logging.getLogger(__name__)

context_parser = PydanticOutputParser(pydantic_object=MeetingContextModel)

CONTEXT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You extract structured meeting context from transcript segments.

Output rules:
- Use only the provided segments.
- Do not invent participants, agenda items, or goals.
- If a value is missing, leave it null or an empty list according to schema.
- Return JSON only, with no markdown fences and no extra commentary.
- The JSON must strictly follow this schema guidance:

{format_instructions}
"""
    ),
    (
        "human",
        """
Transcript segments:
{segments}

Extract:
- title (if not explicit, infer a short neutral title from content)
- participants (name and role only when evidenced)
- agenda (concise list of discussed topics)
- key_purpose (single concise statement)
"""
    )
])

def build_context_chain(llm: LCOpenAI):
    def prepare_input(inputs: dict):
        segments = inputs["segments"]
        return {
            "segments": format_segments(segments),
            "format_instructions": context_parser.get_format_instructions()
        }

    def ensure_context_dict(data):
        """Normalize: if list of contexts, take first; otherwise return as-is."""
        if isinstance(data, list):
            return data[0] if data else {}
        return data

    chain = RunnableLambda(prepare_input) | CONTEXT_PROMPT | llm | RunnableLambda(ensure_context_dict) | context_parser
    return chain