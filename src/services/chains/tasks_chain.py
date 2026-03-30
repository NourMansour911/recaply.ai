import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from services.chains.chains_output_schemas import TasksOutput
from .utils import format_segments

logger = logging.getLogger(__name__)

task_parser = PydanticOutputParser(pydantic_object=TasksOutput)

TASK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
Extract actionable tasks from meeting segments.

Rules:
- Use ONLY provided segments, context, and decisions
- Output MUST be valid JSON
{format_instructions}
"""),
    ("human", """
Segments:
{segments}

Context:
{context}

Decisions:
{decisions}

Extract tasks with:
- id
- title
- description
- type
- owner
- deadline
- priority
- constraints
- target
- related_decision_ids
- confidence
- segment_id
"""
    )
])

def build_tasks_chain(llm: LCOpenAI):
    def prepare_input(inputs: dict):
        segments = inputs["segments"]
        context = inputs["context"]
        decisions = inputs["decisions"]
        return {
            "segments": format_segments(segments),
            "context": context,
            "decisions": decisions,
            "format_instructions": task_parser.get_format_instructions()
        }

    return RunnableLambda(prepare_input) | TASK_PROMPT | llm | task_parser | RunnableLambda(lambda x: x.tasks)