#!/usr/bin/env python3
"""
value_radar.py — VALUE RADAR: lăng kính ĐỊNH GIÁ thị trường, hiển thị cạnh DT5G
==============================================================================
Đóng gói lại (production-ready) composite định giá đã nghiên cứu ở **Phụ lục C** của
`mike/agents/Taylor/research/market_regime_probability_20260729.md`
(job `Taylor_20260730_154733`, sandbox nghiên cứu `mike/agents/Taylor/exp_value_radar/`
giữ nguyên làm audit trail — file này KHÔNG thay thế nó, chỉ tái dùng đúng công thức).

⚠️ **RANH GIỚI CỨNG — ĐỌC TRƯỚC KHI IMPORT Ở BẤT KỲ ĐÂU**
Đây là **THÔNG TIN HIỂN THỊ**, KHÔNG phải tín hiệu giao dịch:
  * Phụ lục C: **0/17 lăng kính** qua BH(FDR 10%) hay Bonferroni; hiệu RẺ−ĐẮT p=0,049
    (chưa hiệu chỉnh đa kiểm định, dự đoán khó sống sót DSR); đầu RẺ **không đơn điệu**
    (dải 0-20 tệ hơn dải 20-33) ⇒ "càng rẻ càng nên mua" là SAI.
  * ⇒ **KHÔNG được đọc bởi bất kỳ code ra quyết định trading nào** — không
    `golive_recommend_v23.py`, không `bot_execute.py`, không sizing CAPIT/LAG/BAL, không
    một threshold nào. Đúng tiền lệ **DT4-gate clock** (`dna_report.build_dt_gate_line`):
    thuần hiển thị, KHÔNG phải gate.
  * Consumer hợp lệ duy nhất: `dna_report.py` (khối NOW) + `mike/bin/eod_trading_report.sh`.

CÔNG THỨC (giữ NGUYÊN Phụ lục C §C.4.1 — không tự đổi):
  3 thành phần, mỗi thành phần quy về **phân vị nhân quả** (chỉ dùng dữ liệu ĐẾN ngày t):
    1. P/E capped-weight 10%   (bền, đối xứng theo thời gian — §C.1)
    2. P/B capped-weight 10%   (cột "bền mặc định" §B.4)
    3. Spread EY − lãi suất huy động Big-4 12M, **đảo chiều** (spread rộng = rẻ)
  Rổ = top-100 vốn hoá/phiên (lọc PB>0) cắt từ panel top-300, floor 2008-01-01.
  Điểm composite = trung bình 3 phân vị. Ngưỡng cố định khai báo trước:
    **RẺ < 33 · TRUNG TÍNH 33–67 · ĐẮT > 67**

CỬA SỔ = **ROLLING 10 NĂM (2500 phiên, tối thiểu 500)** — user chốt 2026-07-30 (chọn ưu
tiên giai đoạn gần thay vì cân bằng cả lịch sử 2008+; đây là lựa chọn PHƯƠNG PHÁP của user,
không phải kết luận thống kê). Bản expanding-from-2008 vẫn tính song song (`score_expanding`)
để đối chiếu, nhưng `score`/`label` = rolling-10Y.

NGUỒN (đã tra `mike/kb/data_registry/`, coding_guidelines §9):
  * `tav2_bq.ticker` — CANONICAL (`price-volume/ticker_ohlcv_tables.md`); floor 2008-01-01
    theo quy ước bắt buộc của `price-volume/vnindex_pe_mirror_col.md`.
  * `deposit_rate_vn.deposit_events_df()` — CANONICAL-PROXY (`macro/deposit_rate_vn.md`).
    Caveat (b) của registry: 26 mốc neo hồi tố 1 lần 2026-06-19 ⇒ phân vị lịch sử của
    thành phần spread mang bias "biết trước". Đây là thành phần YẾU NHẤT của radar.
  * Cache local `data/value_radar_series.csv` (chuỗi thô pe_cap10/pb_cap10 theo phiên) để
    không phải quét lại 1,36M dòng mỗi lần đọc; cập nhật tăng dần (chỉ query ngày mới).

Vintage: đọc BQ ⇒ **T-1** cho tới khi `sync_bq_cache_daily.sh` 23:45 chạy. Mọi dòng hiển thị
đều đóng dấu "dữ liệu tới <asof>" — giống DT4-gate clock (fix 2026-07-14). Đây KHÔNG phải số
same-day nên không vướng bright-line DNSE-vs-BQ (coding_guidelines §6, chỉ áp cho số live).

CLI:
    python3 value_radar.py                 # đọc hôm nay (tự cập nhật tăng dần)
    python3 value_radar.py --rebuild       # dựng lại cache từ 2008 (chậm, ~1,4M dòng)
    python3 value_radar.py --selfcheck     # parity với Phụ lục C (exp_value_radar/radar.csv)
"""
import os
import sys

import numpy as np
import pandas as pd

W = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
PROJECT = "lithe-record-440915-m9"
CACHE = os.path.join(W, "data", "value_radar_series.csv")

FLOOR = "2008-01-01"      # quy ước bắt buộc: mọi percentile định giá floor 2008 (registry)
TOP_N = 100               # rổ chuẩn Phụ lục B/C
PANEL_N = 300             # cắt rộng hơn để sau khi lọc PB>0 vẫn đủ 100
MIN_NAMES = 50            # loại phiên hỏng dữ liệu (2 ngày 2025-05-04/11)
ROLL_WIN = 2500           # ~10 năm phiên
MIN_PERIODS = 500         # khởi động tối thiểu (giữ nguyên Phụ lục C)
CHEAP_MAX, EXPENSIVE_MIN = 33.0, 67.0
REFETCH_TAIL = 10         # luôn kéo lại N phiên cuối (BQ hay bị restate) rồi ghi đè cache

_LABEL_VN = {"CHEAP": "RẺ", "FAIR": "TRUNG TÍNH", "EXPENSIVE": "ĐẮT"}

_SQL = """
WITH base AS (
  SELECT t.time, t.ticker,
         t.Price*t.OShares AS mcap,
         t.BVPS*t.OShares  AS book,
         t.PE
  FROM `{project}.tav2_bq.ticker` t
  WHERE t.time >= '{start}' AND t.ticker != 'VNINDEX'
    AND t.OShares > 0 AND t.Price > 0
)
SELECT * FROM base
QUALIFY ROW_NUMBER() OVER (PARTITION BY time ORDER BY mcap DESC) <= {panel_n}
"""


# --------------------------------------------------------------------------- công thức
def _cap_weights(w, cap=0.10):
    """Water-filling: trần `cap` mỗi tên, phần dư chia lại theo tỷ lệ (Phụ lục B/C)."""
    w = np.asarray(w, float).copy()
    for _ in range(60):
        w = w / w.sum()
        over = w > cap + 1e-12
        if not over.any():
            break
        ex = (w[over] - cap).sum()
        w[over] = cap
        fr = ~over
        if w[fr].sum() <= 0:
            break
        w[fr] += ex * w[fr] / w[fr].sum()
    return w / w.sum()


def _harm(w, x):
    """Trung bình điều hoà có trọng số = aggregate ratio-of-sums với trọng số đã capped."""
    return w.sum() / (w / x).sum()


def _daily_from_panel(p):
    """panel top-300 -> chuỗi pe_cap10 / pb_cap10 theo phiên (rổ top-100, lọc PB>0)."""
    p = p.copy()
    p["time"] = pd.to_datetime(p["time"])
    p["pb_i"] = p["mcap"] / p["book"]
    p = p[np.isfinite(p["pb_i"]) & (p["pb_i"] > 0)].copy()
    p["rk"] = p.groupby("time")["mcap"].rank(ascending=False, method="first")
    t100 = p[p["rk"] <= TOP_N].copy()
    nday = t100.groupby("time").size()
    t100 = t100[t100["time"].isin(nday[nday >= MIN_NAMES].index)].copy()
    t100["w"] = t100["mcap"] / t100.groupby("time")["mcap"].transform("sum")

    rows = []
    for t, d in t100.groupby("time"):
        w = d["w"].values
        pb = d["pb_i"].values
        pe_i = d["PE"].values.astype(float)
        okp = np.isfinite(pe_i) & (pe_i > 0)
        rows.append(dict(
            time=t, n=len(d),
            pe_cap10=_harm(_cap_weights(w[okp]), pe_i[okp]) if okp.sum() > 5 else np.nan,
            pb_cap10=_harm(_cap_weights(w), pb),
        ))
    return pd.DataFrame(rows).sort_values("time").reset_index(drop=True)


def _roll_pct(s, win=ROLL_WIN, minp=MIN_PERIODS):
    """Phân vị NHÂN QUẢ trong cửa sổ trượt `win` phiên: chỉ so với các giá trị TRƯỚC đó
    (h[:-1]), hoàn toàn không nhìn trước. Giữ nguyên bit-for-bit hàm của Phụ lục C."""
    v = np.asarray(s, float)
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        if not np.isfinite(v[i]):
            continue
        h = v[max(0, i - win + 1):i + 1]
        h = h[np.isfinite(h)]
        if len(h) < minp:
            continue
        out[i] = 100 * (h[:-1] < v[i]).mean()
    return out


def _exp_pct(s, minp=MIN_PERIODS):
    """Bản expanding (floor 2008) — giữ để đối chiếu, KHÔNG phải cửa sổ chính."""
    return _roll_pct(s, win=len(s) if len(s) else 1, minp=minp)


def label_of(score):
    if not np.isfinite(score):
        return None
    return "CHEAP" if score < CHEAP_MAX else ("EXPENSIVE" if score > EXPENSIVE_MIN else "FAIR")


# ------------------------------------------------------------------------------- cache
def _fetch(start):
    from google.cloud import bigquery
    c = bigquery.Client(project=PROJECT)
    sql = _SQL.format(project=PROJECT, start=start, panel_n=PANEL_N)
    return c.query(sql).result().to_dataframe()


def update_cache(rebuild=False, verbose=False):
    """Cập nhật `data/value_radar_series.csv`. Tăng dần: chỉ query từ (phiên cuối − 10) trở
    đi rồi GHI ĐÈ phần đuôi (BQ `ticker` bị TRUNCATE+rebuild mỗi ngày ⇒ số cũ có thể restate,
    không được tin cache đuôi một cách mù quáng). `rebuild=True` dựng lại toàn bộ từ 2008."""
    old = None
    start = FLOOR
    if not rebuild:
        # KHÔNG bao giờ tự dựng lại toàn bộ (1,4M dòng) khi thiếu cache — hàm này được gọi
        # từ đường sống của bot Telegram / EOD report; dựng lại phải là thao tác TƯỜNG MINH
        # (`python3 value_radar.py --rebuild`), không được kích hoạt bởi 1 tin nhắn.
        if not os.path.exists(CACHE):
            raise FileNotFoundError(f"thiếu cache {CACHE} — chạy `value_radar.py --rebuild` trước")
        old = pd.read_csv(CACHE, parse_dates=["time"])
        if len(old):
            tail = old["time"].sort_values().iloc[-min(REFETCH_TAIL, len(old))]
            start = str(pd.Timestamp(tail).date())
    if verbose:
        print(f"[value_radar] fetch panel từ {start} (rebuild={rebuild}) ...", file=sys.stderr)
    new = _daily_from_panel(_fetch(start))
    if old is not None and len(old):
        old = old[old["time"] < new["time"].min()]
        new = pd.concat([old, new], ignore_index=True)
    new = new.sort_values("time").drop_duplicates("time", keep="last").reset_index(drop=True)
    tmp = CACHE + ".tmp"
    new.to_csv(tmp, index=False)
    os.replace(tmp, CACHE)     # ghi nguyên tử (coding_guidelines §5)
    if verbose:
        print(f"[value_radar] cache: {len(new)} phiên, {new.time.min().date()} -> "
              f"{new.time.max().date()}", file=sys.stderr)
    return new


def load_series(update=True, rebuild=False):
    """Chuỗi đầy đủ: 3 thành phần thô + phân vị rolling-10Y + expanding + composite."""
    if rebuild or update:
        d = update_cache(rebuild=rebuild)
    else:
        d = pd.read_csv(CACHE, parse_dates=["time"])
    d = d.sort_values("time").reset_index(drop=True)

    if W not in sys.path:
        sys.path.insert(0, W)
    from deposit_rate_vn import deposit_events_df
    ev = deposit_events_df().sort_values("time")
    d = pd.merge_asof(d, ev, on="time", direction="backward")   # nhân quả: mốc ≤ t
    d["ey"] = 100.0 / d["pe_cap10"]
    d["spread"] = d["ey"] - d["deposit_rate"]

    d["p_pe"] = _roll_pct(d["pe_cap10"])
    d["p_pb"] = _roll_pct(d["pb_cap10"])
    d["p_sp"] = 100 - _roll_pct(d["spread"])        # spread rộng = rẻ ⇒ đảo chiều
    d["score"] = d[["p_pe", "p_pb", "p_sp"]].mean(axis=1)
    d["label"] = d["score"].map(label_of)

    d["p_pe_e"] = _exp_pct(d["pe_cap10"])
    d["p_pb_e"] = _exp_pct(d["pb_cap10"])
    d["p_sp_e"] = 100 - _exp_pct(d["spread"])
    d["score_expanding"] = d[["p_pe_e", "p_pb_e", "p_sp_e"]].mean(axis=1)
    return d


# ------------------------------------------------------------------------------ đọc số
_CACHE_NOW = {"t": 0.0, "val": None}


def value_radar_now(update=True, ttl=900):
    """Đọc radar hôm nay. Trả dict hoặc None (mọi lỗi ⇒ None, caller bỏ dòng, KHÔNG crash).

    dict: score/label (rolling-10Y = bản chính), score_expanding/label_expanding (đối chiếu),
          pe_cap10/pb_cap10/spread + phân vị từng thành phần, deposit_rate, asof."""
    import time as _t
    if _CACHE_NOW["val"] is not None and (_t.time() - _CACHE_NOW["t"]) < ttl:
        return _CACHE_NOW["val"]
    val = None
    try:
        d = load_series(update=update)
        cur = d.dropna(subset=["score"]).iloc[-1]
        val = dict(
            score=float(cur["score"]), label=label_of(cur["score"]),
            score_expanding=float(cur["score_expanding"]),
            label_expanding=label_of(cur["score_expanding"]),
            pe_cap10=float(cur["pe_cap10"]), p_pe=float(cur["p_pe"]),
            pb_cap10=float(cur["pb_cap10"]), p_pb=float(cur["p_pb"]),
            spread=float(cur["spread"]), p_sp=float(cur["p_sp"]),
            deposit_rate=float(cur["deposit_rate"]),
            asof=str(pd.Timestamp(cur["time"]).date()),
            window="rolling-10Y",
        )
    except Exception as e:
        print(f"[value_radar] skipped (fail-safe): {e}", file=sys.stderr)
        val = None
    _CACHE_NOW.update(t=_t.time(), val=val)
    return val


def build_value_radar_line(html=True, update=True):
    """1 dòng cho khối NOW / EOD report. None khi lỗi dữ liệu (caller bỏ dòng).

    THUẦN HIỂN THỊ — không hàm nào ở đây được nối vào sizing/allocator/threshold."""
    c = value_radar_now(update=update)
    if not c:
        return None
    B = (lambda s: f"<b>{s}</b>") if html else (lambda s: s)
    vn = _LABEL_VN.get(c["label"], c["label"])
    emo = {"CHEAP": "🟢", "FAIR": "🟡", "EXPENSIVE": "🔴"}.get(c["label"], "")
    asof = f"[dữ liệu tới {c['asof']}]"
    asof = f"<i>{asof}</i>" if html else asof
    head = B("%.1f %s" % (c["score"], vn))
    return (
        f"Value Radar: {emo} {head}"
        f" (phân vị 10 năm) · P/E {c['pe_cap10']:.2f} (p{c['p_pe']:.0f})"
        f" · P/B {c['pb_cap10']:.2f} (p{c['p_pb']:.0f})"
        f" · spread EY−tiết kiệm {c['spread']:+.2f}pp (p{c['p_sp']:.0f})  {asof}"
        f"\n  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing "
        f"(0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán."
    )


# --------------------------------------------------------------------------------- CLI
def _selfcheck():
    """Parity với Phụ lục C (`exp_value_radar/radar.csv`: radar3_roll / radar3 / p_*_r).

    Tiêu chí PASS (khai báo trước):
      (1) **Nhãn khớp 100%** trên mọi phiên cả hai bên đều có dữ liệu — đây là thứ được hiển thị.
      (2) Số hôm nay khớp số đã pin ở Phụ lục C §C.4.5: rolling-10Y **25,9 RẺ**, expanding **36,0**.
      (3) Sai lệch số học chỉ được phép ở **hiện tượng đồng hạng vốn hoá** khi cắt top-100 mà
          chính Phụ lục B/C đã ghi nhận: trung vị = 0, và <1% số phiên lệch > 1e-9."""
    ref_path = os.path.join(W, "mike", "agents", "Taylor", "exp_value_radar", "radar.csv")
    ref = pd.read_csv(ref_path, parse_dates=["time"])
    d = load_series(update=True)
    m = d.merge(ref[["time", "pe_cap10", "pb_cap10", "sp_pe_cap10",
                     "p_pe_r", "p_pb_r", "p_sp_r", "radar3_roll", "radar3"]],
                on="time", suffixes=("", "_ref"))
    print(f"SELF-CHECK PARITY vs Phụ lục C — {len(m)} phiên chung "
          f"({m.time.min().date()} -> {m.time.max().date()})")
    pairs = [("pe_cap10", "pe_cap10_ref"), ("pb_cap10", "pb_cap10_ref"),
             ("spread", "sp_pe_cap10"), ("p_pe", "p_pe_r"), ("p_pb", "p_pb_r"),
             ("p_sp", "p_sp_r"), ("score", "radar3_roll"), ("score_expanding", "radar3")]
    n_drift = 0
    for a, b in pairs:
        diff = (m[a] - m[b]).abs()
        n_drift = max(n_drift, int((diff > 1e-9).sum()))
        print(f"  {a:16s} vs {b:14s}  maxdiff={diff.max():.3e}  median={diff.median():.3e}"
              f"  corr={m[a].corr(m[b]):.10f}  n(>1e-9)={int((diff > 1e-9).sum())}")

    sub = m[m["score"].notna() & m["radar3_roll"].notna()]
    n_lab = int((sub["score"].map(label_of) != sub["radar3_roll"].map(label_of)).sum())
    cur = d.dropna(subset=["score"]).iloc[-1]
    pin_ok = (round(float(cur["score"]), 1) == 25.9
              and round(float(cur["score_expanding"]), 1) == 36.0)
    drift_ok = n_drift < 0.01 * len(sub)
    print(f"  (1) lệch NHÃN: {n_lab}/{len(sub)} phiên  -> {'OK' if n_lab == 0 else 'FAIL'}")
    print(f"  (2) hôm nay ({str(pd.Timestamp(cur['time']).date())}): rolling-10Y "
          f"{cur['score']:.1f} {label_of(cur['score'])} · expanding {cur['score_expanding']:.1f}"
          f"  -> {'OK (khớp pin C.4.5: 25,9 / 36,0)' if pin_ok else 'FAIL'}")
    print(f"  (3) phiên lệch >1e-9 (đồng hạng vốn hoá): {n_drift}/{len(sub)} "
          f"({100*n_drift/max(1,len(sub)):.2f}%)  -> {'OK (<1%)' if drift_ok else 'FAIL'}")
    ok = (n_lab == 0) and pin_ok and drift_ok
    print("  => PASS" if ok else "  => FAIL")
    return ok


if __name__ == "__main__":
    if "--rebuild" in sys.argv:
        update_cache(rebuild=True, verbose=True)
    if "--selfcheck" in sys.argv:
        sys.exit(0 if _selfcheck() else 1)
    c = value_radar_now()
    if not c:
        print("value_radar: n/a")
        sys.exit(1)
    print(build_value_radar_line(html=False))
    print(f"\n(đối chiếu) expanding-2008 = {c['score_expanding']:.1f} "
          f"{_LABEL_VN.get(c['label_expanding'], '')} · lãi suất huy động {c['deposit_rate']:.2f}%")
