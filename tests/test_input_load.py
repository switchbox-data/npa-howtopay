import numpy as np
import polars as pl
import pytest
from polars.testing import assert_frame_equal

from npa_howtopay.params import (
    ScenarioParams,
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
        "scattershot_electrification_users_per_year": 5,
        "gas_fixed_overhead_costs": 100.0,
        "electric_fixed_overhead_costs": 100.0,
        "gas_bau_lpp_costs_per_year": 100.0,
        "is_scattershot": False,
    }


@pytest.fixture
def expected_gas_bau_lpp_costs_no_inflation():
    """Expected gas BAU LPP costs for 2025-2030 with no inflation"""
    return pl.DataFrame({
        "year": [2025, 2026, 2027, 2028, 2029, 2030],
        "cost": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
    })


@pytest.fixture
def expected_gas_fixed_overhead_costs_no_inflation():
    """Expected gas fixed overhead costs for 2025-2030 with no inflation"""
    return pl.DataFrame({
        "year": [2025, 2026, 2027, 2028, 2029, 2030],
        "cost": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
    })


@pytest.fixture
def expected_electric_fixed_overhead_costs_no_inflation():
    """Expected electric fixed overhead costs for 2025-2030 with no inflation"""
    return pl.DataFrame({
        "year": [2025, 2026, 2027, 2028, 2029, 2030],
        "cost": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
    })


@pytest.fixture
def expected_gas_bau_lpp_costs_with_inflation():
    """Expected gas BAU LPP costs for 2025-2030 with 5% inflation"""
    return pl.DataFrame({
        "year": [2025, 2026, 2027, 2028, 2029, 2030],
        "cost": [100.0, 105.0, 110.25, 115.7625, 121.550625, 127.62815625],
    })


@pytest.fixture
def expected_gas_fixed_overhead_costs_with_inflation():
    """Expected gas fixed overhead costs for 2025-2030 with 5% inflation"""
    return pl.DataFrame({
        "year": [2025, 2026, 2027, 2028, 2029, 2030],
        "cost": [100.0, 105.0, 110.25, 115.7625, 121.550625, 127.62815625],
    })


@pytest.fixture
def expected_electric_fixed_overhead_costs_with_inflation():
    """Expected electric fixed overhead costs for 2025-2030 with 5% inflation"""
    return pl.DataFrame({
        "year": [2025, 2026, 2027, 2028, 2029, 2030],
        "cost": [100.0, 105.0, 110.25, 115.7625, 121.550625, 127.62815625],
    })


@pytest.fixture
def expected_npa_projects():
    """Expected NPA projects for 2025-2030"""
    return pl.DataFrame({
        "project_year": [2025, 2026, 2027, 2028, 2029, 2030, 2025, 2026, 2027, 2028, 2029, 2030],
        "num_converts": [100, 100, 100, 100, 100, 100, 5, 5, 5, 5, 5, 5],
        "pipe_value_per_user": [1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "pipe_decomm_cost_per_user": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "peak_kw_winter_headroom": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],
        "peak_kw_summer_headroom": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],
        "aircon_percent_adoption_pre_npa": [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "is_scattershot": [False, False, False, False, False, False, True, True, True, True, True, True],
    })


def test_load_sample_yaml():
    """Test loading the sample.yaml file"""
    # Load the sample scenario
    params = load_scenario_from_yaml("sample")
    # Verify that params is not None and has expected structure
    assert params is not None


def test_load_web_params_no_inflation(
    web_params,
    expected_gas_bau_lpp_costs_no_inflation,
    expected_gas_fixed_overhead_costs_no_inflation,
    expected_electric_fixed_overhead_costs_no_inflation,
    expected_npa_projects,
):
    """Test loading the web params without inflation"""
    params = load_time_series_params_from_web_params(web_params, 2025, 2030)

    # Verify params is not None
    assert params is not None

    # Test each DataFrame against expected values
    assert params.gas_bau_lpp_costs_per_year.equals(expected_gas_bau_lpp_costs_no_inflation)
    assert params.gas_fixed_overhead_costs.equals(expected_gas_fixed_overhead_costs_no_inflation)
    assert params.electric_fixed_overhead_costs.equals(expected_electric_fixed_overhead_costs_no_inflation)
    assert params.npa_projects.equals(expected_npa_projects)


def test_load_web_params_with_inflation(
    web_params,
    expected_gas_bau_lpp_costs_with_inflation,
    expected_gas_fixed_overhead_costs_with_inflation,
    expected_electric_fixed_overhead_costs_with_inflation,
    expected_npa_projects,
):
    """Test loading the web params with 5% inflation"""
    params = load_time_series_params_from_web_params(web_params, 2025, 2030, cost_inflation_rate=0.05)

    # Verify params is not None
    assert params is not None

    # Test each DataFrame against expected values with proper float tolerance
    assert_frame_equal(
        params.gas_bau_lpp_costs_per_year, expected_gas_bau_lpp_costs_with_inflation, check_exact=False, atol=1e-10
    )
    assert_frame_equal(
        params.gas_fixed_overhead_costs, expected_gas_fixed_overhead_costs_with_inflation, check_exact=False, atol=1e-10
    )
    assert_frame_equal(
        params.electric_fixed_overhead_costs,
        expected_electric_fixed_overhead_costs_with_inflation,
        check_exact=False,
        atol=1e-10,
    )
    # NPA projects should match exactly (no floats)
    assert params.npa_projects.equals(expected_npa_projects)


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
    # 28 rows from npa_projects + 26 rows from scattershot_electrification = 54 total rows
    assert params.npa_projects.shape == (54, 8)
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
