#!/usr/bin/env python3
"""Ghi/đọc xác nhận của USER cho gói DD LAG (`data/lag_dd/ack.json`) + trạng thái cổng DD theo mã.

Chỉ Mike ghi ack, và CHỈ khi user đã trả lời thật (coding_guidelines §20: decided_by="user" chỉ
khi user xác nhận real-time). lag_dd_pack.py KHÔNG BAO GIỜ ghi file này.

Mỗi mục: {ticker, release_date, decision: PROCEED|DROP|RESEARCH, decided_by: "user", at (ISO có
múi giờ), flags_hash, note, source}. Append-only; mục MỚI NHẤT theo (ticker, release_date) thắng.
`flags_hash` khoá ack vào ĐÚNG bộ cờ user đã xem: tin Discord in hash ngắn kèm mã cờ; `record()`
BẮT BUỘC `--flags-hash` (hash trong tin user đã thấy) và TỪ CHỐI khi lệch hash gói hiện tại — gói sinh
lại giữa lúc gửi tin và lúc user trả lời ⇒ ack bị từ chối, KHÔNG đóng dấu bộ cờ mới. `--source` bắt
buộc khác rỗng (provenance, coding_guidelines §20). Gói sinh lại SAU khi ack đã ghi ⇒ ACK_STALE.

    python3 bin/lag_dd_ack.py --ticker SCL --release-date 2026-10-19 --decision PROCEED \
        --decided-by user --at 2026-10-25T18:30:00+07:00 --flags-hash <hash trong tin> \
        --note "..." --source "discord <link>"
    python3 bin/lag_dd_ack.py --show
    python3 bin/lag_dd_ack.py --gate SCL --plan-date 2026-10-26     # trạng thái cổng 1 mã
    python3 bin/lag_dd_ack.py --note-prompt --plan-date 2026-10-26  # đoạn cổng DD + quy mô cho prompt DollarBill

Mã thoát: 0 OK · 1 dữ liệu vào không hợp lệ / lỗi đọc-ghi.
"""
import argparse
import datetime as dt
import fcntl
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lag_dd_pack import dd_dir, write_atomic  # noqa: E402

DECISIONS = ("PROCEED", "DROP", "RESEARCH")
PACK_MAX_AGE_DAYS = 30     # gói có release_date cách plan_date > 30 ngày lịch ⇒ không phải sự kiện đang xét
PACK_ASOF_MAX_DAYS = 7     # gói có asof cách plan_date > 7 ngày lịch ⇒ PACK_STALE (insider/ex-date/anomaly đã cũ)
_RE_PACK = re.compile(r"^([A-Z0-9]{3,5})_(\d{4}-\d{2}-\d{2}|NA)\.json$")
BUY_OK = ("CLEARED", "ACK_PROCEED")


def ack_path():
    return os.path.join(dd_dir(), "ack.json")


def load_acks(path=None):
    """list mục ack. File không có ⇒ []. File hỏng ⇒ raise (caller fail-closed)."""
    p = path or ack_path()
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    acks = d.get("acks") if isinstance(d, dict) else None
    if not isinstance(acks, list):
        raise ValueError(f"{p}: thiếu list 'acks'")
    return acks


def latest_ack(acks, ticker, release_date):
    hit = [a for a in acks if isinstance(a, dict) and str(a.get("ticker")).upper() == ticker
           and str(a.get("release_date")) == str(release_date)]
    return hit[-1] if hit else None


def _read_pack(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _generated_at(path):
    """datetime tz-aware của gói hoặc None (không đọc được ⇒ không so được thứ tự)."""
    try:
        v = dt.datetime.fromisoformat(str(_read_pack(path).get("generated_at")))
        return v if v.tzinfo else None
    except (OSError, ValueError, TypeError, AttributeError):
        return None


def find_pack(ticker, plan_date, directory=None, release_date=None):
    """(path|None, lý do). Gói release_date ≤ plan_date, trong PACK_MAX_AGE_DAYS, mới nhất; nếu
    `release_date` (của ứng viên) được truyền ⇒ CHỈ gói đúng release đó. Gói `<MÃ>_NA` (không xác
    định được release) sinh SAU gói có release ⇒ thắng (không dùng gói CLEARED cũ khi lần chạy mới
    nhất đã báo RELEASE_NA)."""
    d0 = dt.date.fromisoformat(str(plan_date)[:10])
    best, na = None, None
    for p in glob.glob(os.path.join(directory or dd_dir(), f"{ticker}_*.json")):
        m = _RE_PACK.match(os.path.basename(p))
        if not m or m.group(1) != ticker:
            continue
        if m.group(2) == "NA":
            na = p
            continue
        if release_date and m.group(2) != str(release_date)[:10]:
            continue
        rel = dt.date.fromisoformat(m.group(2))
        if rel <= d0 and (d0 - rel).days <= PACK_MAX_AGE_DAYS and (best is None or rel > best[0]):
            best = (rel, p)
    if best and na:
        g_best, g_na = _generated_at(best[1]), _generated_at(na)
        if g_na is None or g_best is None or g_na > g_best:    # không so được ⇒ fail-closed: NA thắng
            return na, f"gói {os.path.basename(na)} mới hơn (hoặc không so được) gói {os.path.basename(best[1])}"
    if best:
        return best[1], ""
    if na:
        return na, "chỉ có gói release=NA"
    return None, f"không có data/lag_dd/{ticker}_<release>.json với release ≤ {plan_date} trong {PACK_MAX_AGE_DAYS} ngày"


def dd_gate(ticker, plan_date, directory=None, acks=None, release_date=None):
    """Trạng thái cổng DD của 1 mã cho plan_date. KHÔNG raise.

    state ∈ CLEARED | ACK_PROCEED (được mua) · FLAG_NO_ACK | ACK_DROP | ACK_RESEARCH | ACK_STALE |
    ACK_NOT_USER | NO_PACK | PACK_STALE | PACK_UNREADABLE | ACK_UNREADABLE (KHÔNG được mua).
    `release_date` (tuỳ chọn) = release của ứng viên: chỉ chấp nhận gói đúng release đó.
    """
    t = str(ticker or "").strip().upper()
    out = {"ticker": t, "plan_date": str(plan_date), "state": None, "pack": None,
           "release_date": None, "status": None, "flags": [], "ack": None, "evidence": ""}
    try:
        path, why = find_pack(t, plan_date, directory, release_date)
    except (ValueError, OSError) as e:
        path, why = None, f"{type(e).__name__}: {e}"
    if not path:
        out.update(state="NO_PACK", evidence=why)
        return out
    out["pack"] = path
    try:
        pk = _read_pack(path)
        status, fl, rel, fh = pk["status"], pk.get("flags") or [], pk.get("release_date"), pk["flags_hash"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        out.update(state="PACK_UNREADABLE", evidence=f"{os.path.basename(path)}: {type(e).__name__}: {e}")
        return out
    out.update(release_date=rel, status=status, flags=[f.get("code") for f in fl if isinstance(f, dict)])
    try:
        age = (dt.date.fromisoformat(str(plan_date)[:10]) - dt.date.fromisoformat(str(pk["asof"])[:10])).days
    except (KeyError, ValueError, TypeError):
        out.update(state="PACK_STALE", evidence=f"{os.path.basename(path)}: không đọc được asof ({pk.get('asof')!r})")
        return out
    if age > PACK_ASOF_MAX_DAYS or age < 0:
        out.update(state="PACK_STALE", evidence=f"{os.path.basename(path)}: DD asof {pk['asof']} cách plan_date "
                                                f"{plan_date} {age} ngày (cho phép 0..{PACK_ASOF_MAX_DAYS}) — chạy lại lag_dd_pack.py")
        return out
    if status == "CLEARED" and not fl:
        # CLEARED không được NUỐT quyết định LOẠI/NGHIÊN CỨU của user cho đúng release này: gói sinh lại
        # sạch cờ (vd DCF_RICH nhẹ chuyển thành warning) sẽ đổi flags_hash, nhưng DROP vẫn là DROP.
        # Chỉ chiều AN TOÀN (chặn thêm) — PROCEED không bao giờ được đọc ở nhánh này. ack.json hỏng ở
        # nhánh CLEARED: giữ hành vi cũ (CLEARED) vì CLEARED vốn không cần ack.
        try:
            la = latest_ack(load_acks(os.path.join(directory, "ack.json") if directory else None)
                            if acks is None else acks, t, rel)
        except (OSError, ValueError):
            la = None
        if la and la.get("decided_by") == "user" and la.get("decision") in ("DROP", "RESEARCH"):
            out.update(state=f"ACK_{la['decision']}", ack=la,
                       evidence=f"{os.path.basename(path)} nay CLEARED nhưng user {la['decision']} lúc "
                                f"{la.get('at')} cho release này — quyết định loại vẫn hiệu lực")
            return out
        out.update(state="CLEARED", evidence=f"{os.path.basename(path)} CLEARED (0 cờ)")
        return out
    try:
        acks = load_acks(os.path.join(directory, "ack.json") if directory else None) if acks is None else acks
    except (OSError, ValueError) as e:
        out.update(state="ACK_UNREADABLE", evidence=f"ack.json: {type(e).__name__}: {e}")
        return out
    a = latest_ack(acks, t, rel)
    out["ack"] = a
    codes = ",".join(out["flags"]) or "-"
    if not a:
        out.update(state="FLAG_NO_ACK", evidence=f"{os.path.basename(path)} FLAG [{codes}], user chưa trả lời")
    elif a.get("decided_by") != "user":
        out.update(state="ACK_NOT_USER", evidence=f"ack decided_by={a.get('decided_by')!r} ≠ 'user'")
    elif a.get("flags_hash") != fh:
        out.update(state="ACK_STALE", evidence=f"ack {a.get('decision')} lúc {a.get('at')} cho bộ cờ "
                                               f"{a.get('flags_hash')} ≠ gói hiện tại {fh} [{codes}]")
    elif a.get("decision") == "PROCEED":
        out.update(state="ACK_PROCEED", evidence=f"user PROCEED lúc {a.get('at')} dù cờ [{codes}]")
    elif a.get("decision") in ("DROP", "RESEARCH"):
        out.update(state=f"ACK_{a['decision']}", evidence=f"user {a['decision']} lúc {a.get('at')} [{codes}]")
    else:
        out.update(state="ACK_NOT_USER", evidence=f"ack decision lạ {a.get('decision')!r}")
    return out


_RE_TIER = re.compile(r"\b(LAG_(?:LO|HI))\b(?:\s*(\d+(?:[.,]\d+)?)\s*%)?")
_RE_TIER_NEG = re.compile(r"\b(?:không|ko|chưa|bỏ|thay vì|not)\b[^;.]{0,20}\bLAG_(?:LO|HI)\b", re.I)


def ack_tier(note):
    """(tier, pct|None) user chốt trong note ack, vd 'LAG_LO 8%' ⇒ ('LAG_LO', '8'). Không nêu hoặc
    nêu >1 tier khác nhau, hoặc tier đứng sau phủ định ('không LAG_HI') ⇒ (None, None) — mơ hồ thì
    KHÔNG đoán."""
    if _RE_TIER_NEG.search(str(note or "")):
        return None, None
    hits = _RE_TIER.findall(str(note or ""))
    tiers = {h[0] for h in hits}
    if len(tiers) != 1:
        return None, None
    pcts = {h[1].replace(",", ".") for h in hits if h[1]}
    return tiers.pop(), (pcts.pop() if len(pcts) == 1 else None)


def prompt_note(plan_date, directory=None):
    """1 đoạn văn cho prompt DollarBill: trạng thái cổng DD + quy mô user chốt của MỌI mã có gói DD
    trong cửa sổ plan_date. Sinh bằng code từ dd_gate() — DollarBill không phải tự đọc/diễn giải
    ack.json. Mã NO_PACK (ngoài cửa sổ) bỏ qua."""
    d = directory or dd_dir()
    tickers = sorted({m.group(1) for m in (_RE_PACK.match(os.path.basename(p))
                                           for p in glob.glob(os.path.join(d, "*.json"))) if m})
    ok, bad = [], []
    for t in tickers:
        g = dd_gate(t, plan_date, directory)
        st = g["state"]
        if st == "NO_PACK":
            continue
        if st == "CLEARED":
            ok.append(f"{t} (CLEARED — quy mô theo play_type trong recommend)")
        elif st == "ACK_PROCEED":
            a = g.get("ack") or {}
            tier, pct = ack_tier(a.get("note"))
            size = (f"quy mô {tier}{' ' + pct + '%' if pct else ''} DO USER CHỐT" if tier else
                    "ack KHÔNG nêu quy mô rõ ràng — KHÔNG mặc định LAG_HI: dùng LAG_LO 8% (mức nhỏ hơn), "
                    "đặt requires_user_approval=true và ghi rõ trong plan note để user xác nhận quy mô")
            cond = " ".join(str(a.get("note") or "").split())
            cond = cond if len(cond) <= 400 else cond[:400] + "…"
            ok.append(f"{t} (user PROCEED lúc {a.get('at')}: {size}; điều kiện user: '{cond}')")
        else:
            bad.append(f"{t} ({st})")
    if not ok and not bad:
        return ""
    return (f" CỔNG DD LAG cho plan {plan_date} (sinh bằng code từ data/lag_dd/ack.json + gói DD, "
            f"`bin/lag_dd_ack.py --note-prompt --plan-date {plan_date}`; kiểm 1 mã: `--gate <MÃ> --plan-date {plan_date}`):"
            " PHẠM VI: danh sách này CHỈ gate/size các mã LAG mà recommend ĐỀ XUẤT VÀO đúng phiên"
            f" {plan_date} theo cửa sổ entry/status của recommend (vd 'UPCOMING T+1'). Nó KHÔNG thêm mã,"
            " KHÔNG kéo ngày vào sớm (mã recommend ghi UPCOMING T+2 trở lên vẫn chờ đúng phiên), và KHÔNG"
            " loại mã CLEARED recommend đề xuất."
            f" ĐƯỢC PHÉP (nếu recommend đề xuất vào phiên này): {'; '.join(ok) or 'không mã nào'}."
            f" KHÔNG ĐƯA VÀO orders[] (kể cả khi recommend đề xuất): {', '.join(bad) or 'không'}."
            " Quy mô user chốt trong ack THẮNG play_type của CSV recommend — recommend ghi LAG_HI 10% mà ack"
            " ghi LAG_LO 8% thì size LAG_LO 8% và ghi play_type LAG_LO trong lệnh; KHÔNG tự nâng lại LAG_HI."
            " Mã LAG có gói DD mà ở trạng thái khác CLEARED/ACK_PROCEED (ACK_DROP, ACK_RESEARCH, FLAG_NO_ACK,"
            " ACK_STALE, PACK_STALE...) TUYỆT ĐỐI không vào orders[] — lag_plan_consistency_check chỉ báo"
            " đỏ trong report (chưa chặn cứng), nên tuân thủ ở bước lập plan là lớp bảo vệ chính.")


def _parse_at(s):
    v = dt.datetime.fromisoformat(str(s))
    if v.tzinfo is None:
        raise ValueError("--at phải có múi giờ (vd 2026-10-25T18:30:00+07:00)")
    return v


def record(ticker, release_date, decision, decided_by, at, flags_hash, source, note="", directory=None):
    """Validate + append 1 ack. Trả mục đã ghi. Raise ValueError khi không hợp lệ (gồm: flags_hash
    rỗng hoặc ≠ hash gói HIỆN TẠI — user đã xem bộ cờ khác; source rỗng)."""
    t = str(ticker).strip().upper()
    if not str(source or "").strip():
        raise ValueError("--source bắt buộc (link/trích tin nhắn user trả lời — provenance, §20)")
    if not str(flags_hash or "").strip():
        raise ValueError("--flags-hash bắt buộc (hash in trong tin Discord user đã xem)")
    if decision not in DECISIONS:
        raise ValueError(f"decision phải ∈ {DECISIONS}, nhận {decision!r}")
    if decided_by != "user":
        raise ValueError("decided_by phải là 'user' — ack chỉ ghi khi USER đã trả lời thật (§20)")
    at_v = _parse_at(at)
    dt.date.fromisoformat(str(release_date))
    dd = directory or dd_dir()
    pack_p = os.path.join(dd, f"{t}_{release_date}.json")
    try:
        pk = _read_pack(pack_p)
    except (OSError, ValueError) as e:
        raise ValueError(f"không đọc được gói {pack_p}: {e} — ack phải gắn với gói DD có thật")
    if pk.get("ticker") != t or str(pk.get("release_date")) != str(release_date):
        raise ValueError(f"gói {pack_p} ticker/release không khớp ({pk.get('ticker')}, {pk.get('release_date')})")
    if str(flags_hash).strip() != pk.get("flags_hash"):
        raise ValueError(f"flags_hash {flags_hash!r} ≠ gói hiện tại {pk.get('flags_hash')!r} "
                         f"({[f.get('code') for f in pk.get('flags') or []]}) — gói đã sinh lại sau khi gửi tin; "
                         "hỏi lại user với bộ cờ mới, KHÔNG ghi ack")
    entry = {"ticker": t, "release_date": str(release_date), "decision": decision,
             "decided_by": "user", "at": at_v.isoformat(), "flags_hash": pk.get("flags_hash"),
             "flags": [f.get("code") for f in pk.get("flags") or []], "pack_status": pk.get("status"),
             "note": note, "source": source,
             "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    ap = os.path.join(dd, "ack.json")
    os.makedirs(dd, exist_ok=True)
    with open(ap + ".lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        acks = load_acks(ap)
        write_atomic(ap, {"acks": acks + [entry]})
    return entry


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ticker")
    ap.add_argument("--release-date")
    ap.add_argument("--decision", choices=DECISIONS)
    ap.add_argument("--decided-by")
    ap.add_argument("--at", help="ISO có múi giờ: lúc user trả lời")
    ap.add_argument("--note", default="")
    ap.add_argument("--flags-hash", help="hash in trong tin Discord user đã xem (bắt buộc khi ghi ack)")
    ap.add_argument("--source", default="", help="link/trích tin nhắn user (bắt buộc khi ghi ack)")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--gate", metavar="TICKER")
    ap.add_argument("--plan-date")
    ap.add_argument("--note-prompt", "--prompt-note", dest="prompt_note", action="store_true",
                    help="in đoạn cổng DD + quy mô user chốt cho prompt DollarBill (cần --plan-date)")
    a = ap.parse_args(argv)
    try:
        if a.show:
            print(json.dumps(load_acks(), ensure_ascii=False, indent=1))
            return 0
        if a.prompt_note:
            if not a.plan_date:
                ap.error("--note-prompt cần --plan-date")
            print(prompt_note(a.plan_date))
            return 0
        if a.gate:
            if not a.plan_date:
                ap.error("--gate cần --plan-date")
            print(json.dumps(dd_gate(a.gate, a.plan_date), ensure_ascii=False, indent=1, default=str))
            return 0
        missing = [k for k in ("ticker", "release_date", "decision", "decided_by", "at", "flags_hash", "source")
                   if not getattr(a, k)]
        if missing:
            ap.error("thiếu " + ", ".join("--" + m.replace("_", "-") for m in missing))
        e = record(a.ticker, a.release_date, a.decision, a.decided_by, a.at, a.flags_hash, a.source, a.note)
    except (ValueError, OSError) as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    print(json.dumps(e, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
