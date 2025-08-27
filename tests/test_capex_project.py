## Switchbox
## 2025-08-25

import numpy as np
import polars as pl
import pytest
from polars.testing import assert_frame_equal

from src.npa_howtopay.capex_project import (
    compute_depreciation_expense_from_capex_projects,
    compute_ratebase_from_capex_projects,
    get_grid_upgrade_capex_projects,
    get_lpp_gas_capex_projects,
    get_non_lpp_gas_capex_projects,
    get_non_npa_electric_capex_projects,
    get_npa_capex_projects,
    get_synthetic_initial_capex_projects,
)


def test_get_synthetic_initial_capex_projects():
    start_year = 2025
    initial_ratebase = 6000
    # 3000 * (1 + 2/3 + 1/3) = 6000
    df = get_synthetic_initial_capex_projects(
        start_year=start_year, initial_ratebase=initial_ratebase, depreciation_lifetime=3
    )
    ref_df = pl.DataFrame({
        "project_year": [2023, 2024, 2025],
        "project_type": ["synthetic_initial", "synthetic_initial", "synthetic_initial"],
        "original_cost": [3000, 3000, 3000],
        "depreciation_lifetime": [3, 3, 3],
    })
    assert_frame_equal(ref_df, df, check_dtypes=False)
    assert np.isclose(compute_ratebase_from_capex_projects(start_year, df), initial_ratebase)


def test_get_non_lpp_gas_capex_projects():
    df = get_non_lpp_gas_capex_projects(
        year=2025, current_ratebase=1000, baseline_non_lpp_gas_ratebase_growth=0.015, depreciation_lifetime=60
    )
    ref_df = pl.DataFrame({
        "project_year": [2025],
        "project_type": ["misc"],
        "original_cost": [15],
        "depreciation_lifetime": [60],
    })
    assert_frame_equal(ref_df, df, check_dtypes=False)


def test_get_non_npa_electric_capex_projects():
    df = get_non_npa_electric_capex_projects(
        year=2025, current_ratebase=1000, baseline_electric_ratebase_growth=0.03, depreciation_lifetime=60
    )
    ref_df = pl.DataFrame({
        "project_year": [2025],
        "project_type": ["misc"],
        "original_cost": [30],
        "depreciation_lifetime": [60],
    })
    assert_frame_equal(ref_df, df, check_dtypes=False)


## NPA TESTS
@pytest.fixture
def npa_projects():
    return pl.DataFrame({
        "project_year": [2025, 2025, 2025],
        "num_converts": [10, 20, 5],  # 35 total
        "pipe_value_per_user": [1000, 100, 3000],  # $27_000 total
        # 5_500; does not affect capex?
        "pipe_decomm_cost_per_user": [100, 200, 100],
        "peak_kw_winter_headroom": [10, 100, 1],
        "peak_kw_summer_headroom": [10, 1, 10],
        "aircon_percent_adoption_pre_npa": [0.2, 0.8, 0.8],
    })


def test_get_lpp_gas_capex_projects(npa_projects):
    lpp_costs_standard = pl.DataFrame({
        "year": [2025, 2025, 2026],
        "cost": [30000, 20000, 30000],  # 50k in 2025
    })
    df = get_lpp_gas_capex_projects(
        year=2025,
        gas_bau_lpp_costs_per_year=lpp_costs_standard,
        npa_projects=npa_projects,
        depreciation_lifetime=60,
    )
    ref_df = pl.DataFrame({
        "project_year": [2025],
        "project_type": ["pipeline"],
        "original_cost": [23000],
        "depreciation_lifetime": [60],
    })
    assert_frame_equal(ref_df, df, check_dtypes=False)

    # test zero bound
    lpp_costs_small = pl.DataFrame({
        "year": [2025, 2025, 2026],
        "cost": [100, 200, 300],  # 300 in 2025
    })
    df_zero = get_lpp_gas_capex_projects(
        year=2025, gas_bau_lpp_costs_per_year=lpp_costs_small, npa_projects=npa_projects, depreciation_lifetime=60
    )
    assert df_zero.is_empty()


def test_get_grid_upgrade_capex_projects(npa_projects):
    df = get_grid_upgrade_capex_projects(
        year=2025,
        npa_projects=npa_projects,
        peak_hp_kw=2,
        peak_aircon_kw=3,
        distribution_cost_per_peak_kw_increase=1000,
        grid_upgrade_depreciation_lifetime=30,
    )
    ref_df = pl.DataFrame({
        "project_year": [2025],
        "original_cost": [34000],  # three projects increase peak_kw by 14, 11, 9
        "depreciation_lifetime": [30],
    })
    assert_frame_equal(ref_df, df, check_dtypes=False)


def test_get_npa_capex_projects(npa_projects):
    df = get_npa_capex_projects(year=2025, npa_projects=npa_projects, npa_install_cost=1000, npa_lifetime=10)
    ref_df = pl.DataFrame({
        "project_year": [2025],
        "original_cost": [35000],
        "depreciation_lifetime": [10],
    })
    assert_frame_equal(ref_df, df, check_dtypes=False)


## COMPUTE TESTS
capex_df = pl.DataFrame({
    "project_year": [2025, 2026, 2027],
    "original_cost": [1000, 1000, 1000],
    "depreciation_lifetime": [10, 20, 10],
})


def test_compute_ratebase_from_capex_projects():
    ratebases = [compute_ratebase_from_capex_projects(year, capex_df) for year in [2025, 2026, 2027, 2028, 2045, 2046]]
    assert np.isclose(ratebases, [1000, 1900, 2750, 2500, 50, 0]).all()


def test_compute_depreciation_expense_from_capex_projects():
    depreciations = [
        compute_depreciation_expense_from_capex_projects(year, capex_df)
        for year in [2025, 2026, 2027, 2028, 2045, 2046, 2047]
    ]
    assert np.isclose(depreciations, [0, 100, 150, 250, 50, 50, 0]).all()
