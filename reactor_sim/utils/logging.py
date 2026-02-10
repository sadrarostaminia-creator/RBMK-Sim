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
            f" power={state.reactor.power:.1f}%"
            f" rods={state.reactor.control_rod_insertion:.1f}%"
            f" temp={state.reactor.temperature:.1f}"
            f" fuel={state.reactor.fuel_condition:.1f}%"
            f" pump={state.cooling.pump_speed:.1f}%"
            f" cool_eff={state.cooling.heat_removal_efficiency:.1f}%"
        )
        self.entries.append(LogEntry(timestamp=state.time, message=message))
