from .base_normalizer import BaseNormalizer
from .normalize_exceptions import TextExtractionException
from helpers.logger import get_logger
import PyPDF2
from src.schemas.normalized_schemas import Segment

logger = get_logger(__name__)

class TextNormalizer(BaseNormalizer):
    
    def __init__(self, file_path: str, file_name: str, file_type: str, tenant_id: str, project_id: str, language: str ):
        self.file_path = file_path
        self.file_name = file_name
        self.file_type = file_type
        self.tenant_id = tenant_id
        self.project_id = project_id
        self.language = language
    
    async def normalize(self):
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
            
            segment_objects = [
                Segment(
                    segment_id="seg_0",
                    text=text_content.strip(),
                    start=0.0,
                    end=0.0, 
                    speaker=None,
                    page=1
                )
            ]
            
            result = self._create_normalized_file_model(

                language=self.language,
                segments=segment_objects,
                
            )
            
            return result
            
        except TextExtractionException:
            raise
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
