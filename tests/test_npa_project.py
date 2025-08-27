## Switchbox
## 2025-08-26

import numpy as np
import polars as pl

from src.npa_howtopay.npa_project import (
    generate_npa_projects,
    generate_scattershot_electrification_projects,
)


def test_generate_npa_projects():
    df = generate_npa_projects(
        start_year=2025,
        end_year=2027,
        total_num_projects=5,
        num_converts_per_project=1,
        pipe_value_per_user=100,
        pipe_decomm_cost_per_user=10,
        peak_kw_winter_headroom_per_project=100,
        peak_kw_summer_headroom_per_project=100,
        aircon_percent_adoption_pre_npa=0.5,
        pipe_decomm_cost_inflation_rate=0.03,
    )
    assert df.select(pl.col("year")).to_series().equals(pl.Series([2025, 2025, 2026, 2026, 2027]))
    assert np.isclose(
        df.select(pl.all().exclude("year")).sum().transpose().to_series(), [5, 500, 51.209, 500, 500, 2.5, 0]
    ).all()


def test_generate_scattershot_electrification_projects():
    df = generate_scattershot_electrification_projects(
        start_year=2025,
        end_year=2027,
        total_num_converts=5,
    )
    assert df.select(pl.col("year")).to_series().equals(pl.Series([2025, 2026, 2027]))
    assert np.isclose(
        df.select(pl.all().exclude("year")).sum().transpose().to_series(), [5, 0, 0, np.inf, np.inf, 0, 3]
    ).all()
