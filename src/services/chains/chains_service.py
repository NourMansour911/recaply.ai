# services/chains/generate/chains_service.py

import logging
from typing import List, Optional

from langchain_core.runnables import RunnableAssign

from integrations.llm import ChatOpenAICompatible
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

    def __init__(
        self,
        
        context_llm: ChatOpenAICompatible,
        decision_llm: Optional[ChatOpenAICompatible] = None,
        task_llm: Optional[ChatOpenAICompatible] = None,
        conflict_llm: Optional[ChatOpenAICompatible] = None,
        risk_llm: Optional[ChatOpenAICompatible] = None,
        summary_llm: Optional[ChatOpenAICompatible] = None,
        sentiment_llm: Optional[ChatOpenAICompatible] = None,
    ):
        self.context_llm = context_llm

        
        self.decision_llm = decision_llm or context_llm
        self.task_llm = task_llm or context_llm
        self.conflict_llm = conflict_llm or context_llm
        self.risk_llm = risk_llm or context_llm
        self.summary_llm = summary_llm or context_llm
        self.sentiment_llm = sentiment_llm or context_llm

        self._pipeline = None

    def _build_pipeline(self):

        
        context = build_context_chain(self.context_llm)

        """ 

        decisions = build_decisions_chain(self.decision_llm)

        tasks = build_tasks_chain(self.task_llm)

        conflicts = build_conflict_chain(self.conflict_llm)

        risks = build_risks_chain(self.risk_llm)

        summary = build_summary_chain(self.summary_llm)

        sentiment = build_sentiment_chain(self.sentiment_llm)
        """

        pipeline = (
            context
        )

        """ 
        | RunnableAssign({
            "decisions": decisions,
            "tasks": tasks,
        })
        | RunnableAssign({
            "conflicts": conflicts,
            "risks": risks,
            "summary": summary,
            "sentiment": sentiment
        }) 
        """

        return pipeline


    def _get_pipeline(self):
        if self._pipeline is None:
            self._pipeline = self._build_pipeline()
        return self._pipeline

    # Execution

    async def run(
        self,
        segments: List[Segment],
    ) -> GenerateOutput:

        logger.info("Running generate pipeline", extra={"segments_count": len(segments)})

        try:
            pipeline = self._get_pipeline()

            result = await pipeline.ainvoke({
                "segments": segments
            })

            return GenerateOutput(**result)

        except Exception as e:
            logger.exception("Generate pipeline failed")
            raise