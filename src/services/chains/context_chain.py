import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from .output_models import MeetingContextModel
from .utils import format_segments

logger = logging.getLogger(__name__)



context_parser = PydanticOutputParser(pydantic_object=MeetingContextModel)


CONTEXT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an AI assistant that extracts structured meeting context.

Rules:
- Use ONLY provided segments
- Do NOT hallucinate
- Do NOT generate timestamps or metadata
- Output MUST be valid JSON

{format_instructions}
"""
    ),
    (
        "human",
        """
Segments:
{segments}

Extract:
- title
- participants (name, role if available)
- agenda (list)
- key purpose
"""
    )
])





def build_context_chain(llm:LCOpenAI):


    def prepare_input(inputs: dict):
        segments = inputs["segments"]

        return {
            "segments": format_segments(segments),
            "format_instructions": context_parser.get_format_instructions()
        }

    chain = (
        RunnableLambda(prepare_input)
        | CONTEXT_PROMPT
        | llm
        | context_parser
    )

    return chain