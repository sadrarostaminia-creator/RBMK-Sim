"""Random events and failure stubs for the fictional simulator."""

from __future__ import annotations

import random

from reactor_sim.core.state import PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class AnomalyManager:
    """Placeholder anomaly system with lightweight fictional events."""

    def __init__(self) -> None:
        """Initialize the anomaly manager with simple timers."""
        self.pump_degradation = 0.0
        self.rod_lag = 0.0
        self.sensor_drift = 0.0

    def update_step(self, global_state: PlantState) -> None:
        """Apply small fictional anomalies to the global state."""
        roll = random.random()
        if roll < 0.02:
            self.pump_degradation = min(1.0, self.pump_degradation + 0.1)
        if 0.02 <= roll < 0.04:
            self.rod_lag = min(1.0, self.rod_lag + 0.1)
        if 0.04 <= roll < 0.06:
            self.sensor_drift = min(1.0, self.sensor_drift + 0.1)

        cooling = global_state.cooling
        reactor = global_state.reactor
        sensors = global_state.sensors

        cooling.system_health = clamp_percent(cooling.system_health - self.pump_degradation * 0.05)
        reactor.desired_rod_insertion = clamp_percent(
            reactor.desired_rod_insertion + self.rod_lag * 0.1
        )
        sensors.values["drift_bias"] = clamp_percent(self.sensor_drift * 10.0)
