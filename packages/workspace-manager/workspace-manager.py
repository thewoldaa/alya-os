#!/usr/bin/env python3
import argparse, json, os, subprocess, sys
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

CONFIG_DIR = os.path.expanduser("~/.config/alya")
CONFIG_PATH = os.path.join(CONFIG_DIR, "workspaces.json")

DEFAULT = {
    "workspaces": {
        "AI": {"path": os.path.expanduser("~/workspace/ai"), "type":"ai","description":"AI projects and models"},
        "Minecraft": {"path": os.path.expanduser("~/workspace/minecraft"), "type":"minecraft","description":"Minecraft mods and resource packs"},
        "Projects": {"path": os.path.expanduser("~/workspace/projects"), "type":"general","description":"Development projects"},
        "Downloads": {"path": os.path.expanduser("~/workspace/downloads"), "type":"general","description":"Download files"},
    },
    "mounts":[], "symlinks":[]
}

def load():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        save(DEFAULT); return dict(DEFAULT)
    try:
        with open(CONFIG_PATH) as f: return json.load(f)
    except: return dict(DEFAULT)

def save(data):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f: json.dump(data, f, indent=2)

def create_workspace(name, path, desc=""):
    d = load()
    os.makedirs(path, exist_ok=True)
    d["workspaces"][name] = {"path":os.path.abspath(path),"type":"general","description":desc}
    save(d)
    return d["workspaces"][name]

def detect_windows():
    r = subprocess.run(["lsblk","-o","NAME,SIZE,FSTYPE,LABEL","-n","-l"], capture_output=True, text=True)
    parts = []
    for line in r.stdout.strip().split("\n"):
        p = line.split()
        if len(p)>=3 and p[2] in ("ntfs","vfat"):
            parts.append({"device":f"/dev/{p[0]}","size":p[1],"fstype":p[2],"label":p[3] if len(p)>3 else ""})
    return parts

class WorkspaceGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Alya Workspace Manager")
        self.set_default_size(700,500); self.set_position(Gtk.WindowPosition.CENTER)
        self.data = load()
        css = "window{background:#1a1b26} .wn{color:#c0caf5;font-size:14px;font-weight:bold} .wp{color:#565f89;font-size:11px}"
        provider = Gtk.CssProvider(); provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(Gtk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self._build_ui()
        self.connect("destroy", Gtk.main_quit)

    def _build_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_start(20); vbox.set_margin_end(20); vbox.set_margin_top(20)
        h = Gtk.Label(label="Workspaces"); h.set_markup('<span color="#7dcfff" size="large" weight="bold">Workspaces</span>')
        vbox.pack_start(h, False, False, 0)
        for name, ws in self.data.get("workspaces",{}).items():
            f = Gtk.Frame(); f.set_margin_bottom(6)
            b = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            b.set_margin_start(10); b.set_margin_end(10); b.set_margin_top(6); b.set_margin_bottom(6)
            ib = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            nl = Gtk.Label(label=name); nl.get_style_context().add_class("wn"); nl.set_halign(Gtk.Align.START)
            pl = Gtk.Label(label=ws["path"]); pl.get_style_context().add_class("wp"); pl.set_halign(Gtk.Align.START)
            ib.pack_start(nl,False,False,0); ib.pack_start(pl,False,False,0)
            b.pack_start(ib,True,True,0)
            o = Gtk.Button(label="Open")
            o.connect("clicked", lambda _,p=ws["path"]: subprocess.Popen(["pcmanfm-qt",p],start_new_session=True))
            b.pack_end(o,False,False,0)
            f.add(b); vbox.pack_start(f, False, False, 0)
        self.add(vbox)

def cli():
    p = argparse.ArgumentParser(description="Alya OS Workspace Manager")
    p.add_argument("--list", action="store_true")
    p.add_argument("--create", nargs=2, metavar=("NAME","PATH"))
    p.add_argument("--detect", action="store_true")
    p.add_argument("--gui", action="store_true")
    args = p.parse_args()
    if args.gui or len(sys.argv)==1:
        WorkspaceGUI().show_all(); Gtk.main(); return
    if args.list:
        for n,ws in load().get("workspaces",{}).items(): print(f"{n}: {ws['path']}")
    if args.create:
        ws = create_workspace(args.create[0], args.create[1]); print(f"Created {ws}")
    if args.detect:
        for p in detect_windows(): print(f"{p['device']}: {p.get('label','')}")

if __name__=="__main__": cli()
