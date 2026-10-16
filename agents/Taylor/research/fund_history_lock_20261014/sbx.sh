#!/usr/bin/env bash
# Chạy 1 lệnh TRONG sandbox: sbx.sh <sandbox> <script trong mike/bin> [args...]
set -euo pipefail
S="${1:?}"; shift; P="${1:?}"; shift
[ -f "$S/wc_env.sh" ] || { echo "không phải sandbox: $S" >&2; exit 2; }
case "$S" in /tmp/*) ;; *) echo "sandbox phải ở /tmp" >&2; exit 2;; esac
WC_ROOT="$S" TZ="${SBX_TZ-Asia/Ho_Chi_Minh}" exec python3 "$S/mike/bin/$P" "$@"
