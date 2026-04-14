# CI/CD and API Tests

This folder contains the GitHub Actions setup for CI, continuous delivery, and API test coverage.

## What is inside
- `workflows/ci.yml`: runs linting and tests, then builds the Docker image on `main` and uploads it as an artifact.
- `workflows/cd.yml`: runs after CI succeeds on `main`, downloads the image artifact, loads it, and pushes it to Docker Hub.

## Required GitHub Secrets
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD` (Docker Hub access token)

## Pipeline Flow
1. Push or manual run starts CI.
2. CI installs Python 3.11 dependencies.
3. CI runs Ruff linting and `pytest -v`.
4. On `main`, CI builds `docker/api/Dockerfile` into a Docker image artifact.
5. CD starts only after CI succeeds on `main`.
6. CD downloads the artifact, loads the Docker image locally, logs in to Docker Hub, and pushes the image.

## Why this is continuous delivery
- CI validates the code and builds the image.
- CD delivers the already-built image to Docker Hub.
- The image promotion step is separated from the build step, which keeps the flow safer and clearer.

## Tests
- Main API tests are in [tests/test_api.py](../tests/test_api.py).
- Test bootstrapping is in [tests/conftest.py](../tests/conftest.py).
- Coverage includes:
  - Basic health check (`/`)
  - Workspace chat endpoint test
  - Workspace chains endpoint test
  - Workspace file upload test using `transcript.txt`
