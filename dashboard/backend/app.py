"""
Flask backend API for the Brent Oil Price Analysis Dashboard.
Provides endpoints for data, analysis results, and event correlations.
"""

import json
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

warnings.filterwarnings("ignore")

app = Flask(__name__, static_folder=None)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_BUILD_DIR = BASE_DIR / "dashboard" / "frontend" / "build"


class DataManager:
    """Manage data loading and processing for the dashboard."""

    def __init__(self):
        self.df_prices = None
        self.df_returns = None
        self.df_events = None
        self.model_results = None
        self.load_data()

    def load_model_results(self):
        """Load model results from known locations."""
        candidates = [
            BASE_DIR / "models" / "single_cp_results.json",
            BASE_DIR / "models" / "oil_cp_results.json",
        ]
        for model_path in candidates:
            if model_path.exists():
                with open(model_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        return None

    def normalize_model_results(self, results):
        """Normalize model results to dashboard-friendly keys."""
        if not results:
            return {}

        change_point = results.get("change_point", {}) or {}
        param_changes = results.get("parameter_changes", {}) or {}

        if "mu" in param_changes or "sigma" in param_changes:
            mean_change = param_changes.get("mu", {}) or {}
            vol_change = param_changes.get("sigma", {}) or {}
            param_changes = {
                "mean_change": {
                    "mean": mean_change.get("change_mean"),
                    "hdi_95": mean_change.get("hdi_95"),
                    "probability_positive": mean_change.get("probability_increase"),
                },
                "volatility_change": {
                    "mean": vol_change.get("change_mean"),
                    "hdi_95": vol_change.get("hdi_95"),
                    "probability_increase": vol_change.get("probability_increase"),
                },
            }

        return {
            "change_point": {
                "mean_date": change_point.get("mean_date"),
                "hdi_95_dates": change_point.get("hdi_95_dates"),
                "probability": change_point.get("probability"),
            },
            "parameter_changes": param_changes,
        }

    def load_data(self):
        """Load all required data."""
        try:
            price_path = BASE_DIR / "data" / "raw" / "BrentOilPrices.csv"
            self.df_prices = pd.read_csv(price_path)
            self.df_prices["Date"] = pd.to_datetime(
                self.df_prices["Date"], format="%d-%b-%y", errors="coerce"
            )
            self.df_prices = self.df_prices.dropna(subset=["Date"]).sort_values("Date")
            self.df_prices["Price"] = self.df_prices["Price"].interpolate(
                method="linear"
            )

            self.df_returns = self.df_prices.copy()
            self.df_returns["Returns"] = self.df_returns["Price"].pct_change()
            self.df_returns["Log_Returns"] = np.log(
                self.df_returns["Price"] / self.df_returns["Price"].shift(1)
            )
            self.df_returns = self.df_returns.dropna()

            events_path = BASE_DIR / "data" / "events" / "enhanced_events.csv"
            if events_path.exists():
                self.df_events = pd.read_csv(events_path)
            else:
                events_path = BASE_DIR / "data" / "events" / "key_events.csv"
                self.df_events = pd.read_csv(events_path)
            self.df_events["Date"] = pd.to_datetime(self.df_events["Date"])

            raw_results = self.load_model_results()
            self.model_results = self.normalize_model_results(raw_results)

            print(
                f"Data loaded: {len(self.df_prices)} prices, {len(self.df_events)} events"
            )

        except Exception as e:
            print(f"Error loading data: {e}")
            self.create_sample_data()

    def create_sample_data(self):
        """Create sample data if real data fails to load."""
        dates = pd.date_range(start="2000-01-01", end="2022-12-31", freq="D")
        self.df_prices = pd.DataFrame(
            {"Date": dates, "Price": 50 + np.random.randn(len(dates)).cumsum() * 10}
        )

        self.df_returns = self.df_prices.copy()
        self.df_returns["Returns"] = self.df_returns["Price"].pct_change()
        self.df_returns["Log_Returns"] = np.log(
            self.df_returns["Price"] / self.df_returns["Price"].shift(1)
        )
        self.df_returns = self.df_returns.dropna()

        self.df_events = pd.DataFrame(
            {
                "Date": pd.to_datetime(["2008-09-15", "2020-03-08", "2022-02-24"]),
                "Event_Title": ["Financial Crisis", "COVID-19", "Russia-Ukraine War"],
                "Event_Type": ["Financial Crisis", "Pandemic", "Conflict"],
            }
        )

        self.model_results = {
            "change_point": {"mean_date": "2014-01-01"},
            "parameter_changes": {
                "mean_change": {"mean": 0.01, "probability_positive": 0.5},
                "volatility_change": {"mean": 0.02, "probability_increase": 0.5},
            },
        }

    def get_event_impact(self, event_date, window_days=30):
        """Calculate impact of a specific event."""
        event_date = pd.to_datetime(event_date)
        start_date = event_date - timedelta(days=window_days)
        end_date = event_date + timedelta(days=window_days)

        mask = (self.df_prices["Date"] >= start_date) & (
            self.df_prices["Date"] <= end_date
        )
        window_data = self.df_prices[mask].copy()

        if len(window_data) < 10:
            return None

        pre_mask = window_data["Date"] < event_date
        post_mask = window_data["Date"] > event_date

        if pre_mask.sum() == 0 or post_mask.sum() == 0:
            return None

        pre_avg = window_data[pre_mask]["Price"].mean()
        post_avg = window_data[post_mask]["Price"].mean()

        return {
            "pre_avg": float(pre_avg),
            "post_avg": float(post_avg),
            "price_change": float(post_avg - pre_avg),
            "percent_change": float((post_avg - pre_avg) / pre_avg * 100),
            "window_days": window_days,
        }


data_manager = DataManager()


@app.route("/")
def home():
    """Dashboard home page."""
    return jsonify(
        {
            "message": "Brent Oil Price Analysis Dashboard API",
            "endpoints": [
                "/api/prices - Get price data",
                "/api/events - Get events data",
                "/api/analysis/summary - Get analysis summary",
                "/api/analysis/changepoints - Get change points",
                "/api/analysis/event-impact/<event_title> - Get event impact",
                "/api/analysis/volatility - Get volatility",
                "/api/analysis/correlation - Get event-price correlation",
            ],
        }
    )


@app.route("/api/health")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/api/prices", methods=["GET"])
def get_prices():
    """Get price data with optional filtering."""
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        resample = request.args.get("resample", "D")

        df = data_manager.df_prices.copy()

        if start_date:
            df = df[df["Date"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["Date"] <= pd.to_datetime(end_date)]

        if resample != "D":
            if resample == "W":
                df_resampled = (
                    df.set_index("Date")
                    .resample("W")
                    .agg({"Price": "mean"})
                    .reset_index()
                )
            elif resample == "M":
                df_resampled = (
                    df.set_index("Date")
                    .resample("M")
                    .agg({"Price": "mean"})
                    .reset_index()
                )
            else:
                df_resampled = df
            df = df_resampled

        if df.empty:
            return jsonify(
                {
                    "dates": [],
                    "prices": [],
                    "count": 0,
                    "date_range": {"start": None, "end": None},
                    "stats": {
                        "mean": None,
                        "median": None,
                        "min": None,
                        "max": None,
                        "std": None,
                    },
                }
            )

        response = {
            "dates": df["Date"].dt.strftime("%Y-%m-%d").tolist(),
            "prices": df["Price"].tolist(),
            "count": len(df),
            "date_range": {
                "start": df["Date"].min().strftime("%Y-%m-%d"),
                "end": df["Date"].max().strftime("%Y-%m-%d"),
            },
            "stats": {
                "mean": float(df["Price"].mean()),
                "median": float(df["Price"].median()),
                "min": float(df["Price"].min()),
                "max": float(df["Price"].max()),
                "std": float(df["Price"].std()),
            },
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/events", methods=["GET"])
def get_events():
    """Get events data with optional filtering."""
    try:
        event_type = request.args.get("event_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        df = data_manager.df_events.copy()

        if event_type and event_type != "all":
            df = df[df["Event_Type"] == event_type]
        if start_date:
            df = df[df["Date"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["Date"] <= pd.to_datetime(end_date)]

        events = []
        for _, row in df.iterrows():
            event = {
                "date": row["Date"].strftime("%Y-%m-%d"),
                "title": row["Event_Title"],
                "type": row["Event_Type"],
                "description": row.get("Short_Description", ""),
                "region": row.get("Region_Country", ""),
                "expected_direction": row.get("Expected_Price_Direction", "neutral"),
                "expected_magnitude": row.get("Expected_Impact_Magnitude", "medium"),
            }
            events.append(event)

        type_distribution = df["Event_Type"].value_counts().to_dict()

        return jsonify(
            {
                "events": events,
                "count": len(events),
                "type_distribution": type_distribution,
                "date_range": {
                    "start": df["Date"].min().strftime("%Y-%m-%d")
                    if len(df) > 0
                    else None,
                    "end": df["Date"].max().strftime("%Y-%m-%d")
                    if len(df) > 0
                    else None,
                },
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analysis/summary", methods=["GET"])
def get_analysis_summary():
    """Get analysis summary including change points and impacts."""
    try:
        results = data_manager.model_results

        if not results:
            results = {}

        change_point = results.get("change_point", {})
        param_changes = results.get("parameter_changes", {})

        price_stats = {
            "mean": float(data_manager.df_prices["Price"].mean()),
            "median": float(data_manager.df_prices["Price"].median()),
            "min": float(data_manager.df_prices["Price"].min()),
            "max": float(data_manager.df_prices["Price"].max()),
            "std": float(data_manager.df_prices["Price"].std()),
        }

        returns_stats = {
            "mean": float(data_manager.df_returns["Log_Returns"].mean()),
            "std": float(data_manager.df_returns["Log_Returns"].std()),
            "min": float(data_manager.df_returns["Log_Returns"].min()),
            "max": float(data_manager.df_returns["Log_Returns"].max()),
        }

        event_stats = {
            "total": len(data_manager.df_events),
            "by_type": data_manager.df_events["Event_Type"].value_counts().to_dict(),
            "by_year": data_manager.df_events["Date"]
            .dt.year.value_counts()
            .sort_index()
            .to_dict(),
        }

        summary = {
            "change_point": {
                "date": change_point.get("mean_date"),
                "hdi_95": change_point.get("hdi_95_dates"),
                "probability": change_point.get("probability"),
            },
            "parameter_changes": param_changes,
            "price_statistics": price_stats,
            "returns_statistics": returns_stats,
            "event_statistics": event_stats,
            "data_info": {
                "price_records": len(data_manager.df_prices),
                "date_range": {
                    "start": data_manager.df_prices["Date"].min().strftime("%Y-%m-%d"),
                    "end": data_manager.df_prices["Date"].max().strftime("%Y-%m-%d"),
                },
            },
        }

        return jsonify(summary)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analysis/changepoints", methods=["GET"])
def get_changepoints():
    """Get detected change points with details."""
    try:
        results = data_manager.model_results

        if not results or "change_point" not in results:
            return jsonify({"change_points": []})

        cp = results["change_point"]
        cp_date_value = cp.get("mean_date")
        cp_date = pd.to_datetime(cp_date_value) if cp_date_value else None

        window_days = int(request.args.get("window_days", 90))

        nearby_events = []
        if cp_date is not None and not pd.isna(cp_date):
            start_date = cp_date - timedelta(days=window_days)
            end_date = cp_date + timedelta(days=window_days)

            mask = (data_manager.df_events["Date"] >= start_date) & (
                data_manager.df_events["Date"] <= end_date
            )
            nearby_df = data_manager.df_events[mask].copy()

            if len(nearby_df) > 0:
                nearby_df["Days_Difference"] = (nearby_df["Date"] - cp_date).dt.days
                nearby_df = nearby_df.sort_values("Days_Difference", key=abs)

                for _, row in nearby_df.iterrows():
                    event = {
                        "title": row["Event_Title"],
                        "date": row["Date"].strftime("%Y-%m-%d"),
                        "type": row["Event_Type"],
                        "days_from_cp": int(row["Days_Difference"]),
                        "description": row.get("Short_Description", ""),
                    }
                    nearby_events.append(event)

        changepoints = [
            {
                "date": cp.get("mean_date"),
                "hdi_95": cp.get("hdi_95_dates"),
                "probability": cp.get("probability"),
                "nearby_events": nearby_events[:5],
                "parameter_changes": results.get("parameter_changes", {}),
            }
        ]

        return jsonify({"change_points": changepoints})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analysis/event-impact/<event_title>", methods=["GET"])
def get_event_impact(event_title):
    """Get impact analysis for a specific event."""
    try:
        event_match = data_manager.df_events[
            data_manager.df_events["Event_Title"].str.contains(
                event_title, case=False, na=False
            )
        ]

        if len(event_match) == 0:
            return jsonify({"error": "Event not found"}), 404

        event = event_match.iloc[0]
        event_date = event["Date"]

        window_days = int(request.args.get("window_days", 30))
        impact = data_manager.get_event_impact(event_date, window_days)

        if impact is None:
            return jsonify({"error": "Insufficient data for impact analysis"}), 400

        start_date = event_date - timedelta(days=window_days)
        end_date = event_date + timedelta(days=window_days)

        mask = (data_manager.df_prices["Date"] >= start_date) & (
            data_manager.df_prices["Date"] <= end_date
        )
        price_data = data_manager.df_prices[mask].copy()

        response = {
            "event": {
                "title": event["Event_Title"],
                "date": event_date.strftime("%Y-%m-%d"),
                "type": event["Event_Type"],
                "description": event.get("Short_Description", ""),
                "region": event.get("Region_Country", ""),
                "expected_direction": event.get("Expected_Price_Direction", "neutral"),
            },
            "impact": impact,
            "price_data": {
                "dates": price_data["Date"].dt.strftime("%Y-%m-%d").tolist(),
                "prices": price_data["Price"].tolist(),
            },
            "analysis": {
                "window_days": window_days,
                "data_points": len(price_data),
                "significance": "high"
                if abs(impact["percent_change"]) > 10
                else "medium"
                if abs(impact["percent_change"]) > 5
                else "low",
            },
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analysis/volatility", methods=["GET"])
def get_volatility():
    """Get volatility analysis."""
    try:
        window = int(request.args.get("window", 30))
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        df = data_manager.df_returns.copy()

        if start_date:
            df = df[df["Date"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["Date"] <= pd.to_datetime(end_date)]

        df["Volatility"] = df["Log_Returns"].rolling(window=window).std()

        if df.empty:
            return jsonify(
                {
                    "volatility_series": {"dates": [], "volatility": []},
                    "event_volatility": [],
                    "window": window,
                    "average_volatility": None,
                    "max_volatility": None,
                }
            )

        event_volatility = []
        for _, event in data_manager.df_events.iterrows():
            event_date = event["Date"]
            window_start = event_date - timedelta(days=window)
            window_end = event_date + timedelta(days=window)

            mask = (df["Date"] >= window_start) & (df["Date"] <= window_end)
            event_data = df[mask]

            if len(event_data) > 10:
                pre_vol = event_data[event_data["Date"] < event_date][
                    "Volatility"
                ].mean()
                post_vol = event_data[event_data["Date"] > event_date][
                    "Volatility"
                ].mean()

                pre_value = float(pre_vol) if not pd.isna(pre_vol) else None
                post_value = float(post_vol) if not pd.isna(post_vol) else None
                change = None
                if pre_value is not None and pre_value != 0 and post_value is not None:
                    change = float((post_value - pre_value) / pre_value * 100)

                event_volatility.append(
                    {
                        "event": event["Event_Title"],
                        "date": event_date.strftime("%Y-%m-%d"),
                        "pre_volatility": pre_value,
                        "post_volatility": post_value,
                        "volatility_change": change,
                    }
                )

        return jsonify(
            {
                "volatility_series": {
                    "dates": df["Date"].dt.strftime("%Y-%m-%d").tolist(),
                    "volatility": df["Volatility"].tolist(),
                },
                "event_volatility": event_volatility,
                "window": window,
                "average_volatility": float(df["Volatility"].mean()),
                "max_volatility": float(df["Volatility"].max()),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analysis/correlation", methods=["GET"])
def get_correlation():
    """Get event-price correlation analysis."""
    try:
        correlations = []

        for _, event in data_manager.df_events.iterrows():
            impact = data_manager.get_event_impact(event["Date"], window_days=30)

            if impact:
                correlation = {
                    "event": event["Event_Title"],
                    "title": event["Event_Title"],
                    "date": event["Date"].strftime("%Y-%m-%d"),
                    "type": event["Event_Type"],
                    "price_change": impact["percent_change"],
                    "magnitude": abs(impact["percent_change"]),
                    "direction": "increase"
                    if impact["percent_change"] > 0
                    else "decrease",
                    "significance": "high"
                    if abs(impact["percent_change"]) > 15
                    else "medium"
                    if abs(impact["percent_change"]) > 5
                    else "low",
                }
                correlations.append(correlation)

        correlations.sort(key=lambda x: x["magnitude"], reverse=True)

        if correlations:
            changes = [c["price_change"] for c in correlations]
            summary = {
                "average_change": float(np.mean(changes)),
                "median_change": float(np.median(changes)),
                "max_increase": float(max(changes)),
                "max_decrease": float(min(changes)),
                "positive_count": int(
                    sum(1 for c in correlations if c["price_change"] > 0)
                ),
                "negative_count": int(
                    sum(1 for c in correlations if c["price_change"] < 0)
                ),
            }
        else:
            summary = {}

        return jsonify(
            {
                "correlations": correlations,
                "summary": summary,
                "total_events_analyzed": len(correlations),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/manifest.json")
def serve_manifest():
    """Serve React manifest from build output."""
    return send_from_directory(str(FRONTEND_BUILD_DIR), "manifest.json")


@app.route("/asset-manifest.json")
def serve_asset_manifest():
    """Serve React asset manifest from build output."""
    return send_from_directory(str(FRONTEND_BUILD_DIR), "asset-manifest.json")


@app.route("/favicon.ico")
def serve_favicon():
    """Serve React favicon from build output."""
    return send_from_directory(str(FRONTEND_BUILD_DIR), "favicon.ico")


@app.route("/static/<path:path>")
def serve_static(path):
    """Serve React static assets."""
    return send_from_directory(str(FRONTEND_BUILD_DIR / "static"), path)


@app.route("/dashboard")
def serve_dashboard():
    """Serve the React dashboard."""
    return send_from_directory(str(FRONTEND_BUILD_DIR), "index.html")


@app.route("/dashboard/<path:path>")
def serve_dashboard_files(path):
    """Serve static files for the React dashboard."""
    return send_from_directory(str(FRONTEND_BUILD_DIR), path)


if __name__ == "__main__":
    print("=" * 60)
    print("Brent Oil Price Analysis Dashboard API")
    print("=" * 60)
    print("API URL: http://localhost:5000")
    print("Dashboard URL: http://localhost:5000/dashboard")
    print("Health Check: http://localhost:5000/api/health")
    print("=" * 60)

    app.run(debug=True, host="0.0.0.0", port=5000)
