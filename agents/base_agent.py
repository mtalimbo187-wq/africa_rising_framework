#!/usr/bin/env python3
"""
Base Agent — Abstract class for all specialized agents

Each agent:
- Has a single responsibility
- Communicates via message queue
- Reports progress and errors
- Returns structured output
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import json
from enum import Enum


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentMessage:
    """Inter-agent communication"""
    sender: str
    receiver: str
    message_type: str  # "task", "result", "error", "status"
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentResult:
    """Agent execution result"""
    agent_name: str
    status: AgentStatus
    output: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "agent": self.agent_name,
            "status": self.status.value,
            "output": self.output,
            "errors": self.errors,
            "duration": self.duration_seconds,
            "timestamp": self.timestamp
        }


class BaseAgent(ABC):
    """Abstract base class for all agents"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.message_queue: List[AgentMessage] = []
        self.result = None
        self.start_time = None

    def send_message(self, receiver: str, message_type: str, content: Dict) -> None:
        """Send message to another agent"""
        message = AgentMessage(
            sender=self.name,
            receiver=receiver,
            message_type=message_type,
            content=content
        )
        self.message_queue.append(message)
        print(f"[{self.name}] → [{receiver}] {message_type}")

    def get_messages(self, message_type: str = None) -> List[AgentMessage]:
        """Retrieve messages for this agent"""
        if message_type:
            return [m for m in self.message_queue if m.message_type == message_type]
        return self.message_queue

    def clear_messages(self) -> None:
        """Clear processed messages"""
        self.message_queue = []

    def log_error(self, error: str) -> None:
        """Log an error"""
        if self.result is None:
            self.result = AgentResult(self.name, AgentStatus.FAILED, {})
        self.result.errors.append(error)
        print(f"❌ [{self.name}] {error}")

    def log_status(self, message: str) -> None:
        """Log status update"""
        print(f"📊 [{self.name}] {message}")

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute agent's task

        Must be implemented by subclasses
        Returns AgentResult with output
        """
        pass

    def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute agent with timing and error handling

        Wraps execute() to handle lifecycle
        """
        import time

        self.status = AgentStatus.RUNNING
        self.start_time = time.time()

        print(f"\n🚀 [{self.name}] Starting...")
        print(f"   Description: {self.description}")

        try:
            self.result = self.execute(input_data)
            self.status = self.result.status

        except Exception as e:
            self.status = AgentStatus.FAILED
            error_msg = f"Execution failed: {str(e)}"
            self.log_error(error_msg)
            self.result = AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                output={},
                errors=[error_msg]
            )

        # Timing
        duration = time.time() - self.start_time
        self.result.duration_seconds = duration

        # Status report
        status_emoji = {
            AgentStatus.COMPLETED: "✅",
            AgentStatus.FAILED: "❌",
            AgentStatus.SKIPPED: "⏭️ ",
        }.get(self.status, "❓")

        print(f"{status_emoji} [{self.name}] {self.status.value.upper()} ({duration:.1f}s)")

        return self.result

    def export_result(self, filepath: str = None) -> Dict:
        """Export result as JSON"""
        if self.result is None:
            return {}

        result_dict = self.result.to_dict()

        if filepath:
            import json
            from pathlib import Path
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(result_dict, f, indent=2)
            print(f"💾 [{self.name}] Result saved to {filepath}")

        return result_dict
