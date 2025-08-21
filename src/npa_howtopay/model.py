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
    # initialize all the state
    gas_ratebase = 0
    electric_ratebase = 0
    num_gas_users = input_params.num_users
    num_electric_users = input_params.num_users

    gas_capex_projects = []
    electric_capex_projects = []

    output_df = pl.DataFrame()

    for year in range(scenario_params.start_year, scenario_params.end_year):
        # INFLATION - probably looks like evolving input_params to current_params
        do_cost_inflation(year, input_params)

        # get the npas for this year
        npas_this_year = get_info_about_projects(npa_projects, year)  # polars groupby year, weighted_sum

        ####### ticket
        # gas capex
        gas_capex_projects.append(
            non_lpp_gas_capex_projects(year, input_params)
        )  # maybe has different depreciation schedule
        gas_capex_projects.append(lpp_gas_capex_projects(year, input_params, npas_this_year))

        ####### ticket
        # electric capex
        electric_capex_projects.append(non_npa_electric_capex_projects(year, input_params))
        electric_capex_projects.append(grid_upgrade_capex_projects(year, input_params, npa_projects))

        # npa capex
        if scenario_params.capex_opex == "capex":
            npa_capex = get_npa_capex_project(npas_this_year)
            if scenario_params.gas_electric == "gas":
                gas_capex_projects.append(npa_capex)
            elif scenario_params.gas_electric == "electric":
                electric_capex_projects.append(npa_capex)

        gas_ratebase = update_ratebase(year, gas_ratebase, gas_capex_projects)
        electric_ratebase = update_ratebase(year, electric_ratebase, electric_capex_projects)

        num_gas_users -= npas_this_year.num_converts

        ####### ticket
        intermediate_columns = compute_blue_columns()  # returns pl.Series

        output_df.append([gas_ratebase, electric_ratebase, intermediate_columns])  # bad syntax

    output_df = compute_bill_costs(output_df, discount_rate)  # appends new columns to output_df


####### ticket
def analyze_scenarios(scenario_runs: dict[ScenarioParams, pl.DataFrame]) -> None:
    pass
