from helpers.logger import get_logger
from schemas import NormalizedFileData
from integrations.llm import LLMInterface
from datetime import datetime
from typing import List

from schemas import Segment, NormalizedFileData
from models.chunk_model import ChunkMetadata

from .semantic_chunking import SemanticChunkingService
from .merge_chunking import MergeChunkingService
from core import Settings

logger = get_logger(__name__)


class ChunkingService:
    def __init__(self, embedding_client: LLMInterface,settings=Settings):
        self.settings = settings
        self.embedding_client = embedding_client
        self.merge_service = MergeChunkingService()
        self.semantic_service = SemanticChunkingService(embedding_client=self.embedding_client,similarity_threshold=self.settings.CHUNKS_SIMILARITY_THRESHOLD)
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

        if any(seg.speakers for seg in segments):
            chunks = await self.merge_service.run(segments,max_chunk_size=self.settings.CHUNK_MAX_SIZE)
        else:
            chunks = await self.semantic_service.run(segments,max_chunk_size=self.settings.CHUNK_MAX_SIZE,overlap=self.settings.CHUNK_OVERLAP)

        return await self.embed(
            chunks=chunks,
            file=file_data,
            project_iid=project_iid,
            tenant_id=tenant_id,
            idx=idx
        )
        
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
            emb = await self.embedding_client.embed_text(chunk.text)

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




