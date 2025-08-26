import polars as pl
from .params import InputParams, ScenarioParams, load_scenario_from_yaml, KWH_PER_THERM, TimeSeriesParams

# import sys
# sys.path.append('/workspaces/npa-howtopay')
import capex_project as cp
import npa_project as npa


def compute_intermediate_cols(
    year: int,
    input_params: InputParams,
    ts_params: TimeSeriesParams,
    gas_electric: Literal["gas", "electric"],
) -> pl.DataFrame:
    # TODO: implement this
    if gas_electric == "gas":
        num_gas_users = input_params.gas.num_users_init - npa.compute_num_converts_from_df(ts_params.npa_projects, year)
        total_usage = num_gas_users * input_params.gas.per_user_heating_need_therms
        # total_ratebase = gas_ratebase
        costs_volumetric = total_usage * input_params.gas.gas_generation_cost_per_therm
        costs_fixed = (
            ts_params.gas_fixed_overhead_costs + gas_maintenance_cost + npa_opex
        )  # npa_opex is 0 if scenario_params.capex_opex == "capex" OR gas_electric == "electric"
        # costs_depreciation = gas_depreciation_expense
        total_costs = costs_fixed + costs_volumetric
        revenue_requirement = gas_total_ratebase * input_params.gas.ror + total_costs + gas_costs_depreciation

    if gas_electric == "electric":
        total_converts_cumul = npa.compute_num_converts_from_df(ts_params.npa_projects, year)
        total_usage = input_params.electric.num_users_init * input_params.electric.per_user_electric_need_kwh + (
            total_converts_cumul
            * input_params.gas.per_user_heating_need_therms
            * KWH_PER_THERM
            / input_params.electric.hp_efficiency
        )
        # total_ratebase = electric_ratebase
        costs_volumetric = total_usage * input_params.electric.electricity_generation_cost_per_kwh
        costs_fixed = (
            ts_params.electric_fixed_overhead_costs + electric_maintenance_cost + npa_opex
        )  # npa_opex is 0 if scenario_params.capex_opex == "capex" OR gas_electric == "gas"
        # costs_depreciation = electric_depreciation_expense
        total_costs = costs_fixed + costs_volumetric
        revenue_requirement = (
            electric_total_ratebase * input_params.electric.ror + total_costs + electric_costs_depreciation
        )

    # gas_usage = input_params.gas_usage_per_user * num_gas_users
    # gas_costs_volumetric = gas_usage * input_params.gas_cost_per_therm
    # return pl.DataFrame({"year": year, "gas_usage": gas_usage, "gas_costs_volumetric": gas_costs_volumetric})
    pass  # type: ignore


def run_model(scenario_params: ScenarioParams, input_params: InputParams, npa_projects: pl.DataFrame) -> pl.DataFrame:
    gas_ratebase = input_params.gas.ratebase_init
    electric_ratebase = input_params.electric.ratebase_init

    gas_capex_projects = pl.DataFrame()
    electric_capex_projects = pl.DataFrame()

    output_df = pl.DataFrame()

    live_params = input_params

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
        # TODO: INFLATION - probably looks like evolving input_params to current_params
        live_params = do_cost_inflation(year, live_params)  # type: ignore

        # get the npas for this year
        npas_this_year = npa_projects.filter(pl.col("year") == year)

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
                    gas_bau_lpp_costs_per_year=input_params.gas_bau_lpp_costs_per_year,
                    npas_this_year=npas_this_year,
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
                    npas_this_year=npas_this_year,
                    peak_hp_kw=input_params.electric.hp_peak_kw,
                    peak_aircon_kw=input_params.electric.aircon_peak_kw,
                    distribution_cost_per_peak_kw_increase=input_params.electric.distribution_cost_per_peak_kw_increase,
                    grid_upgrade_depreciation_lifetime=input_params.electric.grid_upgrade_depreciation_lifetime,
                ),
            ],
            how="vertical",
        )

        # npa capex
        if scenario_params.capex_opex == "capex":
            npa_capex = cp.get_npa_capex_projects(
                npas_this_year, year, input_params.shared.npa_install_costs, input_params.shared.npa_lifetime
            )
            if scenario_params.gas_electric == "gas":
                gas_capex_projects = gas_capex_projects.pl.concat(npa_capex)
            elif scenario_params.gas_electric == "electric":
                electric_capex_projects = electric_capex_projects.pl.concat(npa_capex)

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

        ## TODO: opex stuff?

        # TODO: ticket
        intermediate_df_gas = compute_intermediate_cols(year, input_params, scenario_params, "gas")
        intermediate_df_electric = compute_intermediate_cols(year, input_params, scenario_params, "electric")

        # Build output row for this year
        year_output = pl.DataFrame({
            "year": [year],
            "gas_ratebase": [gas_ratebase],
            "electric_ratebase": [electric_ratebase],
            # Add other columns as needed
        })

        output_df = pl.concat([output_df, year_output], how="vertical")

    output_df = compute_bill_costs(output_df, input_params.shared.discount_rate)  # appends new columns to output_df

    return output_df


####### ticket
def analyze_scenarios(scenario_runs: dict[ScenarioParams, pl.DataFrame]) -> None:
    pass


if __name__ == "__main__":
    scenario_params = ScenarioParams(start_year=2025, end_year=2050, gas_electric="gas", capex_opex="capex")
    input_params = load_scenario_from_yaml("sample")
    npa_projects = pl.DataFrame()  # TODO
    run_model(scenario_params, input_params, npa_projects)
