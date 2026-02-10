"""Interactive guided tutorial scenario for the fictional simulator."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List

from reactor_sim.core.state import PlantState

PROGRESS_PATH = Path.home() / ".rbmk_sim_tutorial_progress.json"


@dataclass
class TutorialStage:
    """Defines one guided tutorial stage with goals, hints, and checks."""

    key: str
    title: str
    objective: str
    explanation: str
    hint: str
    success_check: Callable[[PlantState, List[str]], bool]


class TutorialScenario:
    """Stage-based tutorial manager with safety guardrails and progress tracking."""

    def __init__(self) -> None:
        """Initialize tutorial stages and persisted progress history."""
        self.stages: List[TutorialStage] = [
            TutorialStage(
                key="orientation",
                title="Stage 1 — Orientation",
                objective="Observe power, temperature, and alarms for a few ticks.",
                explanation="You first learn to read the plant before controlling it.",
                hint="Run a few ticks and watch real vs sensor readouts.",
                success_check=lambda s, a: s.time >= 0.6,
            ),
            TutorialStage(
                key="rods",
                title="Stage 2 — Control Rod Basics",
                objective="Adjust rods slightly and observe delayed response.",
                explanation="Reactivity changes first; power and temperature follow with inertia.",
                hint="Use action 'raise_rods' or 'lower_rods' once.",
                success_check=lambda _s, a: any(x in a for x in {"raise_rods", "lower_rods"}),
            ),
            TutorialStage(
                key="cooling",
                title="Stage 3 — Cooling Interaction",
                objective="Change pump speed and observe thermal behavior.",
                explanation="Cooling changes temperature gradually, not instantly.",
                hint="Use 'pump_up' or 'pump_down'.",
                success_check=lambda _s, a: any(x in a for x in {"pump_up", "pump_down"}),
            ),
            TutorialStage(
                key="steam_turbine",
                title="Stage 4 — Steam & Turbine",
                objective="Open turbine valve and observe RPM response.",
                explanation="Steam pressure bridges reactor heat to turbine motion.",
                hint="Use 'valve_up' gradually.",
                success_check=lambda s, a: "valve_up" in a and s.turbine.rpm > 18.0,
            ),
            TutorialStage(
                key="electrical",
                title="Stage 5 — Electrical Load",
                objective="Adjust generator load while observing grid stability.",
                explanation="Higher load can increase resistance and pressure on stability.",
                hint="Use 'load_up' or 'load_down'.",
                success_check=lambda _s, a: any(x in a for x in {"load_up", "load_down"}),
            ),
            TutorialStage(
                key="alarms",
                title="Stage 6 — Alarms & Warnings",
                objective="Acknowledge an alarm and review alarm history.",
                explanation="Acknowledging alarms silences repetition but does not solve root causes.",
                hint="Use 'ack Core temperature trending high'.",
                success_check=lambda s, a: bool(s.safety.acknowledged_alarms) and "ack" in a,
            ),
            TutorialStage(
                key="autopilot",
                title="Stage 7 — Autopilot Demonstration",
                objective="Enable autopilot and observe at least one decision.",
                explanation="Autopilot is cautious and sensor-limited, not perfect.",
                hint="Use 'autopilot_on' and wait a few ticks.",
                success_check=lambda s, a: s.control.autopilot_enabled and len(s.control.decision_log) > 1,
            ),
        ]

        self.active: bool = False
        self.current_index: int = 0
        self.completed: List[str] = []
        self.skipped: List[str] = []
        self.actions: List[str] = []
        self._last_prompted_stage: int = -1
        self.progress = self._load_progress()

    @property
    def current_stage(self) -> TutorialStage:
        """Return current stage definition."""
        return self.stages[min(self.current_index, len(self.stages) - 1)]

    def start(self, state: PlantState) -> None:
        """Activate tutorial mode and reset stage-local action tracking."""
        self.active = True
        self.current_index = 0
        self.actions.clear()
        state.control.autopilot_enabled = False
        state.control.tutorial_active = True
        self._sync_stage_to_state(state)
        self._announce_stage()

    def stop(self) -> None:
        """Deactivate tutorial mode."""
        self.active = False

    def request_hint(self) -> str:
        """Return hint for current stage."""
        return self.current_stage.hint

    def explain_why(self) -> str:
        """Return learning explanation for current stage."""
        return self.current_stage.explanation

    def skip_stage(self) -> None:
        """Skip current stage and move forward."""
        key = self.current_stage.key
        if key not in self.skipped:
            self.skipped.append(key)
        self._advance_stage()

    def register_action(self, action: str) -> None:
        """Register a player tutorial action for success checks."""
        self.actions.append(action)

    def apply_guardrails(self, state: PlantState) -> None:
        """Apply stage-specific safety guardrails and auto-corrections."""
        if not self.active:
            state.control.tutorial_active = False
            return

        state.control.tutorial_active = True
        self._sync_stage_to_state(state)
        stage = self.current_stage.key
        if stage == "orientation":
            state.control.autopilot_enabled = False
            state.reactor.desired_rod_insertion = 55.0
            state.cooling.desired_pump_speed = 58.0
            state.turbine.desired_valve_opening = 30.0
            state.electrical.desired_load_target = 40.0

        elif stage == "rods":
            state.control.autopilot_enabled = False
            state.cooling.desired_pump_speed = 65.0
            state.reactor.power = min(state.reactor.power, 60.0)
            state.reactor.temperature = min(state.reactor.temperature, 82.0)

        elif stage == "cooling":
            state.control.autopilot_enabled = False
            state.cooling.system_health = max(state.cooling.system_health, 85.0)

        elif stage == "steam_turbine":
            state.turbine.desired_valve_opening = min(state.turbine.desired_valve_opening, 72.0)
            state.turbine.rpm = min(state.turbine.rpm, 82.0)

        elif stage == "electrical":
            state.electrical.grid_stability = max(state.electrical.grid_stability, 55.0)
            state.electrical.penalty_level = min(state.electrical.penalty_level, 35.0)

        elif stage == "alarms":
            state.control.autopilot_enabled = False
            if state.time > 0.5:
                state.safety.alarm_states["Core temperature trending high"] = max(
                    12.0, state.safety.alarm_states.get("Core temperature trending high", 0.0)
                )

        elif stage == "autopilot":
            state.control.autopilot_enabled = True
            state.control.autopilot_mode = "safe_hold"

    def post_step(self, state: PlantState) -> None:
        """Evaluate stage completion after each simulation tick."""
        if not self.active:
            return

        if self.current_stage.success_check(state, self.actions):
            completed_key = self.current_stage.key
            if completed_key not in self.completed:
                self.completed.append(completed_key)
            print(f"✅ Tutorial success: {self.current_stage.title}")
            self._advance_stage(state)

    def _advance_stage(self, state: PlantState | None = None) -> None:
        """Move to next stage or finish tutorial, then persist progress."""
        self.current_index += 1
        self.actions.clear()

        if self.current_index >= len(self.stages):
            self.active = False
            if state is not None:
                state.control.tutorial_active = False
                state.control.tutorial_stage = ""
                state.control.tutorial_objective = ""
            self.progress["completed_runs"] = int(self.progress.get("completed_runs", 0)) + 1
            self.progress["last_completed"] = self.completed
            self.progress["last_skipped"] = self.skipped
            self._save_progress()
            print("🎉 Tutorial complete. You can replay any time.")
            return

        if state is not None:
            self._sync_stage_to_state(state)
        self._announce_stage()


    def _sync_stage_to_state(self, state: PlantState) -> None:
        """Expose active tutorial stage/objective for UI layers."""
        state.control.tutorial_stage = self.current_stage.title
        state.control.tutorial_objective = self.current_stage.objective

    def _announce_stage(self) -> None:
        """Print current stage objective for console tutorial flow."""
        if self._last_prompted_stage == self.current_index:
            return
        self._last_prompted_stage = self.current_index
        stage = self.current_stage
        print(f"📘 {stage.title}")
        print(f"Objective: {stage.objective}")

    def _load_progress(self) -> Dict[str, object]:
        """Load persisted tutorial progress from disk."""
        if not PROGRESS_PATH.exists():
            return {"completed_runs": 0, "last_completed": [], "last_skipped": []}
        try:
            return json.loads(PROGRESS_PATH.read_text())
        except json.JSONDecodeError:
            return {"completed_runs": 0, "last_completed": [], "last_skipped": []}

    def _save_progress(self) -> None:
        """Save tutorial progress to disk."""
        PROGRESS_PATH.write_text(json.dumps(self.progress, indent=2))


def run_interactive_tutorial(engine) -> None:
    """Console-driven tutorial loop. Type commands to progress through stages."""
    tutorial = TutorialScenario()
    engine.attach_tutorial(tutorial)
    tutorial.start(engine.state)

    print("Commands: step, hint, why, skip, raise_rods, lower_rods, pump_up, pump_down,")
    print("          valve_up, valve_down, load_up, load_down, ack <alarm>, autopilot_on, exit")

    while tutorial.active:
        cmd = input("tutorial> ").strip()
        if cmd == "":
            continue
        if cmd == "exit":
            break
        if cmd == "step":
            engine.step()
            engine.renderer.render(engine.state)
            continue
        if cmd == "hint":
            print("Hint:", tutorial.request_hint())
            continue
        if cmd == "why":
            print("Why:", tutorial.explain_why())
            continue
        if cmd == "skip":
            tutorial.skip_stage()
            continue

        if cmd == "raise_rods":
            engine.player.raise_rods(engine.state)
            tutorial.register_action("raise_rods")
        elif cmd == "lower_rods":
            engine.player.lower_rods(engine.state)
            tutorial.register_action("lower_rods")
        elif cmd == "pump_up":
            engine.player.increase_pump_speed(engine.state)
            tutorial.register_action("pump_up")
        elif cmd == "pump_down":
            engine.player.decrease_pump_speed(engine.state)
            tutorial.register_action("pump_down")
        elif cmd == "valve_up":
            engine.player.increase_valve_opening(engine.state)
            tutorial.register_action("valve_up")
        elif cmd == "valve_down":
            engine.player.decrease_valve_opening(engine.state)
            tutorial.register_action("valve_down")
        elif cmd == "load_up":
            engine.player.increase_load_target(engine.state)
            tutorial.register_action("load_up")
        elif cmd == "load_down":
            engine.player.decrease_load_target(engine.state)
            tutorial.register_action("load_down")
        elif cmd.startswith("ack "):
            alarm_name = cmd[4:].strip()
            engine.player.acknowledge_alarm(engine.state, alarm_name)
            tutorial.register_action("ack")
        elif cmd == "autopilot_on":
            engine.player.set_autopilot_enabled(engine.state, True)
            tutorial.register_action("autopilot_on")
        else:
            print("Unknown command. Use hint/why/step/skip or control commands.")

        engine.step()
        engine.renderer.render(engine.state)

    print("Tutorial session ended.")
