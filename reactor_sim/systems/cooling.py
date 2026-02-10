"""Fictional cooling subsystem with thermal lag, strain, and degradation."""

from __future__ import annotations

from reactor_sim.core.state import CoolingSystemState, PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class CoolingSystem:
    """Cooling system that removes heat with abstract delayed behavior."""

    def __init__(self) -> None:
        """Initialize tunable coefficients for fictional cooling behavior."""
        self.flow_response = 0.12
        self.coolant_heat_gain = 0.06
        self.coolant_cooldown = 0.08
        self.base_efficiency = 0.20
        self.pump_efficiency = 0.75
        self.health_efficiency = 0.65
        self.hot_coolant_penalty = 0.55
        self.demand_response = 0.10
        self.strain_damage = 0.05
        self.idle_recovery = 0.01

    def update_step(self, global_state: PlantState) -> None:
        """Update cooling state and compute per-tick cooling effect."""
        cooling = global_state.cooling
        reactor = global_state.reactor

        pump_factor = cooling.pump_speed / 100.0
        health_factor = cooling.system_health / 100.0

        desired_flow = cooling.pump_speed * 0.9
        cooling.flow_rate = clamp_percent(
            cooling.flow_rate + (desired_flow - cooling.flow_rate) * self.flow_response
        )

        heat_load = max(0.0, reactor.temperature - 35.0)
        cooling.coolant_temperature = clamp_percent(
            cooling.coolant_temperature
            + heat_load * self.coolant_heat_gain * (0.25 + pump_factor)
            - cooling.pump_speed * self.coolant_cooldown * 0.1
        )

        hot_penalty = max(0.0, cooling.coolant_temperature - 70.0) * self.hot_coolant_penalty
        demand_bonus = max(0.0, reactor.temperature - 55.0) * self.demand_response
        raw_efficiency = (
            self.base_efficiency * 100.0
            + cooling.flow_rate * self.pump_efficiency
            + cooling.system_health * self.health_efficiency
            + demand_bonus
            - hot_penalty
        )
        cooling.heat_removal_efficiency = clamp_percent(raw_efficiency / 2.2)

        diminishing = 1.0 - min(0.65, cooling.heat_removal_efficiency / 140.0)
        cooling.cooling_effect = max(0.0, cooling.heat_removal_efficiency * (0.2 + diminishing))

        if cooling.pump_speed > 85.0:
            strain = (cooling.pump_speed - 85.0) / 15.0
            cooling.system_health = clamp_percent(cooling.system_health - strain * self.strain_damage)
        elif cooling.pump_speed < 55.0:
            cooling.system_health = clamp_percent(cooling.system_health + self.idle_recovery)

        self._update_warnings(cooling)

    def _update_warnings(self, cooling: CoolingSystemState) -> None:
        """Populate cooling warning indicators for future safety handling."""
        cooling.warnings_active.clear()
        if cooling.heat_removal_efficiency <= 40.0:
            cooling.warnings_active.append("Cooling efficiency reduced")
        if cooling.pump_speed >= 88.0:
            cooling.warnings_active.append("Pump strain detected")
        if cooling.coolant_temperature >= 75.0:
            cooling.warnings_active.append("Coolant temperature elevated")
        if cooling.system_health <= 45.0:
            cooling.warnings_active.append("Cooling system health degraded")
