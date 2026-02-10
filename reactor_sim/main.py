"""Application entry point for the fictional reactor simulator (console hook)."""

from reactor_sim.core.simulation import SimulationEngine


def main() -> None:
    """Run a short console simulation demo with autopilot + manual overrides."""
    engine = SimulationEngine()
    engine.run(steps=4)

    engine.player.set_autopilot_enabled(engine.state, True)
    engine.player.set_autopilot_mode(engine.state, "safe_hold")
    engine.run(steps=6)

    engine.player.set_autopilot_mode(engine.state, "load_follow")
    engine.player.set_mode_grid_follow(engine.state)
    engine.run(steps=8)

    engine.player.set_valve_mode_idle(engine.state)
    engine.player.increase_pump_speed(engine.state, steps=2)
    engine.run(steps=5)

    engine.player.set_autopilot_mode(engine.state, "power_hold")
    engine.state.control.autopilot_target_power = 55.0
    engine.run(steps=6)

    engine.player.set_autopilot_enabled(engine.state, False)
    engine.run(steps=3)


if __name__ == "__main__":
    main()
