#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dc_candidate_feeder.py — candidate feeder cho pipeline due-diligence/discretionary, nguồn tín
hiệu = Double-Confirm (DC) book (sector-lens BUY ∩ 8L rating≤2, universe 16 mã cố định
`sector_lens_monitor.NAMES`). Việc #2, job Taylor_20260831_014244 (dispatch Mike, user duyệt
2026-08-31 08:41 ICT, decided_by user), theo bối cảnh
`agents/Taylor/research/dc_3book_factor_neutral_20260830.md`.

KIẾN TRÚC — vì sao KHÔNG dùng chung `bin/discretionary_candidate_funnel.py`:
`discretionary_candidate_funnel.py` là 1 pipeline BQ chấm điểm/RANK 1 COHORT rộng (washout+dd52+
PB adaptive threshold quét TOÀN BỘ universe_pit) — output là 1 bảng rank MỚI mỗi lần chạy, KHÔNG
có khái niệm "đã thấy mã này chưa". DC hoàn toàn khác dạng: universe CỐ ĐỊNH 16 mã, tín hiệu là
MEMBERSHIP nhị phân (đã có sẵn `sector_lens_monitor.compute_status()` + `load_ratings()`, đúng
logic `dc_book_waterfall_paper.py::load_double_confirm()` — KHÔNG viết lại). Việc cần làm ở đây là
"khi nào 1 mã BẮT ĐẦU thoả DC mà hôm trước chưa thoả" — một bài toán STATEFUL (diff theo thời
gian), không phải bài toán rank. Nhét vào funnel PB-adaptive sẽ vừa tái tạo sai logic threshold
(dispatch cấm rõ) vừa làm funnel đó mất tính "1 lần chạy = 1 bảng rank sạch". Giải pháp: 1 registry
riêng, cùng QUY ƯỚC OUTPUT với funnel (RECON-only, KHÔNG auto-arm, `--print-block` để nhúng prompt)
nhưng có STATE riêng để làm diff.

CƠ CHẾ:
  1. Tính DC set HÔM NAY = sector-lens BUY ∩ 8L rating≤2 (y hệt load_double_confirm()).
  2. So với `active_members` lưu trong state file (data/dc_candidate_state.json) = tập DC set
     lần chạy TRƯỚC.
  3. Mã nào trong DC set hôm nay mà KHÔNG có trong `active_members` → 1 CANDIDATE ENTRY mới, ghi
     append vào registry (data/dc_candidate_registry.csv) — dù là lần đầu tiên (chưa từng thấy)
     hay tái xuất hiện (đã rời DC set rồi quay lại — vẫn là tín hiệu DD mới, không phải noise, vì
     8L rating hoặc sector-lens status đã đổi kể từ lần trước).
  4. Idempotent theo ngày: state có `last_run_date`; chạy lại cùng ngày (asof không đổi) → không
     ghi trùng, chỉ cập nhật `active_members` (an toàn khi cron/bus gọi nhiều lần trong ngày).
  5. Atomic write state (tmp+os.replace, coding_guidelines §5) — killed giữa chừng không làm hỏng
     file kế tiếp đọc.

Output: RECON — mỗi hàng registry là 1 gợi ý đưa qua DD (fundamental-skeptic) rồi
`discretionary_margin_gate.py`/DollarBill nếu muốn theo đuổi. KHÔNG tự động hoá gì, KHÔNG arm.

DÙNG:
    python3 mike/bin/dc_candidate_feeder.py                  # chạy, in candidate mới (nếu có)
    python3 mike/bin/dc_candidate_feeder.py --print-block    # khối text nhúng prompt LLM khác
    python3 mike/bin/dc_candidate_feeder.py --show-registry  # in toàn bộ registry tích luỹ
"""

import argparse
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

import pandas as pd

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, WC_ROOT)

ICT = ZoneInfo("Asia/Ho_Chi_Minh")  # §16: neo múi giờ tường minh

DATA_DIR = os.path.join(WC_ROOT, "data")
STATE_FILE = os.path.join(DATA_DIR, "dc_candidate_state.json")
REGISTRY_CSV = os.path.join(DATA_DIR, "dc_candidate_registry.csv")

REGISTRY_COLS = ["event_date", "ticker", "event", "sector", "buy_mode", "rating",
                  "primary", "value", "reference", "reason", "logged_at_ict"]


def _now_ict_iso():
    return dt.datetime.now(ICT).isoformat()


def live_dc_status():
    """Trả (rows:list[dict], asof:str|None). Mỗi row = 1 mã trong DC set hôm nay (status==BUY
    ∧ rating<=2), kèm context (sector/buy_mode/primary/value/reference/reason) từ
    sector_lens_monitor.compute_status() để feed DD. None asof = lỗi đọc cache (fail-safe:
    caller KHÔNG được suy diễn "không có candidate" từ lỗi này)."""
    import sector_lens_monitor as slm
    r = slm.compute_status()
    ratings = slm.load_ratings()
    df = r["df"]
    asof = str(df["date"].iloc[0]) if len(df) else None
    rows = []
    for _, row in df[df["status"] == "BUY"].iterrows():
        tk = str(row["ticker"])
        rt = ratings.get(tk)
        if rt is None or int(rt) > 2:
            continue
        rows.append({
            "ticker": tk, "sector": row.get("sector", ""),
            "buy_mode": row.get("buy_mode") or "ACCUMULATE",
            "rating": int(rt), "primary": row.get("primary", ""),
            "value": row.get("value", ""), "reference": row.get("reference", ""),
            "reason": row.get("reason", ""),
        })
    return rows, asof


def _load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def _save_state(st):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_FILE)  # atomic


def _append_registry(new_rows):
    if not new_rows:
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    exists = os.path.exists(REGISTRY_CSV)
    df = pd.DataFrame(new_rows, columns=REGISTRY_COLS)
    df.to_csv(REGISTRY_CSV, mode="a", header=not exists, index=False)


def run(dry_run=False):
    """Trả (new_candidates:list[dict], asof:str|None, status:str). status ∈
    {no_data, unchanged, advanced}. KHÔNG raise — lỗi đọc dữ liệu (import/cache) là fail-safe
    'no_data', giữ nguyên state cũ (không xoá active_members đã biết)."""
    st = _load_state() or {"active_members": [], "last_run_date": None}

    try:
        rows, asof = live_dc_status()
    except Exception as e:
        return [], None, f"no_data ({e})"

    if asof is None:
        return [], None, "no_data (compute_status trả rỗng)"

    cur_members = {r["ticker"] for r in rows}
    prev_members = set(st.get("active_members", []))
    already_run_today = st.get("last_run_date") == asof

    new_tickers = cur_members - prev_members
    new_rows = []
    if new_tickers and not already_run_today:
        logged_at = _now_ict_iso()
        by_ticker = {r["ticker"]: r for r in rows}
        for tk in sorted(new_tickers):
            r = by_ticker[tk]
            event = "re_entry" if tk in _all_ever_seen() else "new_entry"
            new_rows.append({
                "event_date": asof, "ticker": tk, "event": event,
                "sector": r["sector"], "buy_mode": r["buy_mode"], "rating": r["rating"],
                "primary": r["primary"], "value": r["value"], "reference": r["reference"],
                "reason": r["reason"], "logged_at_ict": logged_at,
            })

    if not dry_run:
        if new_rows:
            _append_registry(new_rows)
        st["active_members"] = sorted(cur_members)
        st["last_run_date"] = asof
        _save_state(st)

    status = "unchanged" if already_run_today else "advanced"
    return new_rows, asof, status


def _all_ever_seen():
    """Set ticker đã từng xuất hiện trong registry (để phân biệt new_entry vs re_entry).
    Registry chưa tồn tại → set rỗng (mọi candidate đầu tiên đều new_entry)."""
    if not os.path.exists(REGISTRY_CSV):
        return set()
    try:
        df = pd.read_csv(REGISTRY_CSV, usecols=["ticker"])
        return set(df["ticker"].astype(str))
    except Exception:
        return set()


def format_block(new_rows, asof, status):
    lines = [f"=== DC candidate feeder — {_now_ict_iso()} (asof {asof or '?'}, {status}) ==="]
    if status.startswith("no_data"):
        lines.append(f"  ⚠️ {status} — giữ nguyên registry/state cũ, không suy diễn gì thêm")
        return "\n".join(lines)
    if not new_rows:
        lines.append("  (không có mã DC mới hôm nay — registry không đổi)")
        return "\n".join(lines)
    for r in new_rows:
        lines.append(
            f"  {r['ticker']:6} [{r['event']}] sector={r['sector']} mode={r['buy_mode']} "
            f"rating={r['rating']} primary={r['primary']} value={r['value']} "
            f"ref={r['reference']} — {r['reason']}")
    lines.append("  → RECON only, chưa arm. Đưa qua fundamental-skeptic/DD rồi mới cân nhắc plan.")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--print-block", action="store_true", help="in khối text gọn nhúng prompt")
    ap.add_argument("--show-registry", action="store_true", help="in toàn bộ registry tích luỹ")
    ap.add_argument("--dry-run", action="store_true", help="tính candidate mới nhưng KHÔNG ghi state/registry")
    args = ap.parse_args()

    if args.show_registry:
        if not os.path.exists(REGISTRY_CSV):
            print("(registry rỗng — chưa từng chạy hoặc chưa có candidate nào)")
            return 0
        print(pd.read_csv(REGISTRY_CSV).to_string(index=False))
        return 0

    new_rows, asof, status = run(dry_run=args.dry_run)
    if args.print_block:
        print(format_block(new_rows, asof, status))
    else:
        print(f"[{_now_ict_iso()}] asof={asof} status={status} n_new={len(new_rows)}")
        for r in new_rows:
            print(f"  {r['ticker']} [{r['event']}] rating={r['rating']} mode={r['buy_mode']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
