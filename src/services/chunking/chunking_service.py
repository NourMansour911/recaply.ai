from helpers.logger import get_logger
from schemas import NormalizedFileData, Segment
from models.chunk_model import ChunkMetadata
from .semantic_chunking import SemanticChunkingService
from .merge_chunking import MergeChunkingService
from .chunking_exceptions import ChunkProcessingError, EmbeddingError
from core import Settings
from integrations.llm import LLMInterface
from datetime import datetime
from typing import List

logger = get_logger(__name__)


class ChunkingService:
    def __init__(self, embedding_client: LLMInterface, settings=Settings):
        self.settings = settings
        self.embedding_client = embedding_client
        self.merge_service = MergeChunkingService()
        self.semantic_service = SemanticChunkingService(
            embedding_client=self.embedding_client,
            similarity_threshold=self.settings.CHUNKS_SIMILARITY_THRESHOLD
        )

    async def process_file_chunks(
        self,
        file_data: NormalizedFileData,
        project_iid: str,
        tenant_id: str,
        idx: int,
    ):
        segments = file_data.normalized_file.segments or []
        if not segments:
            return [], [], [], []

        try:
            if any(seg.speakers for seg in segments):
                chunks = await self.merge_service.run(
                    segments, max_chunk_size=self.settings.CHUNK_MAX_SIZE
                )
            else:
                chunks = await self.semantic_service.run(
                    segments,
                    max_chunk_size=self.settings.CHUNK_MAX_SIZE,
                    overlap=self.settings.CHUNK_OVERLAP
                )

            return await self.embed(
                chunks=chunks,
                file=file_data,
                project_iid=project_iid,
                tenant_id=tenant_id,
                idx=idx
            )
        except Exception as e:
            logger.error("Failed to process file chunks", exc_info=True)
            raise ChunkProcessingError(segment_index=idx, message=str(e))

    async def embed(
        self,
        chunks: List[Segment],
        file: NormalizedFileData,
        project_iid: str,
        tenant_id: str,
        idx: int
    ):
        texts, vectors, ids, metas = [], [], [], []

        for i, chunk in enumerate(chunks):
            try:
                emb = await self.embedding_client.embed_text(chunk.text)
            except Exception as e:
                logger.error("Embedding failed", exc_info=True, extra={"chunk_index": i})
                raise EmbeddingError(segment_index=i, message=str(e))

            metadata = ChunkMetadata(
                speakers=chunk.speakers or [],
                word_count=len(chunk.text.split()),
                file_id=file.file_id,
                file_name=file.file_name,
                file_type=file.file_type,
                file_order=file.file_order,
                language=file.normalized_file.language,
                tenant_id=tenant_id,
                project_iid=str(project_iid),
                chunk_order=idx + i,
                created_at=datetime.now().isoformat(),
                start=chunk.start,
                end=chunk.end,
            )

            texts.append(chunk.text)
            vectors.append(emb)
            ids.append(list(range(idx, idx + len(chunks))))
            metas.append(metadata)

        return texts, vectors, ids, metas