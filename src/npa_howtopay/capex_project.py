import numpy as np
import polars as pl

## All dataframes used by functions in this class will have the following columns:
# project_year: int
# original_cost: float
# depreciation_lifetime: int
## (someday)depreciation_schedule: str # "straight line" or "accelerated"


# functions for generating dataframe rows for capex projects
def get_synthetic_initial_capex_projects(
    start_year: int, initial_ratebase: float, depreciation_lifetime: int
) -> pl.DataFrame:
    total_weight = (depreciation_lifetime * (depreciation_lifetime + 1) / 2) / depreciation_lifetime
    est_original_cost_per_year = initial_ratebase / total_weight
    return pl.DataFrame({
        "project_year": range(start_year - depreciation_lifetime + 1, start_year + 1),
        "original_cost": est_original_cost_per_year,
        "depreciation_lifetime": depreciation_lifetime,
    })


def get_non_lpp_gas_capex_projects(
    year: int,
    current_ratebase: float,
    baseline_non_lpp_gas_ratebase_growth: float,
    depreciation_lifetime: int,
) -> pl.DataFrame:
    return pl.DataFrame({
        "project_year": year,
        "original_cost": current_ratebase * baseline_non_lpp_gas_ratebase_growth,
        "depreciation_lifetime": depreciation_lifetime,
    })


def get_lpp_gas_capex_projects(
    year: int,
    gas_bau_lpp_costs_per_year: pl.DataFrame,
    npas_this_year: pl.DataFrame,
    depreciation_lifetime: int,
) -> pl.DataFrame:
    """
    Inputs:
    - year: int
    - gas_bau_lpp_costs_per_year: pl.DataFrame
      - columns: year, cost
      - year is not required to be unique
    - npas_this_year: pl.DataFrame
      - npa columns
    - depreciation_lifetime: int

    Outputs:
    - pl.DataFrame
      - capex project columns
    """
    assert all(npas_this_year["year"] == year)  # noqa: S101
    npa_pipe_costs_avoided = npas_this_year.select(pl.col("pipe_value_per_user") * pl.col("num_converts")).sum().item()
    bau_pipe_replacement_costs = (
        gas_bau_lpp_costs_per_year.filter(pl.col("year") == year).select(pl.col("cost")).sum().item()
    )
    remaining_pipe_replacement_cost = np.maximum(0, bau_pipe_replacement_costs - npa_pipe_costs_avoided)
    if remaining_pipe_replacement_cost > 0:
        return pl.DataFrame({
            "project_year": year,
            "original_cost": remaining_pipe_replacement_cost,
            "depreciation_lifetime": depreciation_lifetime,
        })
    else:
        return pl.DataFrame()


def get_non_npa_electric_capex_projects(
    year: int,
    current_ratebase: float,
    baseline_electric_ratebase_growth: float,
    depreciation_lifetime: int,
) -> pl.DataFrame:
    return pl.DataFrame({
        "project_year": year,
        "original_cost": current_ratebase * baseline_electric_ratebase_growth,
        "depreciation_lifetime": depreciation_lifetime,
    })


def get_grid_upgrade_capex_projects(
    year: int,
    npas_this_year: pl.DataFrame,
    peak_hp_kw: float,
    peak_aircon_kw: float,
    distribution_cost_per_peak_kw_increase: float,
    grid_upgrade_depreciation_lifetime: int,
) -> pl.DataFrame:
    assert all(npas_this_year["year"] == year)  # noqa: S101
    peak_kw_increase = (
        npas_this_year.select(
            pl.max_horizontal(
                pl.max_horizontal(
                    pl.col("num_converts") * pl.lit(peak_hp_kw) - pl.col("peak_kw_winter_headroom"), pl.lit(0)
                ),
                pl.max_horizontal(
                    pl.col("num_converts") * (1 - pl.col("aircon_percent_adoption_pre_npa")) * pl.lit(peak_aircon_kw)
                    - pl.col("peak_kw_summer_headroom"),
                    pl.lit(0),
                ),
            )
        )
        .sum()
        .item()
    )
    if peak_kw_increase > 0:
        return pl.DataFrame({
            "project_year": year,
            "original_cost": peak_kw_increase * distribution_cost_per_peak_kw_increase,
            "depreciation_lifetime": grid_upgrade_depreciation_lifetime,
        })
    else:
        return pl.DataFrame()


def get_npa_capex_projects(
    year: int, npas_this_year: pl.DataFrame, npa_install_cost: float, npa_lifetime: int
) -> pl.DataFrame:
    assert all(npas_this_year["year"] == year)  # noqa: S101
    npa_total_cost = npa_install_cost * npas_this_year.select(pl.col("num_converts")).sum().item()
    if npa_total_cost > 0:
        return pl.DataFrame({
            "project_year": year,
            "original_cost": npa_total_cost,
            "depreciation_lifetime": npa_lifetime,
        })
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


def compute_maintanence_costs(year: int, df: pl.DataFrame, maintenance_cost_pct: float) -> float:
    """Compute annual maintenance costs for capital projects.

    Args:
        year: The year to compute maintenance costs for
        df: DataFrame containing capital projects with columns:
            - project_type: str - Type of project (npa or other)
            - original_cost: float - Original cost of the project
        maintenance_cost_pct: float - Annual maintenance cost as percentage of original cost

    Returns:
        float: Total maintenance costs for the year, excluding NPA projects
    """
    df = df.filter(pl.col("project_type") != "npa")
    return float(df.select(pl.col("original_cost") * maintenance_cost_pct).sum().item())
