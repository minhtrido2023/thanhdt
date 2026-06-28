#!/usr/bin/env bash
# apply_dq2_patch.sh — Apply DQ-2 fix to kaffa pipeline
# Run from: /home/trido/thanhdt/WorkingClaude/
# Requires: SSH access to kaffa (python ssh_kaffa.py must work)
# Status: STAGED 2026-06-28 by Winston — awaiting user approval for SSH

set -euo pipefail
WORKDIR="/home/trido/thanhdt/WorkingClaude"
PATCH_FILE="$WORKDIR/mike/agents/Winston/dq2_patch_staged.py"
KAFFA_WS="/workspace/kaffa_v2"
SSH="python $WORKDIR/ssh_kaffa.py"

echo "=== DQ-2 PATCH APPLY SCRIPT ==="
echo "Step 1: Find process_stock_indicator + ffill block on kaffa"

# Find the exact file and lines
$SSH "grep -rn 'process_stock_indicator\|ffill\|fillna.*NaN\|last.*row.*NaN\|combine_first' $KAFFA_WS/worker/ 2>/dev/null | grep -v '__pycache__' | grep -v '.pyc' | head -40"

echo ""
echo "Step 2: Show context around ffill in data_tasks.py"
$SSH "grep -n 'ffill\|fillna.*NaN\|fill.*last\|last.*row\|combine_first' $KAFFA_WS/worker/data_tasks.py 2>/dev/null || echo 'data_tasks.py not found — search in other files'"

echo ""
echo "Step 3: Show profit_ column references"
$SSH "grep -n 'profit_\|forward.fill\|look.ahead' $KAFFA_WS/worker/data_tasks.py 2>/dev/null | head -20"

echo ""
echo "=== Manual apply steps ==="
echo "After identifying the exact lines above, apply changes:"
echo "  1. Upload patch module:  scp $PATCH_FILE trido@192.168.100.7:$KAFFA_WS/worker/dq2_profit_fill_guard.py"
echo "  2. In data_tasks.py, find 'ffill' block in process_stock_indicator"
echo "  3. Replace with: from worker.dq2_profit_fill_guard import fill_last_row_whitelist, assert_profit_cols_null"
echo "     df = fill_last_row_whitelist(df)"
echo "  4. Before BQ append [H]: assert_profit_cols_null(df, n_recent=60)"
echo "  5. Run test: python -c 'from worker.dq2_profit_fill_guard import fill_last_row_whitelist; print(\"OK\")'"
echo ""
echo "IMPORTANT: DO NOT deploy to production until user reviews and approves."
