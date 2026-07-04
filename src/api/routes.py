"""API Routes for Performance Tracking System

Defines REST API endpoints for the performance tracking system.
"""

from typing import Dict, Any, List


class APIRoutes:
    """API route definitions and handlers."""

    def __init__(self, metrics_collector, analyzer, alert_manager):
        """
        Initialize API routes.

        Args:
            metrics_collector: MetricsCollector instance
            analyzer: PerformanceAnalyzer instance
            alert_manager: AlertManager instance
        """
        self.metrics_collector = metrics_collector
        self.analyzer = analyzer
        self.alert_manager = alert_manager

    def get_current_metrics(self) -> Dict[str, Any]:
        """GET /api/metrics/current - Get current system metrics."""
        return {
            'success': True,
            'data': self.metrics_collector.get_latest_metric(),
        }

    def get_metrics_history(self, limit: int = 100) -> Dict[str, Any]:
        """GET /api/metrics/history - Get metrics history."""
        return {
            'success': True,
            'data': self.metrics_collector.get_metrics(limit),
        }

    def get_analysis(self) -> Dict[str, Any]:
        """GET /api/analysis - Get performance analysis."""
        metrics = self.metrics_collector.get_metrics()
        analysis = self.analyzer.analyze_metrics(metrics)
        score = self.analyzer.get_performance_score(analysis)
        
        return {
            'success': True,
            'data': {
                'analysis': analysis,
                'performance_score': score,
            },
        }

    def create_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/alerts - Create a new alert."""
        try:
            alert = self.alert_manager.create_alert(
                alert_id=alert_data.get('id'),
                name=alert_data.get('name'),
                metric=alert_data.get('metric'),
                operator=alert_data.get('operator'),
                threshold=alert_data.get('threshold'),
                severity=alert_data.get('severity', 'warning'),
            )
            
            return {
                'success': True,
                'data': {
                    'alert_id': alert.alert_id,
                    'name': alert.name,
                },
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_alerts(self) -> Dict[str, Any]:
        """GET /api/alerts - Get all alerts."""
        alerts = self.alert_manager.list_alerts()
        return {
            'success': True,
            'data': [{
                'id': a.alert_id,
                'name': a.name,
                'metric': a.metric,
                'operator': a.operator,
                'threshold': a.threshold,
                'severity': a.severity,
                'enabled': a.enabled,
                'triggered_count': a.triggered_count,
            } for a in alerts],
        }

    def update_alert(self, alert_id: str, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """PUT /api/alerts/{id} - Update an alert."""
        alert = self.alert_manager.get_alert(alert_id)
        if not alert:
            return {'success': False, 'error': 'Alert not found'}
        
        # Update alert properties
        for key, value in alert_data.items():
            if hasattr(alert, key):
                setattr(alert, key, value)
        
        return {'success': True, 'data': {'alert_id': alert_id}}

    def delete_alert(self, alert_id: str) -> Dict[str, Any]:
        """DELETE /api/alerts/{id} - Delete an alert."""
        if self.alert_manager.remove_alert(alert_id):
            return {'success': True}
        return {'success': False, 'error': 'Alert not found'}

    def get_alert_history(self, limit: int = 100) -> Dict[str, Any]:
        """GET /api/alerts/history - Get alert history."""
        return {
            'success': True,
            'data': self.alert_manager.get_alert_history(limit),
        }

    def export_metrics(self, format: str = 'json') -> Dict[str, Any]:
        """POST /api/export - Export metrics."""
        try:
            filepath = f"metrics_export.{format}"
            self.metrics_collector.export_metrics(filepath, format)
            return {'success': True, 'data': {'filepath': filepath}}
        except Exception as e:
            return {'success': False, 'error': str(e)}
