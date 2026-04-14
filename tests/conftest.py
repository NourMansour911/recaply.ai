from pathlib import Path
import os
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

os.environ.setdefault("APP_NAME", "test_recaply")
os.environ.setdefault("APP_VERSION", "test_0.0.0")
os.environ.setdefault("STORAGE_PATH", str(ROOT_DIR / "storage"))
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DATABASE", "test_recaply")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("MAX_AUDIO_SIZE_MB", "100")
os.environ.setdefault("MAX_TEXT_SIZE_MB", "100")
os.environ.setdefault("MAX_SUBTITLE_SIZE_MB", "100")
os.environ.setdefault("MAX_PDF_SIZE_MB", "100")
os.environ.setdefault("TO_BYTES", "1048576")
os.environ.setdefault("CHUNK_OVERLAP", "200")
os.environ.setdefault("CHUNK_MIN_SIZE", "200")
os.environ.setdefault("CHUNK_MAX_SIZE", "1000")
os.environ.setdefault("CHUNKS_SIMILARITY_THRESHOLD", "0.75")
os.environ.setdefault("COHERE_API_KEY", "test-cohere-key")
os.environ.setdefault("LANGSMITH_API_KEY", "test-langsmith-key")
os.environ.setdefault("OPENAI_API_URL", "https://api.openai.com/v1")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("GENERATION_BACKEND", "OPENAI")
os.environ.setdefault("GENERATION_MODEL_ID", "test-model")
os.environ.setdefault("EMBEDDING_BACKEND", "HF")
os.environ.setdefault("EMBEDDING_MODEL_ID", "test-embed-model")
os.environ.setdefault("EMBEDDING_MODEL_SIZE", "384")
os.environ.setdefault("TOP_K_DOCS", "5")
os.environ.setdefault("VECTOR_DB_BACKEND", "QDRANT")
os.environ.setdefault("VECTOR_DB_DISTANCE_METHOD", "Cosine")

for path in (ROOT_DIR, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))