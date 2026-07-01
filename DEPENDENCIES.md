# Alya OS — Package Dependency Documentation

## Upstream (CachyOS) Base Packages

**Source:** `upstream/archiso/packages_desktop.x86_64`  
**Count:** 200 packages  
**Coverage:** KDE Plasma, CachyOS kernels (linux-cachyos, linux-cachyos-lts, -zfs, -nvidia-open), firmware, pipewire, NetworkManager, bluetooth, printing, virtualization tools, filesystem tools, ZFS

Unchanged from CachyOS upstream.

---

## Alya Additions (packages-alya.x86_64)

**Count:** 40 packages appended to upstream list.

### Category Breakdown

### 1. Display Manager & Session

| Package | Type | Dependencies | Purpose |
|---------|------|-------------|---------|
| `ly` | DM | (minimal) | TUI display manager, auto-login as `alya` user |
| `labwc` | WM | wlroots, wayland | Wayland stacking compositor |
| `wlroots` | lib | wayland | Wayland compositor library |
| `wayland` | lib | — | Wayland protocol |
| `wayland-utils` | util | wayland | Wayland info tools |

### 2. Wayland Desktop Apps

| Package | Type | Dependencies | Purpose |
|---------|------|-------------|---------|
| `foot` | terminal | wayland | Wayland-native terminal emulator |
| `swaybg` | util | wayland | Wallpaper setter for Wayland |
| `swaylock` | util | wayland | Screen locker |
| `waybar` | panel | wayland | Wayland status bar |
| `mako` | daemon | wayland | Notification daemon |
| `polkit-gnome` | auth | polkit | PolicyKit authentication agent |
| `imv` | viewer | wayland | Image viewer |
| `grim` | util | wayland | Screenshot tool |
| `slurp` | util | wayland | Region selection |
| `swappy` | util | grim, slurp | Screenshot editor |
| `wl-clipboard` | util | wayland | Clipboard manager |

### 3. X11 Fallback

| Package | Type | Dependencies | Purpose |
|---------|------|-------------|---------|
| `picom` | compositor | X11 | X11 compositor (vsync, transparency) |
| `feh` | viewer | X11 | Image viewer / wallpaper setter |
| `nitrogen` | util | X11 | Wallpaper browser/setter |

### 4. Themes & Fonts

| Package | Type | Dependencies | Purpose |
|---------|------|-------------|---------|
| `ttf-jetbrains-mono-nerd` | font | — | Monospace font with Nerd Font patches |
| `xcursor-vanilla-dmz` | theme | — | Cursor theme |
| `papirus-icon-theme` | theme | — | Icon theme (GTK, Qt, others) |

### 5. Python GTK (Alya Custom Tools Runtime)

| Package | Type | Dependencies | Purpose |
|---------|------|-------------|---------|
| `python-gobject` | lib | python, glib, gtk3 | Python GTK bindings |
| `python-cairo` | lib | python, cairo | Python Cairo bindings |
| `python-psutil` | lib | python | System/process utilities |
| `python-dbus` | lib | python, dbus | Python D-Bus bindings |

### 6. AI Development

| Package | Type | Dependencies | Purpose |
|---------|------|-------------|---------|
| `ollama` | app | — | Local LLM runtime (heaviest package ~500MB) |
| `jdk21-openjdk` | sdk | — | Java 21 Development Kit |
| `jdk21-openjdk-src` | sdk | — | Java 21 source code |

### 7. Minecraft Development

| Package | Type | Dependencies | Purpose |
|---------|------|-------------|---------|
| `prismlauncher` | app | java-runtime | Minecraft launcher with mod support |
| `gradle` | build | java-runtime | Build automation (Minecraft mods) |
| `maven` | build | java-runtime | Build automation (Minecraft mods) |
| `fernflower` | util | java-runtime | Java decompiler |

### 8. Development Utilities

| Package | Type | Dependencies | Purpose |
|---------|------|-------------|---------|
| `python-pillow` | lib | python | Image processing (launcher screenshots) |
| `optipng` | util | — | PNG optimizer |
| `oxipng` | util | — | Rust-based PNG optimizer |

---

## Custom Alya Packages (4 PKGBUILDs)

### alya-launcher

| Field | Value |
|-------|-------|
| **Provides** | `alya-launcher` |
| **Conflicts** | none |
| **Depends** | `python`, `python-gobject`, `gtk3`, `python-cairo` |
| **OptDepends** | none |
| **Required by** | `labwc/autostart` and `rc.xml` at `/usr/bin/alya-launcher` |
| **Files** | `/usr/bin/alya-launcher`, `/usr/share/alya/launcher.json`, `/usr/share/applications/alya-launcher.desktop`, `/usr/share/pixmaps/alya-launcher.png` |

### alya-hub

| Field | Value |
|-------|-------|
| **Provides** | `alya-hub` |
| **Conflicts** | none |
| **Depends** | `python`, `python-gobject`, `gtk3`, `python-psutil` |
| **OptDepends** | none |
| **Required by** | (user-launched, no autostart) |
| **Files** | `/usr/bin/alya-hub`, `/usr/share/applications/alya-hub.desktop`, `/usr/share/pixmaps/alya-hub.png` |

### workspace-manager

| Field | Value |
|-------|-------|
| **Provides** | `workspace-manager` |
| **Conflicts** | none |
| **Depends** | `python`, `python-gobject`, `gtk3` |
| **OptDepends** | none |
| **Required by** | (user-launched, no autostart) |
| **Files** | `/usr/bin/workspace-manager`, `/usr/share/applications/workspace-manager.desktop`, `/usr/share/pixmaps/workspace-manager.png` |

### alya-theme

| Field | Value |
|-------|-------|
| **Provides** | `alya-theme` |
| **Conflicts** | none |
| **Depends** | none |
| **OptDepends** | `plymouth` (for boot splash), `labwc` (for GTK theme) |
| **Required by** | (leaf package, no reverse deps) |
| **Files** | See `packages/alya-theme/PKGBUILD` |

---

## Reverse Dependency Map

```
alya-theme (no deps, no rdeps)
  └─ [leaf package]

alya-launcher
  ├─ depends: python, python-gobject, gtk3, python-cairo
  └─ required by: labwc/autostart (runtime, not pkgsrc)

alya-hub
  ├─ depends: python, python-gobject, gtk3, python-psutil
  └─ required by: (none - user-launched)

workspace-manager
  ├─ depends: python, python-gobject, gtk3
  └─ required by: (none - user-launched)
```

---

## Upstream-Alya Duplicate Check

| Check | Result |
|-------|--------|
| Package overlap upstream ↔ Alya | **NONE** — 0 packages duplicated |
| Upstream count | 200 packages |
| Alya additions count | 40 packages |
| Total merged | 240 packages (unique) |

---

## ISO Size Estimates by Dependency Group

| Group | Packages | Est. ISO Impact |
|-------|----------|-----------------|
| Wayland stack (labwc, wlroots, foot, etc.) | ~15 | +80 MB |
| Python GTK stack | ~5 | +20 MB |
| AI tools (ollama, jdk21, gradle, maven) | ~6 | +800-1200 MB |
| Minecraft (prismlauncher, fernflower) | ~3 | +200 MB |
| Themes, fonts, cursors | ~4 | +30 MB |
| Custom packages (4 PKGBUILDs) | 4 | +5 MB |
| **Total Alya additions** | **40** | **~+500-800 MB** |
