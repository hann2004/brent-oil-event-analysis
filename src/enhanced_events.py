"""
Script to enhance the events data with additional metadata for analysis.
Run this once to create enhanced_events.csv
"""
import numpy as np
import pandas as pd

# Load existing events
events_df = pd.read_csv("data/events/key_events.csv")
events_df["Date"] = pd.to_datetime(events_df["Date"])

# Add metadata columns
enhanced_events = []

# Define impact expectations based on event type
event_type_impact = {
    "Conflict": {"direction": "positive", "duration": 60, "magnitude": "high"},
    "Economic Crisis": {"direction": "negative", "duration": 90, "magnitude": "high"},
    "Policy": {"direction": "mixed", "duration": 30, "magnitude": "medium"},
    "Geopolitical": {"direction": "positive", "duration": 45, "magnitude": "medium"},
    "Financial Crisis": {"direction": "negative", "duration": 120, "magnitude": "high"},
    "Weather/Production Disruption": {
        "direction": "positive",
        "duration": 30,
        "magnitude": "medium",
    },
    "Pandemic/Demand Shock": {
        "direction": "negative",
        "duration": 180,
        "magnitude": "high",
    },
    "Sanctions/Geopolitical": {
        "direction": "positive",
        "duration": 60,
        "magnitude": "medium",
    },
    "Supply Shock": {"direction": "mixed", "duration": 45, "magnitude": "high"},
    "Demand Shock": {"direction": "negative", "duration": 90, "magnitude": "high"},
    "Supply Shift": {"direction": "negative", "duration": 365, "magnitude": "medium"},
}

for _, row in events_df.iterrows():
    event = row.to_dict()

    # Add metadata
    event_type = row["Event_Type"]
    metadata = event_type_impact.get(
        event_type, {"direction": "neutral", "duration": 30, "magnitude": "low"}
    )

    event["Expected_Price_Direction"] = metadata["direction"]
    event["Expected_Impact_Duration_Days"] = metadata["duration"]
    event["Expected_Impact_Magnitude"] = metadata["magnitude"]
    event["Region_Code"] = (
        row["Region_Country"].split("/")[0]
        if "/" in row["Region_Country"]
        else row["Region_Country"]
    )
    event["Is_OPEC_Related"] = (
        1 if "OPEC" in row["Event_Title"] or "OPEC" in row["Short_Description"] else 0
    )
    event["Is_US_Related"] = (
        1 if "U.S." in row["Event_Title"] or "U.S." in row["Region_Country"] else 0
    )
    event["Is_Middle_East"] = (
        1
        if any(
            region in row["Region_Country"]
            for region in ["Iraq", "Kuwait", "Saudi", "Libya", "Iran", "Abqaiq"]
        )
        else 0
    )

    enhanced_events.append(event)

# Create enhanced dataframe
enhanced_df = pd.DataFrame(enhanced_events)

# Save enhanced version
enhanced_df.to_csv("data/events/enhanced_events.csv", index=False)
print(
    f"Enhanced events saved with {len(enhanced_df)} events and {len(enhanced_df.columns)} columns"
)
print(f"New columns: {list(set(enhanced_df.columns) - set(events_df.columns))}")
