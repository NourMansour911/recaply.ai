from typing import List
from schemas import Segment
from scipy.spatial.distance import cosine  

class SemanticChunkingService:

    def __init__(self, embedding_client, similarity_threshold: float = 0.85):
        self.embedding_client = embedding_client
        self.similarity_threshold = similarity_threshold

    async def run(
        self,
        segments: List[Segment],
        max_chunk_size: int,
        overlap: int 
    ):


       
        all_words = []
        for seg in segments:
            all_words.extend(seg.text.split())

        
        chunks_words = []
        i = 0
        while i < len(all_words):
            end = min(i + max_chunk_size, len(all_words))
            chunks_words.append(all_words[i:end])
            if end >= len(all_words):
                break
            i = end - overlap

       
        chunks: List[Segment] = []
        for chunk in chunks_words:
            text = " ".join(chunk)
            chunks.append(Segment(text=text, start=None, end=None, speakers=None))

        
        embeddings = []
        for chunk in chunks:
            emb = await self.embedding_client.embed_text(chunk.text)
            embeddings.append(emb)

        
        final_chunks = []
        if not chunks:
            return final_chunks

        current_chunk = chunks[0]
        current_emb = embeddings[0]

        for next_chunk, next_emb in zip(chunks[1:], embeddings[1:]):
            similarity = 1 - cosine(current_emb, next_emb)
            if similarity >= self.similarity_threshold:
                
                merged_text = f"{current_chunk.text}\n{next_chunk.text}"
                current_chunk = Segment(
                    text=merged_text,
                    start=current_chunk.start,
                    end=next_chunk.end,
                    speakers=current_chunk.speakers  
                )
                
                current_emb = [(a + b) / 2 for a, b in zip(current_emb, next_emb)]
            else:
                final_chunks.append(current_chunk)
                current_chunk = next_chunk
                current_emb = next_emb

       
        final_chunks.append(current_chunk)


        return final_chunks