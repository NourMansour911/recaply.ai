from .base_normalizer import BaseNormalizer
from .normalize_exceptions import TextExtractionException
from helpers.logger import get_logger
import PyPDF2
from schemas.normalized_schemas import Segment,NormalizedContent
from typing import List

logger = get_logger(__name__)

class TextNormalizer(BaseNormalizer):
    
    def __init__(self, file_path: str, file_name: str, file_type: str, tenant_id: str, project_id: str, language: str ):
        self.file_path = file_path
        self.file_name = file_name
        self.file_type = file_type
        self.tenant_id = tenant_id
        self.project_id = project_id
        self.language = language
    
    async def normalize(self) -> NormalizedContent:
        try:
            if self.file_type == 'txt':
                text_content = self._read_text_file()
            elif self.file_type == 'pdf':
                text_content = self._read_pdf_file()
            else:
                raise TextExtractionException(
                    file_name=self.file_name,
                    file_type=self.file_type,
                    extraction_error="Unsupported text format"
                )
            
            segment_objects = self.split_text_into_segments(
            text_content,
            words_per_segment=70  
        )
            
            
            merged_segments = self.merge_small_segments(segment_objects)
            logger.info("Text normalization completed")
            
            result = self._create_normalized_file_model( self.language, merged_segments)
            return result
            

        except Exception as e:
            logger.error(
                "Text normalization failed",
                extra={
                    "file_name": self.file_name,
                    "file_type": self.file_type,
                    "tenant_id": self.tenant_id,
                    "project_id": self.project_id,
                    "error": str(e)
                }
            )
            raise TextExtractionException(
                file_name=self.file_name,
                file_type=self.file_type,
                extraction_error=str(e)
            )
    
    def split_text_into_segments(
    self,
    text: str,
    words_per_segment: int = 80
    ) -> List[Segment]:

        words = text.split()
        segments = []

        start_idx = 0
        segment_counter = 0

        while start_idx < len(words):
            end_idx = start_idx + words_per_segment
            chunk_words = words[start_idx:end_idx]

            segment_text = " ".join(chunk_words)

            segments.append(
                Segment(
                    text=segment_text,
                    start=0.0,  
                    end=0.0,
                    speakers=None,
                    
                )
            )

            start_idx = end_idx
            segment_counter += 1

        return segments
    def _read_text_file(self) -> str:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(self.file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                raise TextExtractionException(
                    file_name=self.file_name,
                    file_type="txt",
                    extraction_error=f"Encoding error: {str(e)}"
                )
        except Exception as e:
            raise TextExtractionException(
                file_name=self.file_name,
                file_type="txt",
                extraction_error=str(e)
            )
    
    def _read_pdf_file(self) -> str:
        try:
            text = ""
            with open(self.file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"[Page {page_num + 1}]\n{page_text}\n\n"
            return text.strip()
        except Exception as e:
            logger.error(
                "PDF reading failed",
                extra={
                    "file_name": self.file_name,
                    "tenant_id": self.tenant_id,
                    "project_id": self.project_id,
                    "error": str(e)
                }
            )
            raise TextExtractionException(
                file_name=self.file_name,
                file_type="pdf",
                extraction_error=f"PDF reading failed: {str(e)}"
            )
