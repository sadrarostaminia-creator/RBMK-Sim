"""Monitoring-only alarm and safety awareness system for fictional gameplay."""

from __future__ import annotations

from reactor_sim.core.state import PlantState


class SafetySystem:
    """Evaluates sensor readings, escalates alarms, and tracks alarm trends."""

    def __init__(self) -> None:
        """Initialize fictional sensor thresholds and escalation rates."""
        self.thresholds = {
            "Core temperature trending high": (74.0, 84.0, 92.0, "core_temperature"),
            "Steam pressure instability detected": (78.0, 88.0, 96.0, "steam_pressure"),
            "Generator overheating warning": (72.0, 82.0, 90.0, "generator_temperature"),
            "Grid instability increasing": (65.0, 55.0, 45.0, "grid_stability"),
        }
        self.history_limit = 50

    def update_step(self, global_state: PlantState) -> None:
        """Update alarm scores and severities using sensor-only information."""
        safety = global_state.safety
        sensors = global_state.sensors

        safety.warnings_active.clear()
        safety.trip_flags.setdefault("manual_trip", False)

        for alarm_name, rule in self.thresholds.items():
            advisory, warning, critical, sensor_name = rule
            reading = sensors.values.get(sensor_name, sensors.true_values.get(sensor_name, 0.0))
            prev_score = safety.alarm_states.get(alarm_name, 0.0)

            score_delta = self._score_delta(sensor_name, reading, advisory, warning, critical)
            new_score = max(0.0, min(100.0, prev_score + score_delta))
            safety.alarm_states[alarm_name] = new_score

            trend = "rising" if score_delta > 0.2 else "falling" if score_delta < -0.2 else "stable"
            safety.alarm_trends[alarm_name] = trend
            severity = self._severity_from_score(new_score)
            safety.alarm_severity[alarm_name] = severity

            if severity != "none":
                message = f"{severity.upper()}: {alarm_name} ({trend})"
                if not (safety.muted_advisories and severity == "advisory"):
                    safety.warnings_active.append(message)

            if self._crossed_boundary(prev_score, new_score):
                self._append_history(
                    safety,
                    f"t={global_state.time:.1f} {alarm_name} -> {severity} ({trend})"
                )

        # retain compatibility by appending subsystem direct warnings as advisory notes
        for subsystem_warning in (
            global_state.reactor.warnings_active
            + global_state.cooling.warnings_active
            + global_state.turbine.warnings_active
            + global_state.electrical.warnings_active
        ):
            safety.warnings_active.append(f"ADVISORY: {subsystem_warning} (stable)")

    def acknowledge_alarm(self, global_state: PlantState, alarm_name: str) -> None:
        """Record player acknowledgement; does not change the underlying condition."""
        safety = global_state.safety
        if alarm_name not in safety.acknowledged_alarms:
            safety.acknowledged_alarms.append(alarm_name)
            self._append_history(safety, f"t={global_state.time:.1f} acknowledged: {alarm_name}")

    def set_mute_advisories(self, global_state: PlantState, muted: bool) -> None:
        """Enable/disable muting of advisory-level alarm messages."""
        global_state.safety.muted_advisories = muted

    def _score_delta(
        self,
        sensor_name: str,
        reading: float,
        advisory: float,
        warning: float,
        critical: float,
    ) -> float:
        """Compute alarm score delta with gradual escalation/de-escalation."""
        if sensor_name == "grid_stability":
            if reading <= critical:
                return 3.0
            if reading <= warning:
                return 1.8
            if reading <= advisory:
                return 0.9
            return -0.8

        if reading >= critical:
            return 3.0
        if reading >= warning:
            return 1.8
        if reading >= advisory:
            return 0.9
        return -0.8

    def _severity_from_score(self, score: float) -> str:
        """Map alarm score to user-facing severity labels."""
        if score >= 70.0:
            return "critical"
        if score >= 35.0:
            return "warning"
        if score >= 10.0:
            return "advisory"
        return "none"

    def _crossed_boundary(self, previous: float, current: float) -> bool:
        """Detect boundary crossings for logging state changes only."""
        boundaries = (10.0, 35.0, 70.0)
        for boundary in boundaries:
            if (previous < boundary <= current) or (previous >= boundary > current):
                return True
        return False

    def _append_history(self, safety_state, event: str) -> None:
        """Append an event to rolling alarm history."""
        safety_state.alarm_history.append(event)
        if len(safety_state.alarm_history) > self.history_limit:
            safety_state.alarm_history.pop(0)
