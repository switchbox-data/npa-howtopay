# run_example.py

from npa_howtopay.model import run_model
from npa_howtopay.params import (
    ScenarioParams,
    load_scenario_from_yaml,
    load_time_series_params_from_web_params,
    load_time_series_params_from_yaml,
)

if __name__ == "__main__":
    scenario_params = ScenarioParams(start_year=2025, end_year=2050, gas_electric="gas", capex_opex="capex")

    # Method 1: Using YAML with discrete values per year
    input_params = load_scenario_from_yaml("sample")
    ts_params = load_time_series_params_from_yaml("sample")

    out1 = run_model(scenario_params, input_params, ts_params)
    print("YAML-based result:", out1)

    # Method 2: Using web parameters (scalar values)
    web_params = {
        "npa_num_projects": 10,
        "num_converts": 100,
        "pipe_value_per_user": 1000.0,
        "pipe_decomm_cost_per_user": 100.0,
        "peak_kw_winter_headroom": 10.0,
        "peak_kw_summer_headroom": 10.0,
        "aircon_percent_adoption_pre_npa": 0.8,
        "non_npa_scattershot_electrifiction_users_per_year": 5,
        "gas_fixed_overhead_costs": 100.0,
        "electric_fixed_overhead_costs": 100.0,
        "gas_bau_lpp_costs_per_year": 100.0,
        "is_scattershot": False,
    }

    input_params2 = load_scenario_from_yaml("sample")  # Still load base params from YAML
    ts_params2 = load_time_series_params_from_web_params(web_params, 2025, 2050)

    out2 = run_model(scenario_params, input_params2, ts_params2)
    print("Web-params-based result:", out2)

