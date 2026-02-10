"""Random fictional failures and anomalies for game pressure and storytelling."""

from __future__ import annotations

import random

from reactor_sim.core.state import PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class AnomalyManager:
    """Injects gradual, recoverable fictional failures into plant systems."""

    def __init__(self) -> None:
        """Initialize anomaly strengths and active failure durations."""
        self.pump_degradation = 0.0
        self.rod_lag = 0.0
        self.sensor_drift = 0.0
        self.failures: dict[str, int] = {}

    def update_step(self, global_state: PlantState) -> None:
        """Apply baseline anomalies and trigger occasional named failures."""
        roll = random.random()
        if roll < 0.02:
            self.pump_degradation = min(1.0, self.pump_degradation + 0.1)
        if 0.02 <= roll < 0.04:
            self.rod_lag = min(1.0, self.rod_lag + 0.1)
        if 0.04 <= roll < 0.06:
            self.sensor_drift = min(1.0, self.sensor_drift + 0.1)

        # transient failure triggers
        failure_roll = random.random()
        if failure_roll < 0.01 and "Pump Cavitation" not in self.failures:
            self.failures["Pump Cavitation"] = 45
            self._record_failure(global_state, "Pump Cavitation started")
        elif 0.01 <= failure_roll < 0.02 and "Valve Stiction" not in self.failures:
            self.failures["Valve Stiction"] = 35
            self._record_failure(global_state, "Valve Stiction started")
        elif 0.02 <= failure_roll < 0.03 and "Sensor Ghost Drift" not in self.failures:
            self.failures["Sensor Ghost Drift"] = 55
            self._record_failure(global_state, "Sensor Ghost Drift started")
        elif 0.03 <= failure_roll < 0.04 and "Generator Hotspot" not in self.failures:
            self.failures["Generator Hotspot"] = 40
            self._record_failure(global_state, "Generator Hotspot started")

        cooling = global_state.cooling
        reactor = global_state.reactor
        sensors = global_state.sensors
        turbine = global_state.turbine
        electrical = global_state.electrical

        # baseline soft drift
        cooling.system_health = clamp_percent(cooling.system_health - self.pump_degradation * 0.05)
        reactor.desired_rod_insertion = clamp_percent(
            reactor.desired_rod_insertion + self.rod_lag * 0.1
        )
        sensors.values["drift_bias"] = clamp_percent(self.sensor_drift * 10.0)

        # apply active failures and decay durations
        ended: list[str] = []
        for name, ticks_left in list(self.failures.items()):
            if name == "Pump Cavitation":
                cooling.desired_pump_speed = clamp_percent(cooling.desired_pump_speed - 0.8)
                cooling.heat_removal_efficiency = clamp_percent(cooling.heat_removal_efficiency - 0.6)
            elif name == "Valve Stiction":
                turbine.desired_valve_opening = clamp_percent(turbine.desired_valve_opening * 0.992)
            elif name == "Sensor Ghost Drift":
                self.sensor_drift = min(1.0, self.sensor_drift + 0.02)
                sensors.health_bias["core_temperature"] = sensors.health_bias.get("core_temperature", 0.0) + 0.4
            elif name == "Generator Hotspot":
                electrical.generator_temperature = clamp_percent(electrical.generator_temperature + 0.9)
                electrical.generator_efficiency = clamp_percent(electrical.generator_efficiency - 0.4)

            self.failures[name] = ticks_left - 1
            if self.failures[name] <= 0:
                ended.append(name)

        for name in ended:
            del self.failures[name]
            self._record_failure(global_state, f"{name} ended")

        global_state.safety.active_failures = sorted(self.failures.keys())

    def _record_failure(self, state: PlantState, text: str) -> None:
        """Append failure lifecycle entries to shared history buffers."""
        entry = f"t={state.time:.1f} {text}"
        state.safety.failure_history.append(entry)
        if len(state.safety.failure_history) > 80:
            state.safety.failure_history.pop(0)
