# Upstream: CachyOS-Live-ISO

## Relationship

Alya OS is based on **CachyOS-Live-ISO**, which provides the Arch Linux
installation framework (archiso), kernel configuration, package selection,
and boot infrastructure.

CachyOS is tracked as a **Git submodule** (not forked, not copied).

## Pinned Commit

```
33bbc02104ee0172f7ce7e6c35f74360241fc61e
```

This commit is the RC1 baseline. All Alya OS overlays, patches, and
configurations are designed against this specific upstream state.

## Why Submodule?

| Aspect | Submodule | Fork | Plain Copy |
|--------|-----------|------|------------|
| Upstream history | ✅ Preserved | ✅ Preserved | ❌ Lost |
| Diff visibility | ✅ Clear | ✅ Clear | ❌ No diff |
| Update cost | Low (1 command) | Medium (merge) | High (re-copy) |
| Clone complexity | Slightly higher | Normal | Normal |
| Contribution path | PR to Alya only | PR to fork | N/A |

A submodule was chosen because:
1. **Preserves upstream provenance** — every file's origin is verifiable
2. **Clear diff** — `git diff --submodule` shows exactly what changed
3. **Low update burden** — updating is `git submodule update --remote`
4. **No fork management** — no need to maintain a separate CachyOS fork

## Update Procedure

```bash
# 1. Update submodule to latest upstream
cd upstream
git fetch origin
git checkout <new-tag-or-commit>
cd ..

# 2. Verify Alya OS compatibility
./build.sh  # Must pass

# 3. Commit the new submodule reference
git add upstream
git commit -m "upstream: update to <commit>"
git push
```

## Maintenance Rules

1. **Never modify files inside `upstream/` directly.** Changes go in
   `overlay/` or `patches/`.
2. **Verify PoC workflow passes** after each upstream update.
3. **Update `ALYA_UPSTREAM_COMMIT` in `build.sh`** to match the new
   pinned commit.
4. **Regenerate patches** if upstream files change significantly.
