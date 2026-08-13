#!/usr/bin/env bash
# corp_action_daily.sh — vỏ cron cho mike/bin/corp_action_daily.py.
#
# Vỏ này tồn tại vì đúng MỘT lý do: `bq` CLI cần `CLOUDSDK_CONFIG` (tài khoản dtienthanh) và
# PATH của google-cloud-sdk, cả hai nằm trong `wc_env.sh`. Mọi logic ở file .py — đừng thêm phép
# tính nào vào đây.
#
# `wc_env.sh` cũng export `BQ_LOCAL_CACHE` (cache T-1). Script Python tự `os.environ.pop()` nó
# ngay đầu file (§11 coding_guidelines: script PUBLISH phải đọc nguồn sống, không qua cache
# T-1). KHÔNG sửa `wc_env.sh` để gỡ biến đó — hàng chục script khác cần nó.
set -euo pipefail

# shellcheck source=/dev/null
source /home/trido/thanhdt/WorkingClaude/wc_env.sh

exec python3 /home/trido/thanhdt/WorkingClaude/mike/bin/corp_action_daily.py "$@"
