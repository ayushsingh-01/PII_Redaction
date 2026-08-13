"""
Tests for evaluation metrics calculation in evaluation/evaluate.py.
"""

import pytest
from evaluation.evaluate import compute_metrics


def test_compute_metrics_perfect():
    metrics = compute_metrics(tp=10, fp=0, fn=0)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0


def test_compute_metrics_partial():
    metrics = compute_metrics(tp=8, fp=2, fn=2)
    assert metrics["precision"] == 0.8
    assert metrics["recall"] == 0.8
    assert metrics["f1"] == 0.8


def test_compute_metrics_zero():
    metrics = compute_metrics(tp=0, fp=5, fn=5)
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["f1"] == 0.0
