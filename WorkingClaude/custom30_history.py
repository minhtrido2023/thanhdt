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
import datetime as _dt
from zoneinfo import ZoneInfo
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
#
# ⚠️ THỜI ĐIỂM ĐÁNH GIÁ — fix 2026-09-30 (job Taylor_20260930_030814, user chỉ đạo sau ca PNJ:
# "nếu một năm không trả thì tự động rớt"). CÔNG THỨC KHÔNG ĐỔI (vẫn 3 cửa sổ rolling 365 ngày,
# đếm SỰ KIỆN chi trả, không ngưỡng số tiền) — chỉ ASOF đổi:
#   - kỳ rebal ĐANG MỞ  -> asof = HÔM NAY (ICT), đánh giá lại mỗi lần publisher chạy;
#   - kỳ rebal ĐÃ ĐÓNG -> asof = rebal_date, GIỮ NGUYÊN (lịch sử point-in-time, không restate).
# Trước fix mọi kỳ đều dùng asof=rebal_date ⇒ nhãn của kỳ đang mở bị ĐÓNG BĂNG tại đầu quý:
# PNJ công bố "2026 không chia cổ tức" giữa quý mà `is_stable_payer` vẫn `true` cho tới kỳ rebal
# kế tiếp (trễ tối đa ~1 năm). 3 cửa sổ 365 ngày là hàm của `asof`; asof đúng cho câu hỏi
# "mã này CÓ ĐANG trả đều không" là hôm nay, không phải một ngày đã đóng băng trong quá khứ.
# HAI LÔ, mỗi lô neo cổng freshness `corporate_action` RIÊNG (`feed_asof`) — quant-skeptic bắt
# đúng chỗ này ở vòng 1: cổng freshness là TOÀN CỤC cho một lô, nên nếu nhồi cả lịch sử và hôm
# nay vào MỘT lô thì một ngày feed cũ >4 ngày sẽ kéo CẢ 48 kỳ đã đóng về NO_DATA — tức tự phá
# đúng bất biến "không restate lịch sử" mà fix này hứa. Lô lịch sử neo ở `_cur_rd` (y nguyên
# hành vi trước fix), lô kỳ mở neo ở hôm nay.
#   Feed cũ ⇒ kỳ MỞ về NO_DATA ("không biết"), CỐ Ý không fallback về nhãn đóng băng ở
#   rebal_date: mục đích của fix là thôi trưng một `true` đã cũ, nên "không biết" đúng hơn
#   "khẳng định bằng dữ liệu cũ".
#   ⚠️ Nhãn kỳ MỞ là DISPLAY tức thời, không phải sổ lịch sử: khi kỳ rebal kế tiếp mở ra, kỳ
#   này thành "đã đóng" và nhãn quay về giá trị tại rebal_date ⇒ CSV/bảng KHÔNG lưu vết các lần
#   flip giữa quý. Nếu chương trình quan sát (review 2027-02-10) cần vết đó thì phải thêm log
#   append-only riêng — chưa làm, ngoài phạm vi fix này.
#   AI ĐỊNH GỘP LẠI THÀNH 1 LÔ: đọc `custom30_yield_labels_selfcheck.py` mục [D] trước. [D]
#   khoá HỢP ĐỒNG của `label_basket` (lô neo sớm không bị feed-cũ-so-với-hôm-nay làm trắng),
#   nhưng KHÔNG khoá được chỗ tách lô ở đây — file này là script top-level, import vào là
#   chạy nên không unit-test được. Repro tay bất biến: monkeypatch
#   `corp_action_lib.feed_freshness` về (hôm nay − 10 ngày) rồi runpy file này, so md5 phần
#   dòng của các kỳ ĐÃ ĐÓNG trong CSV — phải KHÔNG đổi, chỉ kỳ mở về NO_DATA.
_cur_rd = pd.Timestamp(rebals[-1]).date()
_today_ict = _dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()   # §16: không tin TZ process
_asof_cur = _today_ict if _today_ict > _cur_rd else _cur_rd
_is_cur = [rd == _cur_rd for rd in df["rebal_date"]]
_p_closed = [(tk, rd) for tk, rd, c in zip(df["ticker"], df["rebal_date"], _is_cur) if not c]
_p_open = [(tk, _asof_cur) for tk, c in zip(df["ticker"], _is_cur) if c]
_lab = {}
if _p_closed:
    _lab.update(yfl.label_basket(bq, _p_closed, feed_asof=_cur_rd))
if _p_open:
    _lab.update(yfl.label_basket(bq, _p_open, feed_asof=_asof_cur))
_pair = [(tk, str(_asof_cur if c else rd))
         for tk, rd, c in zip(df["ticker"], df["rebal_date"], _is_cur)]
df["yield_floor_note"] = [_lab.get(k, ("NO_DATA", None))[0] for k in _pair]
df["is_stable_payer"] = ["" if _lab.get(k, ("NO_DATA", None))[1] is None
                         else ("true" if _lab[k][1] else "false") for k in _pair]
_cur = df[df["rebal_date"] == _cur_rd]
print(f"  yield_floor (rebal {_cur_rd}, danh gia lai tai asof={_asof_cur}): " +
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
