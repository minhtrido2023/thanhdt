# -*- coding: utf-8 -*-
"""DCF — 2 dòng HIỂN THỊ lãi suất (job Taylor_20261102_015334; user duyệt 02/11/2026 08:53).

DISPLAY-ONLY. KHÔNG đổi FV / MoS / classify_dcf; KHÔNG nối vào plan echo, DCF_RICH hay đường đặt lệnh.
  (i)  r* thị trường: r sao cho median log(P/FV)=0 trên rổ universe_pit (FV = công thức production),
       kèm vị trí so với lịch sử. Là THƯỚC ĐO HIỂN THỊ, KHÔNG phải tín hiệu mua/bán.
  (ii) TPCP 10Y + Δ12 tháng (tav2_bq.macro_indicator, vn_bond_10y). Thiếu/stale -> 'không có dữ liệu'.
r* tính bằng analysis.rstar của job dcf_rate_proxy_20261102 (KHÔNG viết lại công thức) trên panel_live;
chỉ chạy khi build cache. LÀM MỚI cache HẰNG THÁNG = `dcf_rstar_refresh.py` (cron; dựng panel ở thư mục tạm, KHÔNG ghi đè file nghiên cứu, ghi
cache ở data/cache_untracked/ — xem docstring script đó). Chuỗi 4 bước dưới đây chỉ còn là đường làm tay/di sản:
⚠️ LÀM MỚI cache (tay) = chuỗi 4 bước, THỨ TỰ BẮT BUỘC (arch-review vòng 2):
  1. `engine.py build` ở research/dcf_vn_calibration_20261101 → dựng lại data/panel_monthly.parquet
     (build_live.py:13 và level.py:21 đọc file này; nó đứng yên ở t max 2026-10-30, bỏ bước này thì kẹt mãi);
  2. build_live.py, 3. level.py (research/dcf_level_rerun_20261102) → data/panel_live.parquet;
  4. RỒI MỚI `python dcf_rate_display.py --build-cache`; nếu panel_asof không mới hơn cache cũ, build_rstar_cache từ chối.
⚠️ Các bước 1-3 GHI ĐÈ file nghiên cứu đã track trong git (out/level_gT_star.csv, out/level_live_impact_20261030.csv,
data/level_LY.pkl, data/ của calibration) mà REPORT.md trích dẫn (§8) — chạy tay trong worktree riêng, KHÔNG đưa vào cron
(xem kb/cron_registry_dcf_rstar.proposed). Cache hết hạn sau RSTAR_MAX_AGE_DAYS.
Đọc cache rất rẻ. Cache quá hạn (> RSTAR_MAX_AGE_DAYS so với asof) -> fail-closed.
"""
import json
import os
import sys
import datetime as _dt
import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
RSTAR_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "dcf_rstar_cache.json")  # theo checkout (TRACKED)
# cache do dcf_rstar_refresh.py ghi (KHÔNG track, .gitignore): được ưu tiên nếu panel_asof mới hơn bản tracked
RSTAR_CACHE_LIVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cache_untracked", "dcf_rstar_cache.json")
RSTAR_MAX_AGE_DAYS = 45          # panel_asof cách asof quá số ngày này -> không hiển thị
BQ_TIMEOUT_S = 30                # trần truy vấn TPCP: BQ treo không được chặn báo cáo newdeals 06:00
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
def build_rstar_cache(path=RSTAR_CACHE, panel=None):
    """Tính r* theo tháng bằng analysis.rstar (job dcf_rate_proxy_20261102) trên panel_live. Ghi nguyên tử.
    panel=None: đọc panel_live.parquet của job nghiên cứu (đường tay). panel=DataFrame: do dcf_rstar_refresh dựng."""
    rd = os.path.join(_RESEARCH, "dcf_rate_proxy_20261102")
    sys.path.insert(0, rd)
    import analysis as A                                   # noqa: E402  (đổi cwd sang engine — path dưới tuyệt đối)
    if panel is None:
        p = A.load_panel()
    else:
        p = panel.reset_index(drop=True).copy()
        p["m"] = p.t.dt.to_period("M")
    new_asof = str(p.t.max().date())
    try:
        old_asof = json.load(open(path)).get("panel_asof")
    except Exception:
        old_asof = None
    if old_asof and new_asof <= old_asof:
        raise RuntimeError(f"panel_live.parquet chưa được dựng lại: panel_asof {new_asof} <= cache cũ {old_asof}. "
                           "Chuỗi làm mới: engine.py build (dcf_vn_calibration_20261101) -> build_live.py -> level.py (dcf_level_rerun_20261102) -> --build-cache; xem docstring đầu file.")
    s = A.rstar(p, A.G_CAP)
    out = {"built_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
           "panel_asof": str(p.t.max().date()), "g_cap": A.G_CAP, "r_const": A.R_CONST * 100,
           "n_last": int((p.t == p.t.max()).sum()),
           "series": {str(k): round(float(v), 4) for k, v in s.items()}}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    os.replace(tmp, path)
    return out


def _newest_cache(paths):
    """Cache có panel_asof mới nhất trong các đường dẫn đọc được; file thiếu/hỏng bị bỏ qua. Không có -> raise."""
    best = None
    for p in paths:
        try:
            c = json.load(open(p))
            pa = str(pd.to_datetime(c["panel_asof"]).date())
        except Exception:
            continue
        if best is None or pa > best[0]:
            best = (pa, c)
    if best is None:
        raise FileNotFoundError("không có cache r* đọc được")
    return best[1]


def rstar_line(asof, path=RSTAR_CACHE, live_path=RSTAR_CACHE_LIVE):
    try:
        c = _newest_cache([path] if live_path is None else [path, live_path])
        ser = pd.Series(c["series"]); ser.index = pd.PeriodIndex(ser.index, freq="M")
        pa = pd.to_datetime(c["panel_asof"]).date()
        age = (_asof_date(asof) - pa).days
        if age > RSTAR_MAX_AGE_DAYS or age < 0:
            return f"r* thị trường: {_NA} (cache panel {pa}, cách {age} ngày)"
        h = ser.loc[HIST_START:]
        cur = float(h.iloc[-1]); pct = float((h <= cur).mean() * 100)
        pk = h.loc[PEAK_WIN[0]:PEAK_WIN[1]]; tr = h.loc[TROUGH_WIN[0]:TROUGH_WIN[1]]
        return (f"r* thị trường {cur:.1f}% (panel {pa}, n={c.get('n_last')} mã; r hằng {float(c['r_const']):.2f}%) · "
                f"percentile {pct:.0f}% lịch sử {HIST_START}→{h.index[-1]} · "
                f"đỉnh 2022 {pk.max():.1f}% ({pk.idxmax()}), đáy 2022–23 {tr.min():.1f}% ({tr.idxmin()}) "
                f"[DISPLAY-ONLY, thước đo hiển thị, KHÔNG phải tín hiệu mua/bán]")
    except Exception as e:                                  # fail-closed: không điền số cũ
        return f"r* thị trường: {_NA} ({type(e).__name__})"


# ---------------------------------------------------------------- (ii) TPCP 10Y
def _bq_tpcp(asof):
    # cron production chạy /usr/bin/python3 trần, không source wc_env.sh -> tự đặt credential (mẫu corp_action_lib.py:30/86)
    os.environ.setdefault("CLOUDSDK_CONFIG", "/home/trido/thanhdt/gcloud_dtienthanh")
    from google.cloud import bigquery
    d = _asof_date(asof)
    q = ("SELECT observation_date d, value v, fetched_at f FROM tav2_bq.macro_indicator "
         "WHERE series_key='vn_bond_10y' AND observation_date BETWEEN @a AND @b ORDER BY 1")
    cfg = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("a", "DATE", d - _dt.timedelta(days=400)),
        bigquery.ScalarQueryParameter("b", "DATE", d)])
    job = bigquery.Client(project="lithe-record-440915-m9").query(q, job_config=cfg, timeout=BQ_TIMEOUT_S)
    return job.result(timeout=BQ_TIMEOUT_S).to_dataframe()


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


def dcf_rate_lines(asof, rstar_path=RSTAR_CACHE, tpcp_loader=_bq_tpcp, rstar_live_path=RSTAR_CACHE_LIVE):
    return [rstar_line(asof, rstar_path, rstar_live_path), tpcp_line(asof, tpcp_loader)]


if __name__ == "__main__":
    if "--build-cache" in sys.argv:
        c = build_rstar_cache(); print("built", c["panel_asof"], len(c["series"]))
    else:
        a = sys.argv[1] if len(sys.argv) > 1 else _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=7))).date().isoformat()
        print("\n".join(dcf_rate_lines(a)))
