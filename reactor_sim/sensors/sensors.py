"""Sensor abstraction with fictional lag, noise, drift, and stress sensitivity."""

from __future__ import annotations

import math
from collections import defaultdict, deque
from typing import Deque, Dict

from reactor_sim.core.state import PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class SensorSuite:
    """Maintains imperfect sensor channels for all major plant domains."""

    def __init__(self) -> None:
        """Initialize sensor dynamics and per-channel delay buffers."""
        self.time_phase = 0.0
        self.buffers: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=16))

    def update_step(self, global_state: PlantState) -> None:
        """Update delayed/noisy sensor values from current plant state."""
        sensors = global_state.sensors
        reactor = global_state.reactor
        cooling = global_state.cooling
        turbine = global_state.turbine
        electrical = global_state.electrical

        stress_factor = clamp_percent(
            reactor.stress_index * 0.5
            + max(0.0, 80.0 - cooling.system_health) * 0.3
            + max(0.0, 80.0 - turbine.turbine_health) * 0.2
        ) / 100.0

        self.time_phase += 0.09
        channels = {
            "core_power": reactor.power,
            "core_temperature": reactor.temperature,
            "core_reactivity": (reactor.reactivity + 10.0) * 5.0,
            "pump_speed": cooling.pump_speed,
            "coolant_temperature": cooling.coolant_temperature,
            "cooling_efficiency": cooling.heat_removal_efficiency,
            "turbine_rpm": turbine.rpm,
            "valve_position": turbine.valve_opening,
            "steam_pressure": turbine.steam_pressure,
            "generator_output": electrical.output_power,
            "generator_temperature": electrical.generator_temperature,
            "grid_demand": electrical.grid_demand,
            "grid_stability": electrical.grid_stability,
        }

        for index, (name, true_value) in enumerate(channels.items()):
            sensors.true_values[name] = clamp_percent(true_value)
            sensors.noise_levels.setdefault(name, 0.8)
            sensors.drift_rates.setdefault(name, 0.02)
            sensors.delays.setdefault(name, 0.2)
            sensors.health_bias.setdefault(name, 0.0)

            base_noise = 0.8 + (index % 3) * 0.3
            sensors.noise_levels[name] = base_noise + stress_factor * 1.7

            drift_wave = math.sin(self.time_phase * 0.05 + index * 0.7)
            sensors.health_bias[name] = clamp_percent(
                (sensors.health_bias[name] + drift_wave * sensors.drift_rates[name] * 0.1) + 50.0
            ) - 50.0

            noisy_value = true_value + math.sin(self.time_phase + index) * sensors.noise_levels[name]
            noisy_value += sensors.health_bias[name]

            delay_steps = max(1, int(sensors.delays[name] / max(global_state.tick, 0.01)))
            buffer = self.buffers[name]
            buffer.append(clamp_percent(noisy_value))
            while len(buffer) < delay_steps:
                buffer.append(clamp_percent(noisy_value))

            delayed_index = max(0, len(buffer) - delay_steps)
            sensors.values[name] = list(buffer)[delayed_index]

        # legacy compatibility keys for older systems
        sensors.values["reactor_power"] = sensors.values["core_power"]
        sensors.values["core_temp"] = sensors.values["core_temperature"]
