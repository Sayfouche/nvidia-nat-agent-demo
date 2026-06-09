# NAT Phoenix Observability Lesson

## Why This Lesson Matters

Phoenix observability adds the next integration layer after ReAct tools:

```text
baseline chat -> ReAct tools -> Phoenix tracing -> performance analysis
```

The goal is to move from:

```text
The agent answered.
```

to:

```text
We can inspect how the agent answered: LLM calls, tool calls, latency, errors,
and nested workflow steps.
```

## Observability Concept

NAT adds tracing around workflow execution:

```text
Input -> Function -> Output
             |
          Tracer -> Telemetry -> Exporter
```

The tracer captures runtime events, then an exporter sends them to an
observability backend such as Phoenix.

Potential trace events:

- workflow start/end
- LLM call start/end
- tool call start/end
- retriever call
- memory access
- nested function calls
- errors
- latency
- usage metrics, when available

## Unified NAT Observation

NAT observability is useful because it can follow nested workflows, not just the
top-level request:

```text
Workflow
  Function
    LLM
  Function
    Tool
      Retriever
      LLM
```

This is important for ReAct agents because a single user question may trigger
multiple reasoning cycles and tool calls.

## Phoenix Configuration

Workshop YAML pattern seen in the course:

```yaml
general:
  telemetry:
    tracing:
      phoenix:
        _type: phoenix
        endpoint: http://localhost:6006/v1/traces
project: climate_analyzer_baseline
```

Important local difference:

In this repo's current environment, `nvidia-nat==1.7.0` plus
`nvidia-nat-opentelemetry==1.7.0` does not register a NAT tracing component
named `phoenix`.

Verified command:

```bash
nat info components --types tracing --query phoenix --num_results 20
```

Result: no `phoenix` tracing component.

The working local config uses NAT's OpenTelemetry collector exporter and points
it to Phoenix's OTLP HTTP ingestion endpoint:

```yaml
general:
  telemetry:
    tracing:
      phoenix_local:
        _type: otelcollector
        endpoint: http://localhost:6006/v1/traces
        project: training_nvidia_nat_react_climate
```

Interpretation:

- `general.telemetry.tracing` configures NAT tracing globally.
- `_type: otelcollector` selects NAT's OTLP exporter.
- `endpoint` points to the Phoenix trace ingestion endpoint.
- `project` groups traces in Phoenix.

## Integration Impact For This Repo

Implemented config files:

```text
configs/react_climate.yml
configs/react_climate_phoenix.yml
```

or one config with Phoenix enabled when Phoenix is running.

Recommended project names:

```text
training_nvidia_nat_baseline
training_nvidia_nat_react_tools
training_nvidia_nat_optimized
```

## Workshop Setup Flow

The workshop installs the workflow package in editable mode before tracing:

```bash
cd climate_analyzer
uv pip install -e .
cd ..
```

Interpretation:

- NAT needs the package installed so custom entry points and registered tools are
  discoverable.
- This is the same requirement as the ReAct tools lesson.
- For this repo, the equivalent is:

```bash
python -m pip install -e .
```

Then Phoenix is launched:

```bash
scripts/serve_phoenix.sh
```

Local Phoenix URLs:

```text
Phoenix UI:      http://localhost:6006
Trace endpoint:  http://localhost:6006/v1/traces
```

The notebook lab generates a special `p6006` URL because it runs in a hosted
environment. Do not copy that JS workaround into this local project.

These names will make before/after comparisons clearer in Phoenix.

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

Then ask a multi-step question in the UI:

```text
Compare the temperature trends of Canada and Brazil. Which one is warming faster?
Also create a visualization of global trends.
```

Expected Phoenix view:

- one top-level ReAct workflow trace
- LLM calls
- tool calls such as `filter_by_country` and `create_visualization`
- latency and nested execution detail

## Answers From Implementation

- Phoenix is installed with `arize-phoenix==17.2.0`.
- Phoenix is launched locally with `scripts/serve_phoenix.sh`.
- The script sets `PHOENIX_ALLOWED_SANDBOX_PROVIDERS=NONE` by default to avoid
  slow WASM sandbox prefetch during local demo startup.
- NAT does not need a Phoenix-specific component in this environment.
- NAT exports traces through `_type: otelcollector`.
- Phoenix receives traces at `http://localhost:6006/v1/traces`.
- `nat validate` passes even if Phoenix is not running, because validation only
  checks configuration structure and registered component names.
