"""
Module 1: Data Ingestion and Profile Manager

- Handles loading, saving, and updating user profile and goals.
- Uses synthetic data if no file exists.
- Computes monthly savings and goal planning DataFrame.
- Addresses research gap: Standardizes user data for holistic, goal-oriented planning.
"""

import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

DATA_PATH = os.path.join("data", "synthetic_user.json")
TODAY = datetime(2025, 9, 24)  # Hardcoded for reproducibility

DEFAULT_DATA = {
    "income": 5000.0,
    "expenses": 3000.0,
    "risk_profile": "Medium",
    "goals": [
        {
            "name": "Emergency Fund",
            "target_amount": 6000.0,
            "current_amount": 2000.0,
            "deadline": "2026-01-01",
            "priority": 5
        },
        {
            "name": "Vacation",
            "target_amount": 3000.0,
            "current_amount": 500.0,
            "deadline": "2025-12-01",
            "priority": 3
        },
        {
            "name": "House Down Payment",
            "target_amount": 20000.0,
            "current_amount": 5000.0,
            "deadline": "2027-06-01",
            "priority": 4
        },
        {
            "name": "Retirement",
            "target_amount": 100000.0,
            "current_amount": 10000.0,
            "deadline": "2045-01-01",
            "priority": 2
        }
    ]
}

def load_user_data():
    """Load user data from JSON, or create defaults if missing."""
    if not os.path.exists(DATA_PATH):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w") as f:
            json.dump(DEFAULT_DATA, f, indent=2)
        return DEFAULT_DATA.copy()
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_user_data(data):
    """Save user data to JSON, converting any Timestamps to strings."""
    # Convert deadlines to string for JSON serialization
    for goal in data.get("goals", []):
        if not isinstance(goal["deadline"], str):
            goal["deadline"] = str(goal["deadline"].date())  # or .strftime("%Y-%m-%d")
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def compute_monthly_savings(income, expenses):
    """Compute monthly savings."""
    return income - expenses

def get_goals_dataframe(goals):
    """
    Convert goals list to DataFrame and compute:
    - months_left: months until deadline
    - required_monthly: (target - current) / months_left
    """
    df = pd.DataFrame(goals)
    df["deadline"] = pd.to_datetime(df["deadline"])
    df["months_left"] = df["deadline"].apply(lambda d: max(1, (relativedelta(d, TODAY).years * 12 + relativedelta(d, TODAY).months)))
    df["required_monthly"] = (df["target_amount"] - df["current_amount"]) / df["months_left"]
    df["required_monthly"] = df["required_monthly"].clip(lower=0)
    return df

def update_goal(df, idx, allocation):
    """Update current_amount for a goal in DataFrame."""
    df.at[idx, "current_amount"] += allocation
    return df

def update_goals_in_data(data, updated_df):
    """Update the goals in the user data dict from DataFrame."""
    data["goals"] = updated_df.to_dict(orient="records")
    return data