# Modules
::: npa_howtopay.capex_project
::: npa_howtopay.npa_project  
::: npa_howtopay.model
::: npa_howtopay.params

## Overview
The `npa-howtopay` package provides functionality for analyzing energy costs and project economics.

## Core Modules

### Main Package (`npa_howtopay`)
- **`run_model`** - Main function to execute the cost analysis model
- **`load_scenario_from_yaml`** - Load scenario parameters from YAML files

### Parameters (`params`)
- **`ElectricParams`** - Electric utility parameters
- **`GasParams`** - Gas utility parameters  
- **`InputParams`** - Input parameters for the model
- **`ScenarioParams`** - Scenario-specific parameters
- **`SharedParams`** - Shared parameters across scenarios
- **`TimeSeriesParams`** - Time series data parameters
- **`KWH_PER_THERM`** - Conversion constant

### Project Types
- **`npa_project`** - NPA project functionality
- **`capex_project`** - Capital expenditure project functionality

### Utilities
- **`model`** - Core modeling logic
- **`utils`** - Utility functions
- **`web_params`** - Web interface parameters

## Usage Examples
```python
from npa_howtopay import run_model, load_scenario_from_yaml

# Load scenario from YAML
scenario = load_scenario_from_yaml("scenario.yaml")

# Run the model
results = run_model(scenario)
```
