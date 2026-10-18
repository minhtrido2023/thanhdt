#!/usr/bin/env python3
"""Lõi logic của bin/sunday_plan_round.sh (VÒNG PLAN CHỦ NHẬT mùa BCTC) — tách ra Python để test được.

Subcommand (mọi ngày/giờ neo ICT; MIKE_NOW_ICT = ISO không tz, CHỈ cho selfcheck):
  gate [--check YYYY-MM-DD]            in "RUN <ngày-đích>" hoặc "SKIP: <lý do>"
  stash   --plan-dir D --run-dir R --ntd N --labels "A B"
  decide  --plan-dir D --run-dir R --ntd N --account A --status S [--detail T]
  recover --plan-dir D --state-dir S   khôi phục từ stash mọi manifest đang "running"
  jobs    <freshness.log>              in "ACCT job_id" cho từng lần dispatch DollarBill
Quy ước ghi file: tmp + os.replace (coding_guidelines §5). Không bao giờ xoá plan mà không còn bản stash.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.environ.get("WORKDIR_8L", os.path.dirname(os.path.dirname(HERE)))
if not os.path.isdir(os.path.join(WC_ROOT, "trading_bot")):
    WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC_ROOT)
from trading_bot.vn_market import next_trading_day, now_ict, round_price  # noqa: E402

WINDOW_GATE = os.environ.get("SPR_WINDOW_GATE") or os.path.join(HERE, "fa_ratings_earnings_window_daily.sh")
LIMIT_KEYS = ("limit_price_vnd", "limit_price")
CEIL_KEYS = ("hard_no_chase_ceiling_vnd", "price_ceiling_vnd", "max_price_vnd")


def _today():
    raw = os.environ.get("MIKE_NOW_ICT")
    return (dt.datetime.fromisoformat(raw) if raw else now_ict()).date()


def _md5_file(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _atomic_write(path, data: bytes):
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


def _atomic_copy(src, dst):
    tmp = f"{dst}.tmp.{os.getpid()}"
    shutil.copyfile(src, tmp)
    os.replace(tmp, dst)


def _write_json(path, obj):
    _atomic_write(path, json.dumps(obj, ensure_ascii=False, indent=2).encode())


# ── GATE ────────────────────────────────────────────────────────────────────────────────────────
def gate(check=None):
    today = dt.date.fromisoformat(check) if check else _today()
    reasons = []
    if today.weekday() != 6:
        reasons.append(f"khong phai Chu nhat (weekday={today.weekday()})")
    # TÁI DÙNG nguyên gate cửa sổ mùa BCTC của wrapper re-rate (không viết lại — tránh lệch nghĩa).
    r = subprocess.run([WINDOW_GATE, "--check", today.isoformat()], capture_output=True, text=True)
    wg = (r.stdout or "").strip().splitlines()[-1:] or [""]
    if r.returncode != 0 or not (wg[0] == "RUN" or wg[0].startswith("SKIP")):
        reasons.append(f"gate cua so mua BCTC loi rc={r.returncode}: {wg[0] or r.stderr.strip()[-120:]}")
    elif wg[0] != "RUN":
        reasons.append(wg[0].removeprefix("SKIP: "))
    ntd = next_trading_day(today)
    if reasons:
        return "SKIP: " + "; ".join(reasons)
    return f"RUN {ntd.isoformat()}"


# ── CHUẨN HOÁ LỆNH ──────────────────────────────────────────────────────────────────────────────
def _px(o, keys):
    for k in keys:
        v = o.get(k)
        if v not in (None, "", 0):
            try:
                return int(round_price(float(v), str(o.get("ticker", "")), "HOSE", "nearest"))
            except (TypeError, ValueError):
                return str(v)
    return None


def order_sig(o):
    return (str(o.get("ticker", "")).upper(), str(o.get("side", "")).lower(), int(o.get("qty") or 0),
            str(o.get("order_type") or "").upper(), _px(o, LIMIT_KEYS), _px(o, CEIL_KEYS))


def plan_sigs(plan):
    return sorted(order_sig(o) for o in plan["orders"])


def diff_sigs(old, new):
    o, n = list(old), list(new)
    for s in list(o):
        if s in n:
            o.remove(s)
            n.remove(s)
    return o, n   # (bị bỏ/đổi-từ, thêm/đổi-thành)


def fmt_sig(s):
    t, side, q, ot, lp, cl = s
    return f"{side.upper()} {t} x{q}" + (f" {ot}" if ot else "") + (f" @{lp}" if lp else "") + (f" trần {cl}" if cl else "")


def validate_plan(path, account, ntd):
    """→ (plan|None, lý-do-lỗi|None). Plan hợp lệ = JSON object, plan_date khớp, orders là list các dict có ticker."""
    try:
        with open(path, encoding="utf-8") as f:
            p = json.load(f)
    except FileNotFoundError:
        return None, f"file plan khong ton tai: {path}"
    except (OSError, ValueError) as e:
        return None, f"JSON hong ({type(e).__name__}: {str(e)[:120]})"
    if not isinstance(p, dict):
        return None, f"plan khong phai object ({type(p).__name__})"
    if str(p.get("plan_date")) != ntd:
        return None, f"plan_date trong file={p.get('plan_date')} != {ntd}"
    if p.get("account") not in (None, account):
        return None, f"account trong file={p.get('account')} != {account} (§12)"
    if not isinstance(p.get("orders"), list) or not all(isinstance(o, dict) and o.get("ticker") for o in p["orders"]):
        return None, "orders khong phai list cac lenh co ticker"
    return p, None


# ── STASH / MANIFEST ────────────────────────────────────────────────────────────────────────────
def _plan_path(plan_dir, acct, ntd):
    return os.path.join(plan_dir, f"plan_{acct}_{ntd}.json")


def _manifest_path(run_dir):
    return os.path.join(run_dir, "manifest.json")


def _load_manifest(run_dir):
    with open(_manifest_path(run_dir), encoding="utf-8") as f:
        return json.load(f)


def stash(plan_dir, run_dir, ntd, labels):
    os.makedirs(os.path.join(run_dir, "stash"), exist_ok=True)
    m = {"ntd": ntd, "phase": "running", "plan_dir": plan_dir,
         "started_at": dt.datetime.now(dt.timezone.utc).isoformat(), "accounts": {}}
    for a in labels:
        src = _plan_path(plan_dir, a, ntd)
        if os.path.exists(src):
            dst = os.path.join(run_dir, "stash", f"plan_{a}_{ntd}.json")
            _atomic_copy(src, dst)
            if _md5_file(dst) != _md5_file(src):
                raise SystemExit(f"stash {a}: md5 ban sao != nguon — DUNG")
            m["accounts"][a] = {"had_friday": True, "md5": _md5_file(dst), "stash": dst, "decided": None}
        else:
            m["accounts"][a] = {"had_friday": False, "md5": None, "stash": None, "decided": None}
    _write_json(_manifest_path(run_dir), m)
    return m


def _restore(plan_dir, ntd, acct, ent):
    dst = _plan_path(plan_dir, acct, ntd)
    _atomic_copy(ent["stash"], dst)
    if _md5_file(dst) != ent["md5"]:
        raise SystemExit(f"restore {acct}: md5 sau khoi phuc != stash — KHONG tin duoc")


def recover(plan_dir_default, state_dir):
    """Mọi manifest phase=running (lần trước bị kill) → khôi phục account chưa quyết định rồi đánh dấu recovered."""
    n = 0
    if not os.path.isdir(state_dir):
        return 0
    for d in sorted(os.listdir(state_dir)):
        rd = os.path.join(state_dir, d)
        if not os.path.exists(_manifest_path(rd)):
            continue
        try:
            m = _load_manifest(rd)
        except (OSError, ValueError):
            print(f"RECOVER-WARN {rd}: manifest hong, khong doc duoc")
            continue
        if m.get("phase") != "running":
            continue
        for a, ent in m["accounts"].items():
            if ent.get("decided") is None and ent.get("had_friday"):
                _restore(m.get("plan_dir") or plan_dir_default, m["ntd"], a, ent)
                print(f"RECOVER {a} {m['ntd']}: khoi phuc plan thu Sau tu stash (lan chay truoc bi ngat giua chung)")
                n += 1
        m["phase"] = "recovered"
        _write_json(_manifest_path(rd), m)
    return n


def _mark(run_dir, acct, result):
    m = _load_manifest(run_dir)
    m["accounts"][acct]["decided"] = result
    if all(e["decided"] for e in m["accounts"].values()):
        m["phase"] = "done"
    _write_json(_manifest_path(run_dir), m)


# ── QUYẾT ĐỊNH ──────────────────────────────────────────────────────────────────────────────────
def decide(plan_dir, run_dir, ntd, acct, status, detail=""):
    m = _load_manifest(run_dir)
    ent = m["accounts"][acct]
    path = _plan_path(plan_dir, acct, ntd)
    out = {"account": acct, "ntd": ntd}

    def finish(result, msg, **kw):
        out.update(result=result, message=msg, **kw)
        _mark(run_dir, acct, result)
        print(f"RESULT={result}")
        print(msg)
        return out

    def fail_safe(why):
        if ent["had_friday"]:
            _restore(plan_dir, ntd, acct, ent)
            return finish("c", f"❌ {acct}: KHONG co plan moi dung duoc — {why}. DA KHOI PHUC plan thu Sau "
                               f"(md5 {ent['md5']}, giu nguyen trang thai duyet). CAN NGUOI kiem tra.")
        return finish("c", f"❌ {acct}: KHONG co plan nao cho {ntd} (thu Sau cung khong co) — {why}. CAN NGUOI xu ly.")

    if status != "ok":
        return fail_safe(f"{status}{': ' + detail if detail else ''}")
    new, err = validate_plan(path, acct, ntd)
    if new is None:
        return fail_safe(f"plan moi khong hop le: {err}")
    if ent["had_friday"] and _md5_file(path) == ent["md5"]:
        return fail_safe("DollarBill bao xong nhung file plan khong doi byte nao (khong ghi plan moi)")
    if ent["had_friday"]:
        old, _ = validate_plan(ent["stash"], acct, ntd)
        if old is None:   # bản thứ Sáu không đọc được → không so sánh được, KHÔNG khôi phục thứ không hợp lệ
            return finish("b", f"🟡 {acct}: plan moi hop le nhung ban thu Sau khong doc duoc nen khong so sanh — "
                               "giu plan moi, CAN user duyet lai.", diff=None, stripped=_strip_approval(path, new))
        removed, added = diff_sigs(plan_sigs(old), plan_sigs(new))
        if not removed and not added:
            _restore(plan_dir, ntd, acct, ent)
            return finish("a", f"✅ Chu nhat: plan {acct} khong doi so voi thu Sau (tap lenh giong het) — "
                               "khoi phuc nguyen file thu Sau, giu trang thai duyet.")
        stripped = _strip_approval(path, new)
        lines = [f"🟠 {acct}: plan {ntd} KHAC thu Sau — can user DUYET LAI (da go moi dau hieu duyet)."]
        lines += [f"  − {fmt_sig(s)}" for s in removed] + [f"  + {fmt_sig(s)}" for s in added]
        return finish("b", "\n".join(lines), diff={"removed": [fmt_sig(s) for s in removed],
                                                  "added": [fmt_sig(s) for s in added]}, stripped=stripped)
    stripped = _strip_approval(path, new)
    return finish("b", f"🟠 {acct}: plan {ntd} MOI (thu Sau khong co plan) — can user DUYET.", diff=None, stripped=stripped)


def _strip_approval(path, plan):
    """Plan khác thứ Sáu phải được duyệt lại: gỡ approv*/mafee* (DollarBill có thể sửa-tại-chỗ bản đã ký)."""
    bad = [k for k in plan if k.startswith("approv") or k.startswith("mafee")]
    changed = bad or plan.get("requires_user_approval") is not True
    for k in bad:
        del plan[k]
    plan["requires_user_approval"] = True
    if changed:
        _write_json(path, plan)
    return bad


def jobs_from_log(log):
    acct, res = None, []
    with open(log, encoding="utf-8", errors="replace") as f:
        for ln in f:
            m = re.search(r"\[pipeline-4\] dispatch DollarBill .* cho (\S+) ---", ln)
            if m:
                acct = m.group(1)
            m = re.search(r"DISPATCHED \S+ \(job=([^ )]+)", ln)
            if m and acct:
                res.append((acct, m.group(1)))
    return res


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gate"); g.add_argument("--check")
    for name in ("stash", "decide"):
        s = sub.add_parser(name)
        s.add_argument("--plan-dir", required=True); s.add_argument("--run-dir", required=True)
        s.add_argument("--ntd", required=True)
        if name == "stash":
            s.add_argument("--labels", required=True)
        else:
            s.add_argument("--account", required=True); s.add_argument("--status", required=True)
            s.add_argument("--detail", default="")
    r = sub.add_parser("recover"); r.add_argument("--plan-dir", required=True); r.add_argument("--state-dir", required=True)
    j = sub.add_parser("jobs"); j.add_argument("log")
    a = ap.parse_args()
    if a.cmd == "gate":
        print(gate(a.check))
    elif a.cmd == "stash":
        stash(a.plan_dir, a.run_dir, a.ntd, a.labels.split())
    elif a.cmd == "decide":
        decide(a.plan_dir, a.run_dir, a.ntd, a.account, a.status, a.detail)
    elif a.cmd == "recover":
        recover(a.plan_dir, a.state_dir)
    else:
        for acct, jid in jobs_from_log(a.log):
            print(acct, jid)


if __name__ == "__main__":
    main()
