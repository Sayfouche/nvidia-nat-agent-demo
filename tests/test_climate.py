import json

from training_nvidia_nat.climate import (
    calculate_statistics,
    create_visualization,
    filter_by_country,
    find_extreme_years,
    list_countries,
    load_climate_data,
)


def test_list_countries_contains_demo_countries():
    df = load_climate_data()

    result = json.loads(list_countries(df))

    assert result["num_countries"] == 5
    assert "Brazil" in result["countries"]
    assert "Canada" in result["countries"]


def test_calculate_statistics_treats_empty_none_as_global():
    df = load_climate_data()

    empty_country = json.loads(calculate_statistics(df, ""))
    none_country = json.loads(calculate_statistics(df, "None"))

    assert empty_country["num_records"] == 80
    assert none_country["num_records"] == 80
    assert "country" not in empty_country


def test_filter_by_country_returns_country_trend():
    df = load_climate_data()

    result = json.loads(filter_by_country(df, "Canada"))

    assert result["country"] == "Canada"
    assert result["temperature_change_c"] > 0
    assert result["trend_per_decade_c"] > 0


def test_find_extreme_years_limits_results():
    df = load_climate_data()

    result = json.loads(find_extreme_years(df, "France", "warmest", 3))

    assert result["scope"] == "France"
    assert result["extreme_type"] == "warmest"
    assert len(result["years"]) == 3
    assert result["years"][0]["year"] == 2025


def test_create_visualization_writes_svg(tmp_path):
    df = load_climate_data()
    output_path = tmp_path / "trend.svg"

    result = json.loads(create_visualization(df, save_path=output_path))

    assert result["save_path"] == str(output_path)
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").startswith("<svg")
