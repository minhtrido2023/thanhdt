# -*- coding: utf-8 -*-
"""DCF — 2 dòng HIỂN THỊ lãi suất (job Taylor_20261102_015334; user duyệt 02/11/2026 08:53).

DISPLAY-ONLY. KHÔNG đổi FV / MoS / classify_dcf; KHÔNG nối vào plan echo, DCF_RICH hay đường đặt lệnh.
  (i)  r* thị trường: r sao cho median log(P/FV)=0 trên rổ universe_pit (FV = công thức production),
       kèm vị trí so với lịch sử. Là THƯỚC ĐO HIỂN THỊ, KHÔNG phải tín hiệu mua/bán.
  (ii) TPCP 10Y + Δ12 tháng (tav2_bq.macro_indicator, vn_bond_10y). Thiếu/stale -> 'không có dữ liệu'.
r* tính bằng analysis.rstar của job dcf_rate_proxy_20261102 (KHÔNG viết lại công thức) trên panel_live;
chỉ chạy khi build cache (hàng tháng / khi đổi mùa BCTC): `python dcf_rate_display.py --build-cache`.
Đọc cache rất rẻ. Cache quá hạn (> RSTAR_MAX_AGE_DAYS so với asof) -> fail-closed.
"""
import json
import os
import sys
import datetime as _dt
import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
RSTAR_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "dcf_rstar_cache.json")  # theo checkout
RSTAR_MAX_AGE_DAYS = 45          # panel_asof cách asof quá số ngày này -> không hiển thị
TPCP_MAX_AGE_DAYS = 7            # quan sát TPCP cuối cách asof quá số ngày này -> không hiển thị
HIST_START = "2014-01"
PEAK_WIN = ("2021-12", "2022-12")     # đỉnh 2022
TROUGH_WIN = ("2022-12", "2023-12")   # đáy 2022-2023
_RESEARCH = os.path.join(WORKDIR, "mike", "agents", "Taylor", "research")
_NA = "không có dữ liệu"
_TPCP_UNVERIFIED = "UNVERIFIED: chưa có nguồn thứ hai khớp ≤0,2pp; vs VBMA 05–07/2026 lệch +0,13…+0,21pp"


def _asof_date(asof):
    return pd.to_datetime(asof).date()


# ---------------------------------------------------------------- (i) r*
def build_rstar_cache(path=RSTAR_CACHE):
    """Tính r* theo tháng bằng analysis.rstar (job dcf_rate_proxy_20261102) trên panel_live. Ghi nguyên tử."""
    rd = os.path.join(_RESEARCH, "dcf_rate_proxy_20261102")
    sys.path.insert(0, rd)
    import analysis as A                                   # noqa: E402  (đổi cwd sang engine — path dưới tuyệt đối)
    p = A.load_panel()
    s = A.rstar(p, A.G_CAP)
    out = {"built_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
           "panel_asof": str(p.t.max().date()), "g_cap": A.G_CAP, "r_const": A.R_CONST * 100,
           "n_last": int((p.t == p.t.max()).sum()),
           "series": {str(k): round(float(v), 4) for k, v in s.items()}}
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    os.replace(tmp, path)
    return out


def rstar_line(asof, path=RSTAR_CACHE):
    try:
        c = json.load(open(path))
        ser = pd.Series(c["series"]); ser.index = pd.PeriodIndex(ser.index, freq="M")
        pa = pd.to_datetime(c["panel_asof"]).date()
        age = (_asof_date(asof) - pa).days
        if age > RSTAR_MAX_AGE_DAYS or age < 0:
            return f"r* thị trường: {_NA} (cache panel {pa}, cách {age} ngày)"
        h = ser.loc[HIST_START:]
        cur = float(h.iloc[-1]); pct = float((h <= cur).mean() * 100)
        pk = h.loc[PEAK_WIN[0]:PEAK_WIN[1]]; tr = h.loc[TROUGH_WIN[0]:TROUGH_WIN[1]]
        return (f"r* thị trường {cur:.1f}% (panel {pa}, n={c.get('n_last')} mã; r hằng 12,25%) · "
                f"percentile {pct:.0f}% lịch sử {HIST_START}→{h.index[-1]} · "
                f"đỉnh 2022 {pk.max():.1f}% ({pk.idxmax()}), đáy 2022–23 {tr.min():.1f}% ({tr.idxmin()}) "
                f"[DISPLAY-ONLY, thước đo hiển thị, KHÔNG phải tín hiệu mua/bán]")
    except Exception as e:                                  # fail-closed: không điền số cũ
        return f"r* thị trường: {_NA} ({type(e).__name__})"


# ---------------------------------------------------------------- (ii) TPCP 10Y
def _bq_tpcp(asof):
    from google.cloud import bigquery
    d = _asof_date(asof)
    q = ("SELECT observation_date d, value v, fetched_at f FROM tav2_bq.macro_indicator "
         "WHERE series_key='vn_bond_10y' AND observation_date BETWEEN @a AND @b ORDER BY 1")
    cfg = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("a", "DATE", d - _dt.timedelta(days=400)),
        bigquery.ScalarQueryParameter("b", "DATE", d)])
    df = bigquery.Client(project="lithe-record-440915-m9").query(q, job_config=cfg).to_dataframe()
    return df


def tpcp_line(asof, loader=_bq_tpcp):
    """loader(asof) -> DataFrame[d, v, f]. Thiếu / stale / lỗi -> 'không có dữ liệu'."""
    try:
        df = loader(asof)
        df = df.dropna(subset=["v"]).copy()
        df["d"] = pd.to_datetime(df["d"])
        a = pd.Timestamp(_asof_date(asof))
        df = df[df.d <= a].sort_values("d")
        if df.empty:
            return f"TPCP 10Y: {_NA} (không có quan sát)"
        last = df.iloc[-1]
        age = (a - last.d).days
        if age > TPCP_MAX_AGE_DAYS:
            return f"TPCP 10Y: {_NA} (quan sát cuối {last.d.date()}, cách {age} ngày)"
        tgt = last.d - pd.DateOffset(years=1)
        prev = df[(df.d <= tgt) & (df.d >= tgt - pd.Timedelta(days=7))]
        if prev.empty:
            dtxt = "Δ12T: không có dữ liệu"
        else:
            pv = prev.iloc[-1]
            dtxt = f"Δ12T {last.v - pv.v:+.2f}pp (từ {pv.v:.2f}% @{pv.d.date()})"
        f = pd.to_datetime(last.get("f")) if "f" in df.columns and pd.notna(last.get("f")) else None
        ftxt = f", fetch {f.date()}" if f is not None else ""
        return f"TPCP 10Y {last.v:.2f}% @{last.d.date()} (trễ {age} ngày{ftxt}) · {dtxt} [{_TPCP_UNVERIFIED}]"
    except Exception as e:
        return f"TPCP 10Y: {_NA} ({type(e).__name__})"


def dcf_rate_lines(asof, rstar_path=RSTAR_CACHE, tpcp_loader=_bq_tpcp):
    return [rstar_line(asof, rstar_path), tpcp_line(asof, tpcp_loader)]


if __name__ == "__main__":
    if "--build-cache" in sys.argv:
        c = build_rstar_cache(); print("built", c["panel_asof"], len(c["series"]))
    else:
        a = sys.argv[1] if len(sys.argv) > 1 else _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=7))).date().isoformat()
        print("\n".join(dcf_rate_lines(a)))
