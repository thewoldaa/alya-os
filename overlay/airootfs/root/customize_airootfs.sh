#!/usr/bin/env bash
# Alya OS - Customize airootfs (runs inside chroot after pacstrap)
set -euo pipefail

# Configure ly display manager
cat > /etc/ly/ly.conf << 'LYEOF'
auto_login = alya
sessions = /usr/share/wayland-sessions
animate = 0
bg_color = 1a1b26
fg_color = a9b1d6
prompt_color = 7dcfff
path = /sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin
login_timeout = 120
LYEOF
