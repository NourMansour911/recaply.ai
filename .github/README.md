# CI/CD and API Tests

This folder contains automation only for CI/CD and endpoint tests.

## What is inside
- `workflows/ci-cd.yml`: Runs tests, builds Docker image, tags with commit SHA + latest, and pushes to Docker Hub.

## Required GitHub Secrets
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD` (Docker Hub access token)

## What the pipeline does
1. Installs Python 3.11 and project dependencies
2. Runs `pytest -v`
3. Stops immediately if tests fail
4. Builds Docker image from `docker/api/Dockerfile`
5. Tags image as `${DOCKER_USERNAME}/recaply:${GITHUB_SHA}` and `${DOCKER_USERNAME}/recaply:latest`
6. Pushes both tags to Docker Hub

## Tests
- Main API tests are in `tests/test_api.py`
- Includes:
  - Basic health check (`/`)
  - Workspace chat endpoint test
  - Workspace file upload test using `transcript.txt`
