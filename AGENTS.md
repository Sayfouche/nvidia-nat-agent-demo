# Repository Guidelines

## Project Structure & Module Organization

This repository is a NVIDIA NeMo Agent Toolkit (NAT) integration demo.

- `config.yml`: baseline `chat_completion` NAT workflow.
- `configs/`: ReAct and Phoenix-enabled workflow configs.
- `src/training_nvidia_nat/`: Python package code.
- `src/training_nvidia_nat/climate.py`: pure climate data functions.
- `src/training_nvidia_nat/register.py`: NAT tool registration entry point.
- `src/training_nvidia_nat/data/`: bundled demo CSV data.
- `tests/`: pytest unit tests.
- `scripts/`: local run, serve, UI, Phoenix, and validation helpers.
- `docs/`, `HANDOFF.md`, `TECHNICAL_NOTES.md`: implementation notes and handoff context.

Do not commit `.env`, `.venv/`, `.idea/`, `external/`, or generated `artifacts/`.

## Build, Test, and Development Commands

Set up locally:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e . --no-build-isolation
```

Validate everything:

```bash
scripts/validate_local.sh
```

Run workflows:

```bash
scripts/run_climate_workflow.sh --input "What is the greenhouse effect?"
scripts/run_react_demo.sh "List the countries available in the climate dataset."
scripts/serve_react_backend.sh
scripts/serve_phoenix.sh
scripts/serve_ui.sh
```

## Coding Style & Naming Conventions

Use Python 3.13, 4-space indentation, type hints for public functions, and small pure functions where possible. Keep NAT wrappers thin; business logic belongs in modules like `climate.py`.

Ruff is the active lint tool:

```bash
python -m ruff check .
```

Use descriptive NAT names matching YAML keys, for example `calculate_statistics`, `filter_by_country`, and `create_visualization`.

## Testing Guidelines

Tests use `pytest`. Name files `tests/test_*.py` and test pure functions without requiring NVIDIA API access. Add tests for edge cases that LLMs may generate, such as empty strings, `"None"`, and unknown countries.

Run:

```bash
python -m pytest
```

## Commit & Pull Request Guidelines

Commit history uses short imperative messages, for example:

- `Add ReAct climate tools and Phoenix tracing demo`
- `Document next NAT integration steps`

Keep commits feature-scoped. For PRs, include a concise summary, validation output, affected configs/scripts, and screenshots or trace notes when UI or Phoenix behavior changes.

## Security & Configuration Tips

Keep secrets in `.env` only:

```bash
NVIDIA_API_KEY=...
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```

Do not disable SSL verification. If macOS Python certificate issues appear, fix the local certificate bundle or use `SSL_CERT_FILE` with `certifi`.

Phoenix uses OTLP through `_type: otelcollector`; this local NAT version does not register `_type: phoenix`.
