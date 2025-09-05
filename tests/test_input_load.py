from npa_howtopay.params import ScenarioParams
import pytest

from npa_howtopay.params import (
    load_scenario_from_yaml,
    load_time_series_params_from_web_params,
    load_time_series_params_from_yaml,
)


@pytest.fixture
def web_params():
    return {
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


def test_load_sample_yaml():
    """Test loading the sample.yaml file"""
    # Load the sample scenario
    params = load_scenario_from_yaml("sample")
    # Verify that params is not None and has expected structure
    assert params is not None


def test_load_web_params(web_params):
    """Test loading the web params"""
    params = load_time_series_params_from_web_params(web_params, 2025, 2050)
    # Verify params has expected structure
    assert params is not None

    # Verify gas_bau_lpp_costs df has correct shape and columns
    assert params.gas_bau_lpp_costs_per_year.shape == (26, 2)
    assert set(params.gas_bau_lpp_costs_per_year.columns) == {"year", "cost"}

    # Verify gas_fixed_overhead_costs df has correct shape and columns
    assert params.gas_fixed_overhead_costs.shape == (26, 2)
    assert set(params.gas_fixed_overhead_costs.columns) == {"year", "cost"}

    # Verify electric_fixed_overhead_costs df has correct shape and columns
    assert params.electric_fixed_overhead_costs.shape == (26, 2)
    assert set(params.electric_fixed_overhead_costs.columns) == {"year", "cost"}

    # Verify npa_projects df has correct shape and columns
    assert params.npa_projects.shape == (26, 8)
    assert set(params.npa_projects.columns) == {
        "project_year",
        "num_converts",
        "pipe_value_per_user",
        "pipe_decomm_cost_per_user",
        "peak_kw_winter_headroom",
        "peak_kw_summer_headroom",
        "aircon_percent_adoption_pre_npa",
        "is_scattershot",
    }


def test_load_time_series_params_from_yaml():
    """Test loading the time series params from yaml"""
    params = load_time_series_params_from_yaml("sample")
    # Verify that params is not None and has expected structure
    assert params is not None

    # Verify gas_bau_lpp_costs df has correct shape and columns
    assert params.gas_bau_lpp_costs_per_year.shape == (26, 2)
    assert set(params.gas_bau_lpp_costs_per_year.columns) == {"year", "cost"}

    # Verify gas_fixed_overhead_costs df has correct shape and columns
    assert params.gas_fixed_overhead_costs.shape == (26, 2)
    assert set(params.gas_fixed_overhead_costs.columns) == {"year", "cost"}

    # Verify electric_fixed_overhead_costs df has correct shape and columns
    assert params.electric_fixed_overhead_costs.shape == (26, 2)
    assert set(params.electric_fixed_overhead_costs.columns) == {"year", "cost"}

    # Verify npa_projects df has correct shape and columns
    assert params.npa_projects.shape == (28, 8)
    assert set(params.npa_projects.columns) == {
        "project_year",
        "num_converts",
        "pipe_value_per_user",
        "pipe_decomm_cost_per_user",
        "peak_kw_winter_headroom",
        "peak_kw_summer_headroom",
        "aircon_percent_adoption_pre_npa",
        "is_scattershot",
    }


def test_scenario_params_validation():
    """Test conditional validation for ScenarioParams"""
    # Invalid BAU scenarios
    with pytest.raises(ValueError, match="gas_electric must be None when bau=True"):
        ScenarioParams(2025, 2050, bau=True, gas_electric="gas")

    with pytest.raises(ValueError, match="capex_opex must be None when bau=True"):
        ScenarioParams(2025, 2050, bau=True, capex_opex="capex")

    # Invalid taxpayer scenarios
    with pytest.raises(ValueError, match="gas_electric must be None when taxpayer=True"):
        ScenarioParams(2025, 2050, taxpayer=True, gas_electric="electric")

    with pytest.raises(ValueError, match="capex_opex must be None when taxpayer=True"):
        ScenarioParams(2025, 2050, taxpayer=True, capex_opex="opex")

    # Both bau and taxpayer True
    with pytest.raises(ValueError, match="Only one of bau or taxpayer can be True"):
        ScenarioParams(2025, 2050, bau=True, taxpayer=True)

    # Invalid normal scenarios (missing required fields)
    with pytest.raises(ValueError, match="gas_electric must be set when bau=False and taxpayer=False"):
        ScenarioParams(2025, 2050)

    with pytest.raises(ValueError, match="capex_opex must be set when bau=False and taxpayer=False"):
        ScenarioParams(2025, 2050, gas_electric="gas")
