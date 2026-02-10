"""Cooling system stub for the fictional simulator."""

from reactor_sim.core.state import PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class CoolingSystem:
    """Placeholder cooling system with fictional adjustments."""

    def __init__(self) -> None:
        """Initialize the cooling system stub."""
        self.drag = 0.5

    def update_step(self, global_state: PlantState) -> None:
        """Update cooling values using abstract, game-balanced behavior."""
        cooling = global_state.cooling
        reactor = global_state.reactor
        cooling.pump_flow = clamp_percent(cooling.pump_flow - self.drag * 0.1)
        cooling.heat_removal_efficiency = clamp_percent(
            cooling.heat_removal_efficiency + cooling.pump_flow * 0.01
        )
        reactor.temperature = clamp_percent(
            reactor.temperature - cooling.heat_removal_efficiency * 0.02
        )
