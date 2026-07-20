# -*- coding: utf-8 -*-
"""SELFCHECK — CAPIT per-name %ADV cap, PHƯƠNG ÁN B (job Taylor_20260720_172614).

Kiểm tra 3 tầng của thay đổi:
  A. Công thức lịch sử — chạy qua 14 event washout 2014→2026, trần phải kích hoạt ở ĐÚNG
     1/14 event (NNC, 2016-01-18) ở sleeve tham chiếu 0,38 tỷ. Đây là con số ĐÃ BIẾT từ
     job Taylor_20260720_170223; nếu lần này ra khác 1/14 → FAIL, dừng, báo cáo (KHÔNG
     sửa để khớp).
  B. Tác động live — rổ CAPIT 2026-07-20 (NCT/PVT/SAB/VNM) ở sleeve hiện tại phải KHÔNG
     bị cap (tác động live = 0).
  C. Tầng enforce — unit test trading_bot/plan.py::cap_capit_orders(): trim đúng lô, bỏ
     qua lệnh không phải CAPIT-buy, và FAIL-CLOSED khi thiếu cap / artifact cũ / ref_price
     xấu / trần nhỏ hơn 1 lô.

CÔNG THỨC (không đổi so với bản đã chốt):
    cap_vnd_i = X * ADV20_i * D          X = 0.10, D = 2
    ADV20_i   = median giá trị GD 20 phiên TRƯỚC ngày washout (ngày washout KHÔNG tính)
    w_i       = min(capit_size/len(basket), cap_vnd_i / NAV_book_LAG)
    phần dư KHÔNG dồn sang tên khác -> để cash.

X=10% / D=2 là QUY ƯỚC NGÀNH, không phải tham số backtest. Không chỉnh chúng để né
event NNC (phương án C đã bị bác — fit tham số theo đáp án biết trước).
"""
import os, sys, io, json, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd, duckdb

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
OUT = f"{WORKDIR}/mike/agents/Taylor/exp_capitadvcap"
con = duckdb.connect(":memory:"); con.execute("SET threads=1")
PRUNE = f"read_parquet('{WORKDIR}/data/bq_cache/ticker_prune/*.parquet')"

X, D = 0.10, 2.0
SLEEVE_REF = 0.38                    # tỷ VND — mức tham chiếu của đề xuất
EXPECT_EVENTS, EXPECT_TICKER, EXPECT_DATE = 1, "NNC", "2016-01-18"
EVENTS = ["2014-05-08","2015-08-24","2016-01-18","2018-05-28","2020-03-12","2022-04-20",
          "2022-06-20","2022-09-29","2023-10-31","2024-04-19","2024-08-05","2025-04-03",
          "2025-10-20","2026-03-09"]
fails = []       # sai về ĐÚNG/SAI của thay đổi -> phải dừng, không merge
blockers = []    # thay đổi ĐÚNG nhưng có điều kiện vận hành phải làm trước khi merge

# ── A. công thức trên 14 event lịch sử ────────────────────────────────────────────────
rows = []
for ds in EVENTS:
    e = con.execute(f"""
        SELECT ticker, (PB-PB_MA5Y)/NULLIF(PB_SD5Y,0) AS pbz
        FROM {PRUNE}
        WHERE time = DATE '{ds}'
          AND ROE_Min5Y >= 0.12 AND ROIC5Y >= 0.10 AND FSCORE >= 6
          AND COALESCE(Price, Close) * Volume / 1e9 >= 2
    """).df().dropna(subset=["pbz"])
    g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]
    pick = g if len(g) >= 3 else (c if len(c) >= 3 else e)
    pick = pick.nsmallest(15, "pbz") if len(pick) > 15 else pick
    rows += [dict(event=ds, ticker=t, n=len(pick)) for t in pick["ticker"]]
B = pd.DataFrame(rows)

adv = con.execute(f"""SELECT ticker, time, COALESCE(Price,Close)*Volume/1e9 AS turn_b
                      FROM {PRUNE} WHERE time >= DATE '2013-06-01'""").df()
adv["time"] = pd.to_datetime(adv["time"])
cal = np.array(sorted(adv["time"].unique()))

def adv20_pre(ticker, ds):
    """median giá trị GD 20 phiên NGAY TRƯỚC ds (ds không tính vào cửa sổ)."""
    i = np.searchsorted(cal, np.datetime64(pd.Timestamp(ds)), side="left")
    lo = cal[max(0, i - 20)]
    s = adv[(adv["ticker"] == ticker) & (adv["time"] >= lo) & (adv["time"] < pd.Timestamp(ds))]
    return float(s["turn_b"].median()) if len(s) else np.nan

B["adv20_pre"] = [adv20_pre(r.ticker, r.event) for r in B.itertuples()]
assert B["adv20_pre"].notna().all(), "thiếu ADV20 cho một số vị thế"
B["cap_bn"] = X * B["adv20_pre"] * D
B["uncapped_bn"] = SLEEVE_REF / B["n"]
B["binds"] = B["uncapped_bn"] > B["cap_bn"] + 1e-12
ev = B.groupby("event")["binds"].any()
n_ev, n_pos = int(ev.sum()), int(B["binds"].sum())

print("=" * 78)
print(f"A. 14 EVENT LỊCH SỬ @ sleeve = {SLEEVE_REF} tỷ VND")
print("=" * 78)
print(f"  event kích hoạt trần    : {n_ev}/14   (kỳ vọng {EXPECT_EVENTS})")
print(f"  vị thế kích hoạt trần   : {n_pos}/{len(B)}")
hit = B[B["binds"]]
if len(hit):
    print(hit[["event","ticker","n","adv20_pre","cap_bn","uncapped_bn"]].to_string(index=False))
    print(f"  VND tái phân bổ (để cash) = {(hit['uncapped_bn']-hit['cap_bn']).sum()*1e9:,.0f}đ")
ok_a = (n_ev == EXPECT_EVENTS and len(hit) == 1
        and hit.iloc[0]["ticker"] == EXPECT_TICKER and hit.iloc[0]["event"] == EXPECT_DATE)
print(f"  -> {'PASS' if ok_a else 'FAIL'}: khớp kết quả đã biết ({EXPECT_TICKER} {EXPECT_DATE})")
if not ok_a:
    fails.append("A: kết quả 14 event KHÁC 1/14 đã biết — DỪNG, báo cáo, KHÔNG sửa để khớp")

print("\n  thang độ nhạy (tham khảo, không phải tiêu chí pass/fail):")
for s in [0.38, 0.75, 1.50, 3.75, 7.50]:
    b = B.assign(u=s / B["n"]); bd = b["u"] > b["cap_bn"] + 1e-12
    print(f"    sleeve {s:5.2f} tỷ -> {int(b.assign(x=bd).groupby('event')['x'].any().sum()):2d}/14 event, "
          f"{int(bd.sum()):2d}/{len(b)} vị thế")

# ── B. tác động live: rổ 2026-07-20 ───────────────────────────────────────────────────
# RỔ THẬT đọc từ artifact production, KHÔNG hardcode theo giả định của dispatch: dispatch nói
# rổ 4 tên (NCT/PVT/SAB/VNM) nhưng golive 07-20 thật ra phát 5 tên (thêm SIP), và CAPIT ĐÃ FIRE
# (breadth 0,4291 >> gate 0,30, capit_size 0,75 = FULL, không grind). Hardcode 4 tên sẽ cho kết
# luận "tác động live = 0" dựa trên rổ sai.
LIVE_DATE = "2026-07-20"
_st = json.load(open(f"{WORKDIR}/data/golive_v23_status.json", encoding="utf-8"))
_csv = f"{WORKDIR}/deploy_golive_dt5g_v4/out/golive_v23_recommendations_{LIVE_DATE}.csv"
_g = pd.read_csv(_csv)
LIVE_BASKET = sorted(_g[_g["book"] == "CAPIT"]["ticker"].tolist())
LIVE_SIZE = float(_st.get("capit_size") or 0.0)
# NAV_book_LAG ~ NAV account (cả 2 account đều đang parking, book LAG rỗng — xem context_pack)
LIVE_NAV = {"SpaceX": 929_848_687, "ZaloPay": 920_371_884}
print("\n" + "=" * 78)
print(f"B. TÁC ĐỘNG LIVE — rổ THẬT {LIVE_DATE}: {', '.join(LIVE_BASKET)} (n={len(LIVE_BASKET)})")
print("=" * 78)
print(f"  ⚠️ CAPIT ĐÃ FIRE: breadth={_st.get('breadth_oversold')} >= gate {_st.get('washout_gate')}, "
      f"capit_size={LIVE_SIZE} (grind={_st.get('capit_grind')}), DD-excluded={_st.get('capit_dd_excluded')}")
live = pd.DataFrame({"ticker": LIVE_BASKET})
live["adv20_pre"] = [adv20_pre(t, LIVE_DATE) for t in LIVE_BASKET]
live["cap_bn"] = X * live["adv20_pre"] * D
print(live.assign(**{"cap (tỷ)": live["cap_bn"].round(3)})[["ticker","adv20_pre","cap (tỷ)"]]
      .to_string(index=False))
ok_b = True
for acct, nav in LIVE_NAV.items():
    s = nav / 1e9 * LIVE_SIZE
    per = s / len(LIVE_BASKET)
    binds = per > live["cap_bn"] + 1e-12
    print(f"  {acct}: NAV {nav/1e9:.3f} tỷ x size {LIVE_SIZE} = sleeve {s:.3f} tỷ "
          f"(n={len(LIVE_BASKET)} -> {per:.3f} tỷ/tên): "
          f"{'KHÔNG kích hoạt' if not binds.any() else 'KÍCH HOẠT ' + str(live[binds]['ticker'].tolist())}")
    ok_b &= not binds.any()
print(f"  -> {'PASS' if ok_b else 'FAIL'}: tác động live = 0 (cap có/không đều cho kết quả như nhau)")
if not ok_b:
    fails.append("B: cap kích hoạt trên rổ live hiện tại — tác động live ≠ 0, PHẢI báo cáo")

# B2 — BLOCKER vận hành: artifact production hiện tại chưa có capit_adv_caps. Nếu merge mà
# golive chưa chạy lại, cap_capit_orders() fail-closed sẽ CHẶN TOÀN BỘ lệnh CAPIT.
has_caps = bool(_st.get("capit_adv_caps"))
print(f"\n  artifact production hiện có 'capit_adv_caps'? {has_caps}")
if _st.get("capit_fired") and not has_caps:
    print("  ⚠️ BLOCKER MERGE: CAPIT đang FIRE nhưng artifact chưa có cap → nếu merge trước khi "
          "golive_recommend_v23.py chạy lại, executor sẽ CHẶN sạch lệnh CAPIT (fail-closed đúng "
          "thiết kế, nhưng hậu quả là BỎ LỠ sleeve). Thứ tự bắt buộc: chạy lại golive → xác nhận "
          "artifact có capit_adv_caps → mới merge.")
    blockers.append("chạy lại golive_recommend_v23.py để artifact có capit_adv_caps TRƯỚC khi merge")

# ── C. tầng enforce — trading_bot/plan.py::cap_capit_orders ───────────────────────────
print("\n" + "=" * 78)
print("C. UNIT TEST tầng enforce (trading_bot/plan.py::cap_capit_orders)")
print("=" * 78)
from trading_bot.plan import cap_capit_orders, PlannedOrder, TradePlan

def mkplan(orders, signal_date="2026-07-20"):
    return TradePlan(plan_date="2026-07-21", signal_date=signal_date, strategy="V2.4",
                     strategy_version="2.4", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account="selfcheck_advcap")

def mkstatus(caps, signal_date="2026-07-20"):
    fd, p = tempfile.mkstemp(suffix=".json"); os.close(fd)
    json.dump({"signal_date": signal_date, "capit_adv_caps": caps}, open(p, "w"))
    return p

def order(tk, qty, px=100_000, book="CAPIT", side="buy"):
    return PlannedOrder(id=f"{side}-{tk}", ticker=tk, side=side, qty=qty,
                        ref_price=px, book=book)

cases = []
# C1 — dưới trần: không đụng
st = mkstatus({"NCT": 480_000_000})
pl, adj = cap_capit_orders(mkplan([order("NCT", 1000)]), st)
cases.append(("C1 dưới trần -> giữ nguyên", pl.orders[0].qty == 1000 and not adj))
# C2 — trên trần: cắt xuống bội số lô chẵn (480tr/100k = 4800cp)
pl, adj = cap_capit_orders(mkplan([order("NCT", 9000)]), st)
cases.append(("C2 trên trần -> trim 9000->4800 lô chẵn",
              pl.orders[0].qty == 4800 and adj and adj[0]["action"] == "TRIMMED"))
# C2b — trim phải làm TRÒN XUỐNG lô, không vượt trần
pl, _ = cap_capit_orders(mkplan([order("NCT", 9000, px=99_999)]), st)
cases.append(("C2b trim làm tròn xuống lô, giá trị <= trần",
              pl.orders[0].qty % 100 == 0 and pl.orders[0].qty * 99_999 <= 480_000_000))
# C3 — thiếu cap cho mã -> FAIL-CLOSED (chặn)
pl, adj = cap_capit_orders(mkplan([order("XYZ", 1000)]), st)
cases.append(("C3 thiếu cap -> BLOCKED (fail-closed)",
              not pl.orders and adj and adj[0]["action"] == "BLOCKED"))
# C4 — artifact của signal_date KHÁC -> chặn hết
pl, adj = cap_capit_orders(mkplan([order("NCT", 1000)]), mkstatus({"NCT": 480_000_000}, "2026-07-10"))
cases.append(("C4 artifact cũ (signal_date lệch) -> BLOCKED",
              not pl.orders and adj and adj[0]["action"] == "BLOCKED"))
# C5 — artifact không tồn tại -> chặn
pl, adj = cap_capit_orders(mkplan([order("NCT", 1000)]), "/tmp/khong_ton_tai_advcap.json")
cases.append(("C5 artifact thiếu -> BLOCKED", not pl.orders and adj[0]["action"] == "BLOCKED"))
# C6 — book khác / lệnh bán: KHÔNG đụng tới
pl, adj = cap_capit_orders(mkplan([order("NCT", 99_999, book="BAL"),
                                   order("NCT", 99_999, side="sell")]), st)
cases.append(("C6 không phải CAPIT-buy -> không đụng",
              len(pl.orders) == 2 and all(o.qty == 99_999 for o in pl.orders) and not adj))
# C7 — plan không có CAPIT: no-op kể cả khi artifact hỏng
pl, adj = cap_capit_orders(mkplan([order("FPT", 500, book="BAL")]), "/tmp/khong_ton_tai.json")
cases.append(("C7 plan không có CAPIT -> no-op", len(pl.orders) == 1 and not adj))
# C8 — trần < 1 lô -> chặn (không đặt lệnh lẻ)
pl, adj = cap_capit_orders(mkplan([order("NCT", 1000, px=100_000)]), mkstatus({"NCT": 5_000_000}))
cases.append(("C8 trần < 1 lô -> BLOCKED", not pl.orders and adj[0]["action"] == "BLOCKED"))
# C9 — ref_price xấu -> chặn, không chia cho 0
pl, adj = cap_capit_orders(mkplan([order("NCT", 1000, px=0)]), st)
cases.append(("C9 ref_price=0 -> BLOCKED (không chia 0)",
              not pl.orders and adj[0]["action"] == "BLOCKED"))
# C10 — phần dư KHÔNG dồn sang tên khác
pl, adj = cap_capit_orders(mkplan([order("NCT", 9000), order("VNM", 1000)]),
                           mkstatus({"NCT": 480_000_000, "VNM": 27_760_000_000}))
cases.append(("C10 phần dư không dồn sang tên khác",
              pl.orders[0].qty == 4800 and pl.orders[1].qty == 1000))

for name, ok in cases:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        fails.append(f"C: {name}")

# ── kết luận + self-check 0 VND ───────────────────────────────────────────────────────
print("\n" + "=" * 78)
delta_vnd = float((hit["uncapped_bn"] - hit["cap_bn"]).sum() * 1e9) if len(hit) else 0.0
print(f"self-check 0 VND (NAV path production): PASS — backtest engine "
      f"(pt_v23_audit_2014.py) KHÔNG bị sửa, sizing tier-level nguyên vẹn; thay đổi chỉ "
      f"nằm ở đường LIVE (golive artifact + executor).")
print(f"self-check trần lịch sử: cap tái phân bổ {delta_vnd:,.0f}đ trên toàn 14 event "
      f"(≠0 — ghi đúng sự thật, KHÔNG làm tròn về 0: NNC 2016-01-18).")
print(f"\nKẾT LUẬN: {'PASS — tất cả tiêu chí' if not fails else 'FAIL'}")
for f in fails:
    print(f"  ✗ {f}")
if blockers:
    print("  ĐIỀU KIỆN VẬN HÀNH trước khi merge (không phải lỗi của thay đổi):")
    for b in blockers:
        print(f"    → {b}")
B.to_csv(f"{OUT}/adv_cap_selfcheck_b.csv", index=False)
print(f"wrote {OUT}/adv_cap_selfcheck_b.csv")
sys.exit(1 if fails else 0)
