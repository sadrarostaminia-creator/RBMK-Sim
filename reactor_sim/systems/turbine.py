"""Fictional steam generation and turbine behavior system."""

from __future__ import annotations

from reactor_sim.core.state import PlantState, TurbineSystemState
from reactor_sim.utils.math_helpers import clamp_percent


class TurbineSystem:
    """Converts fictional steam conditions into mechanical turbine RPM."""

    def __init__(self) -> None:
        """Initialize tunable constants for steam and turbine dynamics."""
        self.steam_gain = 0.11
        self.steam_decay = 0.07
        self.quality_recovery = 0.10
        self.quality_penalty = 0.15
        self.rpm_inertia = 0.08
        self.rpm_drag = 0.05
        self.load_drag_factor = 0.01
        self.valve_wear_factor = 0.018
        self.overspeed_wear_factor = 0.02

    def update_step(self, global_state: PlantState) -> None:
        """Advance steam production and turbine RPM one tick."""
        reactor = global_state.reactor
        cooling = global_state.cooling
        turbine = global_state.turbine

        heat_available = max(0.0, reactor.temperature - 40.0)
        extraction_bonus = cooling.cooling_effect * 0.10
        production_target = (heat_available * 0.8 + extraction_bonus) * (turbine.steam_system_health / 100.0)
        turbine.steam_production_rate = clamp_percent(
            turbine.steam_production_rate + (production_target - turbine.steam_production_rate) * self.steam_gain
        )

        valve_flow = turbine.steam_pressure * (turbine.valve_opening / 100.0) * 0.55
        turbine.steam_loss_rate = clamp_percent(
            turbine.steam_loss_rate + (valve_flow - turbine.steam_loss_rate) * self.steam_decay
        )

        pressure_delta = (turbine.steam_production_rate - turbine.steam_loss_rate) * 0.35
        turbine.steam_pressure = clamp_percent(turbine.steam_pressure + pressure_delta)

        quality_drop = max(0.0, turbine.steam_pressure - 78.0) * self.quality_penalty * 0.1
        quality_recovery = (cooling.system_health / 100.0) * self.quality_recovery
        turbine.steam_quality = clamp_percent(turbine.steam_quality + quality_recovery - quality_drop)

        quality_factor = turbine.steam_quality / 100.0
        health_factor = turbine.turbine_health / 100.0
        turbine.turbine_efficiency = clamp_percent(
            (35.0 + quality_factor * 40.0 + health_factor * 25.0)
            - max(0.0, turbine.steam_pressure - 90.0) * 0.6
        )

        torque_input = turbine.steam_loss_rate * (turbine.turbine_efficiency / 100.0)
        desired_rpm = clamp_percent(torque_input * 2.4)
        max_rpm = 40.0 + turbine.turbine_health * 0.60
        if desired_rpm > max_rpm:
            desired_rpm = max_rpm + (desired_rpm - max_rpm) * 0.2

        load_drag = turbine.electrical_resistance * self.load_drag_factor
        turbine.rpm = clamp_percent(
            turbine.rpm + (desired_rpm - turbine.rpm) * self.rpm_inertia - self.rpm_drag - load_drag
        )

        turbine.mechanical_load = clamp_percent(
            turbine.rpm * (0.35 + turbine.valve_opening / 320.0) + turbine.electrical_resistance * 0.4
        )

        wear = 0.0
        if turbine.valve_opening > 85.0:
            wear += (turbine.valve_opening - 85.0) * self.valve_wear_factor
        if turbine.rpm > 88.0:
            wear += (turbine.rpm - 88.0) * self.overspeed_wear_factor
        if turbine.steam_quality < 45.0:
            wear += (45.0 - turbine.steam_quality) * 0.01

        turbine.turbine_health = clamp_percent(turbine.turbine_health - wear)
        turbine.steam_system_health = clamp_percent(turbine.steam_system_health - wear * 0.6)

        self._update_warnings(turbine)

    def _update_warnings(self, turbine: TurbineSystemState) -> None:
        """Populate turbine warnings for safety aggregation and UI display."""
        turbine.warnings_active.clear()
        if turbine.steam_pressure >= 85.0:
            turbine.warnings_active.append("Steam pressure high")
        if turbine.rpm >= 90.0:
            turbine.warnings_active.append("Turbine overspeed risk")
        if turbine.turbine_efficiency <= 50.0:
            turbine.warnings_active.append("Efficiency loss detected")
        if turbine.turbine_health <= 50.0:
            turbine.warnings_active.append("Turbine health degraded")
