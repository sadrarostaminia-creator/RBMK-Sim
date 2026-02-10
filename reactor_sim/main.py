"""Application entry point for the fictional reactor simulator (console hook)."""

from reactor_sim.core.simulation import SimulationEngine


def main() -> None:
    """Run a short console simulation demo with sensor/alarm visibility."""
    engine = SimulationEngine()
    engine.run(steps=5)

    engine.player.set_mode_grid_follow(engine.state)
    engine.player.increase_load_target(engine.state, steps=4)
    engine.player.set_valve_mode_high_load(engine.state)
    engine.player.set_pump_mode_low(engine.state)
    engine.run(steps=10)

    engine.player.set_advisory_mute(engine.state, True)
    engine.player.emergency_load_shed(engine.state)
    engine.run(steps=6)

    engine.player.acknowledge_alarm(engine.state, "Core temperature trending high")
    recent = engine.player.recent_alarm_history(engine.state, limit=5)
    print("Recent alarm history:")
    for line in recent:
        print(f"- {line}")


if __name__ == "__main__":
    main()
