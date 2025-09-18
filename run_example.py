# run_example.py

import polars as pl

from npa_howtopay.model import analyze_scenarios, create_scenario_runs
from npa_howtopay.params import (
    COMPARE_COLS,
    load_scenario_from_yaml,
    load_time_series_params_from_web_params,
    load_time_series_params_from_yaml,
)
from npa_howtopay.utils import (
    plot_depreciation_accruals,
    plot_ratebase,
    plot_return_on_ratebase_pct,
    plot_revenue_requirements,
    plot_total_bills,
    plot_user_bills_converts,
    plot_user_bills_nonconverts,
    plot_volumetric_tariff,
    transform_to_long_format,
)

if __name__ == "__main__":
    scenario_runs = create_scenario_runs(2025, 2050, ["gas", "electric"], ["capex", "opex"])
    input_params = load_scenario_from_yaml("sample")
    ts_params = load_time_series_params_from_yaml("sample")
    results_df, delta_bau_df = analyze_scenarios(scenario_runs, input_params, ts_params)
    # EDA plots
    # For delta values (original behavior)
    plt_df_delta = transform_to_long_format(delta_bau_df)
    plot_revenue_requirements(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_volumetric_tariff(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_ratebase(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_return_on_ratebase_pct(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_depreciation_accruals(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_user_bills_converts(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_user_bills_nonconverts(plt_df_delta, show_absolute=False, save_dir="plots")
    # For absolute values - filter results_df to COMPARE_COLS and transform
    filtered_results = {}
    for scenario_name, scenario_df in results_df.items():
        if scenario_name == "bau":
            continue  # Skip BAU for absolute value plotting
        filtered_results[scenario_name] = scenario_df.select(["year", *COMPARE_COLS])

    # Concatenate and transform to long format
    combined_df = pl.concat(
        [df.with_columns(pl.lit(scenario_id).alias("scenario_id")) for scenario_id, df in filtered_results.items()],
        how="vertical",
    )
    plt_df_absolute = transform_to_long_format(combined_df)
    plot_revenue_requirements(plt_df_absolute, show_absolute=True, save_dir="plots")
    plot_volumetric_tariff(plt_df_absolute, show_absolute=True, save_dir="plots")
    plot_ratebase(plt_df_absolute, show_absolute=True, save_dir="plots")
    plot_depreciation_accruals(plt_df_absolute, show_absolute=True, save_dir="plots")

    plot_user_bills_converts(plt_df_absolute, show_absolute=True, save_dir="plots")
    plot_user_bills_nonconverts(plt_df_absolute, show_absolute=True, save_dir="plots")

    plot_total_bills(delta_bau_df, save_dir="plots")

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

out2 = analyze_scenarios(scenario_runs, input_params2, ts_params2)
