"""
API endpoints for events data
"""

import pandas as pd
from data.load_data import DataLoader
from flask import Blueprint, jsonify, request

from config import config

bp = Blueprint('events', __name__, url_prefix='/events')
data_loader = DataLoader(config)

@bp.route('/', methods=['GET'])
def get_events():
    """Get all events with filtering."""
    try:
        event_type = request.args.get('event_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        df = data_loader.get_events_by_type(event_type, start_date, end_date)
        
        events = []
        for _, row in df.iterrows():
            event = {
                "date": row['Date'].strftime("%Y-%m-%d"),
                "title": row['Event_Title'],
                "type": row['Event_Type'],
                "region": row.get('Region_Country', ''),
                "description": row.get('Short_Description', ''),
                "expected_direction": row.get('Expected_Price_Direction', 'neutral')
            }
            events.append(event)
        
        return jsonify({
            "success": True,
            "data": events,
            "metadata": {
                "count": len(events),
                "available_types": list(data_loader.df_events['Event_Type'].unique()),
                "date_range": {
                    "start": df['Date'].min().strftime("%Y-%m-%d") if len(df) > 0 else None,
                    "end": df['Date'].max().strftime("%Y-%m-%d") if len(df) > 0 else None
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/impact', methods=['GET'])
def get_event_impact():
    """Calculate impact of a specific event."""
    try:
        event_title = request.args.get('event_title')
        event_date = request.args.get('event_date')
        window_days = int(request.args.get('window_days', 30))
        
        if not event_date and not event_title:
            return jsonify({
                "success": False,
                "error": "Either event_date or event_title must be provided"
            }), 400
        
        # Find event by title if date not provided
        if event_title and not event_date:
            event = data_loader.df_events[data_loader.df_events['Event_Title'] == event_title]
            if len(event) == 0:
                return jsonify({
                    "success": False,
                    "error": f"Event not found: {event_title}"
                }), 404
            event_date = event.iloc[0]['Date'].strftime("%Y-%m-%d")
        
        # Calculate impact
        impact = data_loader.get_event_impact(event_date, window_days)
        
        if impact is None:
            return jsonify({
                "success": False,
                "error": "Could not calculate impact. Insufficient data around event."
            }), 400
        
        # Find event details
        event_date_dt = pd.to_datetime(event_date)
        event_details = data_loader.df_events[data_loader.df_events['Date'] == event_date_dt]
        
        if len(event_details) > 0:
            event_info = {
                "title": event_details.iloc[0]['Event_Title'],
                "date": event_date,
                "type": event_details.iloc[0]['Event_Type'],
                "description": event_details.iloc[0].get('Short_Description', '')
            }
        else:
            event_info = {
                "title": "Unknown Event",
                "date": event_date,
                "type": "Unknown",
                "description": "Event details not available"
            }
        
        return jsonify({
            "success": True,
            "data": {
                "event": event_info,
                "impact": impact,
                "window_days": window_days
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500