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


def generate_npa_projects(
    start_year: int,
    end_year: int,
    total_num_projects: int,
    num_converts_per_project: int,
    pipe_value_per_user: float,
    pipe_decomm_cost_per_user: float,
    peak_kw_winter_headroom_per_project: float,
    peak_kw_summer_headroom_per_project: float,
    aircon_percent_adoption_pre_npa: float,
    pipe_decomm_cost_inflation_rate: float = 0.0,
) -> pl.DataFrame:
    """
    Generate a dataframe of NPA projects of length total_num_projects.
    The projects are distributed evenly across the years, with remainders added
    to earlier years. Note that there can be multiple project rows per year
    in the result
    """
    years = range(start_year, end_year + 1)
    num_years = len(years)
    base = total_num_projects // num_years
    remainder = total_num_projects % num_years

    projects_per_year = np.full(num_years, base, dtype=int)
    projects_per_year[:remainder] += 1

    project_years = [b for a in [[y] * r for y, r in zip(years, projects_per_year)] for b in a]
    pipe_decomm_costs = [
        pipe_decomm_cost_per_user * (1.0 + pipe_decomm_cost_inflation_rate) ** (y - start_year) for y in project_years
    ]

    return pl.DataFrame({
        "project_year": project_years,
        "num_converts": [num_converts_per_project] * total_num_projects,
        "pipe_value_per_user": [float(pipe_value_per_user)] * total_num_projects,
        "pipe_decomm_cost_per_user": pipe_decomm_costs,
        "peak_kw_winter_headroom": [float(peak_kw_winter_headroom_per_project)] * total_num_projects,
        "peak_kw_summer_headroom": [float(peak_kw_summer_headroom_per_project)] * total_num_projects,
        "aircon_percent_adoption_pre_npa": [float(aircon_percent_adoption_pre_npa)] * total_num_projects,
        "is_scattershot": [False] * total_num_projects,
    })


def generate_scattershot_electrification_projects(
    start_year: int,
    end_year: int,
    total_num_converts: int,
) -> pl.DataFrame:
    """
    Generate a dataframe of scattershot electrification projects, one per year.
    The projects are distributed evenly across the years, with remainders added
    to earlier years. These match the schema for npa projects, but will only
    affect the number of users, not anything related to pipe value or grid upgrades
    """
    years = range(start_year, end_year + 1)
    num_years = len(years)
    base = total_num_converts // num_years
    remainder = total_num_converts % num_years

    converts_per_year = np.full(num_years, base, dtype=int)
    converts_per_year[:remainder] += 1

    return pl.DataFrame({
        "project_year": years,
        "num_converts": converts_per_year,
        "pipe_value_per_user": [0.0] * num_years,
        "pipe_decomm_cost_per_user": [0.0] * num_years,
        "peak_kw_winter_headroom": [np.inf] * num_years,
        "peak_kw_summer_headroom": [np.inf] * num_years,
        "aircon_percent_adoption_pre_npa": [0.0] * num_years,
        "is_scattershot": [True] * num_years,
    })


def compute_hp_converts_from_df(year: int, df: pl.DataFrame, cumulative: bool = False, npa_only: bool = False) -> int:
    year_filter = pl.col("project_year") <= pl.lit(year) if cumulative else pl.col("project_year") == pl.lit(year)
    npa_filter = ~pl.col("is_scattershot") if npa_only else pl.lit(True)
    return int(df.filter(year_filter & npa_filter).select(pl.col("num_converts")).sum().item())


def compute_npa_install_costs_from_df(year: int, df: pl.DataFrame, npa_install_cost: float) -> float:
    # TODO: should this also include pipe_decomm_costs?
    return npa_install_cost * compute_hp_converts_from_df(year, df, cumulative=False, npa_only=True)


def compute_npa_pipe_cost_avoided_from_df(year: int, df: pl.DataFrame) -> float:
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
