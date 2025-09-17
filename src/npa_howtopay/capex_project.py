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
            "depreciation_lifetime": pl.Series([self.depreciation_lifetime], dtype=pl.Int64),
            "retirement_year": [self.project_year + self.depreciation_lifetime],
        })


def get_synthetic_initial_capex_projects(
    start_year: int, initial_ratebase: float, depreciation_lifetime: int
) -> pl.DataFrame:
    """
    Generate synthetic capex projects to represent the projects that make up the initial ratebase.

    Creates a series of historical capex projects that would result in the given initial ratebase value, assuming straight-line depreciation. Uses the triangular number formula to create a uniform distribution of projects over the depreciation lifetime, where each project has the same original cost. Projects are distributed evenly over depreciation_lifetime years leading up to start_year.

    Args:
        start_year: The first year of the model
        initial_ratebase: The target ratebase value at start_year
        depreciation_lifetime: The blended depreciation lifetime for the synthetic projects

    Returns:
        pl.DataFrame with columns:
            - project_year: Year the project was initiated
            - project_type: "synthetic_initial"
            - original_cost: Cost of the project
            - depreciation_lifetime: Depreciation lifetime in years
            - retirement_year: Year the project is fully depreciated
    """
    total_weight = (depreciation_lifetime * (depreciation_lifetime + 1) / 2) / depreciation_lifetime
    est_original_cost_per_year = initial_ratebase / total_weight
    project_years = range(start_year - depreciation_lifetime + 1, start_year + 1)
    return pl.DataFrame({
        "project_year": project_years,
        "project_type": ["synthetic_initial"] * depreciation_lifetime,
        "original_cost": est_original_cost_per_year,
        "depreciation_lifetime": pl.Series([depreciation_lifetime] * depreciation_lifetime, dtype=pl.Int64),
        "retirement_year": pl.Series([year + depreciation_lifetime for year in project_years], dtype=pl.Int64),
    })


def get_non_lpp_gas_capex_projects(
    year: int,
    current_ratebase: float,
    baseline_non_lpp_gas_ratebase_growth: float,
    depreciation_lifetime: int,
    construction_inflation_rate: float,
) -> pl.DataFrame:
    """
    Generate capex projects for non-LPP (non-leak prone pipe) gas infrastructure.

    These represent routine gas infrastructure investments not related to pipe replacement or npas,
    such as meter replacements, regulator stations, etc. The cost is calculated as a
    percentage of current ratebase, adjusted for construction cost inflation.

    Args:
        year: The year to generate projects for
        current_ratebase: Current value of the gas utility's ratebase
        baseline_non_lpp_gas_ratebase_growth: Annual growth rate for non-LPP capex as fraction of ratebase
        depreciation_lifetime: Blended depreciation lifetime in years for these projects
        construction_inflation_rate: Annual inflation rate for construction costs

    Returns:
        pl.DataFrame with columns:
            - project_year: Year the project was initiated
            - project_type: "misc" for miscellaneous gas infrastructure
            - original_cost: Cost of the project
            - depreciation_lifetime: Depreciation lifetime in years
            - retirement_year: Year the project is fully depreciated
    """
    return CapexProject(
        project_year=year,
        project_type="misc",
        original_cost=current_ratebase * baseline_non_lpp_gas_ratebase_growth * (1 + construction_inflation_rate),
        depreciation_lifetime=depreciation_lifetime,
    ).to_df()


def get_lpp_gas_capex_projects(
    year: int,
    gas_bau_lpp_costs_per_year: pl.DataFrame,
    npa_projects: pl.DataFrame,
    depreciation_lifetime: int,
) -> pl.DataFrame:
    """
    Generate capex projects for leak-prone pipe (LPP) replacement in the gas system.

    This function calculates the remaining pipe replacement costs after accounting for pipe
    replacements avoided by NPA projects. If NPAs avoid all planned pipe replacements in a given
    year, returns an empty dataframe.

    Args:
        year: The year to generate projects for
        gas_bau_lpp_costs_per_year: DataFrame containing business-as-usual pipe replacement costs
            with columns:
            - year: Year of planned replacement
            - cost: Cost of planned replacement
            Note: Multiple entries may exist per year
        npa_projects: DataFrame containing NPA project details, used to calculate avoided pipe costs
        depreciation_lifetime: Depreciation lifetime in years for pipe replacement projects

    Returns:
        pl.DataFrame with columns:
            - project_year: Year the project was initiated
            - project_type: "pipeline" for pipe replacement projects
            - original_cost: Cost of the project after subtracting avoided costs
            - depreciation_lifetime: Depreciation lifetime in years
            - retirement_year: Year the project is fully depreciated
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
        return return_empty_capex_df()


def get_non_npa_electric_capex_projects(
    year: int,
    current_ratebase: float,
    baseline_electric_ratebase_growth: float,
    depreciation_lifetime: int,
    construction_inflation_rate: float,
) -> pl.DataFrame:
    """
    Generate capex projects for non-NPA non-grid upgrade electric system upgrades.

    This function calculates the baseline capital expenditures for the electric system,
    excluding NPA-related projects. The expenditure grows with both the baseline growth rate
    and construction inflation.

    Args:
        year: The year to generate projects for
        current_ratebase: Current value of the electric utility's ratebase
        baseline_electric_ratebase_growth: Annual growth rate of non-NPA electric capex as fraction of ratebase
        depreciation_lifetime: Blended depreciation lifetime in years for electric system projects
        construction_inflation_rate: Annual inflation rate for construction costs

    Returns:
        pl.DataFrame with columns:
            - project_year: Year the project was initiated
            - project_type: "misc" for miscellaneous electric system upgrades
            - original_cost: Cost of the project including construction inflation
            - depreciation_lifetime: Depreciation lifetime in years
    """
    return CapexProject(
        project_year=year,
        project_type="misc",
        original_cost=current_ratebase * baseline_electric_ratebase_growth * (1 + construction_inflation_rate),
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
    """
    Generate capex projects for grid upgrades needed to support NPA installations.

    This function calculates the required grid upgrades based on the peak power increase
    from heat pumps and air conditioners installed as part of NPA projects. The cost
    scales linearly with the total peak power increase.

    Args:
        year: The year to generate projects for
        npa_projects: DataFrame containing NPA project details
        peak_hp_kw: Peak power draw in kW for a heat pump
        peak_aircon_kw: Peak power draw in kW for an air conditioner
        distribution_cost_per_peak_kw_increase: Cost per kW of increasing grid capacity in year of project
        grid_upgrade_depreciation_lifetime: Depreciation lifetime in years for grid upgrades

    Returns:
        pl.DataFrame with columns:
            - project_year: Year the project was initiated
            - project_type: "grid_upgrade" for grid capacity upgrades
            - original_cost: Total cost of grid upgrades
            - depreciation_lifetime: Depreciation lifetime in years
    """
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
        return return_empty_capex_df()


def get_npa_capex_projects(
    year: int, npa_projects: pl.DataFrame, npa_install_cost: float, npa_lifetime: int
) -> pl.DataFrame:
    """
    Generate capex projects for NPA (non-pipe alternative) installations.

    This function calculates the capital costs associated with installing NPAs in a given year.
    The total cost is based on the number of heat pump conversions and the per-unit installation cost.

    Args:
        year: The year to generate projects for
        npa_projects: DataFrame containing NPA project details
        npa_install_cost: Cost per household of installing an NPA
        npa_lifetime: Expected lifetime in years of an NPA installation

    Returns:
        pl.DataFrame with columns:
            - project_year: Year the project was initiated
            - project_type: "npa" for NPA installations
            - original_cost: Total cost of NPA installations
            - depreciation_lifetime: Depreciation lifetime in years
    """
    npas_this_year = npa_projects.filter(pl.col("project_year") == year)
    npa_total_cost = npa_install_cost * compute_hp_converts_from_df(
        year, npas_this_year, cumulative=False, npa_only=True
    )
    if npa_total_cost > 0:
        return CapexProject(
            project_year=year, project_type="npa", original_cost=npa_total_cost, depreciation_lifetime=npa_lifetime
        ).to_df()
    else:
        return return_empty_capex_df()


def compute_ratebase_from_capex_projects(year: int, df: pl.DataFrame) -> float:
    """Compute the ratebase value for a given year from capital projects.

    For each project, the ratebase value declines linearly from the original cost to zero over the depreciation lifetime.
    Projects that haven't started yet (year < project_year) have zero ratebase value.
    Projects that are fully depreciated have zero ratebase value.
    Projects that are in the year of the project have the full original cost added to the ratebase.

    Args:
        year: The year to compute ratebase for
        df: DataFrame containing capital projects with columns:
            - project_year: int - Year project was initiated
            - original_cost: float - Original cost of the project
            - depreciation_lifetime: int - Number of years to depreciate over

    Returns:
        float: Total ratebase value for the year across all projects
    """
    df = df.with_columns(
        pl.when(pl.lit(year) < pl.col("project_year"))
        .then(pl.lit(0))
        .otherwise((1 - (pl.lit(year) - pl.col("project_year")) / pl.col("depreciation_lifetime")).clip(lower_bound=0))
        .alias("depreciation_fraction")
    )
    return float(df.select(pl.col("depreciation_fraction") * pl.col("original_cost")).sum().item())


def compute_depreciation_expense_from_capex_projects(year: int, df: pl.DataFrame) -> float:
    """Compute annual depreciation expense for capital projects.

    For each project, depreciation expense is the original cost divided evenly over the depreciation lifetime.
    Depreciation starts the year after the project year and continues for the depreciation lifetime.

    Args:
        year: The year to compute depreciation expense for
        df: DataFrame containing capital projects with columns:
            - project_year: int - Year project was initiated
            - original_cost: float - Original cost of the project
            - depreciation_lifetime: int - Number of years to depreciate over

    Returns:
        float: Total depreciation expense for the year across all projects
    """
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
    df = df.filter(pl.col("project_type") != "npa", pl.col("project_year") <= year, pl.col("retirement_year") >= year)
    return float(df.select(pl.col("original_cost")).sum().item() * maintenance_cost_pct)


def return_empty_capex_df() -> pl.DataFrame:
    return pl.DataFrame({
        "project_year": pl.Series([], dtype=pl.Int64),
        "project_type": pl.Series([], dtype=pl.Utf8),
        "original_cost": pl.Series([], dtype=pl.Float64),
        "depreciation_lifetime": pl.Series([], dtype=pl.Int64),
        "retirement_year": pl.Series([], dtype=pl.Int64),
    })
