#!/usr/bin/env python3
"""
Resource Monitoring & Alerts

Tracks:
- CPU and memory usage
- GPU utilization (if available)
- API costs in real-time
- Job progress and ETAs
"""

import psutil
import time
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
import json


class ResourceMonitor:
    """Monitor system and API resources"""

    def __init__(self, budget_limit_usd: float = 100.0):
        self.budget_limit = budget_limit_usd
        self.current_cost = 0.0
        self.start_time = time.time()
        self.samples = []

    def track_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        process = psutil.Process()
        mem_info = process.memory_info()

        usage = {
            "rss_mb": mem_info.rss / 1024 / 1024,
            "vms_mb": mem_info.vms / 1024 / 1024,
            "percent": process.memory_percent()
        }

        return usage

    def track_cpu_usage(self) -> Dict[str, float]:
        """Get CPU usage"""
        process = psutil.Process()

        usage = {
            "percent_one_core": process.cpu_percent(interval=1),
            "percent_all_cores": psutil.cpu_percent(),
            "num_threads": process.num_threads()
        }

        return usage

    def track_gpu_utilization(self) -> Optional[Dict[str, float]]:
        """Get GPU utilization (if available)"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # First GPU
                return {
                    "id": gpu.id,
                    "name": gpu.name,
                    "load_percent": gpu.load * 100,
                    "memory_used_mb": gpu.memoryUsed,
                    "memory_total_mb": gpu.memoryTotal,
                    "memory_percent": (gpu.memoryUsed / gpu.memoryTotal) * 100
                }
        except ImportError:
            pass
        return None

    def track_disk_usage(self, path: str = ".") -> Dict[str, float]:
        """Get disk usage"""
        usage = psutil.disk_usage(path)
        return {
            "used_gb": usage.used / 1024 / 1024 / 1024,
            "total_gb": usage.total / 1024 / 1024 / 1024,
            "free_gb": usage.free / 1024 / 1024 / 1024,
            "percent": usage.percent
        }

    def track_api_costs_realtime(self, provider: str, cost_usd: float) -> Dict[str, Any]:
        """Track API costs and alert if over budget"""
        self.current_cost += cost_usd

        result = {
            "provider": provider,
            "cost_usd": cost_usd,
            "total_cost_usd": self.current_cost,
            "budget_remaining": self.budget_limit - self.current_cost,
            "percent_of_budget": (self.current_cost / self.budget_limit) * 100 if self.budget_limit > 0 else 0,
            "budget_exceeded": self.current_cost > self.budget_limit
        }

        # Generate alert if over budget
        if result["budget_exceeded"]:
            result["alert"] = f"⚠️  BUDGET EXCEEDED: ${self.current_cost:.2f} > ${self.budget_limit:.2f}"

        # Warn at 80% of budget
        if result["percent_of_budget"] >= 80:
            result["warning"] = f"⚠️  80% of budget used (${self.current_cost:.2f}/${self.budget_limit:.2f})"

        return result

    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        elapsed = time.time() - self.start_time

        report = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            "cpu": self.track_cpu_usage(),
            "memory": self.track_memory_usage(),
            "disk": self.track_disk_usage(),
            "api_costs": {
                "current_total": self.current_cost,
                "budget_limit": self.budget_limit,
                "percent_used": (self.current_cost / self.budget_limit) * 100 if self.budget_limit > 0 else 0
            }
        }

        # Add GPU if available
        gpu = self.track_gpu_utilization()
        if gpu:
            report["gpu"] = gpu

        # Identify resource constraints
        constraints = []
        if report["memory"]["percent"] > 80:
            constraints.append("High memory usage (>80%)")
        if report["cpu"]["percent_all_cores"] > 80:
            constraints.append("High CPU usage (>80%)")
        if report["api_costs"]["percent_used"] > 80:
            constraints.append("High API cost usage (>80%)")

        report["resource_constraints"] = constraints
        report["health_status"] = (
            "CRITICAL" if len(constraints) > 2 else
            "WARNING" if len(constraints) > 0 else
            "OK"
        )

        return report

    def print_status(self):
        """Print status to console"""
        report = self.generate_status_report()

        print("\n" + "=" * 60)
        print("RESOURCE STATUS REPORT")
        print("=" * 60)
        print(f"Status: {report['health_status']}")
        print(f"Elapsed: {report['elapsed_seconds']:.1f}s")
        print(f"\nCPU: {report['cpu']['percent_all_cores']:.1f}% | Memory: {report['memory']['percent']:.1f}%")
        print(f"API Costs: ${report['api_costs']['current_total']:.2f} / ${report['api_costs']['budget_limit']:.2f}")

        if report['resource_constraints']:
            print(f"\n⚠️  Constraints:")
            for constraint in report['resource_constraints']:
                print(f"   - {constraint}")

        print("=" * 60 + "\n")


class JobMonitor:
    """Monitor long-running jobs and provide ETAs"""

    def __init__(self, total_items: int):
        self.total_items = total_items
        self.completed = 0
        self.start_time = time.time()
        self.item_times = []

    def record_item_complete(self):
        """Record completion of one item"""
        self.completed += 1
        elapsed = time.time() - self.start_time
        self.item_times.append(elapsed / self.completed if self.completed > 0 else 0)

    def get_eta_seconds(self) -> float:
        """Get estimated time remaining"""
        if self.completed == 0:
            return 0

        avg_time_per_item = sum(self.item_times) / len(self.item_times)
        remaining = self.total_items - self.completed
        return avg_time_per_item * remaining

    def get_progress_report(self) -> Dict[str, Any]:
        """Get progress report with ETA"""
        elapsed = time.time() - self.start_time
        eta_remaining = self.get_eta_seconds()

        return {
            "completed": self.completed,
            "total": self.total_items,
            "percent_complete": (self.completed / self.total_items) * 100 if self.total_items > 0 else 0,
            "elapsed_seconds": elapsed,
            "eta_seconds": eta_remaining,
            "avg_time_per_item": (elapsed / self.completed) if self.completed > 0 else 0
        }

    def print_progress(self):
        """Print progress bar to console"""
        report = self.get_progress_report()
        percent = report["percent_complete"]
        filled = int(percent / 5)
        bar = "█" * filled + "░" * (20 - filled)

        remaining_min = report["eta_seconds"] / 60
        elapsed_min = report["elapsed_seconds"] / 60

        print(f"\r[{bar}] {percent:.1f}% ({report['completed']}/{report['total']}) "
              f"ETA: {remaining_min:.1f}m | Elapsed: {elapsed_min:.1f}m", end="", flush=True)


class AlertManager:
    """Manage alerts and notifications"""

    def __init__(self, alert_log: str = "alerts.log"):
        self.alert_log = Path(alert_log)

    def create_alert(self, severity: str, message: str, context: Optional[Dict] = None):
        """Create an alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,  # INFO, WARNING, CRITICAL
            "message": message,
            "context": context or {}
        }

        with open(self.alert_log, "a") as f:
            f.write(json.dumps(alert) + "\n")

        # Print to console
        icon = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨"}[severity]
        print(f"\n{icon} {severity}: {message}")

    def alert_budget_exceeded(self, current_cost: float, limit: float):
        """Alert budget exceeded"""
        self.create_alert(
            "CRITICAL",
            f"API budget exceeded: ${current_cost:.2f} > ${limit:.2f}",
            {"current_cost": current_cost, "limit": limit}
        )

    def alert_memory_critical(self, percent: float):
        """Alert on critical memory usage"""
        self.create_alert(
            "CRITICAL",
            f"Memory usage critical: {percent:.1f}%",
            {"memory_percent": percent}
        )

    def alert_api_error(self, provider: str, error: str):
        """Alert on API error"""
        self.create_alert(
            "WARNING",
            f"API error from {provider}: {error}",
            {"provider": provider}
        )
