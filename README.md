# npa-howtopay

[![Release](https://img.shields.io/github/v/release/switchbox-data/npa-howtopay)](https://img.shields.io/github/v/release/switchbox-data/npa-howtopay)
[![Build status](https://img.shields.io/github/actions/workflow/status/switchbox-data/npa-howtopay/main.yml?branch=main)](https://github.com/switchbox-data/npa-howtopay/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/switchbox-data/npa-howtopay/branch/main/graph/badge.svg)](https://codecov.io/gh/switchbox-data/npa-howtopay)
[![Commit activity](https://img.shields.io/github/commit-activity/m/switchbox-data/npa-howtopay)](https://img.shields.io/github/commit-activity/m/switchbox-data/npa-howtopay)
[![License](https://img.shields.io/github/license/switchbox-data/npa-howtopay)](https://img.shields.io/github/license/switchbox-data/npa-howtopay)

[Link to the app](https://switchbox.shinyapps.io/npa_how_to_pay_app/)

package for ca_npa_howtopay

- **Github repository**: <https://github.com/switchbox-data/npa-howtopay/>
- **Documentation** <https://switchbox-data.github.io/npa-howtopay/>

## Overview
`npa-howtopay` analyzes impact of targeted electrification projects on utilities and customers under different expense scenarios. It compares impacts across scenarios where NPA (Non-Pipeline Alternatives) costs are treated as capex or opex and allocated to gas utilities, electric utilities, or taxpayers.

## Installation (GitHub)
Requires Python >= 3.9.

```bash
pip install git+https://github.com/switchbox-data/npa-howtopay.git
```

Optional: install a specific tag.
```bash
pip install git+https://github.com/switchbox-data/npa-howtopay.git@v0.0.1
```

## Quickstart (local run)
```python
from npa_howtopay.model import (
    create_scenario_runs,
    run_all_scenarios,
    create_delta_df,
    return_absolute_values_df,
)
from npa_howtopay.params import (
    COMPARE_COLS,
    load_scenario_from_yaml,
    load_time_series_params_from_yaml,
)

run_name = "sample"  # must match the YAML file name in npa_howtopay/data
scenario_runs = create_scenario_runs(2025, 2050, ["gas", "electric"], ["capex", "opex"])

input_params = load_scenario_from_yaml(run_name)
ts_params = load_time_series_params_from_yaml(run_name)

results_df_all = run_all_scenarios(scenario_runs, input_params, ts_params)

delta_df = create_delta_df(results_df_all, COMPARE_COLS)
absolute_df = return_absolute_values_df(results_df_all, COMPARE_COLS)
```

## Scenario Definitions
| Scenario Name          | Description                                                                                      |
|------------------------|--------------------------------------------------------------------------------------------------|
| bau                    | Business-as-usual (BAU): No NPA projects, baseline utility costs and spending.                   |
| taxpayer               | All NPA costs are paid by taxpayers, not by utility customers.                                   |
| gas_capex              | Gas utility pays for NPA projects as capital expenditures (added to gas ratebase).               |
| gas_opex               | Gas utility pays for NPA projects as operating expenses (expensed in year incurred).             |
| electric_capex         | Electric utility pays for NPA projects as capital expenditures (added to electric ratebase).     |
| electric_opex          | Electric utility pays for NPA projects as operating expenses (expensed in year incurred).        |
| performance_incentive  | Cost savings are NPV(BAU) - NPV(NPA); a share is recovered as capex over 10 years.                |

## Data Inputs
- Scenario and time series inputs can be provided via YAML files located in `npa_howtopay/data`.
- For web app runs, time series can be built from user constants via:
  - `load_time_series_params_from_web_params` in `npa_howtopay.params`

## API Highlights
- `run_model`: Run the model for a single scenario
- `run_all_scenarios`: Run across scenarios and return a dict of results
- `create_delta_df`: Compute BAU deltas for selected columns
- `return_absolute_values_df`: Combine results into a single dataframe

## Links
- Repository: https://github.com/switchbox-data/npa-howtopay
- Documentation: https://switchbox-data.github.io/npa-howtopay/
- App: https://switchbox.shinyapps.io/npa_how_to_pay_app/
