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

        top = [
            f"t={state.time:.1f}",
            f"REAL CoreT={state.reactor.temperature:.1f}",
            f"SENS CoreT={sensors.values.get('core_temperature', 0.0):.1f}",
            f"REAL RPM={state.turbine.rpm:.1f}",
            f"SENS RPM={sensors.values.get('turbine_rpm', 0.0):.1f}",
            f"REAL Out={state.electrical.output_power:.1f}%",
            f"SENS Out={sensors.values.get('generator_output', 0.0):.1f}%",
        ]
        print(" | ".join(top))

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

        if self.debug:
            recent = state.safety.alarm_history[-3:]
            print("HISTORY: " + (" || ".join(recent) if recent else "none"))

    # TODO: swap console output for GUI in future steps.
