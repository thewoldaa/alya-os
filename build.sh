#!/usr/bin/env bash
# Alya OS Build System
# 9-stage pipeline: Validate → Sync → Overlay → Branding → Patch → Build Pkgs → Merge → Generate → Report
set -euo pipefail

ALYA_VERSION="0.1.0"
ALYA_UPSTREAM_COMMIT="33bbc02"
START_TS=$(date +%s)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM_DIR="${SCRIPT_DIR}/upstream"
BUILD_DIR="${SCRIPT_DIR}/build"
OUT_DIR="${SCRIPT_DIR}/out"
PKG_DIR="${SCRIPT_DIR}/build/pkgs"
REPORT_FILE="${OUT_DIR}/build-report.txt"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'
log_i() { echo -e "${BLUE}[${1}/${TOTAL_STAGES}]${NC} $2"; }
log_ok() { echo -e "${GREEN}[OK]${NC}  $1"; }
log_w()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_e()  { echo -e "${RED}[FAIL]${NC} $1"; }

CACHYOS_COMMIT=""
STAGE=0; TOTAL_STAGES=9; FAILED=""; ERRORS=""; WARNINGS=""

stage() {
    STAGE=$1; local name="$2"
    echo -e "\n${CYAN}════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Stage ${STAGE}/${TOTAL_STAGES}: ${name}${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}\n"
}
fail() { log_e "$1"; ERRORS+="  - $1\n"; FAILED="FAILED"; exit 1; }
warn() { log_w "$1"; WARNINGS+="  - $1\n"; }

# ──────────────── STAGE 1: VALIDATE ────────────────
stage 1 "Validate Environment"
log_i 1 "Checking dependencies..."
DEPS=("mkarchiso" "pacman" "xorriso" "mksquashfs" "grub-mkrescue")
MISSING=()
for dep in "${DEPS[@]}"; do
    command -v "$dep" &>/dev/null || MISSING+=("$dep")
done
if [[ ${#MISSING[@]} -gt 0 ]]; then
    fail "Missing: ${MISSING[*]}. Install: sudo pacman -S archiso xorriso squashfs-tools grub binutils"
fi
if [[ "$(uname -m)" != "x86_64" ]]; then fail "Host must be x86_64"; fi
if [[ ! -d "${UPSTREAM_DIR}/.git" ]]; then fail "upstream/ not found. Clone: git clone https://github.com/CachyOS/CachyOS-Live-ISO.git upstream"; fi
log_ok "Environment validated"

# ──────────────── STAGE 2: SYNC ────────────────
stage 2 "Synchronize Upstream"
log_i 2 "Pinning upstream to commit ${ALYA_UPSTREAM_COMMIT}..."
cd "${UPSTREAM_DIR}"
if ! git checkout -f "${ALYA_UPSTREAM_COMMIT}" 2>/dev/null; then
    warn "Cannot checkout ${ALYA_UPSTREAM_COMMIT}, trying fetch..."
    git fetch origin 2>/dev/null || warn "Cannot fetch upstream (offline?)"
    if ! git checkout -f "${ALYA_UPSTREAM_COMMIT}" 2>/dev/null; then
        warn "Cannot pin commit; using current HEAD"
    fi
fi
CACHYOS_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
log_ok "Upstream at commit: ${CACHYOS_COMMIT}"
cd "${SCRIPT_DIR}"

# ──────────────── STAGE 3: OVERLAY ────────────────
stage 3 "Apply Overlay"
log_i 3 "Copying upstream to build directory..."
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
cp -r "${UPSTREAM_DIR}/archiso" "${BUILD_DIR}/archiso"
cp "${UPSTREAM_DIR}/buildiso.sh" "${BUILD_DIR}/buildiso.sh" 2>/dev/null || true
cp "${UPSTREAM_DIR}/util-iso.sh" "${BUILD_DIR}/util-iso.sh" 2>/dev/null || true

log_i 3 "Applying overlay files..."
# GRUB
if [[ -f "${SCRIPT_DIR}/overlay/grub/grub.cfg" ]]; then
    cp "${SCRIPT_DIR}/overlay/grub/grub.cfg" "${BUILD_DIR}/archiso/grub/grub.cfg"
fi
# EFI boot
if [[ -d "${SCRIPT_DIR}/overlay/efiboot" ]]; then
    cp -r "${SCRIPT_DIR}/overlay/efiboot"/* "${BUILD_DIR}/archiso/efiboot/" 2>/dev/null || true
fi
# Syslinux
if [[ -d "${SCRIPT_DIR}/overlay/syslinux" ]]; then
    cp -r "${SCRIPT_DIR}/overlay/syslinux"/* "${BUILD_DIR}/archiso/syslinux/" 2>/dev/null || true
fi
# airootfs additions
if [[ -d "${SCRIPT_DIR}/overlay/airootfs" ]]; then
    cp -r "${SCRIPT_DIR}/overlay/airootfs"/* "${BUILD_DIR}/archiso/airootfs/" 2>/dev/null || true
fi
# Desktop configs (inject into skel)
if [[ -d "${SCRIPT_DIR}/overlay/desktop/labwc" ]]; then
    mkdir -p "${BUILD_DIR}/archiso/airootfs/etc/skel/.config/labwc"
    cp -r "${SCRIPT_DIR}/overlay/desktop/labwc"/* "${BUILD_DIR}/archiso/airootfs/etc/skel/.config/labwc/"
fi
if [[ -d "${SCRIPT_DIR}/overlay/desktop/openbox" ]]; then
    mkdir -p "${BUILD_DIR}/archiso/airootfs/etc/skel/.config/openbox"
    shopt -s nullglob
    for f in "${SCRIPT_DIR}/overlay/desktop/openbox"/*; do cp "$f" "${BUILD_DIR}/archiso/airootfs/etc/skel/.config/openbox/"; done
    shopt -u nullglob
fi
if [[ -d "${SCRIPT_DIR}/overlay/desktop/lxqt" ]]; then
    mkdir -p "${BUILD_DIR}/archiso/airootfs/etc/skel/.config/lxqt"
    shopt -s nullglob
    for f in "${SCRIPT_DIR}/overlay/desktop/lxqt"/*; do cp "$f" "${BUILD_DIR}/archiso/airootfs/etc/skel/.config/lxqt/"; done
    shopt -u nullglob
fi
log_ok "Overlay applied"

# ──────────────── STAGE 4: BRANDING ────────────────
stage 4 "Inject Branding"
log_i 4 "Injecting Alya OS branding..."
BRAND="${SCRIPT_DIR}/overlay/branding"
AIROOTFS="${BUILD_DIR}/archiso/airootfs"

# os-release, hostname, issue
if [[ -f "${BRAND}/os-release" ]]; then cp "${BRAND}/os-release" "${AIROOTFS}/etc/os-release"; fi
if [[ -f "${BRAND}/hostname" ]]; then cp "${BRAND}/hostname" "${AIROOTFS}/etc/hostname"; fi
if [[ -f "${BRAND}/issue" ]]; then cp "${BRAND}/issue" "${AIROOTFS}/etc/issue"; fi

# profiledef.sh (ISO metadata override)
if [[ -f "${BRAND}/profiledef.sh" ]]; then
    cp "${BRAND}/profiledef.sh" "${BUILD_DIR}/archiso/profiledef.sh"
fi

# GRUB splash
if [[ -f "${BRAND}/grub/splash.png" ]]; then
    mkdir -p "${BUILD_DIR}/archiso/grub" "${BUILD_DIR}/archiso/syslinux"
    cp "${BRAND}/grub/splash.png" "${BUILD_DIR}/archiso/grub/splash.png"
    cp "${BRAND}/grub/splash.png" "${BUILD_DIR}/archiso/syslinux/splash.png"
fi

log_ok "Branding injected"

# ──────────────── STAGE 5: PATCH ────────────────
stage 5 "Apply Patches"
PATCH_COUNT=0
if [[ -d "${SCRIPT_DIR}/patches" ]]; then
    for patch in "${SCRIPT_DIR}/patches/"*.patch; do
        if [[ -f "$patch" ]]; then
            log_i 5 "Applying patch: $(basename "$patch")"
            (cd "${BUILD_DIR}" && patch -p1 < "$patch") || warn "Patch failed: $(basename "$patch")"
            PATCH_COUNT=$((PATCH_COUNT + 1))
        fi
    done
fi
log_ok "Patches applied: ${PATCH_COUNT}"

# ──────────────── STAGE 6: BUILD PACKAGES ────────────────
stage 6 "Build Alya Packages"
mkdir -p "${PKG_DIR}"
BUILT_PKGS=()
for pkg_dir in "${SCRIPT_DIR}/packages"/*/; do
    pkg=$(basename "${pkg_dir}")
    if [[ -f "${pkg_dir}/PKGBUILD" ]]; then
        log_i 6 "Building: ${pkg}"
        (
            cd "${pkg_dir}"
            BUILDDIR="${PKG_DIR}/src" PKGDEST="${PKG_DIR}" makepkg -sc --noconfirm --needed 2>&1 | tail -1
        ) && {
            log_ok "Built: ${pkg}"
            BUILT_PKGS+=("${pkg}")
        } || warn "Failed to build: ${pkg}"
    fi
done

# Create local repo for custom packages
REPO_DIR="${PKG_DIR}/repo"
mkdir -p "${REPO_DIR}"
for f in "${PKG_DIR}"/*.pkg.tar.zst; do
    [[ -f "$f" ]] && cp "$f" "${REPO_DIR}/"
done
if ls "${REPO_DIR}"/*.pkg.tar.zst 1>/dev/null 2>&1; then
    cd "${REPO_DIR}"
    repo-add alya-os.db.tar.gz ./*.pkg.tar.zst
    cd "${SCRIPT_DIR}"
fi
log_ok "Custom packages built: ${#BUILT_PKGS[@]}"

# ──────────────── STAGE 7: MERGE PACKAGES ────────────────
stage 7 "Merge Package Lists"
ALYA_LIST="${SCRIPT_DIR}/packages-alya.x86_64"
MERGED_LIST="${BUILD_DIR}/archiso/packages_desktop.x86_64"

# Auto-detect upstream package list (might be named differently in future)
CACHYOS_LIST=$(find "${UPSTREAM_DIR}/archiso" -maxdepth 1 -name 'packages*.x86_64' | head -1 || true)
if [[ -f "${CACHYOS_LIST}" ]]; then
    cp "${CACHYOS_LIST}" "${MERGED_LIST}"
    log_i 7 "Copied CachyOS packages ($(basename "${CACHYOS_LIST}")): $(wc -l < "${CACHYOS_LIST}") packages"
else
    warn "CachyOS package list not found"
    > "${MERGED_LIST}"
fi

if [[ -f "${ALYA_LIST}" ]]; then
    # Remove duplicates and append
    grep -v '^#' "${ALYA_LIST}" | grep -v '^$' >> "${MERGED_LIST}"
    log_i 7 "Appended Alya packages: $(grep -cve '^\s*#' "${ALYA_LIST}") additions"
fi

# Remove duplicate lines
sort -u -o "${MERGED_LIST}" "${MERGED_LIST}"
TOTAL_PKGS=$(wc -l < "${MERGED_LIST}")
log_ok "Merged package list: ${TOTAL_PKGS} total packages"

# ──────────────── STAGE 8: GENERATE ISO ────────────────
stage 8 "Generate ISO"
mkdir -p "${OUT_DIR}"
log_i 8 "Running mkarchiso..."
cd "${SCRIPT_DIR}"
sudo mkarchiso -v -w "${BUILD_DIR}/work" -o "${OUT_DIR}" "${BUILD_DIR}/archiso"
ISO_FILE=$(find "${OUT_DIR}" -name '*.iso' -print -quit 2>/dev/null || true)
if [[ -z "${ISO_FILE}" ]]; then
    fail "ISO not generated. Check mkarchiso output."
fi
# Rename to Alya OS convention
ALYA_ISO="${OUT_DIR}/alya-os-$(date +%Y.%m.%d)-x86_64.iso"
if [[ "${ISO_FILE}" != "${ALYA_ISO}" ]]; then
    mv -f "${ISO_FILE}" "${ALYA_ISO}"
fi
ISO_SIZE=$(du -h "${ALYA_ISO}" | cut -f1)
ISO_SHA256=$(sha256sum "${ALYA_ISO}" | cut -d' ' -f1)
log_ok "ISO generated: ${ALYA_ISO} (${ISO_SIZE})"

# ──────────────── STAGE 9: REPORT ────────────────
stage 9 "Generate Build Report"
END_TS=$(date +%s)
DURATION=$((END_TS - START_TS))
KERNEL_VER=$(strings "${BUILD_DIR}/archiso/airootfs/boot/vmlinuz-linux-cachyos" 2>/dev/null | grep "^Linux version" | head -1 || echo "unknown")
OVERLAY_COUNT=$(find "${SCRIPT_DIR}/overlay" -type f | wc -l)
BRANDING_COUNT=$(find "${SCRIPT_DIR}/overlay/branding" -type f | wc -l)

cat > "${REPORT_FILE}" << REPORTEOF
╔══════════════════════════════════════════════════╗
║           Alya OS Build Report                    ║
╚══════════════════════════════════════════════════╝

Build Date:     $(date -u '+%Y-%m-%d %H:%M:%S UTC')
Alya Version:   ${ALYA_VERSION}
CachyOS Commit: ${CACHYOS_COMMIT}
Kernel:         ${KERNEL_VER}
Total Packages: ${TOTAL_PKGS}
Overlay Files:  ${OVERLAY_COUNT}
Branding Files: ${BRANDING_COUNT}
Patches:        ${PATCH_COUNT}
Custom Packages: ${#BUILT_PKGS[@]} (${BUILT_PKGS[*]:-none})

ISO Size:       ${ISO_SIZE}
ISO SHA256:     ${ISO_SHA256}

Build Duration: $((DURATION / 60))m $((DURATION % 60))s
Result:         ${FAILED:-SUCCESS}

${ERRORS:+Errors:
${ERRORS}}
${WARNINGS:+Warnings:
${WARNINGS}}
REPORTEOF

log_ok "Build report: ${REPORT_FILE}"
cat "${REPORT_FILE}"

# ──────────────── DONE ────────────────
if [[ -n "${FAILED}" ]]; then
    echo -e "\n${RED}════════════════════════════════════════${NC}"
    echo -e "${RED}  BUILD FAILED${NC}"
    echo -e "${RED}════════════════════════════════════════${NC}"
    exit 1
fi
echo -e "\n${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  Alya OS Build Complete${NC}"
echo -e "${GREEN}  ${ALYA_ISO}${NC}"
echo -e "${GREEN}  ${ISO_SIZE}  │  SHA256: ${ISO_SHA256:0:16}...${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
