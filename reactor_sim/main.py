"""Application entry point for the fictional reactor simulator (console hook)."""

from reactor_sim.core.simulation import SimulationEngine
from reactor_sim.scenarios.tutorial import TutorialScenario


def main() -> None:
    """Run an automated tutorial walkthrough that reaches completion."""
    engine = SimulationEngine()
    engine.player.set_advisor_mode(engine.state, "training")

    tutorial = TutorialScenario()
    engine.attach_tutorial(tutorial)
    tutorial.start(engine.state)

    stage_actions_done: set[str] = set()

    while tutorial.active and engine.state.time < 60.0:
        stage_key = tutorial.current_stage.key

        if stage_key == "rods" and stage_key not in stage_actions_done:
            engine.player.raise_rods(engine.state)
            tutorial.register_action("raise_rods")
            stage_actions_done.add(stage_key)
        elif stage_key == "cooling" and stage_key not in stage_actions_done:
            engine.player.increase_pump_speed(engine.state)
            tutorial.register_action("pump_up")
            stage_actions_done.add(stage_key)
        elif stage_key == "steam_turbine" and stage_key not in stage_actions_done:
            engine.player.increase_valve_opening(engine.state, steps=2)
            tutorial.register_action("valve_up")
            stage_actions_done.add(stage_key)
        elif stage_key == "electrical" and stage_key not in stage_actions_done:
            engine.player.increase_load_target(engine.state)
            tutorial.register_action("load_up")
            stage_actions_done.add(stage_key)
        elif stage_key == "alarms" and stage_key not in stage_actions_done:
            engine.player.acknowledge_alarm(engine.state, "Core temperature trending high")
            tutorial.register_action("ack")
            stage_actions_done.add(stage_key)
        elif stage_key == "autopilot" and stage_key not in stage_actions_done:
            engine.player.set_autopilot_enabled(engine.state, True)
            tutorial.register_action("autopilot_on")
            stage_actions_done.add(stage_key)

        engine.step()
        engine.renderer.render(engine.state)

    print("Tutorial progress summary:", tutorial.progress)


if __name__ == "__main__":
    main()
