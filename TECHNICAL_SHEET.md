# NVIDIA NAT Integration Demo - Technical Sheet

## Purpose

This project demonstrates an end-to-end integration of an agent workflow using
the NVIDIA AI ecosystem:

```text
NVIDIA NIM -> NeMo Agent Toolkit (NAT) -> NAT API server -> official NVIDIA UI
```

The goal is not to reimplement NVIDIA tooling. The goal is to show how an
integrator can assemble NVIDIA components into a working, reproducible agent
demo with a backend API, official UI client, validation scripts, and a clear
deployment path.

## Architecture

| Layer | Component | Role |
| --- | --- | --- |
| Model endpoint | NVIDIA NIM | Hosted LLM provider through NVIDIA API |
| Orchestration | NeMo Agent Toolkit / NAT | Defines and serves the agent workflow |
| Workflow config | `config.yml` | Declares the climate assistant and NIM model |
| Backend API | `nat serve` | Exposes health, chat, generate, and OpenAI-compatible routes |
| UI client | NVIDIA NeMo Agent Toolkit UI | Official chat UI connected to the NAT backend |

Current local ports:

```text
Backend NAT: http://127.0.0.1:8001
UI gateway:  http://localhost:3001
```

The UI is intentionally not vendored in this repo. It is fetched from NVIDIA's
official repository with `scripts/bootstrap_ui.sh`.

## Workflow

The current workflow is a climate science assistant:

- NAT workflow type: `chat_completion`
- LLM type: `nim`
- Model: `meta/llama-3.1-70b-instruct`
- Backend URL: `https://integrate.api.nvidia.com/v1`

Planned next workflow:

- NAT workflow type: `react_agent`
- Tools: climate statistics, country filtering, extreme-year lookup, and
  visualization
- Config file target: `configs/react_climate.yml`
- Lesson notes: `docs/nat-react-tools-lesson.md`

Required local environment:

```bash
NVIDIA_API_KEY=...
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```

## Local Runbook

Install Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Configure secrets:

```bash
cp .env.example .env
```

Validate the backend workflow:

```bash
scripts/validate_local.sh
```

Run the backend:

```bash
scripts/serve_backend.sh
```

Install the official NVIDIA UI:

```bash
scripts/bootstrap_ui.sh
```

Run the UI:

```bash
scripts/serve_ui.sh
```

Open:

```text
http://localhost:3001
```

## Integration Notes

- The course helper `ui_manager` is not part of the local `nvidia-nat` package.
- The official UI is a separate NVIDIA frontend project.
- The UI gateway uses `/api/chat` and proxies to the NAT backend.
- Direct `/api/v1/chat/completions` through the UI proxy is blocked by the UI
  allowlist; direct OpenAI-compatible calls should target the NAT backend.
- `nvidia-nat[app]` provides `nat_app` performance primitives, not the chat UI.
- Custom NAT tools require Python package entry points so NAT can discover local
  registrations.
- ReAct tools should be implemented as pure tested functions plus thin NAT
  wrappers.

## Quality Gates

Local validation:

```bash
nat validate --config_file config.yml
python -m pytest
python -m ruff check .
bash -n scripts/*.sh
```

CI validation:

- installs Python dependencies
- validates NAT config with dummy NVIDIA env vars
- runs tests and Ruff
- checks shell script syntax
- verifies secrets/vendor folders are not tracked

## Deployment Direction

Recommended public demo:

- Backend NAT on Render, Railway, or Fly.io
- NVIDIA UI deployed as a Docker service
- Portfolio page on Vercel linking to the demo
- Short video fallback for cases where API cost or availability limits the live
  demo

Backend command:

```bash
nat serve --config_file config.yml --host 0.0.0.0 --port "$PORT"
```

UI runtime env:

```bash
NAT_BACKEND_URL=https://<deployed-nat-backend>
PORT=3000
NEXT_INTERNAL_URL=http://127.0.0.1:3099
```

## Portfolio Positioning

This project complements `cv-critic-agent`.

`cv-critic-agent` shows a custom/CrewAI implementation of an agent workflow.
This project shows the same integration mindset using NVIDIA NAT, NIM, and the
official NVIDIA UI.

Recommended narrative:

```text
Same agentic integration goal, different ecosystems:
CrewAI for a custom CV audit workflow, NVIDIA NAT/NIM for an enterprise AI
integration stack.
```
