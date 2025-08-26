from attrs import define, field, validators
from typing import Literal
import yaml
import polars as pl

# from npa_project import NpaProject
import os

# Get the directory where this file is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")

KWH_PER_THERM = 29.3071


@define
class GasParams:
    baseline_non_lpp_ratebase_growth: float
    default_depreciation_lifetime: int
    gas_generation_cost_per_therm: float
    lpp_depreciation_lifetime: int
    non_lpp_depreciation_lifetime: int
    num_users_init: int
    per_user_heating_need_therms: float
    pipeline_maintenance_cost_pct: float
    pipeline_replacement_cost: float
    pipeline_replacement_lifetime: float
    ratebase_init: float
    ror: float


@define
class ElectricParams:
    aircon_peak_kw: float
    baseline_non_npa_ratebase_growth: float
    default_depreciation_lifetime: int
    distribution_cost_per_peak_kw_increase: float
    electric_maintenance_cost_pct: float
    electricity_generation_cost_per_kwh: float
    grid_upgrade_depreciation_lifetime: int
    hp_efficiency: float
    hp_peak_kw: float
    num_users_init: int
    per_user_electric_need_kwh: float
    ratebase_init: float
    ror: float


@define
class SharedParams:
    cost_inflation_rate: float
    discount_rate: float
    npa_install_costs: float
    npa_lifetime: float
    start_year: int


@define
class InputParams:
    gas: GasParams
    electric: ElectricParams
    shared: SharedParams


# time series inputs
# maybe these aren't stored in InputParams but in their own class?
@define
class TimeSeriesParams:  # TODO: think through this more
    npa_projects: pl.DataFrame
    # gas_ratebase_baseline: pl.Series
    # electric_ratebase_baseline: pl.Series # I think we dont need these now
    gas_fixed_overhead_costs: pl.DataFrame
    electric_fixed_overhead_costs: pl.DataFrame
    gas_bau_lpp_costs_per_year: pl.DataFrame
    non_npa_converts_per_year: pl.DataFrame


@define
class ScenarioParams:
    gas_electric: Literal["gas", "electric"] = field(validator=validators.in_(["gas", "electric"]))
    capex_opex: Literal["capex", "opex"] = field(validator=validators.in_(["capex", "opex"]))
    end_year: int
    start_year: int


def _load_params_from_yaml(yaml_path: str) -> InputParams:
    with open(yaml_path) as f:
        config = yaml.safe_load(f)

    return InputParams(
        gas=GasParams(**config["gas"]),
        electric=ElectricParams(**config["electric"]),
        shared=SharedParams(**config["shared"]),
    )


def load_scenario_from_yaml(run_name: str, data_dir: str = "data") -> InputParams:
    """Load default parameters for a specific run_name from its YAML file"""
    yaml_path = f"{data_dir}/{run_name}.yaml"
    return _load_params_from_yaml(yaml_path)


def get_available_runs(data_dir: str = "data") -> list[str]:
    """Get list of available run_names from YAML files"""
    import os
    import glob

    yaml_files = glob.glob(f"{data_dir}/*.yaml")
    return [os.path.splitext(os.path.basename(f))[0] for f in yaml_files]
