#!/usr/bin/env python3
"""Lõi logic của bin/sunday_plan_round.sh (VÒNG PLAN CHỦ NHẬT mùa BCTC) — tách ra Python để test được.

Subcommand (mọi ngày/giờ neo ICT; MIKE_NOW_ICT = ISO không tz, CHỈ cho selfcheck):
  gate [--check YYYY-MM-DD]            in "RUN <ngày-đích>" hoặc "SKIP: <lý do>"
  stash   --plan-dir D --run-dir R --ntd N --labels "A B"     idempotent: manifest cùng ntd => giữ stash GỐC
  decide  --plan-dir D --run-dir R --ntd N --account A --status S [--detail T]
  recover --plan-dir D --state-dir S [--account A]   khôi phục mọi manifest "running" CÓ ntd >= hôm nay
  verify  --plan-dir D --state-dir S   kiểm cuối đêm: nội dung plan == nội dung đã quyết; lệch => gỡ dấu duyệt, rc=4
  settle  --jobs-dir J --pend-dir P --removed-dir R --since E [--scan] --job ACCT=ID ...   xác minh job đã dừng
  jobs    <freshness.log>              in "ACCT job_id" cho từng lần dispatch DollarBill
  summary --run-dir R                  in "A=a B=b" (kết quả quyết định từng account)
  busjson --kv k=v ...                 in 1 object JSON (json.dumps, không ghép chuỗi)
  prune   --state-dir S --keep N       xoá thư mục ngày cũ (chỉ phase done/recovered/stale_skipped), giữ N
Quy ước ghi file: tmp + os.replace (coding_guidelines §5). Không bao giờ xoá plan mà không còn bản stash.
"""
import argparse
import contextlib
import datetime as dt
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.environ.get("WORKDIR_8L", os.path.dirname(os.path.dirname(HERE)))
if not os.path.isdir(os.path.join(WC_ROOT, "trading_bot")):
    WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC_ROOT)
from trading_bot.vn_market import next_trading_day, now_ict, round_price  # noqa: E402

WINDOW_GATE = os.environ.get("SPR_WINDOW_GATE") or os.path.join(HERE, "fa_ratings_earnings_window_daily.sh")
# Trạng thái job còn "sống" (đồng bộ mike_json.LIVE_STATUSES) — CHỈ ngoài tập này mới là kết thúc.
LIVE_STATUSES = ("running", "retrying", "usage_limited", "provider_fallback", "maxturns_pending")
PENDING_RESUME_STATES = ("usage_limited", "maxturns_pending")


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


# ── DẤU DUYỆT ───────────────────────────────────────────────────────────────────────────────────
def _is_approval_key(k):
    return k.startswith("approv") or k.startswith("mafee")


def approval_desc(path):
    """Trạng thái duyệt ĐỌC THẬT từ file (§29) — không bao giờ viết 'giữ trạng thái duyệt' mà chưa đọc."""
    try:
        with open(path, encoding="utf-8") as f:
            p = json.load(f)
        if not isinstance(p, dict):
            return "khong doc duoc trang thai duyet (file khong phai object)"
    except (OSError, ValueError) as e:
        return f"khong doc duoc trang thai duyet ({type(e).__name__})"
    ab = p.get("approved_by") or p.get("approved_by_user")
    ks = sorted(k for k in p if _is_approval_key(k))
    return (f"approved_by={ab!r}" if ab else "KHONG co approved_by") + \
        f", requires_user_approval={p.get('requires_user_approval')!r}, truong duyet trong file={ks}"


def _strip_approval(path, plan):
    """Plan khác thứ Sáu / không đáng tin phải được duyệt lại: gỡ approv*/mafee*, requires_user_approval=true."""
    bad = [k for k in plan if _is_approval_key(k)]
    changed = bad or plan.get("requires_user_approval") is not True
    for k in bad:
        del plan[k]
    plan["requires_user_approval"] = True
    if changed:
        _write_json(path, plan)
    return bad


def _content_md5(plan):
    """md5 của NỘI DUNG plan, bỏ dấu duyệt: người duyệt hợp lệ chỉ sửa các trường này; người ghi muộn đổi nội dung."""
    c = {k: v for k, v in plan.items() if not _is_approval_key(k) and k != "requires_user_approval"}
    return hashlib.md5(json.dumps(c, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _content_md5_file(path):
    """→ md5 nội dung | None nếu file vắng | 'CORRUPT' nếu không đọc được."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            p = json.load(f)
        return _content_md5(p) if isinstance(p, dict) else "CORRUPT"
    except (OSError, ValueError):
        return "CORRUPT"


# ── CHUẨN HOÁ LỆNH THEO PHẦN EXECUTOR DÙNG ──────────────────────────────────────────────────────
def _tick(v, ticker):
    if v in (None, "", 0):
        return None
    return int(round_price(float(v), str(ticker), "HOSE", "nearest"))


def executor_view(path, account, ntd):
    """Đưa plan qua ĐÚNG đường nạp của executor (load_plan → PlannedOrder, gồm resolve_buy_ceiling)
    rồi rút ra những gì executor thực sự dùng. order_type/limit_price_vnd KHÔNG nằm trong PlannedOrder
    (load_plan lọc bỏ) nên không phải tiêu chí. Raise nếu load_plan không nạp được."""
    import trading_bot.plan as P
    with tempfile.TemporaryDirectory(prefix="spr_view.") as td:
        shutil.copyfile(path, os.path.join(td, f"plan_{account}_{ntd}.json"))
        old = P.PLAN_DIR
        P.PLAN_DIR = td
        try:
            with contextlib.redirect_stdout(io.StringIO()):   # load_plan in cảnh báo ra stdout; RESULT= parse không được lẫn
                plan = P.load_plan(ntd, account)
        finally:
            P.PLAN_DIR = old
    if plan is None:
        raise ValueError("load_plan tra None")
    orders = []
    for o in plan.orders:
        tk = str(o.ticker).upper()
        orders.append((tk, str(o.side).lower(), int(o.qty), _tick(o.ref_price, tk), str(o.urgency), str(o.book),
                       bool(o.cash_only), _tick(o.hard_no_chase_ceiling_vnd, tk), int(o.priority),
                       o.lever_f, o.loan_package_id))
    head = {"state": plan.state, "state_name": plan.state_name, "strategy": plan.strategy,
            "strategy_version": plan.strategy_version, "signal_date": plan.signal_date}
    return head, sorted(orders, key=repr)


ORDER_FIELDS = ("ticker", "side", "qty", "ref_price", "urgency", "book", "cash_only", "tran_gia", "priority",
                "lever_f", "loan_package_id")


def diff_sigs(old, new):
    o, n = list(old), list(new)
    for s in list(o):
        if s in n:
            o.remove(s)
            n.remove(s)
    return o, n   # (bị bỏ/đổi-từ, thêm/đổi-thành)


def fmt_sig(s):
    t, side, q, ref, urg, book, cash_only, ceil, prio = s[:9]
    return (f"{side.upper()} {t} x{q}" + (f" ref~{ref}" if ref else "") + (f" trần {ceil}" if ceil else "")
            + f" [{book or '-'}/{urg}/prio{prio}" + ("/cash_only" if cash_only else "") + "]")


def validate_plan(path, account, ntd):
    """→ (plan|None, lý-do-lỗi|None). Plan hợp lệ = JSON object, plan_date khớp, orders là list các dict có ticker
    và qty là int dương."""
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
    for o in p["orders"]:
        q = o.get("qty")
        if isinstance(q, bool) or not isinstance(q, int) or q <= 0:
            return None, f"lenh {o.get('id') or o.get('ticker')}: qty={q!r} khong phai so nguyen duong"
    return p, None


# ── STASH / MANIFEST ────────────────────────────────────────────────────────────────────────────
def _plan_path(plan_dir, acct, ntd):
    return os.path.join(plan_dir, f"plan_{acct}_{ntd}.json")


def _manifest_path(run_dir):
    return os.path.join(run_dir, "manifest.json")


def _load_manifest(run_dir):
    with open(_manifest_path(run_dir), encoding="utf-8") as f:
        return json.load(f)


def _stash_ok(ent):
    return bool(ent.get("stash")) and os.path.exists(ent["stash"]) and _md5_file(ent["stash"]) == ent["md5"]


def stash(plan_dir, run_dir, ntd, labels):
    """Idempotent: nếu run_dir đã có manifest CÙNG ntd (lần chạy trước bị ngắt / chạy lại tay) thì KẾ THỪA stash gốc —
    tuyệt đối không chụp lại từ đĩa, vì đĩa lúc này có thể đang là plan do job muộn ghi (mất bản thứ Sáu thật)."""
    os.makedirs(os.path.join(run_dir, "stash"), exist_ok=True)
    prev = None
    if os.path.exists(_manifest_path(run_dir)):
        try:
            prev = _load_manifest(run_dir)
        except (OSError, ValueError):
            raise SystemExit("stash: manifest cu ton tai nhung khong doc duoc — DUNG, khong chup de len ban thu Sau goc")
        if prev.get("ntd") != ntd:
            prev = None
    if prev is not None:   # kiểm stash gốc TRƯỚC khi đụng manifest cũ: hỏng thì DỪNG, manifest cũ còn nguyên để người xem
        for a in labels:
            pe = prev.get("accounts", {}).get(a)
            if pe is not None and pe.get("had_friday") and not _stash_ok(pe):
                raise SystemExit(f"stash {a}: stash goc cua lan truoc mat/hong (md5 lech) — DUNG, khong tu doan ban thu Sau")
        os.replace(_manifest_path(run_dir), os.path.join(run_dir, f"manifest.prev.{int(time.time())}.json"))
    m = {"ntd": ntd, "phase": "running", "plan_dir": plan_dir,
         "started_at": dt.datetime.now(dt.timezone.utc).isoformat(), "accounts": {}}
    for a in labels:
        pe = (prev or {}).get("accounts", {}).get(a)
        if pe is not None:
            m["accounts"][a] = {"had_friday": bool(pe.get("had_friday")), "md5": pe.get("md5"), "stash": pe.get("stash"),
                                "decided": None}
            print(f"STASH-REUSE {a}: giu stash GOC cua lan chay truoc (had_friday={pe.get('had_friday')}, md5={pe.get('md5')})")
            continue
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


def _restore(plan_dir, ntd, acct, ent, run_dir=None):
    """Chép stash về đúng tên. Nếu đĩa đang có file KHÁC (plan muộn/mới) thì cất bản đó vào run_dir/superseded trước."""
    if not _stash_ok(ent):
        raise SystemExit(f"restore {acct}: stash mat/md5 lech manifest — KHONG khoi phuc duoc, can nguoi xu ly ({ent.get('stash')})")
    dst = _plan_path(plan_dir, acct, ntd)
    if run_dir and os.path.exists(dst) and _md5_file(dst) != ent["md5"]:
        os.makedirs(os.path.join(run_dir, "superseded"), exist_ok=True)
        shutil.copyfile(dst, os.path.join(run_dir, "superseded", f"plan_{acct}_{ntd}.{int(time.time())}.json"))
    _atomic_copy(ent["stash"], dst)
    if _md5_file(dst) != ent["md5"]:
        raise SystemExit(f"restore {acct}: md5 sau khoi phuc != stash — KHONG tin duoc")


def _finalize(run_dir, plan_dir, ntd, acct, result):
    """Ghi kết quả quyết định + dấu vân tay NỘI DUNG plan trên đĩa NGAY lúc quyết định (cho `verify` cuối đêm)."""
    m = _load_manifest(run_dir)
    ent = m["accounts"][acct]
    path = _plan_path(plan_dir, acct, ntd)
    ent["decided"] = result
    ent["final_exists"] = os.path.exists(path)
    ent["final_md5"] = _md5_file(path) if ent["final_exists"] else None
    ent["final_content_md5"] = _content_md5_file(path)
    if all(e["decided"] for e in m["accounts"].values()):
        m["phase"] = "done"
    _write_json(_manifest_path(run_dir), m)


def recover(plan_dir_default, state_dir, account=None):
    """Mọi manifest phase=running CÓ ntd >= hôm nay → khôi phục account chưa quyết định. Manifest của tuần cũ
    (ntd < hôm nay) bị BỎ QUA (đánh dấu stale_skipped) — chép stash tuần trước đè plan đã thực thi là sự cố, không phải khôi phục.
    Trả (số account đã khôi phục, số lỗi)."""
    n = bad = 0
    if not os.path.isdir(state_dir):
        return 0, 0
    today = _today().isoformat()
    for d in sorted(os.listdir(state_dir)):
        rd = os.path.join(state_dir, d)
        if not os.path.exists(_manifest_path(rd)):
            continue
        try:
            m = _load_manifest(rd)
        except (OSError, ValueError):
            print(f"RECOVER-WARN {rd}: manifest hong, khong doc duoc")
            bad += 1
            continue
        if m.get("phase") != "running":
            continue
        if str(m.get("ntd")) < today:
            print(f"RECOVER-SKIP {d}: manifest tuan cu (ntd={m.get('ntd')} < hom nay {today}) — khong dong vao plan; danh dau stale_skipped")
            m["phase"] = "stale_skipped"
            _write_json(_manifest_path(rd), m)
            continue
        pdir = m.get("plan_dir") or plan_dir_default
        for a, ent in m["accounts"].items():
            if account and a != account:
                continue
            if ent.get("decided") is not None:
                continue
            try:
                if ent.get("had_friday"):
                    _restore(pdir, m["ntd"], a, ent, rd)
                    _finalize(rd, pdir, m["ntd"], a, "recovered")
                    print(f"RECOVER {a} {m['ntd']}: da khoi phuc plan thu Sau tu stash (md5 {ent['md5']}); "
                          f"{approval_desc(_plan_path(pdir, a, m['ntd']))}")
                    n += 1
                else:
                    p = _plan_path(pdir, a, m["ntd"])
                    plan, _err = validate_plan(p, a, m["ntd"]) if os.path.exists(p) else (None, None)
                    if plan is not None:
                        bad_keys = _strip_approval(p, plan)
                        print(f"RECOVER-NOFRIDAY {a} {m['ntd']}: thu Sau khong co plan; plan hien co do vong CN ghi da GO dau duyet {bad_keys} — can user xem")
                    _finalize(rd, pdir, m["ntd"], a, "recovered")
            except SystemExit as e:
                print(f"RECOVER-FAIL {a} {m['ntd']}: {e}")
                bad += 1
        m = _load_manifest(rd)
        if all(e["decided"] for e in m["accounts"].values()):
            m["phase"] = "recovered"
            _write_json(_manifest_path(rd), m)
    return n, bad


# ── KIỂM CUỐI ĐÊM ──────────────────────────────────────────────────────────────────────────────
def verify(plan_dir_default, state_dir):
    """Với mọi manifest ntd >= hôm nay: nội dung plan trên đĩa phải == nội dung đã quyết. Lệch => gỡ dấu duyệt + rc=4.
    Manifest còn 'running' (vòng bị ngắt) được recover trước. Dấu duyệt do USER thêm sau quyết định KHÔNG phải lệch
    (so md5 nội dung đã bỏ trường duyệt); thay đổi nội dung thì phải."""
    mism = 0
    if not os.path.isdir(state_dir):
        return 0
    today = _today().isoformat()
    for d in sorted(os.listdir(state_dir)):
        rd = os.path.join(state_dir, d)
        if not os.path.exists(_manifest_path(rd)):
            continue
        try:
            m = _load_manifest(rd)
        except (OSError, ValueError):
            print(f"VERIFY-WARN {d}: manifest hong — khong kiem duoc")
            mism += 1
            continue
        if str(m.get("ntd")) < today:
            continue
        if m.get("phase") == "running":
            print(f"VERIFY-NOTE {d}: manifest con 'running' — chay recover truoc")
            recover(plan_dir_default, state_dir)
            m = _load_manifest(rd)
        pdir = m.get("plan_dir") or plan_dir_default
        for a, ent in m["accounts"].items():
            if ent.get("decided") is None:
                print(f"VERIFY-WARN {a} {m['ntd']}: chua co quyet dinh")
                mism += 1
                continue
            path = _plan_path(pdir, a, m["ntd"])
            want, have = ent.get("final_content_md5"), _content_md5_file(path)
            if want == have and have != "CORRUPT":
                print(f"VERIFY-OK {a} {m['ntd']}: noi dung plan khop quyet dinh '{ent['decided']}' ({approval_desc(path) if have else 'khong co file, dung nhu luc quyet dinh'})")
                continue
            mism += 1
            if have is None:
                print(f"VERIFY-MISMATCH {a} {m['ntd']}: luc quyet dinh '{ent['decided']}' co plan (content md5 {want}) nhung nay FILE VANG — can nguoi xu ly")
                continue
            stripped = []
            if have != "CORRUPT":
                with open(path, encoding="utf-8") as f:
                    cur = json.load(f)
                before = approval_desc(path)
                stripped = _strip_approval(path, cur)
                print(f"VERIFY-MISMATCH {a} {m['ntd']}: noi dung plan tren dia (md5 {have}) KHAC luc quyet dinh '{ent['decided']}' "
                      f"(md5 {want}) — co job/tien trinh ghi sau quyet dinh. Truoc khi go: {before}. DA GO dau duyet {stripped}, "
                      f"dat requires_user_approval=true. CAN user xem lai plan nay truoc phien.")
            else:
                print(f"VERIFY-MISMATCH {a} {m['ntd']}: file plan HONG (khong doc duoc JSON) — executor se khong nap duoc; can nguoi xu ly (stash: {ent.get('stash')})")
    return mism


# ── QUYẾT ĐỊNH ──────────────────────────────────────────────────────────────────────────────────
def park_guard(plan_dir, acct, ntd):
    """Chuỗi park (park_trim 19:30 → jit_unpark 19:40 → merge_park 20:20) tự bỏ qua cuối tuần ⇒ plan Chủ nhật KHÔNG có
    lệnh bán park mà plan thứ Sáu đã có. → (chặn:bool, lý do|None). Artifact vắng/hỏng cũng chặn (không biết có đề xuất hay không)."""
    why = []
    for layer, fname, keys in (("L1 park_trim", f"park_trim_{acct}_{ntd}.json", ("orders",)),
                               ("L2 jit_unpark", f"jit_unpark_{acct}_{ntd}.json", ("orders", "buy_amendments"))):
        path = os.path.join(plan_dir, fname)
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            if not isinstance(d, dict):
                raise ValueError("khong phai object")
        except FileNotFoundError:
            why.append(f"{layer}: artifact {fname} VANG (khong biet thu Sau co de xuat park hay khong)")
            continue
        except (OSError, ValueError) as e:
            why.append(f"{layer}: artifact {fname} khong doc duoc ({type(e).__name__})")
            continue
        for k in keys:
            lst = d.get(k) or []
            qty = sum(int(o.get("qty") or 0) for o in lst if isinstance(o, dict)) if k == "orders" else len(lst)
            if qty > 0:
                why.append(f"{layer}: {fname}[{k}] co {len(lst)} muc"
                           + (f", tong qty={qty}" if k == "orders" else ""))
    return bool(why), "; ".join(why) if why else None


def decide(plan_dir, run_dir, ntd, acct, status, detail=""):
    m = _load_manifest(run_dir)
    ent = m["accounts"][acct]
    path = _plan_path(plan_dir, acct, ntd)
    out = {"account": acct, "ntd": ntd}
    printed = []

    def finish(result, msg, **kw):
        out.update(result=result, message=msg, **kw)
        _finalize(run_dir, plan_dir, ntd, acct, result)
        printed.append(result)
        print(f"RESULT={result}")
        print(msg)
        return out

    def fail_safe(why, extra=""):
        if ent["had_friday"]:
            _restore(plan_dir, ntd, acct, ent, run_dir)
            return finish("c", f"❌ {acct}: KHONG co plan moi dung duoc — {why}. DA KHOI PHUC plan thu Sau "
                               f"(md5 {ent['md5']}; {approval_desc(path)}). CAN NGUOI kiem tra.{extra}")
        return finish("c", f"❌ {acct}: KHONG co plan nao cho {ntd} (thu Sau cung khong co) — {why}. CAN NGUOI xu ly.{extra}")

    try:
        if os.environ.get("SPR_FAULT_DECIDE") == acct:   # CHỈ cho selfcheck: giả lập crash riêng một account
            raise RuntimeError("fault-injection SPR_FAULT_DECIDE")
        extra = ""
        if status == "job_unsettled":
            extra = (" ⚠️ KHONG xac minh duoc job DollarBill da dung (xem ly do o tren) — plan thu Sau da khoi phuc NHUNG co the "
                     "bi ghi de muon; `--verify` 23:00 CN / 08:30 T2 se kiem noi dung va go dau duyet neu lech.")
        if status != "ok":
            return fail_safe(f"{status}{': ' + detail if detail else ''}", extra)
        if ent["had_friday"]:
            blocked, why = park_guard(plan_dir, acct, ntd)
            if blocked:
                return fail_safe(f"GIU plan thu Sau vi vong CN khong tai tao duoc lop park ({why}); chuoi park_trim 19:30/jit_unpark 19:40/"
                                 "merge_park 20:20 tu bo qua cuoi tuan nen plan CN se THIEU lenh park cua thu Sau")
        new, err = validate_plan(path, acct, ntd)
        if new is None:
            return fail_safe(f"plan moi khong hop le: {err}")
        if ent["had_friday"] and _md5_file(path) == ent["md5"]:
            return fail_safe("DollarBill bao xong nhung file plan khong doi byte nao (khong ghi plan moi)")
        try:
            new_head, new_orders = executor_view(path, acct, ntd)
        except Exception as e:   # noqa: BLE001 — mọi lỗi nạp = plan không dùng được
            return fail_safe(f"plan moi khong nap duoc qua load_plan cua executor ({type(e).__name__}: {str(e)[:160]})")
        if ent["had_friday"]:
            try:
                old_head, old_orders = executor_view(ent["stash"], acct, ntd)
            except Exception as e:   # noqa: BLE001
                return finish("b", f"🟡 {acct}: plan moi hop le nhung ban thu Sau khong nap duoc qua load_plan ({type(e).__name__}) "
                                   "nen khong so sanh — giu plan moi, CAN user duyet lai.", diff=None, stripped=_strip_approval(path, new))
            removed, added = diff_sigs(old_orders, new_orders)
            head_diff = {k: (old_head[k], new_head[k]) for k in old_head if old_head[k] != new_head[k]}
            if not removed and not added and not head_diff:
                _restore(plan_dir, ntd, acct, ent, run_dir)
                return finish("a", f"✅ Chu nhat: plan {acct} khong doi so voi thu Sau (so theo phan executor dung: ticker/side/qty/"
                                   f"ref/urgency/book/cash_only/tran gia/priority + state) — da khoi phuc nguyen file thu Sau; "
                                   f"{approval_desc(path)}.")
            stripped = _strip_approval(path, new)
            lines = [f"🟠 {acct}: plan {ntd} KHAC thu Sau — can user DUYET LAI (da go dau hieu duyet {stripped})."]
            lines += [f"  Δ {k}: {a_} → {b_}" for k, (a_, b_) in head_diff.items()]
            lines += [f"  − {fmt_sig(s)}" for s in removed] + [f"  + {fmt_sig(s)}" for s in added]
            return finish("b", "\n".join(lines), diff={"removed": [fmt_sig(s) for s in removed],
                                                      "added": [fmt_sig(s) for s in added], "head": head_diff}, stripped=stripped)
        stripped = _strip_approval(path, new)
        return finish("b", f"🟠 {acct}: plan {ntd} MOI (thu Sau khong co plan) — can user DUYET.", diff=None, stripped=stripped)
    except BaseException as e:   # noqa: BLE001 — lỗi của account NÀY không được kéo account khác
        if printed:
            raise
        return _crash(plan_dir, run_dir, ntd, acct, ent, e)


def _crash(plan_dir, run_dir, ntd, acct, ent, exc):
    """decide của MỘT account văng lỗi: khôi phục RIÊNG account đó rồi báo (c); không khôi phục được => RESULT=x (không nói 'đã khôi phục')."""
    why = f"{type(exc).__name__}: {str(exc)[:200]}"
    path = _plan_path(plan_dir, acct, ntd)
    try:
        if ent["had_friday"]:
            _restore(plan_dir, ntd, acct, ent, run_dir)
            res, msg = "c", (f"❌ {acct}: decide VANG LOI ({why}) — DA KHOI PHUC RIENG plan thu Sau (md5 {ent['md5']}; "
                             f"{approval_desc(path)}). Account khac KHONG bi anh huong. CAN NGUOI kiem tra.")
        else:
            bad = []
            p, _e = validate_plan(path, acct, ntd) if os.path.exists(path) else (None, None)
            if p is not None:
                bad = _strip_approval(path, p)
            res, msg = "c", (f"❌ {acct}: decide VANG LOI ({why}); thu Sau khong co plan — plan hien co (neu co) da go dau duyet {bad}. CAN NGUOI xu ly.")
        _finalize(run_dir, plan_dir, ntd, acct, res)
    except BaseException as e2:   # noqa: BLE001
        res, msg = "x", (f"🔴 {acct}: decide VANG LOI ({why}) VA khong khoi phuc duoc ({type(e2).__name__}: {str(e2)[:200]}) — "
                         "KHONG ket luan plan hien tai; CAN NGUOI xu ly NGAY.")
    print(f"RESULT={res}")
    print(msg)
    return {"result": res, "message": msg}


# ── JOB: XÁC MINH ĐÃ DỪNG ──────────────────────────────────────────────────────────────────────
def jobs_from_log(log):
    acct, res = None, []
    with open(log, encoding="utf-8", errors="replace") as f:
        for ln in f:
            m = re.search(r"\[pipeline-4\] dispatch DollarBill .* cho (\S+) ---", ln)
            if m:
                acct = m.group(1)
            m = re.search(r"DISPATCHED \S+ \(job=([^ )]+)", ln)
            if m:
                res.append((acct or "?", m.group(1)))
    return res


def _read_job(jobs_dir, jid):
    try:
        with open(os.path.join(jobs_dir, f"{jid}.json"), encoding="utf-8") as f:
            o = json.load(f)
        return o if isinstance(o, dict) else None
    except (OSError, ValueError):
        return None


def settle_one(jobs_dir, pend_dir, removed_dir, jid):
    """→ (settled:bool, mô tả). 'Đã huỷ' CHỈ khi đọc lại bản ghi job và thấy trạng thái KẾT THÚC; job usage_limited/
    maxturns_pending (cancel là no-op rc=0) chỉ được coi là vô hiệu khi ta gỡ được bản ghi resume còn nguyên — nếu bản
    ghi resume đã mất thì lần resume có thể đã bắn thành job MỚI không rõ id => KHÔNG xác minh được."""
    o = _read_job(jobs_dir, jid)
    if o is None:
        return False, f"khong doc duoc ban ghi job {jid} ({jobs_dir}) — khong xac minh duoc"
    st = o.get("status", "?")
    if st not in LIVE_STATUSES:
        return True, f"status={st} (ket thuc)"
    if st in PENDING_RESUME_STATES:
        pf = os.path.join(pend_dir, f"{jid}.json")
        if not os.path.exists(pf) and os.path.exists(os.path.join(removed_dir, f"{jid}.json")):
            return True, f"status={st} (cho resume) — ban ghi resume DA duoc go o luot truoc (cat o {removed_dir}); resume khong the ban"
        if not os.path.exists(pf):
            return False, (f"status={st} nhung bus/pending_resumes/{jid}.json KHONG con — resume co the DA ban thanh job moi "
                           "(id khong ro), khong xac minh duoc")
        os.makedirs(removed_dir, exist_ok=True)
        os.replace(pf, os.path.join(removed_dir, f"{jid}.json"))
        if os.path.exists(pf):
            return False, f"status={st}; go bus/pending_resumes/{jid}.json that bai"
        return True, (f"status={st} (cho resume) — DA GO ban ghi resume bus/pending_resumes/{jid}.json "
                      f"(cat o {removed_dir}); resume khong the ban nua")
    return False, f"status={st} — job VAN CON SONG sau cancel"


def settle(jobs_dir, pend_dir, removed_dir, since, pairs, scan):
    """In SETTLED/UNSETTLED cho từng job; --scan: job DollarBill nào khác còn sống bắt đầu từ `since` => SCAN-UNSETTLED."""
    bad = 0
    known = {j for _a, j in pairs}
    for acct, jid in pairs:
        ok, why = settle_one(jobs_dir, pend_dir, removed_dir, jid)
        print(f"{'SETTLED' if ok else 'UNSETTLED'} {acct} {jid} {why}")
        bad += 0 if ok else 1
    if scan and os.path.isdir(jobs_dir):
        for fn in sorted(os.listdir(jobs_dir)):
            if not fn.endswith(".json"):
                continue
            jid = fn[:-5]
            o = _read_job(jobs_dir, jid)
            if not o or jid in known or o.get("to") != "DollarBill" or o.get("status") not in LIVE_STATUSES:
                continue
            try:
                started = int(o.get("started_at") or 0)
            except ValueError:
                started = 0
            if started >= since:
                print(f"SCAN-UNSETTLED - {jid} job DollarBill khac con song (status={o.get('status')}, started_at={started} >= {since}) "
                      "— khong nam trong log freshness, khong the xac minh no se khong ghi plan")
                bad += 1
    return bad


def prune(state_dir, keep):
    if not os.path.isdir(state_dir):
        return
    dated = sorted(d for d in os.listdir(state_dir) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) and os.path.isdir(os.path.join(state_dir, d)))
    for d in dated[:-keep] if keep > 0 else dated:
        rd = os.path.join(state_dir, d)
        try:
            ph = _load_manifest(rd).get("phase")
        except (OSError, ValueError):
            ph = "?"
        if ph in ("done", "recovered", "stale_skipped"):
            shutil.rmtree(rd, ignore_errors=True)
            print(f"PRUNE {d} (phase={ph})")


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
    for name in ("recover", "verify"):
        r = sub.add_parser(name); r.add_argument("--plan-dir", required=True); r.add_argument("--state-dir", required=True)
        if name == "recover":
            r.add_argument("--account")
    j = sub.add_parser("jobs"); j.add_argument("log")
    st = sub.add_parser("settle")
    st.add_argument("--jobs-dir", required=True); st.add_argument("--pend-dir", required=True)
    st.add_argument("--removed-dir", required=True); st.add_argument("--since", type=int, default=0)
    st.add_argument("--scan", action="store_true"); st.add_argument("--job", action="append", default=[])
    sm = sub.add_parser("summary"); sm.add_argument("--run-dir", required=True)
    bj = sub.add_parser("busjson"); bj.add_argument("--kv", nargs="*", default=[])
    pr = sub.add_parser("prune"); pr.add_argument("--state-dir", required=True); pr.add_argument("--keep", type=int, default=8)
    a = ap.parse_args()
    if a.cmd == "gate":
        print(gate(a.check))
    elif a.cmd == "stash":
        stash(a.plan_dir, a.run_dir, a.ntd, a.labels.split())
    elif a.cmd == "decide":
        decide(a.plan_dir, a.run_dir, a.ntd, a.account, a.status, a.detail)
    elif a.cmd == "recover":
        n, bad = recover(a.plan_dir, a.state_dir, a.account)
        sys.exit(3 if bad else 0)
    elif a.cmd == "verify":
        sys.exit(4 if verify(a.plan_dir, a.state_dir) else 0)
    elif a.cmd == "settle":
        pairs = [tuple(x.split("=", 1)) for x in a.job]
        sys.exit(3 if settle(a.jobs_dir, a.pend_dir, a.removed_dir, a.since, pairs, a.scan) else 0)
    elif a.cmd == "summary":
        mm = _load_manifest(a.run_dir)
        print(" ".join(f"{k}={v.get('decided')}" for k, v in mm["accounts"].items()))
    elif a.cmd == "busjson":
        print(json.dumps(dict(x.split("=", 1) for x in a.kv), ensure_ascii=False))
    elif a.cmd == "prune":
        prune(a.state_dir, a.keep)
    else:
        for acct, jid in jobs_from_log(a.log):
            print(acct, jid)


if __name__ == "__main__":
    main()
