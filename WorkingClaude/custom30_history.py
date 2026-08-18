# -*- coding: utf-8 -*-
"""custom30_history.py — PUBLISHER for the "8L custom30" parking basket -> BQ table
`tav2_bq.custom30_8l` (single source of truth; consumers query instead of re-running build_pit).
Construction = custompitg + namecap (cap-weight, each name <=10%; data-chosen 2026-06-15).
Per quarterly rebalance (q2m5): the 30 members with as-of 8L rating, liquidity rank, and the
namecap REFERENCE weight at the rebal date. Run in the daily pipeline (cheap; basket only moves
quarterly + on fa_ratings_8l republish). Lookup today's basket:
  SELECT ticker,weight FROM tav2_bq.custom30_8l
  WHERE rebal_date=(SELECT MAX(rebal_date) FROM tav2_bq.custom30_8l WHERE rebal_date<=CURRENT_DATE())
"""
import os, sys, subprocess
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
from pt_dates import detect_end_date
import custom_basket as cb
import custom30_yield_labels as yfl

NAME_CAP = 0.10
START = "2014-01-02"; END = detect_end_date()
# TABLE/CSV env-overridable (2026-06-17). Since 2026-07-11 papertrade_daily.sh runs this TWICE:
# [6] default env -> custom30_8l (blend, legacy/audit) and [6b] BASKET_SELECT=yieldcombo +
# CUSTOM30_TABLE=custom30v_8l -> the V2.4 PRODUCTION parking basket golive_recommend_v23.py reads.
TABLE = os.environ.get("CUSTOM30_TABLE", "lithe-record-440915-m9:tav2_bq.custom30_8l")
CSV = os.path.join(WORKDIR, "data", os.environ.get("CUSTOM30_CSV", "custom30_8l_publish.csv"))
BQ = r"bq"

print(f"building 8L custom30 (namecap {NAME_CAP:.0%}) {START} -> {END} ...")
lvl, adv, memdf, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                   gate_rating=3, weight_scheme="namecap")
bx["time"] = pd.to_datetime(bx["time"])
memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"])
rebals = sorted(memdf["rebal_date"].unique())
adv_s = pd.Series(adv)  # date -> basket ADV (parkable capacity ref)

rows = []
for i, rd in enumerate(rebals):
    rd = pd.Timestamp(rd)
    mem = memdf[memdf["rebal_date"] == rd].sort_values("liq_rank")
    tks = list(mem["ticker"])
    sub = bx[(bx["ticker"].isin(tks)) & (bx["time"] <= rd)]
    # PRICE BASIS — WEIGHT leg uses `mcapw` (raw PIT COALESCE(Price,Close) x OShares), NOT `mcap`
    # (retroactively-adjusted Close x OShares, which is build_pit's RETURN leg). See the PRICE BASIS
    # block in custom_basket.py and mike/kb/data_registry/price-volume/
    # ticker_close_vs_price_dividend_adj.md. This is a cross-sectional weight AT ONE DATE, so it
    # must not be built from a series that gets restated afterwards.
    #   Why it mattered here specifically (job Taylor_20260802_141725, step 5): this publisher is
    #   re-run EVERY session by papertrade_daily.sh [6b], but `rebal_date` only moves quarterly --
    #   so with `mcap` the published weights of a FIXED past rebal silently drifted every time a
    #   member went ex-dividend. Measured on the live 2026-05-05 rebal at the 2026-07-29 vintage:
    #   18/30 members already had Close/Price != 1.00 (ACB 0.862, IDC 0.873), sum|dw| = 1.65pp,
    #   max single name 0.478pp (ACB). On 2026-05-05 itself the factor was 1.00 for all 30, i.e.
    #   the weights were right the day they were published and decayed from there. `Price` is never
    #   restated, so the fixed weights are stable. Membership is unaffected (it comes from `memdf`).
    mc = sub.sort_values("time").groupby("ticker")["mcapw"].last().reindex(tks)
    mc = mc.fillna(0.0)
    base = (mc / mc.sum()).values if mc.sum() > 0 else np.ones(len(tks)) / len(tks)
    w = cb._cap_names(base, NAME_CAP)
    eff_to = (pd.Timestamp(rebals[i + 1]) - pd.Timedelta(days=1)).date() if i + 1 < len(rebals) else ""
    for j, (_, r) in enumerate(mem.iterrows()):
        rows.append(dict(
            rebal_date=rd.date(), effective_from=rd.date(), effective_to=eff_to,
            ticker=r["ticker"], liq_rank=int(r["liq_rank"]),
            rating_8l=(int(r["rating"]) if pd.notna(r["rating"]) else ""),
            weight=round(float(w[j]), 6), quarter=str(r["quarter"])))
df = pd.DataFrame(rows)

# --- nhãn QUAN SÁT yield_floor (Phase 1 Option C, 2026-08-18, job Taylor_20260818_134610) ------
# Chạy SAU khi `rows` đã đóng: rổ đã chọn xong, weight đã cap xong. Hai cột này KHÔNG quay lại
# ảnh hưởng `mem`/`w`/thứ tự — thuần quan sát cho chương trình `yield_floor_custom30v_observe`
# (review 2027-02-10, `mike/kb/paper_programs_registry.json`). Fail-open: `label_basket()` không
# bao giờ raise; cặp nào hỏng về ("NO_DATA", None). Xem custom30_yield_labels.py.
_lab = yfl.label_basket(bq, list(zip(df["ticker"], df["rebal_date"])))
_pair = list(zip(df["ticker"], df["rebal_date"].astype(str)))
df["yield_floor_note"] = [_lab.get(k, ("NO_DATA", None))[0] for k in _pair]
df["is_stable_payer"] = ["" if _lab.get(k, ("NO_DATA", None))[1] is None
                         else ("true" if _lab[k][1] else "false") for k in _pair]
_cur = df[df["rebal_date"] == pd.Timestamp(rebals[-1]).date()]
print("  yield_floor (rebal hien tai): " +
      ", ".join(f"{k}={v}" for k, v in _cur["yield_floor_note"].value_counts().items()))
df.to_csv(CSV, index=False, encoding="utf-8")
print(f"  {len(df)} rows, {len(rebals)} rebals -> {CSV}")

# `bq load --replace` ghi lai CA schema lan du lieu ⇒ 2 cot moi khong can ALTER TABLE.
schema = ("rebal_date:DATE,effective_from:DATE,effective_to:DATE,ticker:STRING,"
          "liq_rank:INTEGER,rating_8l:INTEGER,weight:FLOAT,quarter:STRING,"
          "yield_floor_note:STRING,is_stable_payer:BOOLEAN")
cmd = f'"{BQ}" load --replace --source_format=CSV --skip_leading_rows=1 {TABLE} "{CSV}" {schema}'
print("  bq load ...")
r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
print(r.stdout.strip()); print(r.stderr.strip())
if r.returncode != 0:
    print("LOAD FAILED"); sys.exit(1)
print(f"OK -> {TABLE}  (current rebal {pd.Timestamp(rebals[-1]).date()}, {df[df['rebal_date']==pd.Timestamp(rebals[-1]).date()].shape[0]} mã)")
