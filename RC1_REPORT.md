# Alya OS — Release Candidate 1 Report

**Status:** ✅ All static validation passed. Ready for build validation on Arch Linux.

---

## 1. Architecture Summary

```
AlyaOS/
├── upstream/       124 files  — CachyOS-Live-ISO (git, READ-ONLY)
├── overlay/        14 files   — Alya changes (branding, configs, desktop)
├── patches/         1 file    — 01-efiboot-title.patch
├── packages/       25 files   — 4 custom PKGBUILDs
├── packages-alya.x86_64       — 40 package additions (appended)
├── assets/          3 files   — Canonical source (wallpaper, logo, icon-pack)
├── build.sh                   — 9-stage build pipeline
├── DEPENDENCIES.md            — Dependency documentation
├── ARCHITECTURE.md            — Architecture diagrams
├── BUILD_CHECKLIST.md         — Build validation checklist
└── RC1_REPORT.md              — This file
```

---

## 2. Overlay Statistics

| Metric | Value |
|--------|-------|
| Total overlay files | 14 |
| Files that override upstream | 7 (os-release, hostname, profiledef.sh, grub.cfg, 2× syslinux, splash.png) |
| New files (no upstream equivalent) | 7 (issue, ly.conf, labwc.desktop, lxqt.desktop, openbox.desktop, labwc/autostart, labwc/rc.xml) |
| Upstream files kept identical | 124 |
| Override ratio | 10/134 = 7.5% |

### Override Justification

| File | Why overlay, not package/patch |
|------|-------------------------------|
| `os-release` | Needed early in boot (initramfs level) |
| `hostname` | Trivial, no maintenance cost |
| `issue` | TTY banner, no upstream equivalent |
| `profiledef.sh` | ISO metadata (label, publisher); full file due to shell sourcing |
| `grub.cfg` | Complete rewrite (minified, restructured, entries modified) |
| `syslinux/*.cfg` | Title + label changes + structural (removed color lines, help text) |
| `airootfs/*` | All new files, no upstream conflict |
| `desktop/labwc/*` | All new files, no upstream conflict |

### Patch Statistics

| Patch | Lines Changed | Purpose |
|-------|--------------|---------|
| `01-efiboot-title.patch` | 3 (1 word each) | "CachyOS" → "Alya OS" in 3 UEFI systemd-boot entries |

---

## 3. Package Statistics

### Alya Additions (packages-alya.x86_64)

| Category | Count | Examples |
|----------|-------|---------|
| Wayland stack | ~15 | labwc, foot, waybar, mako, grim, slurp, swaybg, swaylock |
| Display Manager | 1 | ly |
| X11 fallback | 3 | picom, feh, nitrogen |
| Themes/Fonts | 3 | ttf-jetbrains-mono-nerd, papirus-icon-theme, xcursor-vanilla-dmz |
| Python GTK | 4 | python-gobject, python-cairo, python-psutil, python-dbus |
| AI tools | 3 | ollama, jdk21-openjdk, jdk21-openjdk-src |
| Minecraft | 4 | prismlauncher, gradle, maven, fernflower |
| Dev utilities | 3 | python-pillow, optipng, oxipng |
| Custom packages | 4 | alya-launcher, alya-hub, workspace-manager, alya-theme |
| **Total** | **40** | |

### Custom Package Quality

| Package | Depends | .INSTALL | LICENSE | backup | Source |
|---------|---------|----------|---------|--------|--------|
| alya-launcher | python, python-gobject, gtk3, python-cairo | ✅ Full hooks | ✅ MIT | ✅ | ✅ Local files |
| alya-hub | python, python-gobject, gtk3, python-psutil | ✅ Full hooks | ✅ MIT | ✅ | ✅ Local files |
| workspace-manager | python, python-gobject, gtk3 | ✅ Full hooks | ✅ MIT | ✅ | ✅ Local files |
| alya-theme | (none) | ✅ Full hooks | ✅ MIT | ✅ /etc/plymouth | ✅ Local files |

---

## 4. Build Pipeline

| Stage | Name | Description |
|-------|------|-------------|
| 1/9 | Validate | Check dependencies, host arch, upstream/ exists |
| 2/9 | Sync | `git pull` upstream CachyOS |
| 3/9 | Overlay | Copy upstream → build, apply overlay files |
| 4/9 | Branding | Inject os-release, hostname, issue, profiledef.sh, splash |
| 5/9 | Patch | Apply patches/01-efiboot-title.patch |
| 6/9 | Build Pkgs | Build 4 custom PKGBUILDs, create local repo |
| 7/9 | Merge | Append packages-alya.x86_64, deduplicate |
| 8/9 | Generate | `sudo mkarchiso`, rename to alya-os-*.iso |
| 9/9 | Report | Build report with stats, errors, warnings |

---

## 5. Known Limitations

### Limitation 1: Inconsistent LTS Kernel Entry (RESOLVED)
- **Fix**: Patch `01-efiboot-title.patch` expanded to cover all 3 UEFI entries — LTS, CachyOS, and fallback. All now show "Alya OS" title.
- **Remaining inconsistency**: LTS entry available in UEFI but absent from BIOS (GRUB). This is by design — GRUB overlay intentionally only has main + safe mode entries.
- **Impact**: LOW

### Limitation 2: PXE Boot Branding (UNCHANGED)
- **Status**: `archiso_pxe-linux.cfg` not overridden. PXE-booted sessions show "CachyOS".
- **Resolution**: Add overlay for `archiso_pxe-linux.cfg` if needed in future
- **Priority**: LOW (PXE boot is niche for live USB)

### Limitation 3: ISO Size
- **Estimated**: ~2.3-2.6 GB (CachyOS base ~1.8 GB + AI/MC tools ~500-800 MB)
- **Heaviest single package**: `ollama` (~400-800 MB)
- **Recommendation**: Consider moving AI tools to an optional `alya-ai` meta-package for users who want a smaller ISO
- **Priority**: MEDIUM (not blocking RC1)

### Limitation 3a: Launcher Path in Desktop Configs
- **Status**: RESOLVED
- **Fix**: `autostart` and `rc.xml` now use `/usr/bin/alya-launcher` (correct binary path) instead of `/usr/share/alya/launcher.py` (nonexistent path)
- **Impact**: Launcher now starts at session boot; Super+d keybinding works

### Limitation 4: .INSTALL Script Completeness
- **Status**: All 4 packages have full `.install` scripts with post_install/post_upgrade/pre_remove/post_remove hooks
- **Limitation**: The `alya-theme` post_install runs `gtk-update-icon-cache` but does not run `plymouth-set-default-theme`
- **Reason**: Plymouth theme is selected via `/etc/plymouth/plymouthd.defaults` which is tracked by `backup=()`
- **Impact**: First install requires plymouthd.defaults to be present (it is, from the package)

---

## 6. Remaining TODO

### Before RC1 Release
- [ ] Gate 6: Build validation on actual Arch/CachyOS (requires test environment)
- [ ] Verify ISO boots via USB (UEFI + BIOS)
- [ ] Test all custom packages install correctly
- [ ] Verify Wayland session starts with all autostart services

### Future Enhancements (post-RC1)
- [ ] Distinct application icons (currently all 5 icons are copies of the same source)
- [ ] PXE boot branding
- [ ] `alya-ai` optional meta-package for smaller ISO variant
- [ ] Installer/Calamares integration
- [ ] Automated testing pipeline
- [ ] Git repo initialization for AlyaOS itself

---

## 7. Quality Gates Summary

| Gate | Title | Status |
|------|-------|--------|
| 1 | Patch conversion | ✅ PASS — 1 patch created, 14 overlays kept |
| 2 | .INSTALL scripts | ✅ PASS — All 4 packages have full hooks |
| 3 | Dependency docs | ✅ PASS — DEPENDENCIES.md generated |
| 4 | Architecture diagrams | ✅ PASS — ARCHITECTURE.md generated |
| 5 | Maintainability audit | ✅ PASS — 0 blocking issues, all files verified |
| 6 | Build validation | ⏳ PENDING — Requires Arch Linux environment |
| 7 | RC Report | ✅ PASS — This document |

### Gate 5 Audit Results (Final)
- **4 PKGBUILDs**: All source files exist, all `install=` references correct, all `backup=()` arrays present (launcher ✅, hub ✅, ws-mgr ✅, theme ✅ `/etc/plymouth`)
- **14 overlay files**: All present and accounted for
- **1 patch**: `01-efiboot-title.patch` — correct format, targets existing upstream file
- **Desktop entries**: 3 `.desktop` files all use proper `/usr/bin/` Exec paths (no hardcoded `/usr/share/` paths)
- **`.INSTALL` scripts**: All 4 packages have all 4 hooks (post_install, post_upgrade, pre_remove, post_remove)
- **README**: No `sudo ./build.sh` commands; correct invocation is `./build.sh`
- **`profiledef.sh`**: Correct `buildmodes=('iso')`, matches upstream structure, only branding values differ
- **Duplicate assets**: 5 icon copies at 1.48MB each (expected — each package self-contained), 3 wallpaper/splash copies (canonical source in `assets/`)
- **`.gitignore`**: Created (ignores `out/`, `build/`, `__pycache__/`, etc.)

### Gate 6: Build Validation Instructions
To complete Gate 6, run on Arch Linux or CachyOS:

```bash
# Clean room procedure
cd /tmp
cp -r /path/to/AlyaOS /tmp/AlyaOS
cd AlyaOS
# Verify upstream exists at expected commit
git -C upstream checkout 33bbc02
sudo pacman -S --needed archiso xorriso squashfs-tools grub binutils base-devel
rm -rf build out work
./build.sh
```

Expected output: `out/alya-os-YYYY.MM.DD-x86_64.iso` (~2.3-2.6 GB)
Full procedure documented in `BUILD_CHECKLIST.md`.

**Overall: 6/7 gates passed (static). Gate 6 requires execution on Arch/CachyOS.**
