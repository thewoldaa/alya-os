# Patches

Only create patches when overlay/configuration/packaging cannot solve the problem.

Each patch must document:
- Original file (path in upstream/)
- Reason for modification
- Compatibility impact
- Rollback method

Current patches:
- `01-efiboot-title.patch` — Changes "CachyOS" to "Alya OS" in UEFI systemd-boot entries (3 files, 1 word each).
