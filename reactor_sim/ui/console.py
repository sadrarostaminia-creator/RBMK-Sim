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
        cooling = state.cooling
        turbine = state.turbine
        safety = state.safety
        warnings = ", ".join(safety.warnings_active) or "None"

        fields = [
            f"t={state.time:.1f}",
            f"CoreT={reactor.temperature:.1f}",
            f"Pump={cooling.pump_speed:.1f}%",
            f"SteamP={turbine.steam_pressure:.1f}",
            f"Valve={turbine.valve_opening:.1f}%",
            f"RPM={turbine.rpm:.1f}",
            f"TurbEff={turbine.turbine_efficiency:.1f}%",
            f"TurbHP={turbine.turbine_health:.1f}%",
        ]

        if self.debug:
            fields.extend(
                [
                    f"SteamQ={turbine.steam_quality:.1f}%",
                    f"SteamProd={turbine.steam_production_rate:.1f}",
                    f"SteamLoss={turbine.steam_loss_rate:.1f}",
                    f"MechLoad={turbine.mechanical_load:.1f}",
                ]
            )

        fields.append(f"Warn={warnings}")
        print(" | ".join(fields))

    # TODO: swap console output for GUI in future steps.
