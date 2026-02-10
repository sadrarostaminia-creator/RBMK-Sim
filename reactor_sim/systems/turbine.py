"""Steam and turbine system stub for the fictional simulator."""

from reactor_sim.core.state import PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class TurbineSystem:
    """Placeholder turbine system with fictional adjustments."""

    def __init__(self) -> None:
        """Initialize the turbine system stub."""
        self.rpm_drag = 0.3

    def update_step(self, global_state: PlantState) -> None:
        """Update turbine values using abstract, game-balanced behavior."""
        turbine = global_state.turbine
        reactor = global_state.reactor
        turbine.steam_pressure = clamp_percent(turbine.steam_pressure + reactor.temperature * 0.01)
        turbine.rpm = clamp_percent(turbine.rpm + turbine.valve_opening * 0.05 - self.rpm_drag)
        turbine.valve_opening = clamp_percent(turbine.valve_opening + (reactor.power - 50.0) * 0.02)
