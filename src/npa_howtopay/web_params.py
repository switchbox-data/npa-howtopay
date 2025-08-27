from attrs import define
from npa_project import NpaProject


@define
class WebParams:
    npa_num_projects: int
    npa_households_per_project: int
    npa_pipe_value_per_user: float
    npa_pipe_decomm_cost_per_user: float
    non_npa_scattershot_electrifiction_users_per_year: int
    peak_kw_winter_headroom_per_project: float
    peak_kw_summer_headroom_per_project: float
    aircon_percent_adoption_pre_npa: float
    # stuff_for_producing_ratebase_baseline

    def get_npa_projects(self) -> list[NpaProject]:
        pass
