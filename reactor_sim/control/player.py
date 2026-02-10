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
    ) -> None:
        """Initialize manual control limits and defaults."""
        self.rod_step = max(0.1, rod_step)
        self.rod_rate_limit = max(0.1, rod_rate_limit)
        self.pump_step = max(0.1, pump_step)
        self.pump_rate_limit = max(0.1, pump_rate_limit)

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

    def _set_desired_rod(self, state: PlantState, desired: float) -> None:
        """Validate and clamp desired rod insertion request."""
        state.reactor.desired_rod_insertion = clamp_percent(desired)

    def _set_desired_pump(self, state: PlantState, desired: float) -> None:
        """Validate and clamp desired pump speed request."""
        state.cooling.desired_pump_speed = clamp_percent(desired)

    # TODO: expose this controller to autopilot command arbitration.
    # TODO: add AI advisor suggestions mapped to these control actions.
