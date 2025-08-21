from attrs import define

import polars as pl


## All dataframes used by functions in this class will have the following columns:
# year: int
# num_converts: int
# pipe_value_per_user: float
# pipe_decomm_cost_per_user: float

# note: could represent scattershot electrification as a row with pipe_value_per_user and pipe_decomm_cost_per_user set to 0


def compute_num_converts_from_df(df: pl.DataFrame, year: int) -> int:
    return df.filter(pl.col("year") <= year).sum("num_converts")


def compute_avoided_pipe_costs_from_df(df: pl.DataFrame, year: int) -> float:
    # wrong, needs to multiply by num_converts
    # return df.filter(pl.col("year") == year).sum("pipe_value_per_user")
    pass


def compute_pipe_decomm_cost_from_df(df: pl.DataFrame) -> pl.DataFrame:
    pass
