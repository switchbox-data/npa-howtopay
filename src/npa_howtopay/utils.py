import polars as pl
import matplotlib.pyplot as plt


def plot_revenue_requirements(plt_df: pl.DataFrame, scenario_colors: dict, show_absolute: bool = False) -> None:
    """Utility Revenue Requirements - Faceted"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Define line styles to cycle through
    line_styles = ["-", "--", "-.", ":", "-", "--", "-.", ":"]

    # Determine y-axis label based on show_absolute parameter
    y_label = "Absolute Value ($)" if show_absolute else "Delta ($)"

    # Gas facet
    ax1.set_title("GAS", fontsize=14, fontweight="bold")
    gas_data = plt_df.filter(pl.col("utility_type") == "gas")

    for i, scenario in enumerate(gas_data["scenario_id"].unique()):
        color = scenario_colors.get(scenario, "#666666")
        linestyle = line_styles[i % len(line_styles)]
        scenario_data = gas_data.filter(pl.col("scenario_id") == scenario)
        ax1.plot(
            scenario_data["year"],
            scenario_data["inflation_adjusted_revenue_requirement"],
            color=color,
            linestyle=linestyle,
            label=scenario,
            linewidth=2,
        )

    ax1.set_xlabel("Year")
    ax1.set_ylabel(y_label)
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Electric facet
    ax2.set_title("ELECTRIC", fontsize=14, fontweight="bold")
    electric_data = plt_df.filter(pl.col("utility_type") == "electric")

    for i, scenario in enumerate(electric_data["scenario_id"].unique()):
        color = scenario_colors.get(scenario, "#666666")
        linestyle = line_styles[i % len(line_styles)]
        scenario_data = electric_data.filter(pl.col("scenario_id") == scenario)
        ax2.plot(
            scenario_data["year"],
            scenario_data["inflation_adjusted_revenue_requirement"],
            color=color,
            linestyle=linestyle,
            label=scenario,
            linewidth=2,
        )

    ax2.set_xlabel("Year")
    ax2.set_ylabel(y_label)
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    title_suffix = " (Absolute Values)" if show_absolute else ""
    plt.suptitle(f"Utility Revenue Requirements{title_suffix}", fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_volumetric_tariff(plt_df: pl.DataFrame, scenario_colors: dict, show_absolute: bool = False) -> None:
    """Volumetric Tariff - Faceted"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Define line styles to cycle through
    line_styles = ["-", "--", "-.", ":", "-", "--", "-.", ":"]

    # Determine y-axis label based on show_absolute parameter
    y_label = "Absolute Value ($/unit)" if show_absolute else "Delta ($/unit)"

    # Gas facet
    ax1.set_title("GAS", fontsize=14, fontweight="bold")
    gas_data = plt_df.filter(pl.col("utility_type") == "gas")

    for i, scenario in enumerate(gas_data["scenario_id"].unique()):
        color = scenario_colors.get(scenario, "#666666")
        linestyle = line_styles[i % len(line_styles)]
        scenario_data = gas_data.filter(pl.col("scenario_id") == scenario)
        ax1.plot(
            scenario_data["year"],
            scenario_data["variable_cost"],
            color=color,
            linestyle=linestyle,
            label=scenario,
            linewidth=2,
        )

    ax1.set_xlabel("Year")
    ax1.set_ylabel(y_label)
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Electric facet
    ax2.set_title("ELECTRIC", fontsize=14, fontweight="bold")
    electric_data = plt_df.filter(pl.col("utility_type") == "electric")

    for i, scenario in enumerate(electric_data["scenario_id"].unique()):
        color = scenario_colors.get(scenario, "#666666")
        linestyle = line_styles[i % len(line_styles)]
        scenario_data = electric_data.filter(pl.col("scenario_id") == scenario)
        ax2.plot(
            scenario_data["year"],
            scenario_data["variable_cost"],
            color=color,
            linestyle=linestyle,
            label=scenario,
            linewidth=2,
        )

    ax2.set_xlabel("Year")
    ax2.set_ylabel(y_label)
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    title_suffix = " (Absolute Values)" if show_absolute else ""
    plt.suptitle(f"Volumetric Tariff{title_suffix}", fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_ratebase(plt_df: pl.DataFrame, scenario_colors: dict, show_absolute: bool = False) -> None:
    """Ratebase - Faceted"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Define line styles to cycle through
    line_styles = ["-", "--", "-.", ":", "-", "--", "-.", ":"]

    # Determine y-axis label based on show_absolute parameter
    y_label = "Absolute Value ($)" if show_absolute else "Delta ($)"

    # Gas facet
    ax1.set_title("GAS", fontsize=14, fontweight="bold")
    gas_data = plt_df.filter(pl.col("utility_type") == "gas")

    for i, scenario in enumerate(gas_data["scenario_id"].unique()):
        color = scenario_colors.get(scenario, "#666666")
        linestyle = line_styles[i % len(line_styles)]
        scenario_data = gas_data.filter(pl.col("scenario_id") == scenario)
        ax1.plot(
            scenario_data["year"],
            scenario_data["ratebase"],
            color=color,
            linestyle=linestyle,
            label=scenario,
            linewidth=2,
        )

    ax1.set_xlabel("Year")
    ax1.set_ylabel(y_label)
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Electric facet
    ax2.set_title("ELECTRIC", fontsize=14, fontweight="bold")
    electric_data = plt_df.filter(pl.col("utility_type") == "electric")

    for i, scenario in enumerate(electric_data["scenario_id"].unique()):
        color = scenario_colors.get(scenario, "#666666")
        linestyle = line_styles[i % len(line_styles)]
        scenario_data = electric_data.filter(pl.col("scenario_id") == scenario)
        ax2.plot(
            scenario_data["year"],
            scenario_data["ratebase"],
            color=color,
            linestyle=linestyle,
            label=scenario,
            linewidth=2,
        )

    ax2.set_xlabel("Year")
    ax2.set_ylabel(y_label)
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    title_suffix = " (Absolute Values)" if show_absolute else ""
    plt.suptitle(f"Ratebase{title_suffix}", fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_depreciation_accruals(plt_df: pl.DataFrame, scenario_colors: dict, show_absolute: bool = False) -> None:
    """Depreciation Accruals - Faceted"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Define line styles to cycle through
    line_styles = ["-", "--", "-.", ":", "-", "--", "-.", ":"]

    # Determine y-axis label based on show_absolute parameter
    y_label = "Absolute Value ($)" if show_absolute else "Delta ($)"

    # Gas facet
    ax1.set_title("GAS", fontsize=14, fontweight="bold")
    gas_data = plt_df.filter(pl.col("utility_type") == "gas")

    for i, scenario in enumerate(gas_data["scenario_id"].unique()):
        color = scenario_colors.get(scenario, "#666666")
        linestyle = line_styles[i % len(line_styles)]
        scenario_data = gas_data.filter(pl.col("scenario_id") == scenario)
        ax1.plot(
            scenario_data["year"],
            scenario_data["depreciation_expense"],
            color=color,
            linestyle=linestyle,
            label=scenario,
            linewidth=2,
        )

    ax1.set_xlabel("Year")
    ax1.set_ylabel(y_label)
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Electric facet
    ax2.set_title("ELECTRIC", fontsize=14, fontweight="bold")
    electric_data = plt_df.filter(pl.col("utility_type") == "electric")

    for i, scenario in enumerate(electric_data["scenario_id"].unique()):
        color = scenario_colors.get(scenario, "#666666")
        linestyle = line_styles[i % len(line_styles)]
        scenario_data = electric_data.filter(pl.col("scenario_id") == scenario)
        ax2.plot(
            scenario_data["year"],
            scenario_data["depreciation_expense"],
            color=color,
            linestyle=linestyle,
            label=scenario,
            linewidth=2,
        )

    ax2.set_xlabel("Year")
    ax2.set_ylabel(y_label)
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    title_suffix = " (Absolute Values)" if show_absolute else ""
    plt.suptitle(f"Depreciation Accruals{title_suffix}", fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.show()


def transform_to_long_format(delta_bau_df: pl.DataFrame) -> pl.DataFrame:
    """Transform wide format (gas_/electric_ prefixes) to long format with utility_type column"""

    # Get all columns except year and scenario_id
    metric_cols = [col for col in delta_bau_df.columns if col not in ["year", "scenario_id"]]

    # Separate gas and electric columns
    gas_cols = [col for col in metric_cols if col.startswith("gas_")]
    electric_cols = [col for col in metric_cols if col.startswith("electric_")]

    # Sort the columns to ensure consistent order
    gas_cols = sorted(gas_cols)
    electric_cols = sorted(electric_cols)

    # Create explicit mapping dictionaries with special case handling
    gas_rename_map = {}
    for col in gas_cols:
        base_col = col.replace("gas_", "")
        # Special case: map both variable cost columns to "variable_cost"
        if base_col == "variable_cost_per_therm":
            gas_rename_map[col] = "variable_cost"
        else:
            gas_rename_map[col] = base_col

    electric_rename_map = {}
    for col in electric_cols:
        base_col = col.replace("electric_", "")
        # Special case: map both variable cost columns to "variable_cost"
        if base_col == "variable_cost_per_kwh":
            electric_rename_map[col] = "variable_cost"
        else:
            electric_rename_map[col] = base_col

    # Create gas dataframe with sorted columns
    gas_df = (
        delta_bau_df.select(["year", "scenario_id", *gas_cols])
        .rename(gas_rename_map)
        .with_columns(pl.lit("gas").alias("utility_type"))
    )

    # Create electric dataframe with sorted columns
    electric_df = (
        delta_bau_df.select(["year", "scenario_id", *electric_cols])
        .rename(electric_rename_map)
        .with_columns(pl.lit("electric").alias("utility_type"))
    )

    # Concatenate them
    long_df = pl.concat([gas_df, electric_df], how="vertical")

    return long_df
