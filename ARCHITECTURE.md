# Alya OS — Architecture

## 1. Overlay Hierarchy

```
AlyaOS/overlay/
├── branding/           # ISO identity and metadata
│   ├── os-release      ──►  archiso/airootfs/etc/os-release
│   ├── hostname        ──►  archiso/airootfs/etc/hostname
│   ├── issue           ──►  archiso/airootfs/etc/issue  (new file, no upstream)
│   ├── profiledef.sh   ──►  archiso/profiledef.sh       (ISO label, publisher)
│   └── grub/
│       └── splash.png  ──►  archiso/grub/splash.png
│
├── airootfs/           # Live-session filesystem additions
│   ├── etc/ly/ly.conf  ──►  archiso/airootfs/etc/ly/ly.conf
│   └── usr/share/
│       ├── wayland-sessions/labwc.desktop
│       └── xsessions/{lxqt,openbox}.desktop
│
├── desktop/            # Window manager configs (injected into skel)
│   └── labwc/
│       ├── autostart   ──►  /etc/skel/.config/labwc/autostart
│       └── rc.xml      ──►  /etc/skel/.config/labwc/rc.xml
│
├── grub/
│   └── grub.cfg        ──►  archiso/grub/grub.cfg  (Alya-branded, minified)
│
└── syslinux/
    ├── archiso_head.cfg     ──►  archiso/syslinux/archiso_head.cfg
    └── archiso_sys-linux.cfg ──►  archiso/syslinux/archiso_sys-linux.cfg
```

### Override Strategy

| Strategy | Count | Files |
|----------|-------|-------|
| **Full overlay** (structural changes) | 14 | All files in `overlay/` |
| **Patch** (text-only changes) | 1 | `01-efiboot-title.patch` (3 files, 1 word each) |
| **No override** (upstream as-is) | ~124 | Kernel, initramfs, drivers, firmware, pacman.conf, buildiso.sh |

### New Files (no upstream equivalent)

| File | Purpose |
|------|---------|
| `overlay/branding/issue` | TTY login banner |
| `overlay/airootfs/etc/ly/ly.conf` | Ly DM config with auto-login, Tokyo Night theme |
| `overlay/airootfs/usr/share/wayland-sessions/labwc.desktop` | Labwc Wayland session |
| `overlay/airootfs/usr/share/xsessions/openbox.desktop` | Openbox X11 session |
| `overlay/airootfs/usr/share/xsessions/lxqt.desktop` | LXQt X11 session |
| `overlay/desktop/labwc/autostart` | Labwc autostart (swaybg, waybar, mako, launcher) |
| `overlay/desktop/labwc/rc.xml` | Labwc keybindings, theme, workspaces |

---

## 2. Package Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                   packages-alya.x86_64                   │
│              (appended to upstream list,                 │
│               deduplicated at build time)                │
└─────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────────┐   ┌──────────────┐
│ Wayland Stack │   │  Python GTK Stack  │   │ AI/MC Stack │
│  labwc        │   │  python-gobject    │   │  ollama     │
│  wlroots      │   │  python-cairo      │   │  jdk21      │
│  foot         │   │  python-psutil     │   │  prismlnchr │
│  waybar       │   │  python-dbus       │   │  gradle     │
│  mako         │   │                    │   │  maven      │
│  grim/slurp   │   │                    │   └──────────────┘
│  wl-clipboard │   │                    │
└───────────────┘   └───────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────────────────────────────────────────────┐
│               Custom Alya Packages (4)                   │
│                                                          │
│  alya-launcher ── depends ──► python-gobject, gtk3       │
│  alya-hub      ── depends ──► python-gobject, psutil     │
│  workspace-mgr ── depends ──► python-gobject, gtk3       │
│  alya-theme    ── depends ──► (none, leaf package)       │
└─────────────────────────────────────────────────────────┘
```

### Package Dependency Flow

```
                    ┌──────────────┐
                    │  alya-theme  │  (GTK theme, wallpapers, plymouth, icons)
                    └──────┬───────┘
                           │ (provides icons/themes at runtime)
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
    ┌────────────┐ ┌────────────┐ ┌──────────────┐
    │ala-launcher│ │ alya-hub   │ │ws-manager    │
    │dep: python │ │dep: python │ │dep: python   │
    │    pygobject│ │    pygobject│ │    pygobject │
    │    gtk3    │ │    gtk3    │ │    gtk3      │
    │    pycairo │ │    psutil  │ │              │
    └────────────┘ └────────────┘ └──────────────┘
```

---

## 3. Boot Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Alya OS Boot Sequence                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  FIRMWARE ──► BOOTLOADER ──► KERNEL ──► INITRAMFS ──► DISPLAY MGR ──► DESKTOP │
│                                                                      │
│  UEFI ─────────┐                                                     │
│   ├─ systemd-boot ──► vmlinuz-linux-cachyos                          │
│   │   [Alya OS]      + initramfs-linux-cachyos.img                   │
│   │                                                                  │
│  BIOS ─────────┐                                                     │
│   └─ syslinux ────┤                                                  │
│     [alya64]      │                                                  │
│                   ▼                                                  │
│    ┌─────────────────────────────┐                                   │
│    │      GRUB (fallback)        │                                   │
│    │  [Alya OS / Safe Mode]      │                                   │
│    └─────────────┬───────────────┘                                   │
│                  │                                                    │
│                  ▼                                                    │
│    ┌─────────────────────────────┐                                   │
│    │       Kernel Boot           │                                   │
│    │  cow_spacesize=10G          │                                   │
│    │  copytoram=auto             │                                   │
│    └─────────────┬───────────────┘                                   │
│                  │                                                    │
│                  ▼                                                    │
│    ┌─────────────────────────────┐                                   │
│    │       initramfs             │                                   │
│    │  archiso hooks: base, udev, │                                   │
│    │  microcode, memdisk, archiso│                                   │
│    │  _loop_mnt, _pxe_*          │                                   │
│    │  block, filesystems, keyboard│                                  │
│    └─────────────┬───────────────┘                                   │
│                  │                                                    │
│                  ▼                                                    │
│    ┌─────────────────────────────┐                                   │
│    │     plymouth (Alya theme)   │                                   │
│    │  "Starting Alya OS..."      │                                   │
│    │  with animated progress bar │                                   │
│    └─────────────┬───────────────┘                                   │
│                  │                                                    │
│                  ▼                                                    │
│    ┌─────────────────────────────┐                                   │
│    │    Display Manager (ly)     │                                   │
│    │  auto_login = alya          │                                   │
│    │  session  = labwc (Wayland) │                                   │
│    │  fallback = openbox (X11)   │                                   │
│    └─────────────┬───────────────┘                                   │
│                  │                                                    │
│                  ▼                                                    │
│    ┌─────────────────────────────┐                                   │
│    │      labwc (Wayland)        │                                   │
│    │  see "Desktop Startup Flow" │                                   │
│    └─────────────────────────────┘                                   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 4. Desktop Startup Flow

```
ly (display manager)
  │
  └─► labwc-session
       │
       ├─► ~/.config/labwc/autostart
       │    │
       │    ├─► swaybg           # Set Alya OS wallpaper
       │    ├─► /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1
       │    ├─► mako             # Notification daemon
       │    ├─► waybar           # Status bar
       │    ├─► nm-applet        # NetworkManager applet
       │    ├─► /usr/bin/alya-launcher  # Alya full-screen launcher
       │    └─► xfce4-power-manager     # Power management
       │
       └─► ~/.config/labwc/rc.xml
            │
            ├─► Theme: Alya-Dark (alya-dark.css)
            ├─► Font: JetBrains Mono Nerd (10px)
            ├─► Corner radius: 6px
            │
            ├─► Keybindings:
            │    ├─► Super+Return → foot (terminal)
            │    ├─► Super+d      → alya-launcher
            │    ├─► Super+q      → close window
            │    ├─► Super+f      → toggle fullscreen
            │    ├─► Super+Tab    → cycle windows
            │    ├─► Super+1..5   → switch workspace
            │    └─► Alt+Tab      → next window
            │
            └─► Workspaces:
                 ├─► 1: Terminal
                 ├─► 2: Development
                 ├─► 3: AI
                 ├─► 4: Minecraft
                 └─► 5: Web
```

---

## 5. Build Pipeline (9 Stages)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Alya OS Build Pipeline                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  STAGE 1: VALIDATE                                                      │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ Check: mkarchiso, pacman, xorriso, mksquashfs, grub-mkrescue│       │
│  │ Check: x86_64 host, upstream/.git exists                     │       │
│  └──────────┬──────────────────────────────────────────────────┘       │
│             │ PASS                                                     │
│             ▼                                                          │
│  STAGE 2: SYNC                                                         │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ git fetch origin; git reset --hard origin/<default branch>   │       │
│  │ CACHYOS_COMMIT=$(git rev-parse HEAD)                         │       │
│  └──────────┬──────────────────────────────────────────────────┘       │
│             │ PASS                                                     │
│             ▼                                                          │
│  STAGE 3: OVERLAY                                                      │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ cp -r upstream/archiso/ → build/archiso/                    │       │
│  │ Apply: grub.cfg, syslinux/*, airootfs/*, desktop/labwc/*    │       │
│  └──────────┬──────────────────────────────────────────────────┘       │
│             │ PASS                                                     │
│             ▼                                                          │
│  STAGE 4: BRANDING                                                     │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ Inject: os-release, hostname, issue, profiledef.sh          │       │
│  │ Inject: GRUB splash.png                                      │       │
│  └──────────┬──────────────────────────────────────────────────┘       │
│             │ PASS                                                     │
│             ▼                                                          │
│  STAGE 5: PATCH                                                       │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ Apply patches/*.patch: 01-efiboot-title.patch                │       │
│  │ patch -p1 < patches/*.patch                                   │       │
│  └──────────┬──────────────────────────────────────────────────┘       │
│             │ PASS                                                     │
│             ▼                                                          │
│  STAGE 6: BUILD PACKAGES                                               │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ For each package/ directory with PKGBUILD:                  │       │
│  │   makepkg -sc --noconfirm --needed                           │       │
│  │ Create local repo: repo-add alya-os.db.tar.gz               │       │
│  └──────────┬──────────────────────────────────────────────────┘       │
│             │ PASS                                                     │
│             ▼                                                          │
│  STAGE 7: MERGE PACKAGES                                               │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ Copy upstream packages_desktop.x86_64 → merged               │       │
│  │ Append packages-alya.x86_64 (removing blanks/comments)       │       │
│  │ sort -u (deduplicate)                                         │       │
│  └──────────┬──────────────────────────────────────────────────┘       │
│             │ PASS                                                     │
│             ▼                                                          │
│  STAGE 8: GENERATE ISO                                                  │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ sudo mkarchiso -w build/work -o out/ build/archiso           │       │
│  │ Rename: cachyos-*.iso → alya-os-YYYY.MM.DD-x86_64.iso       │       │
│  └──────────┬──────────────────────────────────────────────────┘       │
│             │ PASS                                                     │
│             ▼                                                          │
│  STAGE 9: REPORT                                                       │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ Generate: out/build-report.txt                               │       │
│  │ ISO size, SHA256, build duration, kernel version,            │       │
│  │ overlay files, patches, packages, errors, warnings           │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Project Statistics (Post-Quality-Gate)

| Metric | Value |
|--------|-------|
| Upstream files | 124 |
| Overlay files | 14 |
| Patch files | 1 (covering 3 upstream files) |
| Custom packages | 4 (25 files) |
| Assets (canonical) | 3 |
| Files differing from upstream | 15 (14 overlay + 1 patch affecting 3 files) |
| Upstream identical | 124 |
