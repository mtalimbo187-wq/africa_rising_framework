#!/usr/bin/env python3
"""
Comprehensive Logging & Observability

Structured logging for every agent action, API call, cost tracking,
and telemetry collection.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class AgentAction:
    """Record of a single agent action"""
    timestamp: str
    agent_name: str
    action_type: str  # script_analysis, asset_search, api_call, etc.
    status: str  # success, failed, partial
    duration_ms: float
    cost_usd: float = 0.0
    model_used: Optional[str] = None
    prompt_version: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class APICall:
    """Record of an API call"""
    timestamp: str
    provider: str  # OpenAI, ElevenLabs, Google, etc.
    endpoint: str
    method: str  # POST, GET, etc.
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    response_time_ms: float = 0.0
    status_code: int = 200
    error_message: Optional[str] = None


class ProductionLogger:
    """Structured logging for production pipelines"""

    def __init__(self, log_dir: str = "output/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Set up JSON logging
        self.production_log = self.log_dir / "production.jsonl"
        self.api_log = self.log_dir / "api_calls.jsonl"
        self.error_log = self.log_dir / "errors.jsonl"
        self.cost_log = self.log_dir / "costs.jsonl"

        # Set up standard logger
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup standard logging configuration"""
        logger = logging.getLogger("production")
        logger.setLevel(logging.DEBUG)

        # File handler for all logs
        fh = logging.FileHandler(self.log_dir / "application.log")
        fh.setLevel(logging.DEBUG)

        # Console handler for important logs
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def log_agent_action(self, agent_name: str, action_type: str, status: str,
                        duration_ms: float, cost_usd: float = 0.0,
                        model_used: Optional[str] = None,
                        prompt_version: Optional[str] = None,
                        input_tokens: int = 0, output_tokens: int = 0,
                        error_message: Optional[str] = None,
                        metadata: Optional[Dict] = None):
        """Log agent action"""
        action = AgentAction(
            timestamp=datetime.now().isoformat(),
            agent_name=agent_name,
            action_type=action_type,
            status=status,
            duration_ms=duration_ms,
            cost_usd=cost_usd,
            model_used=model_used,
            prompt_version=prompt_version,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error_message=error_message,
            metadata=metadata or {}
        )

        # Write to production log
        with open(self.production_log, "a") as f:
            f.write(json.dumps(asdict(action)) + "\n")

        # Log level based on status
        if status == "success":
            self.logger.info(f"{agent_name}: {action_type} completed in {duration_ms:.0f}ms (${cost_usd:.2f})")
        elif status == "partial":
            self.logger.warning(f"{agent_name}: {action_type} completed with issues in {duration_ms:.0f}ms")
        else:
            self.logger.error(f"{agent_name}: {action_type} failed - {error_message}")

    def log_api_call(self, provider: str, endpoint: str, method: str = "POST",
                    input_tokens: int = 0, output_tokens: int = 0,
                    cost_usd: float = 0.0, response_time_ms: float = 0.0,
                    status_code: int = 200, error_message: Optional[str] = None):
        """Log API call"""
        api_call = APICall(
            timestamp=datetime.now().isoformat(),
            provider=provider,
            endpoint=endpoint,
            method=method,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            response_time_ms=response_time_ms,
            status_code=status_code,
            error_message=error_message
        )

        # Write to API log
        with open(self.api_log, "a") as f:
            f.write(json.dumps(asdict(api_call)) + "\n")

        # Log cost to cost log
        self._log_cost(provider, cost_usd)

        if status_code >= 400:
            self.logger.warning(f"API Error {status_code}: {provider} {endpoint} - {error_message}")
        else:
            self.logger.debug(f"API: {provider} {endpoint} - {response_time_ms:.0f}ms, ${cost_usd:.4f}")

    def _log_cost(self, provider: str, cost_usd: float):
        """Log cost separately for billing tracking"""
        cost_entry = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "cost_usd": cost_usd
        }

        with open(self.cost_log, "a") as f:
            f.write(json.dumps(cost_entry) + "\n")

    def log_error(self, agent_name: str, error_type: str, message: str, context: Optional[Dict] = None):
        """Log error"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "error_type": error_type,
            "message": message,
            "context": context or {}
        }

        with open(self.error_log, "a") as f:
            f.write(json.dumps(error_entry) + "\n")

        self.logger.error(f"[{agent_name}] {error_type}: {message}")

    def generate_project_telemetry(self) -> Dict[str, Any]:
        """Aggregate all logs and generate project telemetry"""
        telemetry = {
            "timestamp": datetime.now().isoformat(),
            "total_agents": 0,
            "total_duration_seconds": 0.0,
            "total_cost_usd": 0.0,
            "api_calls_total": 0,
            "api_calls_by_provider": {},
            "agents": {},
            "cost_breakdown": {},
            "errors": []
        }

        # Parse production log
        if self.production_log.exists():
            agents_data = {}
            with open(self.production_log) as f:
                for line in f:
                    action = json.loads(line)
                    agent = action["agent_name"]

                    if agent not in agents_data:
                        agents_data[agent] = {
                            "total_actions": 0,
                            "successful_actions": 0,
                            "failed_actions": 0,
                            "total_duration_ms": 0,
                            "total_cost_usd": 0.0
                        }

                    agents_data[agent]["total_actions"] += 1
                    if action["status"] == "success":
                        agents_data[agent]["successful_actions"] += 1
                    else:
                        agents_data[agent]["failed_actions"] += 1
                    agents_data[agent]["total_duration_ms"] += action["duration_ms"]
                    agents_data[agent]["total_cost_usd"] += action["cost_usd"]

            telemetry["agents"] = agents_data
            telemetry["total_agents"] = len(agents_data)
            telemetry["total_duration_seconds"] = sum(
                a["total_duration_ms"] for a in agents_data.values()
            ) / 1000

        # Parse API log
        if self.api_log.exists():
            api_by_provider = {}
            with open(self.api_log) as f:
                for line in f:
                    call = json.loads(line)
                    provider = call["provider"]

                    if provider not in api_by_provider:
                        api_by_provider[provider] = {
                            "call_count": 0,
                            "total_cost_usd": 0.0,
                            "total_input_tokens": 0,
                            "total_output_tokens": 0
                        }

                    api_by_provider[provider]["call_count"] += 1
                    api_by_provider[provider]["total_cost_usd"] += call["cost_usd"]
                    api_by_provider[provider]["total_input_tokens"] += call["input_tokens"]
                    api_by_provider[provider]["total_output_tokens"] += call["output_tokens"]

            telemetry["api_calls_by_provider"] = api_by_provider
            telemetry["api_calls_total"] = sum(
                p["call_count"] for p in api_by_provider.values()
            )
            telemetry["total_cost_usd"] = sum(
                p["total_cost_usd"] for p in api_by_provider.values()
            )

        # Parse cost log
        if self.cost_log.exists():
            cost_by_provider = {}
            with open(self.cost_log) as f:
                for line in f:
                    cost_entry = json.loads(line)
                    provider = cost_entry["provider"]
                    cost_by_provider[provider] = cost_by_provider.get(provider, 0) + cost_entry["cost_usd"]

            telemetry["cost_breakdown"] = cost_by_provider

        # Parse error log
        if self.error_log.exists():
            errors = []
            with open(self.error_log) as f:
                for line in f:
                    errors.append(json.loads(line))

            telemetry["errors"] = errors

        return telemetry

    def save_telemetry(self, output_file: str = "project_telemetry.json"):
        """Generate and save telemetry report"""
        telemetry = self.generate_project_telemetry()

        with open(self.log_dir / output_file, "w") as f:
            json.dump(telemetry, f, indent=2)

        return telemetry

    def print_summary(self):
        """Print telemetry summary to console"""
        telemetry = self.generate_project_telemetry()

        print("\n" + "=" * 60)
        print("PROJECT TELEMETRY SUMMARY")
        print("=" * 60)
        print(f"Total Agents: {telemetry['total_agents']}")
        print(f"Total Duration: {telemetry['total_duration_seconds']:.1f}s")
        print(f"Total Cost: ${telemetry['total_cost_usd']:.2f}")
        print(f"API Calls: {telemetry['api_calls_total']}")
        print(f"Errors: {len(telemetry['errors'])}")

        print("\nCost Breakdown:")
        for provider, cost in telemetry["cost_breakdown"].items():
            print(f"  {provider}: ${cost:.2f}")

        print("\n" + "=" * 60)
