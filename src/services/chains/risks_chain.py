import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from services.chains.chains_output_schemas import RisksOutput
from .utils import format_segments

logger = logging.getLogger(__name__)

risk_parser = PydanticOutputParser(pydantic_object=RisksOutput)

RISK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
Extract risks from tasks and decisions.

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

Extract risks with:
- id
- title
- description
- severity
- likelihood
- mitigation
- related_task_ids
- related_decision_ids
- segment_id
"""
    )
])

def build_risks_chain(llm: LCOpenAI):
    def prepare_input(inputs: dict):
        decisions = inputs["decisions"]
        tasks = inputs["tasks"]
        return {
            "decisions": decisions,
            "tasks":tasks,
            "format_instructions": risk_parser.get_format_instructions()
        }

    return RunnableLambda(prepare_input) | RISK_PROMPT | llm | risk_parser | RunnableLambda(lambda x: x.risks)