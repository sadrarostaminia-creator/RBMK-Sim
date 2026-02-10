"""Application entry point for the fictional reactor simulator (console hook)."""

from reactor_sim.core.simulation import SimulationEngine
from reactor_sim.scenarios.tutorial import TutorialScenario


def main() -> None:
    """Run a scripted tutorial walkthrough to verify guided onboarding flow."""
    engine = SimulationEngine()
    tutorial = TutorialScenario()
    engine.attach_tutorial(tutorial)
    tutorial.start(engine.state)

    # Stage 1
    engine.run(steps=7)

    # Stage 2
    engine.player.raise_rods(engine.state)
    tutorial.register_action("raise_rods")
    engine.run(steps=3)

    # Stage 3
    engine.player.increase_pump_speed(engine.state)
    tutorial.register_action("pump_up")
    engine.run(steps=3)

    # Stage 4
    engine.player.increase_valve_opening(engine.state, steps=2)
    tutorial.register_action("valve_up")
    engine.run(steps=4)

    # Stage 5
    engine.player.increase_load_target(engine.state)
    tutorial.register_action("load_up")
    engine.run(steps=3)

    # Stage 6
    engine.player.acknowledge_alarm(engine.state, "Core temperature trending high")
    tutorial.register_action("ack")
    engine.run(steps=3)

    # Stage 7
    engine.player.set_autopilot_enabled(engine.state, True)
    tutorial.register_action("autopilot_on")
    engine.run(steps=4)

    print("Tutorial progress summary:", tutorial.progress)


if __name__ == "__main__":
    main()
