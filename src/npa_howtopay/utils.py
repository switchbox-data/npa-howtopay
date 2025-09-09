import polars as pl
import matplotlib.pyplot as plt
from typing import Optional


def plot_utility_metric(
    plt_df: pl.DataFrame,
    column: str,
    title: str,
    y_label_unit: str = "$",
    scenario_colors: Optional[dict] = None,
    show_absolute: bool = False,
    save_dir: Optional[str] = None,
) -> None:
    """
    Generic utility plotting function for faceted plots (Gas/Electric)

    Args:
        plt_df: DataFrame with utility data in long format
        column: Column name to plot
        title: Title for the plot
        y_label_unit: Unit for y-axis label (e.g., "$", "$/unit", "$/kWh")
        scenario_colors: Dictionary mapping scenario_id to colors
        show_absolute: Whether to show absolute values or deltas
        save_dir: Directory to save the plot (optional)
    """
    if scenario_colors is None:
        scenario_colors = {}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Define line styles to cycle through
    line_styles = ["-", "--", "-.", ":", "-", "--", "-.", ":"]

    # Determine y-axis label based on show_absolute parameter
    y_label = f"Absolute Value ({y_label_unit})" if show_absolute else f"Delta ({y_label_unit})"

    # Gas facet
    ax1.set_title("GAS", fontsize=14, fontweight="bold")
    gas_data = plt_df.filter(pl.col("utility_type") == "gas")

    for i, scenario in enumerate(gas_data["scenario_id"].unique()):
        color = scenario_colors.get(scenario, "#666666")
        linestyle = line_styles[i % len(line_styles)]
        scenario_data = gas_data.filter(pl.col("scenario_id") == scenario)
        ax1.plot(
            scenario_data["year"],
            scenario_data[column],
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
            scenario_data[column],
            color=color,
            linestyle=linestyle,
            label=scenario,
            linewidth=2,
        )

    ax2.set_xlabel("Year")
    ax2.set_ylabel(y_label)
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    title_suffix = " (Absolute Values)" if show_absolute else "(Delta from BAU)"
    plt.suptitle(f"{title}{title_suffix}", fontsize=16, fontweight="bold")
    plt.tight_layout()

    if save_dir:
        value_type = "absolute" if show_absolute else "delta"
        # Create filename from title (lowercase, replace spaces with underscores)
        filename_base = title.lower().replace(" ", "_")
        filename = f"{filename_base}_{value_type}.png"
        save_path = f"{save_dir}/{filename}"
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


def plot_revenue_requirements(
    plt_df: pl.DataFrame, scenario_colors: dict, show_absolute: bool = False, save_dir: Optional[str] = None
) -> None:
    """Utility Revenue Requirements - Faceted"""
    plot_utility_metric(
        plt_df=plt_df,
        column="inflation_adjusted_revenue_requirement",
        title="Utility Revenue Requirements",
        y_label_unit="$",
        scenario_colors=scenario_colors,
        show_absolute=show_absolute,
        save_dir=save_dir,
    )


def plot_volumetric_tariff(
    plt_df: pl.DataFrame, scenario_colors: dict, show_absolute: bool = False, save_dir: Optional[str] = None
) -> None:
    """Volumetric Tariff - Faceted"""
    plot_utility_metric(
        plt_df=plt_df,
        column="variable_cost",
        title="Volumetric Tariff",
        y_label_unit="$/unit",
        scenario_colors=scenario_colors,
        show_absolute=show_absolute,
        save_dir=save_dir,
    )


def plot_ratebase(
    plt_df: pl.DataFrame, scenario_colors: dict, show_absolute: bool = False, save_dir: Optional[str] = None
) -> None:
    """Ratebase - Faceted"""
    plot_utility_metric(
        plt_df=plt_df,
        column="ratebase",
        title="Ratebase",
        y_label_unit="$",
        scenario_colors=scenario_colors,
        show_absolute=show_absolute,
        save_dir=save_dir,
    )


def plot_depreciation_accruals(
    plt_df: pl.DataFrame, scenario_colors: dict, show_absolute: bool = False, save_dir: Optional[str] = None
) -> None:
    """Depreciation Accruals - Faceted"""
    plot_utility_metric(
        plt_df=plt_df,
        column="depreciation_expense",
        title="Depreciation Accruals",
        y_label_unit="$",
        scenario_colors=scenario_colors,
        show_absolute=show_absolute,
        save_dir=save_dir,
    )


def plot_user_bills_converts(
    plt_df: pl.DataFrame, scenario_colors: dict, show_absolute: bool = False, save_dir: Optional[str] = None
) -> None:
    """User Bills and Converts - Faceted"""
    plot_utility_metric(
        plt_df=plt_df,
        column="converts_bill_per_user",
        title="User Bills and Converts",
        y_label_unit="$",
        scenario_colors=scenario_colors,
        show_absolute=show_absolute,
        save_dir=save_dir,
    )


def plot_user_bills_nonconverts(
    plt_df: pl.DataFrame, scenario_colors: dict, show_absolute: bool = False, save_dir: Optional[str] = None
) -> None:
    """User Bills and Nonconverts - Faceted"""
    plot_utility_metric(
        plt_df=plt_df,
        column="nonconverts_bill_per_user",
        title="User Bills and Nonconverts",
        y_label_unit="$",
        scenario_colors=scenario_colors,
        show_absolute=show_absolute,
        save_dir=save_dir,
    )


def plot_total_bills(delta_bau_df: pl.DataFrame, scenario_colors: dict, save_dir: Optional[str] = None) -> None:
    """Total Bills - Faceted"""
    if scenario_colors is None:
        scenario_colors = {}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Define line styles to cycle through
    line_styles = ["-", "--", "-.", ":", "-", "--", "-.", ":"]

    # Determine y-axis label based on show_absolute parameter
    y_label = "User bills (total)"

    # Gas facet
    ax1.set_title("Converts", fontsize=14, fontweight="bold")
    # gas_data = plt_df.filter(pl.col("utility_type") == "gas")

    for i, scenario in enumerate(delta_bau_df["scenario_id"].unique()):
        color = scenario_colors.get(scenario, "#666666")
        linestyle = line_styles[i % len(line_styles)]
        scenario_data = delta_bau_df.filter(pl.col("scenario_id") == scenario)
        ax1.plot(
            scenario_data["year"],
            scenario_data["converts_total_bill_per_user"],
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
    ax2.set_title("Nonconverts", fontsize=14, fontweight="bold")
    # electric_data = plt_df.filter(pl.col("utility_type") == "electric")

    for i, scenario in enumerate(delta_bau_df["scenario_id"].unique()):
        color = scenario_colors.get(scenario, "#666666")
        linestyle = line_styles[i % len(line_styles)]
        scenario_data = delta_bau_df.filter(pl.col("scenario_id") == scenario)
        ax2.plot(
            scenario_data["year"],
            scenario_data["nonconverts_total_bill_per_user"],
            color=color,
            linestyle=linestyle,
            label=scenario,
            linewidth=2,
        )

    ax2.set_xlabel("Year")
    ax2.set_ylabel(y_label)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    title = "Total User Bills"
    title_suffix = "(Delta from BAU)"
    plt.suptitle(f"{title}{title_suffix}", fontsize=16, fontweight="bold")
    plt.tight_layout()

    if save_dir:
        value_type = "delta"
        # Create filename from title (lowercase, replace spaces with underscores)
        filename_base = title.lower().replace(" ", "_")
        filename = f"{filename_base}_{value_type}.png"
        save_path = f"{save_dir}/{filename}"
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
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
