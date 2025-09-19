---
author:
- Switchbox
authors:
- id: 1
  letter: a
  metadata: {}
  name:
    family: Switchbox
    literal: Switchbox
  number: 1
biblio-config: true
by-author:
- id: 1
  letter: a
  metadata: {}
  name:
    family: Switchbox
    literal: Switchbox
  number: 1
date: 2025-09-15
labels:
  abstract: Abstract
  affiliations: Affiliations
  authors: Author
  description: Description
  doi: Doi
  keywords: Keywords
  modified: Modified
  published: Published
  related_formats: Other Formats
title: Formulas - NPA How to Pay Model
toc-title: Table of contents
---

This document contains the  formulas implemented in the
`npa-howtopay` model, organized by functional area.

## Variable Definitions

### Customer and Conversion Variables
| Variable | Description | Units |
|----------|-------------|-------|
| $N_{gas}(t)$ | Number of gas customers in year $t$ | customers |
| $N_{gas,init}$ | Initial number of gas customers | customers |
| $N_{electric}(t)$ | Number of electric customers in year $t$ | customers |
| $N_{electric,init}$ | Initial number of electric customers | customers |
| $N_{converts}(t)$ | Cumulative number of converted households including non-npa households through year $t$ | customers |
| $N_{NPAconverts}(t)$ | Sum of NPA households converters in year $t$ (excludes scattershot electrification) | customers |
| $N_{customers}(t)$ | Total number of customers in year $t$ | customers |

### Energy Usage and Efficiency Variables
| Variable | Description | Units |
|----------|-------------|-------|
| $U_{gas}(t)$ | Total gas usage in therms in year $t$ | therms |
| $U_{electric}(t)$ | Total electric usage in kWh in year $t$ | kWh |
| $Q_{heating,therms}$ | Average per-customer heating need in therms | therms/customer |
| $Q_{electric,kWh}$ | Average per-customer electric need in kWh | kWh/customer |
| $K_{therm\to kWh}$ | Conversion factor from therms to kWh | kWh/therm |
| $\eta_{HP}$ | Heat pump efficiency | dimensionless |

### Gas System Variables
| Variable | Description | Units |
|----------|-------------|-------|
| $C_{gas,var}(t)$ | Gas variable costs in year $t$ | $ |
| $C_{gas,fixed}(t)$ | Gas fixed costs in year $t$ | $ |
| $C_{gas,overhead}(t)$ | Gas fixed overhead costs in year $t$ | $ |
| $C_{gas,maintenance}(t)$ | Gas maintenance costs in year $t$ | $ |
| $C_{gas,NPA,opex}(t)$ | Gas NPA OPEX in year $t$ | $ |
| $C_{gas,opex}(t)$ | Gas OPEX costs in year $t$ | $ |
| $R_{gas}(t)$ | Gas revenue requirement in year $t$ | $ |
| $RB_{gas}(t)$ | Gas ratebase in year $t$ | $ |
| $ror_{gas}$ | Gas rate of return | % |
| $D_{gas}(t)$ | Gas depreciation expense in year $t$ | $ |
| $P_{gas}(t)$ | Gas generation cost per therm in year $t$ | $/therm |

### Electric System Variables
| Variable | Description | Units |
|----------|-------------|-------|
| $C_{electric,var}(t)$ | Electric variable costs in year $t$ | $ |
| $C_{electric,fixed}(t)$ | Electric fixed costs in year $t$ | $ |
| $C_{electric,overhead}(t)$ | Electric fixed overhead costs in year $t$ | $ |
| $C_{electric,maintenance}(t)$ | Electric maintenance costs in year $t$ | $ |
| $C_{electric,NPA,opex}(t)$ | Electric NPA OPEX in year $t$ | $ |
| $C_{electric,opex}(t)$ | Electric OPEX costs in year $t$ | $ |
| $R_{electric}(t)$ | Electric revenue requirement in year $t$ | $ |
| $RB_{electric}(t)$ | Electric ratebase in year $t$ | $ |
| $ror_{electric}$ | Electric rate of return | % |
| $D_{electric}(t)$ | Electric depreciation expense in year $t$ | $ |
| $P_{electric}(t)$ | Electricity generation cost per kWh in year $t$ | $/kWh |
| $P_{peak,kw}$| Distribution cost per peak kW increase | $/kWh |

### Revenue and Inflation Variables
| Variable | Description | Units |
|----------|-------------|-------|
| $R(t)$ | Revenue requirement in year $t$ | $ |
| $R_{adj}(t)$ | Inflation-adjusted revenue requirement in year $t$ | $ |
| $R_{electric,adj}(t)$ | Inflation-adjusted electric revenue requirement in year $t$ | $ |
| $R_{gas,adj}(t)$ | Inflation-adjusted gas revenue requirement in year $t$ | $ |
| $d$ | Discount rate | % |
| $t_0$ | Start year | year |

### Tariff and Billing Variables
| Variable | Description | Units |
|----------|-------------|-------|
| $C_{electric,fixed,per\_customer}$ | Electric fixed charge per customer (user input) | $/customer |
| $C_{electric,var,kWh}(t)$ | Electric volumetric tariff per kWh in year $t$ | $/kWh |
| $C_{gas,fixed,per\_customer}$ | Gas fixed charge per customer (user input) | $/customer |
| $C_{gas,var,therm}(t)$ | Gas volumetric tariff per therm in year $t$ | $/therm |
| $B_{per\_customer}(t)$ | Bill per customer in year $t$ | $/customer |
| $B_{electric,converts}(t)$ | Electric bill per customer for converts in year $t$ | $/customer |
| $B_{electric,nonconverts}(t)$ | Electric bill per customer for non-converts in year $t$ | $/customer |
| $B_{total,converts}(t)$ | Total bill per customer for converts in year $t$ | $/customer |
| $B_{total,nonconverts}(t)$ | Total bill per customer for non-converts in year $t$ | $/customer |
| $B_{gas,nonconverts}(t)$ | Gas bill per customer for non-converts in year $t$ | $/customer |

### Depreciation and Project Variables
| Variable | Description | Units |
|----------|-------------|-------|
| $f_{dep}(t, t_p, L)$ | Depreciation fraction for project $p$ in year $t$ | dimensionless |
| $RB(t)$ | Total ratebase in year $t$ | $ |
| $D(t)$ | Total depreciation expense in year $t$ | $ |
| $C_{maintenance}(t)$ | Total maintenance costs in year $t$ | $ |
| $t_p$ | Project year for project $p$ | year |
| $L_p$ | Depreciation lifetime for project $p$ | years |
| $C_p$ | Original cost of project $p$ | $ |
| $C_{p_{non-NPA}}$ | Original cost of non-NPA project $p$ | $ |
| $m_{pct}$ | Maintenance cost percentage | % |

### Synthetic Initial Project Variables
| Variable | Description | Units |
|----------|-------------|-------|
| $W_{total}$ | Total weight for synthetic initial projects | dimensionless |
| $L$ | Depreciation lifetime | years |
| $RB_{init}$ | Initial ratebase | $ |
| $C_{est}$ | Estimated original cost per year | $/year |

## Gas System Calculations

### Gas Number of customers

The number of gas customers decreases over time as customers convert to
heat pumps. There is no growth in the number of gas customers:

$$N_{gas}(t) = N_{gas,init} - \sum_{i=1}^{t} N_{converts}(i)$$

**Variables:**

-   $N_{gas}(t)$: Number of gas customers in year $t$
-   $N_{gas,init}$: Initial number of gas customers
-   $N_{converts}(t)$: Sum of NPA households and scattershot converters
    in year $t$.

### Total Gas Usage

Total gas usage is calculated as the product of remaining gas customers
and their heating needs:

$$U_{gas}(t) = N_{gas}(t) \times Q_{heating,therms}$$

**Variables:**

-   $U_{gas}(t)$: Total gas usage in therms in year $t$
-   $Q_{heating,therms}$: Average per-customer heating need in therms

### Gas Variable Costs

Variable costs of the utility are based on total usage and generation
costs:

$$C_{gas,var}(t) = U_{gas}(t) \times P_{gas}(t)$$

**Variables:**

-   $C_{gas,var}(t)$: Gas variable costs in year $t$
-   $P_{gas}(t)$: Gas generation cost per therm in year $t$

### Gas Fixed Costs

Fixed costs include overhead, maintenance, and NPA OPEX:

$$C_{gas,fixed}(t) = C_{gas,overhead}(t) + C_{gas,maintenance}(t) + C_{gas,NPA,opex}(t)$$

**Variables:**

-   $C_{gas,fixed}(t)$: Gas fixed costs in year $t$
-   $C_{gas,overhead}(t)$: Gas fixed overhead costs in year $t$
-   $C_{gas,maintenance}(t)$: Gas maintenance costs in year $t$
-   $C_{gas,NPA,opex}(t)$: Gas NPA OPEX in year $t$

### Gas OPEX Costs

Total gas operating expenses combine fixed and variable costs:

$$C_{gas,opex}(t) = C_{gas,fixed}(t) + C_{gas,var}(t)$$

**Variables:**

-   $C_{gas,opex}(t)$: Gas OPEX costs in year $t$
-   $C_{gas,fixed}(t)$: Gas fixed costs in year $t$
-   $C_{gas,var}(t)$: Gas variable costs in year $t$

### Gas Avoided LPP Spending

The avoided LPP spending in a given year is the sum of the pipe value per customer times the number of converts for each NPA project in that year:

$$C_{gas,LPP,avoided}(t) = \sum_{p \in P(t)} N_{converts}(p) \times V_{pipe,user}(p)$$

**Variables:**

-   $C_{gas,LPP,avoided}(t)$: Gas LPP spending avoided in year $t$
-   $P(t)$: Set of NPA projects in year $t$
-   $N_{converts}(p)$: Number of converts in project $p$
-   $V_{pipe,user}(p)$: Pipe value per user for project $p$


### Gas Revenue Requirement

The gas revenue requirement includes ratebase return, OPEX, and
depreciation:

$$R_{gas}(t) = RB_{gas}(t) \times ror_{gas} + C_{gas,opex}(t) + D_{gas}(t)$$

**Variables:**

-   $R_{gas}(t)$: Gas revenue requirement in year $t$
-   $RB_{gas}(t)$: Gas ratebase in year $t$
-   $ror_{gas}$: Gas rate of return
-   $C_{gas,opex}(t)$: Gas OPEX costs in year $t$
-   $D_{gas}(t)$: Gas depreciation expense in year $t$

## Electric System Calculations

### Electric Number of customers

The number of electric customers is the initial number of electric
customers. There is no growth in the number of electric customers:
$$N_{electric}(t) = N_{electric,init}$$

**Variables:**

-   $N_{electric}(t)$: Number of electric customers in year $t$
-   $N_{electric,init}$: Initial number of electric customers


### Total Electric Usage

Electric usage includes both base electric needs and heating loads from
converts:

$$U_{electric}(t) = N_{electric,init} \times Q_{electric,kWh} + \frac{N_{converts}(t) \times Q_{heating,therms} \times K_{therm\to kWh}}{\eta_{HP}}$$

**Variables:**

-   $U_{electric}(t)$: Total electric usage in kWh in year $t$
-   $N_{electric,init}$: Initial number of electric customers
-   $N_{converts}(t)$: Cumulative electrification converts through year $t$
-   $Q_{electric,kWh}$: Average per-customer electric need in kWh
-   $Q_{heating,therms}$: Average per-customer heating need in therms
-   $K_{therm\to kWh}$: Conversion factor from therms to kWh
-   $\eta_{HP}$: Heat pump efficiency

### Electric Variable Costs

Electric utility variable costs are based on total usage and generation
costs:

$$C_{electric,var}(t) = U_{electric}(t) \times P_{electric}(t)$$

**Variables:**

-   $C_{electric,var}(t)$: Electric variable costs in year $t$
-   $U_{electric}(t)$: Total electric usage in kWh in year $t$
-   $P_{electric}(t)$: Electricity generation cost per kWh in year $t$

### Electric Fixed Costs

Electric fixed costs include overhead, maintenance, and NPA OPEX:

$$C_{electric,fixed}(t) = C_{electric,overhead}(t) + C_{electric,maintenance}(t) + C_{electric,NPA,opex}(t)$$

**Variables:**

-   $C_{electric,fixed}(t)$: Electric fixed costs in year $t$
-   $C_{electric,overhead}(t)$: Electric fixed overhead costs in year
    $t$
-   $C_{electric,maintenance}(t)$: Electric maintenance costs in year
    $t$
-   $C_{electric,NPA,opex}(t)$: Electric NPA OPEX in year $t$

### Electric Operating Expenses Costs

Total electric operating expenses combine fixed and variable costs:

$$C_{electric,opex}(t) = C_{electric,fixed}(t) + C_{electric,var}(t)$$

**Variables:**

-   $C_{electric,opex}(t)$: Electric OPEX costs in year $t$
-   $C_{electric,fixed}(t)$: Electric fixed costs in year $t$
-   $C_{electric,var}(t)$: Electric variable costs in year $t$

### Electric Revenue Requirement

The electric revenue requirement includes ratebase return, OPEX, and
depreciation:

$$R_{electric}(t) = RB_{electric}(t) \times ror_{electric} + C_{electric,opex}(t) + D_{electric}(t)$$

**Variables:**

-   $R_{electric}(t)$: Electric revenue requirement in year $t$
-   $RB_{electric}(t)$: Electric ratebase in year $t$
-   $ror_{electric}$: Electric rate of return
-   $C_{electric,opex}(t)$: Electric OPEX costs in year $t$
-   $D_{electric}(t)$: Electric depreciation expense in year $t$

### Electric Grid Upgrades

The cost of electric grid upgrades is determined by the peak kW increase from heat pumps and air conditioning, multiplied by a per-peak kW distribution cost:

$$C_{grid,upgrade}(t) = \Delta kW_{peak}(t) \times P_{peak,kw}$$

where the peak kW increase is:

$$\Delta kW_{peak}(t) = \sum_{p \in P(t)} \left[ N_{NPAconverts}(p) \times \left( kW_{HP,peak} + (kW_{AC,peak} \times (1 - a_{pre})) \right) \right]$$

**Variables:**

-   $C_{grid,upgrade}(t)$: Grid upgrade capital cost in year $t$
-   $\Delta kW_{peak}(t)$: Total peak kW increase in year $t$
-   $P_{peak,kw}$: Distribution cost per peak kW increase
-   $P(t)$: Set of NPA projects in year $t$
-   $N_{NPAconverts}(p)$: Number of converts in project $p$
-   $kW_{HP,peak}$: Peak kW per heat pump
-   $kW_{AC,peak}$: Peak kW per air conditioner
-   $a_{pre}$: Pre-NPA air conditioner adoption rate


## Bill Cost Calculations

### Inflation-Adjusted Revenue Requirement

Revenue requirements are adjusted for inflation using the discount rate:

$$R_{adj}(t) = \frac{R(t)}{(1 + d)^{t - t_0}}$$

**Variables:**

-   $R_{adj}(t)$: Inflation-adjusted revenue requirement in year $t$
-   $R(t)$: Revenue requirement in year $t$
-   $d$: Discount rate
-   $t_0$: Start year

### Bill Per customer

The basic bill per customer calculation averages the inflation-adjusted
revenue requirement over the number of customers:

$$B_{per\_customer}(t) = \frac{R_{adj}(t)}{N_{customers}(t)}$$

**Variables:**

-   $B_{per\_customer}(t)$: Bill per customer in year $t$
-   $R_{adj}(t)$: Inflation-adjusted revenue requirement in year $t$
-   $N_{customers}(t)$: Number of customers in year $t$

### Electric Fixed Charge Per customer

The fixed charge of customers bills is a model input. We hold this
constant over time:

-   $C_{electric,fixed,per\_customer}$: Electric fixed charge per
    customer in year $t$ (user input)

### Electric Customer Volumetric Tariff Per kWh

Electric volumetric tariffs are allocated per kWh on the total
inflation-adjusted revenue requirement minus the fixed charge revenue:

$$C_{electric,var,kWh}(t) =  \frac{(R_{electric,adj}(t) - C_{electric,fixed,per\_customer} \times N_{customers}(t))}{U_{electric}(t)}$$

**Variables:**

-   $C_{electric,var,kWh}(t)$: Electric volumetric tariff per kWh in
    year $t$
-   $U_{electric}(t)$: Total electric usage in kWh in year $t$
-   $R_{electric,adj}(t)$: Inflation-adjusted electric revenue
    requirement in year $t$
-   $C_{electric,fixed,per\_customer}$: Electric fixed charge per
    customer in year $t$ (user input)
-   $N_{customers}(t)$: Number of customers in year $t$

### Gas Fixed Charge Per customer

The fixed charge of customers bills is a model input. We hold this
constant over time:

-   $C_{gas,fixed,per\_customer}$: Gas fixed charge per customer in year
    $t$ (user input)

### Gas Customer Volumetric Tariff Per Therm

Gas volumetric tariffs are allocated per therm on the total
inflation-adjusted revenue requirement minus the fixed charge revenue:

$$C_{gas,var,therm}(t) =  \frac{(R_{gas,adj}(t) - C_{gas,fixed,per\_customer} \times N_{customers}(t))}{U_{gas}(t)}$$

**Variables:**

-   $C_{gas,var,therm}(t)$: Gas volumetric tariff per therm in year $t$
-   $R_{gas,adj}(t)$: Inflation-adjusted gas revenue requirement in year
    $t$
-   $C_{gas,fixed,per\_customer}(t)$: Gas fixed charge per customer in
    year $t$ (user input)
-   $N_{customers}(t)$: Number of customers in year $t$
-   $U_{gas}(t)$: Total gas usage in therms in year $t$

### Converts Electric Bill Per customer

Electric bills for converts include both base electric needs and heating
loads:

$$B_{electric,converts}(t) = C_{electric,fixed,per\_customer} + C_{electric,var,kWh}(t) \times \left(Q_{electric,kWh} + \frac{Q_{heating,therms} \times K_{therm\to kWh}}{\eta_{HP}}\right)$$

**Variables:**

-   $B_{electric,converts}(t)$: Electric bill per customer for converts
    in year $t$
-   $C_{electric,fixed,per\_customer}$: Electric fixed charge per customer (user input)
-   $C_{electric,var,kWh}(t)$: Electric volumetric tariff per kWh in year $t$
-   $Q_{electric,kWh}$: Average per-customer electric need in kWh
-   $Q_{heating,therms}$: Average per-customer heating need in therms
-   $K_{therm\to kWh}$: Conversion factor from therms to kWh
-   $\eta_{HP}$: Heat pump efficiency

### Non-Converts Electric Bill Per customer

Electric bills for non-converts include only base electric needs:

$$B_{electric,nonconverts}(t) = C_{electric,fixed,per\_customer} + C_{electric,var,kWh}(t) \times Q_{electric,kWh}$$

**Variables:**

-   $B_{electric,nonconverts}(t)$: Electric bill per customer for
    non-converts in year $t$
-   $C_{electric,fixed,per\_customer}$: Electric fixed charge per customer (user input)
-   $C_{electric,var,kWh}(t)$: Electric volumetric tariff per kWh in year $t$
-   $Q_{electric,kWh}$: Average per-customer electric need in kWh

### Converts Total Bill Per customer

Total bills for converts include both gas and electric components:

$$B_{total,converts}(t) = B_{electric,converts}(t)$$

**Variables:**

-   $B_{total,converts}(t)$: Total bill per customer for converts in
    year $t$
-   $B_{electric,converts}(t)$: Electric bill per customer for converts in year $t$

### Non-Converts Total Bill Per customer

Total bills for non-converts include both gas and electric components:

$$B_{total,nonconverts}(t) = B_{gas,nonconverts}(t) + B_{electric,nonconverts}(t)$$

**Variables:**

-   $B_{total,nonconverts}(t)$: Total bill per customer for non-converts
    in year $t$
-   $B_{gas,nonconverts}(t)$: Gas bill per customer for non-converts in
    year $t$
-   $B_{electric,nonconverts}(t)$: Electric bill per customer for non-converts in year $t$

## Depreciation and Inflation Calculations

### Ratebase Calculation

The depreciation fraction determines how much of a project's original
cost remains in the ratebase:

$$f_{dep}(t, t_p, L) = \max\left(0, 1 - \frac{t - t_p}{L}\right)$$

The total ratebase is the sum of all projects' remaining values:

$$RB(t) = \sum_{p} f_{dep}(t, t_p, L_p) \times C_p$$

**Variables:**

-   $f_{dep}(t, t_p, L)$: Depreciation fraction for project $p$ in year
    $t$
-   $RB(t)$: Total ratebase in year $t$
-   $t$: Current year
-   $t_p$: Project year for project $p$
-   $L$: Depreciation lifetime
-   $L_p$: Depreciation lifetime for project $p$
-   $C_p$: Original cost of project $p$

### Depreciation Expense

Annual depreciation expense uses straight-line depreciation:

$$D(t) = \sum_{p} \begin{cases}
\frac{C_p}{L_p} & \text{if } t_p < t \leq t_p + L_p \\
0 & \text{otherwise}
\end{cases}$$

**Variables:**

-   $D(t)$: Total depreciation expense in year $t$
-   $t$: Current year
-   $C_p$: Original cost of project $p$
-   $L_p$: Depreciation lifetime for project $p$
-   $t_p$: Project year for project $p$

### Maintenance Costs

Annual maintenance costs are calculated as a percentage of original
project costs for non-NPA capex projects still in service:

$$C_{maintenance}(t) = m_{pct} \times  \sum_{p} \begin{cases}
C_{p_{non-NPA}} & \text{if } t_p < t \leq t_p + L_p \\
0 & \text{otherwise}
\end{cases}$$

**Variables:**

-   $C_{maintenance}(t)$: Total maintenance costs in year $t$
-   $t$: Current year
-   $m_{pct}$: Maintenance cost percentage
-   $C_{p_{non-NPA}}$: Original cost of non-NPA project $p$
-   $t_p$: Project year for project $p$
-   $L_p$: Depreciation lifetime for project $p$

### Synthetic Initial Projects

For synthetic initial projects representing existing infrastructure, the
total weight calculation is:

$$W_{total} = \frac{L \times (L + 1)}{2 \times L} = \frac{L + 1}{2}$$

The estimated original cost per year is:

$$C_{est} = \frac{RB_{init}}{W_{total}}$$

This creates a table of synthetic project with uniform original costs of that would results in the inital ratebase value in year 0.
**Variables:**

-   $W_{total}$: Total weight for synthetic initial projects
-   $L$: Depreciation lifetime
-   $RB_{init}$: Initial ratebase
-   $C_{est}$: Estimated original cost per year
