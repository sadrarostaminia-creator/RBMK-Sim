"""Manual control hooks for fictional player-driven reactor controls."""

from __future__ import annotations

from reactor_sim.core.state import PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class PlayerController:
    """Applies validated manual control intents to the global plant state."""

    def __init__(
        self,
        rod_step: float = 2.0,
        rod_rate_limit: float = 3.0,
        pump_step: float = 4.0,
        pump_rate_limit: float = 4.0,
        valve_step: float = 4.0,
        valve_rate_limit: float = 4.0,
        load_step: float = 5.0,
        load_rate_limit: float = 4.0,
    ) -> None:
        """Initialize manual control limits and defaults."""
        self.rod_step = max(0.1, rod_step)
        self.rod_rate_limit = max(0.1, rod_rate_limit)
        self.pump_step = max(0.1, pump_step)
        self.pump_rate_limit = max(0.1, pump_rate_limit)
        self.valve_step = max(0.1, valve_step)
        self.valve_rate_limit = max(0.1, valve_rate_limit)
        self.load_step = max(0.1, load_step)
        self.load_rate_limit = max(0.1, load_rate_limit)

    def set_autopilot_enabled(self, state: PlantState, enabled: bool) -> None:
        """Enable or disable autopilot instantly."""
        state.control.autopilot_enabled = enabled
        status = "ON" if enabled else "OFF"
        state.control.decision_log.append(f"t={state.time:.1f} player set autopilot {status}")

    def set_autopilot_mode(self, state: PlantState, mode: str) -> None:
        """Set autopilot mode for subsequent autonomous decisions."""
        state.control.autopilot_mode = mode
        state.control.decision_log.append(f"t={state.time:.1f} player mode={mode}")

    def raise_rods(self, state: PlantState, steps: int = 1) -> None:
        """Withdraw rods in small increments to increase potential reactivity."""
        delta = self.rod_step * max(1, steps)
        self._set_desired_rod(state, state.reactor.desired_rod_insertion - delta)

    def lower_rods(self, state: PlantState, steps: int = 1) -> None:
        """Insert rods in small increments to reduce potential reactivity."""
        delta = self.rod_step * max(1, steps)
        self._set_desired_rod(state, state.reactor.desired_rod_insertion + delta)

    def set_power_target(self, state: PlantState, power_percent: float) -> None:
        """Set a desired abstract power target used by reactor balancing logic."""
        state.reactor.desired_power_target = clamp_percent(power_percent)

    def emergency_insert(self, state: PlantState) -> None:
        """Request a fictional SCRAM-style full insertion command."""
        state.reactor.scram_requested = True
        state.reactor.desired_rod_insertion = 100.0
        self._flag_override(state, "rods")

    def increase_pump_speed(self, state: PlantState, steps: int = 1) -> None:
        """Increase desired pump speed in small player-adjustable increments."""
        delta = self.pump_step * max(1, steps)
        self._set_desired_pump(state, state.cooling.desired_pump_speed + delta)

    def decrease_pump_speed(self, state: PlantState, steps: int = 1) -> None:
        """Decrease desired pump speed in small player-adjustable increments."""
        delta = self.pump_step * max(1, steps)
        self._set_desired_pump(state, state.cooling.desired_pump_speed - delta)

    def set_pump_mode_low(self, state: PlantState) -> None:
        """Apply a fictional low cooling preset."""
        self._set_desired_pump(state, 35.0)

    def set_pump_mode_normal(self, state: PlantState) -> None:
        """Apply a fictional normal cooling preset."""
        self._set_desired_pump(state, 58.0)

    def set_pump_mode_high(self, state: PlantState) -> None:
        """Apply a fictional high cooling preset."""
        self._set_desired_pump(state, 82.0)

    def increase_valve_opening(self, state: PlantState, steps: int = 1) -> None:
        """Increase turbine valve opening in small increments."""
        delta = self.valve_step * max(1, steps)
        self._set_desired_valve(state, state.turbine.desired_valve_opening + delta)

    def decrease_valve_opening(self, state: PlantState, steps: int = 1) -> None:
        """Decrease turbine valve opening in small increments."""
        delta = self.valve_step * max(1, steps)
        self._set_desired_valve(state, state.turbine.desired_valve_opening - delta)

    def set_valve_mode_idle(self, state: PlantState) -> None:
        """Apply fictional idle valve preset."""
        self._set_desired_valve(state, 20.0)

    def set_valve_mode_cruise(self, state: PlantState) -> None:
        """Apply fictional cruise valve preset."""
        self._set_desired_valve(state, 50.0)

    def set_valve_mode_high_load(self, state: PlantState) -> None:
        """Apply fictional high-load valve preset."""
        self._set_desired_valve(state, 80.0)

    def increase_load_target(self, state: PlantState, steps: int = 1) -> None:
        """Increase electrical load target in small increments."""
        delta = self.load_step * max(1, steps)
        self._set_desired_load(state, state.electrical.desired_load_target + delta)

    def decrease_load_target(self, state: PlantState, steps: int = 1) -> None:
        """Decrease electrical load target in small increments."""
        delta = self.load_step * max(1, steps)
        self._set_desired_load(state, state.electrical.desired_load_target - delta)

    def set_mode_islanded(self, state: PlantState) -> None:
        """Set generator to isolated mode with lower target demand."""
        state.electrical.grid_mode = "islanded"
        self._set_desired_load(state, 30.0)

    def set_mode_grid_follow(self, state: PlantState) -> None:
        """Set generator to grid-follow mode."""
        state.electrical.grid_mode = "grid_follow"

    def emergency_load_shed(self, state: PlantState) -> None:
        """Trigger immediate fictional load shedding target."""
        state.electrical.grid_mode = "load_shed"
        self._set_desired_load(state, 10.0)

    def acknowledge_alarm(self, state: PlantState, alarm_name: str) -> None:
        """Acknowledge an alarm without resolving its root condition."""
        if alarm_name not in state.safety.acknowledged_alarms:
            state.safety.acknowledged_alarms.append(alarm_name)
            state.safety.alarm_history.append(f"t={state.time:.1f} acknowledged: {alarm_name}")
            if len(state.safety.alarm_history) > 50:
                state.safety.alarm_history.pop(0)

    def set_advisory_mute(self, state: PlantState, muted: bool) -> None:
        """Mute or unmute advisory-level alarm repetition."""
        state.safety.muted_advisories = bool(muted)
        state.safety.alarm_history.append(
            f"t={state.time:.1f} advisory mute {'on' if muted else 'off'}"
        )
        if len(state.safety.alarm_history) > 50:
            state.safety.alarm_history.pop(0)

    def recent_alarm_history(self, state: PlantState, limit: int = 8) -> list[str]:
        """Return recent alarm history entries for UI/console display."""
        return state.safety.alarm_history[-max(1, limit):]

    def apply_step(self, state: PlantState) -> None:
        """Rate-limit motion so controls affect systems indirectly and smoothly."""
        reactor = state.reactor
        rod_delta = reactor.desired_rod_insertion - reactor.control_rod_insertion
        limited_rod_delta = max(-self.rod_rate_limit, min(self.rod_rate_limit, rod_delta))
        reactor.control_rod_insertion = clamp_percent(reactor.control_rod_insertion + limited_rod_delta)
        if reactor.scram_requested and reactor.control_rod_insertion >= 99.9:
            reactor.scram_requested = False

        cooling = state.cooling
        pump_delta = cooling.desired_pump_speed - cooling.pump_speed
        limited_pump_delta = max(-self.pump_rate_limit, min(self.pump_rate_limit, pump_delta))
        cooling.pump_speed = clamp_percent(cooling.pump_speed + limited_pump_delta)

        turbine = state.turbine
        valve_delta = turbine.desired_valve_opening - turbine.valve_opening
        limited_valve_delta = max(-self.valve_rate_limit, min(self.valve_rate_limit, valve_delta))
        turbine.valve_opening = clamp_percent(turbine.valve_opening + limited_valve_delta)

        electrical = state.electrical
        load_delta = electrical.desired_load_target - electrical.load_target
        limited_load_delta = max(-self.load_rate_limit, min(self.load_rate_limit, load_delta))
        electrical.load_target = clamp_percent(electrical.load_target + limited_load_delta)

        self._decay_overrides(state)

    def _set_desired_rod(self, state: PlantState, desired: float) -> None:
        """Validate and clamp desired rod insertion request."""
        state.reactor.desired_rod_insertion = clamp_percent(desired)
        self._flag_override(state, "rods")

    def _set_desired_pump(self, state: PlantState, desired: float) -> None:
        """Validate and clamp desired pump speed request."""
        state.cooling.desired_pump_speed = clamp_percent(desired)
        self._flag_override(state, "pump")

    def _set_desired_valve(self, state: PlantState, desired: float) -> None:
        """Validate and clamp desired valve opening request."""
        state.turbine.desired_valve_opening = clamp_percent(desired)
        self._flag_override(state, "valve")

    def _set_desired_load(self, state: PlantState, desired: float) -> None:
        """Validate and clamp desired electrical load request."""
        state.electrical.desired_load_target = clamp_percent(desired)
        self._flag_override(state, "load")

    def _flag_override(self, state: PlantState, control_key: str, ticks: int = 8) -> None:
        """Mark a control path as player-overridden for a short time window."""
        state.control.override_ticks[control_key] = max(state.control.override_ticks.get(control_key, 0), ticks)

    def _decay_overrides(self, state: PlantState) -> None:
        """Decay override timers each tick."""
        for key, value in state.control.override_ticks.items():
            state.control.override_ticks[key] = max(0, value - 1)

    # TODO: expose this controller to autopilot command arbitration.
    # TODO: add AI advisor suggestions mapped to these control actions.
