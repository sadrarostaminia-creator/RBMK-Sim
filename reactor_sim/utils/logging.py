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
    """In-memory log for snapshots and alarm/autopilot/advisor timeline events."""

    entries: List[LogEntry] = field(default_factory=list)
    _alarm_cursor: int = 0
    _autopilot_cursor: int = 0
    _advisor_cursor: int = 0

    def capture_snapshot(self, state: PlantState) -> None:
        """Record plant snapshot plus newly appended timeline events."""
        message = (
            "Snapshot"
            f" rpm={state.turbine.rpm:.1f}"
            f" out={state.electrical.output_power:.1f}%"
            f" grid_stb={state.electrical.grid_stability:.1f}%"
            f" alarms={len(state.safety.warnings_active)}"
            f" ap_mode={state.control.autopilot_mode}"
            f" adv_mode={state.advisor.mode}"
        )
        self.entries.append(LogEntry(timestamp=state.time, message=message))

        while self._alarm_cursor < len(state.safety.alarm_history):
            self.entries.append(
                LogEntry(
                    timestamp=state.time,
                    message=f"AlarmEvent {state.safety.alarm_history[self._alarm_cursor]}",
                )
            )
            self._alarm_cursor += 1

        while self._autopilot_cursor < len(state.control.decision_log):
            self.entries.append(
                LogEntry(
                    timestamp=state.time,
                    message=f"Autopilot {state.control.decision_log[self._autopilot_cursor]}",
                )
            )
            self._autopilot_cursor += 1

        while self._advisor_cursor < len(state.advisor.history):
            item = state.advisor.history[self._advisor_cursor]
            self.entries.append(
                LogEntry(
                    timestamp=item.timestamp,
                    message=f"Advisor {item.level}/{item.category}: {item.text}",
                )
            )
            self._advisor_cursor += 1
