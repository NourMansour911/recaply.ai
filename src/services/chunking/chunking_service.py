import logging
from typing import List, Tuple

from schemas import NormalizedFileData
from models.chunk_model import ChunkMetadata
from integrations.llm import LLMInterface

from .utils import has_speakers
from .merge_chunking import MergeChunkingService
from .semantic_chunking import SemanticChunkingService

logger = logging.getLogger(__name__)


class ChunkingService:
    def __init__(self, embedding_client: LLMInterface):
        self.embedding_client = embedding_client
        self.semantic_service = SemanticChunkingService(embedding_client)
        self.merge_service = MergeChunkingService()

    async def process_file_chunks(
        self,
        file_data: NormalizedFileData,
        project_iid: str,
        tenant_id: str,
        idx: int
    ):

        segments = file_data.normalized_file.segments or []

        if not segments:
            return [], [], [], []

        if has_speakers(segments):
            logger.info("Using MERGE chunking")

            merged_segments = await self.merge_service.run(segments)

            return await self.semantic_service.embed_prebuilt_chunks(
                chunks=merged_segments,
                file=file_data,
                project_iid=project_iid,
                tenant_id=tenant_id,
                start_idx=idx
            )

        else:
            logger.info("Using SEMANTIC chunking")

            return await self.semantic_service.run(
                segments=segments,
                file=file_data,
                project_iid=project_iid,
                tenant_id=tenant_id,
                start_idx=idx
            )