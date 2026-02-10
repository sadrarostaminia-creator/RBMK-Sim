"""Alarms and trip logic stub for the fictional simulator."""

from reactor_sim.core.state import PlantState


class SafetySystem:
    """Placeholder safety system with fictional warnings."""

    def __init__(self) -> None:
        """Initialize the safety system stub."""
        self.temperature_warning = 80.0
        self.power_warning = 85.0

    def update_step(self, global_state: PlantState) -> None:
        """Update warnings and trip flags using abstract rules."""
        safety = global_state.safety
        reactor = global_state.reactor
        safety.warnings_active.clear()
        safety.trip_flags.setdefault("manual_trip", False)
        if reactor.temperature > self.temperature_warning:
            safety.warnings_active.append("Core temperature elevated")
        if reactor.power > self.power_warning:
            safety.warnings_active.append("Power output elevated")
