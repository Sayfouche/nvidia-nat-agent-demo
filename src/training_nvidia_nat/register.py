"""NAT tool registration for the climate analysis demo."""

from nat.builder.builder import Builder
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.function import FunctionBaseConfig
from pydantic import BaseModel, Field

from training_nvidia_nat.climate import (
    calculate_statistics,
    create_visualization,
    filter_by_country,
    find_extreme_years,
    list_countries,
    load_climate_data,
)


class ListCountriesInput(BaseModel):
    pass


class CountryInput(BaseModel):
    country: str = Field(description="Country name, for example 'Canada' or 'Brazil'.")


class CalculateStatsInput(BaseModel):
    country: str = Field(
        default="",
        description="Country name to filter by. Leave empty for global statistics.",
    )


class ExtremeYearsInput(BaseModel):
    country: str = Field(
        default="",
        description="Optional country name. Leave empty for global extremes.",
    )
    extreme_type: str = Field(
        default="warmest",
        description="Use 'warmest' or 'coldest'.",
    )
    top_n: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of years to return.",
    )


class VisualizationInput(BaseModel):
    plot_type: str = Field(
        default="annual_trend",
        description="Visualization type. This demo supports 'annual_trend'.",
    )
    country: str = Field(
        default="",
        description="Optional country name. Leave empty for a global trend.",
    )
    save_path: str = Field(
        default="artifacts/global_temperature_trend.svg",
        description="Local SVG path where the visualization should be saved.",
    )


class ListCountriesConfig(FunctionBaseConfig, name="list_countries"):
    """Configuration for listing available countries."""


class CalculateStatisticsConfig(FunctionBaseConfig, name="calculate_statistics"):
    """Configuration for calculating climate statistics."""


class FilterByCountryConfig(FunctionBaseConfig, name="filter_by_country"):
    """Configuration for filtering climate data by country."""


class FindExtremeYearsConfig(FunctionBaseConfig, name="find_extreme_years"):
    """Configuration for finding warmest or coldest years."""


class CreateVisualizationConfig(FunctionBaseConfig, name="create_visualization"):
    """Configuration for creating climate visualizations."""


@register_function(config_type=ListCountriesConfig)
async def list_countries_tool(config: ListCountriesConfig, builder: Builder):
    df = load_climate_data()

    async def _wrapper(inputs: ListCountriesInput) -> str:
        return list_countries(df)

    yield FunctionInfo.from_fn(
        _wrapper,
        input_schema=ListCountriesInput,
        description="List all available countries in the climate dataset.",
    )


@register_function(config_type=CalculateStatisticsConfig)
async def calculate_statistics_tool(
    config: CalculateStatisticsConfig,
    builder: Builder,
):
    df = load_climate_data()

    async def _wrapper(inputs: CalculateStatsInput) -> str:
        return calculate_statistics(df, inputs.country)

    yield FunctionInfo.from_fn(
        _wrapper,
        input_schema=CalculateStatsInput,
        description=(
            "Calculate temperature statistics globally or for a specific country. "
            "Returns JSON with mean, min, max, standard deviation, record count, "
            "trend per decade, and analyzed year range."
        ),
    )


@register_function(config_type=FilterByCountryConfig)
async def filter_by_country_tool(config: FilterByCountryConfig, builder: Builder):
    df = load_climate_data()

    async def _wrapper(inputs: CountryInput) -> str:
        return filter_by_country(df, inputs.country)

    yield FunctionInfo.from_fn(
        _wrapper,
        input_schema=CountryInput,
        description="Get climate trend details for one specific country.",
    )


@register_function(config_type=FindExtremeYearsConfig)
async def find_extreme_years_tool(config: FindExtremeYearsConfig, builder: Builder):
    df = load_climate_data()

    async def _wrapper(inputs: ExtremeYearsInput) -> str:
        return find_extreme_years(
            df,
            inputs.country,
            inputs.extreme_type,
            inputs.top_n,
        )

    yield FunctionInfo.from_fn(
        _wrapper,
        input_schema=ExtremeYearsInput,
        description=(
            "Find the warmest or coldest years globally or for a specific country."
        ),
    )


@register_function(config_type=CreateVisualizationConfig)
async def create_visualization_tool(
    config: CreateVisualizationConfig,
    builder: Builder,
):
    df = load_climate_data()

    async def _wrapper(inputs: VisualizationInput) -> str:
        return create_visualization(
            df,
            inputs.plot_type,
            inputs.country,
            inputs.save_path,
        )

    yield FunctionInfo.from_fn(
        _wrapper,
        input_schema=VisualizationInput,
        description=(
            "Create a climate trend SVG visualization and save it to a local file."
        ),
    )
