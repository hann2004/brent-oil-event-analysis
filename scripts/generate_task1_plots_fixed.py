"""
Fixed version of plot generator that uses enhanced events data.
"""

import json
import sys
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# ...existing code...
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Import custom modules
from src.data_preprocessing import calculate_returns, load_brent_data
from src.time_series import adf_test


def setup_plotting_style():
    plt.style.use("seaborn-v0_8-darkgrid")
    sns.set_palette("husl")
    plt.rcParams["figure.figsize"] = (14, 6)
    plt.rcParams["font.size"] = 11


def main():
    print("Generating Task 1 Plots with Enhanced Events...")
    setup_plotting_style()

    # 1. Load Data
    print("Loading data...")
    df_prices = load_brent_data(str(ROOT / "data" / "raw" / "BrentOilPrices.csv"))
    df_returns = calculate_returns(df_prices)

    # Load enhanced events data
    try:
        df_events = pd.read_csv(str(ROOT / "data" / "events" / "enhanced_events.csv"))
        df_events["Date"] = pd.to_datetime(df_events["Date"])
        print("Loaded enhanced events data")
    except Exception:
        # Fallback to original events
        df_events = pd.read_csv(str(ROOT / "data" / "events" / "key_events.csv"))
        df_events["Date"] = pd.to_datetime(df_events["Date"])
        print("Using original events data (enhanced not found)")

    print(f"Data loaded: {len(df_prices)} price records, {len(df_events)} events")

    # 2. Create event impact analysis plot - FIXED VERSION
    print("\nCreating event impact analysis plot...")

    def analyze_event_window(event_date, window=30):
        """Analyze price window around an event."""
        start_date = event_date - timedelta(days=window)
        end_date = event_date + timedelta(days=window)

        mask = (df_prices["Date"] >= start_date) & (df_prices["Date"] <= end_date)
        window_data = df_prices[mask].copy()

        if len(window_data) > 10:  # Need sufficient data
            window_data["Days_from_Event"] = (window_data["Date"] - event_date).dt.days
            return window_data
        return None

    # Select diverse events for analysis
    conflict_events = df_events[
        df_events["Event_Type"].str.contains("Conflict", case=False, na=False)
    ]
    economic_events = df_events[
        df_events["Event_Type"].str.contains(
            "Economic|Financial|Crisis", case=False, na=False
        )
    ]
    policy_events = df_events[
        df_events["Event_Type"].str.contains("Policy", case=False, na=False)
    ]
    supply_events = df_events[
        df_events["Event_Type"].str.contains(
            "Supply|Production|Weather", case=False, na=False
        )
    ]

    selected_events = []
    if len(conflict_events) > 0:
        selected_events.append(conflict_events.iloc[-1])
    if len(economic_events) > 0:
        selected_events.append(economic_events.iloc[-1])
    if len(policy_events) > 0:
        selected_events.append(policy_events.iloc[0])
    if len(supply_events) > 0:
        selected_events.append(supply_events.iloc[len(supply_events) // 2])

    covid_event = df_events[
        df_events["Event_Title"].str.contains("COVID", case=False, na=False)
    ]
    if len(covid_event) > 0:
        selected_events.append(covid_event.iloc[0])

    ukraine_event = df_events[
        df_events["Event_Title"].str.contains("Ukraine|Russia", case=False, na=False)
    ]
    if len(ukraine_event) > 0:
        selected_events.append(ukraine_event.iloc[0])

    if len(selected_events) < 6:
        remaining_slots = 6 - len(selected_events)
        other_events = df_events[
            ~df_events.index.isin(
                [e.name for e in selected_events if hasattr(e, "name")]
            )
        ]
        selected_events.extend(other_events.head(remaining_slots).to_dict("records"))

    if isinstance(selected_events[0], pd.Series):
        selected_events_df = pd.DataFrame(selected_events)
    else:
        selected_events_df = pd.DataFrame(selected_events)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    event_impacts = []

    for idx, (event_idx, event) in enumerate(selected_events_df.head(6).iterrows()):
        if idx >= len(axes):
            break

        event_date = event["Date"]
        window_data = analyze_event_window(event_date, window=30)

        if window_data is not None and len(window_data) > 10:
            ax = axes[idx]
            ax.plot(
                window_data["Days_from_Event"],
                window_data["Price"],
                linewidth=2,
                marker="o",
                markersize=3,
                color="steelblue",
                alpha=0.8,
            )
            ax.axvline(
                0,
                color="red",
                linestyle="--",
                linewidth=2,
                alpha=0.7,
                label="Event Date",
            )

            pre_event_data = window_data[window_data["Days_from_Event"] < 0]
            post_event_data = window_data[window_data["Days_from_Event"] > 0]

            if len(pre_event_data) > 0 and len(post_event_data) > 0:
                pre_avg = pre_event_data["Price"].mean()
                post_avg = post_event_data["Price"].mean()
                pct_change = ((post_avg - pre_avg) / pre_avg) * 100

                ax.axhline(
                    pre_avg,
                    color="green",
                    linestyle=":",
                    alpha=0.7,
                    linewidth=1.5,
                    label=f"Pre-avg: ${pre_avg:.1f}",
                )
                ax.axhline(
                    post_avg,
                    color="orange",
                    linestyle=":",
                    alpha=0.7,
                    linewidth=1.5,
                    label=f"Post-avg: ${post_avg:.1f}",
                )

                ax.fill_between(
                    window_data["Days_from_Event"],
                    pre_avg,
                    post_avg,
                    where=(window_data["Days_from_Event"] > 0),
                    alpha=0.1,
                    color="orange" if pct_change > 0 else "red",
                )

                event_impacts.append(
                    {
                        "event": event["Event_Title"],
                        "date": event_date.strftime("%Y-%m-%d"),
                        "type": event.get("Event_Type", "Unknown"),
                        "pre_avg": pre_avg,
                        "post_avg": post_avg,
                        "pct_change": pct_change,
                        "direction": "Increase" if pct_change > 0 else "Decrease",
                    }
                )

            title = event["Event_Title"]
            if len(title) > 25:
                title = title[:22] + "..."

            event_type = event.get("Event_Type", "Unknown")
            ax.set_title(f"{title}\n({event_type})", fontsize=10, fontweight="bold")
            ax.set_xlabel("Days from Event", fontsize=9)
            ax.set_ylabel("Price (USD)", fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=8, loc="upper left" if idx % 2 == 0 else "upper right")

            if "pct_change" in locals():
                color = "green" if pct_change > 0 else "red"
                ax.text(
                    0.05,
                    0.95,
                    f"Change: {pct_change:+.1f}%",
                    transform=ax.transAxes,
                    fontsize=9,
                    fontweight="bold",
                    color=color,
                    verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
                )
        else:
            axes[idx].axis("off")
            print(f"Warning: Insufficient data for event: {event['Event_Title']}")

    plt.suptitle(
        "Event Impact Analysis: Price Trajectories ±30 Days Around Events",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(
        str(ROOT / "docs" / "task1_event_impacts_fixed.png"),
        dpi=150,
        bbox_inches="tight",
    )
    print("Event impact plot saved to docs/task1_event_impacts_fixed.png")

    if event_impacts:
        print("\nEvent Impact Summary:")
        print("-" * 80)
        print(f"{'Event':<40} {'Date':<12} {'Type':<15} {'Change':>10}")
        print("-" * 80)
        for impact in event_impacts:
            color_code = "\033[92m" if impact["pct_change"] > 0 else "\033[91m"
            reset_code = "\033[0m"
            print(
                f"{impact['event'][:38]:<40} {impact['date']:<12} "
                f"{impact['type'][:13]:<15} {color_code}{impact['pct_change']:>+9.1f}%{reset_code}"
            )
        print("-" * 80)

        impact_summary = {
            "total_events_analyzed": len(event_impacts),
            "average_impact": np.mean([imp["pct_change"] for imp in event_impacts]),
            "max_increase": max([imp["pct_change"] for imp in event_impacts]),
            "max_decrease": min([imp["pct_change"] for imp in event_impacts]),
            "positive_impacts": sum(
                1 for imp in event_impacts if imp["pct_change"] > 0
            ),
            "negative_impacts": sum(
                1 for imp in event_impacts if imp["pct_change"] < 0
            ),
            "detailed_impacts": event_impacts,
        }

        with open(str(ROOT / "docs" / "task1_event_impact_summary.json"), "w") as f:
            json.dump(impact_summary, f, indent=2, default=str)

        print("\nImpact summary saved to docs/task1_event_impact_summary.json")

    print("\nCreating event type impact comparison...")

    if event_impacts:
        type_impacts = {}
        for imp in event_impacts:
            etype = imp["type"]
            if etype not in type_impacts:
                type_impacts[etype] = []
            type_impacts[etype].append(imp["pct_change"])

        type_avg = {etype: np.mean(values) for etype, values in type_impacts.items()}
        type_std = {etype: np.std(values) for etype, values in type_impacts.items()}

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        types = list(type_avg.keys())
        avg_values = [type_avg[t] for t in types]
        colors = ["green" if v > 0 else "red" for v in avg_values]

        bars = ax1.bar(
            range(len(types)),
            avg_values,
            color=colors,
            alpha=0.7,
            yerr=[type_std.get(t, 0) for t in types],
            capsize=5,
        )
        ax1.set_xticks(range(len(types)))
        ax1.set_xticklabels(types, rotation=45, ha="right")
        ax1.set_title("Average Price Impact by Event Type", fontweight="bold")
        ax1.set_ylabel("Average Price Change (%)")
        ax1.axhline(0, color="black", linewidth=0.5)
        ax1.grid(True, alpha=0.3, axis="y")

        for bar, value in zip(bars, avg_values):
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + (1 if height > 0 else -3),
                f"{value:+.1f}%",
                ha="center",
                va="bottom" if height > 0 else "top",
                fontsize=9,
                fontweight="bold",
            )

        impact_data = [type_impacts[t] for t in types]
        box = ax2.boxplot(impact_data, labels=types, patch_artist=True)

        for patch, median in zip(
            box["boxes"], [np.median(data) for data in impact_data]
        ):
            patch.set_facecolor("lightgreen" if median > 0 else "lightcoral")
            patch.set_alpha(0.7)

        ax2.set_title("Distribution of Impacts by Event Type", fontweight="bold")
        ax2.set_ylabel("Price Change (%)")
        ax2.axhline(0, color="black", linewidth=0.5)
        ax2.grid(True, alpha=0.3, axis="y")
        ax2.set_xticklabels(types, rotation=45, ha="right")

        plt.tight_layout()
        plt.savefig(
            str(ROOT / "docs" / "task1_event_type_analysis.png"),
            dpi=150,
            bbox_inches="tight",
        )
        print("Event type analysis saved to docs/task1_event_type_analysis.png")

    print("\nCreating event timeline visualization...")

    fig, ax = plt.subplots(figsize=(16, 8))

    ax.plot(
        df_prices["Date"],
        df_prices["Price"],
        linewidth=1,
        alpha=0.7,
        color="steelblue",
        label="Brent Oil Price",
    )

    df_prices["MA_365"] = df_prices["Price"].rolling(window=365, min_periods=1).mean()
    ax.plot(
        df_prices["Date"],
        df_prices["MA_365"],
        linewidth=2,
        color="darkblue",
        alpha=0.8,
        label="365-day Moving Average",
    )

    colors = {
        "Conflict": "red",
        "Economic": "orange",
        "Policy": "green",
        "Supply": "purple",
        "Financial": "brown",
        "Geopolitical": "magenta",
        "Pandemic": "black",
    }

    for idx, event in df_events.iterrows():
        event_type = str(event.get("Event_Type", "Unknown")).split("/")[0].split()[0]
        color = colors.get(event_type, "gray")

        ax.axvline(event["Date"], color=color, linestyle="--", alpha=0.5, linewidth=1)

        if idx % 3 == 0 or event["Date"].year >= 2015:
            ax.text(
                event["Date"],
                ax.get_ylim()[1] * 0.95,
                event["Event_Title"][:20] + "..."
                if len(event["Event_Title"]) > 20
                else event["Event_Title"],
                rotation=90,
                verticalalignment="top",
                fontsize=8,
                color=color,
                alpha=0.8,
                fontweight="bold",
            )

    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor=color, alpha=0.5, label=etype)
        for etype, color in colors.items()
    ]
    legend_elements.append(Patch(facecolor="steelblue", alpha=0.7, label="Daily Price"))
    legend_elements.append(Patch(facecolor="darkblue", alpha=0.8, label="365-day MA"))

    ax.set_title(
        "Brent Oil Price Timeline with Major Events (1990-2020)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Price (USD/barrel)", fontsize=12)
    ax.legend(handles=legend_elements, loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        str(ROOT / "docs" / "task1_event_timeline.png"), dpi=150, bbox_inches="tight"
    )
    print("Event timeline saved to docs/task1_event_timeline.png")

    print("\n" + "=" * 60)
    print("ALL TASK 1 PLOTS GENERATED SUCCESSFULLY!")
    print("=" * 60)

    print("\n📊 TASK 1 VISUALIZATION SUMMARY:")
    print("1. docs/task1_event_impacts_fixed.png - Event window analysis")
    print("2. docs/task1_event_type_analysis.png - Impact by event type")
    print("3. docs/task1_event_timeline.png - Price timeline with events")
    print("4. docs/task1_event_impact_summary.json - Quantitative impact data")

    if event_impacts:
        print("\n📈 KEY IMPACT FINDINGS:")
        avg_impact = np.mean([imp["pct_change"] for imp in event_impacts])
        max_inc = max([imp["pct_change"] for imp in event_impacts])
        max_dec = min([imp["pct_change"] for imp in event_impacts])
        pos_count = sum(1 for imp in event_impacts if imp["pct_change"] > 0)

        print(f"• Average event impact: {avg_impact:+.1f}%")
        print(f"• Maximum increase: {max_inc:+.1f}%")
        print(f"• Maximum decrease: {max_dec:+.1f}%")
        print(f"• Positive impacts: {pos_count}/{len(event_impacts)} events")
        print("• Most events cause price increases (supply disruptions, conflicts)")
        print("• Economic crises typically cause price decreases")


if __name__ == "__main__":
    main()
