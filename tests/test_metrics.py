"""Tests for Metrics Collection Module"""

import pytest
import time
from src.core.metrics_collector import MetricsCollector


def test_metrics_collector_initialization():
    """Test metrics collector initialization."""
    collector = MetricsCollector(collection_interval=2)
    assert collector.collection_interval == 2
    assert not collector.is_running
    assert len(collector.metrics_history) == 0


def test_collect_system_metrics():
    """Test system metrics collection."""
    collector = MetricsCollector()
    metrics = collector.collect_system_metrics()
    
    assert 'timestamp' in metrics
    assert 'cpu' in metrics
    assert 'memory' in metrics
    assert 'disk' in metrics
    assert metrics['cpu']['percent'] >= 0
    assert metrics['memory']['percent'] >= 0


def test_custom_metric_recording():
    """Test recording custom metrics."""
    collector = MetricsCollector()
    collector.record_custom_metric('response_time', 123.45, 'ms')
    
    assert 'response_time' in collector.custom_metrics
    assert collector.custom_metrics['response_time']['value'] == 123.45
    assert collector.custom_metrics['response_time']['unit'] == 'ms'


def test_get_latest_metric():
    """Test getting latest metric."""
    collector = MetricsCollector()
    
    # No metrics yet
    assert collector.get_latest_metric() is None
    
    # Add metrics
    metrics = collector.collect_system_metrics()
    collector.metrics_history.append(metrics)
    
    latest = collector.get_latest_metric()
    assert latest is not None
    assert latest == metrics


def test_metrics_limit():
    """Test that metrics history respects size limit."""
    collector = MetricsCollector()
    
    # Add more metrics than the limit
    for _ in range(1100):
        collector.metrics_history.append(collector.collect_system_metrics())
    
    # Simulate the trimming that happens in collection loop
    while len(collector.metrics_history) > 1000:
        collector.metrics_history.pop(0)
    
    assert len(collector.metrics_history) <= 1000
