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

Current workflow:

- Config file: `config.yml`
- Workflow type: `chat_completion`
- Model: `meta/llama-3.1-70b-instruct`
- Backend server: `nat serve --config_file config.yml --host 127.0.0.1 --port 8001`
- UI proxy: `http://localhost:3001`

## Current Local State

Validated locally:

- `nat validate --config_file config.yml`
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

## Next Work

1. Add GitHub Actions for NAT validation, tests, lint, and shell syntax.
2. Create `TECHNICAL_SHEET.md` as a polished portfolio-facing document.
3. Add architecture diagram and screenshots/video.
4. Add deployment docs for Render/Railway/Fly.
5. Connect the final demo page from `cv-portfolio`.

