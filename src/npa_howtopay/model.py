import polars as pl
from .params import (
    InputParams,
    ScenarioParams,
    load_scenario_from_yaml,
    GasParams,
    SharedParams,
    TimeSeriesParams,
    KWH_PER_THERM,
    COMPARE_COLS,
)
from . import npa_project as npa
from . import capex_project as cp
from attrs import evolve
from dataclasses import dataclass
from typing import Literal, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class YearContext:
    """Context for all values needed in a given year"""

    year: int
    gas_ratebase: float
    electric_ratebase: float
    gas_depreciation_expense: float
    electric_depreciation_expense: float
    gas_maintenance_cost: float
    electric_maintenance_cost: float
    gas_npa_opex: float
    electric_npa_opex: float


def create_scenario_runs(
    start_year: int,
    end_year: int,
    gas_electric: list[Literal["gas", "electric"]],
    capex_opex: list[Literal["capex", "opex"]],
) -> dict[str, ScenarioParams]:
    """Create a dictionary of scenario parameters for different model runs.

    Creates scenarios for business-as-usual (BAU), taxpayer-funded, and combinations of
    gas/electric and capex/opex interventions. Each scenario specifies the time period
    and configuration parameters.

    Args:
        start_year: First year of the scenario analysis
        end_year: Last year of the scenario analysis
        gas_electric: List specifying which utilities to analyze ("gas" and/or "electric")
        capex_opex: List specifying which cost types to analyze ("capex" and/or "opex")

    Returns:
        Dictionary mapping scenario names to ScenarioParams objects containing the
        configuration for that scenario. Includes "bau" and "taxpayer" base scenarios
        plus combinations of gas/electric and capex/opex parameters.
    """
    scenarios = {
        "bau": ScenarioParams(start_year=start_year, end_year=end_year, bau=True),
        "taxpayer": ScenarioParams(start_year=start_year, end_year=end_year, taxpayer=True),
    }

    # Add the regular scenarios
    for ge in gas_electric:
        for co in capex_opex:
            scenarios[f"{ge}_{co}"] = ScenarioParams(
                start_year=start_year, end_year=end_year, gas_electric=ge, capex_opex=co
            )

    return scenarios


def compute_intermediate_cols_gas(
    context: YearContext, input_params: InputParams, ts_params: TimeSeriesParams
) -> pl.DataFrame:
    """Compute intermediate columns for gas utility calculations.

    Calculates gas utility metrics for a given year including:
    - Number of users (accounting for heat pump converts)
    - Total gas usage in therms
    - Fixed and volumetric costs
    - Operating expenses and revenue requirements

    Args:
        context: Year context containing ratebase, depreciation and maintenance costs
        input_params: Input parameters with utility rates and user counts
        ts_params: Time series parameters with NPA projects and overhead costs

    Returns:
        DataFrame with calculated gas utility metrics for the given year
    """
    gas_fixed_overhead_costs = (
        ts_params.gas_fixed_overhead_costs.filter(pl.col("year") == context.year).select(pl.col("cost")).sum().item()
    )
    gas_num_users = input_params.gas.num_users_init - npa.compute_hp_converts_from_df(
        context.year, ts_params.npa_projects, cumulative=True, npa_only=False
    )
    total_usage = gas_num_users * input_params.gas.per_user_heating_need_therms
    costs_volumetric = total_usage * input_params.gas.gas_generation_cost_per_therm(context.year)
    costs_fixed = gas_fixed_overhead_costs + context.gas_maintenance_cost + context.gas_npa_opex
    opex_costs = costs_fixed + costs_volumetric
    revenue_requirement = context.gas_ratebase * input_params.gas.ror + opex_costs + context.gas_depreciation_expense

    return pl.DataFrame({
        "year": [context.year],
        "gas_num_users": [gas_num_users],
        "total_gas_usage_therms": [total_usage],
        "gas_costs_volumetric": [costs_volumetric],
        "gas_costs_fixed": [costs_fixed],
        "gas_opex_costs": [opex_costs],
        "gas_revenue_requirement": [revenue_requirement],
    })


def compute_intermediate_cols_electric(
    context: YearContext, input_params: InputParams, ts_params: TimeSeriesParams
) -> pl.DataFrame:
    """Compute intermediate columns for electric utility calculations.

    Calculates electric utility metrics for a given year including:
    - Number of users and cumulative heat pump converts
    - Total electric usage in kWh (base usage + heating from converts)
    - Fixed and volumetric costs
    - Operating expenses and revenue requirements

    Args:
        context: Year context containing ratebase, depreciation and maintenance costs
        input_params: Input parameters with utility rates and user counts
        ts_params: Time series parameters with NPA projects and overhead costs

    Returns:
        DataFrame with calculated electric utility metrics for the given year
    """
    electric_fixed_overhead_costs = (
        ts_params.electric_fixed_overhead_costs.filter(pl.col("year") == context.year)
        .select(pl.col("cost"))
        .sum()
        .item()
    )
    total_converts_cumul = npa.compute_hp_converts_from_df(
        context.year, ts_params.npa_projects, cumulative=True, npa_only=False
    )
    electric_num_users = input_params.electric.num_users_init
    added_usage = (
        total_converts_cumul
        * input_params.gas.per_user_heating_need_therms
        * KWH_PER_THERM
        / input_params.electric.hp_efficiency
        + total_converts_cumul
        * input_params.gas.per_user_water_heating_need_therms
        * KWH_PER_THERM
        / input_params.electric.water_heater_efficiency
    )
    total_usage = input_params.electric.num_users_init * input_params.electric.per_user_electric_need_kwh + added_usage
    costs_volumetric = total_usage * input_params.electric.electricity_generation_cost_per_kwh(context.year)
    costs_fixed = electric_fixed_overhead_costs + context.electric_maintenance_cost + context.electric_npa_opex
    opex_costs = costs_fixed + costs_volumetric
    revenue_requirement = (
        context.electric_ratebase * input_params.electric.ror + opex_costs + context.electric_depreciation_expense
    )

    return pl.DataFrame({
        "year": [context.year],
        "electric_num_users": [electric_num_users],
        "total_converts_cumul": [total_converts_cumul],
        "electric_added_usage_kwh": [added_usage],
        "total_electric_usage_kwh": [total_usage],
        "electric_costs_volumetric": [costs_volumetric],
        "electric_costs_fixed": [costs_fixed],
        "electric_opex_costs": [opex_costs],
        "electric_revenue_requirement": [revenue_requirement],
    })


# Helper functions for bill cost calculations
def inflation_adjust_revenue_requirement(revenue_req: float, year: int, start_year: int, discount_rate: float) -> float:
    """Adjust revenue requirement for inflation using discount rate."""
    if year < start_year:
        raise ValueError(f"Year {year} cannot be before start year {start_year}")
    return revenue_req / ((1 + discount_rate) ** (year - start_year))


# Average bill per user
def calculate_avg_bill_per_user(inflation_adjusted_revenue: float, num_users: int) -> float:
    """Calculate the average bill per user by dividing total revenue by number of users.

    Args:
        inflation_adjusted_revenue: Total revenue adjusted for inflation
        num_users: Total number of users to divide revenue among

    Returns:
        float: Average bill amount per user
    """
    return inflation_adjusted_revenue / num_users


# Electric bills
# Fixed charge per user
def calculate_electric_fixed_charge_per_user(fixed_charge: float) -> float:
    """Return electric fixed charge per user. Currently a user defined constant"""
    return fixed_charge


# Volumetric bill per user
def calculate_electric_variable_tariff_per_kwh(
    electric_infl_adj_revenue: float, total_electric_usage_kwh: float, fixed_charge: float, num_users: int
) -> float:
    """Calculate electric variable cost per kWh.

    Args:
        electric_infl_adj_revenue: Total electric revenue adjusted for inflation
        total_electric_usage_kwh: Total electric usage in kWh
        fixed_charge: Fixed charge per user
        num_users: Number of users

    Returns:
        float: Variable cost per kWh calculated by subtracting total fixed charges
              from revenue and dividing by total usage
    """
    return (electric_infl_adj_revenue - num_users * fixed_charge) / total_electric_usage_kwh


def calculate_gas_fixed_charge_per_user(fixed_charge: float) -> float:
    """Return gas fixed cost per user. Currently a user defined constant"""
    return fixed_charge


def calculate_gas_variable_tariff_per_therm(
    gas_infl_adj_revenue: float,
    total_gas_usage_therms: float,
    fixed_charge: float,
    num_users: int,
) -> float:
    """Calculate gas variable cost per therm.

    Args:
        gas_infl_adj_revenue: Total gas revenue adjusted for inflation
        total_gas_usage_therms: Total gas usage in therms
        fixed_charge: Fixed charge per user
        num_users: Number of users

    Returns:
        float: Variable cost per therm calculated by subtracting total fixed charges
              from revenue and dividing by total usage
    """
    return (gas_infl_adj_revenue - num_users * fixed_charge) / total_gas_usage_therms


def calculate_nonconverts_gas_bill_per_user(
    gas_fixed_charge: float, gas_variable_tariff: float, per_user_heating_need: float
) -> float:
    """Calculate gas bill per user for nonconverts.

    Args:
        gas_fixed_charge: Fixed charge per user
        gas_variable_tariff: Variable tariff per therm
        per_user_heating_need: Heating need per user

    Returns:
        float: Gas bill per user for nonconverts
    """
    return gas_fixed_charge + gas_variable_tariff * per_user_heating_need


def calculate_converts_electric_bill_per_user(
    electric_fixed_charge: float,
    electric_variable_tariff: float,
    per_user_electric_need: float,
    per_user_heating_need: float,
    per_user_water_heating_need: float,
    hp_efficiency: float,
    water_heater_efficiency: float,
) -> float:
    """Calculate electric bill per user for converts (includes heating).

    Args:
        electric_fixed_charge: Fixed charge per user
        electric_variable_tariff: Variable tariff per kWh
        per_user_electric_need: Electric need per user
        per_user_heating_need: Heating need per user (therms)
        per_user_water_heating_need: Water heating need per user (therms)
        hp_efficiency: Heat pump efficiency
        water_heater_efficiency: Water heater efficiency

    Returns:
        float: Electric bill per user for converts
    """
    add_on_usage = (
        per_user_heating_need * KWH_PER_THERM / hp_efficiency
        + per_user_water_heating_need * KWH_PER_THERM / water_heater_efficiency
    )
    return electric_fixed_charge + electric_variable_tariff * (per_user_electric_need + add_on_usage)


def calculate_nonconverts_electric_bill_per_user(
    electric_fixed_charge: float, electric_variable_tariff: float, per_user_electric_need: float
) -> float:
    """Calculate electric bill per user for nonconverts (no heating).

    Args:
        electric_fixed_charge: Fixed charge per user
        electric_variable_tariff: Variable tariff per kWh
        per_user_electric_need: Electric need per user

    Returns:
        float: Electric bill per user for nonconverts
    """
    return electric_fixed_charge + electric_variable_tariff * per_user_electric_need


# Total Energy bills
def calculate_converts_total_bill_per_user(converts_gas_bill: float, converts_electric_bill: float) -> float:
    """Calculate total bill per user for converts (gas + electric).

    Args:
        converts_gas_bill: Gas bill per user for converts
        converts_electric_bill: Electric bill per user for converts

    Returns:
        float: Total bill per user for converts
    """
    return converts_gas_bill + converts_electric_bill


def calculate_nonconverts_total_bill_per_user(nonconverts_gas_bill: float, nonconverts_electric_bill: float) -> float:
    """Calculate total bill per user for nonconverts (gas + electric).

    Args:
        nonconverts_gas_bill: Gas bill per user for nonconverts
        nonconverts_electric_bill: Electric bill per user for nonconverts

    Returns:
        float: Total bill per user for nonconverts
    """
    return nonconverts_gas_bill + nonconverts_electric_bill


def compute_bill_costs(
    df: pl.DataFrame,
    input_params: InputParams,
) -> pl.DataFrame:
    """Compute bill costs and tariffs for gas and electric utilities.

    Takes a DataFrame with revenue requirements and usage data and computes:
    - Inflation adjusted revenue requirements for gas and electric
    - Fixed charges per user and Variable tariffs per therm (gas) and kWh (electric)
    - Utility bills per user for converts and nonconverts
    - Total bills per user for converts and nonconverts

    Args:
        df: DataFrame containing revenue requirements and usage data
        input_params: Input parameters containing utility rates and user counts

    Returns:
        DataFrame with added columns for adjusted revenue requirements and tariffs
    """
    start_year = df.select(pl.col("year")).min().item()

    # Create inflation-adjusted revenue requirement columns
    df = df.with_columns([
        pl.struct(["gas_revenue_requirement", "year"])
        .map_elements(
            lambda x: inflation_adjust_revenue_requirement(
                x["gas_revenue_requirement"], x["year"], start_year, input_params.shared.discount_rate
            ),
            return_dtype=pl.Float64,
        )
        .alias("gas_inflation_adjusted_revenue_requirement"),
        pl.struct(["electric_revenue_requirement", "year"])
        .map_elements(
            lambda x: inflation_adjust_revenue_requirement(
                x["electric_revenue_requirement"], x["year"], start_year, input_params.shared.discount_rate
            ),
            return_dtype=pl.Float64,
        )
        .alias("electric_inflation_adjusted_revenue_requirement"),
        (pl.col("gas_revenue_requirement") + pl.col("electric_revenue_requirement")).alias("total_revenue_requirement"),
    ])

    # Create gas and electric tariffs columns (and total inflation adjusted revenue requirement)
    df = df.with_columns([
        (
            pl.col("gas_inflation_adjusted_revenue_requirement")
            + pl.col("electric_inflation_adjusted_revenue_requirement")
        ).alias("total_inflation_adjusted_revenue_requirement"),
        pl.struct(["gas_inflation_adjusted_revenue_requirement", "total_gas_usage_therms"])
        .map_elements(
            lambda x: calculate_gas_variable_tariff_per_therm(
                x["gas_inflation_adjusted_revenue_requirement"],
                x["total_gas_usage_therms"],
                input_params.gas.user_bill_fixed_charge,
                input_params.gas.num_users_init,
            ),
            return_dtype=pl.Float64,
        )
        .alias("gas_variable_tariff_per_therm"),
        pl.struct(["electric_inflation_adjusted_revenue_requirement", "total_electric_usage_kwh"])
        .map_elements(
            lambda x: calculate_electric_variable_tariff_per_kwh(
                x["electric_inflation_adjusted_revenue_requirement"],
                x["total_electric_usage_kwh"],
                input_params.electric.user_bill_fixed_charge,
                input_params.electric.num_users_init,
            ),
            return_dtype=pl.Float64,
        )
        .alias("electric_variable_tariff_per_kwh"),
        pl.lit(
            calculate_electric_fixed_charge_per_user(
                input_params.electric.user_bill_fixed_charge,
            )
        ).alias("electric_fixed_charge_per_user"),
        pl.lit(
            calculate_gas_fixed_charge_per_user(
                input_params.gas.user_bill_fixed_charge,
            )
        ).alias("gas_fixed_charge_per_user"),
    ])

    # Create per-user gas bill columns and total inflation adjusted revenue requirement
    df = df.with_columns([
        pl.struct(["gas_inflation_adjusted_revenue_requirement", "gas_num_users"])
        .map_elements(
            lambda x: calculate_avg_bill_per_user(x["gas_inflation_adjusted_revenue_requirement"], x["gas_num_users"]),
            return_dtype=pl.Float64,
        )
        .alias("gas_avg_bill_per_user"),
        pl.struct(["gas_fixed_charge_per_user", "gas_variable_tariff_per_therm"])
        .map_elements(
            lambda x: calculate_nonconverts_gas_bill_per_user(
                x["gas_fixed_charge_per_user"],
                x["gas_variable_tariff_per_therm"],
                input_params.gas.per_user_heating_need_therms,
            ),
            return_dtype=pl.Float64,
        )
        .alias("gas_nonconverts_bill_per_user"),
        pl.lit(0.0).alias("gas_converts_bill_per_user"),
    ])

    # Create converts and nonconverts electric bills
    df = df.with_columns([
        pl.struct(["electric_inflation_adjusted_revenue_requirement", "electric_num_users"])
        .map_elements(
            lambda x: calculate_avg_bill_per_user(
                x["electric_inflation_adjusted_revenue_requirement"], x["electric_num_users"]
            ),
            return_dtype=pl.Float64,
        )
        .alias("electric_avg_bill_per_user"),
        pl.struct(["electric_fixed_charge_per_user", "electric_variable_tariff_per_kwh"])
        .map_elements(
            lambda x: calculate_converts_electric_bill_per_user(
                x["electric_fixed_charge_per_user"],
                x["electric_variable_tariff_per_kwh"],
                input_params.electric.per_user_electric_need_kwh,
                input_params.gas.per_user_heating_need_therms,
                input_params.gas.per_user_water_heating_need_therms,
                input_params.electric.hp_efficiency,
                input_params.electric.water_heater_efficiency,
            ),
            return_dtype=pl.Float64,
        )
        .alias("electric_converts_bill_per_user"),
        pl.struct(["electric_fixed_charge_per_user", "electric_variable_tariff_per_kwh"])
        .map_elements(
            lambda x: calculate_nonconverts_electric_bill_per_user(
                x["electric_fixed_charge_per_user"],
                x["electric_variable_tariff_per_kwh"],
                input_params.electric.per_user_electric_need_kwh,
            ),
            return_dtype=pl.Float64,
        )
        .alias("electric_nonconverts_bill_per_user"),
    ])

    # Create total bill calculations for converts and nonconverts
    df = df.with_columns([
        pl.struct(["gas_converts_bill_per_user", "electric_converts_bill_per_user"])
        .map_elements(
            lambda x: calculate_converts_total_bill_per_user(
                x["gas_converts_bill_per_user"], x["electric_converts_bill_per_user"]
            ),
            return_dtype=pl.Float64,
        )
        .alias("converts_total_bill_per_user"),
        pl.struct(["gas_nonconverts_bill_per_user", "electric_nonconverts_bill_per_user"])
        .map_elements(
            lambda x: calculate_nonconverts_total_bill_per_user(
                x["gas_nonconverts_bill_per_user"], x["electric_nonconverts_bill_per_user"]
            ),
            return_dtype=pl.Float64,
        )
        .alias("nonconverts_total_bill_per_user"),
    ])

    return df


def run_model(scenario_params: ScenarioParams, input_params: InputParams, ts_params: TimeSeriesParams) -> pl.DataFrame:
    # in the business-as-usual scenario, we don't have any npa projects. We maintain the scattershot electrification which will still reduce the number of gas customers and total gas usage but will not trigger grid upgrade or capex/opex for either utility.
    if scenario_params.bau:
        ts_params = evolve(ts_params, npa_projects=npa.return_empty_npa_df())

    gas_ratebase = input_params.gas.ratebase_init
    electric_ratebase = input_params.electric.ratebase_init

    # these will be updated depending on the scenario
    gas_npa_opex = 0.0
    electric_npa_opex = 0.0

    output_df = pl.DataFrame()

    # synthetic initial capex projects
    if gas_ratebase > 0:
        gas_capex_projects = cp.get_synthetic_initial_capex_projects(
            start_year=input_params.shared.start_year,
            initial_ratebase=gas_ratebase,
            depreciation_lifetime=input_params.gas.default_depreciation_lifetime,
        )
    else:
        gas_capex_projects = cp.return_empty_capex_df()
    if electric_ratebase > 0:
        electric_capex_projects = cp.get_synthetic_initial_capex_projects(
            start_year=input_params.shared.start_year,
            initial_ratebase=electric_ratebase,
            depreciation_lifetime=input_params.electric.default_depreciation_lifetime,
        )
    else:
        electric_capex_projects = cp.return_empty_capex_df()

    for year in range(scenario_params.start_year, scenario_params.end_year):
        # gas capex
        gas_capex_projects = pl.concat(
            [
                gas_capex_projects,
                cp.get_non_lpp_gas_capex_projects(
                    year=year,
                    current_ratebase=gas_ratebase,
                    baseline_non_lpp_gas_ratebase_growth=input_params.gas.baseline_non_lpp_ratebase_growth,
                    depreciation_lifetime=input_params.gas.non_lpp_depreciation_lifetime,
                ),
                cp.get_lpp_gas_capex_projects(
                    year=year,
                    gas_bau_lpp_costs_per_year=ts_params.gas_bau_lpp_costs_per_year,
                    npa_projects=ts_params.npa_projects,
                    depreciation_lifetime=input_params.gas.pipeline_depreciation_lifetime,
                ),
            ],
            how="vertical",
        )

        # electric capex
        electric_capex_projects = pl.concat(
            [
                electric_capex_projects,
                cp.get_non_npa_electric_capex_projects(
                    year=year,
                    current_ratebase=electric_ratebase,
                    baseline_electric_ratebase_growth=input_params.electric.baseline_non_npa_ratebase_growth,
                    depreciation_lifetime=input_params.electric.default_depreciation_lifetime,
                ),
                cp.get_grid_upgrade_capex_projects(
                    year=year,
                    npa_projects=ts_params.npa_projects,
                    peak_hp_kw=input_params.electric.hp_peak_kw,
                    peak_aircon_kw=input_params.electric.aircon_peak_kw,
                    distribution_cost_per_peak_kw_increase=input_params.electric.distribution_cost_per_peak_kw_increase(
                        year
                    ),
                    grid_upgrade_depreciation_lifetime=input_params.electric.grid_upgrade_depreciation_lifetime,
                ),
            ],
            how="vertical",
        )

        # update npa capex/opex
        if scenario_params.capex_opex == "capex":
            # add npa capex
            npa_capex = cp.get_npa_capex_projects(
                year,
                ts_params.npa_projects,
                input_params.shared.npa_install_costs(year),
                int(input_params.shared.npa_lifetime),
            )
            if scenario_params.gas_electric == "gas":
                gas_capex_projects = pl.concat([gas_capex_projects, npa_capex], how="vertical")
            elif scenario_params.gas_electric == "electric":
                electric_capex_projects = pl.concat([electric_capex_projects, npa_capex], how="vertical")
        elif scenario_params.capex_opex == "opex":
            if scenario_params.gas_electric == "gas":
                gas_npa_opex = npa.compute_npa_install_costs_from_df(
                    year, ts_params.npa_projects, input_params.shared.npa_install_costs(year)
                )
            elif scenario_params.gas_electric == "electric":
                electric_npa_opex = npa.compute_npa_install_costs_from_df(
                    year, ts_params.npa_projects, input_params.shared.npa_install_costs(year)
                )

        # calculate ratebase
        gas_ratebase = cp.compute_ratebase_from_capex_projects(year, gas_capex_projects)
        electric_ratebase = cp.compute_ratebase_from_capex_projects(year, electric_capex_projects)

        # calculate depreciation expense
        gas_depreciation_expense = cp.compute_depreciation_expense_from_capex_projects(year, gas_capex_projects)
        electric_depreciation_expense = cp.compute_depreciation_expense_from_capex_projects(
            year, electric_capex_projects
        )

        # calculate maintanence costs
        gas_maintanence_costs = cp.compute_maintanence_costs(
            year, gas_capex_projects, input_params.gas.pipeline_maintenance_cost_pct
        )
        electric_maintanence_costs = cp.compute_maintanence_costs(
            year, electric_capex_projects, input_params.electric.electric_maintenance_cost_pct
        )

        # Create context object with all values needed for this year
        context = YearContext(
            year=year,
            gas_ratebase=gas_ratebase,
            electric_ratebase=electric_ratebase,
            gas_depreciation_expense=gas_depreciation_expense,
            electric_depreciation_expense=electric_depreciation_expense,
            gas_maintenance_cost=gas_maintanence_costs,
            electric_maintenance_cost=electric_maintanence_costs,
            gas_npa_opex=gas_npa_opex,
            electric_npa_opex=electric_npa_opex,
        )

        # Calculate intermediate columns for both gas and electric
        intermediate_df_gas = compute_intermediate_cols_gas(context, input_params, ts_params)
        intermediate_df_electric = compute_intermediate_cols_electric(context, input_params, ts_params)

        # Build output row for this year with all intermediate calculations
        year_output = pl.DataFrame({
            "year": [year],
            "gas_ratebase": [gas_ratebase],
            "electric_ratebase": [electric_ratebase],
            "gas_depreciation_expense": [gas_depreciation_expense],
            "electric_depreciation_expense": [electric_depreciation_expense],
            "gas_maintenance_costs": [gas_maintanence_costs],
            "electric_maintenance_costs": [electric_maintanence_costs],
        })

        # Join with intermediate calculations
        year_output = year_output.join(intermediate_df_gas, on="year", how="left")
        year_output = year_output.join(intermediate_df_electric, on="year", how="left")

        output_df = pl.concat([output_df, year_output], how="vertical")

    # appends new columns to output_df
    results_df = compute_bill_costs(output_df, input_params)

    return results_df


def create_delta_bau_df(results_df: dict[str, pl.DataFrame], compare_cols_all: list[str]) -> pl.DataFrame:
    bau_df = results_df["bau"].select(["year"] + compare_cols_all)

    # Default mapping: most columns compare against themselves in BAU
    column_mappings = {col: col for col in compare_cols_all}

    # Override special cases: converts columns compare against nonconverts in BAU
    special_cases = {
        "converts_total_bill_per_user": "nonconverts_total_bill_per_user",
        "electric_converts_bill_per_user": "electric_nonconverts_bill_per_user",
        "gas_converts_bill_per_user": "gas_nonconverts_bill_per_user",
    }
    column_mappings.update(special_cases)

    # Create comparison DataFrames for each scenario
    comparison_dfs = {}
    for scenario_name, scenario_df in results_df.items():
        if scenario_name == "bau":
            continue  # Skip BAU itself

        # Join with BAU columns
        bau_cols_to_join = ["year"] + list(set(column_mappings.values()))
        bau_renames = {col: f"bau_{col}" for col in set(column_mappings.values())}

        comparison_df = scenario_df.join(
            bau_df.select(bau_cols_to_join).rename(bau_renames),
            on="year",
        )

        # Create comparison columns
        comparison_cols = []
        for scenario_col, bau_col in column_mappings.items():
            if scenario_col in compare_cols_all:
                comparison_cols.append(pl.col(scenario_col).sub(pl.col(f"bau_{bau_col}")))

        # Select final columns
        comparison_df = comparison_df.select(["year", *comparison_cols])
        comparison_dfs[scenario_name] = comparison_df

    delta_bau_df = pl.concat(
        [df.with_columns(pl.lit(scenario_id).alias("scenario_id")) for scenario_id, df in comparison_dfs.items()],
        how="vertical",
    )
    return delta_bau_df


def analyze_scenarios(
    scenario_runs: dict[str, ScenarioParams], input_params: InputParams, ts_params: TimeSeriesParams
) -> tuple[dict[str, pl.DataFrame], pl.DataFrame]:
    results_df = {}
    for scenario_name, scenario_params in scenario_runs.items():
        logger.info(f"Running scenario: {scenario_name}")
        results_df[scenario_name] = run_model(scenario_params, input_params, ts_params)

    return results_df, create_delta_bau_df(results_df, COMPARE_COLS)
