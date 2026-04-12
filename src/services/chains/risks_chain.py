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
You extract project/meeting risks from decisions and tasks.

Output rules:
- Use only the provided decisions and tasks.
- Do not create speculative risks without evidence.
- Keep risk statements concrete and specific.
- If a field is unknown, set it to null.
- Return JSON only, without markdown or extra text.
- The JSON must strictly follow this schema guidance:

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

Prefer linking related_task_ids and related_decision_ids when available.
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

    def ensure_risks_dict(data):
        """Normalize LLM output: wrap bare array in dict if needed."""
        if isinstance(data, list):
            return {"risks": data}
        return data

    return RunnableLambda(prepare_input) | RISK_PROMPT | llm | RunnableLambda(ensure_risks_dict) | risk_parser | RunnableLambda(lambda x: x.risks)