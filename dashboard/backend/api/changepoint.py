"""
API endpoints for change point analysis results
"""

import pandas as pd
from data.load_data import DataLoader
from flask import Blueprint, jsonify, request

from config import config

bp = Blueprint("changepoint", __name__, url_prefix="/changepoint")
data_loader = DataLoader(config)


@bp.route("/", methods=["GET"])
def get_changepoints():
    """Get all detected change points."""
    try:
        change_points = data_loader.changepoint_results.get("change_points", [])

        # Enhance with nearby events
        enhanced_cps = []
        for cp in change_points:
            cp_date = pd.to_datetime(cp["date"])

            # Find events within 90 days
            start_date = cp_date - pd.Timedelta(days=90)
            end_date = cp_date + pd.Timedelta(days=90)

            nearby_events = data_loader.df_events[
                (data_loader.df_events["Date"] >= start_date)
                & (data_loader.df_events["Date"] <= end_date)
            ].copy()

            nearby_events["days_from_cp"] = (nearby_events["Date"] - cp_date).dt.days
            nearby_events = nearby_events.sort_values("days_from_cp", key=abs)

            enhanced_cp = cp.copy()
            enhanced_cp["nearby_events"] = [
                {
                    "title": row["Event_Title"],
                    "date": row["Date"].strftime("%Y-%m-%d"),
                    "type": row["Event_Type"],
                    "days_from_cp": int(row["days_from_cp"]),
                    "expected_direction": row.get(
                        "Expected_Price_Direction", "neutral"
                    ),
                }
                for _, row in nearby_events.head(5).iterrows()
            ]

            enhanced_cps.append(enhanced_cp)

        return jsonify(
            {
                "success": True,
                "data": {
                    "change_points": enhanced_cps,
                    "model_metrics": data_loader.changepoint_results.get(
                        "model_metrics", {}
                    ),
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/<cp_date>/impact", methods=["GET"])
def get_changepoint_impact(cp_date):
    """Get impact analysis for a specific change point."""
    try:
        cp_date_dt = pd.to_datetime(cp_date)

        # Find the change point
        cp_data = None
        for cp in data_loader.changepoint_results.get("change_points", []):
            if pd.to_datetime(cp["date"]) == cp_date_dt:
                cp_data = cp
                break

        if not cp_data:
            return (
                jsonify(
                    {"success": False, "error": f"Change point not found: {cp_date}"}
                ),
                404,
            )

        # Get price data around change point
        window_days = int(request.args.get("window_days", 180))
        start_date = cp_date_dt - pd.Timedelta(days=window_days)
        end_date = cp_date_dt + pd.Timedelta(days=window_days)

        df = data_loader.get_price_data(
            start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), "daily"
        )

        # Calculate before/after statistics
        before_data = df[df["Date"] < cp_date_dt]
        after_data = df[df["Date"] >= cp_date_dt]

        if len(before_data) == 0 or len(after_data) == 0:
            return (
                jsonify(
                    {"success": False, "error": "Insufficient data for impact analysis"}
                ),
                400,
            )

        before_stats = {
            "mean_price": float(before_data["Price"].mean()),
            "std_price": float(before_data["Price"].std()),
            "count": len(before_data),
        }

        after_stats = {
            "mean_price": float(after_data["Price"].mean()),
            "std_price": float(after_data["Price"].std()),
            "count": len(after_data),
        }

        # Prepare chart data
        chart_data = []
        for _, row in df.iterrows():
            chart_data.append(
                {
                    "date": row["Date"].strftime("%Y-%m-%d"),
                    "price": row["Price"],
                    "period": "before" if row["Date"] < cp_date_dt else "after",
                    "days_from_cp": (row["Date"] - cp_date_dt).days,
                }
            )

        return jsonify(
            {
                "success": True,
                "data": {
                    "change_point": cp_data,
                    "impact": {
                        "price_change": after_stats["mean_price"]
                        - before_stats["mean_price"],
                        "price_change_pct": (
                            (after_stats["mean_price"] - before_stats["mean_price"])
                            / before_stats["mean_price"]
                        )
                        * 100,
                        "volatility_change": after_stats["std_price"]
                        - before_stats["std_price"],
                        "volatility_change_pct": (
                            (after_stats["std_price"] - before_stats["std_price"])
                            / before_stats["std_price"]
                        )
                        * 100,
                    },
                    "statistics": {"before": before_stats, "after": after_stats},
                    "chart_data": chart_data,
                    "window_days": window_days,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
