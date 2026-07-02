# Alya OS — Agent Guide

## Build

```bash
./build.sh                    # DO NOT run as root (makepkg Stage 6 will break)
sudo pacman -S --needed archiso xorriso squashfs-tools grub binutils base-devel
```

9-stage pipeline in `build.sh`. CI env example in `.github/workflows/poc-upstream-build.yml`.

## Upstream Relationship

CachyOS-Live-ISO is a **git submodule** pinned to `33bbc02`:
- `upstream/` is READ-ONLY — never modify files inside it
- All changes go in `overlay/` (14 files) or `patches/` (1 patch, 3 files)
- Update: `cd upstream && git fetch && git checkout <new>` then update `ALYA_UPSTREAM_COMMIT` in `build.sh`

## CI Rules

- **Never modify `build.sh` for CI** — CI adapts to build.sh, never the reverse
- **Call `buildiso.sh`, never `mkarchiso` directly** — `buildiso.sh` runs `prepare_profile()` (copies package list, generates motd/mirrorlist/version tags, etc.). Calling mkarchiso directly skips all that.
- **`$USER` must be set** — `buildiso.sh` runs `sudo chown $USER` after mkarchiso. In containers: `export USER="${USER:-root}"`.
- **CachyOS GPG key** — mkarchiso passes `-G` to pacstrap (no host keyring copy). Key goes stale when cache is cleaned. Solution: copy host keyring to `archiso/airootfs/etc/pacman.d/gnupg/` so `_make_custom_airootfs()` places it before pacstrap.
- **PoC baseline must pass** before any Alya-specific CI is added
- **Overlay `airootfs/` files must NOT overlap with package files** — `_make_custom_airootfs()` copies airootfs to chroot BEFORE `pacstrap`. If a file exists in airootfs and the same path is shipped by a package, `pacstrap` fails with `conflicting files`. Fix: remove the conflicting file from overlay and use `airootfs/root/customize_airootfs.sh` (runs post-pacstrap inside chroot) to generate it after the package is installed.
- **`customize_airootfs.sh` pattern** — place at `overlay/airootfs/root/customize_airootfs.sh`. mkarchiso executes it inside the chroot after all packages are installed. Use for files that would conflict with packages (e.g., `/etc/ly/ly.conf`).

## Key Files

| Path | Role |
|------|------|
| `build.sh` | 9-stage build pipeline (validate, sync, overlay, brand, patch, build-pkgs, merge, mkarchiso, report) |
| `overlay/` | 13 override files (branding, airootfs, desktop configs, grub, syslinux) |
| `packages/` | 4 PKGBUILDs: alya-{launcher,hub,theme}, workspace-manager |
| `packages-alya.x86_64` | 40 package additions appended to CachyOS package list |
| `patches/01-efiboot-title.patch` | UEFI boot title branding (3 files patched) |
| `upstream/` | CachyOS submodule (124+ files, read-only) |

## Gotchas

- `* text=auto` in `.gitattributes` — LF normalization on commit
- Output: `out/alya-os-YYYY.MM.DD-x86_64.iso`
- GitHub: `https://github.com/thewoldaa/alya-os` (public)
- RC1 freeze: no new features, no refactoring, no architecture changes
