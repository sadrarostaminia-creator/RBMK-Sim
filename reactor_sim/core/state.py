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
    turbine_efficiency: float = 78.0
    turbine_health: float = 100.0
    warnings_active: List[str] = field(default_factory=list)


@dataclass
class ElectricalSystemState:
    """Abstract electrical system state."""

    output_power: float = 40.0
    grid_load: float = 50.0
    efficiency: float = 70.0


@dataclass
class SafetySystemState:
    """Abstract safety system state with warnings and trip flags."""

    warnings_active: List[str] = field(default_factory=list)
    trip_flags: Dict[str, bool] = field(default_factory=dict)


@dataclass
class SensorSuiteState:
    """Abstract sensor suite state for noise, drift, and delay."""

    values: Dict[str, float] = field(default_factory=dict)
    noise_levels: Dict[str, float] = field(default_factory=dict)
    drift_rates: Dict[str, float] = field(default_factory=dict)
    delays: Dict[str, float] = field(default_factory=dict)


@dataclass
class PlantState:
    """Centralized plant state container for the fictional simulator."""

    reactor: ReactorCoreState = field(default_factory=ReactorCoreState)
    cooling: CoolingSystemState = field(default_factory=CoolingSystemState)
    turbine: TurbineSystemState = field(default_factory=TurbineSystemState)
    electrical: ElectricalSystemState = field(default_factory=ElectricalSystemState)
    safety: SafetySystemState = field(default_factory=SafetySystemState)
    sensors: SensorSuiteState = field(default_factory=SensorSuiteState)
    time: float = 0.0
    tick: float = 0.1
