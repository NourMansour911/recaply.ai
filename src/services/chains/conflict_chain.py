import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from schemas.chains_output_schemas import Conflict

logger = logging.getLogger(__name__)

conflict_parser = PydanticOutputParser(pydantic_object=Conflict)

CONFLICT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
Extract conflicts between tasks or decisions.

Rules:
- Use ONLY tasks and decisions
- Output MUST be valid JSON
{format_instructions}
"""),
    ("human", """
Decisions:
{decisions}

Tasks:
{tasks}

Extract conflicts with:
- type
- entity ('decision' or 'task')
- related_ids
- reason
"""
    )
])

def build_conflict_chain(llm: LCOpenAI):
    def prepare_input(inputs: dict):
        decisions = inputs["decisions"]
        tasks = inputs["tasks"]
        return {
            "decisions": [d.dict() for d in decisions],
            "tasks": [t.dict() for t in tasks],
            "format_instructions": conflict_parser.get_format_instructions()
        }

    return RunnableLambda(prepare_input) | CONFLICT_PROMPT | llm | conflict_parser