# -*- coding: utf-8 -*-
"""indicator_monitor.py — audit tool (Kaffa-style "Monitor"): daily list of tickers missing
one or more indicator columns needed by the live BAL signal (SIGNAL_V11) or the 8L rating
(rating_8l.py, incl. golden-floor ROE_Min3Y/CF_OA_3Y). Pure observability — does not change
any filter/rating logic. Context: mike/kb/projects/kaffa-comparison-20260910.md ("Monitor").

Scope: same liquidity floor SIGNAL_V11 already uses (Volume_3M_P50*Price >= 1e9 VND) — a name
below that floor is excluded from BAL regardless of data completeness, so it is not actionable
noise here (matches [[dataops-completeness-universe]]: illiquid tail can lag, don't block on it).

Column lists are copied from (not imported from, to avoid triggering their heavy pipelines):
  - BAL_COLS: hit_details.py (== signal_v11_sql.py SIGNAL_V11 `ta` inputs) — checked for drift
    below (_check_bal_cols_in_sync), full parity with hit_details.py's list.
  - RATING_MAIN_COLS / RATING_FIN_COLS: NOT the full rating_8l.py MAIN_SQL/FIN_SQL SELECT lists —
    a curated subset of columns rating_8l.py actually consumes downstream in Python scoring
    (golden floor ROE_Min3Y/CF_OA_3Y, cfo_np/core_score via CF_OA_P0-P3, ps/div_yield via
    Price/Dividend_Min3Y). Deliberately excludes columns only consumed inside rating_8l's own BQ
    SQL for a server-side aggregate (GPM_P1-7, Revenue_P1-7, NP_P2/P3/P5-P7 feed the `neg_q`
    COUNTIF and never reach Python as individual fields) — flagging those as "missing" here would
    be noise, not a real scoring blind spot. Keep RATING_MAIN_COLS/RATING_FIN_COLS in sync by hand
    if rating_8l.py starts consuming a new raw column in its Python scoring.

Usage: python3 indicator_monitor.py [DATE]  (DATE optional, informational only — this tool
always reads the LATEST row per table, since that's what live screening reads)
Output: data/indicator_monitor_<DATE>.md
"""
import ast
import os, sys
from datetime import datetime
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)

import pandas as pd
from simulate_holistic_nav import bq

DATADIR = os.path.join(WORKDIR, "data")

# same column list as hit_details.py's BAL_COLS (signal_v11_sql.py `ta` inputs) — checked for
# drift below (_check_bal_cols_in_sync) by parsing hit_details.py's source, without importing
# it (importing would pull in its BQ/lag_live_schedule pipeline).
BAL_COLS = ["Close", "D_RSI", "MA20", "MA50", "MA200", "MA50_T1", "Close_T1", "Volume",
            "Volume_3M_P50", "D_MACDdiff", "D_RSI_Max1W", "HI_3M_T1", "ID_HI_3Y",
            "PE", "PE_MA5Y", "PE_SD5Y", "FSCORE", "NP_P0", "NP_P1", "NP_P4", "ICB_Code"]


def _check_bal_cols_in_sync():
    hit_details_path = os.path.join(WORKDIR, "hit_details.py")
    tree = ast.parse(open(hit_details_path, encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "BAL_COLS" for t in node.targets
        ):
            other = ast.literal_eval(node.value)
            if other != BAL_COLS:
                sys.exit(
                    "BAL_COLS lệch giữa indicator_monitor.py và hit_details.py — "
                    "cập nhật cả hai file cho khớp trước khi chạy tiếp."
                )
            return
    sys.exit(f"Không tìm thấy BAL_COLS trong {hit_details_path} — kiểm tra lại tên biến.")


_check_bal_cols_in_sync()

# rating_8l.py MAIN_SQL columns (ticker_1m, latest date) actually consumed in Python scoring —
# golden-floor half = ROE_Min3Y; Price/OShares feed ps (sales_yield); Dividend_Min3Y feeds
# div_yield; CF_OA_P0-P3 feed cfo_np/core_score (see rating_8l.py:614).
RATING_MAIN_COLS = ["ROIC3Y", "ROIC_Min3Y", "ROE_Min3Y", "ROIC_Trailing", "ROIC5Y",
                     "ROIC_Min5Y", "ROE_Min5Y", "ROE5Y", "Debt_Eq_P0", "FSCORE",
                     "PB", "PE", "PCF", "EVEB", "Close", "Price", "OShares", "Dividend_Min3Y",
                     "CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3"]
# rating_8l.py FIN_SQL columns (ticker_financial, latest per ticker) actually consumed in Python
# scoring — golden-floor half = CF_OA_3Y. GPM_P1-7/Revenue_P1-7/NP_P2-P3/P5-P7 deliberately
# excluded: only feed the SQL-side `neg_q` COUNTIF, never reach Python individually.
RATING_FIN_COLS = ["CF_OA_3Y", "CF_OA_5Y", "ROE_Trailing", "ROE3Y", "STLTDebt_Eq_P0",
                    "GPM_P0", "Revenue_P0", "UnearnRev_P0", "totalAsset_P0"]
GOLDEN_FLOOR_COLS = {"ROE_Min3Y", "CF_OA_3Y"}


def fetch_universe_and_bal():
    cols = ",".join(f"t.{c}" for c in sorted(set(BAL_COLS) | set(RATING_MAIN_COLS)))
    df = bq(f"""
        WITH L AS (SELECT MAX(time) mx FROM tav2_bq.ticker_1m)
        SELECT t.ticker, {cols},
          t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS liq
        FROM tav2_bq.ticker_1m AS t, L
        WHERE t.time = L.mx
    """)
    return df[df["liq"] >= 1e9].copy()   # same floor SIGNAL_V11 already enforces


def fetch_rating_fin(tickers):
    if not tickers:
        return pd.DataFrame(columns=["ticker"] + RATING_FIN_COLS)
    tl = ",".join(f"'{t}'" for t in sorted(set(tickers)))
    cols = ",".join(RATING_FIN_COLS)
    return bq(f"""
        SELECT ticker, {cols} FROM (
          SELECT t.*, ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) rn
          FROM tav2_bq.ticker_financial AS t WHERE t.ticker IN ({tl}))
        WHERE rn = 1
    """)


def missing_cols(row, cols):
    return [c for c in cols if c not in row or pd.isna(row[c])]


def main():
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now(_ICT).strftime("%Y-%m-%d")

    uni = fetch_universe_and_bal()
    if uni.empty:
        sys.exit("Universe (ticker_1m latest date, liq>=1e9) rỗng — kiểm tra freshness BQ trước.")

    fin = fetch_rating_fin(uni["ticker"].tolist())
    fin_idx = fin.set_index("ticker") if len(fin) else pd.DataFrame()

    rows = []
    for _, r in uni.iterrows():
        t = r["ticker"]
        miss_bal = missing_cols(r, BAL_COLS)
        miss_rating_main = missing_cols(r, RATING_MAIN_COLS)
        fin_row = fin_idx.loc[t] if t in fin_idx.index else pd.Series(dtype=float)
        miss_rating_fin = missing_cols(fin_row, RATING_FIN_COLS) if len(fin_row) else list(RATING_FIN_COLS)
        miss_rating = miss_rating_main + miss_rating_fin
        if not (miss_bal or miss_rating):
            continue
        golden_hit = bool(GOLDEN_FLOOR_COLS & set(miss_rating))
        rows.append({"ticker": t, "miss_bal": miss_bal, "miss_rating": miss_rating,
                     "golden_floor_affected": golden_hit})

    rows.sort(key=lambda x: (not x["golden_floor_affected"], -len(x["miss_bal"]) - len(x["miss_rating"])))

    lines = [f"# Indicator Monitor — {date}\n",
             f"Universe: `tav2_bq.ticker_1m` ngày mới nhất, lọc `liq = Volume_3M_P50*Price >= 1e9` "
             f"(sàn thanh khoản SIGNAL_V11 đã dùng) — {len(uni)} mã. Công cụ audit thuần — KHÔNG đổi "
             f"logic rating/filter. Xem `kb/coding_guidelines.md` §9/§29.\n",
             f"{len(rows)}/{len(uni)} mã thiếu ≥1 cột cần cho BAL (SIGNAL_V11) hoặc 8L rating "
             f"(rating_8l.py, `{sorted(GOLDEN_FLOOR_COLS)}` = golden floor).\n",
             "_Lưu ý đọc bảng: index/ETF (VNINDEX, VN30, E1VFVN30...) thiếu toàn bộ cột tài chính "
             "là BÌNH THƯỜNG (không có BCTC) — không phải data gap. `UnearnRev_P0` thiếu ở NGÂN "
             "HÀNG cũng vậy (không có doanh thu chưa thực hiện). Cả hai vẫn được liệt kê nguyên "
             "văn (tool không tự loại trừ theo ngành) — người đọc tự lọc theo ICB khi cần._\n"]

    if not rows:
        lines.append("_Không có mã nào thiếu cột — sạch._")
    else:
        lines.append("| Ticker | Golden floor? | Thiếu (BAL/SIGNAL_V11) | Thiếu (8L rating) |")
        lines.append("|---|---|---|---|")
        for r in rows:
            gf = "⚠️ CÓ" if r["golden_floor_affected"] else ""
            lines.append(f"| {r['ticker']} | {gf} | {r['miss_bal'] or ''} | {r['miss_rating'] or ''} |")

    out_path = os.path.join(DATADIR, f"indicator_monitor_{date}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(lines) + "\n")
    print(f"Viết {out_path} ({len(rows)}/{len(uni)} mã thiếu cột)")


if __name__ == "__main__":
    main()
