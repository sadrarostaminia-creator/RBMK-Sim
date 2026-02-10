"""AI advisor/mentor system that explains and suggests without controlling."""

from __future__ import annotations

from reactor_sim.core.state import AdvisorMessage, PlantState


class AdvisorSystem:
    """Observes sensors and logs, then emits explanatory advisory messages."""

    def __init__(self) -> None:
        """Initialize advisor cursors and trend memory."""
        self._tick_counter = 0
        self._last_sensor: dict[str, float] = {}
        self._autopilot_cursor = 0
        self._player_cursor = 0
        self._mode_cadence = {"silent": 8, "passive": 7, "guidance": 5, "training": 3}

    def set_mode(self, state: PlantState, mode: str) -> None:
        """Set advisor communication mode if valid."""
        if mode in self._mode_cadence:
            state.advisor.mode = mode
            state.advisor.cadence_ticks = self._mode_cadence[mode]
            self._emit(
                state,
                category="procedural",
                level="info",
                text=f"Advisor mode changed to {mode}.",
            )

    def update_step(self, state: PlantState) -> None:
        """Run periodic advisor analysis and emit messages based on mode."""
        self._tick_counter += 1
        cadence = self._mode_cadence.get(state.advisor.mode, 5)
        state.advisor.cadence_ticks = cadence

        if self._tick_counter % cadence != 0:
            return

        sensors = state.sensors.values
        mode = state.advisor.mode
        messages: list[tuple[str, str, str]] = []

        core_t = sensors.get("core_temperature", 0.0)
        steam_p = sensors.get("steam_pressure", 0.0)
        grid_stability = sensors.get("grid_stability", 100.0)
        power = sensors.get("core_power", 0.0)
        output = sensors.get("generator_output", 0.0)

        prev_t = self._last_sensor.get("core_temperature", core_t)
        prev_p = self._last_sensor.get("steam_pressure", steam_p)
        prev_grid = self._last_sensor.get("grid_stability", grid_stability)

        if core_t - prev_t > 1.1:
            messages.append(
                (
                    "thermal",
                    "warning",
                    "Core temperature is rising faster than cooling response; this trend can raise stress if sustained. Consider a gentler power posture.",
                )
            )
        if steam_p - prev_p > 1.2:
            messages.append(
                (
                    "mechanical",
                    "warning",
                    "Steam pressure is climbing with valve demand; pressure growth can push turbine efficiency down if this continues.",
                )
            )
        if prev_grid - grid_stability > 0.8:
            messages.append(
                (
                    "electrical",
                    "warning",
                    "Grid stability is trending lower; imbalance between output and demand appears to be accumulating.",
                )
            )

        if power > output + 25.0:
            messages.append(
                (
                    "electrical",
                    "info",
                    "Core power exceeds electrical extraction by a wide margin, indicating conversion inefficiency across steam/turbine/load settings.",
                )
            )

        if mode in {"guidance", "training"}:
            messages.extend(self._analyze_player_actions(state))
            messages.extend(self._explain_autopilot(state))

        if mode == "training" and state.control.tutorial_active:
            messages.append(
                (
                    "procedural",
                    "info",
                    f"Tutorial focus: {state.control.tutorial_stage}. Objective: {state.control.tutorial_objective}",
                )
            )

        if mode == "passive":
            messages = [m for m in messages if m[1] in {"warning", "critical"}]

        if mode == "silent":
            for category, level, text in messages:
                self._store_only(state, category, level, text)
        else:
            for category, level, text in messages[:3]:
                self._emit(state, category, level, text)

        self._last_sensor["core_temperature"] = core_t
        self._last_sensor["steam_pressure"] = steam_p
        self._last_sensor["grid_stability"] = grid_stability

    def _analyze_player_actions(self, state: PlantState) -> list[tuple[str, str, str]]:
        """Detect repeated player control habits and explain likely effects."""
        results: list[tuple[str, str, str]] = []
        actions = state.control.player_action_log
        recent = actions[max(0, len(actions) - 6) :]

        if recent.count("raise_rods") >= 3:
            results.append(
                (
                    "control",
                    "warning",
                    "Repeated rod withdrawal is increasing reactivity pressure; delayed temperature response can make this feel stable before it is.",
                )
            )
        if recent.count("load_up") >= 3:
            results.append(
                (
                    "electrical",
                    "warning",
                    "Frequent load increases are adding mechanical resistance; this can suppress RPM and reduce net output if turbine flow does not keep up.",
                )
            )
        return results

    def _explain_autopilot(self, state: PlantState) -> list[tuple[str, str, str]]:
        """Translate recent autopilot decisions into short mentor-style explanations."""
        out: list[tuple[str, str, str]] = []
        decisions = state.control.decision_log

        if self._autopilot_cursor < len(decisions):
            latest = decisions[-1]
            if "mode=" in latest:
                out.append(
                    (
                        "procedural",
                        "info",
                        f"Autopilot rationale: {latest.split(' ', 2)[-1]}. This is sensor-driven and may lag fast transients.",
                    )
                )
            self._autopilot_cursor = len(decisions)
        return out

    def _emit(self, state: PlantState, category: str, level: str, text: str) -> None:
        """Store and expose advisor message to UI/log review layers."""
        msg = AdvisorMessage(timestamp=state.time, category=category, level=level, text=text)
        state.advisor.history.append(msg)
        state.advisor.visible_messages.append(f"{level.upper()} [{category}] {text}")
        if len(state.advisor.history) > 160:
            state.advisor.history.pop(0)
        if len(state.advisor.visible_messages) > 20:
            state.advisor.visible_messages.pop(0)

    def _store_only(self, state: PlantState, category: str, level: str, text: str) -> None:
        """Store advisor analysis silently without visible message emission."""
        msg = AdvisorMessage(timestamp=state.time, category=category, level=level, text=text)
        state.advisor.history.append(msg)
        if len(state.advisor.history) > 160:
            state.advisor.history.pop(0)
