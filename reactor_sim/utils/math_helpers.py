"""Abstract math helpers for game-balanced calculations."""


def clamp_percent(value: float) -> float:
    """Clamp a value into the 0-100 percent range (abstract utility)."""
    return max(0.0, min(100.0, value))
