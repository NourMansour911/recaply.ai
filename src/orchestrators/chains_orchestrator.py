# orchestrators/generate_orchestrator.py

from typing import List
from core import Settings
from helpers.logger import get_logger
from integrations.llm import LLMInterface
from repos import FileRepo, ProjectRepo
from models import Segment
from services.chains.output_models import GenerateOutput
from services.chains import ChainsService



logger = get_logger(__name__)


class GenerateOrchestrator:

    def __init__(
        self,
        settings: Settings ,
        file_repo: FileRepo ,
        project_repo: ProjectRepo ,
        chains_service: ChainsService
        
    ):
        self.settings = settings
        self.file_repo = file_repo
        self.project_repo = project_repo
        self.chains_service = chains_service
    
    async def execute(self, segments: List[Segment]) -> GenerateOutput:

        return await self.chains_service.run(segments)