import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from services.chains.chains_output_schemas import ConflictsOutput

logger = logging.getLogger(__name__)

conflict_parser = PydanticOutputParser(pydantic_object=ConflictsOutput)

CONFLICT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You detect conflicts across provided tasks and decisions.

Output rules:
- Use only provided tasks and decisions.
- Report only genuine contradictions/trade-offs/dependencies.
- Do not emit duplicates.
- If uncertain, omit the conflict rather than inventing one.
- Return JSON only, without markdown or extra prose.
- The JSON must strictly follow this schema guidance:

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

Keep reason short, explicit, and evidence-based.
"""
    )
])

def build_conflict_chain(llm: LCOpenAI):
    def prepare_input(inputs: dict):
        decisions = inputs["decisions"]
        tasks = inputs["tasks"]
        return {
            "decisions": decisions,
            "tasks": tasks,
            "format_instructions": conflict_parser.get_format_instructions()
        }

    def ensure_conflicts_dict(data):
        """Normalize LLM output: wrap bare array in dict if needed."""
        if isinstance(data, list):
            return {"conflicts": data}
        return data

    return RunnableLambda(prepare_input) | CONFLICT_PROMPT | llm | RunnableLambda(ensure_conflicts_dict) | conflict_parser | RunnableLambda(lambda x: x.conflicts)