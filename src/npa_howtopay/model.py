import polars as pl
from .params import InputParams, ScenarioParams, load_scenario_from_yaml, GasParams, SharedParams
import npa_project as npa
import capex_project as cp
from attrs import evolve

KWH_PER_THERM = 29.307107


def compute_blue_columns(year: int, gas_params: GasParams, shared_params: SharedParams) -> pl.DataFrame:
    # TODO: implement this
    # gas_usage = input_params.gas_usage_per_user * num_gas_users
    # gas_costs_volumetric = gas_usage * input_params.gas_cost_per_therm
    # return pl.DataFrame({"year": year, "gas_usage": gas_usage, "gas_costs_volumetric": gas_costs_volumetric})
    pass  # type: ignore


def apply_inflation(initial_year: int, output_year: int, params: InputParams) -> InputParams:
    assert params.year == initial_year
    if output_year == initial_year:
        return params
    if output_year < initial_year:
        raise ValueError(
            f"Cannot apply inflation in reverse, output_year {output_year} is before initial_year {initial_year}"
        )

    gas_params, electric_params, shared_params = params.gas, params.electric, params.shared
    inflation_mult = (1 + shared_params.cost_inflation_rate) ** (output_year - initial_year)
    updated_gas_params = evolve(
        gas_params,
        **{
            x: x * inflation_mult
            for x in [
                "gas_generation_cost_per_therm",
                "pipeline_replacement_cost",
            ]
        },
    )
    updated_electric_params = evolve(
        electric_params,
        **{
            x: x * inflation_mult
            for x in [
                "distribution_cost_per_peak_kw_increase",
                "electricity_generation_cost_per_kwh",
            ]
        },
    )
    updated_shared_params = evolve(
        shared_params,
        **{
            x: x * inflation_mult
            for x in [
                "npa_install_costs",
            ]
        },
    )
    return InputParams(gas=updated_gas_params, electric=updated_electric_params, shared=updated_shared_params)


def compute_bill_costs(
    df: pl.DataFrame, discount_rate: float, input_params: InputParams, scenario_params: ScenarioParams
) -> pl.DataFrame:
    start_year = df.select(pl.col("year")).min().item()
    return df.with_columns(
        (pl.col("gas_revenue_requirement") / ((pl.col("year") - start_year).pow(discount_rate))).alias(
            "gas_inflation_adjusted_revenue_requirement"
        ),
        (pl.col("electric_revenue_requirement") / ((pl.col("year") - start_year).pow(discount_rate))).alias(
            "electric_inflation_adjusted_revenue_requirement"
        ),
        (pl.col("gas_revenue_requirement") + pl.col("electric_revenue_requirement")).alias("total_revenue_requirement"),
        (
            pl.col("gas_inflation_adjusted_revenue_requirement")
            + pl.col("electric_inflation_adjusted_revenue_requirement")
        ).alias("total_inflation_adjusted_revenue_requirement"),
        (pl.col("gas_inflation_adjusted_revenue_requirement") / pl.col("num_users")).alias("gas_bill_per_user"),
        (pl.col("gas_inflation_adjusted_revenue_requirement") / pl.col("num_gas_users")).alias(
            "nonconverts_gas_bill_per_user"
        ),
        (pl.lit(0)).alias("converts_gas_bill_per_user"),
        (pl.col("electric_inflation_adjusted_revenue_requirement") / pl.col("num_users")).alias(
            "electric_bill_per_user"
        ),
        # =who_pays_electric_fixed_cost_pct*electric_inflation_adjusted_revenue_requirement/electric_num_users
        (
            pl.lit(scenario_params.electric_fixed_cost_pct)
            * pl.col("electric_inflation_adjusted_revenue_requirement")
            / pl.col("num_users")
        ).alias("electric_fixed_cost_per_user"),
        # =(1 - who_pays_electric_fixed_cost_pct)*electric_inflation_adjusted_revenue_requirement / electric_total_usage
        (
            (
                pl.lit(1 - scenario_params.electric_fixed_cost_pct)
                * pl.col("electric_inflation_adjusted_revenue_requirement")
            )
            / pl.col("electric_total_usage")
        ).alias("electric_variable_cost_per_kwh"),
        # =electric_per_user_fixed_bill + electric_charge_per_kwh*(per_user_electric_need+per_user_heating_need * KWH_PER_THERM / hp_efficiency)
        (
            pl.col("electric_fixed_cost_per_user")
            + pl.col("electric_variable_cost_per_kwh")
            * (
                input_params.electric.per_user_electric_need_kwh
                + input_params.gas.per_user_heating_need_therms
                * KWH_PER_THERM
                / pl.lit(input_params.electric.hp_efficiency)
            )
        ).alias("converts_electric_bill_per_user"),
        (
            pl.col("electric_fixed_cost_per_user")
            + pl.col("electric_variable_cost_per_kwh") * input_params.electric.per_user_electric_need_kwh
        ).alias("nonconverts_electric_bill_per_user"),
        (pl.col("converts_gas_bill_per_user") + pl.col("converts_electric_bill_per_user")).alias(
            "converts_total_bill_per_user"
        ),
        (pl.col("nonconverts_gas_bill_per_user") + pl.col("nonconverts_electric_bill_per_user")).alias(
            "nonconverts_total_bill_per_user"
        ),
    )


def run_model(scenario_params: ScenarioParams, input_params: InputParams, npa_projects: pl.DataFrame) -> pl.DataFrame:
    gas_ratebase = input_params.gas.ratebase_init
    electric_ratebase = input_params.electric.ratebase_init

    gas_capex_projects = pl.DataFrame()
    electric_capex_projects = pl.DataFrame()

    output_df = pl.DataFrame()

    live_params = input_params.copy()

    # synthetic initial capex projects
    gas_initial_capex_projects = cp.get_synthetic_initial_capex_projects(
        start_year=input_params.shared.start_year,
        initial_ratebase=gas_ratebase,
        depreciation_lifetime=input_params.gas.default_depreciation_lifetime,
    )
    electric_initial_capex_projects = cp.get_synthetic_initial_capex_projects(
        start_year=input_params.shared.start_year,
        initial_ratebase=electric_ratebase,
        depreciation_lifetime=input_params.electric.default_depreciation_lifetime,
    )

    for year in range(scenario_params.start_year, scenario_params.end_year):
        live_params = apply_inflation(live_params.year, year, live_params)  # type: ignore

        # get the npas for this year
        npas_this_year = npa_projects.filter(pl.col("year") == year)

        # gas capex
        gas_capex_projects = pl.concat(
            [
                gas_capex_projects,
                gas_initial_capex_projects.filter(pl.col("project_year") == year),
                cp.get_non_lpp_gas_capex_projects(
                    year=year,
                    current_ratebase=gas_ratebase,
                    baseline_non_lpp_gas_ratebase_growth=live_params.gas.baseline_non_lpp_ratebase_growth,
                    depreciation_lifetime=live_params.gas.default_depreciation_lifetime,
                ),
                cp.get_lpp_gas_capex_projects(
                    year=year,
                    gas_bau_lpp_costs_per_year=live_params.gas_bau_lpp_costs_per_year,
                    npas_this_year=npas_this_year,
                    depreciation_lifetime=live_params.gas.lpp_depreciation_lifetime,
                ),
            ],
            how="vertical",
        )

        # electric capex
        electric_capex_projects = pl.concat(
            [
                electric_capex_projects,
                electric_initial_capex_projects.filter(pl.col("project_year") == year),
                cp.get_non_npa_electric_capex_projects(
                    year=year,
                    current_ratebase=electric_ratebase,
                    baseline_electric_ratebase_growth=live_params.electric.baseline_non_npa_ratebase_growth,
                    depreciation_lifetime=live_params.electric.default_depreciation_lifetime,
                ),
                cp.get_grid_upgrade_capex_projects(
                    year=year,
                    npas_this_year=npas_this_year,
                    peak_hp_kw=live_params.electric.hp_peak_kw,
                    peak_aircon_kw=live_params.electric.aircon_peak_kw,
                    distribution_cost_per_peak_kw_increase=live_params.electric.distribution_cost_per_peak_kw_increase,
                    grid_upgrade_depreciation_lifetime=live_params.electric.grid_upgrade_depreciation_lifetime,
                ),
            ],
            how="vertical",
        )

        # npa capex
        if scenario_params.capex_opex == "capex":
            npa_opex = 0.0
            npa_capex = cp.get_npa_capex_projects(
                npas_this_year, year, live_params.shared.npa_install_costs, live_params.shared.npa_lifetime
            )
            if scenario_params.gas_electric == "gas":
                gas_capex_projects = gas_capex_projects.pl.concat(npa_capex)
            elif scenario_params.gas_electric == "electric":
                electric_capex_projects = electric_capex_projects.pl.concat(npa_capex)
        elif scenario_params.capex_opex == "opex":
            npa_opex = npa.compute_npa_install_costs_from_df(year, npas_this_year, live_params.shared.npa_install_costs)

        gas_ratebase = cp.compute_ratebase_from_capex_projects(year, gas_capex_projects)
        electric_ratebase = cp.compute_ratebase_from_capex_projects(year, electric_capex_projects)

        ## TODO: opex stuff?

        ####### TODO: ticket
        intermediate_columns = compute_blue_columns()  # returns pl.DataFrame

        # Build output row for this year
        year_output = pl.DataFrame({
            "year": [year],
            "gas_ratebase": [gas_ratebase],
            "electric_ratebase": [electric_ratebase],
            # Add other columns as needed
        })

        output_df = pl.concat([output_df, year_output], how="vertical")

    output_df = compute_bill_costs(output_df, input_params.shared.discount_rate)  # appends new columns to output_df

    return output_df


####### ticket
def analyze_scenarios(scenario_runs: dict[ScenarioParams, pl.DataFrame]) -> None:
    pass


if __name__ == "__main__":
    scenario_params = ScenarioParams(start_year=2025, end_year=2050, gas_electric="gas", capex_opex="capex")
    input_params = load_scenario_from_yaml("sample")
    npa_projects = pl.concat(
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
    ).sort("year")

    run_model(scenario_params, input_params, npa_projects)
