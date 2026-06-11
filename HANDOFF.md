# Handoff - NVIDIA NAT Integration Demo

## Objective

Build a public GitHub project that demonstrates integration capability across
the NVIDIA agent ecosystem:

```text
NVIDIA NIM -> NeMo Agent Toolkit (NAT) -> API backend -> official NVIDIA UI -> portfolio demo
```

The repo should not look like a copy of NVIDIA's toolkit. It should show clean
integration: workflow config, scripts, validation, documentation, deployment
thinking, and comparison with the existing `cv-critic-agent` CrewAI project.

## Architecture

- **NIM**: NVIDIA-hosted model endpoint used by the LLM provider.
- **NAT / NeMo Agent Toolkit**: workflow and agent orchestration framework.
- **NVIDIA NAT UI**: official external frontend, used as a demo client.
- **This repo**: integration layer, configuration, scripts, tests, docs, and
  deployment plan.

Implemented workflows:

- Config file: `config.yml`
- Workflow type: `chat_completion`
- Config file: `configs/react_climate.yml`
- Workflow type: `react_agent`
- Tools: `list_countries`, `calculate_statistics`, `filter_by_country`,
  `find_extreme_years`, `create_visualization`
- Config file: `configs/react_climate_phoenix.yml`
- Observability: Phoenix via NAT `_type: otelcollector`
- Model: `meta/llama-3.1-70b-instruct`
- Backend server: `nat serve --config_file config.yml --host 127.0.0.1 --port 8001`
- UI proxy: `http://localhost:3001`
- Phoenix UI: `http://localhost:6006`

## Current Local State

Validated locally:

- `nat validate --config_file config.yml`
- `nat validate --config_file configs/react_climate.yml`
- `nat validate --config_file configs/react_climate_phoenix.yml`
- `python -m pytest`
- `python -m ruff check .`
- `GET http://127.0.0.1:8001/health`
- `GET http://localhost:3001`
- `POST http://localhost:3001/api/chat`

The official UI was cloned locally under `external/nat-ui`, but `external/` is
intentionally ignored by Git. Recreate it with:

```bash
scripts/bootstrap_ui.sh
```

Pinned UI commit:

```text
e5d91c68b913287cbcc4d4689a956a7b3b36333e
```

## Critical Notes

- Do not commit `.env`, `.venv/`, `.idea/`, or `external/nat-ui/`.
- Do not create a fake `ui_manager` module. The course snippet appears to be a
  lab helper, not part of local `nvidia-nat`.
- Do not vendor-copy the NVIDIA UI into this repo unless intentionally creating
  a maintained fork.
- `nvidia-nat[app]` installs `nat_app`, which is Agent Performance Primitives,
  not the chat UI.
- On this machine, port `8000` was already busy, so backend uses `8001`.
- On this machine, port `3000` was already busy, so UI uses `3001`.
- The UI public proxy accepts `/api/chat`; direct `/api/v1/chat/completions` is
  blocked by the UI allowlist.
- NAT 1.7.0 in this venv does not register a tracing component named `phoenix`.
  Use `configs/react_climate_phoenix.yml`, which exports to Phoenix through
  `_type: otelcollector` and endpoint `http://localhost:6006/v1/traces`.
- `arize-phoenix==17.2.0` provides the local `phoenix serve` command.
- `scripts/serve_phoenix.sh` sets `PHOENIX_ALLOWED_SANDBOX_PROVIDERS=NONE` by
  default to avoid slow WASM sandbox prefetch during local demo startup.
- The workshop cleanup calls `ui_manager.stop()`, `nat_process.terminate()`,
  and `nat_process.wait()`. Local equivalent is currently manual `Ctrl+C` in
  backend/UI terminals. Add `scripts/start_demo.sh` and `scripts/stop_demo.sh`
  later for PID-based startup and cleanup.

## SSL Note

Python 3.13 on macOS hit:

```text
CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate
```

Root cause: Python's OpenSSL CA bundle path was not initialized. Correct fix:

```bash
"/Applications/Python 3.13/Install Certificates.command"
```

Do not disable SSL verification.

## GitHub Positioning

Recommended positioning:

```text
NVIDIA agent integration demo
```

Suggested narrative:

```text
Same agentic integration goal, different ecosystems:
CrewAI in cv-critic-agent, NVIDIA NAT/NIM in this project.
```

This project should emphasize:

- reproducible local setup
- official NVIDIA UI integration
- OpenAI-compatible API surface
- deployment plan
- technical tradeoffs and troubleshooting

## Deployment Direction

Preferred public demo:

- hosted demo + video fallback
- backend NAT on Render/Railway/Fly
- NVIDIA UI as Docker service on Render/Railway/Fly
- portfolio page on Vercel linking to both the demo and video

Backend command:

```bash
nat serve --config_file config.yml --host 0.0.0.0 --port "$PORT"
```

Backend env:

```bash
NVIDIA_API_KEY=...
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```

UI env:

```bash
NAT_BACKEND_URL=https://<deployed-backend-url>
PORT=3000
NEXT_INTERNAL_URL=http://127.0.0.1:3099
```

## Demo Run Order

Terminal 1:

```bash
scripts/serve_phoenix.sh
```

Terminal 2:

```bash
NAT_CONFIG_FILE=configs/react_climate_phoenix.yml scripts/serve_react_backend.sh
```

Terminal 3:

```bash
scripts/serve_ui.sh
```

Ask in the UI:

```text
Compare the temperature trends of Canada and Brazil. Which one is warming faster?
Also create a visualization of global trends.
```

## Next Work

1. Continue the NVIDIA NAT course with the multi-agent lesson:
   "Multi-agent integration: adding math".
2. Add a real LangGraph calculator agent and expose it as a NAT tool.
3. Add Docker Compose as a demo packaging layer after the local workflow is
   stable.
4. Add architecture diagram and screenshots/video.
5. Add `scripts/start_demo.sh` and `scripts/stop_demo.sh` for reliable cleanup.
6. Add deployment docs for Render/Railway/Fly.
7. Connect the final demo page from `cv-portfolio`.

## Planned Feature - LangGraph Calculator Agent

The next strong demo feature is to integrate a LangGraph calculator agent as a
tool inside the NAT climate ReAct workflow.

Target architecture:

```text
Climate ReAct agent
  -> climate data tools
  -> calculator_agent
       -> LangGraph calculator sub-agent
  -> final answer
```

Why this matters:

- Shows multi-agent integration, not only simple Python tools.
- Demonstrates that NAT can orchestrate an agent implemented in another
  framework.
- Makes Phoenix traces more interesting: top-level ReAct agent, climate tool
  calls, nested calculator agent calls, and final synthesis.

Implementation direction:

```text
src/training_nvidia_nat/calculator_agent.py
src/training_nvidia_nat/register.py
configs/react_climate_math.yml
configs/react_climate_phoenix_math.yml
tests/test_calculator_agent.py
docs/nat-multi-agent-langgraph-lesson.md
```

Important design choice:

- Do not copy course helper code.
- Build a small local LangGraph calculator agent.
- Wrap it with `@register_function(..., framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])`.
- Get its LLM from NAT YAML via `builder.get_llm(...)`; do not hardcode the
  model in the LangGraph module.

Good demo prompt:

```text
For India, use the observed temperature trend per decade to project the average
temperature in 2050. Explain the calculation.
```

Expected flow:

1. Climate ReAct calls `calculate_statistics(country="India")`.
2. Climate ReAct sends the trend/year math to `calculator_agent`.
3. LangGraph calculator returns the projection.
4. Climate ReAct writes the final answer.
5. Phoenix shows the nested execution.

## Planned Feature - Docker Compose Demo

Docker is useful as a demo packaging layer, not as the primary learning/dev
loop.

Target services:

```text
docker compose
  nat-backend   -> nat serve with configs/react_climate_phoenix.yml
  phoenix       -> Phoenix UI and OTLP endpoint
  nat-ui        -> official NVIDIA NAT UI connected to backend
```

Positioning:

```text
Local venv = learning/debug/fast iteration
Docker Compose = reproducible GitHub/portfolio demo
```

Critical constraints:

- Still requires `NVIDIA_API_KEY`.
- Do not vendor-copy the NVIDIA UI into this repo.
- Use volumes for Phoenix state.
- Keep `.env` local and untracked.

Completed after initial handoff:

- GitHub Actions CI added in `.github/workflows/ci.yml`.
- Portfolio-facing technical sheet added in `TECHNICAL_SHEET.md`.
- NAT ReAct tools lesson consolidated in `docs/nat-react-tools-lesson.md`.
- NAT ReAct climate tools implemented and validated.
- Phoenix observability config implemented through OTLP collector export.
