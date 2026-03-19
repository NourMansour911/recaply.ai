import os
import subprocess
import tempfile
import asyncio
from helpers.logger import get_logger
from core.settings import get_settings
from helpers.disk_helper import get_project_path

logger = get_logger(__name__)
settings = get_settings()


def _run_ffmpeg_sync(cmd: list):
    """Run ffmpeg command synchronously, raise exception on failure"""
    try:
        logger.debug(f"Running ffmpeg command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.exception(f"FFmpeg failed: {e.stderr.decode()}")
        raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")


async def preprocess_audio(file_path: str, tenant_id: str, project_id: str) -> str:

    loop = asyncio.get_running_loop()
    
    # Create a temp file in project's temp folder
    temp_dir = get_project_path(tenant_id, project_id, stage="temp")
    temp_file = tempfile.NamedTemporaryFile(
        suffix=".wav", dir=temp_dir, delete=False
    )
    temp_file_path = temp_file.name
    temp_file.close()  # Will write via ffmpeg

    cmd = [
        "ffmpeg",
        "-i", file_path,
        "-ac", "1",            # mono
        "-ar", "16000",        # 16kHz
        "-af", "loudnorm",     # normalize volume
        "-y",                  # overwrite if exists
        temp_file_path
    ]

    # Run blocking ffmpeg in threadpool
    await loop.run_in_executor(None, _run_ffmpeg_sync, cmd)

    logger.debug(f"Audio preprocessed temp file: {temp_file_path}")
    return temp_file_path


async def cleanup_temp_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Temp file deleted: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to delete temp file {file_path}: {e}")