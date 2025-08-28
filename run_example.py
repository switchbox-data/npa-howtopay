import polars as pl

from npa_howtopay import npa_project as npa
from npa_howtopay.model import run_model

# Make sure the package is installed in development mode first
from npa_howtopay.params import (
    ScenarioParams,
    TimeSeriesParams,
    load_scenario_from_yaml,
)

if __name__ == "__main__":
    scenario_params = ScenarioParams(start_year=2025, end_year=2050, gas_electric="gas", capex_opex="capex")
    input_params = load_scenario_from_yaml("sample")
    ts_params = TimeSeriesParams(
        npa_projects=pl.concat(
            [
                npa.generate_npa_projects(
                    start_year=scenario_params.start_year,
                    end_year=scenario_params.end_year,
                    total_num_projects=10,
                    num_converts_per_project=5,
                    pipe_value_per_user=1000.0,
                    pipe_decomm_cost_per_user=100.0,
                    peak_kw_winter_headroom_per_project=10.0,
                    peak_kw_summer_headroom_per_project=10.0,
                    aircon_percent_adoption_pre_npa=0.8,
                    pipe_decomm_cost_inflation_rate=input_params.shared.cost_inflation_rate,
                ),
                npa.generate_scattershot_electrification_projects(
                    start_year=scenario_params.start_year,
                    end_year=scenario_params.end_year,
                    total_num_converts=10,
                ),
            ],
            how="vertical",
        ).sort("project_year"),
        gas_bau_lpp_costs_per_year=pl.DataFrame({
            "year": list(range(scenario_params.start_year, scenario_params.end_year + 1)),
            "cost": [100] * (scenario_params.end_year - scenario_params.start_year + 1),
        }).sort("year"),
        electric_fixed_overhead_costs=pl.DataFrame({
            "year": list(range(scenario_params.start_year, scenario_params.end_year + 1)),
            "cost": [100] * (scenario_params.end_year - scenario_params.start_year + 1),
        }).sort("year"),
        gas_fixed_overhead_costs=pl.DataFrame({
            "year": list(range(scenario_params.start_year, scenario_params.end_year + 1)),
            "cost": [100] * (scenario_params.end_year - scenario_params.start_year + 1),
        }).sort("year"),
    )

    out = run_model(scenario_params, input_params, ts_params)
    print(out)
