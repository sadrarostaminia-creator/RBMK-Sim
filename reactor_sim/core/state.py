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

    pump_flow: float = 60.0
    heat_removal_efficiency: float = 65.0


@dataclass
class TurbineSystemState:
    """Abstract turbine system state."""

    rpm: float = 40.0
    valve_opening: float = 50.0
    steam_pressure: float = 45.0


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
