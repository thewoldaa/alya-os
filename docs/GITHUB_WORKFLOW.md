# GitHub Workflows — Alya OS CI/CD

## Overview

Alya OS uses GitHub Actions for continuous integration and delivery.
All workflows run on `ubuntu-latest` with Arch Linux containers for
ISO builds.

## Workflows

### 1. PoC - Build Upstream CachyOS ISO (`poc-upstream-build.yml`)

- **Purpose**: Baseline verification that mkarchiso works in CI
- **Triggers**: `workflow_dispatch`, push/PR to workflow file
- **Builds**: Unmodified CachyOS upstream (no Alya overlay)
- **Container**: `archlinux:base-devel` with `--privileged`
- **Artifacts**: ISO + `poc-report.txt` (duration, RAM, disk, size)

This is the **permanent baseline**. Every upstream update must pass
this workflow before Alya-specific CI proceeds.

### 2. Verify Submodule (`verify-submodule.yml`)

- **Purpose**: Ensure CachyOS submodule is pinned and clean
- **Triggers**: Every push and pull request to `main`/`develop`
- **Checks**: Initialized, correct commit, no uncommitted changes

### 3. Build Alya OS ISO (`build.yml`) — *Planned*

- **Purpose**: Full Alya OS ISO build with overlay + packages
- **Depends on**: PoC passing

### 4. Lint (`lint.yml`) — *Planned*

- **Purpose**: Static analysis (shellcheck, PKGBUILD validation, markdown)

### 5. Release (`release.yml`) — *Planned*

- **Purpose**: Tag-triggered release with automated artifact upload

## Architecture

```
Developer
  │
  ├─ git push
  │     │
  │     ▼
  │   verify-submodule.yml  ← fast (<1 min)
  │
  ├─ git push (workflow change)
  │     │
  │     ▼
  │   poc-upstream-build.yml  ← slow (20-60 min)
  │     │
  │     ▼
  │   [future] build.yml → lint.yml → release.yml
  │
  ▼
GitHub Actions Runner
  │
  ├─ Arch Linux container (--privileged)
  │     │
  │     ├─ pacman-key --init
  │     ├─ pacman -S archiso xorriso squashfs-tools grub binutils
  │     ├─ mkarchiso -v ...
  │     └─ sha256sum
  │
  ▼
Artifacts
  ├─ *.iso
  ├─ *.iso.sha256
  └─ *-report.txt
```

## Container Setup

Every ISO build workflow follows this sequence:

```yaml
container:
  image: archlinux:base-devel
  options: --privileged

steps:
  - run: pacman-key --init
  - run: pacman-key --populate archlinux
  - run: pacman -Syu --noconfirm
  - run: pacman -S --noconfirm --needed archiso xorriso squashfs-tools grub binutils git
```

## Artifact Retention

| Artifact | Retention |
|----------|-----------|
| ISO | 7 days |
| Build report | 90 days |
| Release ISO | Permanent |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `pacman-key --init` hangs | Low entropy in container | Add `haveged` or `rng-tools` |
| `mkarchiso` fails with mount error | Missing `--privileged` | Add `options: --privileged` |
| OOM kill (exit 137) | Runner memory limit | Reduce `cow_spacesize` or disable `copytoram` |
| `makepkg` fails as root | Running as root in container | Use `useradd builder && runuser -u builder` |
