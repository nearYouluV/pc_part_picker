# CHAPTER 3. IMPLEMENTATION OF THE ALGORITHM

## 3.1 System Architecture Overview
- The backend is a FastAPI app (`backend/app/main.py`) exposing REST endpoints and lifecycle hooks.
- Background processing uses Celery with broker/backend configured in `backend/app/celery_app.py`.
- Persistent storage is PostgreSQL accessed via sync and async SQLAlchemy engines in `backend/app/database.py`.
- Key modules: API routers (`backend/app/api/*`), models (`backend/app/models/*`), services (`backend/app/services/*`), tasks (`backend/app/tasks/*`), utilities (`backend/app/utils/*`).

## 3.2 Software Implementation

### 3.2.1 Core modules
- `main.py`: application entry, lifespan, router registration, CORS configuration.
- Models: `Product`, `CPU`, `GPU`, `Motherboard`, `RAM`, `PSU`, `StorageSpec`, `CoolingSpec`, `PCBuild`, `BuildComponent`, `User`, `Chats`, `ChatMessage` (`backend/app/models/`).
- Services: `BuilderService`, `DatabaseService`, `ChatService`, `auth_service`, `brute_force_protection` (`backend/app/services/`).
- Tasks: `generate_ai_build_task`, `process_ai_chat_message_task`, `scrape_category_task` (`backend/app/tasks/`).
- Utilities: `scoring_engine.py` (scoring & compatibility), `parse_utils.AIParser` (LLM client), logging config.

### 3.2.2 Data processing pipeline
- Scraping: `tasks/scraping_tasks.py` fetches marketplace data, coerces types and calls `DatabaseService.upsert_product_with_spec` to persist.
- Query & ranking: APIs (e.g., `api/builder.py`) load products with `joinedload` and call `scoring_engine.rank_category_products`.
- AI flow: `tasks/ai_tasks.py` builds candidate maps, calls `AIParser.call_ai`, parses response and updates builds via `BuilderService`.
- PLACEHOLDER: Add sequence diagram and example data flow traces.

### 3.2.3 Network communication layer
- HTTP REST: routers in `backend/app/api/*` mounted under `/api` (`/api/auth`, `/api/builder`, `/api/ai`, `/api/product`, `/api/scraping`).
- Authentication: JWT tokens and `services/auth_service.py` dependency `get_current_active_user` protect endpoints.
- Async work: endpoints dispatch Celery tasks (`.delay()`), Celery communicates via configured broker (env `CELERY_BROKER_URL`).
- AI client: `utils/parse_utils.AIParser` uses an OpenAI-compatible HTTP client to call external LLM endpoints.

### 3.2.4 Concurrency model
- FastAPI async endpoints use `AsyncSessionLocal` from `database.py` for non-blocking DB access.
- Celery workers execute expensive tasks; tasks may run asyncio loops internally via `_run_async`.
- Mix of sync and async DB usage maintained for Celery compatibility; connection pooling configured in `database.py`.
- PLACEHOLDER: Document worker counts, concurrency settings and event loop policy used in deployments.

## 3.3 Algorithm Implementation
- Main algorithm: component scoring & ranking implemented in `backend/app/utils/scoring_engine.py` (`score_component`, `rank_category_products`).
- Supporting algorithms: candidate selection and distribution in `backend/app/tasks/ai_tasks.py` (CPU vendor buckets, motherboard distribution, storage selection).
- High-level flow: build context → extract candidate specs → score each candidate → compatibility checks → filter/sort → top-N recommendations.
- Pseudocode placeholder:
  - Input: build, candidates, budget, goal
  - For each candidate: compute `score = price_fit + performance + category_heuristics`
  - Apply compatibility rules from `evaluate_component_compatibility`
  - Return sorted top-N by `(in_budget, compatible, score)`
- PLACEHOLDER: Insert formal pseudocode and complexity analysis here.

## 3.4 System Deployment and Environment
- Runtime: Python backend (async+sync SQLAlchemy), Celery workers, Redis as broker (typical), PostgreSQL database; Docker manifests available (`Dockerfile`, `docker-compose.yml`).
- Dependencies: see `backend/requirements.txt` and `frontend/package.json` (bindings: SQLAlchemy, asyncpg, Celery, passlib, jose, openai client, etc.).
- Environment variables: `DATABASE_URL`, `CELERY_BROKER_URL`, `SECRET_KEY`, `VENICE_API_KEY` used across modules.
- PLACEHOLDER: Add precise Python version, Docker base images, and exact dependency versions.

## 3.5 Testing and Validation
- Test artifacts: `test_async.py` (root) suggests async test utilities exist.
- Validation in code: unit-like functions in `scoring_engine`, integration via `DatabaseService` upserts, Celery task status endpoints for observing background job results.
- Recommended tests: unit tests for `score_component`, integration tests for `BuilderService` with test DB, end-to-end Celery task tests.
- PLACEHOLDER: Add CI config and concrete test cases with expected assertions.

## 3.6 Scalability and Optimization Considerations
- Identified bottlenecks: full-catalog loads (`_load_all_products` in `tasks/ai_tasks.py`) and in-process scoring (`rank_category_products`) are O(N) and CPU-bound.
- Other concerns: blocking sync DB usage in Celery, external LLM latency, and joinloads producing heavy queries.
- Possible improvements: incremental/paginated candidate loading, caching ranked results in Redis, parallelized scoring, precomputed features/embeddings, and more efficient DB indices.
- PLACEHOLDER: Add benchmarking plan and targeted optimization roadmap.

## 3.7 Results of Execution
- Placeholder for artifacts: attach screenshots, logs, and benchmark tables from sample runs of `generate_ai_build_task` and `api/builder` endpoints.
- Expected outputs: Celery task JSON result structure, `BuildDetailResponse` from `api/builder` with `selected_components`, `total_price`, and `compatibility_warnings`.
- PLACEHOLDER: Insert sample outputs, task timings, and memory/CPU profiles.


---

PLACEHOLDERS TO FILL BEFORE FINAL THESIS:
- Concrete benchmarks and tables
- Formal pseudocode and complexity proofs
- Deployment exact versions and `requirements.txt` pins
- Test suite and CI configuration
- Diagrams (sequence, component, data flow)

