# -*- coding: utf-8 -*-
"""
publish_gated_state.py  —  LAYER 1 (DT5G state engine) publisher.

Computes today's FAIL-SAFE gated market-state series (DT5G macro overlay, auto-reverting
to DT4-only when macro_healthcheck flags the feeds) via macro_state_live.get_gated_state,
then publishes it so the production recommender (LAYER 2) can consume it:
  - BQ table  tav2_bq.vnindex_5state_dt5g_live   (state,state_raw) — read by golive_recommend's SIGNAL_V11
  - local CSV vnindex_5state_dt5g_live.csv        (mirror / audit)
  - golive_state_today.json                       (today's state + source + provenance)

PRECONDITIONS (run earlier in golive_daily.bat): pull_us_market -> rebuild_state_from_ticker
-> macro_healthcheck (writes data/macro_health.json that the gate reads).

Run: python deploy_golive_dt5g_v4/publish_gated_state.py
"""
import os, sys, io, json
from datetime import datetime
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

# This publisher MUST read the base state from LIVE BigQuery, never the local DuckDB cache:
# wc_env.sh exports BQ_LOCAL_CACHE globally, which silently routes simulate_holistic_nav.bq
# through the 23:45-synced cache (always T-1 at the 18:30/19:00 publish slots) — so the
# published dt5g_live series lagged the just-refreshed v34b_clean base by >=1 session and can
# never pass bq_freshness_check's MAX_STATE_LAG=0 gate. Unset here (process-local; cache
# consumers like papertrade/sims/backtests are unaffected). Audit: Winston_20260712_142100 C1.
os.environ.pop("BQ_LOCAL_CACHE", None)

from macro_state_live import get_gated_state

PROJECT = "lithe-record-440915-m9"
BQ_TABLE = f"{PROJECT}:tav2_bq.vnindex_5state_dt5g_live"
WARMUP_START = "2014-01-01"     # SIGNAL_V11 state-join needs history; gate warms DT4 from 2014
END = datetime.now().strftime("%Y-%m-%d")
LOCAL_CSV = os.path.join(WORKDIR, "data/vnindex_5state_dt5g_live.csv")
STATE_JSON = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "golive_state_today.json")

print("=" * 88); print(f"  PUBLISH GATED STATE (DT5G, fail-safe)  -> {END}"); print("=" * 88)

g = get_gated_state(WARMUP_START, END)          # [time, state, base_state, macro_state, source]
out = pd.DataFrame({"time": pd.to_datetime(g["time"]).dt.strftime("%Y-%m-%d"),
                    "state": g["state"].astype(int),
                    "state_raw": g["base_state"].astype(int)})   # state_raw = DT4 base (audit)
print(f"  recomputed series: {len(out)} rows, {out['time'].iloc[0]} -> {out['time'].iloc[-1]}")

# ── LOCAL_CSV giờ được ghi SAU khi publish, và ghi TỪ BẢNG BQ ĐÃ CÔNG BỐ ──────────────────
# TRƯỚC ĐÂY: ghi `out` (chuỗi VỪA TÍNH LẠI) ra CSV ngay tại đây, rồi publish cùng chuỗi đó —
# CSV và BQ luôn khớp vì cả hai đều là bản tính mới. Với publish bất biến thì KHÔNG còn vậy:
# BQ giữ lịch sử ĐÃ CHỐT, còn `out` chứa lịch sử ĐÃ BỊ RESTATE (101 phiên hôm 07-29). Ghi `out`
# ra CSV sẽ tạo ra hai nguồn LỆCH NHAU cho cùng một chuỗi — và tệ nhất là lệch đúng ở phía sai:
# ~7 script nghiên cứu/backtest (f_sleeve_pt.py, crisis_release.py, f_protect_v4v5_test.py,
# f_system_improve_test.py, f_fast_hedge_test.py, test_crisis_release_nav.py,
# analyze_vix_peak_bottom.py) đọc TRỰC TIẾP CSV này làm chuỗi DT5G. Đó chính là nhóm consumer
# CẦN chuỗi point-in-time nhất (backtest 2018 không được dùng state tính bằng PE backfill 2026 —
# lý do gốc của cả thiết kế này, §5 rolling_vs_expanding_dt5g_20260729.md).
# GIỜ: publish trước, rồi export CSV TỪ BQ ⇒ CSV == bảng công bố, mọi consumer CSV tự động
# nhận chuỗi đã chốt, KHÔNG phải sửa 7 script kia.
# Publish HỎNG ⇒ KHÔNG ghi CSV: giữ bản cũ, vẫn khớp BQ (BQ cũng không đổi). Không bao giờ để
# CSV chạy trước BQ.
# Schema CSV giữ NGUYÊN [time,state,state_raw] — cố ý KHÔNG thêm `asof_date` vào CSV để không
# đụng 7 consumer nói trên; `asof_date` là cột audit, sống ở bảng BQ.
#
# publish to BQ so SIGNAL_V11 reads the gated series.
# ── BẢNG CÔNG BỐ BẤT BIẾN (2026-07-30, job Taylor_20260730_013951) ────────────────────────
# TRƯỚC ĐÂY: `bq load --replace` — đè TOÀN BỘ bảng mỗi đêm. Vì chain rebuild cả lịch sử từ
# upstream có thể restate (PE backfill, corp-action, universe membership) qua các cửa sổ
# EXPANDING, state của phiên đã đóng nhiều năm trước bị VIẾT LẠI im lặng (2026-07-29: 101
# phiên ở chính bảng này, 35 phiên lệch >=2 tier — RCA dt5g_history_restate_rca_20260729.md).
# GIỜ: state của phiên đã công bố là SỰ KIỆN ĐÃ XẢY RA. Publisher chỉ append phiên mới +
# recompute đuôi 25 phiên chưa chốt; phần đã chốt KHÔNG BAO GIỜ nằm trong phạm vi câu lệnh
# ghi. Không đổi một dòng CÔNG THỨC nào — chỉ đổi CÁCH GHI (rủi ro mô hình = 0).
# Chi tiết + cơ sở chọn N=25: state_publish_immutable.py (docstring).
from state_publish_immutable import publish_immutable, PublishAbort, export_published_csv

BQ_DS_TABLE = BQ_TABLE.split(":")[1]
publish_ok = True
try:
    stats = publish_immutable(out, BQ_DS_TABLE, "vnindex_5state_dt5g_live (PRODUCTION)")
    print(f"  published -> BQ {BQ_TABLE} (bất biến: đã chốt {stats.get('n_sealed_rows')} dòng, "
          f"đuôi {stats.get('n_tail_rows')} dòng)")
except PublishAbort as e:
    publish_ok = False
    print(f"  !!! PUBLISH ABORT: {e}")
except Exception as e:
    publish_ok = False
    print(f"  !!! PUBLISH FAILED (unexpected): {e}")

if publish_ok:
    # CSV = ảnh chụp bảng ĐÃ CÔNG BỐ (không phải chuỗi vừa tính lại) — xem giải thích ở trên.
    try:
        n = export_published_csv(BQ_DS_TABLE, LOCAL_CSV)
        print(f"  wrote {LOCAL_CSV} ({n} rows) = ảnh chụp bảng đã công bố (KHÔNG phải bản tính lại)")
    except Exception as e:
        # CSV cũ vẫn khớp BQ ở phần đã chốt; chỉ thiếu đuôi mới. Không làm publish thất bại.
        print(f"  WARN: không export được CSV mirror từ BQ ({e}) — giữ bản cũ, BQ vẫn ĐÚNG.")
else:
    print(f"  giữ nguyên {LOCAL_CSV} (publish hỏng ⇒ CSV không được chạy trước BQ)")

last = g.iloc[-1]
prov = {"published_at": datetime.now().isoformat(timespec="seconds"),
        "as_of": str(pd.to_datetime(last["time"]).date()),
        "state": int(last["state"]),
        "base_state_dt4": int(last["base_state"]),
        "macro_state_dt5g": int(last["macro_state"]),
        "source": str(last["source"]),
        "bq_table": BQ_TABLE.split(":")[1],
        "bq_publish_ok": publish_ok}
os.makedirs(os.path.dirname(STATE_JSON), exist_ok=True)
json.dump(prov, open(STATE_JSON, "w", encoding="utf-8"), indent=2)
print(f"  today: as_of={prov['as_of']} state={prov['state']} source={prov['source']} "
      f"(DT4={prov['base_state_dt4']}, DT5G={prov['macro_state_dt5g']})")
print(f"  wrote {STATE_JSON}")
# Trước đây BQ load hỏng chỉ in WARNING rồi exit 0 => publish thất bại LẶNG LẼ. Giờ exit!=0.
# Caller (daily_refresh_v34b_linux.sh step [12]) alert nhưng KHÔNG die: để step [14]
# macro_healthcheck vẫn chạy — health report đứng im sẽ khiến get_gated_state fail-closed về
# DT4 (BỎ macro cap), tức kém phòng thủ hơn, nên không được để publish hỏng kéo theo nó chết.
if not publish_ok:
    print("DONE (with PUBLISH FAILURE).")
    sys.exit(1)
print("DONE.")
