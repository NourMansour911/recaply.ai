from typing import List, Dict
from core import Settings
from helpers.logger import get_logger
from schemas import EnrichedSegment, ChainsResponse
from repos import FileRepo, ProjectRepo
from models import Segment, FileModel
from services.chains.output_models import GenerateOutput
from services.chains import ChainsService

logger = get_logger(__name__)


class ChainsOrchestrator:

    def __init__(
        self,
        settings: Settings,
        file_repo: FileRepo,
        project_repo: ProjectRepo,
        chains_service: ChainsService,
    ):
        self.settings = settings
        self.file_repo = file_repo
        self.project_repo = project_repo
        self.chains_service = chains_service

    async def execute(
        self,
        project_id: str,
        tenant_id: str,
    ) -> ChainsResponse:

        project = await self.project_repo.get_project(
            project_id=project_id,
            tenant_id=tenant_id,
        )

        files: List[FileModel] = await self.file_repo.get_all_project_files(
            project_iid=project.iid
        )

        
        files = sorted(files, key=lambda f: f.file_order or 0)

        segments: List[Segment] = [
            seg
            for file in files
            for seg in file.file_content
        ]

        output: GenerateOutput = await self.chains_service.run(segments)

        segment_index: Dict[str, tuple[Segment, FileModel]] = {}

        for file in files:
            for seg in file.file_content:
                segment_index[seg.id] = (seg, file)

        used_segment_ids = set()

        for item_list in [output.tasks, output.decisions, output.risks]:
            for item in item_list:
                seg_id = getattr(item, "segment_id", None)

                if seg_id:
                    used_segment_ids.add(seg_id)

        enriched_segments: List[EnrichedSegment] = []

        for item_list in [output.tasks, output.decisions, output.risks]:
            for item in item_list:
                seg_id = getattr(item, "segment_id", None)

                if seg_id and seg_id in segment_index:
                    seg, file = segment_index[seg_id]

                    enriched_segments.append(
                        EnrichedSegment(
                            **seg.model_dump(),
                            file_unique_name=file.file_unique_name,
                            file_type=file.file_type,
                            file_order=file.file_order,
                        )
                    )

        return ChainsResponse(
            output=output,
            segments=enriched_segments,
        )