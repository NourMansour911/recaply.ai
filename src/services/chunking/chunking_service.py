import logging
from schemas import NormalizedFileData
from integrations.llm import LLMInterface
import uuid
from datetime import datetime
from typing import List

from schemas import Segment, NormalizedFileData
from models.chunk_model import ChunkMetadata

from .semantic_chunking import SemanticChunkingService
from .merge_chunking import MergeChunkingService

logger = logging.getLogger(__name__)


class ChunkingService:
    def __init__(self, embedding_client: LLMInterface):
        self.merge_service = MergeChunkingService()
        self.embedding_client = embedding_client
        self.semantic_service = SemanticChunkingService(embedding_client=self.embedding_client)

    async def process_file_chunks(
        self,
        file_data: NormalizedFileData,
        project_iid: str,
        tenant_id: str,
        idx: int,
        overlap: int = 10 ,
        max_chunk_size: int = 250 
    ):
        segments = file_data.normalized_file.segments or []
        logger.info(f"Processing {segments[0].text} segments")
        if not segments:
            return [], [], [], []

        if any(seg.speakers for seg in segments):
            logger.info("Using MERGE chunking based on speakers")
            chunks = await self.merge_service.run(segments,max_chunk_size=max_chunk_size)
        else:
            logger.info("Using SEMANTIC chunking")
            chunks = await self.semantic_service.run(segments,max_chunk_size=max_chunk_size,overlap=overlap)

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




