import polars as pl
from .params import (
    InputParams,
    ScenarioParams,
    load_scenario_from_yaml,
    GasParams,
    SharedParams,
    TimeSeriesParams,
    KWH_PER_THERM,
)
from . import npa_project as npa
from . import capex_project as cp
from attrs import evolve
from dataclasses import dataclass
from typing import Literal

KWH_PER_THERM = 29.307107


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
    npa_opex: float


def compute_intermediate_cols_gas(
    context: YearContext, input_params: InputParams, ts_params: TimeSeriesParams
) -> pl.DataFrame:
    gas_fixed_overhead_costs = (
        ts_params.gas_fixed_overhead_costs.filter(pl.col("year") == context.year).select(pl.col("cost")).item()
    )
    gas_num_users = input_params.gas.num_users_init - npa.compute_hp_converts_from_df(
        context.year, ts_params.npa_projects, cumulative=True, npa_only=False
    )
    total_usage = gas_num_users * input_params.gas.per_user_heating_need_therms
    costs_volumetric = total_usage * input_params.gas.gas_generation_cost_per_therm
    costs_fixed = gas_fixed_overhead_costs + context.gas_maintenance_cost + context.npa_opex
    total_costs = costs_fixed + costs_volumetric
    revenue_requirement = context.gas_ratebase * input_params.gas.ror + total_costs + context.gas_depreciation_expense

    return pl.DataFrame({
        "year": [context.year],
        "gas_num_users": [gas_num_users],
        "total_gas_usage_therms": [total_usage],
        "gas_costs_volumetric": [costs_volumetric],
        "gas_costs_fixed": [costs_fixed],
        "gas_total_costs": [total_costs],
        "gas_revenue_requirement": [revenue_requirement],
    })


def compute_intermediate_cols_electric(
    context: YearContext, input_params: InputParams, ts_params: TimeSeriesParams
) -> pl.DataFrame:
    electric_fixed_overhead_costs = (
        ts_params.electric_fixed_overhead_costs.filter(pl.col("year") == context.year).select(pl.col("cost")).item()
    )
    total_converts_cumul = npa.compute_hp_converts_from_df(
        context.year, ts_params.npa_projects, cumulative=True, npa_only=False
    )
    electric_num_users = input_params.electric.num_users_init
    total_usage = input_params.electric.num_users_init * input_params.electric.per_user_electric_need_kwh + (
        total_converts_cumul
        * input_params.gas.per_user_heating_need_therms
        * KWH_PER_THERM
        / input_params.electric.hp_efficiency
    )
    costs_volumetric = total_usage * input_params.electric.electricity_generation_cost_per_kwh
    costs_fixed = electric_fixed_overhead_costs + context.electric_maintenance_cost + context.npa_opex
    total_costs = costs_fixed + costs_volumetric
    revenue_requirement = (
        context.electric_ratebase * input_params.electric.ror + total_costs + context.electric_depreciation_expense
    )

    return pl.DataFrame({
        "year": [context.year],
        "electric_num_users": [electric_num_users],
        "total_converts_cumul": [total_converts_cumul],
        "total_electric_usage_kwh": [total_usage],
        "electric_costs_volumetric": [costs_volumetric],
        "electric_costs_fixed": [costs_fixed],
        "electric_total_costs": [total_costs],
        "electric_revenue_requirement": [revenue_requirement],
    })


def compute_bill_costs(
    df: pl.DataFrame,
    input_params: InputParams,
) -> pl.DataFrame:
    start_year = df.select(pl.col("year")).min().item()
    return df.with_columns(
        (
            pl.col("gas_revenue_requirement") / ((pl.col("year") - start_year).pow(input_params.shared.discount_rate))
        ).alias("gas_inflation_adjusted_revenue_requirement"),
        (
            pl.col("electric_revenue_requirement")
            / ((pl.col("year") - start_year).pow(input_params.shared.discount_rate))
        ).alias("electric_inflation_adjusted_revenue_requirement"),
        (pl.col("gas_revenue_requirement") + pl.col("electric_revenue_requirement")).alias("total_revenue_requirement"),
        (
            pl.col("gas_inflation_adjusted_revenue_requirement")
            + pl.col("electric_inflation_adjusted_revenue_requirement")
        ).alias("total_inflation_adjusted_revenue_requirement"),
        (pl.col("gas_inflation_adjusted_revenue_requirement") / pl.col("gas_num_users")).alias("gas_bill_per_user"),
        (pl.col("gas_inflation_adjusted_revenue_requirement") / pl.col("gas_num_users")).alias(
            "nonconverts_gas_bill_per_user"
        ),
        (pl.lit(0)).alias("converts_gas_bill_per_user"),
        (pl.col("electric_inflation_adjusted_revenue_requirement") / pl.col("electric_num_users")).alias(
            "electric_bill_per_user"
        ),
        # =who_pays_electric_fixed_cost_pct*electric_inflation_adjusted_revenue_requirement/electric_num_users
        (
            pl.lit(input_params.electric.fixed_cost_pct)
            * pl.col("electric_inflation_adjusted_revenue_requirement")
            / pl.col("electric_num_users")
        ).alias("electric_fixed_cost_per_user"),
        # =(1 - who_pays_electric_fixed_cost_pct)*electric_inflation_adjusted_revenue_requirement / electric_total_usage
        (
            (
                pl.lit(1 - input_params.electric.fixed_cost_pct)
                * pl.col("electric_inflation_adjusted_revenue_requirement")
            )
            / pl.col("electric_total_usage")
        ).alias("electric_variable_cost_per_kwh"),
        # =electric_per_user_fixed_bill + electric_charge_per_kwh*(per_user_electric_need+per_user_heating_need * KWH_PER_THERM / hp_efficiency)
        (
            pl.col("electric_fixed_cost_per_user")
            + pl.col("electric_variable_cost_per_kwh")
            * (
                input_params.electric.per_user_electric_need_kwh
                + input_params.gas.per_user_heating_need_therms
                * KWH_PER_THERM
                / pl.lit(input_params.electric.hp_efficiency)
            )
        ).alias("converts_electric_bill_per_user"),
        (
            pl.col("electric_fixed_cost_per_user")
            + pl.col("electric_variable_cost_per_kwh") * input_params.electric.per_user_electric_need_kwh
        ).alias("nonconverts_electric_bill_per_user"),
        (pl.col("converts_gas_bill_per_user") + pl.col("converts_electric_bill_per_user")).alias(
            "converts_total_bill_per_user"
        ),
        (pl.col("nonconverts_gas_bill_per_user") + pl.col("nonconverts_electric_bill_per_user")).alias(
            "nonconverts_total_bill_per_user"
        ),
    )


def run_model(scenario_params: ScenarioParams, input_params: InputParams, ts_params: TimeSeriesParams) -> pl.DataFrame:
    gas_ratebase = input_params.gas.ratebase_init
    electric_ratebase = input_params.electric.ratebase_init

    gas_capex_projects = pl.DataFrame()
    electric_capex_projects = pl.DataFrame()

    output_df = pl.DataFrame()

    # synthetic initial capex projects
    gas_initial_capex_projects = cp.get_synthetic_initial_capex_projects(
        start_year=input_params.shared.start_year,
        initial_ratebase=gas_ratebase,
        depreciation_lifetime=input_params.gas.default_depreciation_lifetime,
    )
    electric_initial_capex_projects = cp.get_synthetic_initial_capex_projects(
        start_year=input_params.shared.start_year,
        initial_ratebase=electric_ratebase,
        depreciation_lifetime=input_params.electric.default_depreciation_lifetime,
    )

    for year in range(scenario_params.start_year, scenario_params.end_year):
        # gas capex
        gas_capex_projects = pl.concat(
            [
                gas_capex_projects,
                gas_initial_capex_projects.filter(pl.col("project_year") == year),
                cp.get_non_lpp_gas_capex_projects(
                    year=year,
                    current_ratebase=gas_ratebase,
                    baseline_non_lpp_gas_ratebase_growth=input_params.gas.baseline_non_lpp_ratebase_growth,
                    depreciation_lifetime=input_params.gas.default_depreciation_lifetime,
                ),
                cp.get_lpp_gas_capex_projects(
                    year=year,
                    gas_bau_lpp_costs_per_year=ts_params.gas_bau_lpp_costs_per_year,
                    npa_projects=ts_params.npa_projects,
                    depreciation_lifetime=input_params.gas.lpp_depreciation_lifetime,
                ),
            ],
            how="vertical",
        )

        # electric capex
        electric_capex_projects = pl.concat(
            [
                electric_capex_projects,
                electric_initial_capex_projects.filter(pl.col("project_year") == year),
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
                    distribution_cost_per_peak_kw_increase=input_params.electric.distribution_cost_per_peak_kw_increase,
                    grid_upgrade_depreciation_lifetime=input_params.electric.grid_upgrade_depreciation_lifetime,
                ),
            ],
            how="vertical",
        )

        # npa capex/opex
        if scenario_params.capex_opex == "capex":
            npa_opex = 0.0
            npa_capex = cp.get_npa_capex_projects(
                year, npa_projects, input_params.shared.npa_install_costs, input_params.shared.npa_lifetime
            )
            if scenario_params.gas_electric == "gas":
                gas_capex_projects = gas_capex_projects.pl.concat(npa_capex)
            elif scenario_params.gas_electric == "electric":
                electric_capex_projects = electric_capex_projects.pl.concat(npa_capex)
        elif scenario_params.capex_opex == "opex":
            npa_opex = npa.compute_npa_install_costs_from_df(
                year, ts_params.npa_projects, input_params.shared.npa_install_costs
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
            npa_opex=npa_opex,
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
    output_df = pl.concat([output_df, compute_bill_costs(output_df, input_params)], how="vertical")

    return output_df


####### ticket
def analyze_scenarios(scenario_runs: dict[ScenarioParams, pl.DataFrame]) -> None:
    pass


if __name__ == "__main__":
    scenario_params = ScenarioParams(start_year=2025, end_year=2050, gas_electric="gas", capex_opex="capex")
    input_params = load_scenario_from_yaml("sample")
    ts_params = TimeSeriesParams()
    #             start_year=scenario_params.start_year,
    #             end_year=scenario_params.end_year,
    #             total_num_projects=10,
    #             num_converts_per_project=5,
    #             pipe_value_per_user=1000.0,
    #             pipe_decomm_cost_per_user=100.0,
    #             peak_kw_winter_headroom_per_project=10.0,
    #             peak_kw_summer_headroom_per_project=10.0,
    #             aircon_percent_adoption_pre_npa=0.8,
    #             pipe_decomm_cost_inflation_rate=input_params.shared.cost_inflation_rate,
    #         ),
    #         npa.generate_scattershot_electrification_projects(
    #             start_year=scenario_params.start_year,
    #             end_year=scenario_params.end_year,
    #             total_num_converts=10,
    #         ),
    #     ],
    #     how="vertical",
    # ).sort("year")

    run_model(scenario_params, input_params, ts_params)
