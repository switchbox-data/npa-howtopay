from attrs import define, field, validators
import numpy as np
import polars as pl


## All dataframes used by functions in this class will have the following columns:
# project_year: int
# num_converts: int
# pipe_value_per_user: float
# pipe_decomm_cost_per_user: float
# peak_kw_winter_headroom: float
# peak_kw_summer_headroom: float
# aircon_percent_adoption_pre_npa: float

# note: could represent scattershot electrification as a row with pipe_value_per_user and pipe_decomm_cost_per_user set to 0


@define
class NpaProject:
    project_year: int
    num_converts: int = field(validator=validators.ge(0))
    pipe_value_per_user: float = field()
    pipe_decomm_cost_per_user: float = field(validator=validators.ge(0.0))
    peak_kw_winter_headroom: float = field(validator=validators.ge(0.0))
    peak_kw_summer_headroom: float = field(validator=validators.ge(0.0))
    aircon_percent_adoption_pre_npa: float = field(
        validator=validators.and_(
            validators.ge(0.0),
            validators.le(1.0),
        )
    )
    is_scattershot: bool = field(default=False)

    def to_df(self) -> pl.DataFrame:
        return pl.DataFrame({
            "project_year": [self.project_year],
            "num_converts": [self.num_converts],
            "pipe_value_per_user": [self.pipe_value_per_user],
            "pipe_decomm_cost_per_user": [self.pipe_decomm_cost_per_user],
            "peak_kw_winter_headroom": [self.peak_kw_winter_headroom],
            "peak_kw_summer_headroom": [self.peak_kw_summer_headroom],
            "aircon_percent_adoption_pre_npa": [self.aircon_percent_adoption_pre_npa],
            "is_scattershot": [self.is_scattershot],
        })


def append_scattershot_electrification_df(
    npa_projects_df: pl.DataFrame,
    scattershot_electrification_df: pl.DataFrame,
) -> pl.DataFrame:
    """
    Append a dataframe of scattershot electrification projects to the npa projects df.
    Scattershot electrification projects match the schema for npa projects, but will only affect the number of users and total electric usage, not anything related to pipe value or grid upgrades. It is meant to capture customers leaving the gas network independent of NPA projects.
    """
    scattershot_with_npa_cols = scattershot_electrification_df.with_columns(
        pl.lit(0.0).alias("pipe_value_per_user"),
        pl.lit(0.0).alias("pipe_decomm_cost_per_user"),
        pl.lit(np.inf).alias("peak_kw_winter_headroom"),
        pl.lit(np.inf).alias("peak_kw_summer_headroom"),
        pl.lit(0.0).alias("aircon_percent_adoption_pre_npa"),
        pl.lit(True).alias("is_scattershot"),
    )
    return pl.concat([npa_projects_df, scattershot_with_npa_cols])


def compute_hp_converts_from_df(year: int, df: pl.DataFrame, cumulative: bool = False, npa_only: bool = False) -> int:
    if df.height == 0:
        return 0
    year_filter = pl.col("project_year") <= pl.lit(year) if cumulative else pl.col("project_year") == pl.lit(year)
    npa_filter = ~pl.col("is_scattershot") if npa_only else pl.lit(True)
    return int(df.filter(year_filter & npa_filter).select(pl.col("num_converts")).sum().item())


def compute_npa_install_costs_from_df(year: int, df: pl.DataFrame, npa_install_cost: float) -> float:
    # TODO: should this also include pipe_decomm_costs?
    return npa_install_cost * compute_hp_converts_from_df(year, df, cumulative=False, npa_only=True)


def compute_npa_pipe_cost_avoided_from_df(year: int, df: pl.DataFrame) -> float:
    if df.height == 0:
        return 0.0
    return float(
        df.filter(pl.col("project_year") == year)
        .select(pl.col("pipe_value_per_user") * pl.col("num_converts"))
        .sum()
        .item()
    )


def compute_peak_kw_increase_from_df(year: int, df: pl.DataFrame, peak_hp_kw: float, peak_aircon_kw: float) -> float:
    return float(
        df.filter(pl.col("project_year") == year)
        .select(
            pl.max_horizontal(
                pl.max_horizontal(
                    pl.col("num_converts") * pl.lit(peak_hp_kw) - pl.col("peak_kw_winter_headroom"), pl.lit(0)
                ),
                pl.max_horizontal(
                    pl.col("num_converts") * (1 - pl.col("aircon_percent_adoption_pre_npa")) * pl.lit(peak_aircon_kw)
                    - pl.col("peak_kw_summer_headroom"),
                    pl.lit(0),
                ),
            )
        )
        .sum()
        .item()
    )


def compute_existing_pipe_value_from_df(year: int, df: pl.DataFrame) -> float:
    return float(
        df.filter(pl.col("project_year") == year)
        .select(pl.col("pipe_value_per_user") * pl.col("num_converts"))
        .sum()
        .item()
    )


def compute_pipe_decomm_cost_from_df(year: int, df: pl.DataFrame) -> float:
    return float(
        df.filter(pl.col("project_year") == year)
        .select(pl.col("pipe_decomm_cost_per_user") * pl.col("num_converts"))
        .sum()
        .item()
    )


def return_empty_npa_df() -> pl.DataFrame:
    return pl.DataFrame({
        "project_year": pl.Series([], dtype=pl.Int64),
        "num_converts": pl.Series([], dtype=pl.Int64),
        "pipe_value_per_user": pl.Series([], dtype=pl.Float64),
        "pipe_decomm_cost_per_user": pl.Series([], dtype=pl.Float64),
        "peak_kw_winter_headroom": pl.Series([], dtype=pl.Float64),
        "peak_kw_summer_headroom": pl.Series([], dtype=pl.Float64),
        "aircon_percent_adoption_pre_npa": pl.Series([], dtype=pl.Float64),
        "is_scattershot": pl.Series([], dtype=pl.Boolean),
    })
