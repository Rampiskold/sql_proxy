# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI application named `proxy-sql-query`. The project uses Python 3.12+ and is managed with `uv` for dependency management.

## Development Commands

### Running the Application
```bash
uvicorn main:app --reload
```

The server runs on `http://127.0.0.1:8000` by default.

### Installing Dependencies
```bash
uv sync
```

### Activating Virtual Environment
```bash
source .venv/bin/activate
```

### Installing Development Dependencies
```bash
uv sync --extra dev
```

### Code Quality Checks

**CRITICAL**: After any code changes, run all linters:
```bash
isort . && ruff check --fix . && ruff format . && mypy .
```

Or individually:
```bash
isort .                    # Sort imports
ruff check --fix .         # Lint and auto-fix
ruff format .              # Format code
mypy .                     # Type checking
```

## Architecture

This is a single-file FastAPI application with the following structure:

- **main.py**: Contains the FastAPI application instance and all route handlers
- **pyproject.toml**: Project metadata and dependencies managed by uv
- **test_main.http**: HTTP client test file for manual API testing

The application currently has two endpoints:
- `GET /`: Returns a simple "Hello World" message
- `GET /hello/{name}`: Returns a personalized greeting

## Dependencies

Core dependencies:
- **fastapi**: Web framework
- **uvicorn**: ASGI server for running the application

Development tools:
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker
- **isort**: Import sorter

All dependencies are locked in `uv.lock`.

Code style configuration:
- Line length: 100 characters
- Python version: 3.12+
- Strict type checking enabled

## Project Rules

**See `claude.local.md` for detailed project-specific rules** including:
- Clean Architecture principles with clear separation of concerns
- Mandatory linter execution after each code change
- Coding standards and naming conventions
- Dependency injection patterns
- Testing requirements
