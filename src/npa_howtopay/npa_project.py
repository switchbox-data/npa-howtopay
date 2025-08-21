from attrs import define


@define
class NpaProject:
    year: int
    num_converts: int
    pipe_value_per_user: float
    pipe_decomm_cost_per_user: float
    # npa_install_costs: float # maybe? is this in 2025 dollars?
