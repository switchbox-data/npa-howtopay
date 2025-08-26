from attrs import define, field, validators
import numpy as np
import polars as pl


## All dataframes used by functions in this class will have the following columns:
# year: int
# num_converts: int
# pipe_value_per_user: float
# pipe_decomm_cost_per_user: float
# peak_kw_winter_headroom: float
# peak_kw_summer_headroom: float
# aircon_percent_adoption_pre_npa: float

# note: could represent scattershot electrification as a row with pipe_value_per_user and pipe_decomm_cost_per_user set to 0


@define
class NpaProject:
    year: int
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

    def to_df(self) -> pl.DataFrame:
        return pl.DataFrame({
            "year": [self.year],
            "num_converts": [self.num_converts],
            "pipe_value_per_user": [self.pipe_value_per_user],
            "pipe_decomm_cost_per_user": [self.pipe_decomm_cost_per_user],
            "peak_kw_winter_headroom": [self.peak_kw_winter_headroom],
            "peak_kw_summer_headroom": [self.peak_kw_summer_headroom],
            "aircon_percent_adoption_pre_npa": [self.aircon_percent_adoption_pre_npa],
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

    return pl.DataFrame({
        "year": project_years,
        "num_converts": [num_converts_per_project] * total_num_projects,
        "pipe_value_per_user": [pipe_value_per_user] * total_num_projects,
        "pipe_decomm_cost_per_user": [pipe_decomm_cost_per_user] * total_num_projects,
        "peak_kw_winter_headroom": [peak_kw_winter_headroom_per_project] * total_num_projects,
        "peak_kw_summer_headroom": [peak_kw_summer_headroom_per_project] * total_num_projects,
        "aircon_percent_adoption_pre_npa": [aircon_percent_adoption_pre_npa] * total_num_projects,
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
        "year": years,
        "num_converts": converts_per_year,
        "pipe_value_per_user": [0.0] * num_years,
        "pipe_decomm_cost_per_user": [0.0] * num_years,
        "peak_kw_winter_headroom": [np.inf] * num_years,
        "peak_kw_summer_headroom": [np.inf] * num_years,
        "aircon_percent_adoption_pre_npa": [0.0] * num_years,
    })


def compute_num_converts_from_df(df: pl.DataFrame, year: int) -> int:
    return df.filter(pl.col("year") <= year).sum("num_converts").item()


def compute_exiting_pipe_value_from_df(year: int, df: pl.DataFrame) -> float:
    return df.filter(pl.col("year") == year).select(pl.col("pipe_value_per_user") * pl.col("num_converts")).sum().item()


def compute_pipe_decomm_cost_from_df(year: int, df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.filter(pl.col("year") == year)
        .select(pl.col("pipe_decomm_cost_per_user") * pl.col("num_converts"))
        .sum()
        .item()
    )
