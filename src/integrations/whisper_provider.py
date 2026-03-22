
from faster_whisper import WhisperModel
from helpers.logger import get_logger

logger = get_logger(__name__)


class WhisperProvider:
    def __init__(self, model_size: str = "base", device: str = "cuda"):
        self.model_size = model_size
        self.device = device
        self._model: WhisperModel | None = None

    def load(self):
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            self._model = WhisperModel(self.model_size, device=self.device)
        return self._model

    def get_model(self) -> WhisperModel:
        if self._model is None:
            raise RuntimeError("Whisper model not loaded")
        return self._model
    

whisper_provider = WhisperProvider()

def get_whisper_provider():
    return whisper_provider