"""Tkinter GUI for the fictional reactor simulator with stylized textured dashboard."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from reactor_sim.core.simulation import SimulationEngine


class ReactorSimGUI:
    """Interactive GUI shell for observing and nudging the simulator."""

    def __init__(self) -> None:
        """Create engine, window, and widgets."""
        self.engine = SimulationEngine()
        self.root = tk.Tk()
        self.root.title("RBMK-Sim Fictional Plant Control Room")
        self.root.geometry("1080x680")
        self.root.configure(bg="#20242b")

        self.running = False
        self.tick_ms = 180

        self._build_texture_background()
        self._build_layout()
        self._refresh_view()

    def _build_texture_background(self) -> None:
        """Draw a subtle checker/stripe pattern to mimic panel texture."""
        canvas = tk.Canvas(self.root, highlightthickness=0, bg="#1b1f26")
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        for y in range(0, 700, 24):
            shade = "#252b35" if (y // 24) % 2 == 0 else "#222833"
            canvas.create_rectangle(0, y, 1200, y + 24, fill=shade, outline="")
        for x in range(0, 1200, 16):
            color = "#2b3240" if (x // 16) % 2 == 0 else "#29303c"
            canvas.create_line(x, 0, x, 700, fill=color)
        self.bg_canvas = canvas

    def _build_layout(self) -> None:
        """Construct metrics, controls, advisor, and failure panels."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#2a313d")
        style.configure("TLabel", background="#2a313d", foreground="#dce6f2")
        style.configure("TButton", padding=6)

        self.main = ttk.Frame(self.root, padding=10)
        self.main.place(x=16, y=16, relwidth=0.97, relheight=0.95)

        left = ttk.Frame(self.main)
        right = ttk.Frame(self.main)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right.pack(side="right", fill="y")

        self.status_label = ttk.Label(left, text="Status")
        self.status_label.pack(anchor="w", pady=(0, 6))

        self.bars = {}
        for key, text in [
            ("power", "Core Power"),
            ("temp", "Core Temp"),
            ("rpm", "Turbine RPM"),
            ("output", "Electrical Output"),
            ("grid", "Grid Stability"),
        ]:
            row = ttk.Frame(left)
            row.pack(fill="x", pady=3)
            ttk.Label(row, text=text, width=18).pack(side="left")
            bar = ttk.Progressbar(row, orient="horizontal", length=320, mode="determinate", maximum=100)
            bar.pack(side="left", padx=6)
            value_lbl = ttk.Label(row, text="0.0", width=8)
            value_lbl.pack(side="left")
            self.bars[key] = (bar, value_lbl)

        self.failure_title = ttk.Label(left, text="Active Failures")
        self.failure_title.pack(anchor="w", pady=(10, 2))
        self.failure_box = tk.Text(left, height=5, bg="#151b22", fg="#f4c17a", relief="flat")
        self.failure_box.pack(fill="x")

        self.alarm_title = ttk.Label(left, text="Active Alarms")
        self.alarm_title.pack(anchor="w", pady=(10, 2))
        self.alarm_box = tk.Text(left, height=8, bg="#12171d", fg="#ffb3b3", relief="flat")
        self.alarm_box.pack(fill="both", expand=True)

        self.advisor_title = ttk.Label(left, text="Advisor")
        self.advisor_title.pack(anchor="w", pady=(10, 2))
        self.advisor_box = tk.Text(left, height=6, bg="#10151a", fg="#b8e1ff", relief="flat")
        self.advisor_box.pack(fill="x")

        ttk.Label(right, text="Controls", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))

        self._add_btn(right, "Run/Pause", self._toggle_run)
        self._add_btn(right, "Step", self._single_step)
        self._add_btn(right, "Rods +", lambda: self.engine.player.raise_rods(self.engine.state))
        self._add_btn(right, "Rods -", lambda: self.engine.player.lower_rods(self.engine.state))
        self._add_btn(right, "Pump +", lambda: self.engine.player.increase_pump_speed(self.engine.state))
        self._add_btn(right, "Pump -", lambda: self.engine.player.decrease_pump_speed(self.engine.state))
        self._add_btn(right, "Valve +", lambda: self.engine.player.increase_valve_opening(self.engine.state))
        self._add_btn(right, "Valve -", lambda: self.engine.player.decrease_valve_opening(self.engine.state))
        self._add_btn(right, "Load +", lambda: self.engine.player.increase_load_target(self.engine.state))
        self._add_btn(right, "Load -", lambda: self.engine.player.decrease_load_target(self.engine.state))
        self._add_btn(right, "Autopilot On", lambda: self.engine.player.set_autopilot_enabled(self.engine.state, True))
        self._add_btn(right, "Autopilot Off", lambda: self.engine.player.set_autopilot_enabled(self.engine.state, False))

        ttk.Label(right, text="Advisor Mode").pack(anchor="w", pady=(10, 4))
        mode_var = tk.StringVar(value=self.engine.state.advisor.mode)
        mode_menu = ttk.Combobox(
            right,
            values=["silent", "passive", "guidance", "training"],
            textvariable=mode_var,
            state="readonly",
            width=14,
        )
        mode_menu.pack(anchor="w")

        def change_mode(_event=None):
            self.engine.player.set_advisor_mode(self.engine.state, mode_var.get())

        mode_menu.bind("<<ComboboxSelected>>", change_mode)

    def _add_btn(self, parent: ttk.Frame, text: str, cmd) -> None:
        """Create a sidebar control button."""
        ttk.Button(parent, text=text, command=cmd, width=18).pack(anchor="w", pady=2)

    def _toggle_run(self) -> None:
        """Start/stop periodic stepping."""
        self.running = not self.running
        if self.running:
            self._tick_loop()

    def _single_step(self) -> None:
        """Advance exactly one simulation tick."""
        self.engine.step()
        self._refresh_view()

    def _tick_loop(self) -> None:
        """Drive continuous simulation while running flag is true."""
        if not self.running:
            return
        self.engine.step()
        self._refresh_view()
        self.root.after(self.tick_ms, self._tick_loop)

    def _refresh_view(self) -> None:
        """Update metric bars and text panels from current state."""
        s = self.engine.state

        self.status_label.configure(
            text=(
                f"Time {s.time:.1f}  |  AP {'ON' if s.control.autopilot_enabled else 'OFF'} "
                f"({s.control.autopilot_mode})  |  ADV {s.advisor.mode.upper()}"
            )
        )

        values = {
            "power": s.reactor.power,
            "temp": s.reactor.temperature,
            "rpm": s.turbine.rpm,
            "output": s.electrical.output_power,
            "grid": s.electrical.grid_stability,
        }
        for key, val in values.items():
            bar, lbl = self.bars[key]
            bar["value"] = max(0.0, min(100.0, val))
            lbl.configure(text=f"{val:.1f}")

        self._set_text(self.failure_box, "\n".join(s.safety.active_failures or ["None"]))
        self._set_text(self.alarm_box, "\n".join(s.safety.warnings_active[-12:] or ["None"]))
        self._set_text(self.advisor_box, "\n".join(s.advisor.visible_messages[-6:] or ["No advisor message yet."]))

    def _set_text(self, widget: tk.Text, text: str) -> None:
        """Replace text widget contents without enabling user edits."""
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def run(self) -> None:
        """Enter GUI main loop."""
        self.root.mainloop()


def launch_gui() -> None:
    """Entry point for GUI mode."""
    ReactorSimGUI().run()
