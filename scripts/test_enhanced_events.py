"""
Test script to verify enhanced events data is loaded correctly.
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

print("Testing Enhanced Events Data Load...")
print("=" * 50)

enhanced_path = ROOT / "data" / "events" / "enhanced_events.csv"
original_path = ROOT / "data" / "events" / "key_events.csv"

try:
    df_enhanced = pd.read_csv(enhanced_path)
    print(f"✓ Enhanced events loaded: {len(df_enhanced)} events")
    print(f"  Columns: {list(df_enhanced.columns)}")
    print(f"  Date range: {df_enhanced['Date'].min()} to {df_enhanced['Date'].max()}")

    original_cols = [
        "Date",
        "Event_Title",
        "Region_Country",
        "Event_Type",
        "Short_Description",
    ]
    new_cols = [col for col in df_enhanced.columns if col not in original_cols]
    print(f"  New metadata columns: {new_cols}")

    print("\nSample of enhanced events:")
    print(
        df_enhanced[
            ["Date", "Event_Title", "Event_Type", "Expected_Price_Direction"]
        ].head()
    )
except FileNotFoundError:
    print("✗ Enhanced events file not found. Creating it now...")

    from src.data_preprocessing import load_events_data

    df_original = load_events_data(str(original_path))

    enhanced_events = []
    for _, row in df_original.iterrows():
        event = row.to_dict()
        event_type = row["Event_Type"]

        if "Conflict" in event_type or "War" in row["Event_Title"]:
            direction, duration, magnitude = "positive", 60, "high"
        elif "Crisis" in event_type or "Financial" in event_type:
            direction, duration, magnitude = "negative", 90, "high"
        elif "OPEC" in row["Event_Title"] or "Policy" in event_type:
            direction, duration, magnitude = "mixed", 30, "medium"
        elif "COVID" in row["Event_Title"] or "Pandemic" in event_type:
            direction, duration, magnitude = "negative", 180, "high"
        else:
            direction, duration, magnitude = "neutral", 30, "medium"

        event["Expected_Price_Direction"] = direction
        event["Expected_Impact_Duration_Days"] = duration
        event["Expected_Impact_Magnitude"] = magnitude
        event["Region_Code"] = (
            row["Region_Country"].split("/")[0]
            if "/" in row["Region_Country"]
            else row["Region_Country"]
        )
        event["Is_OPEC_Related"] = (
            1
            if "OPEC" in row["Event_Title"]
            or "OPEC" in str(row.get("Short_Description", ""))
            else 0
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

    df_enhanced = pd.DataFrame(enhanced_events)
    df_enhanced.to_csv(enhanced_path, index=False)
    print(f"✓ Created enhanced events file with {len(df_enhanced)} events")
    print(f"  Saved to: {enhanced_path}")
