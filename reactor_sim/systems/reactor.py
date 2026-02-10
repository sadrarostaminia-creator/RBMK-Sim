"""Fictional reactor core logic with smooth, tunable, abstract behavior."""

from __future__ import annotations

from reactor_sim.core.state import PlantState, ReactorCoreState
from reactor_sim.utils.math_helpers import clamp_percent


class ReactorSystem:
    """Reactor system that evolves power, heat, and fuel using game logic."""

    def __init__(self) -> None:
        """Initialize tunable coefficients for fictional reactor behavior."""
        self.reactivity_gain = 0.06
        self.reactivity_damping = 0.10
        self.power_inertia = 0.16
        self.base_power_floor = 5.0
        self.thermal_gain = 0.10
        self.thermal_release = 0.05
        self.cooling_influence = 0.08
        self.fuel_wear_base = 0.004
        self.fuel_wear_stress = 0.010

    def update_step(self, global_state: PlantState) -> None:
        """Advance fictional reactor dynamics one simulation tick."""
        reactor = global_state.reactor
        cooling = global_state.cooling

        if reactor.scram_requested:
            reactor.desired_rod_insertion = 100.0

        rod_withdrawal = (50.0 - reactor.control_rod_insertion) / 50.0
        target_reactivity = rod_withdrawal * 6.0 + (reactor.desired_power_target - reactor.power) * 0.02
        reactivity_delta = (target_reactivity - reactor.reactivity) * self.reactivity_gain
        damping = reactor.reactivity * self.reactivity_damping
        reactor.reactivity = max(-10.0, min(10.0, reactor.reactivity + reactivity_delta - damping))

        fuel_cap = 35.0 + (reactor.fuel_condition * 0.65)
        soft_max = min(100.0, fuel_cap)
        power_target = clamp_percent(self.base_power_floor + (reactor.reactivity + 10.0) * 4.6)
        if power_target > soft_max:
            overflow = power_target - soft_max
            power_target = soft_max + overflow * 0.25

        reactor.power = clamp_percent(
            reactor.power + (power_target - reactor.power) * self.power_inertia
        )

        cooling_factor = cooling.heat_removal_efficiency * self.cooling_influence
        heat_input = reactor.power * self.thermal_gain
        reactor.thermal_reservoir = clamp_percent(
            reactor.thermal_reservoir + heat_input - cooling_factor - self.thermal_release
        )
        reactor.temperature = clamp_percent(
            reactor.temperature + (reactor.thermal_reservoir - reactor.temperature) * 0.12
        )

        stress = clamp_percent(
            max(0.0, reactor.temperature - 78.0)
            + max(0.0, abs(reactor.reactivity) - 7.0) * 5.0
            + max(0.0, reactor.power - soft_max) * 0.6
        )
        reactor.stress_index = stress

        wear_rate = self.fuel_wear_base + (reactor.power / 100.0) * 0.02
        wear_rate += (reactor.temperature / 100.0) * 0.01
        wear_rate += (reactor.stress_index / 100.0) * self.fuel_wear_stress
        reactor.fuel_condition = clamp_percent(reactor.fuel_condition - wear_rate)

        self._update_warnings(reactor)

    def _update_warnings(self, reactor_state: ReactorCoreState) -> None:
        """Populate internal reactor warnings for display and future safety hooks."""
        reactor_state.warnings_active.clear()
        if reactor_state.temperature >= 82.0:
            reactor_state.warnings_active.append("Reactor heat stress")
        if abs(reactor_state.reactivity) >= 8.0:
            reactor_state.warnings_active.append("Reactivity instability")
        if reactor_state.fuel_condition <= 35.0:
            reactor_state.warnings_active.append("Fuel condition degraded")
