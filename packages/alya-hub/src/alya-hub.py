#!/usr/bin/env python3
import os, subprocess, sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

TAB_SETTINGS, TAB_SYSTEM, TAB_TOOLS, TAB_ABOUT = 0, 1, 2, 3

def power_action(action):
    cmds = {"shutdown":["systemctl","poweroff"],"reboot":["systemctl","reboot"],"suspend":["systemctl","suspend"]}
    if action in cmds:
        subprocess.Popen(cmds[action], start_new_session=True)

def get_sysinfo():
    try:
        import psutil
        return {
            "mem": f'{psutil.virtual_memory().used//1024//1024}MB / {psutil.virtual_memory().total//1024//1024}MB ({psutil.virtual_memory().percent}%)',
            "cpu": psutil.cpu_percent(interval=0.1),
            "disk": f'{psutil.disk_usage("/").used//1024//1024//1024}G / {psutil.disk_usage("/").total//1024//1024//1024}G ({psutil.disk_usage("/").percent}%)',
            "uptime": int(psutil.boot_time()),
        }
    except: return {}

class AlyaHub(Gtk.Window):
    def __init__(self, initial_tab=0):
        super().__init__(title="Alya Hub")
        self.set_default_size(780, 560)
        self.set_position(Gtk.WindowPosition.CENTER)
        self._setup_css()
        self._build_ui(initial_tab)
        self.connect("destroy", Gtk.main_quit)

    def _setup_css(self):
        css = """
        window { background-color: #1a1b26; }
        .sidebar { background-color: #16161e; }
        .sbtn { background: transparent; color: #565f89; border: none; padding: 12px 20px; font-size: 13px; }
        .sbtn:hover { background: #1f2030; color: #a9b1d6; }
        .sbtn:checked { background: #24283b; color: #7dcfff; border-left: 3px solid #7dcfff; }
        .hdr { color: #7dcfff; font-size: 16px; font-weight: bold; padding: 10px; }
        .lbl { color: #c0caf5; font-size: 13px; padding: 6px 0; }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(Gtk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _build_ui(self, initial_tab):
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sidebar.set_size_request(180, -1)
        sidebar.get_style_context().add_class("sidebar")

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        for name, w in [("settings",self._build_settings()),("system",self._build_system()),("tools",self._build_tools()),("about",self._build_about())]:
            self.stack.add_titled(w, name, name.capitalize())
        self.stack.set_visible_child_name(["settings","system","tools","about"][initial_tab])

        items = [("system-run","Settings","settings"),("computer","System Info","system"),("applications-utilities","Tools","tools"),("help-about","About","about")]
        group = None
        for i,(icon,label,name) in enumerate(items):
            btn = Gtk.RadioButton.new_with_label_from_widget(group, label)
            group = btn; btn.set_mode(False); btn.get_style_context().add_class("sbtn")
            btn.connect("toggled", lambda b,n=name: self.stack.set_visible_child_name(n) if b.get_active() else None)
            sidebar.pack_start(btn, False, False, 0)
            if i==initial_tab: btn.set_active(True)
        sidebar.pack_end(Gtk.Box(), True, True, 0)
        main_box.pack_start(sidebar, False, False, 0)
        main_box.pack_start(self.stack, True, True, 0)
        self.add(main_box)

    def _build_settings(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_start(30); vbox.set_margin_top(20)
        h = Gtk.Label(label="Settings"); h.get_style_context().add_class("hdr"); h.set_halign(Gtk.Align.START)
        vbox.pack_start(h, False, False, 0)
        for icon,label,action in [("system-shutdown","Shutdown","shutdown"),("system-reboot","Restart","reboot"),("system-suspend","Suspend","suspend")]:
            b = Gtk.Button(label="  "+label); b.set_image(Gtk.Image.new_from_icon_name(icon,Gtk.IconSize.BUTTON)); b.set_halign(Gtk.Align.START)
            b.connect("clicked", lambda _,a=action: power_action(a))
            vbox.pack_start(b, False, False, 3)
        return vbox

    def _build_system(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_start(30); vbox.set_margin_top(20)
        h = Gtk.Label(label="System Information"); h.get_style_context().add_class("hdr"); h.set_halign(Gtk.Align.START)
        vbox.pack_start(h, False, False, 0)
        info = get_sysinfo()
        for k,v in info.items():
            r = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            l = Gtk.Label(label=k+":"); l.get_style_context().add_class("lbl"); l.set_size_request(60,-1)
            r.pack_start(l,False,False,0); r.pack_start(Gtk.Label(label=str(v)),False,False,0)
            vbox.pack_start(r, False, False, 3)
        return vbox

    def _build_tools(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_start(30); vbox.set_margin_top(20)
        h = Gtk.Label(label="Tools"); h.get_style_context().add_class("hdr"); h.set_halign(Gtk.Align.START)
        vbox.pack_start(h, False, False, 0)
        for icon,label,cmd in [("utilities-terminal","Terminal","foot"),("system-file-manager","File Manager","pcmanfm-qt"),("network-wireless","Network","nm-connection-editor")]:
            b = Gtk.Button(label="  "+label); b.set_image(Gtk.Image.new_from_icon_name(icon,Gtk.IconSize.BUTTON)); b.set_halign(Gtk.Align.START)
            b.connect("clicked", lambda _,c=cmd: subprocess.Popen(c.split(),start_new_session=True))
            vbox.pack_start(b, False, False, 3)
        return vbox

    def _build_about(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_valign(Gtk.Align.CENTER); vbox.set_halign(Gtk.Align.CENTER)
        t = Gtk.Label(); t.set_markup('<span size="xx-large" weight="bold" color="#7dcfff">Alya OS</span>')
        vbox.pack_start(t,False,False,0)
        vbox.pack_start(Gtk.Label(label="Version 0.1 (Altay)"),False,False,0)
        vbox.pack_start(Gtk.Label(label="Portable AI & Minecraft Dev Environment"),False,False,0)
        vbox.pack_start(Gtk.Label(label="Based on CachyOS / Arch Linux"),False,False,0)
        return vbox

def main():
    tab = TAB_SETTINGS
    if len(sys.argv)>1:
        a = sys.argv[1].lower()
        if a in ("shutdown","poweroff"): power_action("shutdown"); return
        if a=="reboot": power_action("reboot"); return
        if a=="suspend": power_action("suspend"); return
        tab = {"settings":0,"system":1,"info":1,"tools":2,"about":3}.get(a,0)
    AlyaHub(tab).show_all(); Gtk.main()

if __name__=="__main__": main()
