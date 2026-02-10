"""Application entry point for the fictional reactor simulator (console hook)."""

from reactor_sim.core.simulation import SimulationEngine


def main() -> None:
    """Run a short console simulation demo with manual control hooks."""
    engine = SimulationEngine()
    engine.run(steps=4)

    engine.player.set_pump_mode_high(engine.state)
    engine.player.set_valve_mode_idle(engine.state)
    engine.run(steps=6)

    engine.player.set_power_target(engine.state, 65.0)
    engine.player.raise_rods(engine.state, steps=3)
    engine.player.set_valve_mode_cruise(engine.state)
    engine.run(steps=10)

    engine.player.set_valve_mode_high_load(engine.state)
    engine.run(steps=8)

    engine.player.emergency_insert(engine.state)
    engine.run(steps=5)


if __name__ == "__main__":
    main()
