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
        turbine = state.turbine
        electrical = state.electrical
        safety = state.safety
        warnings = ", ".join(safety.warnings_active) or "None"

        fields = [
            f"t={state.time:.1f}",
            f"CoreP={reactor.power:.1f}%",
            f"RPM={turbine.rpm:.1f}",
            f"ElecOut={electrical.output_power:.1f}%",
            f"GenEff={electrical.generator_efficiency:.1f}%",
            f"GridD={electrical.grid_demand:.1f}%",
            f"GridStb={electrical.grid_stability:.1f}%",
            f"Mode={electrical.grid_mode}",
        ]

        if self.debug:
            fields.extend(
                [
                    f"Valve={turbine.valve_opening:.1f}%",
                    f"LoadT={electrical.load_target:.1f}%",
                    f"GenT={electrical.generator_temperature:.1f}",
                    f"GenH={electrical.generator_health:.1f}%",
                    f"Bal={electrical.power_balance:.1f}",
                    f"Penalty={electrical.penalty_level:.1f}",
                ]
            )

        fields.append(f"Warn={warnings}")
        print(" | ".join(fields))

    # TODO: swap console output for GUI in future steps.
