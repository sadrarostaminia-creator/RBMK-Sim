"""Fictional generator and grid pressure system."""

from __future__ import annotations

import math

from reactor_sim.core.state import ElectricalSystemState, PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class GeneratorSystem:
    """Converts turbine RPM into abstract electrical output with grid feedback."""

    def __init__(self) -> None:
        """Initialize tunable constants for generator and grid behavior."""
        self.output_inertia = 0.12
        self.temperature_rise = 0.08
        self.temperature_cool = 0.06
        self.health_wear_factor = 0.02
        self.load_wear_factor = 0.015
        self.phase = 0.0

    def update_step(self, global_state: PlantState) -> None:
        """Advance generator output, grid pressure, and turbine feedback."""
        electrical = global_state.electrical
        turbine = global_state.turbine

        self.phase = (self.phase + 0.05) % (2 * math.pi)
        base_demand = 50.0 + math.sin(self.phase) * 8.0
        mode_shift = -12.0 if electrical.grid_mode == "islanded" else 0.0
        if electrical.grid_mode == "load_shed":
            mode_shift -= 20.0
        electrical.grid_demand = clamp_percent(base_demand + mode_shift)

        max_output = clamp_percent(30.0 + electrical.generator_health * 0.7)
        rpm_factor = turbine.rpm / 100.0
        efficiency_factor = electrical.generator_efficiency / 100.0
        load_factor = electrical.load_target / 100.0

        desired_output = max_output * rpm_factor * efficiency_factor * (0.35 + load_factor)
        electrical.output_power = clamp_percent(
            electrical.output_power + (desired_output - electrical.output_power) * self.output_inertia
        )

        electrical.power_balance = electrical.output_power - electrical.grid_demand

        resistance = clamp_percent(electrical.load_target * 0.5 + max(0.0, electrical.grid_demand - electrical.output_power) * 0.3)
        turbine.electrical_resistance = resistance
        turbine.mechanical_load = clamp_percent(turbine.mechanical_load + resistance * 0.25)

        electrical.generator_temperature = clamp_percent(
            electrical.generator_temperature
            + electrical.output_power * self.temperature_rise * (0.3 + load_factor)
            - self.temperature_cool * (50.0 - min(50.0, turbine.rpm))
        )

        temp_penalty = max(0.0, electrical.generator_temperature - 72.0) * 0.35
        health_penalty = max(0.0, 65.0 - electrical.generator_health) * 0.1
        electrical.generator_efficiency = clamp_percent(
            92.0 - temp_penalty - health_penalty - max(0.0, electrical.load_target - 85.0) * 0.2
        )

        instability_hit = 0.0
        if electrical.power_balance < -8.0:
            instability_hit += abs(electrical.power_balance) * 0.05
        elif electrical.power_balance > 15.0:
            instability_hit += (electrical.power_balance - 15.0) * 0.02

        electrical.grid_stability = clamp_percent(electrical.grid_stability - instability_hit + 0.3)
        electrical.penalty_level = clamp_percent(
            electrical.penalty_level
            + max(0.0, 65.0 - electrical.grid_stability) * 0.04
            + max(0.0, -electrical.power_balance - 5.0) * 0.03
            - 0.2
        )

        wear = 0.0
        if electrical.load_target > 85.0:
            wear += (electrical.load_target - 85.0) * self.load_wear_factor
        if electrical.generator_temperature > 82.0:
            wear += (electrical.generator_temperature - 82.0) * self.health_wear_factor
        electrical.generator_health = clamp_percent(electrical.generator_health - wear)

        self._update_warnings(electrical)

    def _update_warnings(self, electrical: ElectricalSystemState) -> None:
        """Populate generator/grid warning indicators for safety aggregation."""
        electrical.warnings_active.clear()
        if electrical.generator_temperature >= 84.0:
            electrical.warnings_active.append("Generator overheating")
        if electrical.grid_stability <= 60.0:
            electrical.warnings_active.append("Grid instability rising")
        if electrical.load_target >= 88.0:
            electrical.warnings_active.append("Load exceeds safe margin")
        if electrical.generator_efficiency <= 58.0:
            electrical.warnings_active.append("Generator efficiency loss")
