# constants
KWH_PER_THERM = 29.3071

# web app only inputs
npa_num_projects  # shorthand for generating the time series of npa_projects; goes in web app not model
npa_households_per_project  # shorthand for generating the time series of npa_projects; goes in web app not model
npa_pipe_value_per_user  # shorthand for generating the time series of npa_projects; goes in web app not model
npa_pipe_decomm_cost_per_user  # shorthand for generating the time series of npa_projects; goes in web app not model
non_npa_scattershot_electrifiction_users_per_year
stuff_for_producing_ratebase_baseline

# scalar inputs
# split these into separate gas/electric/shared classes so Shiny understands dependencies

num_users
per_user_heating_need
per_user_electric_need
peak_kw_winter_headroom_per_project
peak_kw_summer_headroom_per_project
aircon_percent_adoption_pre_npa
aircon_peak_kw
distribution_cost_per_peak_kw_increase
grid_upgrade_depreciation_lifetime
hp_efficiency
hp_peak_kw
npa_lifetime
npa_install_costs
gas_generation_cost_per_therm
electricity_generation_cost_per_kwh
pipeline_replacement_cost
pipeline_replacement_lifetime
pipeline_maintenance_cost_pct
electric_maintenance_cost_pct
baseline_non_lpp_gas_ratebase_growth
baseline_gas_lpp_costs_per_year
baseline_electric_ratebase_growth
depreciation_lifetime
gas_ror
electric_ror
inflation_rate
cost_inflation_rate

# time series inputs
### maybe these aren't stored in InputParams but in their own class?

npa_projects  # need to define this class
gas_ratebase_baseline
electric_ratebase_baseline
gas_fixed_overhead_costs
electric_fixed_overhead_costs
gas_bau_lpp_costs_per_year
non_npa_converts_per_year

# scenario conditions
gas_electric
capex_opex

####### ticket - flesh this out
class CapexProject:
    project_year: int
    original_cost: float
    depreciation_lifetime: int
    # depreciation_schedule: str # "straight line" or "accelerated"
    @property
    def get_depreciation(self, year: int) -> float:
        if self.project_year < year <= self.project_year + self.depreciation_lifetime:
            return self.original_cost / self.depreciation_lifetime
        else:
            return 0

def non_lpp_gas_capex_projects(year: int, input_params: InputParams) -> list[CapexProject]:
    pass

def update_ratebase(
    year: int, current_ratebase_standard_: float, gas_params: GasParams, shared_params: SharedParams
) -> float:
    pass

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

############ SCRATCH PAD ############
###### WON'T DO ########
# class State:
#     gas_state: GasState
#     electric_state: ElectricState
#     num_users: int
#     num_npa_converts: int

#     gas_ratebase_baseline: float
#     electric_ratebase_baseline: float

# class GasModel:
#     gas_states: dict[int, GasState]

# class GasState:
#     year: int # for safety checks
#     ratebase_baseline: dict
#     ratebase_npa: float
#     npa_capex_original_cost: float # wrong type

#     def compute_new_ratebase_baseline(self, year: int, gas_params: GasParams, shared_params: SharedParams) -> float:
#         return self.ratebase_baseline * (1 + gas_params.baseline_non_lpp_gas_ratebase_growth) + gas_params.gas_bau_lpp_costs_per_year.get(year)

# class ElectricState:
#     pass

# def compute_new_ratebase(state: State, year: int) -> float:
#     pass

# scenario_states =initialize_all_scenarios()
# for year in range(2023, 2053):
#     npas_this_year = get_info_about_projects(npa_projects, year)
#     for scenario in scenario_states:
#         scenario.advance_one_year(year, npas_this_year)

# # do baseline first
# baseline_scenario = initialize_baseline_scenario()
# for year in range(2023, 2053):
#     npas_this_year = <none> # (empty class?)
#     baseline_scenario.advance_one_year(year, npas_this_year)

# for scenario in scenario_states:
#     for year in range(2023, 2053):
#         npas_this_year = get_info_about_projects(npa_projects, year)
#         scenario.advance_one_year(year, npas_this_year)
