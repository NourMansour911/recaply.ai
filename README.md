# Recaply AI — Meeting Intelligence Platform


A production-grade FastAPI backend for ingesting, indexing, and analyzing meeting files with retrieval-augmented AI chat and structured meeting report generation.

Built with clean architecture, dependency injection, custom provider abstractions, Redis-backed chat memory, and sophisticated retrieval-augmented generation pipelines.

---

## Part I: Quick Project Snapshot

| Aspect | Highlights |
|--------|-----------|
| **Core Purpose** | Upload meeting files → search intelligently → get cited answers → generate structured recaps |
| **Key Innovation** | Citation system links every AI answer/insight back to exact meeting segment with timestamps |
| **Architecture** | Layered FastAPI with dependency injection, custom providers, singleton patterns |
| **AI Pipeline** | Query rewriting + multi-method retrieval + reranking + citation-aware generation |
| **Tech Stack** | FastAPI, Python, Pydantic, MongoDB, Redis, Qdrant, Whisper, Cohere, LangChain, Docker |
| **State & Memory** | MongoDB for project/file metadata and Redis for chat memory and short-lived session state |
| **CI & Delivery** | Docker containerized, GitHub Actions CI, test-gated image build and push to Docker Hub |

Docker Hub Repository: [https://hub.docker.com/r/nourmansour41/recaply](https://hub.docker.com/r/nourmansour41/recaply)
---

## The Problem Recaply Solves

Most teams already have meeting content, but they do not have a reliable way to turn that content into searchable institutional memory.

The usual pain points are:

- meeting transcripts are long and hard to search quickly
- important decisions get buried in raw audio or text
- answers need evidence, not just a summary
- recap work is repetitive and manual
- different file types live in different tools, so context gets fragmented

Recaply solves this by turning meeting files into a cited, searchable knowledge layer with timestamps, structured outputs, and workspace-level memory.

## Why It Is Different

Recaply is not just another meeting summarizer.

It is designed as a meeting intelligence platform, which means it focuses on three things most tools miss:

1. **Traceability** - every answer and insight points back to exact source segments.
2. **Retrievability** - the system combines query rewriting, hybrid search, fusion, and reranking instead of relying on one weak search step.
3. **Business usefulness** - it produces decisions, tasks, risks, sentiment, and summary artifacts that can actually be used by teams.

That makes it closer to an evidence-backed operations layer for meetings than a generic chatbot.

## Feature Set

- upload audio, transcript, subtitle, and PDF meeting files
- normalize files into timestamped segments
- build workspace-level searchable memory
- run cited natural-language chat over meeting content
- generate structured reports for decisions, tasks, risks, conflicts, sentiment, and summary
- support hybrid retrieval across semantic and keyword signals
- rerank retrieval results before generation
- keep short-term chat memory in Redis
- persist projects and files in MongoDB
- expose observability through logs, metrics, and tracing

## Tech Stack

| Layer | Technologies |
|------|--------------|
| **API** | FastAPI, Uvicorn, Python 3.11, Pydantic |
| **Persistence** | MongoDB for metadata and project storage |
| **Memory** | Redis for chat memory and session state |
| **Vector Search** | Qdrant in the default compose stack |
| **AI / NLP** | Whisper, LangChain, OpenAI-compatible providers, Cohere reranking |
| **Media Processing** | FFmpeg |
| **Delivery** | Docker, Docker Compose, GitHub Actions |
| **Observability** | Prometheus, Grafana, LangSmith, structured logging |

## Part II: Business Overview

### What Recaply Does

Recaply is an AI meeting intelligence platform designed for teams that handle many meeting assets (audio, transcripts, subtitles, PDFs) and need fast, accurate retrieval of what was actually discussed.

**Core workflow:**
1. Upload multiple meeting file types into a workspace
2. System auto-normalizes and builds a searchable meeting memory
3. Ask natural-language questions and get grounded answers with source citations
4. Generate structured meeting reports (decisions, tasks, risks, sentiment, etc.) with links back to source segments

### Business Value Proposition

| Challenge | Solution | Impact |
|-----------|----------|--------|
| Rewatching long meetings to find one snippet | RAG-powered search + clickable meeting timestamps | Save hours per week per user |
| Lose context about who decided what and when | Citation system links every answer/insight to exact meeting segment | Audit-friendly decision traceability |
| Manual meeting recap work (notes, action items) | Automated structured chain analysis | Faster, more consistent recaps |
| Teams working across timezones | Async-friendly search and reference interface | Better collaboration |

### Target Use Cases

- Mid-to-large teams with frequent meetings (sales, product, engineering, legal)
- Regulatory/compliance workflows requiring decision traceability
- Organizations that record meetings in multiple formats

---

## Part III: System Architecture

### High-Level Design

Recaply follows a **layered FastAPI architecture**:

```
HTTP Request
    ↓
Router (endpoint validation)
    ↓
Orchestrator (workflow coordination)
    ↓
Services (business logic + AI)
    ↓
Repositories & Integrations (data + external systems)
```

This separation ensures:
- Clean HTTP boundaries (routers stay thin)
- Reusable business logic (services are composable)
- Easy testing (dependency injection throughout)
- Clear responsibility ownership

### Core Components

| Component | Purpose |
|-----------|---------|
| **Routers** | HTTP endpoints for workspace, files, projects, vector DB |
| **Orchestrators** | Workflow coordinators (upload, chains, chat) |
| **Services** | AI pipelines and business logic |
| **Repositories** | MongoDB persistence (files, projects) |
| **Integrations** | Adapters to LLMs, Whisper, vector DB, Redis |

For detailed architecture breakdown, see [src/README.md](src/README.md).

---

## Part IV: How Meeting Data Flows Through the System

### Phase 1: Upload & Ingestion

When a user uploads meeting files:

1. **File Detection** → Identify MIME type (audio, text, PDF, subtitle)
2. **File Validation** → Check file size, existence, format compliance
3. **File Storage** → Save raw file to disk with deterministic path structure
4. **Normalization** → Convert file into standardized `Segment` objects (text + time bounds)
5. **Chunking** → Group segments intelligently using semantic or speaker-based strategies
6. **Embedding** → Generate vector embeddings for each chunk
7. **Vector DB Indexing** → Store chunks with hybrid indexing (BM25 + vector search)

**Why this pipeline is well-engineered:**
- Strict validation gates expensive processing
- Deterministic file ordering ensures consistent replay references
- Hybrid indexing improves retrieval precision
- Segments become the core unit across all downstream workflows

### Phase 2: Structured Analysis (Chains)

Once indexed, the system can generate structured meeting artifacts:

- **Context Extraction** → Who attended, agenda, key purpose
- **Decisions Chain** → Extract decisions with confidence scores
- **Tasks Chain** → Identify action items and owners
- **Risks Chain** → Detect risk factors and mitigations
- **Conflicts Chain** → Identify disagreements or tensions
- **Sentiment Chain** → Overall meeting tone and highlights
- **Summary Chain** → High-level recap points

Each chain output includes segment IDs, allowing the orchestrator to link results back to exact source points.

### Phase 3: RAG Chat

Users can ask questions about meeting content:

1. **Query Rewriting** → LLM generates alternative queries to improve coverage
2. **Multi-Query Retrieval** → Parallel semantic + keyword searches using query rewrites
3. **Reciprocal Rank Fusion** → Intelligently merge semantic and keyword results
4. **Reranking** → Cohere API reranks top-20 results for relevance
5. **Generation** → LLM answers using retrieved context with document citations
6. **Citation Mapping** → Convert document indices back to metadata (file, timestamp, order)

**Retrieval Strategy:**
- Semantic search captures meaning-based matches
- Keyword (BM25) captures exact phrase hits
- RRF fusion balances both signals
- Top-K reranking ensures highest-quality context reaches the LLM
- Strict citation rules prevent hallucination

For retrieval implementation details, see [src/README.md](src/README.md) § 7.

---

## Part V: Services Explained

The system is composed of focused, reusable services:

| Service Group | Responsibility | Examples |
|---|---|---|
| **File Services** | Detection, validation, storage | FileDetectorService, FileValidatorService, FileStorageService |
| **Normalizers** | Convert raw files to segments | WhisperNormalizer, TextNormalizer, PDFNormalizer, SubtitleNormalizer |
| **Chunking** | Segment grouping & embedding prep | SemanticChunkingService, MergeChunkingService |
| **Chains** | Structured LLM pipelines | ChainsService (orchestrates all chain types) |
| **Chat** | RAG and answer generation | ChatService, Retrieval, Reranker, QueryRewrite |
| **Project Services** | Lifecycle operations | ProjectService, VDBService |

Each service is independently testable and reusable.

See [src/README.md](src/README.md) § 5 for detailed service responsibilities.

---

## Part VI: Engineering Strengths

### From a Product/Business Perspective

✓ **Citation System** → Every answer links to exact auditable source  
✓ **Multi-Format Support** → Audio, text, subtitles, PDFs all work  
✓ **Fast Search** → Hybrid indexing + reranking for sub-second results  
✓ **Accurate Answers** → Stacked retrieval + reranking prevents hallucination  
✓ **Scalable Workspace Model** → Tenants can have unlimited projects/files  

### From an Engineering Perspective

✓ **Clean Architecture** → Routers → Orchestrators → Services → Repos  
✓ **Dependency Injection** → Easy to mock/test, no globals  
✓ **Composable Services** → Same services used across chat and chains  
✓ **Strong Type Safety** → Pydantic schemas everywhere  
✓ **Observable** → Structured logging, LangSmith tracing, Prometheus metrics  
✓ **Error Handling** → Custom exceptions with business context  

For in-depth code review notes, see [src/README.md](src/README.md).

### From a Deployment & Scalability Perspective

✓ **Stateless API** → Horizontally scalable (no session affinity needed)  
✓ **Async/Await** → Efficient I/O handling for external APIs  
✓ **Containerized** → Docker image with all system dependencies baked in  
✓ **Full-Stack Monitoring** → Prometheus + Grafana for metrics, logs, traces  
✓ **Test-Gated Pipeline** → CI fails fast if tests fail before image publish  
✓ **Multi-Environment Ready** → Docker Compose with MongoDB, Qdrant, Redis  

---

## Part VII: Development Workflow

### Local Development

Set up a Python 3.11 environment and run:

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 5000
```

API docs available at: http://localhost:5000/docs

### Testing

Run the test suite:

```bash
pytest -v
```

Tests include:
- Health check endpoint
- Workspace chat and chains endpoints
- File upload with real multipart requests using transcript.txt

Test setup is handled in [tests/conftest.py](tests/conftest.py), which provides the required import path and environment values before the app is imported.

For test details, see [.github/workflows/README.md](.github/workflows/README.md).

### Code Structure

- `src/` → Backend code (see [src/README.md](src/README.md))
- `tests/` → API test suite
- `docker/` → Containerization and compose stack (see [docker/README.md](docker/README.md))
- `.github/workflows/` → CI workflow and pipeline docs (see [.github/workflows/README.md](.github/workflows/README.md))

---

## Part VIII: CI & Operations

### Docker Containerization

The API is containerized with a multi-stage Docker build (`docker/api/Dockerfile`) to reduce runtime image size.

Current build highlights:
- Builder and runtime stages are separated to keep toolchains out of runtime.
- Runtime is based on slim Python image for lower footprint.
- Torch is installed from CPU wheels during build to avoid CUDA-heavy layers.

For local development with full stack (MongoDB, Qdrant, Redis, Prometheus, Grafana), see [docker/README.md](docker/README.md).

### CI Pipeline

The repository currently uses a single workflow:

1. [ci.yml](.github/workflows/ci.yml)
    - runs on push, pull request, and manual dispatch
    - installs dependencies and uses pip cache
    - runs Ruff linting and pytest
    - on push, can skip build/push with `[no build]` in commit message
    - builds Docker image locally
    - runs smoke test container before publish
    - pushes tags to Docker Hub (`sha`, `latest` on `main`, and git tags)

**Setup required:**
- GitHub Secrets: `DOCKER_USERNAME`, `DOCKER_PASSWORD` (Docker Hub access token)

For full workflow details, see [.github/workflows/README.md](.github/workflows/README.md).

### Full Stack Deployment

See [docker/README.md](docker/README.md) for:
- Environment file setup
- Starting all services (API, MongoDB, Qdrant, Redis, Prometheus, Grafana)
- Volume management
- Monitoring setup
- Troubleshooting

---

## Part IX: Quick Reference

| Task | Command |
|------|---------|
| **Local dev** | `uvicorn src.main:app --reload` |
| **Run tests** | `pytest -v` |
| **Build Docker image** | `docker build -f docker/api/Dockerfile -t recaply:local .` |
| **Full-stack with Docker** | `docker compose -f docker/docker-compose.yml up --build` |
| **View API docs** | http://localhost:5000/docs |
| **View Prometheus metrics** | http://localhost:9090 |
| **View Grafana dashboards** | http://localhost:3000 |

---

## Part X: Next Steps for Code Review / Evaluation

1. **Understand the architecture** → Read [src/README.md](src/README.md) § 2–5
2. **Review the upload pipeline** → See [src/README.md](src/README.md) § 7 (most complex flow)
3. **Understand retrieval** → See [src/README.md](src/README.md) § 7 and `src/services/chat/`
4. **Review tests** → See `tests/test_api.py`
5. **Check runtime and CI** → See [docker/README.md](docker/README.md) and [.github/workflows/README.md](.github/workflows/README.md)

---

## Links to Detailed Documentation

- **Backend Architecture**: [src/README.md](src/README.md)
- **Docker & Full Stack**: [docker/README.md](docker/README.md)
- **CI & Tests**: [.github/workflows/README.md](.github/workflows/README.md)
- **Project Requirements**: `requirements.txt`

---

**Status**: Production-ready backend with comprehensive testing, monitoring, and deployment automation.
