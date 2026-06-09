# NAT ReAct Tools Lesson

## Why This Lesson Matters

This lesson changes the project from a simple LLM chat workflow into an agentic
workflow:

```text
User question -> ReAct agent -> tool selection -> Python function -> observation -> final answer
```

For the GitHub project, this is the key transition from:

```text
NAT + NIM chatbot
```

to:

```text
NAT + NIM tool-using agent
```

## Tool Registration Pattern

NAT exposes Python functions to agents through four pieces:

```text
Input schema -> Config class -> Wrapper function -> YAML config
```

### Input Schema

Use Pydantic to describe tool inputs clearly for the LLM:

```python
from pydantic import BaseModel, Field


class CalculateStatsInput(BaseModel):
    country: str = Field(
        default="",
        description=(
            "Country name to filter by, e.g. 'United States' or 'France'. "
            "Leave empty for global statistics."
        ),
    )
```

The field descriptions are part of the agent interface. They help the LLM decide
how to call the tool.

### Config Class

Register a stable NAT type name:

```python
from nat.data_models.function import FunctionBaseConfig


class CalculateStatisticsConfig(
    FunctionBaseConfig,
    name="climate_calculate_statistics",
):
    """Configuration for calculating climate statistics."""
```

The `name` combines with the Python package namespace to become the `_type` used
in workflow YAML. In this repo, `name="calculate_statistics"` becomes:

```yaml
_type: training_nvidia_nat/calculate_statistics
```

### Wrapper Function

Connect NAT registration, preloaded data, and a callable async wrapper:

```python
from nat.builder.builder import Builder
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function


@register_function(config_type=CalculateStatisticsConfig)
async def calculate_statistics_tool(
    config: CalculateStatisticsConfig,
    builder: Builder,
):
    df = load_climate_data(DATA_PATH)

    async def _wrapper(inputs: CalculateStatsInput) -> str:
        return calculate_statistics(df, inputs.country)

    yield FunctionInfo.from_fn(
        _wrapper,
        input_schema=CalculateStatsInput,
        description=(
            "Calculate temperature statistics globally or for a specific country. "
            "Returns JSON with mean, min, max, standard deviation, record count, "
            "trend per decade, analyzed years, and country when specified."
        ),
    )
```

Important integration detail: ReAct agents may pass `None` when no country is
specified. The wrapper or pure function must normalize `None`, `""`, and
`"None"` as no country filter.

### YAML Wiring

Declare tools under `functions`, then expose selected local function names to
the ReAct workflow:

```yaml
functions:
  calculate_statistics:
    _type: training_nvidia_nat/calculate_statistics
    description: "Calculate temperature statistics globally or for a specific country"

workflow:
  _type: react_agent
  llm_name: climate_llm
  tool_names:
    - calculate_statistics
  verbose: true
  max_tool_calls: 8
  parse_agent_response_max_retries: 2
  additional_instructions: |
    You are a climate analysis assistant.
```

`tool_names` must match keys under `functions`, not `_type` values.

Do not replace `system_prompt` unless you also include NAT's required ReAct
placeholders `{tools}` and `{tool_names}`. This repo uses
`additional_instructions` to keep the default ReAct format intact.

## Python Packaging

NAT discovers custom tools through Python package entry points. In NAT 1.7.0,
this repo uses the `nat.components` entry point group:

```toml
[project.entry-points."nat.components"]
training_nvidia_nat = "training_nvidia_nat.register"
```

Then reinstall in editable mode:

```bash
python -m pip install -e .
```

The target module imports or defines the `@register_function` declarations.

## Multi-Tool Agent Target

The implemented workflow exposes five climate tools:

```text
list_countries
calculate_statistics
filter_by_country
find_extreme_years
create_visualization
```

Each tool should have:

- pure function tests
- Pydantic input schema
- NAT config class
- NAT wrapper function
- YAML reference

## Expected Data Outputs

`calculate_statistics(df)` returns a JSON-compatible string with fields like:

```json
{
  "mean_temperature_c": 17.91,
  "min_temperature_c": -15.71,
  "max_temperature_c": 29.23,
  "std_deviation_c": 7.83,
  "num_records": 1210,
  "trend_per_decade_c": 0.241,
  "years_analyzed": "1950-2025"
}
```

If a country filter is applied, include `country`.

## Visualization Tool

The visualization tool creates SVG file artifacts. This repo uses the Python
standard library instead of `matplotlib`, because `matplotlib` is not installed
in the original workshop venv.

Implemented plot type: `annual_trend`.

## Showcase Scenario

A strong demo prompt:

```text
Compare the temperature trends of Canada and Brazil. Which one is warming faster?
Also create a visualization of global trends.
```

This demonstrates:

- multi-step reasoning
- multiple tool calls
- country comparison
- generated visual artifact
- final synthesis

## Future Repo Shape

Do not run `nat workflow create` directly over the existing repo. Use the
scaffold as a reference and adapt the current package:

```text
configs/
  react_climate.yml
src/training_nvidia_nat/
  register.py
  climate_data.py
  climate_stats.py
  tools/
    climate_statistics.py
tests/
  test_climate_stats.py
  test_climate_tools.py
```

Keep `config.yml` as the baseline `chat_completion` workflow.

## Next Lesson Bridge

The next workshop topic is Phoenix observability. This fits naturally after
tools:

```text
baseline chat -> ReAct tools -> observability/tracing -> evaluation
```

The current docs should guide implementation of the ReAct tools before adding
Phoenix tracing.
