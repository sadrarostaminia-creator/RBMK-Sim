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
    """In-memory log for snapshots and alarm timeline events."""

    entries: List[LogEntry] = field(default_factory=list)
    _alarm_cursor: int = 0

    def capture_snapshot(self, state: PlantState) -> None:
        """Record plant snapshot plus newly appended alarm history entries."""
        message = (
            "Snapshot"
            f" rpm={state.turbine.rpm:.1f}"
            f" out={state.electrical.output_power:.1f}%"
            f" grid_stb={state.electrical.grid_stability:.1f}%"
            f" alarms={len(state.safety.warnings_active)}"
        )
        self.entries.append(LogEntry(timestamp=state.time, message=message))

        history = state.safety.alarm_history
        while self._alarm_cursor < len(history):
            self.entries.append(
                LogEntry(timestamp=state.time, message=f"AlarmEvent {history[self._alarm_cursor]}")
            )
            self._alarm_cursor += 1
