# LLM Gateway

![GitHub License](https://img.shields.io/github/license/yourusername/LLM-Gateway)
![Docker Pulls](https://img.shields.io/docker/pulls/yourdockerhub/llm-gateway)

## Overview

**LLM Gateway** is a lightweight FastAPI‑based service that acts as a gateway for Large Language Model (LLM) providers. It demonstrates how to build a production‑ready API layer with:

- **Rate limiting** (per‑client and per‑endpoint)
- **Health‑check** and **admin** routes
- **Dockerised** deployment for easy scaling
- **Local development** using the modern UV package manager

The project was created as a learning exercise, but the structure follows best practices and can be extended for real‑world workloads.

## Features

- **FastAPI** with automatic OpenAPI/Swagger docs
- **Async context manager** for database and cache initialisation
- **Configurable via `.env`** (see [.env_example](.env_example))
- **Docker Compose** support for containerised deployment
- **Rate Limiter** implementation under `services/rateLimiter.py`
- **Modular routers** (`controller/chat.py`, `controller/admin.py`)
- **SQLite database** for persisting metrics (`metrics.db`)

## Prerequisites

| Tool | Version |
|------|---------|
| Docker & Docker‑Compose | >= 20.10 |
| UV (optional) | >= 0.4 |
| Python | >= 3.10 |

If you prefer not to use Docker, the project can be run directly with Python/UV.

## Quick Start

### Using Docker Compose

```bash
# Build and start the service
docker compose up --build
```

Run in detached mode:

```bash
docker compose up -d --build
```

Stop the service:

```bash
docker compose down
```

### Local Development (without Docker)

```bash
# Install dependencies via UV (recommended)
uv sync

# Run the development server
uv run uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Root welcome message |
| `GET` | `/health` | Liveness probe |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc UI |
| `POST` | `/chat` | Interaction with the LLM (see `controller/chat.py`) |
| `GET/POST/...` | `/admin/*` | Administration utilities (see `controller/admin.py`) |

## Environment Variables

Create a `.env` file based on the provided [.env_example](.env_example). Typical variables include:

```env
# Example configuration
LOG_LEVEL=INFO
RATE_LIMIT=100  # requests per minute per client
DB_PATH=metrics.db
```

## Testing

Run the test suite with:

```bash
pytest tests
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests. Follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feat/awesome-feature`).
3. Install development dependencies (`uv sync --dev`).
4. Add tests for new functionality.
5. Ensure all tests pass (`pytest`).
6. Open a Pull Request against the `main` branch.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

*Built as a learning project – enjoy exploring and extending it!*
