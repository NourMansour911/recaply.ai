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
You extract actionable tasks from transcript segments.

Output rules:
- Use only provided segments, context, and decisions.
- Include only actionable items (not generic discussion points).
- Avoid duplicates; merge equivalent tasks.
- If a field is unknown, set it to null.
- Return JSON only, with no markdown fences and no explanation.
- The JSON must strictly follow this schema guidance:

{format_instructions}
"""),
    ("human", """
Transcript segments:
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

Use related_decision_ids only when a decision linkage is explicit or strongly implied.
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

    def ensure_tasks_dict(data):
        """Normalize LLM output: wrap bare array in dict if needed."""
        if isinstance(data, list):
            return {"tasks": data}
        return data

    return RunnableLambda(prepare_input) | TASK_PROMPT | llm | RunnableLambda(ensure_tasks_dict) | task_parser | RunnableLambda(lambda x: x.tasks)