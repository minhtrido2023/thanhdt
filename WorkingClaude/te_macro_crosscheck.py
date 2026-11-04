#!/usr/bin/env python3
"""te_macro_crosscheck.py — check chéo HẰNG TUẦN TradingEconomics vs nguồn nội bộ. CHỈ CẢNH BÁO.

Job Taylor_20261104_170501 (plan kb/projects/te-macro-integration-plan-20261104.md, bước C1, user duyệt).
Gắn vào refresh_deposit_cctg_weekly.sh (thứ Hai 08:05 ICT), không có dòng crontab riêng.

  (a) vn_policy_rate (TE) vs sbv_macro_overlay.SBV_REFI_EVENTS. TE là nguồn THAM CHIẾU BỔ SUNG:
      kết quả ghi ở data/te_crosscheck_log.json (file RIÊNG) — KHÔNG đụng data/sbv_verify_log.json,
      không đổi verified_at/verified của sbv_policy_verify.py, không đẩy "verified".
  (b) vn_cpi_yoy (TE) vs cpi_vn.NSO_CPI_YOY_REAL và fiinprox_cpi_monthly_20260914.csv. Chỉ ĐO + đề xuất
      TE có thể làm tầng thay phần nội suy; KHÔNG sửa cpi_vn.py.

Không tạo object BQ, không ghi BQ (chỉ SELECT bảng macro_indicator, writer = bq_admin). Không đọc/ghi
macro_state_live.py. Fail-closed: BQ lỗi hoặc series stale >7 ngày (theo fetched_at) ⇒ nói thẳng, không
điền số cũ. Ngày/giờ neo ICT/UTC tường minh (coding_guidelines §16).

Quy ước nhãn tháng của TE (đo 2026-11-05): observation_date = CUỐI THÁNG của tháng chứa thay đổi
(2023-06-30 = 4,5 cho sự kiện 2023-06-19). Sự kiện đầu tháng sau (vd 2020-10-01) bị TE gán nhãn cuối tháng
trước ⇒ cho phép lệch biên ≤3 ngày, không coi là lệch thật.
"""
import argparse
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
PROJECT = "lithe-record-440915-m9"
TABLE = "tav2_bq.macro_indicator"
STALE_DAYS = 7              # theo fetched_at, không theo observation_date (series tháng gắn nhãn cuối tháng)
RATE_EPS_PP = 0.01          # = RATE_EPS_PP của sbv_policy_verify.py
POLICY_ALERT_FROM = "2014-01"   # SBV_REFI_EVENTS pre-2014 là CONTEXTUAL (±1-2 tháng) ⇒ chỉ thông tin
EDGE_DAYS = 3
CPI_NSO_EPS = 0.05          # NSO là số chính thức, TE phải khớp (đo 13/13 diff 0,00)
CPI_FIIN_EPS = 0.30         # fiinprox: đo 224 tháng max 0,15
HISTORY_KEEP = 52
BQ_TIMEOUT_S = 120          # job.result() không được treo vô hạn

_OVR = os.environ.get("TE_XCHECK_DATA_DIR") if os.environ.get("TE_XCHECK_SELFCHECK") == "1" else None
_SELFCHECK = bool(_OVR)
DATA_DIR = _OVR if _SELFCHECK else os.path.join(HERE, "data")
LOG_PATH = os.path.join(DATA_DIR, "te_crosscheck_log.json")
NOTIFY = os.path.join(HERE, "mike", "bin", "notify_thread.sh")
FIIN_CSV = os.environ.get("FIINPRO_CPI_CSV") or os.path.join(
    HERE, "mike", "data", "fiinprox_cpi_monthly_20260914.csv")


class Unavailable(Exception):
    """Không kiểm được (BQ lỗi / stale / thiếu dữ liệu) — báo thẳng, không điền số cũ."""


def _now():
    fake = os.environ.get("TE_XCHECK_FAKE_NOW") if _SELFCHECK else None
    return datetime.fromisoformat(fake).astimezone(timezone.utc) if fake else datetime.now(timezone.utc)


# ───────────────────────── nguồn TE (BQ, chỉ đọc) ─────────────────────────
def fetch_te(series_key):
    """-> ({'YYYY-MM-DD' obs_date: float}, max_fetched_at aware-UTC). Dòng trùng obs_date: lấy fetched_at mới nhất."""
    if _SELFCHECK and os.environ.get("TE_XCHECK_FIXTURE"):
        fx = json.load(open(os.environ["TE_XCHECK_FIXTURE"]))[series_key]
        if fx.get("error"):
            raise Unavailable(f"{series_key}: truy vấn BQ lỗi (giả lập): {fx['error']}")
        return fx["rows"], datetime.fromisoformat(fx["fetched_at"]).astimezone(timezone.utc)
    try:
        from google.cloud import bigquery
        cl = bigquery.Client(project=PROJECT)
        job = cl.query(
            f"SELECT observation_date d, value v, fetched_at f FROM {TABLE} AS t "
            f"WHERE series_key=@k ORDER BY d, f",
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("k", "STRING", series_key)]))
        res = list(job.result(timeout=BQ_TIMEOUT_S))
    except Exception as e:  # noqa: BLE001 — trích lỗi thật (§29)
        raise Unavailable(f"{series_key}: truy vấn BQ lỗi: {e!r}"[:400])
    if not res:
        raise Unavailable(f"{series_key}: BQ trả 0 dòng")
    rows, fmax = {}, None
    for r in res:
        rows[str(r["d"])] = float(r["v"])
        f = r["f"]
        f = f if f.tzinfo else f.replace(tzinfo=timezone.utc)
        fmax = f if fmax is None or f > fmax else fmax
    return rows, fmax


def require_fresh(series_key, fetched_at):
    age = _now() - fetched_at
    if age > timedelta(days=STALE_DAYS):
        raise Unavailable(f"{series_key}: fetched_at mới nhất {fetched_at:%Y-%m-%d %H:%M}Z cách {age.days} ngày "
                          f"(>{STALE_DAYS}) — writer bq_admin có thể hỏng; KHÔNG dùng số cũ")


# ───────────────────────── (a) lãi điều hành ─────────────────────────
def _expected(events, ymd):
    cand = [float(r) for t, r in events if t <= ymd]
    return cand[-1] if cand else None


def check_policy(te, events):
    """te: {obs_date: v}; events: [(date, rate)]. -> dict(alerts, info, current)."""
    from datetime import date
    alerts, info = [], []
    for d in sorted(te):
        v = te[d]
        exp = _expected(events, d)
        if exp is None:
            continue
        edge = (date.fromisoformat(d) + timedelta(days=EDGE_DAYS)).isoformat()
        exp2 = _expected(events, edge)
        if abs(v - exp) <= RATE_EPS_PP or (exp2 is not None and abs(v - exp2) <= RATE_EPS_PP):
            continue
        row = {"month_end": d, "te": v, "ours": exp}
        (alerts if d[:7] >= POLICY_ALERT_FROM else info).append(row)
    last_d = max(te)
    ev_t, ev_r = events[-1]
    cur = {"te_obs": last_d, "te": te[last_d], "ours_event": [ev_t, float(ev_r)],
           "match": abs(te[last_d] - float(ev_r)) <= RATE_EPS_PP}
    return {"alerts": alerts, "info_pre2014": info, "current": cur}


# ───────────────────────── (b) CPI ─────────────────────────
def _ym(s):
    return s[:7]


def load_fiin(path=None):
    path = path or FIIN_CSV
    if not os.path.exists(path):
        raise Unavailable(f"không thấy {path} (worktree không có mike/ — .gitignore:107)")
    out = {}
    with open(path) as fh:
        hdr = fh.readline().strip().split(",")
        i_m, i_c = hdr.index("month"), hdr.index("cpi_yoy_pct")
        for ln in fh:
            p = ln.rstrip("\n").split(",")
            if len(p) > i_c and p[i_c] != "":
                out[p[i_m]] = float(p[i_c])
    return out


def _cmp(te_by_m, ref, eps):
    diffs = {m: round(te_by_m[m] - ref[m], 4) for m in sorted(ref) if m in te_by_m}
    bad = {m: d for m, d in diffs.items() if abs(d) > eps}
    ab = [abs(x) for x in diffs.values()]
    return {"n": len(diffs), "mean_abs": round(sum(ab) / len(ab), 4) if ab else None,
            "max_abs": round(max(ab), 4) if ab else None, "eps": eps,
            "n_over_eps": len(bad), "over_eps": bad,
            "first": min(diffs) if diffs else None, "last": max(diffs) if diffs else None}


def interp_tier2(anchors):
    """Nội suy tuyến tính theo THÁNG giữa các neo Tier 2 (cùng cách cpi_vn.cpi_monthly_df) -> {'YYYY-MM': v}."""
    pts = sorted((_ym(t), float(v)) for t, v in anchors)
    idx = lambda ym: int(ym[:4]) * 12 + int(ym[5:7]) - 1
    out = {}
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        ia, ib = idx(a), idx(b)
        for i in range(ia, ib):
            out[f"{i // 12:04d}-{i % 12 + 1:02d}"] = va + (vb - va) * (i - ia) / (ib - ia)
    return out


def check_cpi(te, nso, fiin, anchors=None):
    """te: {obs_date: v}; nso: {'YYYY-MM-01': v}; fiin: {'YYYY-MM': v}. -> dict."""
    te_m = {_ym(d): v for d, v in te.items()}
    nso_m = {_ym(d): v for d, v in nso.items()}
    r_nso = _cmp(te_m, nso_m, CPI_NSO_EPS)
    r_fiin = _cmp(te_m, fiin, CPI_FIIN_EPS)
    fiin_last = max(fiin)
    t2 = None
    if anchors:  # info: sai số nội suy Tier 2 so với TE (không alert) — cơ sở "TE thay nội suy"
        r = _cmp(te_m, {m: v for m, v in interp_tier2(anchors).items() if m < min(nso_m)}, 9e9)
        t2 = {k: r[k] for k in ("n", "mean_abs", "max_abs", "first", "last")}
    beyond = {m: v for m, v in sorted(te_m.items()) if m > fiin_last}
    alerts = []
    for m, d in r_nso["over_eps"].items():
        alerts.append({"vs": "NSO", "month": m, "te": te_m[m], "ref": nso_m[m], "diff": d})
    for m, d in r_fiin["over_eps"].items():
        alerts.append({"vs": "fiinprox", "month": m, "te": te_m[m], "ref": fiin[m], "diff": d})
    ok = r_nso["n"] >= 10 and r_fiin["n"] >= 100 and not alerts
    tier = {"te_months_total": len(te_m), "te_first": min(te_m), "fiin_last": fiin_last, "tier2_interp_vs_te": t2,
            "te_months_beyond_fiin": beyond,
            "can_replace_interpolation": ok,
            "note": ("TE khớp NSO và fiinprox trong ngưỡng ⇒ đủ tư cách làm tầng ngay DƯỚI NSO (Tier 1) và "
                     "NGANG fiinprox (Tier 1.5), phủ các tháng sau FIINPRO_CPI_LAST_MONTH và trước 2008; "
                     "KHÔNG sửa cpi_vn.py trong lượt này.") if ok else
            "TE chưa đủ khớp / thiếu mẫu ⇒ KHÔNG đề xuất làm tầng; xem alerts."}
    return {"alerts": alerts, "vs_nso": r_nso, "vs_fiinprox": r_fiin, "tier_assessment": tier}


# ───────────────────────── log + cảnh báo ─────────────────────────
def load_log():
    try:
        return json.load(open(LOG_PATH))
    except (OSError, ValueError):
        return {"schema": "te_crosscheck_v1", "history": []}


def save_log(d):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    tmp = LOG_PATH + ".tmp"
    json.dump(d, open(tmp, "w"), indent=1, ensure_ascii=False)
    os.replace(tmp, LOG_PATH)


def _notify(msg):
    if _SELFCHECK or os.environ.get("TE_XCHECK_NO_NOTIFY") == "1":
        print(f"[no-notify] {msg}")
        return True
    try:
        r = subprocess.run([NOTIFY, msg, "trading_daily"], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:  # FileNotFoundError, PermissionError, TimeoutExpired
        print(f"LỖI notify_thread.sh không chạy được: {e!r}"[:300], file=sys.stderr)
        return False
    if r.returncode != 0:
        print(f"LỖI notify_thread.sh rc={r.returncode}: {r.stderr.strip()[:300]}", file=sys.stderr)
    return r.returncode == 0


def format_alert(res):
    L = [f"⚠️ TE cross-check {res['at']}: có LỆCH (chỉ cảnh báo — không tự sửa nguồn nào, không đổi macro gate/DT5G)"]
    p = res.get("policy")
    if p:
        c = p["current"]
        if not c["match"]:
            L.append(f"• Lãi điều hành HIỆN TẠI: TE {c['te']}% (obs {c['te_obs']}) ≠ SBV_REFI_EVENTS {c['ours_event'][1]}% "
                     f"(từ {c['ours_event'][0]}). Kiểm NHNN: `sbv_policy_verify.py` + SBV_REFI_EVENTS.")
        for a in p["alerts"][:6]:
            L.append(f"• Lịch sử {a['month_end']}: TE {a['te']}% vs bảng sự kiện {a['ours']}%")
    k = res.get("cpi")
    if k:
        for a in k["alerts"][:8]:
            L.append(f"• CPI {a['month']} vs {a['vs']}: TE {a['te']} vs {a['ref']} (lệch {a['diff']:+.2f}pp)")
    for br in ("policy", "cpi"):
        if res.get(f"{br}_unavailable"):
            L.append(f"• 🔴 Nhánh {br} KHÔNG kiểm được: {res[f'{br}_unavailable']} (không điền số cũ)")
    L.append(f"Chi tiết: data/te_crosscheck_log.json")
    return "\n".join(L)


def run(dry_run=False):
    now = _now()
    res = {"at": now.astimezone(_ICT).isoformat(timespec="seconds"), "status": "ok"}
    try:
        from sbv_macro_overlay import SBV_REFI_EVENTS
        pol, pf = fetch_te("vn_policy_rate")
        require_fresh("vn_policy_rate", pf)
        res["policy_fetched_at"] = pf.isoformat(timespec="seconds")
        res["policy"] = check_policy(pol, [(t, r) for t, r in SBV_REFI_EVENTS])
    except Unavailable as e:
        res["policy_unavailable"] = str(e)
    try:
        cpi, cf = fetch_te("vn_cpi_yoy")
        require_fresh("vn_cpi_yoy", cf)
        res["cpi_fetched_at"] = cf.isoformat(timespec="seconds")
        from cpi_vn import CPI_ANCHORS, NSO_CPI_YOY_REAL
        res["cpi"] = check_cpi(cpi, NSO_CPI_YOY_REAL, load_fiin(), CPI_ANCHORS)
    except Unavailable as e:
        res["cpi_unavailable"] = str(e)
    n_alert = 0
    if "policy" in res:
        n_alert += len(res["policy"]["alerts"]) + (0 if res["policy"]["current"]["match"] else 1)
    if "cpi" in res:
        n_alert += len(res["cpi"]["alerts"])
    unav = [k for k in ("policy", "cpi") if f"{k}_unavailable" in res]
    if len(unav) == 2:
        res["status"] = "unavailable"
        res["unavailable"] = " | ".join(res[f"{k}_unavailable"] for k in unav)
    elif n_alert:
        res["status"] = "alert"
    elif unav:
        res["status"] = "partial"   # một nhánh không kiểm được, nhánh kia sạch
    res["n_alerts"] = n_alert
    if res["status"] == "unavailable":
        msg = (f"🔴 TE cross-check {res['at']}: KHÔNG kiểm được — {res['unavailable']}. "
               f"Tuần này chưa có đối chiếu TE (không điền số cũ).")
    elif res["status"] == "alert":
        msg = format_alert(res)
    elif res["status"] == "partial":
        k = unav[0]
        msg = (f"🔴 TE cross-check {res['at']}: nhánh {k} KHÔNG kiểm được — {res[f'{k}_unavailable']}. "
               f"Nhánh còn lại sạch. Không điền số cũ.")
    else:
        msg = None
    if dry_run:
        print(json.dumps(res, indent=1, ensure_ascii=False))
        print("[dry-run] không ghi log, không notify;", "sẽ gửi:\n" + msg if msg else "không có gì để gửi")
        return res
    res["notified"] = _notify(msg) if msg else None
    log = load_log()
    log.update({"last": res, "schema": "te_crosscheck_v1"})
    log.setdefault("history", []).append({"at": res["at"], "status": res["status"], "n_alerts": n_alert})
    log["history"] = log["history"][-HISTORY_KEEP:]
    save_log(log)
    print(f"te_macro_crosscheck: status={res['status']} n_alerts={n_alert} notified={res['notified']}")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    res = run(a.dry_run)
    if not a.dry_run and res.get("notified") is False:   # có tin cần gửi mà gửi hỏng ⇒ không im lặng
        print("LỖI: có tin TE cross-check cần gửi nhưng notify thất bại", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
