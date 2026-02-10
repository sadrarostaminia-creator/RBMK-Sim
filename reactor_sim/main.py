"""Application entry point for the fictional reactor simulator (console hook)."""

from reactor_sim.core.simulation import SimulationEngine


def main() -> None:
    """Run a short console simulation demo with manual control hooks."""
    engine = SimulationEngine()
    engine.run(steps=4)

    engine.player.set_mode_grid_follow(engine.state)
    engine.player.increase_load_target(engine.state, steps=4)
    engine.player.set_valve_mode_cruise(engine.state)
    engine.player.set_pump_mode_high(engine.state)
    engine.run(steps=10)

    engine.player.set_mode_islanded(engine.state)
    engine.player.decrease_load_target(engine.state, steps=2)
    engine.run(steps=8)

    engine.player.emergency_load_shed(engine.state)
    engine.run(steps=6)


if __name__ == "__main__":
    main()
