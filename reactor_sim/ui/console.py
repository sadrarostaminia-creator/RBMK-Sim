"""Temporary text UI placeholder for the fictional simulator."""

from __future__ import annotations

from reactor_sim.core.state import PlantState


class ConsoleRenderer:
    """Console renderer for debugging the fictional simulation state."""

    def __init__(self, debug: bool = True) -> None:
        """Initialize renderer with optional debug verbosity."""
        self.debug = debug

    def render(self, state: PlantState) -> None:
        """Render a lightweight status table to the console."""
        reactor = state.reactor
        safety = state.safety
        warnings = ", ".join(safety.warnings_active) or "None"

        fields = [
            f"t={state.time:.1f}",
            f"Rods={reactor.control_rod_insertion:.1f}%",
            f"Pwr={reactor.power:.1f}%",
            f"Temp={reactor.temperature:.1f}",
            f"Fuel={reactor.fuel_condition:.1f}%",
            f"Reac={reactor.reactivity:.2f}",
        ]

        if self.debug:
            fields.extend(
                [
                    f"TargetP={reactor.desired_power_target:.1f}%",
                    f"Stress={reactor.stress_index:.1f}",
                ]
            )

        fields.append(f"Warn={warnings}")
        print(" | ".join(fields))

    # TODO: swap console output for GUI in future steps.
