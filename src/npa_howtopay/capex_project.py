import numpy as np
import polars as pl
from attrs import define, field, validators

from .npa_project import (
    compute_hp_converts_from_df,
    compute_npa_pipe_cost_avoided_from_df,
    compute_peak_kw_increase_from_df,
)

## All dataframes used by functions in this class will have the following columns:
# project_year: int
# project_type: str # "synthetic_initial", "misc", "pipeline", "grid_upgrade", "npa"
# original_cost: float
# depreciation_lifetime: int
## (someday)depreciation_schedule: str # "straight line" or "accelerated"


@define
class CapexProject:
    project_year: int = field()
    project_type: str = field(
        validator=validators.in_(["synthetic_initial", "misc", "pipeline", "grid_upgrade", "npa"])
    )
    original_cost: float = field(validator=validators.ge(0.0))
    depreciation_lifetime: int = field(validator=validators.ge(1))

    def to_df(self) -> pl.DataFrame:
        return pl.DataFrame({
            "project_year": [self.project_year],
            "project_type": [self.project_type],
            "original_cost": [self.original_cost],
            "depreciation_lifetime": [self.depreciation_lifetime],
        })


# functions for generating dataframe rows for capex projects
def get_synthetic_initial_capex_projects(
    start_year: int, initial_ratebase: float, depreciation_lifetime: int
) -> pl.DataFrame:
    total_weight = (depreciation_lifetime * (depreciation_lifetime + 1) / 2) / depreciation_lifetime
    est_original_cost_per_year = initial_ratebase / total_weight
    return pl.DataFrame({
        "project_year": range(start_year - depreciation_lifetime + 1, start_year + 1),
        "project_type": ["synthetic_initial"] * depreciation_lifetime,
        "original_cost": est_original_cost_per_year,
        "depreciation_lifetime": depreciation_lifetime,
    })


def get_non_lpp_gas_capex_projects(
    year: int,
    current_ratebase: float,
    baseline_non_lpp_gas_ratebase_growth: float,
    depreciation_lifetime: int,
) -> pl.DataFrame:
    return CapexProject(
        project_year=year,
        project_type="misc",
        original_cost=current_ratebase * baseline_non_lpp_gas_ratebase_growth,
        depreciation_lifetime=depreciation_lifetime,
    ).to_df()


def get_lpp_gas_capex_projects(
    year: int,
    gas_bau_lpp_costs_per_year: pl.DataFrame,
    npa_projects: pl.DataFrame,
    depreciation_lifetime: int,
) -> pl.DataFrame:
    """
    Inputs:
    - year: int
    - gas_bau_lpp_costs_per_year: pl.DataFrame
      - columns: year, cost
      - year is not required to be unique
    - npa_projects: pl.DataFrame
      - npa columns
    - depreciation_lifetime: int

    Outputs:
    - pl.DataFrame
      - capex project columns
    """
    npas_this_year = npa_projects.filter(pl.col("project_year") == year)
    npa_pipe_costs_avoided = compute_npa_pipe_cost_avoided_from_df(year, npas_this_year)
    bau_pipe_replacement_costs = (
        gas_bau_lpp_costs_per_year.filter(pl.col("year") == year).select(pl.col("cost")).sum().item()
    )
    remaining_pipe_replacement_cost = np.maximum(0, bau_pipe_replacement_costs - npa_pipe_costs_avoided)
    if remaining_pipe_replacement_cost > 0:
        return CapexProject(
            project_year=year,
            project_type="pipeline",
            original_cost=remaining_pipe_replacement_cost,
            depreciation_lifetime=depreciation_lifetime,
        ).to_df()
    else:
        return pl.DataFrame()


def get_non_npa_electric_capex_projects(
    year: int,
    current_ratebase: float,
    baseline_electric_ratebase_growth: float,
    depreciation_lifetime: int,
) -> pl.DataFrame:
    return CapexProject(
        project_year=year,
        project_type="misc",
        original_cost=current_ratebase * baseline_electric_ratebase_growth,
        depreciation_lifetime=depreciation_lifetime,
    ).to_df()


def get_grid_upgrade_capex_projects(
    year: int,
    npa_projects: pl.DataFrame,
    peak_hp_kw: float,
    peak_aircon_kw: float,
    distribution_cost_per_peak_kw_increase: float,
    grid_upgrade_depreciation_lifetime: int,
) -> pl.DataFrame:
    npas_this_year = npa_projects.filter(pl.col("project_year") == year)
    peak_kw_increase = compute_peak_kw_increase_from_df(year, npas_this_year, peak_hp_kw, peak_aircon_kw)
    if peak_kw_increase > 0:
        return CapexProject(
            project_year=year,
            project_type="grid_upgrade",
            original_cost=peak_kw_increase * distribution_cost_per_peak_kw_increase,
            depreciation_lifetime=grid_upgrade_depreciation_lifetime,
        ).to_df()
    else:
        return pl.DataFrame()


def get_npa_capex_projects(
    year: int, npa_projects: pl.DataFrame, npa_install_cost: float, npa_lifetime: int
) -> pl.DataFrame:
    npas_this_year = npa_projects.filter(pl.col("project_year") == year)
    npa_total_cost = npa_install_cost * compute_hp_converts_from_df(
        year, npas_this_year, cumulative=False, npa_only=True
    )
    if npa_total_cost > 0:
        return CapexProject(
            project_year=year, project_type="npa", original_cost=npa_total_cost, depreciation_lifetime=npa_lifetime
        ).to_df()
    else:
        return pl.DataFrame()


# functions for computing things given a dataframe of capex projects
def compute_ratebase_from_capex_projects(year: int, df: pl.DataFrame) -> float:
    df = df.with_columns(
        pl.when(pl.lit(year) < pl.col("project_year"))
        .then(pl.lit(0))
        .otherwise((1 - (pl.lit(year) - pl.col("project_year")) / pl.col("depreciation_lifetime")).clip(lower_bound=0))
        .alias("depreciation_fraction")
    )
    return float(df.select(pl.col("depreciation_fraction") * pl.col("original_cost")).sum().item())


def compute_depreciation_expense_from_capex_projects(year: int, df: pl.DataFrame) -> float:
    return float(
        df.select(
            pl.when(
                (pl.lit(year) > pl.col("project_year"))
                & (pl.lit(year) <= pl.col("project_year") + pl.col("depreciation_lifetime"))
            )
            .then(pl.col("original_cost") / pl.col("depreciation_lifetime"))
            .otherwise(pl.lit(0))
        )
        .sum()
        .item()
    )
