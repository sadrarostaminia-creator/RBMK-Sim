"""Sensor abstraction stubs for the fictional simulator."""

from reactor_sim.core.state import PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class SensorSuite:
    """Placeholder sensor collection with fictional noise and drift."""

    def __init__(self) -> None:
        """Initialize the sensor suite stub."""
        self.noise_seed = 0.0

    def update_step(self, global_state: PlantState) -> None:
        """Update sensor values from plant state with abstract effects."""
        sensors = global_state.sensors
        reactor = global_state.reactor
        self.noise_seed = (self.noise_seed + 0.07) % 1.0
        sensors.values["reactor_power"] = clamp_percent(reactor.power + self.noise_seed)
        sensors.values["core_temp"] = clamp_percent(reactor.temperature - self.noise_seed)
        sensors.noise_levels.setdefault("reactor_power", 1.0)
        sensors.drift_rates.setdefault("core_temp", 0.05)
        sensors.delays.setdefault("reactor_power", 0.2)
