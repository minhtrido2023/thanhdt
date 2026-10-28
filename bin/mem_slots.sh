#!/usr/bin/env bash
# mem_slots.sh <PER_PROC_GB> [RESERVE_GB=8] — in số tiến trình song song AN TOÀN theo MemAvailable hiện tại.
# slots = floor((MemAvailable_GB - RESERVE) / PER_PROC). Tối thiểu 1. Dùng TRƯỚC khi mở N engine nền.
set -euo pipefail
PER="${1:?usage: mem_slots.sh <PER_PROC_GB> [RESERVE_GB]}"; RES="${2:-8}"
awk -v per="$PER" -v res="$RES" '/MemAvailable/{a=$2/1048576; s=int((a-res)/per); if(s<1)s=1; print s}' /proc/meminfo
