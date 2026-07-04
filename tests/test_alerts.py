"""Tests for Alert Management Module"""

import pytest
from src.core.alert_manager import Alert, AlertManager
from datetime import datetime


def test_alert_initialization():
    """Test alert initialization."""
    alert = Alert('alert1', 'High CPU', 'cpu.percent', '>', 80)
    
    assert alert.alert_id == 'alert1'
    assert alert.name == 'High CPU'
    assert alert.metric == 'cpu.percent'
    assert alert.enabled is True


def test_alert_condition_check():
    """Test alert condition checking."""
    alert = Alert('alert1', 'High CPU', 'cpu.percent', '>', 80)
    
    assert alert.check_condition(90) is True
    assert alert.check_condition(75) is False
    assert alert.check_condition(80) is False


def test_alert_operators():
    """Test different alert operators."""
    # Greater than
    alert = Alert('a1', 'Test', 'metric', '>', 50)
    assert alert.check_condition(60) is True
    assert alert.check_condition(40) is False
    
    # Less than
    alert = Alert('a2', 'Test', 'metric', '<', 50)
    assert alert.check_condition(40) is True
    assert alert.check_condition(60) is False
    
    # Greater than or equal
    alert = Alert('a3', 'Test', 'metric', '>=', 50)
    assert alert.check_condition(50) is True
    assert alert.check_condition(60) is True


def test_alert_manager_initialization():
    """Test alert manager initialization."""
    manager = AlertManager()
    assert len(manager.alerts) == 0
    assert len(manager.alert_history) == 0


def test_create_alert():
    """Test creating an alert."""
    manager = AlertManager()
    alert = manager.create_alert('cpu_alert', 'High CPU', 'cpu.percent', '>', 80)
    
    assert alert is not None
    assert 'cpu_alert' in manager.alerts


def test_remove_alert():
    """Test removing an alert."""
    manager = AlertManager()
    manager.create_alert('alert1', 'Test', 'metric', '>', 50)
    
    assert manager.remove_alert('alert1') is True
    assert 'alert1' not in manager.alerts
    assert manager.remove_alert('nonexistent') is False


def test_enable_disable_alert():
    """Test enabling and disabling alerts."""
    manager = AlertManager()
    alert = manager.create_alert('alert1', 'Test', 'metric', '>', 50)
    
    assert alert.enabled is True
    assert manager.disable_alert('alert1') is True
    assert alert.enabled is False
    assert manager.enable_alert('alert1') is True
    assert alert.enabled is True


def test_check_metrics():
    """Test checking metrics against alerts."""
    manager = AlertManager()
    manager.create_alert('cpu_alert', 'High CPU', 'cpu.percent', '>', 80)
    
    metrics = {
        'cpu': {'percent': 90},
        'memory': {'percent': 60}
    }
    
    triggered = manager.check_metrics(metrics)
    assert len(triggered) == 1
    assert triggered[0]['alert_id'] == 'cpu_alert'


def test_alert_callback():
    """Test alert callbacks."""
    manager = AlertManager()
    manager.create_alert('alert1', 'Test', 'cpu.percent', '>', 50)
    
    callback_called = {'count': 0}
    
    def test_callback(alert_event):
        callback_called['count'] += 1
    
    manager.register_callback(test_callback)
    
    metrics = {'cpu': {'percent': 60}}
    manager.check_metrics(metrics)
    
    assert callback_called['count'] == 1
