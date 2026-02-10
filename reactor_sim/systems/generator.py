"""Electrical output system stub for the fictional simulator."""

from reactor_sim.core.state import PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class GeneratorSystem:
    """Placeholder generator system with fictional adjustments."""

    def __init__(self) -> None:
        """Initialize the generator system stub."""
        self.loss_bias = 0.1

    def update_step(self, global_state: PlantState) -> None:
        """Update electrical values using abstract, game-balanced behavior."""
        electrical = global_state.electrical
        turbine = global_state.turbine
        electrical.output_power = clamp_percent(turbine.rpm * 0.8)
        electrical.efficiency = clamp_percent(electrical.efficiency - self.loss_bias)
        electrical.grid_load = clamp_percent(electrical.grid_load + (electrical.output_power - 50.0) * 0.05)
