"""Temporary text UI placeholder for the fictional simulator."""

from __future__ import annotations

from reactor_sim.core.state import PlantState


class ConsoleRenderer:
    """Console renderer for debugging the fictional simulation state."""

    def __init__(self, debug: bool = True) -> None:
        """Initialize renderer with optional debug verbosity."""
        self.debug = debug

    def render(self, state: PlantState) -> None:
        """Render concise situational awareness with sensor-vs-real separation."""
        sensors = state.sensors
        safety = state.safety
        control = state.control

        ap_status = "ON" if control.autopilot_enabled else "OFF"
        top = [
            f"t={state.time:.1f}",
            f"AP={ap_status}/{control.autopilot_mode}",
            f"ADV={state.advisor.mode}",
            f"TargetP={control.autopilot_target_power:.1f}%",
            f"REAL CoreT={state.reactor.temperature:.1f}",
            f"SENS CoreT={sensors.values.get('core_temperature', 0.0):.1f}",
            f"REAL RPM={state.turbine.rpm:.1f}",
            f"SENS RPM={sensors.values.get('turbine_rpm', 0.0):.1f}",
            f"REAL Out={state.electrical.output_power:.1f}%",
            f"SENS Out={sensors.values.get('generator_output', 0.0):.1f}%",
        ]
        print(" | ".join(top))
        if control.tutorial_active:
            print(f"TUTORIAL: {control.tutorial_stage} :: {control.tutorial_objective}")

        alarm_lines = []
        for name, severity in safety.alarm_severity.items():
            if severity == "none":
                continue
            trend = safety.alarm_trends.get(name, "stable")
            emoji = "🟢" if severity == "advisory" else "🟡" if severity == "warning" else "🔴"
            alarm_lines.append(f"{emoji} {name} [{severity}/{trend}]")

        if alarm_lines:
            print("ALARMS: " + " ; ".join(alarm_lines[:4]))
        else:
            print("ALARMS: none")

        if safety.active_failures:
            print("FAILURES: " + ", ".join(safety.active_failures))
        else:
            print("FAILURES: none")

        if state.advisor.visible_messages:
            print("ADVISOR: " + state.advisor.visible_messages[-1])
        else:
            print("ADVISOR: no message")

        if self.debug:
            recent_alarm = state.safety.alarm_history[-2:]
            recent_ap = state.control.decision_log[-2:]
            print("ALARM-HIST: " + (" || ".join(recent_alarm) if recent_alarm else "none"))
            print("AP-DECISIONS: " + (" || ".join(recent_ap) if recent_ap else "none"))

    # TODO: swap console output for GUI in future steps.
