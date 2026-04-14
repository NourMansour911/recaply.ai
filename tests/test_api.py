from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.core import get_settings
from src.orchestrators import (
    get_chains_orchestrator,
    get_chat_orchestrator,
    get_upload_orchestrator,
)
from src.routers.home_router import home_route
from src.routers.workspace_router import workspace_route
from src.schemas.files_schemas import UploadFilesResponse
from src.schemas.chains_schemas import ChainsResponse


ROOT_DIR = Path(__file__).resolve().parents[1]
TEST_TENANT_ID = "test_tenant"
TEST_PROJECT_ID = "test_project"
TEST_SESSION_ID = "test_session"
TEST_USER_ID = "test_user"


class TestHomeResponseSchema(BaseModel):
    app_name: str
    version: str
    status: str
    timestamp: str


class TestChatResponseSchema(BaseModel):
    answer: str
    tenant_id: str
    project_id: str
    user_id: str
    session_id: str


class _DummySettings:
    APP_NAME = "test_recaply"
    APP_VERSION = "test_0.0.0"


class _FakeUploadOrchestrator:
    async def execute_batch(self, files, tenant_id: str, project_id: str):
        uploaded = []
        for idx, file in enumerate(files, start=1):
            uploaded.append(
                {
                    "file_name": file.filename,
                    "file_unique_name": f"{project_id}-{idx}-{file.filename}",
                    "file_order": idx,
                }
            )

        return {
            "project_iid": project_id,
            "vectorDB_collection": f"{tenant_id}_{project_id}",
            "total_files": len(uploaded),
            "total_chunks": len(uploaded),
            "files": uploaded,
        }


class _FakeChatOrchestrator:
    async def execute(self, user_id: str, chat_request, tenant_id: str, project_id: str, session_id: str):
        return {
            "answer": f"echo: {chat_request.message}",
            "tenant_id": tenant_id,
            "project_id": project_id,
            "user_id": user_id,
            "session_id": session_id,
        }


class _FakeChainsOrchestrator:
    async def execute(self, tenant_id: str, project_id: str, user_id: str, session_id: str):
        return {
            "output": {},
            "segments": [],
        }


def _create_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(home_route)
    app.include_router(workspace_route)

    app.dependency_overrides[get_settings] = lambda: _DummySettings()
    app.dependency_overrides[get_chains_orchestrator] = lambda: _FakeChainsOrchestrator()
    app.dependency_overrides[get_upload_orchestrator] = lambda: _FakeUploadOrchestrator()
    app.dependency_overrides[get_chat_orchestrator] = lambda: _FakeChatOrchestrator()

    return TestClient(app)


def test_health_check_root_endpoint():
    client = _create_test_client()
    response = client.get("/")

    assert response.status_code == 200
    data = TestHomeResponseSchema.model_validate(response.json())
    assert data.app_name == "test_recaply"
    assert data.version == "test_0.0.0"
    assert data.status == "running"
    assert data.timestamp


def test_workspace_chat_endpoint_response_structure():
    client = _create_test_client()
    response = client.post(
        f"/api/v1/workspace/{TEST_PROJECT_ID}/chat/{TEST_SESSION_ID}/{TEST_USER_ID}",
        headers={"X-Tenant-ID": TEST_TENANT_ID},
        json={"message": "test_hello"},
    )

    assert response.status_code == 200
    data = TestChatResponseSchema.model_validate(response.json())
    assert data.answer == "echo: test_hello"
    assert data.tenant_id == TEST_TENANT_ID
    assert data.project_id == TEST_PROJECT_ID
    assert data.user_id == TEST_USER_ID
    assert data.session_id == TEST_SESSION_ID


def test_workspace_chains_endpoint_response_schema():
    client = _create_test_client()
    response = client.get(
        f"/api/v1/workspace/{TEST_PROJECT_ID}/chains/{TEST_SESSION_ID}/{TEST_USER_ID}",
        headers={"X-Tenant-ID": TEST_TENANT_ID},
    )

    assert response.status_code == 200
    data = ChainsResponse.model_validate(response.json())
    assert isinstance(data.segments, list)
    assert data.output is not None


def test_workspace_upload_endpoint_with_transcript_file():
    client = _create_test_client()
    transcript_path = ROOT_DIR / "transcript.txt"
    assert transcript_path.exists(), "transcript.txt must exist in repository root"

    with transcript_path.open("rb") as file_stream:
        response = client.post(
            f"/api/v1/workspace/{TEST_PROJECT_ID}/upload",
            headers={"X-Tenant-ID": TEST_TENANT_ID},
            files={"files": ("transcript.txt", file_stream, "text/plain")},
        )

    assert response.status_code == 200
    data = UploadFilesResponse.model_validate(response.json())
    assert data.project_iid == TEST_PROJECT_ID
    assert data.vectorDB_collection == f"{TEST_TENANT_ID}_{TEST_PROJECT_ID}"
    assert data.total_files == 1
    assert data.total_chunks == 1
    assert len(data.files) == 1
    assert data.files[0].file_name == "transcript.txt"
    assert data.files[0].file_unique_name
