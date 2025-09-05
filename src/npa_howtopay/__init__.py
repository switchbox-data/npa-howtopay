"""NPA How to Pay package for ca_npa_howtopay."""

__version__ = "0.0.1"
__author__ = "Switchbox"
__email__ = "hello@switch.box"

# Import and expose the main classes and functions
from . import capex_project as cp
from . import npa_project as npa
from .model import run_model
from .params import (
    COMPARE_COLS,
    KWH_PER_THERM,
    ElectricParams,
    GasParams,
    InputParams,
    ScenarioParams,
    SharedParams,
    TimeSeriesParams,
    load_scenario_from_yaml,
)

__all__ = [
    "COMPARE_COLS",
    "KWH_PER_THERM",
    "ElectricParams",
    "GasParams",
    "InputParams",
    "ScenarioParams",
    "SharedParams",
    "TimeSeriesParams",
    "cp",
    "load_scenario_from_yaml",
    "npa",
    "run_model",
]
