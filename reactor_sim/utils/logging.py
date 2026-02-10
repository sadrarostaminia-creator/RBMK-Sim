"""Event and state logging placeholders for the fictional simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from reactor_sim.core.state import PlantState


@dataclass
class LogEntry:
    """Lightweight log entry for state snapshots."""

    timestamp: float
    message: str


@dataclass
class EventLog:
    """Placeholder event logger with in-memory storage."""

    entries: List[LogEntry] = field(default_factory=list)

    def capture_snapshot(self, state: PlantState) -> None:
        """Record a minimal snapshot for debugging and future UI use."""
        message = (
            "Snapshot"
            f" rpm={state.turbine.rpm:.1f}"
            f" out={state.electrical.output_power:.1f}%"
            f" gen_eff={state.electrical.generator_efficiency:.1f}%"
            f" demand={state.electrical.grid_demand:.1f}%"
            f" stability={state.electrical.grid_stability:.1f}%"
        )
        self.entries.append(LogEntry(timestamp=state.time, message=message))
