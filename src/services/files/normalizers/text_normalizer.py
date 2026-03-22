from typing import Dict, Any, List
from .base_normalizer import BaseNormalizer
from core.exceptions import TextExtractionException
from helpers.logger import get_logger
import PyPDF2
import docx

logger = get_logger(__name__)

class TextNormalizer(BaseNormalizer):
    
        
    async def normalize(self,file_path,file_name,file_type ,tenant_id,project_id,language) -> Dict[str, Any]:
        
        try:
            if file_type == 'txt':
                text_content = self._read_text_file()
            elif file_type == 'pdf':
                text_content = self._read_pdf_file()
            else:
                raise TextExtractionException(
                    file_name=file_name,
                    extraction_error="Unsupported text format"
                )
                
            
            
            
            segments = [{
                "segment_id": "seg_0",
                "text": text_content.strip(),
                "start":None,
                "end": None, 
                "speaker": None,
                "page": 1,
                "source": file_type
            }]
            
            # Calculate metadata
            word_count = len(text_content.split())
            
            # Build result
            result = self._create_base_schema(file_type)
            result["segments"] = segments
            result["metadata"]["duration"] = 0.0
            result["metadata"]["word_count"] = word_count
            
            return result
            
        except TextExtractionException:
            raise
        except Exception as e:
            logger.error(f"Text normalization failed: {str(e)}")
            raise TextExtractionException(
                file_name=file_name,
                file_type=file_type,
                extraction_error=str(e)
            )
    
    def _read_text_file(self,file_path,file_name) -> str:
    
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                raise TextExtractionException(
                    file_name=file_name,
                    file_type="txt",
                    extraction_error=f"Encoding error: {str(e)}"
                )
        except Exception as e:
            raise TextExtractionException(
                file_name=file_name,
                file_type="txt",
                extraction_error=str(e)
            )
    
    def _read_pdf_file(self,file_path,file_name) -> str:
        """Read PDF file and extract text"""
        try:
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"[Page {page_num + 1}]\n{page_text}\n\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PDF reading failed: {str(e)}")
            raise TextExtractionException(
                file_name=file_name,
                file_type="pdf",
                extraction_error=f"PDF reading failed: {str(e)}"
            )
    
