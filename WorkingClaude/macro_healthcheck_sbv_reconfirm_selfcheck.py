# -*- coding: utf-8 -*-
"""
macro_healthcheck_sbv_reconfirm_selfcheck.py — `sbv_verify_reminder` tôn trọng
`official_reconfirmed_at` (sbv_policy_verify.cmd_finalize, outcome `official_unchanged`).

Chạy macro_healthcheck.py THẬT (cả file, không trích hàm) trong tiến trình con hermetic:
  - WORKDIR bị đổi sang thư mục tạm (đúng 1 dòng gán) ⇒ data/macro_health.json, marker,
    MACRO_HEALTH_ALERT.md đều ghi vào thư mục tạm, KHÔNG chạm data/ thật;
  - đồng hồ ghim bằng cách thay `datetime.datetime.now` (dòng `NOW = ...` của file GIỮ NGUYÊN,
    nên neo ICT §16 vẫn được kiểm dưới `env -u TZ` / TZ lạ);
  - bq / sbv_macro_overlay / macro_state_live / telegram_recommend / trading_bot.vn_market là stub.

Các nhóm ca:
  A. mốc NHNN tự đọc lại còn mới ⇒ KHÔNG nhắc; ranh 14/15 ngày; max(last_verified, reconfirm)
  B. cả hai mốc > 14 ngày ⇒ nhắc, detail nêu cả hai mốc
  C. official_reconfirmed_at tương lai / thiếu múi giờ / rác / tràn số ⇒ nhắc như cũ, KHÔNG SEV1
  D. trần 120 ngày của last_verified (= sbv_policy_verify.MAX_SOURCE_AGE_DAYS)
  E. verified_at / last_verified hỏng ⇒ hành vi cũ (kể cả nhánh legacy)
  G. ranh nửa đêm ICT (16:59Z / 17:00Z)
  F1. cùng log, bỏ field official_reconfirmed_at ⇒ toàn bộ JSON chỉ khác check sbv_verify_reminder
  F2. (tuỳ chọn `--baseline <macro_healthcheck.py bản cũ>`) trước/sau trên cùng đầu vào
  H. hằng số ghim; I. hermetic (không Telegram, data/ thật không đổi)

Usage: python macro_healthcheck_sbv_reconfirm_selfcheck.py [--baseline OLD.py]
       (chạy thêm dưới `env -u TZ` và `TZ=Etc/GMT+12`)
"""
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
SRC = HERE / "macro_healthcheck.py"
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
REMINDER = "sbv_verify_reminder"
EVENT_DATE, EVENT_RATE = "2023-06-19", 4.5     # stub SBV_REFI_EVENTS: > 550 ngày ⇒ nhánh legacy quan sát được

results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and not ok else ""))


# Tiến trình con: argv = <file nguồn đã đổi WORKDIR> <root tạm> <NOW ghim, ISO UTC>
CHILD = r'''
import sys, types, json, datetime as _dtm
from zoneinfo import ZoneInfo
import pandas as pd
src_path, root, now_iso = sys.argv[1:4]
_PIN = _dtm.datetime.fromisoformat(now_iso)
_TODAY = _PIN.astimezone(ZoneInfo("Asia/Ho_Chi_Minh")).date()

class _PinnedDT(_dtm.datetime):
    @classmethod
    def now(cls, tz=None):
        b = _PIN.astimezone(tz) if tz is not None else _PIN.astimezone().replace(tzinfo=None)
        return cls(b.year, b.month, b.day, b.hour, b.minute, b.second, b.microsecond, tzinfo=b.tzinfo)

def _mod(name, **attrs):
    m = types.ModuleType(name); m.__dict__.update(attrs); sys.modules[name] = m; return m

def _bq(sql):
    if "MAX(" in sql:
        return pd.DataFrame({"mx": [pd.Timestamp(_TODAY)]})
    if "MA200" in sql:
        return pd.DataFrame({"Close": [1300.0], "MA200": [1200.0]})
    raise RuntimeError("stub bq: SQL lạ: " + sql)

def _get_macro_state(start, end, bq=None):
    return pd.DataFrame({"time": [pd.Timestamp(_TODAY)], "state": [3], "state_dt4": [3],
                         "cap": [9], "easing": [False]})

def _send(*a, **k):
    open(root + "/telegram_calls.txt", "a").write("call\n")

_mod("simulate_holistic_nav", bq=_bq)
_mod("sbv_macro_overlay", SBV_REFI_EVENTS=[("%(ev_date)s", %(ev_rate)r)])
_mod("macro_state_live", get_macro_state=_get_macro_state)
_mod("telegram_recommend", send_telegram_text=_send)
_mod("trading_bot"); _mod("trading_bot.vn_market", is_holiday=lambda d: False)

code = compile(open(src_path, encoding="utf-8").read(), src_path, "exec")
_dtm.datetime = _PinnedDT
try:
    exec(code, {"__name__": "__main__", "__file__": src_path})
finally:
    leaked = sorted({getattr(m, "__file__", None) or "" for m in list(sys.modules.values())
                     if (getattr(m, "__file__", None) or "").startswith("%(here)s")})
    print("@@META " + json.dumps({"leaked": leaked}))
''' % {"ev_date": EVENT_DATE, "ev_rate": EVENT_RATE, "here": str(HERE)}


def _rewrite_workdir(text, root):
    out, n = re.subn(r'(?m)^WORKDIR = r?"[^"\n]*"$', lambda m: f"WORKDIR = {str(root)!r}", text)
    if n != 1:
        raise RuntimeError(f"cần đúng 1 dòng gán WORKDIR ở top-level, thấy {n}")
    return out


def run(src_text, now_utc, log, base="healthy"):
    """Chạy 1 bản macro_healthcheck (text) trên 1 đầu vào. -> dict(rc, report, raw, stdout, alert, tg, leaked)."""
    today = now_utc.astimezone(ICT).date()
    with tempfile.TemporaryDirectory(prefix="mhc_sbv_") as root:
        data = Path(root, "data"); data.mkdir()
        last_us = today - timedelta(days=1 if base == "healthy" else 12)
        rows = ["time,vix,spx_dd_1y,vix_ma252"] + [
            f"{last_us - timedelta(days=k)},{15 + 0.1 * k:.1f},-0.02,18.0" for k in range(11, -1, -1)]
        (data / "us_market_history.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
        if log is not None:
            (data / "sbv_verify_log.json").write_text(
                log if isinstance(log, str) else json.dumps(log, ensure_ascii=False), encoding="utf-8")
        src = Path(root, "macro_healthcheck_under_test.py")
        src.write_text(_rewrite_workdir(src_text, root), encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k not in ("MACRO_HEALTH_PING", "PYTHONPATH")}
        p = subprocess.run([sys.executable, "-c", CHILD, str(src), root, now_utc.isoformat()],
                           cwd=root, env=env, capture_output=True, timeout=180)
        out = p.stdout.decode("utf-8", "replace")
        meta = [json.loads(l[7:]) for l in out.splitlines() if l.startswith("@@META ")]
        hp = data / "macro_health.json"
        raw = hp.read_text(encoding="utf-8") if hp.exists() else None
        ap = data / "MACRO_HEALTH_ALERT.md"
        return {"rc": p.returncode, "raw": raw, "report": json.loads(raw) if raw else None,
                "stdout": "\n".join(l.replace(root, "<ROOT>") for l in out.splitlines()
                                    if not l.startswith("@@META ")),
                "stderr": p.stderr.decode("utf-8", "replace")[-400:],
                "alert": ap.read_text(encoding="utf-8") if ap.exists() else None,
                "tg": Path(root, "telegram_calls.txt").exists(),
                "leaked": meta[-1]["leaked"] if meta else ["<no META line>"]}


def reminder(r):
    hits = [c for c in (r["report"] or {}).get("checks", []) if c["name"] == REMINDER]
    return hits[0] if len(hits) == 1 else (None if not hits else {"detail": f"<{len(hits)} bản>", "sev": "?", "ok": None})


def without_reminder(r):
    """Toàn bộ report, bỏ riêng check sbv_verify_reminder (mọi field khác giữ nguyên, kể cả thứ tự)."""
    rep = json.loads(r["raw"])
    rep["checks"] = [c for c in rep["checks"] if c["name"] != REMINDER]
    return rep


def strip_lines(text):
    return [l for l in (text or "").splitlines() if REMINDER not in l]


def alert_rest(r):
    """MACRO_HEALTH_ALERT.md bỏ dòng reminder. Tiêu đề "failing checks:" chỉ in khi còn ÍT NHẤT một
    check hỏng ⇒ nếu reminder là check hỏng DUY NHẤT thì tiêu đề đi cùng nó (hệ quả đúng, không phải lệch)."""
    lines = strip_lines(r["alert"])
    if not [c for c in without_reminder(r)["checks"] if not c["ok"]]:
        lines = [l for l in lines if l != "failing checks:"]
    return lines


def same_detail_rule(old_c, new_c, appended):
    """Cả hai bản cùng nhắc: name/ok/sev y nguyên; detail y nguyên, hoặc (khi mốc NHNN có giá trị và
    đi nhánh verify log) = detail cũ + '; ' + phần nối."""
    if (old_c["name"], old_c["ok"], old_c["sev"]) != (new_c["name"], new_c["ok"], new_c["sev"]):
        return False
    if appended:
        return new_c["detail"].startswith(old_c["detail"] + "; ")
    return new_c["detail"] == old_c["detail"]


def _const(path, name):
    for node in ast.parse(Path(path).read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError(f"{Path(path).name} không còn gán {name} ở top-level")


# ───────────────────────── đầu vào ─────────────────────────
NOW0 = datetime(2026, 10, 29, 3, 0, 0, tzinfo=timezone.utc)      # 10:00 ICT 2026-10-29
T0 = NOW0.astimezone(ICT).date()
D = lambda n, today=T0: (today - timedelta(days=n)).isoformat()   # noqa: E731
TS = lambda n: f"{D(n)}T08:09:47+07:00"                           # noqa: E731


def L(last=20, reconf=None, **over):
    """Log v2 hợp lệ: last_verified cách `last` ngày, official_reconfirmed_at cách `reconf` ngày."""
    d = {"schema": "sbv_policy_verify_v2", "verified_at": f"{D(last)}T18:05:12+07:00",
         "attempted_at": TS(3), "last_verified": D(last),
         "verified": {"refi_pct": 4.5, "rediscount_pct": 3.0}}
    if reconf is not None:
        d["official_reconfirmed_at"] = TS(reconf)
    d.update(over)
    return {k: v for k, v in d.items() if v is not Ellipsis}


LEGACY_DETAIL = lambda n: (f"last SBV verify {n}d ago (> 14d) — sbv_policy_verify.py (Mon 08:05) "  # noqa: E731
                           f"not verified since; current rate {EVENT_RATE}% (event: {EVENT_DATE})")
NOW_ICT = NOW0.astimezone(ICT)
G_LOG = lambda reconf: {"schema": "sbv_policy_verify_v2", "verified_at": "2026-10-01T18:05:12+07:00",  # noqa: E731
                        "last_verified": "2026-10-01", "verified": {"refi_pct": 4.5},
                        "official_reconfirmed_at": reconf}
Z1659 = datetime(2026, 10, 27, 16, 59, 0, tzinfo=timezone.utc)   # 23:59 ICT 10-27
Z1700 = datetime(2026, 10, 27, 17, 0, 0, tzinfo=timezone.utc)    # 00:00 ICT 10-28

# (tên, now, log, base, kỳ vọng, [chuỗi phải có trong detail], detail chính xác | None)
#   kỳ vọng: "none" = không có check · "remind" = INFO nhắc theo verify log · "legacy" = nhánh không có verify log
CASES = [
    ("A1 last 20d + NHNN đọc lại 3d ⇒ không nhắc", NOW0, L(20, 3), "healthy", "none", [], None),
    ("A2 ranh: NHNN đọc lại đúng 14d ⇒ không nhắc", NOW0, L(20, 14), "healthy", "none", [], None),
    ("A3 ranh: NHNN đọc lại 15d ⇒ nhắc", NOW0, L(20, 15), "healthy", "remind",
     [f"kiểm thật cuối {D(20)}", f"NHNN tự đọc lại {D(15)} (15d ago)"], None),
    ("A4 max: last 2d + NHNN đọc lại 30d (cũ hơn) ⇒ không nhắc", NOW0, L(2, 30), "healthy", "none", [], None),
    ("A5 không có mốc NHNN, last đúng 14d ⇒ không nhắc", NOW0, L(14), "healthy", "none", [], None),
    ("A6 không có mốc NHNN, last 15d ⇒ nhắc, detail Y NGUYÊN bản cũ", NOW0, L(15), "healthy", "remind",
     [], LEGACY_DETAIL(15)),
    ("A7 official_reconfirmed_at=null ⇒ coi như không có, detail Y NGUYÊN bản cũ", NOW0,
     L(20, official_reconfirmed_at=None), "healthy", "remind", [], LEGACY_DETAIL(20)),
    ("A8 mốc NHNN cách 1 giây trước NOW ⇒ dùng được, không nhắc", NOW0,
     L(20, official_reconfirmed_at=(NOW_ICT - timedelta(seconds=1)).isoformat()), "healthy", "none", [], None),
    ("B1 last 40d + NHNN đọc lại 20d ⇒ nhắc, nêu cả hai mốc", NOW0, L(40, 20), "healthy", "remind",
     [LEGACY_DETAIL(40), f"kiểm thật cuối {D(40)}", f"NHNN tự đọc lại {D(20)} (20d ago)"], None),
    ("C1 mốc NHNN ở tương lai (+1 ngày) ⇒ nhắc như cũ", NOW0, L(20, -1), "healthy", "remind",
     [LEGACY_DETAIL(20), "bỏ qua: ở tương lai"], None),
    ("C2 mốc NHNN tương lai 1 giây ⇒ nhắc như cũ", NOW0,
     L(20, official_reconfirmed_at=(NOW_ICT + timedelta(seconds=1)).isoformat()), "healthy", "remind",
     [LEGACY_DETAIL(20), "bỏ qua: ở tương lai"], None),
    ("C3 mốc NHNN thiếu múi giờ ⇒ nhắc như cũ", NOW0, L(20, official_reconfirmed_at=f"{D(3)}T08:09:47"),
     "healthy", "remind", [LEGACY_DETAIL(20), "bỏ qua: thiếu múi giờ"], None),
    ("C4 mốc NHNN chỉ có ngày (không giờ, không múi giờ) ⇒ nhắc như cũ", NOW0,
     L(20, official_reconfirmed_at=D(3)), "healthy", "remind", [LEGACY_DETAIL(20), "bỏ qua: thiếu múi giờ"], None),
    ("C5 mốc NHNN là rác ⇒ nhắc như cũ", NOW0, L(20, official_reconfirmed_at="rác"), "healthy", "remind",
     [LEGACY_DETAIL(20), "bỏ qua: không parse được (ValueError"], None),
    ("C6 mốc NHNN chuỗi rỗng ⇒ nhắc như cũ", NOW0, L(20, official_reconfirmed_at=""), "healthy", "remind",
     [LEGACY_DETAIL(20), "bỏ qua: không parse được"], None),
    ("C7 mốc NHNN là số ⇒ nhắc như cũ", NOW0, L(20, official_reconfirmed_at=20261026), "healthy", "remind",
     [LEGACY_DETAIL(20), "bỏ qua: không parse được (TypeError"], None),
    ("C8 mốc NHNN là object ⇒ nhắc như cũ", NOW0, L(20, official_reconfirmed_at={"at": TS(3)}), "healthy",
     "remind", [LEGACY_DETAIL(20), "bỏ qua: không parse được (TypeError"], None),
    ("C9 mốc NHNN tràn số khi đổi múi giờ (0001-01-01+14:00) ⇒ nhắc như cũ, KHÔNG SEV1", NOW0,
     L(20, official_reconfirmed_at="0001-01-01T00:00:00+14:00"), "healthy", "remind",
     [LEGACY_DETAIL(20), "bỏ qua: OverflowError"], None),
    ("C10 mốc NHNN tràn số (9999-12-31-12:00) ⇒ nhắc như cũ, KHÔNG SEV1", NOW0,
     L(20, official_reconfirmed_at="9999-12-31T23:59:59-12:00"), "healthy", "remind",
     [LEGACY_DETAIL(20), "bỏ qua: OverflowError"], None),
    ("D1 trần: last 121d + NHNN đọc lại 3d ⇒ vẫn nhắc", NOW0, L(121, 3), "healthy", "remind",
     [LEGACY_DETAIL(121), f"bỏ qua: kiểm thật cuối {D(121)} đã 121d (> 120d)"], None),
    ("D2 trần: last đúng 120d + NHNN đọc lại 3d ⇒ không nhắc", NOW0, L(120, 3), "healthy", "none", [], None),
    ("E1 thiếu verified_at + NHNN đọc lại 3d ⇒ nhắc như cũ", NOW0, L(20, 3, verified_at=Ellipsis), "healthy",
     "remind", [LEGACY_DETAIL(20), "bỏ qua: verified_at=None không hợp lệ"], None),
    ("E2 verified_at=null ⇒ nhắc như cũ", NOW0, L(20, 3, verified_at=None), "healthy", "remind",
     [LEGACY_DETAIL(20), "bỏ qua: verified_at=None không hợp lệ"], None),
    ("E3 verified_at rác ⇒ nhắc như cũ", NOW0, L(20, 3, verified_at="rác"), "healthy", "remind",
     [LEGACY_DETAIL(20), "bỏ qua: verified_at='rác' không hợp lệ"], None),
    ("E4 verified_at thiếu múi giờ ⇒ nhắc như cũ", NOW0, L(20, 3, verified_at=f"{D(20)}T18:05:12"), "healthy",
     "remind", [LEGACY_DETAIL(20), "thiếu múi giờ"], None),
    ("E5 thiếu last_verified + NHNN đọc lại 3d ⇒ nhánh legacy như cũ", NOW0, L(20, 3, last_verified=Ellipsis),
     "healthy", "legacy", [], None),
    ("E6 last_verified rác + NHNN đọc lại 3d ⇒ nhánh legacy như cũ", NOW0, L(20, 3, last_verified="rác"),
     "healthy", "legacy", [], None),
    ("E7 không có file verify log ⇒ nhánh legacy như cũ", NOW0, None, "healthy", "legacy", [], None),
    ("E8 verify log là JSON list ⇒ nhánh legacy như cũ", NOW0, json.dumps([L(20, 3)]), "healthy", "legacy", [], None),
    ("E9 verify log không phải JSON ⇒ nhánh legacy như cũ", NOW0, "{rác", "healthy", "legacy", [], None),
    ("G1 16:59Z (23:59 ICT 10-27): mốc 10-12T17:30Z = 10-13 ICT, 14d ⇒ không nhắc", Z1659,
     G_LOG("2026-10-12T17:30:00+00:00"), "healthy", "none", [], None),
    ("G2 17:00Z (00:00 ICT 10-28): cùng mốc, 15d ⇒ nhắc", Z1700, G_LOG("2026-10-12T17:30:00+00:00"),
     "healthy", "remind", ["NHNN tự đọc lại 2026-10-13 (15d ago)", "last SBV verify 27d ago"], None),
    ("G3 16:59Z: cùng thời điểm viết +07:00 ⇒ không nhắc", Z1659, G_LOG("2026-10-13T00:30:00+07:00"),
     "healthy", "none", [], None),
    ("G4 17:00Z: cùng thời điểm viết +07:00 ⇒ nhắc", Z1700, G_LOG("2026-10-13T00:30:00+07:00"),
     "healthy", "remind", ["NHNN tự đọc lại 2026-10-13 (15d ago)"], None),
    ("G5 16:59Z: mốc 17:00:30Z cùng ngày (tương lai 90 giây, viết múi giờ khác) ⇒ nhắc như cũ", Z1659,
     G_LOG("2026-10-27T17:00:30+00:00"), "healthy", "remind", ["bỏ qua: ở tương lai", "last SBV verify 26d ago"], None),
    ("G6 17:00Z: mốc 16:59:30Z (30 giây trước, ICT đã sang 10-28?) ⇒ không nhắc", Z1700,
     G_LOG("2026-10-27T16:59:30+00:00"), "healthy", "none", [], None),
    ("X1 nền DEGRADED (US feed cũ) + NHNN đọc lại 3d ⇒ không nhắc", NOW0, L(20, 3), "degraded", "none", [], None),
    ("X2 nền DEGRADED + cả hai mốc cũ ⇒ nhắc", NOW0, L(40, 20), "degraded", "remind",
     [f"NHNN tự đọc lại {D(20)}"], None),
]
BASE_EXPECT = {"healthy": ("HEALTHY", "OK", "DT5G_macro", 0), "degraded": ("DEGRADED", "SEV2", "DT4_only", 1)}


def _drop_reconf(log):
    return {k: v for k, v in log.items() if k != "official_reconfirmed_at"}


def main():
    baseline = None
    if "--baseline" in sys.argv:
        baseline = Path(sys.argv[sys.argv.index("--baseline") + 1]).read_text(encoding="utf-8")
    new_text = SRC.read_text(encoding="utf-8")
    print(f"macro_healthcheck đang kiểm: {SRC}  sha256={hashlib.sha256(new_text.encode()).hexdigest()[:12]}")
    print(f"TZ env = {os.environ.get('TZ', '<unset>')}  ·  --baseline = {'có' if baseline else 'không'}")

    real = HERE / "data" / "macro_health.json"
    real_before = (real.stat().st_mtime_ns, real.stat().st_size) if real.exists() else None

    jobs = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        for name, now, log, base, *_ in CASES:
            jobs[("new", name)] = ex.submit(run, new_text, now, log, base)
            if isinstance(log, dict) and "official_reconfirmed_at" in log:
                jobs[("nofield", name)] = ex.submit(run, new_text, now, _drop_reconf(log), base)
            if baseline:
                jobs[("old", name)] = ex.submit(run, baseline, now, log, base)
    R = {k: f.result() for k, f in jobs.items()}

    print("\nA–G. hành vi trên macro_healthcheck.py thật")
    for name, now, log, base, want, contains, exact in CASES:
        r = R[("new", name)]
        st, sev, rec, rc = BASE_EXPECT[base]
        rep = r["report"] or {}
        c = reminder(r)
        names = [x["name"] for x in rep.get("checks", [])]
        src_sbv = [s for s in rep.get("sources", []) if s["name"] == "sbv_refi_events"]
        frame_ok = (r["rc"] == rc and rep.get("status") == st and rep.get("sev") == sev
                    and rep.get("recommended_state_source") == rec and "sbv_import" not in names
                    and len(src_sbv) == 1 and src_sbv[0]["ok"] is True)
        check(f"{name} · khung: rc={rc} status={st} sev={sev} source={rec}, không sbv_import", frame_ok,
              f"rc={r['rc']} status={rep.get('status')} sev={rep.get('sev')} checks={names} stderr={r['stderr']!r}")
        if want == "none":
            check(f"{name} · không có check {REMINDER}", c is None, f"có: {c}")
        else:
            head = "last SBV refi event" if want == "legacy" else "last SBV verify"
            ok = (c is not None and c["ok"] is False and c["sev"] == "INFO" and c["detail"].startswith(head)
                  and all(s in c["detail"] for s in contains) and (exact is None or c["detail"] == exact))
            check(f"{name} · {REMINDER} ok=False sev=INFO, detail đúng", ok, f"{c}")

    print("\nF1. cùng log, bỏ official_reconfirmed_at ⇒ report chỉ khác check sbv_verify_reminder")
    for name, now, log, base, want, *_ in CASES:
        if ("nofield", name) not in R:
            continue
        a, b = R[("nofield", name)], R[("new", name)]
        same = (a["rc"] == b["rc"] and without_reminder(a) == without_reminder(b)
                and strip_lines(a["stdout"]) == strip_lines(b["stdout"])
                and alert_rest(a) == alert_rest(b))
        check(f"F1 {name.split()[0]} report/rc/stdout/alert giống hệt ngoài {REMINDER}", same,
              f"rc {a['rc']}/{b['rc']}")
        ca, cb = reminder(a), reminder(b)
        appended = log.get("official_reconfirmed_at") is not None and want == "remind"
        if ca and cb:
            check(f"F1 {name.split()[0]} cả hai cùng nhắc ⇒ ok/sev y nguyên, detail "
                  f"{'= detail cũ + phần nối' if appended else 'y nguyên'}",
                  same_detail_rule(ca, cb, appended), f"{ca} vs {cb}")
        else:
            check(f"F1 {name.split()[0]} mốc NHNN chỉ có thể GỠ nhắc, không bao giờ THÊM nhắc",
                  not (ca is None and cb is not None), f"{ca} vs {cb}")

    if baseline:
        print("\nF2. TRƯỚC (--baseline) vs SAU trên cùng đầu vào")
        n_ident = n_detail = n_gone = 0
        for name, now, log, base, want, *_ in CASES:
            a, b = R[("old", name)], R[("new", name)]
            tag = name.split()[0]
            has_field = isinstance(log, dict) and log.get("official_reconfirmed_at") is not None
            if not has_field:
                n_ident += 1
                check(f"F2 {tag} không có mốc NHNN ⇒ macro_health.json GIỐNG TỪNG BYTE, rc + stdout + alert y nguyên",
                      a["raw"] is not None and a["raw"] == b["raw"] and a["rc"] == b["rc"]
                      and a["stdout"] == b["stdout"] and a["alert"] == b["alert"], f"rc {a['rc']}/{b['rc']}")
                continue
            ca, cb = reminder(a), reminder(b)
            rest = (a["rc"] == b["rc"] and without_reminder(a) == without_reminder(b)
                    and strip_lines(a["stdout"]) == strip_lines(b["stdout"])
                    and alert_rest(a) == alert_rest(b))
            check(f"F2 {tag} mọi thứ ngoài {REMINDER} y nguyên (status/sev/sources/checks khác/rc/stdout/alert)",
                  rest, f"rc {a['rc']}/{b['rc']}")
            if ca is None and cb is None:
                n_ident += 1
                check(f"F2 {tag} trước và sau đều không nhắc ⇒ macro_health.json GIỐNG TỪNG BYTE",
                      a["raw"] == b["raw"] and want == "none")
            elif cb is None:
                n_gone += 1
                check(f"F2 {tag} trước có nhắc, sau không (đúng mục đích)", want == "none", f"{ca} vs {cb}")
            elif ca is None:
                check(f"F2 {tag} KHÔNG được có chiều ngược lại (trước không nhắc, sau nhắc)", False, f"{cb}")
            elif want == "legacy":
                n_ident += 1
                check(f"F2 {tag} nhánh legacy: macro_health.json GIỐNG TỪNG BYTE", a["raw"] == b["raw"])
            else:
                n_detail += 1
                check(f"F2 {tag} vẫn nhắc: name/ok/sev y nguyên, detail = detail cũ + phần nối",
                      same_detail_rule(ca, cb, True), f"{ca} vs {cb}")
        print(f"  (F2: {n_ident} ca JSON giống từng byte · {n_detail} ca chỉ khác detail của {REMINDER} · "
              f"{n_gone} ca hết nhắc)")

    print("\nH. hằng số ghim")
    check("H1 SBV_VERIFY_MAX_DAYS vẫn 14", _const(SRC, "SBV_VERIFY_MAX_DAYS") == 14)
    spv = HERE / "sbv_policy_verify.py"
    check("H2 SBV_RECONFIRM_MAX_DAYS == sbv_policy_verify.MAX_SOURCE_AGE_DAYS",
          _const(SRC, "SBV_RECONFIRM_MAX_DAYS") == _const(spv, "MAX_SOURCE_AGE_DAYS"),
          f"{_const(SRC, 'SBV_RECONFIRM_MAX_DAYS')} vs {_const(spv, 'MAX_SOURCE_AGE_DAYS')}")
    check("H3 macro_healthcheck.py không import sbv_policy_verify",
          not re.search(r"(?m)^\s*(from|import)\s+sbv_policy_verify\b", new_text))

    print("\nI. hermetic")
    check("I1 không lượt nào gọi Telegram", not any(r["tg"] for r in R.values()))
    leaked = sorted({f for r in R.values() for f in r["leaked"]})
    check("I2 tiến trình con không nạp module nào từ thư mục code thật (toàn stub)", not leaked, f"{leaked}")
    real_after = (real.stat().st_mtime_ns, real.stat().st_size) if real.exists() else None
    check(f"I3 {real} không bị đụng tới", real_before == real_after, f"{real_before} -> {real_after}")
    check("I4 mọi lượt đều ghi được macro_health.json (trong thư mục tạm)",
          all(r["raw"] for r in R.values()), f"{[k for k, r in R.items() if not r['raw']]}")

    n, ok = len(results), sum(results)
    print(f"\n===== macro_healthcheck_sbv_reconfirm_selfcheck: {ok}/{n} PASS =====")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
