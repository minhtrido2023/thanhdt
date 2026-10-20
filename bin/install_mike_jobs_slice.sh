#!/usr/bin/env bash
# Cài (idempotent) ~/.config/systemd/user/mike-jobs.slice: TRẦN RAM TỔNG cho mọi job dispatch --bg.
# Mặc định 28G trên container 40GB (nền ~6-7GB gồm dịch vụ user khác). Đổi: MIKE_JOBS_SLICE_GB=NN.
set -euo pipefail
GB="${MIKE_JOBS_SLICE_GB:-28}"
D="$HOME/.config/systemd/user"; mkdir -p "$D"
cat > "$D/mike-jobs.slice" <<UNIT
[Unit]
Description=Mike dispatch jobs — tran RAM tong (chong treo container 2026-10-20)
[Slice]
MemoryMax=${GB}G
MemorySwapMax=0
UNIT
systemctl --user daemon-reload
systemctl --user show mike-jobs.slice -p MemoryMax,MemorySwapMax
