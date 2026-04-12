
# Recaply `src` Architecture

This document explains the `src` package only.
It is written for technical documentation, code review, and project evaluation.
The goal is to describe how the backend is structured, how data flows through the system, and what each layer is responsible for.



## 1. What `src` Contains

`src` is the FastAPI backend for Recaply, an AI system for meeting ingestion, transcript normalization, structured meeting analysis, and retrieval-augmented chat.

The package handles:

- file upload and validation
- storage of raw files
- normalization of audio, subtitle, text, and PDF inputs
- chunking and embedding of normalized content
- vector database indexing
- structured meeting report generation through LLM chains
- RAG chat over project files
- persistence of project and file metadata in MongoDB
- chat memory in Redis
- observability through logs, metrics, and LangSmith tracing

## 2. High-Level Architecture

The code follows a layered architecture:

```text
FastAPI Router
  -> Orchestrator
    -> Service
      -> Repository / Integration
        -> External System
```

### Why this structure matters

- Routers stay thin and only handle HTTP boundaries.
- Orchestrators combine multiple services into one workflow.
- Services implement reusable business logic.
- Repositories isolate MongoDB access.
- Integrations wrap third-party systems like LLMs, Redis, Whisper, and the vector database.

This separation makes the system easier to maintain, test, and evaluate in a review setting.

## 3. Main Runtime Entry Point

The application starts in [main.py](main.py).

At startup, the lifespan handler initializes the core dependencies:

- MongoDB client
- Vector DB client
- embedding client
- Redis client
- LangChain OpenAI-compatible client
- Chains service
- Chat service
- Whisper provider

It also configures:

- LangSmith tracing through environment variables
- Prometheus metrics through `setup_metrics(app)`
- FastAPI exception handling

### Startup role

Startup is where infrastructure dependencies are wired together.
This is important because the app is not a simple stateless API; it is a composed AI backend that depends on multiple connected systems.

## 4. Source Folder Structure

### `core/`
Application foundation:

- settings and environment configuration
- dependency helpers
- shared exception handling

### `helpers/`
Utility and cross-cutting services:

- logging
- metrics
- ffmpeg helpers
- disk/path helpers
- enums

### `integrations/`
Adapters to external systems:

- LLM provider abstractions
- vector DB provider abstractions
- Redis provider
- Whisper provider

### `models/`
Internal domain models:

- `Segment`
- `FileModel`
- `ProjectModel`
- chunk-related metadata models

### `repos/`
MongoDB persistence layer:

- file repository
- project repository
- repository exceptions

### `routers/`
API endpoints exposed by FastAPI.

### `schemas/`
Request and response schemas used at the API boundary.

### `services/`
Business logic and processing pipelines:

- file ingestion helpers
- normalizers
- chunking
- chains
- chat
- project services

### `orchestrators/`
Workflow coordinators that connect routers to services.

### `storage/`
Runtime file storage for uploaded artifacts and generated content.

## 5. Layer Responsibilities

## 5.1 Routers

Routers define the HTTP surface area.
They do not perform heavy business logic.
Instead, they validate inputs, inject dependencies, and delegate work to orchestrators.

Key router files:

- [routers/workspace_router.py](routers/workspace_router.py)
- [routers/files_router.py](routers/files_router.py)
- [routers/projects_router.py](routers/projects_router.py)
- [routers/vectordb_router.py](routers/vectordb_router.py)
- [routers/home_router.py](routers/home_router.py)

### Router design characteristics

- request/response focused
- dependency-injection friendly
- clear route grouping by domain
- small controller surface with thin implementations

## 5.2 Orchestrators

Orchestrators glue together multiple services into one business flow.
They are the coordination layer between HTTP and the internal system.

Key orchestrators:

- `UploadOrchestrator`
- `ChainsOrchestrator`
- `ChatOrchestrator`

### Why orchestrators exist

Some application operations require multiple steps and multiple services.
For example, file upload requires detection, validation, storage, normalization, chunking, and vector indexing.
Placing that sequence in one orchestrator keeps the router clean and avoids spreading workflow logic across many services.

## 5.3 Services

Services contain the actual application logic.
They are the core of the backend design.

Important service groups:

- `services/files/`: detection, validation, storage
- `services/normalizers/`: conversion of raw files into segments
- `services/chunking/`: segment grouping and embedding prep
- `services/chains/`: structured LLM pipelines
- `services/chat/`: RAG retrieval and answer generation
- `services/project_service/`: project-level lifecycle operations
- `services/vdb_service/`: vector database access and utilities

### Service design characteristics

- single responsibility
- reusable across orchestrators
- independent of HTTP concerns
- easier to test than router-level logic

## 5.4 Repositories

Repositories isolate persistence concerns.
They are responsible for MongoDB reads and writes related to files and projects.

This keeps data access separate from business logic and makes persistence easier to replace or refactor.

## 5.5 Integrations

Integrations wrap external infrastructure:

- LLM providers
- vector DB providers
- Redis provider
- Whisper provider

This layer prevents the rest of the application from depending directly on vendor-specific code.
That is a strong abstraction choice for an AI backend.

## 5.6 Schemas and Models

### Schemas

Schemas define API contracts and structured outputs.
They are used at request/response boundaries and also for LLM parsing contracts.

### Models

Models define the internal domain structure.
`Segment` is the most important shared model because it becomes the common unit across normalization, chunking, chains, and chat.

## 6. Core Data Flow

There are three main flows in the system.

1. upload and ingestion
2. structured meeting analysis
3. retrieval-augmented chat

These flows share the same underlying project and file data.

## 7. Upload and Ingestion Flow

This is the most important pipeline in the backend.
It converts raw user files into searchable and structured meeting content.

```text
Upload request
  -> detect file type
  -> validate file
  -> save raw file
  -> normalize into segments
  -> store file metadata
  -> chunk normalized content
  -> embed chunks
  -> store chunks in vector DB
```

### Step 1: Request enters the workspace router

The upload endpoint lives in [routers/workspace_router.py](routers/workspace_router.py).

Route:

- `POST /api/v1/workspace/{project_id}/upload`

The router passes the request to `UploadOrchestrator.execute_batch()`.

### Step 2: Project context is prepared

`UploadOrchestrator.execute_batch()`:

- checks whether the project already exists
- deletes the old project when the workflow requires replacement
- creates the vector DB collection name
- loads or creates the project record

This means upload is project-scoped, not file-scoped.

### Step 3: File detection and validation

For each uploaded file:

- `FileDetectorService.detect()` determines the logical file type
- `FileValidatorService.validate()` checks size and emptiness constraints
- `FileStorageService.generate_file_path()` creates the project file path
- `FileStorageService.save_file()` writes the file to disk

Supported file types:

- audio
- txt
- pdf
- srt
- vtt

### Step 4: Normalization

`NormalizerFactory` selects one of the normalizers based on file type.

#### Audio

`AudioNormalizer`:

- preprocesses audio
- transcribes with Whisper
- creates `Segment` objects
- merges small segments

#### Text and PDF

`TextNormalizer`:

- reads plain text with encoding fallback
- extracts PDF text with `PyPDF2`
- splits text into fixed-size segments
- merges small segments

#### Subtitles

`SubtitleNormalizer`:

- parses SRT with `pysrt`
- parses VTT with `webvtt`
- converts timestamps into segment ranges
- merges small segments

### Output of normalization

All normalizers produce the same internal abstraction:

- a list of `Segment` objects

Each segment contains:

- text
- start time
- end time
- speakers when available

This shared abstraction is what makes the rest of the pipeline uniform.

### Step 5: File metadata persistence

The orchestrator creates a `FileModel` and stores it through `FileRepo`.
This record keeps both the raw file identity and the normalized content.

### Step 6: Chunking

`ChunkingService.process_file_chunks()` decides which chunking strategy to use.

#### Merge chunking

Used when speaker information exists.
It preserves the conversational flow better.

#### Semantic chunking

Used when speaker information is absent.
It compares embeddings and merges adjacent segments by semantic similarity.

### Step 7: Embedding and chunk metadata

`ChunkingService.embed()` prepares chunks for retrieval storage.
Each chunk gets:

- text
- embedding vector
- metadata
- order information
- timestamp information

### Step 8: Vector DB storage

After chunking, the system:

- prepares BM25 support
- stores vectors in the vector DB
- stores metadata alongside embeddings

This provides hybrid retrieval behavior:

- semantic search
- keyword-oriented search support

## 8. Structured Meeting Report Flow

This flow generates meeting intelligence from normalized project content.

Route:

- `GET /api/v1/workspace/{project_id}/chains/{session_id}/{user_id}`

### Flow

```text
Project files
  -> collect segments
  -> run chains service
  -> generate structured outputs
  -> enrich returned segments
```

### Orchestration

`ChainsOrchestrator.execute()`:

- loads the project
- loads all files for that project
- extracts all normalized segments
- validates that segment data exists
- invokes `ChainsService.run()`
- enriches selected output segments with file metadata

### Chain execution

`ChainsService.run()` builds and executes the chain pipeline.
It also sends LangSmith metadata including:

- tenant id
- project id
- user id
- session id
- segment count
- generation model id

### Chain outputs

The chain layer returns structured entities such as:

- context
- decisions
- tasks
- conflicts
- risks
- summary
- sentiment

Each chain has:

- a dedicated prompt template
- a Pydantic output schema
- JSON-constrained parsing logic

### Review significance

This is a strong design pattern because the system is not relying on raw free-text LLM outputs.
It uses schema-driven extraction, which is more reliable and easier to reason about in a production evaluation.

## 9. Chat and RAG Flow

This flow answers questions using retrieved project documents.

Route:

- `POST /api/v1/workspace/{project_id}/chat/{session_id}/{user_id}`

### Flow

```text
User question
  -> load session history
  -> rewrite query
  -> retrieve docs
  -> rerank docs
  -> generate grounded answer
  -> store conversation memory
```

### Chat orchestration

`ChatOrchestrator.execute()`:

- loads the project
- fetches associated files
- delegates to `ChatService.run()`

### Chat service responsibilities

`ChatService.run()`:

- loads history from Redis
- trims history to a bounded window
- configures LangSmith run metadata
- builds the retrieval/generation pipeline
- writes back to memory after generating a response

### Retrieval layer

`Retrieval` performs hybrid retrieval:

- query embedding
- vector search
- keyword search
- reciprocal rank fusion
- deduplication

### Reranking layer

A reranker reduces the retrieved set to the most relevant documents.
This keeps the generation prompt smaller and more focused.

### Generation layer

`services/chat/generation.py`:

- formats retrieved docs into context
- injects chat history
- requests a grounded JSON response
- parses the answer
- maps citations back to source metadata

### Review significance

This design supports grounded answering instead of open-ended generation.
That is important for an AI engineering evaluation because it shows control over hallucination risk.

## 10. Observability and Runtime Quality

The backend includes several observability signals:

- logging through `helpers/logger.py`
- Prometheus metrics through `helpers/metrics.py`
- LangSmith tracing through environment configuration

This is important because the system depends on multiple AI and infrastructure components.
When something fails, visibility matters.

## 11. Design Strengths

The codebase has several strong points:

- clean separation of concerns
- clear workflow orchestration
- shared `Segment` abstraction across the pipeline
- hybrid retrieval strategy
- schema-driven LLM outputs
- project-scoped data organization
- Redis-backed session memory
- observability support

## 12. Tradeoffs and Review Considerations

These are the main things worth discussing in a review or interview:

- the system depends on several external services, so availability is not purely local to the API
- some workflows are long-running and may create request latency
- LLM prompt quality still affects extraction reliability even with schema validation
- vector search quality depends on embeddings, BM25, and reranking quality together
- project re-upload behavior should be reviewed carefully because it can replace previous content

## 13. Configuration Notes

The main runtime variables are documented in [src/.env.example](.env.example).

The configuration covers:

- app metadata
- MongoDB
- Redis
- OpenAI-compatible LLM access
- LangSmith tracing
- embedding settings
- chunking thresholds
- upload size limits
- vector DB backend selection


