"""Unit tests for lib.transformations.

Demonstrates the "Testing" standard: run with `pytest` locally or from a
notebook cell (`!python -m pytest notebooks/tests -q`) to catch issues before
they reach production.
"""
import pytest

from lib.transformations import classify_trip, fare_per_mile


def test_fare_per_mile_basic():
    assert fare_per_mile(20.0, 5.0) == 4.0


def test_fare_per_mile_zero_distance_does_not_raise():
    assert fare_per_mile(20.0, 0.0) == 0.0


@pytest.mark.parametrize(
    "distance,expected",
    [(0.5, "short"), (5.0, "medium"), (25.0, "long")],
)
def test_classify_trip(distance, expected):
    assert classify_trip(distance) == expected


def test_classify_trip_rejects_negative():
    with pytest.raises(ValueError):
        classify_trip(-1.0)
