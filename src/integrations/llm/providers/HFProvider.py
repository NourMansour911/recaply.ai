from ..llm_interface import LLMInterface
from sentence_transformers import SentenceTransformer
from helpers import get_logger
from ..llm_exceptions import (
    LLMInitializationException,
    LLMEmbeddingException,
    LLMModelNotSetException
)

logger = get_logger(__name__)


class HuggingFaceProvider(LLMInterface):
    def __init__(self,
                default_input_max_chars=2048,
                default_out_max_tokens=500,
                default_temperature=0.7,
                ):
        self.default_input_max_chars = default_input_max_chars
        self.default_out_max_tokens = default_out_max_tokens
        self.default_temperature = default_temperature
        
        self.embedding_model_id = None
        self.embedding_size = None
        self.client = None
        
    def set_generation_model(self, model_id: str):
        logger.warning("HuggingFaceProvider doesn't support text generation. Use OpenRouter or OpenAI for that.")
        self.generation_model_id = None
        raise NotImplementedError("HuggingFaceProvider doesn't support text generation")
        
    def set_embedding_model(self, model_id: str, embedding_size: int = None):
        try:
            self.embedding_model_id = model_id
            self.embedding_size = embedding_size
            self.client = SentenceTransformer(model_id)
            
            if not self.embedding_size:
                sample_embedding = self.client.encode("test")
                self.embedding_size = len(sample_embedding)
                
            logger.info(f"HuggingFace model '{model_id}' loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model '{model_id}': {e}")
            raise LLMInitializationException(
                model_id=model_id,
                provider="HuggingFace",
                init_error=str(e)
            )
    

    
    def construct_prompt(self, prompt: str, role: str):
        raise NotImplementedError("HuggingFaceProvider doesn't support prompt construction")
        
    def generate_text(self, prompt: str, chat_history: list = [], temperature: float = None, max_out_tokens: int = None):
        raise NotImplementedError("HuggingFaceProvider doesn't support text generation")
    
    async def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            logger.error("HuggingFace Client not initialized")
            raise LLMModelNotSetException(
                operation="embedding",
                model_type="embedding",
                provider="HuggingFace"
            )
            
        try:
            
            embedding = self.client.encode(text)
            return embedding.tolist() if hasattr(embedding, 'tolist') else embedding
        except Exception as e:
            logger.error(f"Error while embedding text: {e}")
            raise LLMEmbeddingException(
                model_id=self.embedding_model_id,
                text_sample=text[:50],
                embedding_error=str(e)
            )
