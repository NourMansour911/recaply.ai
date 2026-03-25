import uuid
import logging
from typing import List

from schemas import Segment, NormalizedFileData
from models.chunk_model import ChunkMetadata
from datetime import datetime

from .utils import split_with_overlap, map_word_indices_to_timing

logger = logging.getLogger(__name__)


class SemanticChunkingService:

    def __init__(self, embedding_client):
        self.embedding_client = embedding_client

    async def run(
        self,
        segments: List[Segment],
        file: NormalizedFileData,
        project_iid: str,
        tenant_id: str,
        start_idx: int,
        chunk_size: int = 300,
        overlap: int = 50,
    ):

        words, word_map = self._build_word_map(segments)

        chunks = split_with_overlap(words, chunk_size, overlap)

        timings = map_word_indices_to_timing(chunks, word_map)

        return await self._embed(
            chunks,
            timings,
            file,
            project_iid,
            tenant_id,
            start_idx
        )

    async def embed_prebuilt_chunks(
        self,
        chunks: List[Segment],
        file: NormalizedFileData,
        project_iid: str,
        tenant_id: str,
        start_idx: int,
    ):
        texts, vectors, ids, metas = [], [], [], []

        for i, chunk in enumerate(chunks):
            emb = await self.embedding_client.embed_text(chunk.text)

            metadata = ChunkMetadata(
                speakers=[],
                word_count=len(chunk.text.split()),
                file_id=file.file_id,
                file_name=file.file_name,
                file_type=file.file_type,
                file_order=file.file_order,
                language=file.normalized_file.language,
                tenant_id=tenant_id,
                project_iid=str(project_iid),
                chunk_order=start_idx + i,
                created_at=datetime.now().isoformat(),
                start=chunk.start,
                end=chunk.end,
            )

            texts.append(chunk.text)
            vectors.append(emb)
            ids.append(str(uuid.uuid4()))
            metas.append(metadata)

        return texts, vectors, ids, metas

    def _build_word_map(self, segments: List[Segment]):
        words = []
        word_map = []

        for idx, seg in enumerate(segments):
            seg_words = seg.text.split()

            for w in seg_words:
                words.append(w)
                word_map.append({
                    "start": seg.start,
                    "end": seg.end
                })

            if idx < len(segments) - 1:
                words.append("__SEP__")
                word_map.append({
                    "start": seg.end,
                    "end": seg.end
                })

        return words, word_map

    async def _embed(
        self,
        chunks,
        timings,
        file,
        project_iid,
        tenant_id,
        start_idx
    ):
        texts, vectors, ids, metas = [], [], [], []

        for i, (chunk_words, timing) in enumerate(zip(chunks, timings)):

            text = " ".join(chunk_words)
            text = text.replace(" __SEP__ ", "\n\n").replace("__SEP__", "\n\n")

            emb = await self.embedding_client.embed_text(text)

            metadata = ChunkMetadata(
                speakers=[],
                word_count=len(chunk_words),
                file_id=file.file_id,
                file_name=file.file_name,
                file_type=file.file_type,
                file_order=file.file_order,
                language=file.normalized_file.language,
                tenant_id=tenant_id,
                project_iid=str(project_iid),
                chunk_order=start_idx + i,
                created_at=datetime.now().isoformat(),
                start=timing.get("start"),
                end=timing.get("end"),
            )

            texts.append(text)
            vectors.append(emb)
            ids.append(str(uuid.uuid4()))
            metas.append(metadata)

        return texts, vectors, ids, metas