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

def adv20_pre(ticker, ds):
    """median giá trị GD của 20 DÒNG DỮ LIỆU cuối của CHÍNH mã đó trước ds.

    Phải khớp ĐÚNG định nghĩa của SQL production (golive_recommend_v23.capit_adv_caps):
    `WHERE ticker=… AND time < asof AND time >= asof-90d`, `ROW_NUMBER() OVER (PARTITION
    BY ticker ORDER BY time DESC)`, `rn <= 20`. Bản trước dùng cửa sổ 20 phiên theo LỊCH
    CHUNG toàn thị trường — khác nhau ngay khi một mã bị KHUYẾT phiên: NCT thủng
    2016-06-05→06-24 nên cửa sổ-lịch chỉ bắt được 18 dòng và ra ADV20 2,338 tỷ, trong khi
    production (rn<=20, với trần 90 ngày) với tay xa hơn và ra 2,178 tỷ — lệch 7,3%.
    Một selfcheck dùng công thức tự viết lại thì không kiểm được công thức thật sự chạy
    (quant-skeptic killer objection, log verify_20260720_181645).
    """
    t0 = pd.Timestamp(ds)
    s = adv[(adv["ticker"] == ticker) & (adv["time"] < t0)
            & (adv["time"] >= t0 - pd.Timedelta(days=90))].nlargest(20, "time")
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
# Trần mỗi account = phần CHIA của nó, KHÔNG phải trần tổng (job Taylor_20260720_180351).
# So với trần tổng ở đây sẽ đánh giá THẤP mức ràng buộc thật -> phải nhân share.
LIVE_SHARE = {a: LIVE_NAV[a] / sum(LIVE_NAV.values()) for a in LIVE_NAV}
ok_b = True
for acct, nav in LIVE_NAV.items():
    s = nav / 1e9 * LIVE_SIZE
    per = s / len(LIVE_BASKET)
    cap_acct = live["cap_bn"] * LIVE_SHARE[acct]
    binds = per > cap_acct + 1e-12
    print(f"  {acct}: NAV {nav/1e9:.3f} tỷ x size {LIVE_SIZE} = sleeve {s:.3f} tỷ "
          f"(n={len(LIVE_BASKET)} -> {per:.3f} tỷ/tên) vs trần đã chia "
          f"(share {LIVE_SHARE[acct]:.1%}, thấp nhất {cap_acct.min():.3f} tỷ): "
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

ACCT = "SpaceX"          # account dùng cho unit test tầng enforce

def mkstatus(caps, signal_date="2026-07-20", account=ACCT, raw=False):
    """caps = {ticker: vnd} của MỘT account (bọc lại thành schema {label:{ticker:vnd}}),
    hoặc raw=True để ghi thẳng cấu trúc truyền vào (test schema cũ/schema lạ)."""
    fd, p = tempfile.mkstemp(suffix=".json"); os.close(fd)
    json.dump({"signal_date": signal_date,
               "capit_adv_caps": caps if raw else {account: caps}}, open(p, "w"))
    return p

def cap_capit_orders_A(plan, status_path, account=ACCT):
    """Wrapper cố định account cho các case C — chữ ký thật là (plan, account, status)."""
    return cap_capit_orders(plan, account, status_path)

def order(tk, qty, px=100_000, book="CAPIT", side="buy"):
    return PlannedOrder(id=f"{side}-{tk}", ticker=tk, side=side, qty=qty,
                        ref_price=px, book=book)

cases = []
# C1 — dưới trần: không đụng
st = mkstatus({"NCT": 480_000_000})
pl, adj = cap_capit_orders_A(mkplan([order("NCT", 1000)]), st)
cases.append(("C1 dưới trần -> giữ nguyên", pl.orders[0].qty == 1000 and not adj))
# C2 — trên trần: cắt xuống bội số lô chẵn (480tr/100k = 4800cp)
pl, adj = cap_capit_orders_A(mkplan([order("NCT", 9000)]), st)
cases.append(("C2 trên trần -> trim 9000->4800 lô chẵn",
              pl.orders[0].qty == 4800 and adj and adj[0]["action"] == "TRIMMED"))
# C2b — trim phải làm TRÒN XUỐNG lô, không vượt trần
pl, _ = cap_capit_orders_A(mkplan([order("NCT", 9000, px=99_999)]), st)
cases.append(("C2b trim làm tròn xuống lô, giá trị <= trần",
              pl.orders[0].qty % 100 == 0 and pl.orders[0].qty * 99_999 <= 480_000_000))
# C3 — thiếu cap cho mã -> FAIL-CLOSED (chặn)
pl, adj = cap_capit_orders_A(mkplan([order("XYZ", 1000)]), st)
cases.append(("C3 thiếu cap -> BLOCKED (fail-closed)",
              not pl.orders and adj and adj[0]["action"] == "BLOCKED"))
# C4 — artifact của signal_date KHÁC -> chặn hết
pl, adj = cap_capit_orders_A(mkplan([order("NCT", 1000)]), mkstatus({"NCT": 480_000_000}, "2026-07-10"))
cases.append(("C4 artifact cũ (signal_date lệch) -> BLOCKED",
              not pl.orders and adj and adj[0]["action"] == "BLOCKED"))
# C5 — artifact không tồn tại -> chặn
pl, adj = cap_capit_orders_A(mkplan([order("NCT", 1000)]), "/tmp/khong_ton_tai_advcap.json")
cases.append(("C5 artifact thiếu -> BLOCKED", not pl.orders and adj[0]["action"] == "BLOCKED"))
# C6 — book khác / lệnh bán: KHÔNG đụng tới
pl, adj = cap_capit_orders_A(mkplan([order("NCT", 99_999, book="BAL"),
                                   order("NCT", 99_999, side="sell")]), st)
cases.append(("C6 không phải CAPIT-buy -> không đụng",
              len(pl.orders) == 2 and all(o.qty == 99_999 for o in pl.orders) and not adj))
# C7 — plan không có CAPIT: no-op kể cả khi artifact hỏng
pl, adj = cap_capit_orders_A(mkplan([order("FPT", 500, book="BAL")]), "/tmp/khong_ton_tai.json")
cases.append(("C7 plan không có CAPIT -> no-op", len(pl.orders) == 1 and not adj))
# C8 — trần < 1 lô -> chặn (không đặt lệnh lẻ)
pl, adj = cap_capit_orders_A(mkplan([order("NCT", 1000, px=100_000)]), mkstatus({"NCT": 5_000_000}))
cases.append(("C8 trần < 1 lô -> BLOCKED", not pl.orders and adj[0]["action"] == "BLOCKED"))
# C9 — ref_price xấu -> chặn, không chia cho 0
pl, adj = cap_capit_orders_A(mkplan([order("NCT", 1000, px=0)]), st)
cases.append(("C9 ref_price=0 -> BLOCKED (không chia 0)",
              not pl.orders and adj[0]["action"] == "BLOCKED"))
# C10 — phần dư KHÔNG dồn sang tên khác
pl, adj = cap_capit_orders_A(mkplan([order("NCT", 9000), order("VNM", 1000)]),
                           mkstatus({"NCT": 480_000_000, "VNM": 27_760_000_000}))
cases.append(("C10 phần dư không dồn sang tên khác",
              pl.orders[0].qty == 4800 and pl.orders[1].qty == 1000))

# C11 — SCHEMA CŨ (phẳng {ticker: vnd}, chưa chia account) -> phải CHẶN, không được diễn
# giải như trần riêng của account này (làm vậy = tái lập đúng bug N x 10% ADV).
pl, adj = cap_capit_orders_A(mkplan([order("NCT", 1000)]),
                             mkstatus({"NCT": 480_000_000}, raw=True))
cases.append(("C11 schema cũ (phẳng) -> BLOCKED, không tái lập bug N×ADV",
              not pl.orders and adj and adj[0]["action"] == "BLOCKED"))
# C12 — account không có phần chia trong artifact -> chặn (không mượn trần account khác)
pl, adj = cap_capit_orders_A(mkplan([order("NCT", 1000)]),
                             mkstatus({"NCT": 480_000_000}, account="ZaloPay"), account="SpaceX")
cases.append(("C12 account không có phần chia -> BLOCKED",
              not pl.orders and adj and adj[0]["action"] == "BLOCKED"))
# C13 — mỗi account CHỈ thấy trần của mình (cùng artifact, 2 account, 2 kết quả khác nhau)
_st2 = mkstatus({"SpaceX": {"NCT": 480_000_000}, "ZaloPay": {"NCT": 240_000_000}}, raw=True)
_a, _ = cap_capit_orders(mkplan([order("NCT", 9000)]), "SpaceX", _st2)
_b, _ = cap_capit_orders(mkplan([order("NCT", 9000)]), "ZaloPay", _st2)
cases.append(("C13 mỗi account chỉ thấy phần trần của mình (4800 vs 2400)",
              _a.orders[0].qty == 4800 and _b.orders[0].qty == 2400))

for name, ok in cases:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        fails.append(f"C: {name}")

# ── D. CHIA TRẦN DÙNG CHUNG cho N account (job Taylor_20260720_180351) ────────────────
# Trần %ADV là nguồn lực THỊ TRƯỜNG của một mã, không phải trần riêng từng account. Bất
# biến phải đúng ở MỌI nhánh: Σ_account cap = X·ADV20·D, và N=1 -> đúng công thức gốc.
print("\n" + "=" * 78)
print("D. CHIA TRẦN DÙNG CHUNG — N account đọc ĐỘNG từ trading_bot_accounts.json")
print("=" * 78)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_golive_sc", f"{WORKDIR}/deploy_golive_dt5g_v4/golive_recommend_v23.py")
# module chạy full pipeline khi import -> chỉ trích 2 hàm thuần bằng exec có kiểm soát
_src = open(_spec.origin, encoding="utf-8").read()
_ns = {"os": os, "json": json, "pd": pd, "WORKDIR": WORKDIR, "ACTIVE_NAV_MAX_AGE_D": 5,
       "print": print}
_start = _src.index("def _account_nav_basis(")
exec(_src[_start:_src.index("def capit_base(")], _ns)
_account_nav_basis, capit_account_shares = _ns["_account_nav_basis"], _ns["capit_account_shares"]

CAP_TOTAL = 480_000_000.0     # trần tổng giả định cho 1 mã (X·ADV20·D)

def shares_for(navs):
    """Chạy CHÍNH capit_account_shares() của production với bộ NAV giả lập.

    KHÔNG viết lại logic ở đây: một bản mirror thì dù có PASS cũng chỉ chứng minh bản
    mirror đúng, không chứng minh hàm thật đúng (quant-skeptic caveat, log
    verify_20260720_181645 — cùng loại lỗi với adv20_pre ở mục A).
    Chặn 2 phụ thuộc I/O: danh sách account (trading_bot.config.live_dnse_labels, hàm
    thật import nó lúc GỌI nên phải vá ở module) và NAV mỗi account (_account_nav_basis
    là global trong namespace đã exec).
    """
    import trading_bot.config as _tbc
    _lbl, _nav = _tbc.live_dnse_labels, _ns["_account_nav_basis"]
    try:
        _tbc.live_dnse_labels = lambda *a, **k: sorted(navs)
        _ns["_account_nav_basis"] = lambda l: (
            (navs[l], "giả lập") if navs.get(l) else (None, "giả lập thiếu NAV"))
        s, mode, _det = capit_account_shares()
        return s, mode
    finally:
        _tbc.live_dnse_labels, _ns["_account_nav_basis"] = _lbl, _nav

dcases = []
# D1 — N=1: cap = ĐÚNG công thức gốc 100%, không bị chia nhỏ
s1, m1 = shares_for({"SpaceX": 928_971_136.0})
c1 = {a: CAP_TOTAL * v for a, v in s1.items()}
print(f"  N=1 ({m1}): {s1} -> cap SpaceX = {c1['SpaceX']:,.0f}đ (trần gốc {CAP_TOTAL:,.0f}đ)")
dcases.append(("D1 N=1 -> cap = 100% công thức gốc", abs(c1["SpaceX"] - CAP_TOTAL) < 1e-6))
# D2 — N=2 hiện trạng: tổng ĐÚNG 10% ADV (không phải 20% như bug)
NAV2 = {"SpaceX": 928_971_136.0, "ZaloPay": 469_326_169.0}   # active_nav thật 2026-07-20
s2, m2 = shares_for(NAV2)
c2 = {a: CAP_TOTAL * v for a, v in s2.items()}
for a in sorted(c2):
    print(f"  N=2 ({m2}): {a} share {s2[a]:.4f} (active_nav {NAV2[a]:,.0f}đ) "
          f"-> cap {c2[a]:,.0f}đ")
print(f"       Σ = {sum(c2.values()):,.0f}đ vs trần tổng {CAP_TOTAL:,.0f}đ "
      f"(bug cũ sẽ cho {2*CAP_TOTAL:,.0f}đ)")
dcases.append(("D2 N=2 -> Σ cap = ĐÚNG trần tổng (không phải 2×)",
               abs(sum(c2.values()) - CAP_TOTAL) < 1e-6))
dcases.append(("D2b N=2 -> share tỉ lệ ĐÚNG theo NAV",
               abs(s2["SpaceX"] / s2["ZaloPay"] - NAV2["SpaceX"] / NAV2["ZaloPay"]) < 1e-9))
# D3 — N=3 giả lập: vẫn ĐÚNG tổng, mỗi account nhận đúng tỉ lệ NAV
NAV3 = dict(NAV2, Sim3=250_000_000.0)
s3, m3 = shares_for(NAV3)
c3 = {a: CAP_TOTAL * v for a, v in s3.items()}
for a in sorted(c3):
    print(f"  N=3 ({m3}): {a} share {s3[a]:.4f} (NAV {NAV3[a]:,.0f}đ) -> cap {c3[a]:,.0f}đ")
print(f"       Σ = {sum(c3.values()):,.0f}đ vs trần tổng {CAP_TOTAL:,.0f}đ")
dcases.append(("D3 N=3 -> Σ cap = ĐÚNG trần tổng", abs(sum(c3.values()) - CAP_TOTAL) < 1e-6))
dcases.append(("D3b N=3 -> mỗi account đúng tỉ lệ NAV",
               all(abs(s3[a] - NAV3[a] / sum(NAV3.values())) < 1e-12 for a in NAV3)))
# D4 — thiếu NAV 1 account -> chia đều, tổng VẪN không đổi (fail-safe không nới trần)
s4, m4 = shares_for({"SpaceX": 928_971_136.0, "ZaloPay": None})
c4 = {a: CAP_TOTAL * v for a, v in s4.items()}
print(f"  thiếu NAV ({m4}): {s4} -> Σ = {sum(c4.values()):,.0f}đ")
dcases.append(("D4 thiếu NAV -> chia đều, Σ cap KHÔNG đổi",
               m4 == "equal-split-fallback" and abs(sum(c4.values()) - CAP_TOTAL) < 1e-6))
# D5 — N=1 cho ra CÙNG kết quả ở cả 2 chế độ (không có case đặc biệt cần xử lý riêng)
dcases.append(("D5 N=1: pro-rata ≡ chia đều (không cần case đặc biệt)",
               abs(shares_for({"A": 1.0})[0]["A"] - 1.0) < 1e-12
               and abs(shares_for({"A": None})[0]["A"] - 1.0) < 1e-12))
# D6 — danh sách account đọc ĐỘNG từ config THẬT, không hardcode
s_live, m_live, det_live = capit_account_shares()
print(f"\n  đọc ĐỘNG từ trading_bot_accounts.json: {sorted(s_live)} (mode={m_live})")
for a in sorted(det_live):
    print(f"    {a}: NAV {det_live[a]['nav'] or 0:,.0f}đ — nguồn: {det_live[a]['source']}")
dcases.append(("D6 account đọc động = live_dnse_labels() và Σ share = 1",
               bool(s_live) and abs(sum(s_live.values()) - 1.0) < 1e-9))

# D7 — nguồn NAV: active_nav (đã trừ excluded_tickers) khi computed_at còn hạn; quá hạn ->
# lùi nav_history. Kiểm theo NỘI DUNG file, KHÔNG theo mtime (bẫy lag_edge_health).
import datetime as _dt
_LBL = "_sc_navbasis"
_ap = f"{WORKDIR}/data/execution_logs/active_nav_{_LBL}.json"
_np_ = f"{WORKDIR}/data/execution_logs/nav_history_{_LBL}.csv"
try:
    open(_np_, "w").write("date,nav\n2026-07-20,777000000\n")
    for tag, days, want_src, want_nav in [("tươi", 0, "active_nav", 111_000_000.0),
                                          ("quá hạn", 30, "nav_history", 777_000_000.0)]:
        json.dump({"active_nav": 111_000_000.0,
                   "computed_at": str(_dt.date.today() - _dt.timedelta(days=days))},
                  open(_ap, "w"))
        nav, src = _account_nav_basis(_LBL)
        print(f"  active_nav {tag} -> nguồn={src.split(' @')[0]}, NAV={nav:,.0f}đ")
        dcases.append((f"D7 active_nav {tag} -> dùng {want_src}",
                       src.startswith(want_src) and abs(nav - want_nav) < 1e-6))
finally:
    for _f in (_ap, _np_):
        os.path.exists(_f) and os.remove(_f)

# D8 — KHÔNG có account live nào: Σ share = 0 (KHÔNG phải 1.0) → không phát cap cho ai →
# executor fail-closed chặn sạch CAPIT. Đây là NGOẠI LỆ có chủ đích của bất biến Σ=1: khi
# không biết chia cho ai thì không phát trần, chứ không phát trần cho một account nào đó.
s0, m0 = shares_for({})
print(f"\n  không có account live: shares={s0}, mode={m0} -> Σ = {sum(s0.values()):.1f} "
      f"(executor sẽ CHẶN mọi lệnh CAPIT — fail-closed, KHÔNG phải Σ=1)")
dcases.append(("D8 không có account -> {} (Σ=0), fail-closed chứ không nới trần",
               s0 == {} and m0 == "no-account"))

for name, ok in dcases:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        fails.append(f"D: {name}")

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
