# Alya OS — Build Validation Checklist

## Prerequisites

### System Requirements
- **Arch Linux** or **CachyOS** (x86_64)
- **User**: non-root with `sudo` access (passwordless preferred for Stage 8)
- **Storage**: 15+ GB free space
- **Memory**: 4+ GB RAM (8+ GB recommended)
- **Network**: internet connection for `pacman` and `git fetch`

### Dependency Installation

```bash
# Core build tools
sudo pacman -S --needed archiso xorriso squashfs-tools grub binutils

# For custom package builds
sudo pacman -S --needed base-devel git

# For Alya live environment (not required on build host, but verify)
# These are installed INTO the ISO, not needed on host
```

### Source Code

```bash
# Option A: Fresh clone
git clone https://github.com/CachyOS/CachyOS-Live-ISO.git AlyaOS/upstream
cd AlyaOS

# Option B: Existing repo
cd AlyaOS
git -C upstream pull
```

---

## Build Steps

### Step 1: Clean Room Verification

Verify no cached/stale files:

```bash
# Check for build artifacts
ls -la build/ 2>/dev/null && echo "WARNING: build/ exists, remove first" || echo "OK: clean"

# Check for old ISOs
ls -la out/ 2>/dev/null

# Verify upstream integrity
git -C upstream status
git -C upstream log --oneline -1

# Verify no local modifications to overlay
git status 2>/dev/null || echo "Note: project not in git"
```

### Step 2: Dry Run — Validate Dependencies

```bash
# Run only Stage 1 to verify environment
./build.sh
# Press Ctrl+C after Stage 1 completes (or let it fail fast)
```

Expected output:
```
[1/9] Checking dependencies...
[OK] Environment validated
```

### Step 3: Full Build

```bash
./build.sh
```

Expected output:
```
[1/9] Validate Environment  →  [OK]
[2/9] Synchronize Upstream  →  [OK] Upstream at commit: <hash>
[3/9] Apply Overlay          →  [OK] Overlay applied
[4/9] Inject Branding        →  [OK] Branding injected
[5/9] Apply Patches          →  [OK] Patches applied: 1
[6/9] Build Alya Packages    →  [OK] Custom packages built: 4
[7/9] Merge Package Lists    →  [OK] Merged package list: ~240 packages
[8/9] Generate ISO           →  [OK] ISO generated: .../alya-os-<date>-x86_64.iso
[9/9] Generate Build Report  →  [OK] Build report: out/build-report.txt
```

---

## Build Output Verification

### ISO File

```bash
# Check ISO exists
ls -lh out/alya-os-*.iso

# Expected size: ~2.3-2.6 GB
# Verify SHA256
sha256sum out/alya-os-*.iso

# Check ISO label
isoinfo -d -i out/alya-os-*.iso | grep "Volume id"
# Expected: "ALYA_<YYYYMM>"

# Check ISO publisher
isoinfo -d -i out/alya-os-*.iso | grep "Publisher"
# Expected: "Alya OS <https://alya-os.org>"
```

### Build Report

```bash
cat out/build-report.txt
```

Verify these fields:
- `Alya Version: 0.1.0`
- `CachyOS Commit: <valid hash>`
- `Kernel: Linux version 6.x.x`
- `Total Packages: ~240`
- `Overlay Files: 14`
- `Branding Files: 5` (os-release, hostname, issue, profiledef.sh, splash.png)
- `Patches: 1`
- `Custom Packages: 4`
- `ISO Size: ~2.x GB`
- `Result: SUCCESS`

---

## Post-Build Verification

### Boot Test (VM)

```bash
# QEMU (UEFI)
qemu-system-x86_64 -enable-kvm -m 4096 -cpu host \
  -drive if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.4m.fd \
  -cdrom out/alya-os-YYYY.MM.DD-x86_64.iso

# QEMU (BIOS)
qemu-system-x86_64 -enable-kvm -m 4096 -cpu host \
  -cdrom out/alya-os-YYYY.MM.DD-x86_64.iso
```

### Boot Verification Checklist

- [ ] BIOS boot: syslinux shows "Alya OS" menu
- [ ] UEFI boot: systemd-boot shows "Alya OS" entry
- [ ] GRUB fallback: shows "Alya OS" and "Alya OS (Safe Mode)" entries
- [ ] Plymouth splash: shows "Alya OS" with animated progress bar
- [ ] ly display manager: auto-login as `alya` user
- [ ] Wayland session: labwc desktop with Tokyo Night theme
- [ ] Wallpaper: Alya OS default wallpaper displayed
- [ ] Waybar: status bar visible
- [ ] Foot terminal: working
- [ ] Alya Launcher: `Super+d` opens launcher
- [ ] Workspaces: `Super+1-5` switches between named workspaces
- [ ] AI tools: `ollama --version`, `java --version` work
- [ ] Minecraft: `prismlauncher --version` works

---

## Common Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `makepkg` fails as root | Running `sudo ./build.sh` | Run `./build.sh` (no sudo) |
| `grub-mkrescue: command not found` | Missing `grub` package | `sudo pacman -S grub` |
| `mkarchiso: command not found` | Missing `archiso` package | `sudo pacman -S archiso` |
| ISO labeled `COS_*` instead of `ALYA_*` | profiledef.sh not copied | Verify Stage 4 copies `branding/profiledef.sh` |
| LTS kernel entry in UEFI but not GRUB | Known inconsistency | Documented in RC1 report |
| PXE boot shows "CachyOS" | archiso_pxe-linux.cfg not overridden | Documented as out-of-scope |
| Large ISO (~2.6 GB) | ollama + jdk21 + prismlauncher | Expected, see DEPENDENCIES.md |
