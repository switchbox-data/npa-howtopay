from attrs import define
import polars as pl
from typing import Optional


@define
class WebParams:
    npa_num_projects: int
    num_converts: int
    pipe_value_per_user: float
    pipe_decomm_cost_per_user: float
    peak_kw_winter_headroom: float
    peak_kw_summer_headroom: float
    aircon_percent_adoption_pre_npa: float
    non_npa_scattershot_electrifiction_users_per_year: int
    gas_fixed_overhead_costs: float
    electric_fixed_overhead_costs: float
    gas_bau_lpp_costs_per_year: float
    is_scattershot: bool
    # stuff_for_producing_ratebase_baseline


def create_npa_projects(web_params: WebParams, start_year: int, end_year: int) -> pl.DataFrame:
    return pl.DataFrame({
        "project_year": list(range(start_year, end_year + 1)),
        "num_converts": [web_params.num_converts] * (end_year - start_year + 1),
        "pipe_value_per_user": [web_params.pipe_value_per_user] * (end_year - start_year + 1),
        "pipe_decomm_cost_per_user": [web_params.pipe_decomm_cost_per_user] * (end_year - start_year + 1),
        "peak_kw_winter_headroom": [web_params.peak_kw_winter_headroom] * (end_year - start_year + 1),
        "peak_kw_summer_headroom": [web_params.peak_kw_summer_headroom] * (end_year - start_year + 1),
        "aircon_percent_adoption_pre_npa": [web_params.aircon_percent_adoption_pre_npa] * (end_year - start_year + 1),
        "is_scattershot": [web_params.is_scattershot] * (end_year - start_year + 1),
    })


def create_gas_fixed_overhead_costs(
    web_params: WebParams, start_year: int, end_year: int, cost_inflation_rate: float = 0.0
) -> pl.DataFrame:
    years = list(range(start_year, end_year + 1))
    base_cost = web_params.gas_fixed_overhead_costs

    # Apply compound inflation: cost * (1 + rate)^(year - start_year)
    costs = [base_cost * (1 + cost_inflation_rate) ** (year - start_year) for year in years]

    return pl.DataFrame({
        "year": years,
        "cost": costs,
    })


def create_electric_fixed_overhead_costs(
    web_params: WebParams, start_year: int, end_year: int, cost_inflation_rate: float = 0.0
) -> pl.DataFrame:
    years = list(range(start_year, end_year + 1))
    base_cost = web_params.electric_fixed_overhead_costs

    # Apply compound inflation: cost * (1 + rate)^(year - start_year)
    costs = [base_cost * (1 + cost_inflation_rate) ** (year - start_year) for year in years]

    return pl.DataFrame({
        "year": years,
        "cost": costs,
    })


def create_gas_bau_lpp_costs_per_year(
    web_params: WebParams, start_year: int, end_year: int, cost_inflation_rate: float = 0.0
) -> pl.DataFrame:
    years = list(range(start_year, end_year + 1))
    base_cost = web_params.gas_bau_lpp_costs_per_year

    # Apply compound inflation: cost * (1 + rate)^(year - start_year)
    costs = [base_cost * (1 + cost_inflation_rate) ** (year - start_year) for year in years]

    return pl.DataFrame({
        "year": years,
        "cost": costs,
    })


def create_time_series_from_web_params(
    web_params: WebParams, start_year: int, end_year: int, cost_inflation_rate: float = 0.0
) -> dict[str, pl.DataFrame]:
    """Create all time series DataFrames from web parameters"""
    return {
        "npa_projects": create_npa_projects(web_params, start_year, end_year),
        "gas_fixed_overhead_costs": create_gas_fixed_overhead_costs(
            web_params, start_year, end_year, cost_inflation_rate
        ),
        "electric_fixed_overhead_costs": create_electric_fixed_overhead_costs(
            web_params, start_year, end_year, cost_inflation_rate
        ),
        "gas_bau_lpp_costs_per_year": create_gas_bau_lpp_costs_per_year(
            web_params, start_year, end_year, cost_inflation_rate
        ),
    }
