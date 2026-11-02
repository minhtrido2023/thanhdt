# -*- coding: utf-8 -*-
"""dcf_rstar_refresh — làm mới cache r* (dòng hiển thị DCF) HẰNG THÁNG, một lệnh (job Taylor_20261102_034815).

DISPLAY-ONLY. Không đụng dcf_valuation.py / FV / MoS / lệnh. Thay chuỗi tay 4 bước của dcf_rate_display.py (phương án A').
  1. engine.build() (dcf_vn_calibration_20261101)  -> panel_monthly   } dựng ở THƯ MỤC TẠM, bằng chính hàm của
  2. build_live (dcf_level_rerun_20261102), OShares PIT live (1 lần BQ) -> os_live  } nghiên cứu (import, đọc-chỉ), đường
  3. level.load()                                   -> panel_live     } ra bị chuyển hướng: KHÔNG ghi đè file nghiên cứu đã track
  4. analysis.rstar (dcf_rate_proxy_20261102) qua dcf_rate_display.build_rstar_cache(panel=...) -> cache
Cache ra: data/cache_untracked/dcf_rstar_cache.json (.gitignore) — dcf_rate_display đọc cache có panel_asof MỚI NHẤT.
Chỉ dùng THÁNG ĐÃ ĐÓNG (t trong tháng lịch trước tháng ICT hiện tại): tháng đang chạy dở không vào panel.

CONTROL (luôn chạy, `--force` KHÔNG bỏ được): chuỗi r* mới phải khớp cache nền (cache có panel_asof mới nhất đang tồn
tại) trên mọi tháng ≤ panel_asof của nó, sai số ≤ TOL_PP (0,05pp) — sai thì KHÔNG ghi cache, rc=4. Lối thoát duy nhất,
tường minh: `--accept-control-drift` (log đầy đủ diff từng tháng + ghi `control_drift_accepted` vào cache; runbook ở
kb/cron_registry_dcf_rstar_refresh.proposed). `--until YYYY-MM-DD --out PATH` dựng lại đến ngày đó ra PATH tuỳ chọn.
Đã đủ tháng (cache nền cùng tháng với mốc cắt, không --until/--force) -> thoát rc=0 NGAY, không dựng.
Kiểm tháng đóng THẬT: t cuối của panel phải = phiên giao dịch cuối ≤ mốc cắt (trading_bot.vn_market), sai -> rc=3.

rc: 0 ok (kể cả "đã đủ tháng" và "chưa mới hơn nhưng cache còn tươi ≤ ALERT_AGE_DAYS" — im lặng, cron thử lại) ·
    2 panel không mới hơn cache nền VÀ cache đã quá ALERT_AGE_DAYS (lần làm mới lỡ) · 3 lỗi dựng (BQ, dữ liệu, tháng dở) ·
    4 control lệch · 5 (--check-expiry) cache tuổi > ALERT_AGE_DAYS hoặc đã hết hạn.
Chạy:  $DNA_PYEXE dcf_rstar_refresh.py [--until D] [--out P] [--check-expiry] [--force] [--accept-control-drift]
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
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
RES = os.path.join(WC, "mike", "agents", "Taylor", "research")
CAL = os.path.join(RES, "dcf_vn_calibration_20261101")
LVL = os.path.join(RES, "dcf_level_rerun_20261102")
sys.path.insert(0, HERE)
TOL_PP = 0.05
ALERT_AGE_DAYS = 38     # cache tuổi (hôm nay - panel_asof) > ngày này = một lần làm mới tháng đã lỡ (tháng ≤31 ngày + 7 ngày thử lại)
ICT = _dt.timezone(_dt.timedelta(hours=7))
RC_NOT_NEWER, RC_BUILD, RC_CONTROL, RC_EXPIRY = 2, 3, 4, 5


class RefreshError(Exception):
    def __init__(self, rc, msg, tb=None):
        super().__init__(msg)
        self.rc = rc
        self.tb = tb


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


def expiry_status(caches, today, max_age, alert_age=ALERT_AGE_DAYS):
    """(rc, msg). Hết hạn khi tuổi > max_age (dòng hiển thị đã NA); cảnh báo khi tuổi > alert_age = một lần làm mới
    hằng tháng thực sự lỡ (chạy hằng tháng nên tuổi bình thường ≤ ~31 ngày + cửa sổ thử lại)."""
    c = newest(caches)
    if c is None:
        return RC_EXPIRY, "KHÔNG có cache r* nào — dòng r* hiển thị 'không có dữ liệu'"
    pa = _dt.date.fromisoformat(c["panel_asof"])
    age = (today - pa).days
    if age > max_age:
        return RC_EXPIRY, f"cache r* ĐÃ HẾT HẠN {age - max_age} ngày (panel_asof {pa}, tuổi {age}, hạn {max_age} ngày)"
    if age > alert_age:
        return RC_EXPIRY, (f"cache r* tuổi {age} ngày > {alert_age} (panel_asof {pa}): lần làm mới hằng tháng bị lỡ, "
                           f"còn {max_age - age} ngày trước khi dòng r* hiển thị 'không có dữ liệu'; chạy dcf_rstar_refresh.py")
    return 0, f"cache r* tuổi {age} ngày (panel_asof {pa}, báo khi > {alert_age})"


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


def last_trading_day(cutoff):
    """Phiên giao dịch cuối cùng ≤ cutoff (date): bỏ T7/CN và ngày lễ theo trading_bot.vn_market."""
    from trading_bot.vn_market import is_holiday
    d = cutoff
    while d.weekday() >= 5 or is_holiday(d):
        d -= _dt.timedelta(days=1)
    return d


def check_month_closed(tmax, cutoff):
    """tmax (date): t cuối của panel. Phải = phiên cuối ≤ cutoff, nếu không dữ liệu giá/universe dừng giữa tháng
    (hoặc tháng chưa đóng) -> RefreshError rc=3 kèm bằng chứng."""
    exp = last_trading_day(cutoff)
    if tmax != exp:
        raise RefreshError(RC_BUILD, f"THÁNG CHƯA ĐÓNG ĐỦ: t cuối của panel = {tmax}, phiên giao dịch cuối ≤ {cutoff} phải là {exp} "
                           f"(VNINDEX trong bq_cache dừng sớm hoặc cutoff sai) — không dựng cache từ tháng dở")


def _under(tmp, path):
    """path phải nằm dưới tmp (chống ghi đè file nghiên cứu đã track)."""
    ap, at = os.path.abspath(path), os.path.abspath(tmp)
    assert ap == at or ap.startswith(at + os.sep), f"đường ghi {ap} KHÔNG nằm dưới thư mục tạm {at}"


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
    _under(tmp, E.DATA)
    t0 = time.time()
    E.build()
    pan = pd.read_parquet(os.path.join(cal, "data", "panel_monthly.parquet"))
    n0 = len(pan)
    pan = pan[pan.t <= pd.Timestamp(cutoff)]
    if pan.empty:
        raise RefreshError(RC_BUILD, f"panel rỗng sau khi cắt tới {cutoff}")
    check_month_closed(pan.t.max().date(), _dt.date.fromisoformat(str(cutoff)[:10]))
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
    _under(tmp, LV.OLD); _under(tmp, LV.DATA)
    p = LV.load()
    p = p.drop(columns=[c for c in p.columns if c in ("rt",)])
    log(f"panel_live {len(p)} dòng, {p.t.nunique()} tháng, t max {p.t.max().date()}")
    return p


# ------------------------------------------------------------------ chính
def refresh(out_path, until=None, force=False, tmp_root=None, builder=build_panel, today=None,
            baseline_paths=None, accept_drift=False):
    import dcf_rate_display as DISP
    today = today or today_ict()
    cutoff = closed_months_cutoff(today, until)
    base_paths = baseline_paths or [DISP.RSTAR_CACHE, DISP.RSTAR_CACHE_LIVE]
    base = newest(load_caches(base_paths))
    if base and until is None and not force and base["panel_asof"][:7] >= cutoff.isoformat()[:7]:
        log(f"cache nền đã tới tháng {base['panel_asof'][:7]} (panel_asof {base['panel_asof']}) = tháng đóng gần nhất "
            f"{cutoff:%Y-%m} — không cần làm mới, không dựng")
        return None
    tmp = tempfile.mkdtemp(prefix="rstar_refresh_", dir=tmp_root)
    try:
        try:
            p = builder(tmp, cutoff.isoformat())
        except RefreshError:
            raise
        except Exception as e:
            raise RefreshError(RC_BUILD, f"dựng panel lỗi: {type(e).__name__}: {e}", traceback.format_exc())
        new_asof = str(p.t.max().date())
        if base and new_asof <= base["panel_asof"] and not force:
            age = (today - _dt.date.fromisoformat(base["panel_asof"])).days
            msg = (f"panel_asof {new_asof} KHÔNG mới hơn cache nền {base['panel_asof']} ({base['_path']}), tuổi cache {age} ngày "
                   f"— dữ liệu tháng đóng chưa nạp vào bq_cache; không ghi gì")
            if age <= ALERT_AGE_DAYS:
                log(msg + f" · cache còn tươi (≤ {ALERT_AGE_DAYS} ngày) -> im lặng, cron thử lại")
                return None
            raise RefreshError(RC_NOT_NEWER, msg + f" · cache tuổi > {ALERT_AGE_DAYS} ngày: lần làm mới tháng đã LỠ")
        # tính r* vào file tạm, kiểm control, rồi mới atomic-rename sang đích
        stage = os.path.join(tmp, "stage.json")
        try:
            c = DISP.build_rstar_cache(path=stage, panel=p)
        except Exception as e:
            raise RefreshError(RC_BUILD, f"tính r* lỗi: {type(e).__name__}: {e}", traceback.format_exc())
        if base:
            worst, wm, missing = control_compare(c["series"], base["series"])
            log(f"CONTROL vs {base['_path']} (asof {base['panel_asof']}): {len(base['series'])} tháng, "
                f"max|Δ|={worst:.4f}pp tại {wm}, thiếu {len(missing)} tháng, dung sai {TOL_PP}pp")
            if worst > TOL_PP or missing:
                bad = sorted((m, base["series"][m], c["series"][m]) for m in base["series"]
                             if m in c["series"] and abs(float(c["series"][m]) - float(base["series"][m])) > TOL_PP)
                if not accept_drift:
                    raise RefreshError(RC_CONTROL, f"CONTROL LỆCH: max|Δ|={worst:.4f}pp tại {wm} (>{TOL_PP}) hoặc thiếu tháng {missing[:5]} "
                                       f"({len(bad)} tháng lệch) — KHÔNG ghi cache. Đối chiếu vintage dữ liệu/phiên bản code; "
                                       f"nếu lệch là CHỦ ĐÍCH (vendor sửa lịch sử): runbook trong kb/cron_registry_dcf_rstar_refresh.proposed, "
                                       f"chạy lại với --accept-control-drift.")
                log(f"--accept-control-drift: CHẤP NHẬN lệch {len(bad)} tháng, thiếu {len(missing)} tháng — diff từng tháng (cũ -> mới, Δpp):")
                for m, ov, nv in bad:
                    log(f"  {m}: {float(ov):.4f} -> {float(nv):.4f} ({float(nv) - float(ov):+.4f})")
                for m in missing:
                    log(f"  {m}: {float(base['series'][m]):.4f} -> (THIẾU trong chuỗi mới)")
                c["control_drift_accepted"] = {"max_pp": round(worst, 4), "month": wm, "n_months": len(bad),
                                               "missing": missing, "baseline": base["_path"], "baseline_asof": base["panel_asof"]}
                with open(stage, "w") as f:
                    json.dump(c, f, indent=1, sort_keys=True)
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
    ap.add_argument("--accept-control-drift", action="store_true",
                    help="ghi cache dù control lệch (log đầy đủ diff từng tháng); chỉ khi lệch là chủ đích — xem runbook")
    a = ap.parse_args(argv)
    import dcf_rate_display as DISP
    if a.check_expiry:
        rc, msg = expiry_status(load_caches([DISP.RSTAR_CACHE, DISP.RSTAR_CACHE_LIVE]), today_ict(), DISP.RSTAR_MAX_AGE_DAYS)
        log(msg)
        return rc
    out = os.path.abspath(a.out or DISP.RSTAR_CACHE_LIVE)   # TRƯỚC refresh: engine.py chdir -> --out tương đối sẽ rơi vào thư mục nghiên cứu
    try:
        refresh(out, until=a.until, force=a.force, accept_drift=a.accept_control_drift)
    except RefreshError as e:
        if e.tb:
            print(e.tb, file=sys.stderr)
        print(f"LỖI rc={e.rc}: {e}", file=sys.stderr)
        return e.rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
