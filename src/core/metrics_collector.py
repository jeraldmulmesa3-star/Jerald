"""Metrics Collection Module

Responsible for collecting system and application metrics.
"""

import psutil
import time
from datetime import datetime
from typing import Dict, Any, List
import threading
import json


class MetricsCollector:
    """Collects and manages performance metrics."""

    def __init__(self, collection_interval: int = 5):
        """
        Initialize the metrics collector.

        Args:
            collection_interval: Time in seconds between metric collections
        """
        self.collection_interval = collection_interval
        self.metrics_history = []
        self.is_running = False
        self.collector_thread = None
        self.custom_metrics = {}

    def start_monitoring(self) -> None:
        """Start the metrics collection thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.collector_thread = threading.Thread(
            target=self._collect_metrics_loop,
            daemon=True
        )
        self.collector_thread.start()
        print(f"Metrics collection started (interval: {self.collection_interval}s)")

    def stop_monitoring(self) -> None:
        """Stop the metrics collection thread."""
        self.is_running = False
        if self.collector_thread:
            self.collector_thread.join()
        print("Metrics collection stopped")

    def _collect_metrics_loop(self) -> None:
        """Main loop for collecting metrics."""
        while self.is_running:
            metrics = self.collect_system_metrics()
            self.metrics_history.append(metrics)
            # Keep only last 1000 entries
            if len(self.metrics_history) > 1000:
                self.metrics_history.pop(0)
            time.sleep(self.collection_interval)

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics.

        Returns:
            Dictionary containing system metrics
        """
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count(),
            },
            'memory': {
                'total': memory.total,
                'used': memory.used,
                'percent': memory.percent,
                'available': memory.available,
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'percent': disk.percent,
            },
            'custom': self.custom_metrics.copy(),
        }
        return metrics

    def record_custom_metric(self, metric_name: str, value: float, 
                            unit: str = "ms") -> None:
        """Record a custom application metric.

        Args:
            metric_name: Name of the metric
            value: Numeric value of the metric
            unit: Unit of measurement
        """
        self.custom_metrics[metric_name] = {
            'value': value,
            'unit': unit,
            'timestamp': datetime.now().isoformat(),
        }

    def get_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent collected metrics.

        Args:
            limit: Maximum number of metric records to return

        Returns:
            List of recent metric dictionaries
        """
        return self.metrics_history[-limit:]

    def get_latest_metric(self) -> Dict[str, Any] | None:
        """Get the most recent metric.

        Returns:
            Latest metric dictionary or None if no metrics collected
        """
        return self.metrics_history[-1] if self.metrics_history else None

    def export_metrics(self, filepath: str, format: str = "json") -> None:
        """Export collected metrics to file.

        Args:
            filepath: Path to export file
            format: Export format ('json' or 'csv')
        """
        if format == "json":
            with open(filepath, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
        elif format == "csv":
            import csv
            if not self.metrics_history:
                return
            
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.metrics_history[0].keys())
                writer.writeheader()
                writer.writerows(self.metrics_history)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def clear_history(self) -> None:
        """Clear all collected metrics history."""
        self.metrics_history = []
