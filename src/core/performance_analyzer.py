"""Performance Analysis Module

Analyzes collected metrics to identify patterns and anomalies.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import statistics


class PerformanceAnalyzer:
    """Analyzes performance metrics for trends and anomalies."""

    def __init__(self):
        """Initialize the performance analyzer."""
        self.analysis_cache = {}

    def analyze_metrics(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a collection of metrics.

        Args:
            metrics_history: List of metric dictionaries

        Returns:
            Analysis results including statistics and anomalies
        """
        if not metrics_history:
            return {}

        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_samples': len(metrics_history),
            'cpu_analysis': self._analyze_cpu(metrics_history),
            'memory_analysis': self._analyze_memory(metrics_history),
            'disk_analysis': self._analyze_disk(metrics_history),
            'anomalies': self._detect_anomalies(metrics_history),
        }
        return analysis

    def _analyze_cpu(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze CPU metrics.

        Args:
            metrics_history: List of metric dictionaries

        Returns:
            CPU analysis statistics
        """
        cpu_values = [m['cpu']['percent'] for m in metrics_history]
        
        return {
            'avg': round(statistics.mean(cpu_values), 2),
            'min': round(min(cpu_values), 2),
            'max': round(max(cpu_values), 2),
            'median': round(statistics.median(cpu_values), 2),
            'stdev': round(statistics.stdev(cpu_values), 2) if len(cpu_values) > 1 else 0,
            'trend': self._calculate_trend(cpu_values),
        }

    def _analyze_memory(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze memory metrics.

        Args:
            metrics_history: List of metric dictionaries

        Returns:
            Memory analysis statistics
        """
        memory_percent = [m['memory']['percent'] for m in metrics_history]
        memory_used = [m['memory']['used'] / (1024**3) for m in metrics_history]  # Convert to GB
        
        return {
            'avg_percent': round(statistics.mean(memory_percent), 2),
            'max_percent': round(max(memory_percent), 2),
            'avg_used_gb': round(statistics.mean(memory_used), 2),
            'max_used_gb': round(max(memory_used), 2),
            'trend': self._calculate_trend(memory_percent),
        }

    def _analyze_disk(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze disk metrics.

        Args:
            metrics_history: List of metric dictionaries

        Returns:
            Disk analysis statistics
        """
        disk_percent = [m['disk']['percent'] for m in metrics_history]
        
        return {
            'avg_percent': round(statistics.mean(disk_percent), 2),
            'current_percent': round(disk_percent[-1], 2),
            'trend': self._calculate_trend(disk_percent),
        }

    def _detect_anomalies(self, metrics_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics using standard deviation.

        Args:
            metrics_history: List of metric dictionaries

        Returns:
            List of detected anomalies
        """
        anomalies = []
        cpu_values = [m['cpu']['percent'] for m in metrics_history]
        memory_values = [m['memory']['percent'] for m in metrics_history]
        
        # Simple anomaly detection using z-score
        if len(cpu_values) > 3:
            cpu_mean = statistics.mean(cpu_values)
            cpu_stdev = statistics.stdev(cpu_values)
            for i, value in enumerate(cpu_values):
                z_score = abs((value - cpu_mean) / (cpu_stdev + 0.001))
                if z_score > 2.5:  # Threshold for anomaly
                    anomalies.append({
                        'type': 'cpu_spike',
                        'index': i,
                        'timestamp': metrics_history[i]['timestamp'],
                        'value': value,
                        'z_score': round(z_score, 2),
                    })
        
        if len(memory_values) > 3:
            memory_mean = statistics.mean(memory_values)
            memory_stdev = statistics.stdev(memory_values)
            for i, value in enumerate(memory_values):
                z_score = abs((value - memory_mean) / (memory_stdev + 0.001))
                if z_score > 2.5:
                    anomalies.append({
                        'type': 'memory_spike',
                        'index': i,
                        'timestamp': metrics_history[i]['timestamp'],
                        'value': value,
                        'z_score': round(z_score, 2),
                    })
        
        return anomalies

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values.

        Args:
            values: List of numeric values

        Returns:
            Trend direction: 'increasing', 'decreasing', or 'stable'
        """
        if len(values) < 2:
            return 'stable'
        
        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])
        
        diff_percent = ((second_half - first_half) / (first_half + 0.001)) * 100
        
        if diff_percent > 5:
            return 'increasing'
        elif diff_percent < -5:
            return 'decreasing'
        else:
            return 'stable'

    def get_performance_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate an overall performance score (0-100).

        Args:
            analysis: Analysis results from analyze_metrics()

        Returns:
            Performance score between 0 and 100
        """
        if not analysis:
            return 0.0
        
        cpu_score = max(0, 100 - analysis['cpu_analysis']['avg'] * 1.5)
        memory_score = max(0, 100 - analysis['memory_analysis']['avg_percent'] * 1.2)
        anomaly_penalty = len(analysis['anomalies']) * 5
        
        score = (cpu_score + memory_score) / 2 - anomaly_penalty
        return max(0, min(100, score))
