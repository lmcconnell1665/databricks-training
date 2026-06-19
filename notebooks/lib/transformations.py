"""Reusable business logic for the CMA Databricks training demo.

This module exists to demonstrate the "Modular Code" standard: keep business
logic in plain .py files that can be unit-tested with pytest and imported into
notebooks, rather than burying logic inside notebook cells.
"""
from __future__ import annotations


def fare_per_mile(fare_amount: float, trip_distance: float) -> float:
    """Return the fare charged per mile for a single trip.

    Returns 0.0 when the trip distance is zero or negative so that callers do
    not have to guard against divide-by-zero on bad source rows.
    """
    if trip_distance <= 0:
        return 0.0
    return round(fare_amount / trip_distance, 2)


def classify_trip(trip_distance: float) -> str:
    """Bucket a taxi trip into a human-readable distance category."""
    if trip_distance < 0:
        raise ValueError("trip_distance cannot be negative")
    if trip_distance < 2:
        return "short"
    if trip_distance < 10:
        return "medium"
    return "long"
