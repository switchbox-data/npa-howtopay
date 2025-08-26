import polars as pl
from .params import InputParams, ScenarioParams, load_scenario_from_yaml, GasParams, SharedParams

import capex_project as cp


def compute_blue_columns(year: int, gas_params: GasParams, shared_params: SharedParams) -> pl.DataFrame:
    # TODO: implement this
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
                    baseline_non_lpp_gas_ratebase_growth=input_params.gas.ratebase_growth,
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
                    baseline_electric_ratebase_growth=input_params.electric.ratebase_growth,
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

        gas_ratebase = cp.compute_ratebase_from_capex_projects(year, gas_capex_projects)
        electric_ratebase = cp.compute_ratebase_from_capex_projects(year, electric_capex_projects)

        ## TODO: opex stuff?

        ####### TODO: ticket
        intermediate_columns = compute_blue_columns()  # returns pl.DataFrame

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
