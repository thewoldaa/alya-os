# Alya OS — Agent Guide

## Build

```bash
./build.sh                    # DO NOT run as root (makepkg Stage 6 will break)
sudo pacman -S --needed archiso xorriso squashfs-tools grub binutils base-devel
```
Output: `out/alya-os-YYYY.MM.DD-x86_64.iso` (`.gitignore` ignores `out/`, `build/`, `work/`).

## Upstream

CachyOS-Live-ISO is a **git submodule** pinned to commit `33bbc02`:
- `upstream/` is READ-ONLY — never modify files inside it
- All changes go in `overlay/` or `patches/`
- Update: `cd upstream && git fetch && git checkout <new>` then update `ALYA_UPSTREAM_COMMIT` in `build.sh`

## CI Rules

- **Never modify `build.sh` for CI** — CI adapts to build.sh, never the reverse
- **Call `buildiso.sh`, never `mkarchiso` directly** — `buildiso.sh` runs `prepare_profile()` (copies package list, generates motd/mirrorlist/version tags). Calling `mkarchiso` directly skips all that
- **`$USER` must be set** —`buildiso.sh` runs `sudo chown $USER` after mkarchiso. In containers: `export USER="${USER:-root}"`
- **PoC baseline must pass** before any Alya-specific CI is added (see `poc-upstream-build.yml`)

## CI Gotchas

- **archlinux:base-devel does NOT include git** — install git before `actions/checkout` when submodules are needed
- **`git safe.directory`** — after `chown -R build: .`, git 2.35+ blocks the workspace and submodule repos. Add exceptions: `git config --global --add safe.directory "${GITHUB_WORKSPACE}"` and `"${GITHUB_WORKSPACE}/upstream"`
- **CachyOS GPG key** — mkarchiso passes `-G` to pacstrap (no host keyring copy). Solution: copy host keyring to `archiso/airootfs/etc/pacman.d/gnupg/` so `_make_custom_airootfs()` places it before pacstrap
- **Overlay `airootfs/` must NOT overlap with package files** — `_make_custom_airootfs()` copies airootfs to chroot BEFORE `pacstrap`. Files that package also ships cause `conflicting files`. Fix: remove from overlay and use `airootfs/root/customize_airootfs.sh` (runs post-pacstrap inside chroot) to generate them
- **`customize_airootfs.sh`** — place at `overlay/airootfs/root/customize_airootfs.sh`. mkarchiso executes it inside the chroot after all packages are installed
- **Artifact naming** — build.yml uploads ISO as `alya-os-iso-${{ github.sha }}`, reports as `alya-os-reports-${{ github.sha }}`. boot-test.yml downloads from that artifact
- **Dependabot** — `.github/dependabot.yml` configured for `github-actions` ecosystem, weekly schedule, auto-PRs for action SHA updates

## Key Files

| Path | Role |
|------|------|
| `build.sh` | 9-stage build pipeline (validate, sync, overlay, brand, patch, build-pkgs, merge, mkarchiso, report) |
| `overlay/` | Branding, airootfs, desktop configs, grub, syslinux |
| `packages/` | 4 PKGBUILDs: alya-{launcher,hub,theme}, workspace-manager |
| `packages-alya.x86_64` | ~40 package additions appended to CachyOS package list |
| `patches/01-efiboot-title.patch` | UEFI boot title branding (3 files patched) |
| `overlay/airootfs/root/customize_airootfs.sh` | Post-pacstrap hook (writes `/etc/ly/ly.conf`) |
| `upstream/` | CachyOS submodule (read-only, pinned) |
| `.github/workflows/build.yml` | Full Alya OS ISO build (archlinux:base-devel, --privileged) |
| `.github/workflows/boot-test.yml` | QEMU boot validation (BIOS + UEFI) |
| `.github/workflows/lint.yml` | ShellCheck + yamllint + structure checks |
| `.github/workflows/release.yml` | Tag-triggered (v*) release |
| `.github/workflows/poc-upstream-build.yml` | Upstream-only baseline build |
| `.github/workflows/verify-submodule.yml` | Submodule pin + cleanliness |
| `.github/dependabot.yml` | Auto-update github-actions action pins |

## Workflow Triggers

| Workflow | Triggers |
|----------|---------|
| `build.yml` | push (path-scoped), PR (path-scoped), workflow_dispatch |
| `boot-test.yml` | workflow_run after `build.yml` success, workflow_dispatch, PR (path-scoped to workflow) |
| `release.yml` | tag push `v*` |
| `lint.yml` | push, PR to main/develop |
| `verify-submodule.yml` | push, PR to main/develop |

## Package Sources

- `packages-alya.x86_64` contains only packages NOT in upstream CachyOS `packages_desktop.x86_64`
- Build creates local repo `[alya-os]` (file://, SigLevel=TrustAll) in profile's pacman.conf
- AUR-only packages (fernflower, nitrogen, jdk21-openjdk-src) removed — not in official repos
- `wlroots0.20` used instead of `wlroots` (versioned package)

## `.gitattributes`

- `* text=auto` — LF normalization on commit (CRLF on checkout on Windows)
- Images, ISOs, archives, signatures marked binary

## PKGBUILD Quirks

- Sources must be **flattened** (no `src/` subdirectory) — BUILDDIR causes `srcdir` nesting with `src/` subdirs
- `sha256sums` array length must exactly match `source` array length — use `SKIP` entries
- `backup` entries must NOT have leading `/`
