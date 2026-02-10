"""Fictional autopilot operator that drives plant controls via sensor readings."""

from __future__ import annotations

from reactor_sim.core.state import PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class AutopilotController:
    """Conservative, imperfect operator using delayed/noisy sensor values only."""

    def __init__(self) -> None:
        """Initialize tuning values for each autopilot mode."""
        self.mode_aggressiveness = {
            "safe_hold": 0.4,
            "power_hold": 0.65,
            "load_follow": 0.75,
            "recovery": 0.85,
        }

    def set_enabled(self, state: PlantState, enabled: bool) -> None:
        """Enable or disable autopilot authority."""
        state.control.autopilot_enabled = enabled
        status = "ON" if enabled else "OFF"
        self._log(state, f"autopilot {status}")

    def set_mode(self, state: PlantState, mode: str) -> None:
        """Set requested autopilot mode if valid."""
        if mode in self.mode_aggressiveness:
            state.control.autopilot_mode = mode
            self._log(state, f"mode set to {mode}")

    def update_step(self, state: PlantState) -> None:
        """Read sensors, evaluate risk, and adjust desired controls gradually."""
        if not state.control.autopilot_enabled:
            return

        sensors = state.sensors.values
        alarm_severity = state.safety.alarm_severity
        critical_count = sum(1 for value in alarm_severity.values() if value == "critical")
        warning_count = sum(1 for value in alarm_severity.values() if value == "warning")

        active_mode = state.control.autopilot_mode
        if critical_count > 0 or warning_count >= 2:
            active_mode = "recovery"

        aggression = self.mode_aggressiveness.get(active_mode, 0.5)
        if state.control.autopilot_difficulty == "hard":
            aggression *= 1.1
        elif state.control.autopilot_difficulty == "easy":
            aggression *= 0.9

        core_temp = sensors.get("core_temperature", 50.0)
        core_power = sensors.get("core_power", 45.0)
        grid_demand = sensors.get("grid_demand", 50.0)
        grid_stability = sensors.get("grid_stability", 90.0)

        rod_target = state.reactor.desired_rod_insertion
        pump_target = state.cooling.desired_pump_speed
        valve_target = state.turbine.desired_valve_opening
        load_target = state.electrical.desired_load_target
        reason = "steady"

        if active_mode == "safe_hold":
            state.control.autopilot_target_power = 35.0
            rod_target += (core_power - 35.0) * aggression * 0.6
            pump_target += max(0.0, core_temp - 62.0) * aggression * 0.5
            valve_target += (30.0 - state.turbine.valve_opening) * 0.2
            load_target += (28.0 - state.electrical.load_target) * 0.2
            reason = "maintain low stable operation"
        elif active_mode == "power_hold":
            target = state.control.autopilot_target_power
            rod_target += (core_power - target) * aggression * 0.7
            pump_target += max(0.0, core_temp - 68.0) * aggression * 0.4
            valve_target += (45.0 - state.turbine.valve_opening) * 0.2
            reason = f"hold power near {target:.0f}%"
        elif active_mode == "load_follow":
            target = clamp_percent(grid_demand * 0.92)
            state.control.autopilot_target_power = target
            rod_target += (core_power - target) * aggression * 0.55
            valve_target += (58.0 - state.turbine.valve_opening) * 0.22
            load_target += (grid_demand - state.electrical.load_target) * 0.35
            pump_target += max(0.0, core_temp - 70.0) * aggression * 0.45
            reason = "follow grid demand with conservative offset"
        else:  # recovery
            state.control.autopilot_target_power = 30.0
            rod_target += (core_power - 30.0) * aggression * 0.8
            pump_target += max(0.0, core_temp - 58.0) * aggression * 0.8
            valve_target += (25.0 - state.turbine.valve_opening) * 0.3
            load_target += (18.0 - state.electrical.load_target) * 0.35
            if grid_stability < 55.0:
                load_target += (12.0 - load_target) * 0.5
            reason = "recover from alarm escalation"

        self._apply_if_not_overridden(state, "rods", "reactor", clamp_percent(rod_target))
        self._apply_if_not_overridden(state, "pump", "cooling", clamp_percent(pump_target))
        self._apply_if_not_overridden(state, "valve", "turbine", clamp_percent(valve_target))
        self._apply_if_not_overridden(state, "load", "electrical", clamp_percent(load_target))

        self._log(
            state,
            f"mode={active_mode} targetP={state.control.autopilot_target_power:.1f} reason={reason}",
        )

    def _apply_if_not_overridden(
        self, state: PlantState, control_key: str, domain: str, target_value: float
    ) -> None:
        """Apply target if player has not recently overridden this control path."""
        if state.control.override_ticks.get(control_key, 0) > 0:
            self._log(state, f"{control_key} override active; skipped")
            return

        if domain == "reactor":
            state.reactor.desired_rod_insertion = target_value
        elif domain == "cooling":
            state.cooling.desired_pump_speed = target_value
        elif domain == "turbine":
            state.turbine.desired_valve_opening = target_value
        elif domain == "electrical":
            state.electrical.desired_load_target = target_value

    def _log(self, state: PlantState, message: str) -> None:
        """Append a short autopilot decision message with rolling buffer."""
        entry = f"t={state.time:.1f} {message}"
        state.control.decision_log.append(entry)
        if len(state.control.decision_log) > 40:
            state.control.decision_log.pop(0)
