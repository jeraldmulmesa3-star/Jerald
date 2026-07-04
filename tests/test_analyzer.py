"""Tests for Performance Analysis Module"""

import pytest
from src.core.performance_analyzer import PerformanceAnalyzer
from datetime import datetime


def create_mock_metrics(cpu_percent=50, memory_percent=60, disk_percent=40, count=5):
    """Create mock metrics for testing."""
    metrics = []
    for i in range(count):
        metrics.append({
            'timestamp': datetime.now().isoformat(),
            'cpu': {'percent': cpu_percent + i, 'count': 4},
            'memory': {'total': 16000, 'used': 10000, 'percent': memory_percent + i},
            'disk': {'total': 500000, 'used': 250000, 'percent': disk_percent},
            'custom': {}
        })
    return metrics


def test_analyzer_initialization():
    """Test analyzer initialization."""
    analyzer = PerformanceAnalyzer()
    assert isinstance(analyzer.analysis_cache, dict)


def test_analyze_metrics():
    """Test metrics analysis."""
    analyzer = PerformanceAnalyzer()
    metrics = create_mock_metrics()
    
    analysis = analyzer.analyze_metrics(metrics)
    
    assert 'cpu_analysis' in analysis
    assert 'memory_analysis' in analysis
    assert 'disk_analysis' in analysis
    assert 'anomalies' in analysis
    assert analysis['total_samples'] == 5


def test_cpu_analysis():
    """Test CPU metrics analysis."""
    analyzer = PerformanceAnalyzer()
    metrics = create_mock_metrics(cpu_percent=50, count=10)
    
    analysis = analyzer.analyze_metrics(metrics)
    cpu = analysis['cpu_analysis']
    
    assert 'avg' in cpu
    assert 'min' in cpu
    assert 'max' in cpu
    assert 'median' in cpu
    assert cpu['avg'] > 0


def test_trend_calculation():
    """Test trend calculation."""
    analyzer = PerformanceAnalyzer()
    
    # Increasing trend
    increasing = [10, 20, 30, 40, 50]
    trend = analyzer._calculate_trend(increasing)
    assert trend == 'increasing'
    
    # Decreasing trend
    decreasing = [50, 40, 30, 20, 10]
    trend = analyzer._calculate_trend(decreasing)
    assert trend == 'decreasing'
    
    # Stable trend
    stable = [25, 25, 25, 25, 25]
    trend = analyzer._calculate_trend(stable)
    assert trend == 'stable'


def test_performance_score():
    """Test performance score calculation."""
    analyzer = PerformanceAnalyzer()
    metrics = create_mock_metrics(cpu_percent=30, memory_percent=40)
    
    analysis = analyzer.analyze_metrics(metrics)
    score = analyzer.get_performance_score(analysis)
    
    assert 0 <= score <= 100
