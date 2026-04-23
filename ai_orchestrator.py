#!/usr/bin/env python3
"""ai_orchestrator.py — AI agent orchestration for knowledge base operations.

Coordinates multiple AI providers (Anthropic, OpenAI, local models)
for batch processing tasks: insight extraction, tagging, summarization,
and relationship detection.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

log = logging.getLogger("ai_orchestrator")


class Provider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    LOCAL = "local"


class TaskType(Enum):
    INSIGHT_EXTRACTION = "insight_extraction"
    SMART_TAGGING = "smart_tagging"
    SUMMARIZATION = "summarization"
    RELATIONSHIP_DETECTION = "relationship_detection"
    EMBEDDING_GENERATION = "embedding_generation"


@dataclass
class AITask:
    """A unit of AI work to be orchestrated."""

    id: str
    task_type: TaskType
    input_data: dict[str, Any]
    provider: Provider = Provider.ANTHROPIC
    priority: int = 1
    status: str = "pending"
    result: dict[str, Any] | None = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: str | None = None


@dataclass
class OrchestratorConfig:
    """Configuration for the AI orchestrator."""

    max_parallel: int = 3
    anthropic_model: str = "claude-sonnet-4-20250514"
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    max_retries: int = 2
    retry_delay_seconds: float = 1.0
    enable_caching: bool = True
    cost_limit_usd: float = 10.0


class AIOrchestrator:
    """Orchestrate AI tasks across multiple providers."""

    def __init__(self, config: OrchestratorConfig | None = None) -> None:
        self.config = config or OrchestratorConfig()
        self.tasks: list[AITask] = []
        self.total_cost: float = 0.0
        self.total_tokens: int = 0

    def add_task(self, task: AITask) -> None:
        """Queue a task for processing."""
        self.tasks.append(task)

    def get_pending(self) -> list[AITask]:
        """Return all pending tasks, ordered by priority."""
        return sorted(
            [t for t in self.tasks if t.status == "pending"],
            key=lambda t: t.priority,
        )

    def route_task(self, task: AITask) -> Provider:
        """Determine the best provider for a task type."""
        routing = {
            TaskType.INSIGHT_EXTRACTION: Provider.ANTHROPIC,
            TaskType.SMART_TAGGING: Provider.ANTHROPIC,
            TaskType.SUMMARIZATION: Provider.ANTHROPIC,
            TaskType.RELATIONSHIP_DETECTION: Provider.ANTHROPIC,
            TaskType.EMBEDDING_GENERATION: Provider.OPENAI,
        }
        return routing.get(task.task_type, Provider.ANTHROPIC)

    def estimate_cost(self, task: AITask) -> float:
        """Estimate the cost of a task in USD."""
        input_tokens = len(json.dumps(task.input_data)) // 4

        cost_per_1k = {
            Provider.ANTHROPIC: 0.003,  # Sonnet input
            Provider.OPENAI: 0.00015,   # GPT-4o-mini input
            Provider.LOCAL: 0.0,
        }

        provider = self.route_task(task)
        return (input_tokens / 1000) * cost_per_1k.get(provider, 0.003)

    def check_budget(self) -> bool:
        """Check if total cost is within budget."""
        return self.total_cost < self.config.cost_limit_usd

    def process_task(self, task: AITask) -> AITask:
        """Process a single task (stub -- actual API calls handled by service layer)."""
        if not self.check_budget():
            task.status = "budget_exceeded"
            log.warning("Budget exceeded ($%.2f / $%.2f)", self.total_cost, self.config.cost_limit_usd)
            return task

        task.provider = self.route_task(task)
        task.status = "processing"
        log.info("Processing task %s (%s) via %s", task.id, task.task_type.value, task.provider.value)

        # Actual processing delegated to service layer
        # This orchestrator handles routing, budgeting, and state management
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc).isoformat()

        estimated = self.estimate_cost(task)
        task.cost_usd = estimated
        self.total_cost += estimated

        return task

    def get_stats(self) -> dict[str, Any]:
        """Return orchestrator statistics."""
        completed = [t for t in self.tasks if t.status == "completed"]
        failed = [t for t in self.tasks if t.status in ("failed", "budget_exceeded")]

        return {
            "total_tasks": len(self.tasks),
            "completed": len(completed),
            "failed": len(failed),
            "pending": len(self.get_pending()),
            "total_cost_usd": round(self.total_cost, 4),
            "budget_remaining_usd": round(self.config.cost_limit_usd - self.total_cost, 4),
            "total_tokens": self.total_tokens,
        }

    def save_state(self, path: Path) -> None:
        """Persist orchestrator state to disk."""
        data = {
            "stats": self.get_stats(),
            "tasks": [
                {
                    "id": t.id,
                    "task_type": t.task_type.value,
                    "provider": t.provider.value,
                    "status": t.status,
                    "cost_usd": t.cost_usd,
                    "created_at": t.created_at,
                    "completed_at": t.completed_at,
                }
                for t in self.tasks
            ],
        }
        path.write_text(json.dumps(data, indent=2))
