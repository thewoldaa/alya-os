# Alya OS

**Alya OS** is a downstream customization of **CachyOS** — like Linux Mint is to Ubuntu.

Focused on portable AI Development and Minecraft Mod Development.

## Architecture

```
AlyaOS/
├── upstream/              ← CachyOS-Live-ISO (READ-ONLY, source of truth)
├── overlay/
│   ├── branding/          ← os-release, hostname, issue, profiledef.sh, grub splash
│   ├── airootfs/          ← ly.conf, labwc/lxqt/openbox session files
│   ├── desktop/           ← labwc autostart and rc.xml config
│   ├── grub/              ← grub.cfg (Alya OS boot menu)
│   └── syslinux/          ← BIOS boot menu configs
├── packages/              ← 4 custom PKGBUILDs (alya-{launcher,hub,theme}, workspace-manager)
├── packages-alya.x86_64   ← 40 package additions (appended to CachyOS list)
├── patches/               ← 01-efiboot-title.patch (UEFI boot title branding)
└── assets/                ← Canonical source: wallpapers, icons, icon-pack
```

## Build (on Arch/CachyOS)

```bash
sudo pacman -S archiso xorriso squashfs-tools grub binutils
git clone https://github.com/alya-os/alya-os
cd AlyaOS
./build.sh
```

Output: `out/alya-os-YYYY.MM.DD-x86_64.iso`

**Note:** Do NOT run `sudo ./build.sh` — the script calls `sudo` internally only for `mkarchiso` (Stage 8). Running as root would break `makepkg` (Stage 6).

## Upstream Compatibility

**Files that differ from upstream (15):**
- 14 overlay files: os-release, hostname, issue, profiledef.sh, splash.png, grub.cfg, 2× syslinux, ly.conf, 3× session .desktop, labwc autostart, labwc rc.xml
- 1 patch: 01-efiboot-title.patch (UEFI boot titles, 3 files)

**Assets provided by packages, not overlay:** wallpapers, icons, plymouth theme (all in `alya-theme` package).

**Everything else (124+ files)** is identical to CachyOS.

Updating: `cd upstream && git pull && cd .. && ./build.sh`
