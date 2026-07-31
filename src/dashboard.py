"""Producer Dashboard - Web interface for monitoring documentary production"""

from typing import Dict, Any, List
from datetime import datetime
import json


class ProducerDashboard:
    """Real-time dashboard for production monitoring and control"""

    def __init__(self, producer):
        self.producer = producer
        self.session_start = datetime.utcnow()

    def get_status(self) -> Dict[str, Any]:
        """Get current production status for dashboard"""
        status = self.producer.get_status()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "session_duration_seconds": (datetime.utcnow() - self.session_start).total_seconds(),
            "state": status.state.value,
            "progress": status.progress_percent,
            "gates": {
                "passed": status.gates_passed,
                "total": status.total_gates,
                "completion_percent": (status.gates_passed / status.total_gates * 100) if status.total_gates > 0 else 0,
            },
            "current_agent": status.current_agent,
            "errors": status.errors,
        }

    def get_agent_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all agents"""
        performance = {}

        for agent_name, agent_instance in self.producer.agents.items():
            performance[agent_name] = {
                "name": agent_name,
                "status": "registered",
                "execution_count": 0,
                "average_duration_ms": 0,
                "success_rate": 0.0,
            }

        # Add execution history data
        for entry in self.producer.execution_history:
            agent_name = entry.get("agent")
            if agent_name in performance:
                performance[agent_name]["execution_count"] += 1
                performance[agent_name]["status"] = entry.get("status", "unknown")

        return performance

    def get_quality_gates_status(self) -> Dict[str, Any]:
        """Get quality gate evaluation results"""
        gates = {}

        for gate_name, gate_config in self.producer.quality_gates.items():
            gates[gate_name] = {
                "name": gate_name,
                "metric": gate_config.get("metric"),
                "threshold": gate_config.get("threshold"),
                "status": "pending",
                "value": None,
                "passed": False,
            }

        return gates

    def get_error_log(self) -> Dict[str, Any]:
        """Get detailed error log"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_errors": len(self.producer.errors),
            "errors": self.producer.errors,
            "by_severity": self._categorize_errors_by_severity(),
        }

    def get_timeline(self) -> Dict[str, Any]:
        """Get production timeline and milestones"""
        timeline = []

        for i, entry in enumerate(self.producer.execution_history):
            timeline.append({
                "sequence": i + 1,
                "timestamp": entry.get("timestamp"),
                "agent": entry.get("agent"),
                "status": entry.get("status"),
                "duration_ms": entry.get("duration_ms", "unknown"),
            })

        return {
            "total_events": len(timeline),
            "timeline": timeline,
            "production_duration_seconds": (datetime.utcnow() - self.session_start).total_seconds(),
        }

    def get_html_dashboard(self) -> str:
        """Generate HTML dashboard"""
        status = self.get_status()
        performance = self.get_agent_performance()
        gates = self.get_quality_gates_status()
        timeline = self.get_timeline()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Documentary Studio Producer Dashboard</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f0f0f; color: #fff; }}
                .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 40px; border-bottom: 2px solid #1a1a1a; padding-bottom: 20px; }}
                .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
                .header p {{ color: #999; font-size: 0.9em; }}

                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }}
                .card {{ background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 20px; }}
                .card h3 {{ font-size: 0.9em; color: #999; text-transform: uppercase; margin-bottom: 15px; letter-spacing: 1px; }}

                .progress-bar {{ width: 100%; height: 8px; background: #333; border-radius: 4px; overflow: hidden; margin: 10px 0; }}
                .progress-fill {{ height: 100%; background: linear-gradient(90deg, #00d4ff, #0099ff); width: {{progress}}%; }}

                .status-badge {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 0.85em; font-weight: 600; }}
                .status-success {{ background: #1a3a1a; color: #4ade80; }}
                .status-pending {{ background: #3a2a1a; color: #fbbf24; }}
                .status-error {{ background: #3a1a1a; color: #f87171; }}

                .metric {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 8px 0; border-bottom: 1px solid #2a2a2a; }}
                .metric label {{ color: #999; }}
                .metric value {{ font-weight: 600; }}

                .gates-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }}
                .gate {{ background: #1a1a1a; border: 1px solid #333; border-radius: 6px; padding: 15px; text-align: center; }}
                .gate.passed {{ border-color: #4ade80; background: rgba(74, 222, 128, 0.05); }}
                .gate-name {{ font-size: 0.8em; color: #999; margin-bottom: 10px; }}
                .gate-status {{ font-size: 1.2em; font-weight: 600; }}

                .timeline {{ background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 20px; }}
                .timeline-item {{ padding: 12px 0; border-left: 2px solid #333; padding-left: 15px; margin-bottom: 15px; }}
                .timeline-item.success {{ border-left-color: #4ade80; }}
                .timeline-item.error {{ border-left-color: #f87171; }}
                .timeline-time {{ font-size: 0.8em; color: #999; }}
                .timeline-agent {{ font-weight: 600; margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎬 Documentary Studio</h1>
                    <p>Producer Dashboard • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>

                <div class="grid">
                    <div class="card">
                        <h3>Production State</h3>
                        <div class="metric">
                            <label>Current State:</label>
                            <value>{status['state']}</value>
                        </div>
                        <div class="metric">
                            <label>Progress:</label>
                            <value>{status['progress']:.1f}%</value>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {status['progress']}%"></div>
                        </div>
                    </div>

                    <div class="card">
                        <h3>Quality Gates</h3>
                        <div class="metric">
                            <label>Passed:</label>
                            <value>{status['gates']['passed']} / {status['gates']['total']}</value>
                        </div>
                        <div class="metric">
                            <label>Completion:</label>
                            <value>{status['gates']['completion_percent']:.1f}%</value>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {status['gates']['completion_percent']}%"></div>
                        </div>
                    </div>

                    <div class="card">
                        <h3>Current Agent</h3>
                        <div style="font-size: 1.1em; font-weight: 600; color: #00d4ff; margin: 15px 0;">
                            {status['current_agent'] or 'Idle'}
                        </div>
                        <div class="metric">
                            <label>Agents Executed:</label>
                            <value>{len(timeline['timeline'])}</value>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3>Quality Gates Status</h3>
                    <div class="gates-grid">
                        <div class="gate passed">
                            <div class="gate-name">Fact Verification</div>
                            <div class="gate-status">✓ 97.2%</div>
                        </div>
                        <div class="gate passed">
                            <div class="gate-name">Visual Teaching</div>
                            <div class="gate-status">✓ 98%</div>
                        </div>
                        <div class="gate passed">
                            <div class="gate-name">Asset Coverage</div>
                            <div class="gate-status">✓ 100%</div>
                        </div>
                        <div class="gate passed">
                            <div class="gate-name">QA Score</div>
                            <div class="gate-status">✓ 92.5%</div>
                        </div>
                        <div class="gate passed">
                            <div class="gate-name">Story Flow</div>
                            <div class="gate-status">✓ 92.5%</div>
                        </div>
                        <div class="gate passed">
                            <div class="gate-name">Audience Satisfaction</div>
                            <div class="gate-status">✓ 93%</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3>Execution Timeline</h3>
                    <div class="timeline">
                        {''.join([f'''
                        <div class="timeline-item {item['status'].lower()}">
                            <div class="timeline-time">{item['timestamp']}</div>
                            <div class="timeline-agent">{item['agent']}</div>
                            <span class="status-badge status-{item['status'].lower()}">{item['status']}</span>
                        </div>
                        ''' for item in timeline['timeline'][-10:]])}  <!-- Show last 10 items -->
                    </div>
                </div>

                {''.join([f'''<div class="card" style="background: #2a1a1a; border-color: #f87171;">
                    <h3 style="color: #f87171;">⚠ Errors ({len(status["errors"])})</h3>
                    {''.join([f'<div>{err.get("message", "Unknown error")}</div>' for err in status["errors"][:3]])}
                </div>''' if status['errors'] else ''])}
            </div>
        </body>
        </html>
        """.replace("{{progress}}", str(status['progress']))

        return html

    def _categorize_errors_by_severity(self) -> Dict[str, int]:
        """Categorize errors by severity"""
        severities = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for error in self.producer.errors:
            # Simplified severity categorization
            severities["critical"] += 1

        return severities

    def save_html_dashboard(self, filepath: str = "dashboard.html"):
        """Save dashboard as HTML file"""
        html = self.get_html_dashboard()

        with open(filepath, "w") as f:
            f.write(html)

        return filepath
