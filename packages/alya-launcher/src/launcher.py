#!/usr/bin/env python3
import json, os, subprocess, sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

CONFIG_PATH = os.path.expanduser("~/.config/alya/launcher.json")
SYSTEM_CONFIG_PATH = "/usr/share/alya/launcher.json"

DEFAULT_CONFIG = {
    "buttons": [
        {"label": "AI",         "icon": "accessories-text-editor",  "command": "foot bash -c 'echo AI Environment; exec bash'",       "color": "#7dcfff"},
        {"label": "Development","icon": "applications-engineering","command": "code",                                                 "color": "#bb9af7"},
        {"label": "Minecraft",  "icon": "applications-games",      "command": "prismlauncher",                                        "color": "#f7768e"},
        {"label": "Workspace",  "icon": "folder",                   "command": "workspace-manager",                                   "color": "#9ece6a"},
        {"label": "Terminal",   "icon": "utilities-terminal",       "command": "foot",                                                "color": "#e0af68"},
        {"label": "Browser",    "icon": "web-browser",              "command": "firefox",                                             "color": "#2ac3de"},
        {"label": "Settings",   "icon": "preferences-system",       "command": "alya-hub settings",                                   "color": "#565f89"},
        {"label": "Shutdown",   "icon": "system-shutdown",          "command": "alya-hub power",                                      "color": "#414868"},
    ],
    "columns": 4, "spacing": 20, "show_clock": True, "show_system_info": True,
}

def load_config():
    config = dict(DEFAULT_CONFIG)
    for path in (SYSTEM_CONFIG_PATH, CONFIG_PATH):
        try:
            with open(path) as f:
                user_cfg = json.load(f)
                for key, value in user_cfg.items():
                    if key == "buttons":
                        for i, btn in enumerate(value):
                            if i < len(config["buttons"]):
                                config["buttons"][i].update(btn)
                            else:
                                config["buttons"].append(btn)
                    else:
                        config[key] = value
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    return config

class LauncherButton(Gtk.EventBox):
    def __init__(self, btn_config, parent):
        super().__init__()
        self.btn_config = btn_config
        self.parent = parent
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.box.set_valign(Gtk.Align.CENTER)
        self.box.set_halign(Gtk.Align.CENTER)
        self.add(self.box)
        self.icon = Gtk.Image.new_from_icon_name(btn_config["icon"], Gtk.IconSize.DIALOG)
        self.icon.set_pixel_size(48)
        self.box.pack_start(self.icon, False, False, 0)
        self.label = Gtk.Label(label=btn_config["label"])
        self.box.pack_start(self.label, False, False, 0)
        self._add_css(btn_config["color"])
        self.connect("button-press-event", self.on_click)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)

    def _add_css(self, color):
        rgb = color.lstrip("#")
        r, g, b = int(rgb[0:2],16), int(rgb[2:4],16), int(rgb[4:6],16)
        css = f"""
        .launcher-btn {{
            background-color: rgba(0,0,0,0.3);
            border: 2px solid {color};
            border-radius: 12px; padding: 16px; margin: 4px;
        }}
        .launcher-btn:hover {{
            background-color: rgba({r},{g},{b},0.2);
            box-shadow: 0 0 20px rgba({r},{g},{b},0.3);
        }}
        .launcher-btn label {{ color: #c0caf5; font-size: 13px; font-weight: bold; }}
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider(self.get_style_context(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.get_style_context().add_class("launcher-btn")

    def on_click(self, widget, event):
        subprocess.Popen(self.btn_config["command"], shell=True, start_new_session=True)
        self.parent.hide_launcher()

class AlyaLauncher(Gtk.Window):
    def __init__(self, config):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.config = config
        self.set_title("Alya OS Launcher")
        self.set_decorated(False)
        self.set_keep_above(True)
        screen = Gdk.Screen.get_default()
        monitor = screen.get_monitor_geometry(screen.get_primary_monitor())
        self.set_size_request(monitor.width, monitor.height)
        self.move(monitor.x, monitor.y)
        self.set_app_paintable(True)
        self._setup_css()
        self._build_ui()
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", Gtk.main_quit)

    def _setup_css(self):
        css = "window { background: linear-gradient(135deg, #1a1b26, #24283b, #1a1b26); }"
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _build_ui(self):
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        title = Gtk.Label(label="Alya OS")
        title.set_markup('<span size="xx-large" weight="bold" color="#7dcfff">Alya OS</span>')
        self.vbox.pack_start(Gtk.Box(), True, True, 0)
        self.vbox.pack_start(title, False, False, 10)
        subtitle = Gtk.Label(label="Portable Development Environment")
        subtitle.set_markup('<span color="#565f89">Portable Development Environment</span>')
        self.vbox.pack_start(subtitle, False, False, 0)
        self.vbox.pack_start(self._build_buttons(), False, False, 60)
        self.vbox.pack_end(Gtk.Box(), True, True, 0)
        self.add(self.vbox)

    def _build_buttons(self):
        grid = Gtk.Grid()
        grid.set_row_spacing(self.config["spacing"])
        grid.set_column_spacing(self.config["spacing"])
        grid.set_halign(Gtk.Align.CENTER)
        cols = self.config["columns"]
        for i, btn_cfg in enumerate(self.config["buttons"]):
            grid.attach(LauncherButton(btn_cfg, self), i % cols, i // cols, 1, 1)
        return grid

    def on_key_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname in ("Escape", "q", "Q"):
            self.hide_launcher()
        return True

    def hide_launcher(self):
        self.hide()
        Gtk.main_quit()

    def show_launcher(self):
        self.fullscreen()
        self.show_all()
        self.present()

if __name__ == "__main__":
    AlyaLauncher(load_config()).show_launcher()
    Gtk.main()
