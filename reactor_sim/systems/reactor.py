"""Reactor core logic stub for the fictional simulator."""

from reactor_sim.core.state import PlantState
from reactor_sim.utils.math_helpers import clamp_percent


class ReactorSystem:
    """Placeholder reactor system with fictional adjustments."""

    def __init__(self) -> None:
        """Initialize the reactor system stub."""
        self.heat_bias = 0.2

    def update_step(self, global_state: PlantState) -> None:
        """Update reactor state using abstract, game-balanced behavior."""
        reactor = global_state.reactor
        control_effect = (50.0 - reactor.control_rod_insertion) * 0.02
        reactor.reactivity = max(-10.0, min(10.0, reactor.reactivity + control_effect))
        reactor.power = clamp_percent(reactor.power + reactor.reactivity * 0.1)
        reactor.temperature = clamp_percent(reactor.temperature + reactor.power * 0.02 + self.heat_bias)
        reactor.fuel_condition = clamp_percent(reactor.fuel_condition - reactor.power * 0.005)
