# CI and API Tests

This folder contains the GitHub Actions setup for CI, continuous delivery, and API test coverage.

## What Is Inside

- `ci.yml`: installs dependencies, runs lint and tests, optionally builds/tests/pushes Docker image.


## Required GitHub Secrets

- `DOCKER_USERNAME`
- `DOCKER_PASSWORD` (Docker Hub access token)

## CI Flow

1. CI starts on `push`, `pull_request`, or manual dispatch.
2. Python 3.11 is prepared with pip cache.
3. Ruff lint and `pytest -v` are executed.
4. On push events, Docker build/push can be skipped with `[no build]` in the commit message.
5. If image build is enabled, CI builds `docker/api/Dockerfile` locally.
6. CI runs a smoke test container (`/` health check) before publishing.
7. If smoke test passes, image tags are pushed to Docker Hub.

## Image Tags

- `:<git-sha>` for each pushed commit
- `:latest` for `main`
- `:<git-tag>` when the workflow runs on tag pushes

## Notes

- CI includes Docker layer caching via Buildx (`type=gha`) for faster rebuilds.
- Pull requests do not push images.

## Tests

- Main API tests are in [tests/test_api.py](../../tests/test_api.py).
- Test bootstrap is in [tests/conftest.py](../../tests/conftest.py).
- Coverage includes:
  - Health endpoint (`/`)
  - Workspace chat endpoint
  - Workspace chains endpoint
  - Workspace upload endpoint (using `transcript.txt`)
