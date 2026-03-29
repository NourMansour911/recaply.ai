import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from schemas.chains_output_schemas import Summary

logger = logging.getLogger(__name__)

summary_parser = PydanticOutputParser(pydantic_object=Summary)

SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
Summarize the meeting content.

Rules:
- Use context, decisions, tasks, conflicts, and risks
- Output MUST be valid JSON
{format_instructions}
"""),
    ("human", """
Context:
{context}

Decisions:
{decisions}

Tasks:
{tasks}

Conflicts:
{conflicts}

Risks:
{risks}

Extract summary with:
- overview
- key_points
- decisions_summary
- tasks_summary
"""
    )
])

def build_summary_chain(llm: LCOpenAI):
    def prepare_input(inputs: dict):
        return {
            "context": inputs["context"].json(),
            "decisions": [d.dict() for d in inputs["decisions"]],
            "tasks": [t.dict() for t in inputs["tasks"]],
            "conflicts": [c.dict() for c in inputs["conflicts"]],
            "risks": [r.dict() for r in inputs["risks"]],
            "format_instructions": summary_parser.get_format_instructions()
        }

    return RunnableLambda(prepare_input) | SUMMARY_PROMPT | llm | summary_parser