# PC Builder Platform

A full-stack PC configuration platform that helps users build optimized computer setups based on budget, performance goals, and component compatibility.

The system combines a structured hardware database, rule-based scoring engine, and AI-assisted recommendations to generate balanced PC builds for different use cases such as esports gaming, AAA gaming, office workloads, and general-purpose systems.

---

## Key Features

- Smart PC build generator based on budget and goal type
- Component compatibility validation (CPU, motherboard, RAM, GPU, etc.)
- Rule-based scoring system for hardware ranking and selection
- Manual PC builder with editable configurations
- Scraping pipeline for hardware data collection (Celery-based workers)
- REST API with authentication (JWT)
- Extensible architecture prepared for AI-assisted recommendations

---

## Build Goals

- **Office** — efficient and low-cost systems for everyday tasks
- **CyberSport** — optimized for high FPS competitive gaming
- **Balanced** — general-purpose performance setups
- **AAA** — high-end gaming builds focused on graphics quality

---

## Tech Stack

**Backend**
- FastAPI
- SQLAlchemy
- PostgreSQL
- Celery
- Redis

**Frontend**
- React
- TypeScript
- TailwindCSS

**Infrastructure**
- Docker
- Docker Compose

**AI Integration**
- OpenAI-compatible API layer (optional extension)