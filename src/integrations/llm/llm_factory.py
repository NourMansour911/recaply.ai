from .providers import OpenAIProvider,  HuggingFaceProvider
from helpers import get_logger
from core import Settings


logger = get_logger(__name__)
class LLMFactory:
    def __init__(self,settings: Settings):
        self.settings = settings


    def create(self, provider: str):
        if provider == "OPENAI":
            return OpenAIProvider(
                api_key = self.settings.OPENAI_API_KEY,
                api_url = self.settings.OPENAI_API_URL,

            )
            
        if provider == "HF":
            return HuggingFaceProvider()

        return None
