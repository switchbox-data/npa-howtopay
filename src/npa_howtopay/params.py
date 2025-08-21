import polars as pl
from attrs import define
from npa_project import NpaProject

# scalar inputs
# split these into separate gas/electric/shared classes so Shiny understands dependencies


@define
class InputParams:
    num_users: int
    per_user_heating_need: float
    per_user_electric_need: float
    peak_kw_winter_headroom_per_project: float
    peak_kw_summer_headroom_per_project: float
    aircon_percent_adoption_pre_npa: float
    aircon_peak_kw: float
    distribution_cost_per_peak_kw_increase: float
    grid_upgrade_depreciation_lifetime: float
    hp_efficiency: float
    hp_peak_kw: float
    npa_lifetime: float
    npa_install_costs: float
    gas_generation_cost_per_therm: float
    electricity_generation_cost_per_kwh: float
    pipeline_replacement_cost: float
    pipeline_replacement_lifetime: float
    pipeline_maintenance_cost_pct: float
    electric_maintenance_cost_pct: float
    baseline_non_lpp_gas_ratebase_growth: float
    baseline_gas_lpp_costs_per_year: float
    baseline_electric_ratebase_growth: float
    depreciation_lifetime: float
    gas_ror: float
    electric_ror: float
    inflation_rate: float
    cost_inflation_rate: float

    # time series inputs
    ### maybe these aren't stored in InputParams but in their own class?

    npa_projects: list[NpaProject]
    gas_ratebase_baseline: pl.Series
    electric_ratebase_baseline: pl.Series
    gas_fixed_overhead_costs: pl.Series
    electric_fixed_overhead_costs: pl.Series
    gas_bau_lpp_costs_per_year: pl.Series
    non_npa_converts_per_year: pl.Series


@define
class ScenarioParams:
    gas_electric: str  # add validation
    capex_opex: str
