# -*- coding: utf-8 -*-
"""dcf_rstar_refresh — làm mới cache r* (dòng hiển thị DCF) HẰNG THÁNG, một lệnh (job Taylor_20261102_034815).

DISPLAY-ONLY. Không đụng dcf_valuation.py / FV / MoS / lệnh. Thay chuỗi tay 4 bước của dcf_rate_display.py (phương án A').
  1. engine.build() (dcf_vn_calibration_20261101)  -> panel_monthly   } dựng ở THƯ MỤC TẠM, bằng chính hàm của
  2. build_live (dcf_level_rerun_20261102), OShares PIT live (1 lần BQ) -> os_live  } nghiên cứu (import, đọc-chỉ), đường
  3. level.load()                                   -> panel_live     } ra bị chuyển hướng: KHÔNG ghi đè file nghiên cứu đã track
  4. analysis.rstar (dcf_rate_proxy_20261102) qua dcf_rate_display.build_rstar_cache(panel=...) -> cache
Cache ra: data/cache_untracked/dcf_rstar_cache.json (.gitignore) — dcf_rate_display đọc cache có panel_asof MỚI NHẤT.
Chỉ dùng THÁNG ĐÃ ĐÓNG (t trong tháng lịch trước tháng ICT hiện tại): tháng đang chạy dở không vào panel.

CONTROL (luôn chạy, không tắt được): chuỗi r* mới phải khớp cache nền (cache có panel_asof mới nhất đang tồn tại)
trên mọi tháng ≤ panel_asof của nó, sai số ≤ TOL_PP (0,05pp) — sai thì KHÔNG ghi cache, rc=4.
`--until YYYY-MM-DD --out PATH` dựng lại đến ngày đó ra PATH tuỳ chọn (dùng để tái lập cache tracked).

rc: 0 ok · 2 panel không mới hơn cache nền (vendor chưa nạp / chạy sớm) · 3 lỗi dựng (BQ, dữ liệu) ·
    4 control lệch · 5 (--check-expiry) cache sắp/đã hết hạn.
Chạy:  $DNA_PYEXE dcf_rstar_refresh.py [--until D] [--out P] [--check-expiry] [--force]
Lỗi in nguyên văn ra stderr (§29: không nuốt, không đoán nguyên nhân); vỏ cron: bin/fund_bench_cron.sh.
"""
import argparse
import datetime as _dt
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
RES = os.path.join(WC, "mike", "agents", "Taylor", "research")
CAL = os.path.join(RES, "dcf_vn_calibration_20261101")
LVL = os.path.join(RES, "dcf_level_rerun_20261102")
sys.path.insert(0, HERE)
TOL_PP = 0.05
WARN_DAYS = 10
ICT = _dt.timezone(_dt.timedelta(hours=7))
RC_NOT_NEWER, RC_BUILD, RC_CONTROL, RC_EXPIRY = 2, 3, 4, 5


class RefreshError(Exception):
    def __init__(self, rc, msg):
        super().__init__(msg)
        self.rc = rc


def log(msg):
    print(f"[dcf_rstar_refresh {_dt.datetime.now(ICT):%Y-%m-%d %H:%M:%S} ICT] {msg}", flush=True)


def today_ict():
    return _dt.datetime.now(ICT).date()


# ------------------------------------------------------------------ cache nền / hết hạn
def load_caches(paths):
    out = []
    for p in paths:
        try:
            c = json.load(open(p))
            c["_path"] = p
            out.append(c)
        except FileNotFoundError:
            continue
        except Exception as e:
            log(f"CẢNH BÁO cache {p} không đọc được ({type(e).__name__}: {e}) — bỏ qua")
    return out


def newest(caches):
    return max(caches, key=lambda c: c["panel_asof"]) if caches else None


def expiry_status(caches, today, max_age, warn_days=WARN_DAYS):
    """(rc, msg). Hết hạn khi today - panel_asof > max_age; cảnh báo khi còn < warn_days."""
    c = newest(caches)
    if c is None:
        return RC_EXPIRY, "KHÔNG có cache r* nào — dòng r* hiển thị 'không có dữ liệu'"
    pa = _dt.date.fromisoformat(c["panel_asof"])
    left = max_age - (today - pa).days
    if left < 0:
        return RC_EXPIRY, f"cache r* ĐÃ HẾT HẠN {-left} ngày (panel_asof {pa}, hạn {max_age} ngày)"
    if left < warn_days:
        return RC_EXPIRY, f"cache r* còn {left} ngày hết hạn (panel_asof {pa}); chạy dcf_rstar_refresh.py"
    return 0, f"cache r* còn {left} ngày (panel_asof {pa})"


def control_compare(new_series, base_series, tol_pp=TOL_PP):
    """So chuỗi mới vs nền trên mọi tháng của nền. Trả (max|Δ|, tháng_tệ_nhất, tháng_thiếu)."""
    worst, wm, missing = 0.0, None, []
    for m, v in base_series.items():
        if m not in new_series:
            missing.append(m)
            continue
        d = abs(float(new_series[m]) - float(v))
        if d > worst:
            worst, wm = d, m
    return worst, wm, missing


def closed_months_cutoff(today, until=None):
    """Mốc cắt: t phải ≤ until (nếu có) và thuộc tháng lịch < tháng hiện tại (trừ khi until cho trước)."""
    if until is not None:
        return _dt.date.fromisoformat(until)
    first = today.replace(day=1)
    return first - _dt.timedelta(days=1)


# ------------------------------------------------------------------ dựng panel (thư mục tạm)
def build_panel(tmp, cutoff):
    """Trả panel_live (DataFrame) với mọi t ≤ cutoff. Mọi file trung gian nằm trong tmp."""
    import numpy as np
    import pandas as pd
    cal = os.path.join(tmp, "cal"); lv = os.path.join(tmp, "lv")
    os.makedirs(os.path.join(cal, "data")); os.makedirs(os.path.join(lv, "data"))
    shutil.copy(os.path.join(CAL, "data", "px_2008_2012.csv.gz"), os.path.join(cal, "data"))
    sys.path.insert(0, CAL); sys.path.insert(0, WC)
    os.environ["DCF_RATE_FRAME"] = "domestic_v2"
    import engine as E
    E.DATA = os.path.join(cal, "data")                     # build() đọc/ghi qua biến module này -> thư mục tạm
    t0 = time.time()
    E.build()
    pan = pd.read_parquet(os.path.join(cal, "data", "panel_monthly.parquet"))
    n0 = len(pan)
    pan = pan[pan.t <= pd.Timestamp(cutoff)]
    if pan.empty:
        raise RefreshError(RC_BUILD, f"panel rỗng sau khi cắt tới {cutoff}")
    # tháng đang dở: t cuối của panel phải là phiên cuối tháng đã đóng (cutoff là cuối tháng lịch trước) — kiểm
    pan.to_parquet(os.path.join(cal, "data", "panel_monthly.parquet"))
    log(f"engine.build xong {time.time()-t0:.0f}s: panel {n0} dòng -> {len(pan)} (t ≤ {cutoff}, t max {pan.t.max().date()})")
    # OShares live PIT (copy nguyên build_live.py của dcf_level_rerun_20261102, đổi đường dẫn)
    import oshares_pit as OP
    import oshares_live as OL
    import dcf_valuation as D
    tol = 0.005
    assert D.LIVE_BELOW_FIN_TOL == tol, f"LIVE_BELOW_FIN_TOL production {D.LIVE_BELOW_FIN_TOL} != {tol}"
    p0 = pan[["t", "ticker", "OShares"]]
    tks = sorted(p0.ticker.unique()); until = str(p0.t.max().date())
    t0 = time.time()
    cache = OL._fetch(tks, until)
    log(f"BQ OShares live {time.time()-t0:.0f}s: quý {len(cache[0])}, corp {len(cache[1])}")
    out = []
    for t, g in p0.groupby("t"):
        fb = dict(zip(g.ticker, g.OShares))
        recs = OP.oshares_pit(list(g.ticker), str(t.date()), fb, cache=cache)
        for tk in g.ticker:
            r = recs[tk]
            out.append((t, tk, r["value"], r["source"], r.get("method"), r.get("live_value")))
    L = pd.DataFrame(out, columns=["t", "ticker", "os_pit", "source", "method", "live_value"]).merge(p0, on=["t", "ticker"])
    below = (L.source == "oshares_live") & (L.os_pit < L.OShares * (1 - tol))
    L["os_live"] = np.where(below, L.OShares, L.os_pit)
    L["r10_fallback"] = below
    L.to_parquet(os.path.join(lv, "data", "os_live.parquet"))
    # level.load() với đường dẫn chuyển hướng (OLD -> cal tạm, DATA -> lv tạm)
    sys.path.insert(0, LVL)
    import level as LV
    LV.OLD, LV.DATA = cal, os.path.join(lv, "data")
    p = LV.load()
    p = p.drop(columns=[c for c in p.columns if c in ("rt",)])
    log(f"panel_live {len(p)} dòng, {p.t.nunique()} tháng, t max {p.t.max().date()}")
    return p


# ------------------------------------------------------------------ chính
def refresh(out_path, until=None, force=False, tmp_root=None, builder=build_panel, today=None,
            baseline_paths=None):
    import dcf_rate_display as DISP
    today = today or today_ict()
    cutoff = closed_months_cutoff(today, until)
    base_paths = baseline_paths or [DISP.RSTAR_CACHE, DISP.RSTAR_CACHE_LIVE]
    base = newest(load_caches(base_paths))
    tmp = tempfile.mkdtemp(prefix="rstar_refresh_", dir=tmp_root)
    try:
        try:
            p = builder(tmp, cutoff.isoformat())
        except RefreshError:
            raise
        except Exception as e:
            raise RefreshError(RC_BUILD, f"dựng panel lỗi: {type(e).__name__}: {e}")
        new_asof = str(p.t.max().date())
        if base and new_asof <= base["panel_asof"] and not force:
            raise RefreshError(RC_NOT_NEWER, f"panel_asof {new_asof} KHÔNG mới hơn cache nền {base['panel_asof']} "
                               f"({base['_path']}) — vendor chưa nạp BCTC/giá mới hoặc chạy sớm; không ghi gì")
        # tính r* vào file tạm, kiểm control, rồi mới atomic-rename sang đích
        stage = os.path.join(tmp, "stage.json")
        try:
            c = DISP.build_rstar_cache(path=stage, panel=p)
        except Exception as e:
            raise RefreshError(RC_BUILD, f"tính r* lỗi: {type(e).__name__}: {e}")
        if base:
            worst, wm, missing = control_compare(c["series"], base["series"])
            log(f"CONTROL vs {base['_path']} (asof {base['panel_asof']}): {len(base['series'])} tháng, "
                f"max|Δ|={worst:.4f}pp tại {wm}, thiếu {len(missing)} tháng, dung sai {TOL_PP}pp")
            if worst > TOL_PP or missing:
                raise RefreshError(RC_CONTROL, f"CONTROL LỆCH: max|Δ|={worst:.4f}pp tại {wm} (>{TOL_PP}) hoặc thiếu tháng {missing[:5]} "
                                   f"— KHÔNG ghi cache. Đối chiếu vintage dữ liệu/phiên bản code.")
        else:
            log("không có cache nền — bỏ qua control (lần dựng đầu tiên)")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        tmpo = out_path + ".tmp"
        shutil.copyfile(stage, tmpo)
        os.replace(tmpo, out_path)                          # nguyên tử
        log(f"GHI {out_path}: panel_asof {c['panel_asof']}, {len(c['series'])} tháng, n_last {c['n_last']}, "
            f"r* cuối {list(c['series'].values())[-1]:.2f}%")
        return c
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--until"); ap.add_argument("--out"); ap.add_argument("--force", action="store_true")
    ap.add_argument("--check-expiry", action="store_true")
    a = ap.parse_args(argv)
    import dcf_rate_display as DISP
    if a.check_expiry:
        rc, msg = expiry_status(load_caches([DISP.RSTAR_CACHE, DISP.RSTAR_CACHE_LIVE]), today_ict(), DISP.RSTAR_MAX_AGE_DAYS)
        log(msg)
        return rc
    out = a.out or DISP.RSTAR_CACHE_LIVE
    try:
        refresh(out, until=a.until, force=a.force)
    except RefreshError as e:
        print(f"LỖI rc={e.rc}: {e}", file=sys.stderr)
        return e.rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
