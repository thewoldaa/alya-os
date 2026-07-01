# Alya OS RC1 — Build & Validation Guide

## Prerequisites

- **OS**: Arch Linux or CachyOS (x86_64)
- **Packages**: `sudo pacman -S --needed archiso xorriso squashfs-tools grub binutils base-devel`
- **Disk**: At least 10 GB free

## 1. Clean Room Build

```bash
# Place AlyaOS project and verify structure
cd /tmp
# Copy or clone AlyaOS project (with upstream/ at commit 33bbc02)
cd AlyaOS

# Initialize upstream (if not already present)
git clone https://github.com/CachyOS/CachyOS-Live-ISO.git upstream
# or: git -C upstream pull  # if already cloned

# Remove any stale artifacts
rm -rf build out work

# Execute build
./build.sh
```

Expected result: `SUCCESS` in final output. ISO at `out/alya-os-YYYY.MM.DD-x86_64.iso`.

## 2. Build Log

Record the following after a successful or failed build:

```
Build Date:       <date>
Alya Version:     0.1.0
CachyOS Commit:   <from report>
Kernel:           <from report>
Total Packages:   <from report>
Overlay Files:    14
Branding Files:   <from report>
Patches:          1
Custom Packages:  4 (alya-launcher alya-hub workspace-manager alya-theme)

ISO Size:         <from report>
ISO SHA256:       <from report>
Build Duration:   <from report>
Result:           SUCCESS or FAILED

Errors:

Warnings:

Notes:
- First clean build: Yes / No
- Any customizations beyond AlyaOS: Yes / No
```

## 3. Boot Validation

### UEFI Boot Test (QEMU)

```bash
qemu-system-x86_64 -enable-kvm -m 4096 -cpu host -smp 4 \
  -drive file=out/alya-os-$(date +%Y.%m.%d)-x86_64.iso,format=raw,if=none,id=drive0 \
  -device virtio-blk,drive=drive0 \
  -bios /usr/share/edk2/x64/OVMF_CODE.fd
```

### BIOS Boot Test (QEMU)

```bash
qemu-system-x86_64 -enable-kvm -m 4096 -cpu host -smp 4 \
  -cdrom out/alya-os-$(date +%Y.%m.%d)-x86_64.iso
```

### Boot Log

```
┌──────────────────────────────────────────────┐
│          Alya OS Boot Validation             │
└──────────────────────────────────────────────┘

UEFI Boot:
  Boot menu shows "Alya OS":                    Yes / No
  Boot menu shows "Alya OS (LTS)":              Yes / No
  Default boot succeeds:                        Yes / No
  Desktop loads (labwc):                        Yes / No
  Alya Launcher launches:                       Yes / No
  Alya Hub launches:                            Yes / No
  Workspace Manager launches:                   Yes / No

BIOS Boot:
  Boot menu shows "Alya OS":                    Yes / No
  Boot menu shows "Alya OS (LTS)":              Yes / No
  Default boot succeeds:                        Yes / No
  Desktop loads (labwc):                        Yes / No
  Alya Launcher launches:                       Yes / No
  Alya Hub launches:                            Yes / No
  Workspace Manager launches:                   Yes / No

Known Issues:
  - LTS kernel entry present in UEFI but absent in BIOS:  Observed / Not Observed
  - PXE boot still shows "CachyOS":                       Observed / Not Observed

Screenshots / VM console captures:
  <attach if available>

Overall: PASS / FAIL
```

## 4. Bug Reporting

If any bug is found during build or boot:

### Bug Template

```
---
title: "[RC1] <short description>"
---

**Severity**: critical / major / minor
**Found during**: build / UEFI boot / BIOS boot / package validation
**Category**: branding / boot / desktop / packaging / build

**Description**:
<clear description of the bug>

**Steps to Reproduce**:
1. <step 1>
2. <step 2>
3. <step 3>

**Expected Behavior**:
<what should happen>

**Actual Behavior**:
<what actually happens>

**Screenshots / Logs**:
<attach relevant output>

**Fix scope**: <what file(s) need changing, estimated complexity>
```

### Fix Rules
- Fix ONLY the bug — no scope expansion
- No new features, no refactoring, no architecture changes
- After fix: rebuild + rebootstrap + rebot
- Update this file with the fix details

## 5. Package Validation

Test each Alya package (install/upgrade/remove):

```bash
# From within the running ISO or a test system:
sudo pacman -U build/pkgs/alya-launcher-*.pkg.tar.zst
sudo pacman -U build/pkgs/alya-hub-*.pkg.tar.zst
sudo pacman -U build/pkgs/workspace-manager-*.pkg.tar.zst
sudo pacman -U build/pkgs/alya-theme-*.pkg.tar.zst
```

```
Package Installation:
  alya-launcher:      PASS / FAIL
  alya-hub:           PASS / FAIL
  workspace-manager:  PASS / FAIL
  alya-theme:         PASS / FAIL

Package Removal:
  alya-launcher:      PASS / FAIL (cleanup hooks OK)
  alya-hub:           PASS / FAIL (cleanup hooks OK)
  workspace-manager:  PASS / FAIL (cleanup hooks OK)
  alya-theme:         PASS / FAIL (cleanup hooks OK)
```

## 6. Final Validation

All 6 quality gates must pass:

| Gate | Description | Status |
|------|-------------|--------|
| 1 | Boot title shows "Alya OS" | PASS / FAIL |
| 2 | Package .install hooks work | PASS / FAIL |
| 3 | Dependencies documented | PASS / FAIL |
| 4 | Architecture documented | PASS / FAIL |
| 5 | Maintainability standards met | PASS / FAIL |
| 6 | Clean build succeeds | PASS / FAIL |
| 7 | RC1 report complete | PASS / FAIL |

**Final Verdict**: RC1-READY / BLOCKED

---

*Document generated by Alya OS build system. Update this file with build results, boot logs, and any bugs found.*
