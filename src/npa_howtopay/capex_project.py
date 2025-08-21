from attrs import define
from params import InputParams

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
        "project_year": range(start_year, start_year + depreciation_lifetime),
        "original_cost": est_original_cost_per_year,
        "depreciation_lifetime": depreciation_lifetime,
    })


def get_non_lpp_gas_capex_projects(year: int, input_params: InputParams) -> pl.DataFrame:
    pass


def get_lpp_gas_capex_projects(year: int, input_params: InputParams, npas_this_year: NpaProject) -> pl.DataFrame:
    pass


def get_non_npa_electric_capex_projects(year: int, input_params: InputParams) -> pl.DataFrame:
    pass


def get_grid_upgrade_capex_projects(year: int, input_params: InputParams, npas_projects: pl.DataFrame) -> pl.DataFrame:
    pass


def get_npa_capex_projects(year: int, input_params: InputParams, npas_projects: pl.DataFrame) -> pl.DataFrame:
    pass


# functions for computing things given a dataframe of capex projects
def compute_ratebase_from_capex_projects(df: pl.DataFrame, year: int) -> float:
    pass


def compute_depreciation_expense_from_capex_projects(df: pl.DataFrame, year: int) -> float:
    pass
