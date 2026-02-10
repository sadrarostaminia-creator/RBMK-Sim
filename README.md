# Fictional Reactor & Turbine Simulator (RBMK-Inspired, Abstracted)

This project is a **fictional, educational game system** inspired by RBMK-style ideas, but it is fully abstracted and non-realistic. The simulator is designed to teach cause-and-effect through **percentages, abstract units, and invented relationships**. It is **not** science software and must never be used for real-world replication.

## Project Goals

- Simulate a fictional **reactor → steam → turbine → generator** chain.
- Provide a playable and observable game loop.
- Support manual control, autopilot, and AI guidance.
- Be structured for future packaging as a Windows executable.

## Safety & Fiction Disclaimer

- **No real reactor equations**
- **No real material constants**
- **No real operational limits or emergency logic**
- **No instructional or operational realism**

All systems use **percentages**, **abstract units**, and **game-balanced behavior**.

## Repository Layout

```
reactor_sim/
├── main.py                 # Application entry point (later GUI hook)
├── core/
│   ├── __init__.py
│   ├── simulation.py       # Main tick loop (empty for now)
│   └── state.py            # Global plant state definitions
├── systems/
│   ├── __init__.py
│   ├── reactor.py          # Reactor core logic (stub only)
│   ├── cooling.py          # Cooling system (stub)
│   ├── turbine.py          # Steam & turbine system (stub)
│   ├── generator.py        # Electrical output system (stub)
│   └── safety.py           # Alarms & trips (stub)
├── control/
│   ├── __init__.py
│   ├── player.py           # Manual controls (empty)
│   ├── autopilot.py        # Automatic control logic (empty)
│   └── ai_advisor.py       # Advisory AI (empty)
├── sensors/
│   ├── __init__.py
│   └── sensors.py          # Sensor abstractions (stub)
├── events/
│   ├── __init__.py
│   └── anomalies.py        # Random events & failures (stub)
├── ui/
│   ├── __init__.py
│   ├── console.py          # Temporary text UI
│   └── gui.py              # Future GUI placeholder
├── scenarios/
│   ├── __init__.py
│   ├── sandbox.py
│   └── tutorial.py
├── utils/
│   ├── __init__.py
│   ├── math_helpers.py     # Abstract math helpers
│   └── logging.py          # Event & state logging
├── README.md
├── requirements.txt
└── .gitignore
```

## Planned Features (High-Level)

- Deterministic simulation tick engine with pluggable subsystems.
- Scenario scripting (tutorial and sandbox modes).
- Manual control panel with optional autopilot.
- Advisory AI for hints and coaching.
- Save/load of fictional plant state.

> **Note:** Step 1 focuses only on structure and stubs. No simulation logic, UI behavior, or real-world math is implemented yet.
