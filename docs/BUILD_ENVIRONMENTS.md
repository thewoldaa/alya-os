# Alya OS — Build Environments

## Supported Environments

| Environment | Status | Notes |
|-------------|--------|-------|
| Native Arch Linux | ✅ Primary | Full feature set |
| CachyOS | ✅ Primary | Same as Arch |
| GitHub Actions (Docker) | ✅ CI | `--privileged` required |
| Ubuntu (WSL2) | ❌ Not supported | No pacman |
| macOS | ❌ Not supported | No pacman, no mkarchiso |
| Windows (native) | ❌ Not supported | No pacman, no mkarchiso |

## Prerequisites

### Native Arch Linux / CachyOS

```bash
sudo pacman -S --needed archiso xorriso squashfs-tools grub binutils base-devel
```

### GitHub Actions (CI)

Provided by the workflow container. See `docs/GITHUB_WORKFLOW.md`.

## Build Commands

### Full Alya OS Build

```bash
cd AlyaOS
git submodule update --init --recursive
./build.sh
```

### Upstream-Only Build (CI Baseline)

```bash
cd AlyaOS
git submodule update --init --recursive
sudo mkarchiso -v -w /tmp/work -o out upstream/archiso
```

## Caching

Local builds do NOT cache between runs. Each build is fresh:

```bash
rm -rf build out work
./build.sh
```

CI builds are always fresh (ephemeral runner).

## Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| Disk | 10 GB | 20 GB |
| RAM | 2 GB | 4 GB |
| CPU | 2 cores | 4 cores |
| Network | Required (package downloads) | Broadband |

## Known Limitations

1. **makepkg requires non-root**: `build.sh` Stage 6 runs `makepkg`
   which refuses to run as root. In Docker containers (CI), a `builder`
   user is required. This is handled by a CI wrapper, NOT by modifying
   `build.sh`.
2. **mkarchiso requires root**: Stage 8 uses `sudo mkarchiso`. In
   Docker containers running as root, `sudo` does not exist. Future CI
   workflows should call `mkarchiso` directly.
