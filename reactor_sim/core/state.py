"""Global plant state definitions for the fictional reactor simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ReactorCoreState:
    """Abstract reactor core state using fictional values and percentages."""

    power: float = 45.0
    temperature: float = 48.0
    reactivity: float = 0.0
    fuel_condition: float = 100.0
    control_rod_insertion: float = 55.0
    desired_rod_insertion: float = 55.0
    desired_power_target: float = 45.0
    thermal_reservoir: float = 50.0
    warnings_active: List[str] = field(default_factory=list)
    stress_index: float = 0.0
    scram_requested: bool = False


@dataclass
class CoolingSystemState:
    """Abstract cooling system state."""

    pump_speed: float = 58.0
    desired_pump_speed: float = 58.0
    flow_rate: float = 50.0
    heat_removal_efficiency: float = 62.0
    coolant_temperature: float = 35.0
    system_health: float = 100.0
    cooling_effect: float = 0.0
    warnings_active: List[str] = field(default_factory=list)


@dataclass
class TurbineSystemState:
    """Abstract steam and turbine state."""

    steam_pressure: float = 35.0
    steam_production_rate: float = 20.0
    steam_loss_rate: float = 6.0
    steam_quality: float = 80.0
    steam_system_health: float = 100.0
    rpm: float = 20.0
    valve_opening: float = 30.0
    desired_valve_opening: float = 30.0
    mechanical_load: float = 20.0
    electrical_resistance: float = 0.0
    turbine_efficiency: float = 78.0
    turbine_health: float = 100.0
    warnings_active: List[str] = field(default_factory=list)


@dataclass
class ElectricalSystemState:
    """Abstract generator and grid state."""

    output_power: float = 15.0
    generator_efficiency: float = 86.0
    generator_temperature: float = 30.0
    generator_health: float = 100.0
    load_target: float = 45.0
    desired_load_target: float = 45.0
    grid_mode: str = "grid_follow"
    grid_demand: float = 50.0
    power_balance: float = 0.0
    grid_stability: float = 92.0
    penalty_level: float = 0.0
    warnings_active: List[str] = field(default_factory=list)


@dataclass
class SafetySystemState:
    """Abstract safety monitor state with alarm progression and history."""

    warnings_active: List[str] = field(default_factory=list)
    trip_flags: Dict[str, bool] = field(default_factory=dict)
    alarm_states: Dict[str, float] = field(default_factory=dict)
    alarm_trends: Dict[str, str] = field(default_factory=dict)
    alarm_severity: Dict[str, str] = field(default_factory=dict)
    alarm_history: List[str] = field(default_factory=list)
    acknowledged_alarms: List[str] = field(default_factory=list)
    muted_advisories: bool = False


@dataclass
class SensorSuiteState:
    """Abstract sensor suite state for noise, drift, delay, and diagnostics."""

    values: Dict[str, float] = field(default_factory=dict)
    noise_levels: Dict[str, float] = field(default_factory=dict)
    drift_rates: Dict[str, float] = field(default_factory=dict)
    delays: Dict[str, float] = field(default_factory=dict)
    true_values: Dict[str, float] = field(default_factory=dict)
    health_bias: Dict[str, float] = field(default_factory=dict)


@dataclass
class ControlSystemState:
    """Control authority state for autopilot status, overrides, and decisions."""

    autopilot_enabled: bool = False
    autopilot_mode: str = "safe_hold"
    autopilot_target_power: float = 45.0
    autopilot_difficulty: str = "normal"
    override_ticks: Dict[str, int] = field(
        default_factory=lambda: {"rods": 0, "pump": 0, "valve": 0, "load": 0}
    )
    decision_log: List[str] = field(default_factory=list)
    tutorial_active: bool = False
    tutorial_stage: str = ""
    tutorial_objective: str = ""


@dataclass
class PlantState:
    """Centralized plant state container for the fictional simulator."""

    reactor: ReactorCoreState = field(default_factory=ReactorCoreState)
    cooling: CoolingSystemState = field(default_factory=CoolingSystemState)
    turbine: TurbineSystemState = field(default_factory=TurbineSystemState)
    electrical: ElectricalSystemState = field(default_factory=ElectricalSystemState)
    safety: SafetySystemState = field(default_factory=SafetySystemState)
    sensors: SensorSuiteState = field(default_factory=SensorSuiteState)
    control: ControlSystemState = field(default_factory=ControlSystemState)
    time: float = 0.0
    tick: float = 0.1
