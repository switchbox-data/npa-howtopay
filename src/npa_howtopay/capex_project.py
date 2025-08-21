class CapexProject:
    project_year: int
    original_cost: float
    depreciation_lifetime: int
    # depreciation_schedule: str # "straight line" or "accelerated"

    @property
    def get_depreciation(self, year: int) -> float:
        if self.project_year < year <= self.project_year + self.depreciation_lifetime:
            return self.original_cost / self.depreciation_lifetime
        else:
            return 0


def non_lpp_gas_capex_projects(year: int, input_params: InputParams) -> list[CapexProject]:
    pass


def lpp_gas_capex_projects(year: int, input_params: InputParams, npas_this_year: NpaProject) -> list[CapexProject]:
    pass


def non_npa_electric_capex_projects(year: int, input_params: InputParams) -> list[CapexProject]:
    pass


def grid_upgrade_capex_projects(year: int, input_params: InputParams, npas_this_year: NpaProject) -> list[CapexProject]:
    pass
