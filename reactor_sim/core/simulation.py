"""Tick-based simulation engine for fictional plant system coordination."""

from __future__ import annotations

from typing import Iterable

from reactor_sim.control.player import PlayerController
from reactor_sim.core.state import PlantState
from reactor_sim.events.anomalies import AnomalyManager
from reactor_sim.sensors.sensors import SensorSuite
from reactor_sim.systems.cooling import CoolingSystem
from reactor_sim.systems.generator import GeneratorSystem
from reactor_sim.systems.reactor import ReactorSystem
from reactor_sim.systems.safety import SafetySystem
from reactor_sim.systems.turbine import TurbineSystem
from reactor_sim.ui.console import ConsoleRenderer
from reactor_sim.utils.logging import EventLog


class SimulationEngine:
    """Simulation engine coordinating fictional subsystem updates."""

    def __init__(self, state: PlantState | None = None, tick: float = 0.1) -> None:
        """Initialize the simulation engine with core subsystems."""
        self.state = state or PlantState()
        self.state.tick = tick
        self.player = PlayerController()
        self.reactor = ReactorSystem()
        self.cooling = CoolingSystem()
        self.turbine = TurbineSystem()
        self.generator = GeneratorSystem()
        self.safety = SafetySystem()
        self.sensors = SensorSuite()
        self.anomalies = AnomalyManager()
        self.event_log = EventLog()
        self.renderer = ConsoleRenderer()
        self.paused = False
        self.speed_multiplier = 1.0

    def set_paused(self, paused: bool) -> None:
        """Pause or resume the simulation loop."""
        self.paused = paused

    def set_speed(self, multiplier: float) -> None:
        """Adjust the simulation speed for testing purposes."""
        self.speed_multiplier = max(0.1, multiplier)

    def step(self) -> None:
        """Advance the simulation by a single tick."""
        if self.paused:
            return
        self.state.time += self.state.tick * self.speed_multiplier
        self.player.apply_step(self.state)
        self.reactor.update_step(self.state)
        self.cooling.update_step(self.state)
        self.turbine.update_step(self.state)
        self.generator.update_step(self.state)
        self.anomalies.update_step(self.state)
        self.sensors.update_step(self.state)
        self.safety.update_step(self.state)
        self.event_log.capture_snapshot(self.state)

    def run(self, steps: int = 10, render: bool = True) -> None:
        """Run the simulation for a fixed number of steps."""
        for _ in range(steps):
            self.step()
            if render:
                self.renderer.render(self.state)

    def run_with_schedule(self, schedule: Iterable[float], render: bool = True) -> None:
        """Run the simulation using a custom schedule of speed multipliers."""
        for multiplier in schedule:
            self.set_speed(multiplier)
            self.step()
            if render:
                self.renderer.render(self.state)

    # TODO: hook GUI integration here in a future step.
    # TODO: add autopilot hooks for control modules.
    # TODO: integrate AI advisor messaging.
