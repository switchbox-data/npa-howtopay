# run_example.py


from npa_howtopay.model import create_delta_df, create_scenario_runs, return_absolute_values_df, run_all_scenarios
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
    results_df_all = run_all_scenarios(scenario_runs, input_params, ts_params)

    delta_df = create_delta_df(results_df_all, COMPARE_COLS)
    results_df = return_absolute_values_df(results_df_all, COMPARE_COLS)

    # EDA plots
    # For delta values (original behavior)
    plt_df_delta = transform_to_long_format(delta_df)
    plot_revenue_requirements(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_volumetric_tariff(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_ratebase(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_return_on_ratebase_pct(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_depreciation_accruals(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_user_bills_converts(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_user_bills_nonconverts(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_total_bills(plt_df_delta, show_absolute=False, save_dir="plots")
    plot_return_on_ratebase_pct(plt_df_delta, show_absolute=False, save_dir="plots")
    # For absolute values
    plt_df_absolute = transform_to_long_format(results_df)
    plot_revenue_requirements(plt_df_absolute, show_absolute=True, save_dir="plots")
    plot_volumetric_tariff(plt_df_absolute, show_absolute=True, save_dir="plots")
    plot_ratebase(plt_df_absolute, show_absolute=True, save_dir="plots")
    plot_depreciation_accruals(plt_df_absolute, show_absolute=True, save_dir="plots")

    plot_user_bills_converts(plt_df_absolute, show_absolute=True, save_dir="plots")
    plot_user_bills_nonconverts(plt_df_absolute, show_absolute=True, save_dir="plots")

    plot_total_bills(results_df, show_absolute=True, save_dir="plots")
    plot_return_on_ratebase_pct(results_df, show_absolute=True, save_dir="plots")

# Method 2: Using web parameters (scalar values)
web_params = {
    "npa_num_projects": 10,
    "num_converts": 100,
    "pipe_value_per_user": 1000.0,
    "pipe_decomm_cost_per_user": 100.0,
    "peak_kw_winter_headroom": 10.0,
    "peak_kw_summer_headroom": 10.0,
    "aircon_percent_adoption_pre_npa": 0.8,
    "scattershot_electrification_users_per_year": 5,
    "gas_fixed_overhead_costs": 100.0,
    "electric_fixed_overhead_costs": 100.0,
    "gas_bau_lpp_costs_per_year": 100.0,
    "npa_year_start": 2025,
    "npa_year_end": 2030,
    "is_scattershot": False,
}

input_params2 = load_scenario_from_yaml("sample")  # Still load base params from YAML
ts_params2 = load_time_series_params_from_web_params(web_params, 2025, 2050)

out2 = run_all_scenarios(scenario_runs, input_params2, ts_params2)
delta_df2 = create_delta_df(out2, COMPARE_COLS)
results_df2 = return_absolute_values_df(out2, COMPARE_COLS)
