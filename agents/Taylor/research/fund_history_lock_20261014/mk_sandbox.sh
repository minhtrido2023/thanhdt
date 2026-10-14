#!/usr/bin/env bash
# Dựng sandbox khép kín từ worktree (code) + BẢN SAO dữ liệu thật. KHÔNG ghi vào data/ thật.
# Dùng: mk_sandbox.sh <đích> [worktree]. Mọi lệnh chạy trong sandbox PHẢI đặt WC_ROOT=<đích>
# (dispatch.sh export WC_ROOT trỏ cây thật, và wc_paths ưu tiên env) — dùng sbx.sh.
set -euo pipefail
R=/home/trido/thanhdt/WorkingClaude
DST="${1:?thiếu đích}"; WT="${2:-$R/mike/agents/Taylor/wt-fundlock-1014}"
case "$DST" in /tmp/*) ;; *) echo "đích phải nằm trong /tmp" >&2; exit 2;; esac
rm -rf "$DST"; mkdir -p "$DST/mike" "$DST/data"
cp -r "$WT/bin" "$DST/mike/bin"; cp -r "$WT/kb" "$DST/mike/kb"
[ -d "$WT/templates" ] && cp -r "$WT/templates" "$DST/mike/templates"
cp -r "$R/mike/reports" "$DST/mike/reports"
cp -r "$R/data/execution_logs" "$DST/data/execution_logs"
cp -r "$R/data/corp_action_daily" "$DST/data/corp_action_daily" 2>/dev/null || true
for f in account_inception.json account_cash_flows.json cash_identity_acks.json corp_actions.json \
         account_seed_capital.json trading_rules.json; do
  [ -f "$R/data/$f" ] && cp "$R/data/$f" "$DST/data/$f"
done
: > "$DST/wc_env.sh"
ln -s "$R/trading_bot" "$DST/trading_bot"
find "$DST" -name __pycache__ -prune -exec rm -rf {} +
echo "sandbox: $DST (code: $WT @ $(git -C "$WT" rev-parse --short HEAD))"
