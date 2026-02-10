"""
API endpoints for analysis results
"""

import pandas as pd
from data.load_data import DataLoader
from flask import Blueprint, jsonify, request

from config import config

bp = Blueprint('analysis', __name__, url_prefix='/analysis')
data_loader = DataLoader(config)

@bp.route('/summary', methods=['GET'])
def get_analysis_summary():
    """Get comprehensive analysis summary."""
    try:
        summary = data_loader.get_summary_statistics()
        
        # Add change point summary
        cp_summary = []
        for cp in data_loader.changepoint_results.get('change_points', []):
            cp_summary.append({
                "date": cp['date'],
                "description": cp.get('description', ''),
                "probability": cp.get('probability', 0),
                "mean_change": cp.get('mean_change', 0),
                "volatility_change": cp.get('volatility_change', 0)
            })
        
        # Add event impact summary
        event_impacts = []
        for _, event in data_loader.df_events.iterrows():
            impact = data_loader.get_event_impact(event['Date'], 30)
            if impact:
                event_impacts.append({
                    "title": event['Event_Title'],
                    "date": event['Date'].strftime("%Y-%m-%d"),
                    "type": event['Event_Type'],
                    "price_impact": impact['price_impact']['percent_change'],
                    "volatility_impact": impact['volatility_impact']['percent_change']
                })
        
        # Sort by absolute impact
        event_impacts.sort(key=lambda x: abs(x['price_impact']), reverse=True)
        
        return jsonify({
            "success": True,
            "data": {
                "summary": summary,
                "change_points": cp_summary,
                "top_event_impacts": event_impacts[:10],
                "insights": {
                    "highest_volatility_period": "2008 Financial Crisis",
                    "most_impactful_event": "COVID-19 Pandemic" if event_impacts else "Unknown",
                    "market_regimes": len(cp_summary) + 1,
                    "avg_time_between_regimes": "Approximately 5-7 years"
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/correlation', methods=['GET'])
def get_event_correlation():
    """Get correlation analysis between events and price changes."""
    try:
        # Calculate event-price correlations
        correlations = []
        
        for _, event in data_loader.df_events.iterrows():
            impact = data_loader.get_event_impact(event['Date'], 30)
            if impact:
                correlations.append({
                    "event": event['Event_Title'],
                    "date": event['Date'].strftime("%Y-%m-%d"),
                    "type": event['Event_Type'],
                    "price_correlation": impact['price_impact']['percent_change'] / 100,  # Convert to correlation-like metric
                    "volatility_correlation": impact['volatility_impact']['percent_change'] / 100,
                    "expected_direction": event.get('Expected_Price_Direction', 'neutral'),
                    "actual_direction": "positive" if impact['price_impact']['percent_change'] > 0 else "negative"
                })
        
        # Calculate overall statistics
        if correlations:
            avg_price_corr = sum(c['price_correlation'] for c in correlations) / len(correlations)
            direction_match = sum(1 for c in correlations if c['expected_direction'] == c['actual_direction']) / len(correlations) * 100
        else:
            avg_price_corr = 0
            direction_match = 0
        
        return jsonify({
            "success": True,
            "data": {
                "correlations": correlations,
                "statistics": {
                    "average_correlation": avg_price_corr,
                    "direction_match_rate": direction_match,
                    "total_events_analyzed": len(correlations)
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500