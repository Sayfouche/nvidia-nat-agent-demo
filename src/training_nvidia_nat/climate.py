from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

import numpy as np
import pandas as pd

DATA_RESOURCE = "data/temperature_annual.csv"


def default_data_path() -> Path:
    return Path(str(files("training_nvidia_nat").joinpath(DATA_RESOURCE)))


def load_climate_data(file_path: str | Path | None = None) -> pd.DataFrame:
    path = Path(file_path) if file_path else default_data_path()
    df = pd.read_csv(path)
    expected_columns = {"country", "year", "temperature_c"}
    missing_columns = expected_columns - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Climate dataset is missing columns: {missing}")
    return df


def normalize_country(country: str | None) -> str | None:
    if country is None:
        return None

    normalized = str(country).strip()
    if normalized == "" or normalized.lower() in {"none", "null", "global", "world"}:
        return None
    return normalized


def _json(data: dict[str, Any] | list[dict[str, Any]]) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def _country_frame(df: pd.DataFrame, country: str | None) -> pd.DataFrame:
    normalized_country = normalize_country(country)
    if normalized_country is None:
        return df.copy()

    country_mask = df["country"].str.lower() == normalized_country.lower()
    country_df = df.loc[country_mask].copy()
    if country_df.empty:
        available = sorted(df["country"].unique().tolist())
        raise ValueError(
            f"No climate data found for country '{normalized_country}'. "
            f"Available countries: {', '.join(available)}"
        )
    return country_df


def _trend_per_decade(frame: pd.DataFrame) -> float:
    yearly_mean = frame.groupby("year", as_index=False)["temperature_c"].mean()
    if len(yearly_mean) < 2:
        return 0.0
    slope_per_year = np.polyfit(
        yearly_mean["year"].to_numpy(),
        yearly_mean["temperature_c"].to_numpy(),
        1,
    )[0]
    return round(float(slope_per_year * 10), 3)


def calculate_statistics(df: pd.DataFrame, country: str | None = None) -> str:
    frame = _country_frame(df, country)
    values = frame["temperature_c"].astype(float).tolist()
    country_name = normalize_country(country)
    result: dict[str, Any] = {
        "mean_temperature_c": round(mean(values), 2),
        "min_temperature_c": round(min(values), 2),
        "max_temperature_c": round(max(values), 2),
        "std_deviation_c": round(pstdev(values), 2),
        "num_records": len(values),
        "trend_per_decade_c": _trend_per_decade(frame),
        "years_analyzed": f"{int(frame['year'].min())}-{int(frame['year'].max())}",
    }
    if country_name:
        result["country"] = country_name
    return _json(result)


def list_countries(df: pd.DataFrame) -> str:
    countries = sorted(df["country"].unique().tolist())
    return _json(
        {
            "countries": countries,
            "num_countries": len(countries),
            "years_analyzed": f"{int(df['year'].min())}-{int(df['year'].max())}",
        }
    )


def filter_by_country(df: pd.DataFrame, country: str) -> str:
    country_name = normalize_country(country)
    if not country_name:
        raise ValueError("country is required for filter_by_country")

    frame = _country_frame(df, country_name).sort_values("year")
    first = frame.iloc[0]
    last = frame.iloc[-1]
    return _json(
        {
            "country": country_name,
            "num_records": len(frame),
            "years_analyzed": f"{int(first['year'])}-{int(last['year'])}",
            "first_temperature_c": round(float(first["temperature_c"]), 2),
            "last_temperature_c": round(float(last["temperature_c"]), 2),
            "temperature_change_c": round(
                float(last["temperature_c"]) - float(first["temperature_c"]), 2
            ),
            "trend_per_decade_c": _trend_per_decade(frame),
        }
    )


def find_extreme_years(
    df: pd.DataFrame,
    country: str | None = None,
    extreme_type: str = "warmest",
    top_n: int = 5,
) -> str:
    frame = _country_frame(df, country)
    yearly_mean = frame.groupby("year", as_index=False)["temperature_c"].mean()
    ascending = extreme_type.strip().lower() in {"coldest", "min", "lowest"}
    ordered = yearly_mean.sort_values("temperature_c", ascending=ascending).head(top_n)
    rows = [
        {"year": int(row.year), "temperature_c": round(float(row.temperature_c), 2)}
        for row in ordered.itertuples()
    ]
    payload: dict[str, Any] = {
        "extreme_type": "coldest" if ascending else "warmest",
        "years": rows,
        "scope": normalize_country(country) or "global",
    }
    return _json(payload)


def create_visualization(
    df: pd.DataFrame,
    plot_type: str = "annual_trend",
    country: str | None = None,
    save_path: str | Path | None = None,
) -> str:
    if plot_type != "annual_trend":
        raise ValueError("Only plot_type='annual_trend' is supported in this demo")

    frame = _country_frame(df, country)
    yearly_mean = frame.groupby("year", as_index=False)["temperature_c"].mean()
    output_path = Path(save_path or "artifacts/global_temperature_trend.svg")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scope = normalize_country(country) or "Global"
    _write_line_chart_svg(yearly_mean, output_path, scope)
    return _json(
        {
            "plot_type": plot_type,
            "scope": normalize_country(country) or "global",
            "save_path": str(output_path),
            "description": "Created annual average temperature trend SVG.",
        }
    )


def _write_line_chart_svg(
    frame: pd.DataFrame,
    output_path: Path,
    title_scope: str,
) -> None:
    width = 900
    height = 520
    margin_left = 70
    margin_right = 35
    margin_top = 60
    margin_bottom = 70
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    years = frame["year"].astype(float).tolist()
    temps = frame["temperature_c"].astype(float).tolist()
    min_year, max_year = min(years), max(years)
    min_temp, max_temp = min(temps), max(temps)
    temp_padding = max((max_temp - min_temp) * 0.12, 0.5)
    min_temp -= temp_padding
    max_temp += temp_padding

    def x_for(year: float) -> float:
        return margin_left + ((year - min_year) / (max_year - min_year)) * plot_width

    def y_for(temp: float) -> float:
        return margin_top + ((max_temp - temp) / (max_temp - min_temp)) * plot_height

    points = " ".join(
        f"{x_for(year):.1f},{y_for(temp):.1f}"
        for year, temp in zip(years, temps, strict=True)
    )
    trend = _trend_per_decade(frame)
    trend_start = temps[0]
    trend_end = trend_start + ((max_year - min_year) / 10) * trend
    trend_points = (
        f"{x_for(min_year):.1f},{y_for(trend_start):.1f} "
        f"{x_for(max_year):.1f},{y_for(trend_end):.1f}"
    )

    x_labels = [int(min_year), int((min_year + max_year) / 2), int(max_year)]
    y_labels = [min_temp, (min_temp + max_temp) / 2, max_temp]
    grid = []
    for year in x_labels:
        x = x_for(year)
        grid.append(
            f'<line x1="{x:.1f}" y1="{margin_top}" x2="{x:.1f}" '
            f'y2="{height - margin_bottom}" stroke="#d8dee9"/>'
        )
        grid.append(
            f'<text x="{x:.1f}" y="{height - 35}" '
            f'text-anchor="middle">{year}</text>'
        )
    for temp in y_labels:
        y = y_for(temp)
        grid.append(
            f'<line x1="{margin_left}" y1="{y:.1f}" '
            f'x2="{width - margin_right}" y2="{y:.1f}" stroke="#d8dee9"/>'
        )
        grid.append(
            f'<text x="{margin_left - 12}" y="{y + 4:.1f}" '
            f'text-anchor="end">{temp:.1f}</text>'
        )

    svg_lines = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        (
            f'  <text x="{width / 2}" y="32" text-anchor="middle" '
            'font-family="Arial" font-size="22" font-weight="700">'
            f"{title_scope} Annual Average Temperature Trend</text>"
        ),
        '  <g font-family="Arial" font-size="13" fill="#2f3747">',
        f"    {''.join(grid)}",
        "  </g>",
        (
            f'  <line x1="{margin_left}" y1="{height - margin_bottom}" '
            f'x2="{width - margin_right}" y2="{height - margin_bottom}" '
            'stroke="#2f3747" stroke-width="1.5"/>'
        ),
        (
            f'  <line x1="{margin_left}" y1="{margin_top}" '
            f'x2="{margin_left}" y2="{height - margin_bottom}" '
            'stroke="#2f3747" stroke-width="1.5"/>'
        ),
        (
            f'  <polyline points="{points}" fill="none" '
            'stroke="#2563eb" stroke-width="3"/>'
        ),
        (
            f'  <polyline points="{trend_points}" fill="none" '
            'stroke="#dc2626" stroke-width="2" stroke-dasharray="7 5"/>'
        ),
        (
            f'  <text x="{width / 2}" y="{height - 12}" text-anchor="middle" '
            'font-family="Arial" font-size="14">Year</text>'
        ),
        (
            f'  <text transform="translate(18 {height / 2}) rotate(-90)" '
            'text-anchor="middle" font-family="Arial" font-size="14">'
            "Temperature (C)</text>"
        ),
        (
            f'  <text x="{width - margin_right}" y="54" text-anchor="end" '
            'font-family="Arial" font-size="13" fill="#dc2626">'
            f"Trend: {trend:.3f} C/decade</text>"
        ),
        "</svg>",
    ]
    svg = "\n".join(svg_lines) + "\n"
    output_path.write_text(svg, encoding="utf-8")
