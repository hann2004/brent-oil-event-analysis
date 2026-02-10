"""
API endpoints for price data
"""

import pandas as pd
from data.load_data import DataLoader
from flask import Blueprint, jsonify, request

from config import config

bp = Blueprint("prices", __name__, url_prefix="/prices")
data_loader = DataLoader(config)


@bp.route("/", methods=["GET"])
def get_prices():
    """Get price data with filtering."""
    try:
        # Get query parameters
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        resolution = request.args.get("resolution", "daily")

        # Validate resolution
        valid_resolutions = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if resolution not in valid_resolutions:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Invalid resolution. Must be one of: {valid_resolutions}",
                    }
                ),
                400,
            )

        # Get data
        df = data_loader.get_price_data(start_date, end_date, resolution)

        # Prepare response
        response = {
            "success": True,
            "data": {
                "dates": df["Date"].dt.strftime("%Y-%m-%d").tolist(),
                "prices": df["Price"].tolist(),
                "years": df["Year"].tolist() if "Year" in df.columns else [],
                "months": df["Month"].tolist() if "Month" in df.columns else [],
            },
            "metadata": {
                "count": len(df),
                "resolution": resolution,
                "date_range": {
                    "start": df["Date"].min().strftime("%Y-%m-%d"),
                    "end": df["Date"].max().strftime("%Y-%m-%d"),
                },
            },
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/returns", methods=["GET"])
def get_returns():
    """Get returns and volatility data."""
    try:
        window = int(request.args.get("window", 30))

        df = data_loader.df_returns.copy()

        response = {
            "success": True,
            "data": {
                "dates": df["Date"].dt.strftime("%Y-%m-%d").tolist(),
                "returns": df["Log_Returns"].tolist(),
                "volatility": df["Volatility_30D"].fillna(0).tolist(),
                "prices": df["Price"].tolist(),
            },
            "metadata": {"window": window, "count": len(df)},
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary", methods=["GET"])
def get_price_summary():
    """Get price summary statistics."""
    try:
        stats = data_loader.get_summary_statistics()

        return jsonify({"success": True, "data": stats})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
