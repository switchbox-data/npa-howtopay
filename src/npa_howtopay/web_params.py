from attrs import define


@define
class WebParams:
    npa_num_projects: int
    npa_households_per_project: int
    npa_pipe_value_per_user: float
    npa_pipe_decomm_cost_per_user: float
    non_npa_scattershot_electrifiction_users_per_year: int
    # stuff_for_producing_ratebase_baseline
