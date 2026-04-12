import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from integrations.llm import LCOpenAI
from services.chains.chains_output_schemas import Summary

logger = logging.getLogger(__name__)

summary_parser = PydanticOutputParser(pydantic_object=Summary)

SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You produce a structured summary from context, decisions, tasks, conflicts, and risks.

Output rules:
- Use only the provided structured inputs.
- Do not introduce new facts.
- Keep points concise and non-redundant.
- Return JSON only, with no markdown or explanatory text.
- The JSON must strictly follow this schema guidance:

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

Return summary with fields:
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
            "context": inputs["context"],
            "decisions":  inputs["decisions"],
            "tasks": inputs["tasks"],
            "conflicts": inputs["conflicts"],
            "risks": inputs["risks"],
            "format_instructions": summary_parser.get_format_instructions()
        }

    def ensure_summary_dict(data):
        """Normalize: if list of summaries, take first; if list of dicts, wrap in Summary dict."""
        if isinstance(data, list):
            return data[0] if data else {}
        return data

    return RunnableLambda(prepare_input) | SUMMARY_PROMPT | llm | RunnableLambda(ensure_summary_dict) | summary_parser 