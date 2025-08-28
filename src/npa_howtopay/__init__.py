"""NPA How to Pay package for ca_npa_howtopay."""

__version__ = "0.0.1"
__author__ = "Switchbox"
__email__ = "hello@switch.box"

# Import and expose the main classes and functions
from .params import (
    InputParams,
    ScenarioParams,
    TimeSeriesParams,
    GasParams,
    ElectricParams,
    SharedParams,
    load_scenario_from_yaml,
    KWH_PER_THERM,
)
from .model import run_model
from . import npa_project as npa
from . import capex_project as cp

__all__ = [
    "InputParams",
    "ScenarioParams",
    "TimeSeriesParams",
    "GasParams",
    "ElectricParams",
    "SharedParams",
    "load_scenario_from_yaml",
    "run_model",
    "npa",
    "cp",
    "KWH_PER_THERM",
]
