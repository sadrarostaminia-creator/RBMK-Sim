"""Temporary text UI placeholder for the fictional simulator."""

from __future__ import annotations

from reactor_sim.core.state import PlantState


class ConsoleRenderer:
    """Console renderer for debugging the fictional simulation state."""

    def render(self, state: PlantState) -> None:
        """Render a lightweight status table to the console."""
        reactor = state.reactor
        cooling = state.cooling
        turbine = state.turbine
        electrical = state.electrical
        safety = state.safety
        warnings = ", ".join(safety.warnings_active) or "None"

        print(
            " | ".join(
                [
                    f"t={state.time:.1f}",
                    f"Pwr={reactor.power:.1f}%",
                    f"Temp={reactor.temperature:.1f}",
                    f"Reac={reactor.reactivity:.1f}",
                    f"Fuel={reactor.fuel_condition:.1f}%",
                    f"Flow={cooling.pump_flow:.1f}%",
                    f"RPM={turbine.rpm:.1f}",
                    f"Out={electrical.output_power:.1f}%",
                    f"Warn={warnings}",
                ]
            )
        )

    # TODO: swap console output for GUI in future steps.
