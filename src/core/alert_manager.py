"""Alert Management Module

Handles alert configuration and triggering based on performance metrics.
"""

from typing import Dict, Any, Callable, List
from datetime import datetime
import json


class Alert:
    """Represents a single alert condition."""

    def __init__(self, alert_id: str, name: str, metric: str, 
                 operator: str, threshold: float, severity: str = "warning"):
        """
        Initialize an alert.

        Args:
            alert_id: Unique identifier for the alert
            name: Human-readable alert name
            metric: Metric to monitor (e.g., 'cpu.percent')
            operator: Comparison operator ('>', '<', '>=', '<=', '==')
            threshold: Threshold value to trigger alert
            severity: Alert severity level ('info', 'warning', 'critical')
        """
        self.alert_id = alert_id
        self.name = name
        self.metric = metric
        self.operator = operator
        self.threshold = threshold
        self.severity = severity
        self.enabled = True
        self.triggered_count = 0
        self.last_triggered = None

    def check_condition(self, metric_value: float) -> bool:
        """Check if alert condition is met.

        Args:
            metric_value: Current value of the metric

        Returns:
            True if alert condition is triggered
        """
        if not self.enabled:
            return False
        
        if self.operator == '>':
            return metric_value > self.threshold
        elif self.operator == '<':
            return metric_value < self.threshold
        elif self.operator == '>=':
            return metric_value >= self.threshold
        elif self.operator == '<=':
            return metric_value <= self.threshold
        elif self.operator == '==':
            return metric_value == self.threshold
        return False


class AlertManager:
    """Manages performance alerts and notifications."""

    def __init__(self):
        """Initialize the alert manager."""
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self.callbacks: List[Callable] = []

    def create_alert(self, alert_id: str, name: str, metric: str,
                    operator: str, threshold: float, 
                    severity: str = "warning") -> Alert:
        """Create a new alert.

        Args:
            alert_id: Unique identifier
            name: Alert name
            metric: Metric to monitor
            operator: Comparison operator
            threshold: Threshold value
            severity: Severity level

        Returns:
            Created Alert object
        """
        alert = Alert(alert_id, name, metric, operator, threshold, severity)
        self.alerts[alert_id] = alert
        return alert

    def remove_alert(self, alert_id: str) -> bool:
        """Remove an alert.

        Args:
            alert_id: Alert identifier

        Returns:
            True if alert was removed
        """
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            return True
        return False

    def enable_alert(self, alert_id: str) -> bool:
        """Enable an alert.

        Args:
            alert_id: Alert identifier

        Returns:
            True if alert was enabled
        """
        if alert_id in self.alerts:
            self.alerts[alert_id].enabled = True
            return True
        return False

    def disable_alert(self, alert_id: str) -> bool:
        """Disable an alert.

        Args:
            alert_id: Alert identifier

        Returns:
            True if alert was disabled
        """
        if alert_id in self.alerts:
            self.alerts[alert_id].enabled = False
            return True
        return False

    def check_metrics(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check all alerts against current metrics.

        Args:
            metrics: Current metrics dictionary

        Returns:
            List of triggered alerts
        """
        triggered = []
        
        for alert_id, alert in self.alerts.items():
            metric_value = self._get_metric_value(metrics, alert.metric)
            
            if metric_value is not None and alert.check_condition(metric_value):
                alert.triggered_count += 1
                alert.last_triggered = datetime.now().isoformat()
                
                alert_event = {
                    'alert_id': alert_id,
                    'name': alert.name,
                    'metric': alert.metric,
                    'value': metric_value,
                    'threshold': alert.threshold,
                    'severity': alert.severity,
                    'timestamp': datetime.now().isoformat(),
                    'triggered_count': alert.triggered_count,
                }
                
                triggered.append(alert_event)
                self.alert_history.append(alert_event)
                
                # Call registered callbacks
                for callback in self.callbacks:
                    try:
                        callback(alert_event)
                    except Exception as e:
                        print(f"Error calling alert callback: {e}")
        
        return triggered

    def register_callback(self, callback: Callable) -> None:
        """Register a callback function to be called when alerts trigger.

        Args:
            callback: Callable that accepts an alert event dict
        """
        self.callbacks.append(callback)

    def get_alert(self, alert_id: str) -> Alert | None:
        """Get an alert by ID.

        Args:
            alert_id: Alert identifier

        Returns:
            Alert object or None if not found
        """
        return self.alerts.get(alert_id)

    def list_alerts(self) -> List[Alert]:
        """Get all alerts.

        Returns:
            List of all Alert objects
        """
        return list(self.alerts.values())

    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of recent alert events
        """
        return self.alert_history[-limit:]

    def _get_metric_value(self, metrics: Dict[str, Any], metric_path: str) -> float | None:
        """Extract a metric value using dot notation.

        Args:
            metrics: Metrics dictionary
            metric_path: Path to metric (e.g., 'cpu.percent')

        Returns:
            Metric value or None if not found
        """
        parts = metric_path.split('.')
        value = metrics
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return float(value) if isinstance(value, (int, float)) else None

    def clear_history(self) -> None:
        """Clear alert history."""
        self.alert_history = []
