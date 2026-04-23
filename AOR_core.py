#!/usr/bin/env python3
"""AOR_core.py — Agent Orchestration Runtime core module.

Provides the foundational primitives for multi-agent coordination
within the knowledge base system: task routing, state management,
and inter-agent communication.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

log = logging.getLogger("aor_core")


class TaskStatus(Enum):
    """Lifecycle states for orchestrated tasks."""

    PENDING = "pending"
    DISPATCHED = "dispatched"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentType(Enum):
    """Supported agent backends."""

    CLAUDE = "claude"
    CODEX = "codex"
    GEMINI = "gemini"
    OPENCODE = "opencode"


@dataclass
class Task:
    """A unit of work dispatched to an agent."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    prompt: str = ""
    directory: str = "."
    agent: AgentType = AgentType.CLAUDE
    priority: str = "P1"
    status: TaskStatus = TaskStatus.PENDING
    result: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: str | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["agent"] = self.agent.value
        d["status"] = self.status.value
        return d


@dataclass
class OrchestratorState:
    """Runtime state for the agent orchestrator."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tasks: list[Task] = field(default_factory=list)
    completed_count: int = 0
    failed_count: int = 0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_pending(self) -> list[Task]:
        return [t for t in self.tasks if t.status == TaskStatus.PENDING]

    def get_by_agent(self, agent: AgentType) -> list[Task]:
        return [t for t in self.tasks if t.agent == agent]

    def complete_task(self, task_id: str, result: dict | None = None) -> None:
        for task in self.tasks:
            if task.id == task_id:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(timezone.utc).isoformat()
                if result:
                    task.result = result
                self.completed_count += 1
                return
        raise ValueError(f"Task {task_id} not found")

    def fail_task(self, task_id: str, reason: str = "") -> None:
        for task in self.tasks:
            if task.id == task_id:
                task.status = TaskStatus.FAILED
                task.result = {"error": reason}
                self.failed_count += 1
                return
        raise ValueError(f"Task {task_id} not found")

    def save(self, path: Path) -> None:
        data = {
            "session_id": self.session_id,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count,
            "created_at": self.created_at,
            "tasks": [t.to_dict() for t in self.tasks],
        }
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> OrchestratorState:
        raw = json.loads(path.read_text())
        state = cls(
            session_id=raw["session_id"],
            completed_count=raw.get("completed_count", 0),
            failed_count=raw.get("failed_count", 0),
            created_at=raw.get("created_at", ""),
        )
        for t in raw.get("tasks", []):
            task = Task(
                id=t["id"],
                prompt=t.get("prompt", ""),
                directory=t.get("directory", "."),
                agent=AgentType(t.get("agent", "claude")),
                priority=t.get("priority", "P1"),
                status=TaskStatus(t.get("status", "pending")),
                result=t.get("result", {}),
                created_at=t.get("created_at", ""),
                completed_at=t.get("completed_at"),
            )
            state.tasks.append(task)
        return state


def route_task(prompt: str, domain: str = "general") -> AgentType:
    """Route a task to the most appropriate agent based on content heuristics.

    Architecture/debugging/audit -> Claude
    Boilerplate/scaffolding -> Codex
    Content/research -> Gemini
    Infrastructure -> OpenCode
    """
    prompt_lower = prompt.lower()

    if any(w in prompt_lower for w in ("architect", "debug", "audit", "design", "review")):
        return AgentType.CLAUDE
    if any(w in prompt_lower for w in ("scaffold", "boilerplate", "create file", "create the file")):
        return AgentType.CODEX
    if any(w in prompt_lower for w in ("research", "content", "draft", "essay", "summarize")):
        return AgentType.GEMINI
    if any(w in prompt_lower for w in ("infra", "deploy", "ci", "docker", "terraform")):
        return AgentType.OPENCODE

    return AgentType.CODEX  # default for mechanical work
