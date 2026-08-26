import os
import threading
import tkinter as tk
from tkinter import messagebox
import time
import keyboard
import pystray
from PIL import Image, ImageDraw
from config import ScriptConfig
from PathOfExile2GameStateController import PathOfExile2GameStateController
from screen_types import Size, Vector2
from IConfigurable import IConfigurable

class UI(IConfigurable):
    def __init__(self, config: ScriptConfig, screen_size: Size, game_controller: PathOfExile2GameStateController, game_logic_fn=None , on_config_change_fn=None):
        self._on_config_change = on_config_change_fn
        self.game_controller = game_controller
        self.is_running_text_pos = game_controller.poe2_positions.get_top_of_mana_bar()
        self.configure(config)
        self.screen_w = screen_size[0]
        self.screen_h = screen_size[1]
        self._on_kill = lambda: os._exit(0)
        self._game_logic_fn = game_logic_fn
        self._game_logic_thread: threading.Thread | None = None

        self._running_event = threading.Event()
        self._overlay_stop = threading.Event()
        self._overlay_canvas = None

    def configure(self, config: ScriptConfig) -> None:
        self.config = config
        self.game_controller.reader.configure(config)

        for hotkey in getattr(self, "_hotkeys", []):
            keyboard.remove_hotkey(hotkey)

        self._hotkeys = [self.config.configData.hotkey_toggle, self.config.configData.hotkey_exit]
        keyboard.add_hotkey(self.config.configData.hotkey_toggle, self.toggle)
        keyboard.add_hotkey(self.config.configData.hotkey_exit, self.kill)

    @property
    def running(self) -> bool:
        return self._running_event.is_set()

    def toggle(self):
        if self._running_event.is_set():
            print("paused")
            self.stop_game_logic()
        else:
            self._running_event.set()
            print("started")
            self.start_game_logic()

    def target_game_logic_fn(self):
        while self._running_event.is_set():
            self._game_logic_fn()
            if self._running_event.is_set():
                time.sleep(self.config.configData.check_screen_rate_ms/1000)
            else:
                break

    def start_game_logic(self):
        if self._game_logic_fn is None:
            return
        if self._game_logic_thread and self._game_logic_thread.is_alive():
            return
        self._game_logic_thread = threading.Thread(target=self.target_game_logic_fn, daemon=True)
        self._game_logic_thread.start()

    def stop_game_logic(self):
        self._running_event.clear()

    def kill(self):
        self.stop_game_logic()
        self._overlay_stop.set()
        if self._on_kill:
            self._on_kill()

    def show_error(self, title: str, message: str):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror(title, message)
        root.destroy()

    def clear_debug_pixels(self):
        c = self._overlay_canvas
        if c:
            c.after(0, lambda: c.delete("debug_px"))

    def draw_debug_pixels(self, points: list[Vector2]):
        c = self._overlay_canvas
        if not (self.config.configData.debug and c):
            return
        def _draw(pts=points):
            for x, y in pts:
                c.create_rectangle(x, y + 1, x + 1, y + 2, fill="white", outline="white", tags="debug_px")
        c.after(0, _draw)

    def _debug_points(self) -> list[Vector2]:
        health_pixels, energy_shield_pixels, poison_pixel, mana_pixel, rage_pixel = self.game_controller.reader.pixels_to_be_read
        return [*health_pixels, *energy_shield_pixels, poison_pixel, mana_pixel, rage_pixel]

    def run_overlay(self):
        self._overlay_stop.clear()

        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        root.configure(bg="black")

        if os.name == "nt":
            root.attributes("-transparentcolor", "black")
        else:
            root.attributes("-alpha", 0.4)

        canvas = tk.Canvas(root, width=self.screen_w, height=self.screen_h, bg="black", highlightthickness=0)
        canvas.pack()
        self._overlay_canvas = canvas

        y = 0
        status_text = canvas.create_text(self.is_running_text_pos[0], self.is_running_text_pos[1], text="Paused", fill="white", anchor="sw", font=("Arial", 10, "bold"))
        frame_text = canvas.create_text(self.screen_w - 10, 10, text="", fill="white", anchor="ne", font=("Arial", 10, "bold"))

        def _poll():
            if self._overlay_stop.is_set():
                self._overlay_canvas = None
                root.destroy()
            else:
                if self.config.configData.draw_script_state_overlay:
                    canvas.itemconfig(status_text, text="Running" if self.running else "Paused")
                    if self.config.configData.debug:
                        canvas.itemconfig(frame_text, text=f"frame: {self.game_controller.frame}")
                    else:
                        canvas.itemconfig(frame_text, text="")
                    self.clear_debug_pixels()
                    self.draw_debug_pixels(self._debug_points())
                else:
                    canvas.itemconfig(status_text, text="")
                    canvas.itemconfig(frame_text, text="")
                    self.clear_debug_pixels()
                root.after(self.config.configData.check_screen_rate_ms, _poll)

        root.after(self.config.configData.check_screen_rate_ms, _poll)
        root.mainloop()

    def _open_config_editor(self, icon=None, item=None):
        def run():
            root = tk.Tk()
            root.title("Edit config.json")
            root.attributes("-topmost", True)

            text = tk.Text(root, width=80, height=30, wrap="none")
            text.pack(fill="both", expand=True)

            text.insert("1.0", self.config.to_text())

            def save():
                self.config.write_text(text.get("1.0", "end-1c"))
                self.config.load()
                self.configure(self.config)
                if self._on_config_change:
                    self._on_config_change()
                root.destroy()

            button_frame = tk.Frame(root)
            button_frame.pack(fill="x")
            tk.Button(button_frame, text="Save", command=save).pack(side="left")
            tk.Button(button_frame, text="Cancel", command=root.destroy).pack(side="left")

            root.mainloop()

        threading.Thread(target=run, daemon=True).start()

    def _create_tray_icon(self):
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # bottle body
        draw.rounded_rectangle((14, 28, 50, 60), radius=6, fill=(30, 100, 220), outline=(10, 60, 160), width=2)
        # bottle neck
        draw.rectangle((24, 14, 40, 30), fill=(30, 100, 220), outline=(10, 60, 160), width=2)
        # bottle cap
        draw.rounded_rectangle((20, 8, 44, 18), radius=3, fill=(10, 60, 160))
        # shine highlight
        draw.ellipse((18, 34, 26, 48), fill=(100, 180, 255, 120))
        return img

    def _tray_toggle(self, icon, item):
        self.toggle()
        icon.update_menu()

    def _tray_stop(self, icon, item):
        icon.stop()
        self.kill()

    def _toggle_label(self, item):
        hotkey = self.config.configData.hotkey_toggle
        return f"Pause({hotkey})" if self.running else f"Start({hotkey})"

    def _exit_label(self, item):
        return f"Exit({self.config.configData.hotkey_exit})"

    def run_tray(self):
        icon = pystray.Icon(
            "poe2-mana",
            self._create_tray_icon(),
            "POE2 Mana Bot",
            menu=pystray.Menu(
                pystray.MenuItem(self._toggle_label, self._tray_toggle),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Edit Config", self._open_config_editor),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(self._exit_label, self._tray_stop),
            ),
        )
        icon.run()