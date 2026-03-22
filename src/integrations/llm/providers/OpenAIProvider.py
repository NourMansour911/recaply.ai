from ..llm_interface import LLMInterface
from openai import OpenAI, APIError, RateLimitError
from helpers import get_logger
from ..llm_enums import OpenAIEnums
from ..llm_exceptions import (
    LLMInitializationException,
    LLMGenerationException,
    LLMEmbeddingException,
    LLMModelNotSetException,
    LLMAPINotAvailableException,
    LLMRateLimitException,
    LLMInvalidResponseException
)

logger = get_logger(__name__)


class OpenAIProvider(LLMInterface):
    def __init__(self,
                api_key: str,
                api_url: str = None,
                default_input_max_chars=2048,
                default_out_max_tokens=500,
                default_temperature=0.7,
                ):
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_chars = default_input_max_chars
        self.default_out_max_tokens = default_out_max_tokens
        self.default_temperature = default_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        try:
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise LLMInitializationException(
                provider="OpenAI",
                init_error=str(e)
            )
                
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        logger.debug(f"OpenAI generation model set to: {model_id}")
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        logger.info(f"OpenAI embedding model set to: {model_id}")
        logger.info(f"OpenAI embedding size set to: {embedding_size}")
   
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": prompt
        }
    
    def generate_text(self, prompt: str, chat_history: list = [], temperature: float = None, max_out_tokens: int = None):
        if not self.client:
            logger.error("OpenAI Client not initialized")
            raise LLMModelNotSetException(
                operation="generation",
                model_type="generation",
                provider="OpenAI"
            )
        
        if not self.generation_model_id:
            logger.error("OpenAI Generation model not set")
            raise LLMModelNotSetException(
                operation="text generation",
                model_type="generation",
                provider="OpenAI"
            )
        
        if not temperature:
            temperature = self.default_temperature
            
        if not max_out_tokens:
            max_out_tokens = self.default_out_max_tokens
            
        try:
            chat_history.append(self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value))
        
            response = self.client.chat.completions.create(
                model=self.generation_model_id,
                messages=chat_history,
                temperature=temperature,
                max_tokens=max_out_tokens
            )
            
            if not response or not response.choices or not response.choices[0].message.content:
                logger.error("OpenAI Error while generating text - invalid response")
                raise LLMInvalidResponseException(
                    model_id=self.generation_model_id,
                    response_data=str(response)[:200] if response else None,
                    validation_error="No content in response"
                )
            
            return response.choices[0].message.content
            
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise LLMRateLimitException(
                model_id=self.generation_model_id,
                retry_after=getattr(e, 'reset', None)
            )
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMAPINotAvailableException(
                provider="OpenAI",
                api_endpoint="chat/completions",
                network_error=str(e)
            )
        except Exception as e:
            logger.error(f"Error while generating text: {e}")
            raise LLMGenerationException(
                model_id=self.generation_model_id,
                prompt=prompt[:100],
                generation_error=str(e)
            )

    def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            logger.error("OpenAI Client not initialized")
            raise LLMModelNotSetException(
                operation="embedding",
                model_type="embedding",
                provider="OpenAI"
            )
        
        if not self.embedding_model_id:
            logger.error("OpenAI Embedding model not set")
            raise LLMModelNotSetException(
                operation="text embedding",
                model_type="embedding",
                provider="OpenAI"
            )

        try:
            response = self.client.embeddings.create(
                model=self.embedding_model_id,
                input=[text]
            )    
            
            if not response.data or not response.data[0].embedding:
                logger.error("OpenAI Error while embedding text - invalid response")
                raise LLMInvalidResponseException(
                    model_id=self.embedding_model_id,
                    response_data=str(response)[:200] if response else None,
                    validation_error="No embedding in response"
                )
                
            return response.data[0].embedding
            
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise LLMRateLimitException(
                model_id=self.embedding_model_id,
                retry_after=getattr(e, 'reset', None)
            )
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMAPINotAvailableException(
                provider="OpenAI",
                api_endpoint="embeddings",
                network_error=str(e)
            )
        except Exception as e:
            logger.error(f"Error while embedding text: {e}")
            raise LLMEmbeddingException(
                model_id=self.embedding_model_id,
                text_sample=text[:50],
                embedding_error=str(e)
            )
