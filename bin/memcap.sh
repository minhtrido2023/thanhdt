#!/usr/bin/env bash
# memcap.sh <MAX_GB> <cmd...> — chạy cmd trong cgroup user có MemoryMax cứng, KHÔNG swap.
# Vượt trần ⇒ kernel giết RIÊNG cmd đó (exit 137), không kéo cả container tới thrash.
# Lý do: sự cố 2026-10-20 (container LXC 40GB, KHÔNG swap, engine backtest ~3,2GB/tiến trình × 8 song song).
# Fail-closed: không dựng được cgroup (systemd-run hỏng) ⇒ exit 3, KHÔNG chạy trần.
set -euo pipefail
[ "$#" -ge 2 ] || { echo "usage: memcap.sh <MAX_GB> <cmd...>" >&2; exit 2; }
GB="$1"; shift
[[ "$GB" =~ ^[0-9]+$ ]] || { echo "memcap: MAX_GB phải là số nguyên, nhận '$GB'" >&2; exit 2; }
command -v systemd-run >/dev/null || { echo "memcap: thiếu systemd-run — từ chối chạy không trần" >&2; exit 3; }
exec systemd-run --user --scope --quiet -p "MemoryMax=${GB}G" -p MemorySwapMax=0 -- "$@"
