# npa-howtopay

[![Release](https://img.shields.io/github/v/release/switchbox-data/npa-howtopay)](https://img.shields.io/github/v/release/switchbox-data/npa-howtopay)
[![Build status](https://img.shields.io/github/actions/workflow/status/switchbox-data/npa-howtopay/main.yml?branch=main)](https://github.com/switchbox-data/npa-howtopay/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/switchbox-data/npa-howtopay)](https://img.shields.io/github/commit-activity/m/switchbox-data/npa-howtopay)
[![License](https://img.shields.io/github/license/switchbox-data/npa-howtopay)](https://img.shields.io/github/license/switchbox-data/npa-howtopay)

package for ca_npa_howtopay

## Overview
The `npa-howtopay` package provides functionality for analyzing energy costs and project economics under different expense scenarios.

## Core Modules

### Main Package (`npa_howtopay`)
- **`run_model`** - Main function to execute the cost analysis model for a single scenario
- **`analyze_scenarios`** - Execute run_model for all scenarios and return results and delta from BAU (no NPAs) dfs.

### Initialize Model
If running locally:
- **`load_scenario_from_yaml`** - Load input parameters from YAML files
In a local run, users can provide timeseries inputs for NPA projects, gas and electric fixed overhead, and planned LPP spending in each year,

If running from web app:
- **`load_scenario_from_yaml`** - Load input parameters from YAML files
- **`load_time_series_params_from_web_params`** - Automatically creates time-series inputs using user defined constants.

### Parameters (`params`)
- **`ElectricParams`** - Electric utility parameters
- **`GasParams`** - Gas utility parameters
- **`InputParams`** - Input parameters for the model
- **`ScenarioParams`** - Scenario-specific parameters (who pays (gas/electric/taxpayer), and how (capex/opex/none))
- **`SharedParams`** - Shared parameters across scenarios
- **`TimeSeriesParams`** - Time series data parameters. NPA projects per year, fixed overhead costs, gas LPP BAU spending
- **`KWH_PER_THERM`** - Conversion constant

### Project Types
- **`npa_project`** - NPA project functionality
- **`capex_project`** - Capital expenditure project functionality

### Utilities
- **`model`** - Core modeling logic
- **`utils`** - Utility plotting functions
- **`web_params`** - Web interface parameters



## Usage Examples
```python
from npa_howtopay import run_model, load_scenario_from_yaml
# Local execution
# Define scenarios
  run_name = "sample" #should match yaml file name
  scenario_runs = create_scenario_runs(2025, 2050, ["gas", "electric"], ["capex", "opex"])
  input_params = load_scenario_from_yaml(run_name)
  ts_params = load_time_series_params_from_yaml(run_name)
  results_df, delta_bau_df = analyze_scenarios(scenario_runs, input_params, ts_params)
```
