## Switchbox
## 2025-08-26

import numpy as np
import polars as pl
import pytest
from polars.testing import assert_frame_equal

from npa_howtopay.npa_project import (
    append_scattershot_electrification_df,
    compute_existing_pipe_value_from_df,
    compute_hp_converts_from_df,
    compute_npa_install_costs_from_df,
    compute_npa_pipe_cost_avoided_from_df,
    compute_peak_kw_increase_from_df,
    compute_pipe_decomm_cost_from_df,
    return_empty_npa_df,
)


@pytest.fixture
def sample_npa_projects_df():
    """Fixture for a sample NPA projects dataframe."""
    return pl.DataFrame({
        "project_year": [2024, 2025, 2025, 2026],
        "num_converts": [100, 200, 150, 300],
        "pipe_value_per_user": [1000.0, 1200.0, 1100.0, 1300.0],
        "pipe_decomm_cost_per_user": [500.0, 600.0, 550.0, 700.0],
        "peak_kw_winter_headroom": [50.0, 60.0, 55.0, 70.0],
        "peak_kw_summer_headroom": [75.0, 80.0, 77.0, 85.0],
        "aircon_percent_adoption_pre_npa": [0.3, 0.4, 0.35, 0.5],
        "is_scattershot": [False, False, False, False],
    })


@pytest.fixture
def sample_scattershot_df():
    """Fixture for a sample scattershot electrification dataframe."""
    return pl.DataFrame({
        "project_year": [2025, 2027],
        "num_converts": [50, 75],
    })


def test_append_scattershot_electrification_df(sample_npa_projects_df, sample_scattershot_df):
    """Test appending scattershot electrification."""
    result = append_scattershot_electrification_df(sample_npa_projects_df, sample_scattershot_df)

    expected_df = pl.DataFrame({
        "project_year": [2024, 2025, 2025, 2026, 2025, 2027],
        "num_converts": [100, 200, 150, 300, 50, 75],
        "pipe_value_per_user": [1000.0, 1200.0, 1100.0, 1300.0, 0.0, 0.0],
        "pipe_decomm_cost_per_user": [500.0, 600.0, 550.0, 700.0, 0.0, 0.0],
        "peak_kw_winter_headroom": [50.0, 60.0, 55.0, 70.0, np.inf, np.inf],
        "peak_kw_summer_headroom": [75.0, 80.0, 77.0, 85.0, np.inf, np.inf],
        "aircon_percent_adoption_pre_npa": [0.3, 0.4, 0.35, 0.5, 0.0, 0.0],
        "is_scattershot": [False, False, False, False, True, True],
    })

    assert_frame_equal(result, expected_df, check_dtypes=False)


def test_append_scattershot_electrification_df_empty_npa(sample_scattershot_df):
    """Test appending scattershot to empty NPA dataframe."""
    empty_npa_df = return_empty_npa_df()

    result = append_scattershot_electrification_df(empty_npa_df, sample_scattershot_df)

    expected_df = pl.DataFrame({
        "project_year": [2025, 2027],
        "num_converts": [50, 75],
        "pipe_value_per_user": [0.0, 0.0],
        "pipe_decomm_cost_per_user": [0.0, 0.0],
        "peak_kw_winter_headroom": [np.inf, np.inf],
        "peak_kw_summer_headroom": [np.inf, np.inf],
        "aircon_percent_adoption_pre_npa": [0.0, 0.0],
        "is_scattershot": [True, True],
    })

    assert_frame_equal(result, expected_df, check_dtypes=False)


def test_compute_hp_converts_npa_only(sample_npa_projects_df, sample_scattershot_df):
    """Test computing HP converts."""
    combined_df = append_scattershot_electrification_df(sample_npa_projects_df, sample_scattershot_df)
    result = compute_hp_converts_from_df(2025, combined_df, cumulative=False, npa_only=True)
    assert result == 350  # 200 + 150


def test_compute_hp_converts_include_scattershot(sample_npa_projects_df, sample_scattershot_df):
    """Test computing HP converts."""
    combined_df = append_scattershot_electrification_df(sample_npa_projects_df, sample_scattershot_df)
    result = compute_hp_converts_from_df(2025, combined_df, cumulative=False, npa_only=False)
    assert result == 400  # 200 + 150


def test_compute_npa_install_costs_from_df(sample_npa_projects_df, sample_scattershot_df):
    """Test computing NPA install costs."""
    combined_df = append_scattershot_electrification_df(sample_npa_projects_df, sample_scattershot_df)
    result = compute_npa_install_costs_from_df(2025, combined_df, 5000.0)
    assert result == 5000.0 * 350  # Only NPA projects


def test_compute_npa_pipe_cost_avoided_from_df(sample_npa_projects_df, sample_scattershot_df):
    """Test computing pipe cost avoided."""
    combined_df = append_scattershot_electrification_df(sample_npa_projects_df, sample_scattershot_df)
    result = compute_npa_pipe_cost_avoided_from_df(2025, combined_df)
    expected = (1200.0 * 200) + (1100.0 * 150)
    assert result == expected


def test_compute_peak_kw_increase_from_df(sample_npa_projects_df, sample_scattershot_df):
    """Test computing peak kW increase."""
    combined_df = append_scattershot_electrification_df(sample_npa_projects_df, sample_scattershot_df)
    result = compute_peak_kw_increase_from_df(2025, combined_df, 5.0, 3.0)
    assert result > 0  # Should be positive


def test_compute_existing_pipe_value_from_df(sample_npa_projects_df, sample_scattershot_df):
    """Test computing existing pipe value."""
    combined_df = append_scattershot_electrification_df(sample_npa_projects_df, sample_scattershot_df)
    result = compute_existing_pipe_value_from_df(2025, combined_df)
    expected = (1200.0 * 200) + (1100.0 * 150)
    assert result == expected


def test_compute_pipe_decomm_cost_from_df(sample_npa_projects_df, sample_scattershot_df):
    """Test computing pipe decommissioning cost."""
    combined_df = append_scattershot_electrification_df(sample_npa_projects_df, sample_scattershot_df)
    result = compute_pipe_decomm_cost_from_df(2025, combined_df)
    expected = (600.0 * 200) + (550.0 * 150)
    assert result == expected
