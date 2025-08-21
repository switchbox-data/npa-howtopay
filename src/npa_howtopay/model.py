import polars as pl
from params import InputParams, ScenarioParams

from capex_project import (
    grid_upgrade_capex_projects,
    lpp_gas_capex_projects,
    non_lpp_gas_capex_projects,
    non_npa_electric_capex_projects,
)


def compute_blue_columns(year: int, gas_params: GasParams, shared_params: SharedParams) -> pl.DataFrame:
    gas_usage = input_params.gas_usage_per_user * num_gas_users
    gas_costs_volumetric = gas_usage * input_params.gas_cost_per_therm
    return pl.DataFrame({"year": year, "gas_usage": gas_usage, "gas_costs_volumetric": gas_costs_volumetric})


def run_model(scenario_params: ScenarioParams, input_params: InputParams, npa_projects: pl.DataFrame) -> pl.DataFrame:
    gas_capex_projects = pl.DataFrame()
    electric_capex_projects = pl.DataFrame()

    output_df = pl.DataFrame()

    live_params = input_params

    for year in range(scenario_params.start_year, scenario_params.end_year):
        # INFLATION - probably looks like evolving input_params to current_params
        live_params = do_cost_inflation(year, live_params)

        # get the npas for this year
        npas_this_year = npa_projects.filter(pl.col("year") == year)

        ####### ticket
        # gas capex
        gas_capex_projects = gas_capex_projects.vstack(
            non_lpp_gas_capex_projects(year, input_params)
        )  # maybe has different depreciation schedule
        gas_capex_projects = gas_capex_projects.vstack(lpp_gas_capex_projects(year, input_params, npas_this_year))

        ####### ticket
        # electric capex
        electric_capex_projects = electric_capex_projects.vstack(non_npa_electric_capex_projects(year, input_params))
        electric_capex_projects = electric_capex_projects.vstack(
            grid_upgrade_capex_projects(year, input_params, npa_projects)
        )

        # npa capex
        if scenario_params.capex_opex == "capex":
            npa_capex = get_npa_capex_projects(npas_this_year, year, input_params)
            if scenario_params.gas_electric == "gas":
                gas_capex_projects = gas_capex_projects.vstack(npa_capex)
            elif scenario_params.gas_electric == "electric":
                electric_capex_projects = electric_capex_projects.vstack(npa_capex)

        gas_ratebase = get_ratebase_from_capex_projects(year, gas_capex_projects)
        electric_ratebase = get_ratebase_from_capex_projects(year, electric_capex_projects)

        ## TODO: opex stuff?

        ####### ticket
        intermediate_columns = compute_blue_columns()  # returns pl.Series

        output_df.append([gas_ratebase, electric_ratebase, intermediate_columns])  # bad syntax

    output_df = compute_bill_costs(output_df, discount_rate)  # appends new columns to output_df


####### ticket
def analyze_scenarios(scenario_runs: dict[ScenarioParams, pl.DataFrame]) -> None:
    pass
