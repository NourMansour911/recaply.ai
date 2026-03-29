# services/chains/generate/chains_service.py

import logging
from typing import List, Dict
from core import Settings
from langchain_core.runnables import RunnableAssign

from integrations.llm import LCOpenAI
from models import Segment
from .output_models import GenerateOutput, MeetingContextModel

from .context_chain import build_context_chain
""" from .decisions_chain import build_decisions_chain
from .tasks_chain import build_tasks_chain
from .conflict_chain import build_conflict_chain
from .risks_chain import build_risks_chain
from .summary_chain import build_summary_chain
from .sentiment_chain import build_sentiment_chain """

logger = logging.getLogger(__name__)


class ChainsService:


    def __init__(self, lc_openai_client: LCOpenAI,settings: Settings):
        self.llm_factory = lc_openai_client
        self.settings = settings
        self.llms: Dict[str, LCOpenAI] = {
            "context": lc_openai_client.get_langchain_llm(model=settings.GENERATION_MODEL_ID),
            "decision": lc_openai_client.get_langchain_llm(model=settings.GENERATION_MODEL_ID),
            "task": lc_openai_client.get_langchain_llm(model=settings.GENERATION_MODEL_ID),
            "conflict": lc_openai_client.get_langchain_llm(model=settings.GENERATION_MODEL_ID),
            "risk": lc_openai_client.get_langchain_llm(model=settings.GENERATION_MODEL_ID),
            "summary": lc_openai_client.get_langchain_llm(model=settings.GENERATION_MODEL_ID),
            "sentiment": lc_openai_client.get_langchain_llm(model=settings.GENERATION_MODEL_ID),
        }

        self._pipeline = None  
    
    async def run(self, segments: List[Segment]) -> GenerateOutput:

        logger.info("Running generate pipeline", extra={"segments_count": len(segments)})

        try:
            pipeline = self._get_pipeline()
            result = await pipeline.ainvoke({"segments": segments})
            return GenerateOutput(**result)
        except Exception as e:
            logger.exception("Generate pipeline failed")
            raise
        
            
    def _build_pipeline(self):

        context_chain = build_context_chain(self.llms["context"])

        """
        # Uncomment and connect the rest when ready
        decision_chain = build_decisions_chain(self.llms["decision"])
        task_chain = build_tasks_chain(self.llms["task"])
        conflict_chain = build_conflict_chain(self.llms["conflict"])
        risk_chain = build_risks_chain(self.llms["risk"])
        summary_chain = build_summary_chain(self.llms["summary"])
        sentiment_chain = build_sentiment_chain(self.llms["sentiment"])

        pipeline = (
            context_chain
            | RunnableAssign({"decisions": decision_chain, "tasks": task_chain})
            | RunnableAssign({
                "conflicts": conflict_chain,
                "risks": risk_chain,
                "summary": summary_chain,
                "sentiment": sentiment_chain
            })
        )
        """
        
        pipeline = context_chain  

        return pipeline

    def _get_pipeline(self):
        if self._pipeline is None:
            self._pipeline = self._build_pipeline()
        return self._pipeline


