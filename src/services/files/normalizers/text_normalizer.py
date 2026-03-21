from typing import Dict, Any, List
from .base_normalizer import BaseNormalizer
from core.exceptions import TextExtractionException
from helpers.logger import get_logger
import PyPDF2
import docx

logger = get_logger(__name__)

class TextNormalizer(BaseNormalizer):
    """Normalizer for text-based files (txt, pdf)"""
    
    def __init__(self, file_path: str, language: str = "en"):
        super().__init__(file_path, language)
        self.file_extension = file_path.lower().split('.')[-1]
        
    async def normalize(self) -> Dict[str, Any]:
        """Normalize text file to standard JSON schema"""
        try:
            if self.file_extension == 'txt':
                text_content = self._read_text_file()
            elif self.file_extension == 'pdf':
                text_content = self._read_pdf_file()
            elif self.file_extension in ['doc', 'docx']:
                text_content = self._read_docx_file()
            else:
                raise TextExtractionException(
                    file_name=self.file_name,
                    file_type=self.file_extension,
                    extraction_error="Unsupported text format"
                )
                
            # Create single segment for text content
            segments = [{
                "segment_id": "seg_0",
                "text": text_content.strip(),
                "start": 0.0,
                "end": 0.0,  # No timing info for text files
                "speaker": None,
                "page": 1,
                "source": self.file_extension
            }]
            
            # Calculate metadata
            word_count = len(text_content.split())
            
            # Build result
            result = self._create_base_schema(self.file_extension)
            result["segments"] = segments
            result["metadata"]["duration"] = 0.0
            result["metadata"]["word_count"] = word_count
            
            return result
            
        except TextExtractionException:
            raise
        except Exception as e:
            logger.error(f"Text normalization failed: {str(e)}")
            raise TextExtractionException(
                file_name=self.file_name,
                file_type=self.file_extension,
                extraction_error=str(e)
            )
    
    def _read_text_file(self) -> str:
        """Read plain text file"""
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
        """Read PDF file and extract text"""
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
            logger.error(f"PDF reading failed: {str(e)}")
            raise TextExtractionException(
                file_name=self.file_name,
                file_type="pdf",
                extraction_error=f"PDF reading failed: {str(e)}"
            )
    
    def _read_docx_file(self) -> str:
        """Read DOCX file and extract text"""
        try:
            doc = docx.Document(self.file_path)
            text = ""
            for para in doc.paragraphs:
                if para.text.strip():
                    text += para.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX reading failed: {str(e)}")
            raise TextExtractionException(
                file_name=self.file_name,
                file_type="docx",
                extraction_error=f"DOCX reading failed: {str(e)}"
            )
