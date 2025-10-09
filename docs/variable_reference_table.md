# Input Parameter Reference Table

## Pipeline Economics

| YAML Name | Display Label | Type | Description |
|-----------|---------------|------|-------------|
| `pipe_value_per_user` | Pipeline replacement cost | float | Pipeline replacement cost per NPA household |
| `pipeline_depreciation_lifetime` | Pipeline depreciation | int | Number of years over which pipeline assets are depreciated for accounting purposes |
| `pipeline_maintenance_cost_pct` | Maintenance cost (%) | float | Annual maintenance costs as a percentage of total pipeline value |

## NPA Program

| YAML Name | Display Label | Type | Description |
|-----------|---------------|------|-------------|
| `npa_install_costs_init` | NPA cost per household | float | Initial cost per household to install NPA equipment (excluding any incentive programs). Cost will grow annually by the cost inflation rate. |
| `npa_projects_per_year` | NPA projects per year | int | Number of NPA projects completed annually |
| `num_converts_per_project` | Conversions per project | int | Number of household conversions included in each NPA project |
| `npa_year_start` | NPA start year | int | Year NPA projects start |
| `npa_year_end` | NPA end year | int | Year NPA projects end. After the year, the model assumes no more NPA projects are completed. |
| `npa_lifetime` | NPA lifetime (years) | int | Expected operational lifetime of NPA equipment |
| `hp_efficiency` | HP efficiency | int | Heat pump coefficient of performance (COP) - units of heat per unit of electricity. Used to estimate additional electric demand after conversion |
| `water_heater_efficiency` | Water heater efficiency | int | Water heater efficiency - units of heat per unit of electricity. Used to estimate additional electric demand after conversion |
| `aircon_percent_adoption_pre_npa` | Aircon percent adoption pre-NPA | float | Percentage of households that already have air conditioning before NPA |
| `peak_kw_summer_headroom` | Summer peak headroom (kW) | float | Peak headroom in summer for the grid feeding these households |
| `peak_kw_winter_headroom` | Winter peak headroom (kW) | float | Peak headroom in winter for the grid feeding these households |

## Electric Utility

| YAML Name | Display Label | Type | Description |
|-----------|---------------|------|-------------|
| `electric_num_users_init` | Number of users | float | Initial number of customers served by electric utility |
| `scattershot_electrification_users_per_year` | Scattershot electrification users per year | int | Number of customers who electrified each year, independent of NPAs. This increases overall electric demand and reduces the number of gas customers but has no impact on NPAs or grid upgrades. It is held constant in the BAU scenario. |
| `baseline_non_npa_ratebase_growth` | Baseline non-NPA ratebase growth | float | Annual growth rate of utility ratebase excluding NPA investments |
| `electric_default_depreciation_lifetime` | Electric default depreciation lifetime | int | Default number of years over which electric utility assets are depreciated (excluding NPAs). Used to estimate depreciation for synthetic initial capex projects that would result in the initial ratebase. |
| `electric_maintenance_cost_pct` | Electric maintenance cost (%) | float | Annual maintenance costs as percentage of electric utility ratebase (excluding NPAs) |
| `electricity_generation_cost_per_kwh_init` | Electricity generation cost per kWh | float | Cost per kilowatt-hour of electricity generation in the initial year. This cost will grow annually by the cost inflation rate. |
| `electric_ratebase_init` | Electric ratebase | float | Initial value of electric utility's ratebase (total assets) |
| `electric_ror` | Rate of return (%) | float | Total rate of return, which is a combination of return on capital and return on debt for electric utility investments (after taxes) |
| `electric_fixed_overhead_costs` | Electric fixed overhead costs | float | Fixed annual overhead costs for electric utility |
| `electric_user_bill_fixed_charge` | Customer bill annual fixed charge (dollars) | int | Annual fixed charge per customer (dollars) |
| `grid_upgrade_depreciation_lifetime` | Grid upgrade depreciation lifetime | int | Depreciation lifetime for grid infrastructure upgrades |
| `per_user_electric_need_kwh` | Per user electric need (kWh) | float | Average annual electricity consumption per customer in kilowatt-hours |
| `aircon_peak_kw` | Aircon peak kW | float | Peak energy consumption of a household's new air conditioning unit. Used to estimate additional summer electric demand for converters without AC prior to NPA. |
| `hp_peak_kw` | Heat pump peak kW | float | Maximum electrical demand of new heat pump during peak operation |
| `distribution_cost_per_peak_kw_increase_init` | Distribution cost per peak kW increase | float | Cost to increase grid capacity by one kilowatt of peak demand. This cost will grow annually by the cost inflation rate. |

## Gas Utility

| YAML Name | Display Label | Type | Description |
|-----------|---------------|------|-------------|
| `gas_num_users_init` | Number of users | float | Initial number of customers served by gas utility |
| `gas_ratebase_init` | Gas ratebase | float | Initial value of gas utility's ratebase (total assets) |
| `gas_ror` | Rate of return (%) | float | Total rate of return, which is a combination of return on capital and return on debt for gas utility investments (after taxes) |
| `gas_fixed_overhead_costs` | Gas fixed overhead costs | float | Fixed annual overhead costs for gas utility. These costs will grow annually by the cost inflation rate. |
| `gas_bau_lpp_costs_per_year` | Gas BAU pipeline replacement costs per year | float | Gas pipeline replacement costs per year without any NPA projects (BAU). These costs will grow annually by the cost inflation rate. |
| `baseline_non_lpp_ratebase_growth` | Baseline non-LPP ratebase growth | float | Annual growth rate of gas utility ratebase excluding pipeline replacements |
| `non_lpp_depreciation_lifetime` | Non-pipeline depreciation lifetime | int | Depreciation lifetime for non-pipeline gas utility assets |
| `gas_user_bill_fixed_charge` | Customer bill annual fixed charge (dollars) | int | Annual fixed charge per customer (dollars) |
| `gas_generation_cost_per_therm_init` | Gas generation cost per therm | int | Cost per therm of natural gas in the initial year. These costs will grow annually by the cost inflation rate. |
| `per_user_heating_need_therms` | Per user heating need (therms) | float | Average annual heating demand per customer in therms |
| `per_user_water_heating_need_therms` | Per user water heating need (therms) | float | Average annual water heating demand per customer in therms |

## Financial Parameters

| YAML Name | Display Label | Type | Description |
|-----------|---------------|------|-------------|
| `cost_inflation_rate` | Cost inflation rate (%) | float | Nominal annual growth rate applied to costs and expenses |
| `construction_inflation_rate` | Construction inflation rate (%) | float | Nominal annual growth rate applied to construction costs |
| `real_dollar_discount_rate` | Inflation adjustment rate (%) | float | Rate at which future costs and expenses are discounted to present results in today's dollars |
| `npv_discount_rate` | NPV discount rate (%) | float | Real discount rate for calculating net present value of capex projects (used for performance incentive scenario) |
| `performance_incentive_pct` | Performance incentive percentage (%) | float | Percentage of savings (avoided LPP spending) on which gas utility receives a performance incentive (used for performance incentive scenario) |
| `incentive_payback_period` | Incentive payback period (years) | int | Number of years to pay incentives (used for performance incentive scenario) |

## Shared Parameters

| YAML Name | Display Label | Type | Description |
|-----------|---------------|------|-------------|
| `start_year` | Start year | int | First year of the analysis period |
| `end_year` | End year | int | Last year of the analysis period |
