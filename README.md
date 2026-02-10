# Fictional Reactor & Turbine Simulator (RBMK-Inspired, Abstracted)

This project is a **fictional, educational game system** inspired by RBMK-style ideas, but fully abstracted and non-realistic. It teaches cause-and-effect through **percentages, abstract units, and invented relationships**. It is **not** science software and must never be used for real-world replication.

## Safety & Fiction Rules

- **No real reactor equations**
- **No real material constants**
- **No real operational limits or emergency logic**
- **No instructional or operational realism**

All systems use game-balanced behavior only.

## Run Modes

### Console tutorial demo

```bash
python -m reactor_sim.main
```

### Textured Tkinter GUI

```bash
python -m reactor_sim.main --gui
```

The GUI provides:
- live bars for power/temperature/RPM/output/stability
- alarm and failure panels
- advisor message stream
- control buttons for rods/pump/valve/load/autopilot

## Failure System (Fictional)

The simulator includes random, temporary failures (for gameplay pressure), including examples like:
- Pump Cavitation
- Valve Stiction
- Sensor Ghost Drift
- Generator Hotspot

These produce degraded behavior and warnings, but remain abstract.

## Packaging to Executable

From repo root:

```bash
pyinstaller --onefile --name rbmk_sim reactor_sim/main.py
```

Output binary will appear under `dist/` for the current platform.

## Repository Layout

```
reactor_sim/
├── ai/                    # Advisor mentor logic
├── control/               # Player + autopilot controls
├── core/                  # Plant state + simulation engine
├── events/                # Failures and anomalies
├── scenarios/             # Tutorial/sandbox scenarios
├── sensors/               # Noisy delayed sensors
├── systems/               # Reactor/cooling/turbine/generator/safety
├── ui/                    # Console + GUI interfaces
└── utils/                 # Logging and helpers
```
