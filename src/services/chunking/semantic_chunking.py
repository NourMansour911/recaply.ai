from typing import List
from schemas import Segment
from scipy.spatial.distance import cosine
from helpers.logger import get_logger

logger = get_logger(__name__)

class SemanticChunkingService:

    def __init__(self, embedding_client, similarity_threshold: float = 0.70):
        self.embedding_client = embedding_client
        self.similarity_threshold = similarity_threshold

    async def run(
        self,
        segments: List[Segment],
        max_chunk_size: int = 300,
        overlap: int = 20
    ) -> List[Segment]:

        if not segments:
            return []

        chunks: List[Segment] = []
        i = 0
        while i < len(segments):
            chunk_texts = []
            chunk_start = segments[i].start
            chunk_end = segments[i].end
            word_count = 0
            seg_idx = i

            # جمع النصوص مع الحفاظ على separators حتى الوصول للـ max_chunk_size
            while seg_idx < len(segments) and word_count < max_chunk_size:
                seg = segments[seg_idx]
                chunk_texts.append(seg.text)  # نحافظ على \n الأصلية
                chunk_end = seg.end
                word_count += len(seg.text.split())
                seg_idx += 1

            chunks.append(Segment(
                text="\n".join(chunk_texts),
                start=chunk_start,
                end=chunk_end,
                speakers=None
            ))

            # move index forward مع overlap
            if seg_idx >= len(segments):
                break

            # حساب عدد الـ segments المغطاة بالـ overlap على مستوى الكلمات
            overlap_count = 0
            overlap_words = 0
            back_idx = seg_idx - 1
            while back_idx >= i and overlap_words < overlap:
                overlap_words += len(segments[back_idx].text.split())
                back_idx -= 1
                overlap_count += 1
            i = seg_idx - overlap_count  # رجوع بمقدار الـ overlap

        # 2️⃣ حساب embeddings لكل chunk
        embeddings = []
        for chunk in chunks:
            emb = await self.embedding_client.embed_text(chunk.text)
            embeddings.append(emb)

        # 3️⃣ دمج chunks حسب similarity threshold
        final_chunks = []
        current_chunk = chunks[0]
        current_emb = embeddings[0]

        for next_chunk, next_emb in zip(chunks[1:], embeddings[1:]):
            similarity = 1 - cosine(current_emb, next_emb)
            logger.info(f"Similarity between chunks: {similarity:.3f}")

            if similarity >= self.similarity_threshold:
                # دمج مع الحفاظ على start/end و separators
                merged_text = f"{current_chunk.text}\n{next_chunk.text}"
                current_chunk = Segment(
                    text=merged_text,
                    start=current_chunk.start,
                    end=next_chunk.end,
                    speakers=current_chunk.speakers
                )
                # متوسط embeddings
                current_emb = [(a + b) / 2 for a, b in zip(current_emb, next_emb)]
            else:
                final_chunks.append(current_chunk)
                current_chunk = next_chunk
                current_emb = next_emb

        final_chunks.append(current_chunk)
        return final_chunks