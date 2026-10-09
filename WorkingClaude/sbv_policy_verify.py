#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sbv_policy_verify.py — kiểm HẰNG TUẦN lãi suất điều hành NHNN (tái cấp vốn + tái chiết khấu; OMO nếu
nguồn có), chạy trong chuỗi Thứ Hai 08:05 ICT của refresh_deposit_cctg_weekly.sh (user duyệt
2026-10-09, job Winston_20261009_094651). Thay phần fetch/stamp của mike/bin/check_sbv_weekly.sh
(đã retire) — bản đó ghi `last_verified=<hôm nay>` kể cả khi fetch HỎNG ("fetch_failed_assumed_
unchanged"), nên nhãn "đã kiểm" sai suốt 07/08→09/10/2026 (URL cũ 404 + UA bị WAF chặn).

HAI MỐC TÁCH RỜI (luật cốt lõi của file này):
  verified_at  — lần cuối LẤY ĐƯỢC SỐ từ NHNN VÀ khớp nguồn độc lập VÀ khớp SBV_REFI_EVENTS.
                 CHỈ `cmd_verify` nhánh thành công được đẩy mốc này. Không có đường nào khác.
  attempted_at — lần cuối THỬ (mọi kết cục). Fetch hỏng / lệch / thiếu nguồn CHỈ đẩy mốc này.
`last_verified` (YYYY-MM-DD) giữ cho macro_healthcheck.py đọc như cũ = ngày của verified_at.

Nguồn (chuẩn giống CCTG/Big-4 — append_cctg_rate.py):
  A. Trang chính thức NHNN `sbv.gov.vn/vi/lãi-suất1` — script TỰ fetch + parse (cơ học, agent không
     tự khai số NHNN được).
  B. >=1 nguồn ĐỘC LẬP khác chủ (không thuộc sbv.gov.vn), agent WebSearch rồi cite qua --sources,
     mỗi nguồn ghi rõ refi + rediscount (+ omo tùy chọn), ngày <=MAX_SOURCE_AGE_DAYS, URL không được
     trùng lần ghi trước (sidecar, dùng lại guard của append_deposit_rate.py).
  Khớp hết ⇒ verified. Lệch / thiếu ⇒ KHÔNG ghi số, chỉ attempted_at + outcome. Lãi NHNN khác
  SBV_REFI_EVENTS ⇒ 🔴 cảnh báo, KHÔNG tự sửa SBV_REFI_EVENTS (người duyệt).

KHÔNG đổi hành vi macro gate/DT5G: file này không ghi sbv_macro_overlay.py, chỉ ghi
data/sbv_verify_log.json (chỉ hiển thị + nhắc).

Lệnh:
  python3 sbv_policy_verify.py fetch                       # in số NHNN parse được (không ghi gì)
  python3 sbv_policy_verify.py verify --sources '<JSON>'    # agent/người gọi; ghi log
  python3 sbv_policy_verify.py finalize --run-start <UTC>  # cuối wrapper Thứ Hai: ghi attempt nếu
                                                           # chưa ai gọi verify + nhắc stale >21 ngày
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")  # coding_guidelines §16

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from append_deposit_rate import (  # noqa: E402 — dùng lại guard đã qua 8 vòng review, không chép
    _owner_group, _check_urls_not_reused, _save_last_auto_urls)

OFFICIAL_URL = "https://sbv.gov.vn/vi/l%C3%A3i-su%E1%BA%A5t1"
OFFICIAL_OWNER = "sbv.gov.vn"
# UA trình duyệt: UA tự khai bot ("compatible; SBV-verify") bị WAF trang chủ trả "Request Rejected".
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0 Safari/537.36")
MAX_SOURCE_AGE_DAYS = 35      # cùng ngưỡng append_cctg_rate.py
RATE_EPS_PP = 0.01            # lãi điều hành niêm yết 3 số lẻ — phải khớp, không phải "gần"
RATE_MIN_PCT, RATE_MAX_PCT = 0.5, 20.0
STALE_DAYS = 21
HISTORY_KEEP = 52

# Ghi đè đường dẫn/HTML CHỈ cho selfcheck (một biến sót lại không được âm thầm đổi đích ghi).
_SELFCHECK = os.environ.get("SBV_POLICY_SELFCHECK") == "1"
DATA_DIR = (os.environ.get("SBV_POLICY_DATA_DIR") if _SELFCHECK else None) or os.path.join(HERE, "data")
LOG_PATH = os.path.join(DATA_DIR, "sbv_verify_log.json")
SIDECAR_PATH = os.path.join(DATA_DIR, "sbv_policy_last_auto_sources.json")
NOTIFY = os.path.join(HERE, "mike", "bin", "notify_thread.sh")


class Refuse(Exception):
    def __init__(self, outcome, detail):
        super().__init__(detail)
        self.outcome, self.detail = outcome, detail


def _now():
    return datetime.now(_ICT)


# ───────────────────────── nguồn A: trang NHNN ─────────────────────────
def _fetch_official_html():
    fake = os.environ.get("SBV_POLICY_FAKE_HTML") if _SELFCHECK else None
    if fake:
        with open(fake, encoding="utf-8") as f:
            return f.read()
    last_err = None
    for _ in range(3):
        try:
            req = urllib.request.Request(OFFICIAL_URL, headers={
                "User-Agent": UA, "Accept-Language": "vi,en;q=0.8"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001 — giữ nguyên lỗi thật để trích (§29)
            last_err = e
    raise Refuse("official_fetch_failed", f"GET {OFFICIAL_URL} lỗi sau 3 lần: {last_err!r}")


def _vn_num(s):
    return float(s.replace(".", "").replace(",", "."))


def parse_official(page):
    """-> {refi_pct, rediscount_pct, refi_decision, refi_effective_text, ...}. Refuse nếu không
    thấy ĐÚNG 1 giá trị cho mỗi loại — trích tiêu đề trang + đoạn quanh từ khóa làm bằng chứng."""
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page, flags=re.S | re.I)
    s = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))
    out = {}
    for key, label in (("refi", "tái cấp vốn"), ("rediscount", "tái chiết khấu")):
        pat = (r"Lãi suất " + label + r"\s+([0-9]{1,2},[0-9]{1,3})\s*%\s*"
               r"(\S+/QĐ-NHNN ngày \d{1,2}/\d{1,2}/\d{4})?\s*(\d{1,2}/\d{1,2}/\d{4})?")
        hits = re.findall(pat, s, flags=re.I)
        vals = {_vn_num(h[0]) for h in hits}
        if len(vals) != 1:
            title = re.search(r"<title>(.*?)</title>", page, flags=re.S | re.I)
            i = s.lower().find(label)
            raise Refuse("official_parse_failed",
                         f"'{label}': {len(vals)} giá trị khác nhau {sorted(vals)} (cần đúng 1). "
                         f"title={title.group(1).strip()[:80] if title else None!r} "
                         f"đoạn={s[max(0, i - 80):i + 160] if i >= 0 else '(không thấy từ khóa)'!r}")
        v = vals.pop()
        if not (RATE_MIN_PCT <= v <= RATE_MAX_PCT):
            raise Refuse("official_parse_failed", f"'{label}'={v}% ngoài khoảng hợp lý")
        out[f"{key}_pct"] = v
        out[f"{key}_decision"] = hits[0][1] or None
        out[f"{key}_effective_text"] = hits[0][2] or None
    return out


# ───────────────────────── log ─────────────────────────
def _migrate_legacy(old):
    """Định dạng check_sbv_weekly.sh: `last_verified` bị đẩy cả khi fetch_failed ⇒ KHÔNG tin.
    verified_at = mục legacy cuối KHÔNG phải fetch_failed (seed user xác nhận 2026-06-27 /
    fetched-unchanged), tức mốc kiểm thật cuối cùng."""
    real = [h for h in old.get("history", [])
            if (h.get("fetch_status") == "fetched" and h.get("note") == "unchanged")
            or str(h.get("note", "")).startswith("initial seed")]
    last = real[-1] if real else None
    va = f"{last['date']}T00:00:00+07:00" if last else None
    return {"schema": "sbv_policy_verify_v2", "verified_at": va, "attempted_at": None,
            "last_verified": last["date"] if last else None,
            "verified": ({"refi_pct": last.get("rate_confirmed"), "method": "legacy_check_sbv_weekly",
                          "note": last.get("note")} if last else None),
            "last_attempt": None, "history": [],
            "legacy_history": old.get("history", []),
            "migrated_note": ("Di trú từ check_sbv_weekly.sh 2026-10-09: last_verified cũ bị đẩy "
                              "cả khi fetch_failed nên bị bỏ; verified_at = lần kiểm thật cuối.")}


def load_log():
    try:
        with open(LOG_PATH, encoding="utf-8") as f:
            d = json.load(f)
    except FileNotFoundError:
        d = {}
    if d.get("schema") != "sbv_policy_verify_v2":
        d = _migrate_legacy(d)
    return d


def save_log(d):
    os.makedirs(DATA_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, prefix=".sbvlog_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        os.replace(tmp, LOG_PATH)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def record_attempt(d, outcome, detail, at=None):
    at = at or _now().isoformat(timespec="seconds")
    d["attempted_at"] = at
    d["last_attempt"] = {"at": at, "outcome": outcome, "detail": detail}
    d.setdefault("history", []).append({"at": at, "outcome": outcome, "detail": detail[:300]})
    d["history"] = d["history"][-HISTORY_KEEP:]


def _notify(msg):
    if os.environ.get("SBV_POLICY_NO_NOTIFY") == "1" or _SELFCHECK:
        print(f"[no-notify] {msg}")
        return True
    r = subprocess.run([NOTIFY, msg, "trading_daily"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"LỖI notify_thread.sh rc={r.returncode}: {r.stderr.strip()[:300]}", file=sys.stderr)
    return r.returncode == 0


def _recorded_refi():
    try:
        from sbv_macro_overlay import SBV_REFI_EVENTS
        ev = SBV_REFI_EVENTS[-1]
        return str(ev[0]), float(ev[1])
    except Exception as e:  # noqa: BLE001 — fail-closed, trích lỗi thật (§29)
        raise Refuse("recorded_refi_unreadable", f"không đọc được SBV_REFI_EVENTS: {e!r}")


# ───────────────────────── nguồn B: kiểm --sources ─────────────────────────
def check_sources(raw, official, today):
    try:
        sources = json.loads(raw)
    except json.JSONDecodeError as e:
        raise Refuse("bad_sources", f"--sources không phải JSON: {e}")
    if not isinstance(sources, list) or not sources or not all(isinstance(s, dict) for s in sources):
        raise Refuse("bad_sources", "--sources phải là mảng JSON >=1 object")
    owners, urls = set(), []
    for s in sources:
        url = str(s.get("url", ""))
        try:
            owner = _owner_group(url)
        except ValueError as e:
            raise Refuse("bad_sources", str(e))
        if owner == OFFICIAL_OWNER:
            raise Refuse("not_independent",
                         f"{url}: thuộc {OFFICIAL_OWNER} — nguồn B phải KHÁC chủ với NHNN")
        try:
            sd = datetime.strptime(str(s.get("date", "")), "%Y-%m-%d").date()
        except ValueError:
            raise Refuse("bad_sources", f"{url}: 'date' thiếu/sai ({s.get('date')!r})")
        age = (today - sd).days
        if age < 0 or age > MAX_SOURCE_AGE_DAYS:
            raise Refuse("stale_source", f"{url}: ngày {sd} cách hôm nay {age} ngày "
                                         f"(cho phép 0..{MAX_SOURCE_AGE_DAYS})")
        for k in ("refi", "rediscount"):
            try:
                v = float(s[k])
            except (KeyError, TypeError, ValueError):
                raise Refuse("bad_sources", f"{url}: thiếu/sai '{k}' ({s.get(k)!r}) — mỗi nguồn "
                                            f"phải ghi rõ số nó báo")
            if abs(v - official[f"{k}_pct"]) > RATE_EPS_PP:
                raise Refuse("source_mismatch",
                             f"{url}: {k}={v}% ≠ NHNN {official[k + '_pct']}% — KHÔNG ghi số, "
                             f"cần người xem")
        owners.add(owner)
        urls.append(url)
    try:
        _check_urls_not_reused(urls, SIDECAR_PATH)
    except SystemExit as e:
        raise Refuse("url_reused", str(e))
    return sources, urls, sorted(owners)


def _omo(sources):
    """OMO chỉ ghi số khi >=2 chủ khác nhau báo cùng giá trị; còn lại chỉ lưu trích dẫn."""
    rep = []
    for s in sources:
        if s.get("omo") is None:
            continue
        try:
            rep.append((_owner_group(s["url"]), float(s["omo"])))
        except (TypeError, ValueError):
            continue
    if not rep:
        return None, "not_provided"
    vals = {round(v, 3) for _, v in rep}
    if len({o for o, _ in rep}) >= 2 and len(vals) == 1:
        return vals.pop(), "cross_checked"
    return None, "single_source" if len(vals) == 1 else "mismatch"


# ───────────────────────── lệnh ─────────────────────────
def cmd_fetch(_a):
    try:
        print(json.dumps(parse_official(_fetch_official_html()), ensure_ascii=False))
        return 0
    except Refuse as e:
        print(f"REFUSE {e.outcome}: {e.detail}", file=sys.stderr)
        return 2


def cmd_verify(a):
    d = load_log()
    now = _now()
    try:
        official = parse_official(_fetch_official_html())
        sources, urls, owners = check_sources(a.sources, official, now.date())
        ev_date, ev_rate = _recorded_refi()
        if abs(official["refi_pct"] - ev_rate) > RATE_EPS_PP:
            msg = (f"🔴 LÃI TÁI CẤP VỐN NHNN ĐỔI? NHNN + {len(owners)} nguồn độc lập báo "
                   f"{official['refi_pct']}% ({official['refi_decision']}) nhưng SBV_REFI_EVENTS "
                   f"đang {ev_rate}% (từ {ev_date}). KHÔNG tự sửa — người duyệt cập nhật "
                   f"sbv_macro_overlay.py rồi chạy lại daily refresh. Nguồn: {OFFICIAL_URL} + "
                   f"{', '.join(urls)}")
            _notify(msg)
            raise Refuse("rate_change_detected", msg)
    except Exception as e:  # noqa: BLE001 — mọi kết cục không-verified đều phải để lại attempt
        if not isinstance(e, Refuse):
            e = Refuse("internal_error", repr(e))
        record_attempt(d, e.outcome, e.detail)
        save_log(d)
        print(f"REFUSE {e.outcome}: {e.detail}", file=sys.stderr)
        print(f"verified_at GIỮ NGUYÊN = {d.get('verified_at')}; attempted_at = {d['attempted_at']}")
        return 2
    omo_pct, omo_status = _omo(sources)
    at = now.isoformat(timespec="seconds")
    d["verified_at"] = at
    d["last_verified"] = now.date().isoformat()
    d["verified"] = {**official, "official_url": OFFICIAL_URL, "independent_owners": owners,
                     "independent_sources": sources, "omo_pct": omo_pct, "omo_status": omo_status,
                     "recorded_refi_event": [ev_date, ev_rate], "note": a.note or ""}
    record_attempt(d, "verified", f"refi={official['refi_pct']} rediscount="
                                  f"{official['rediscount_pct']} omo={omo_pct}({omo_status}) "
                                  f"NHNN+{owners}", at=at)
    save_log(d)
    _save_last_auto_urls(SIDECAR_PATH, now.date().isoformat(), urls)
    print(f"VERIFIED {at}: tái cấp vốn {official['refi_pct']}% | tái chiết khấu "
          f"{official['rediscount_pct']}% | OMO {omo_pct} ({omo_status}) | "
          f"{official['refi_decision']} | nguồn: NHNN + {owners}")
    return 0


def cmd_finalize(a):
    """Cuối wrapper Thứ Hai. (1) Không ai gọi verify từ run-start ⇒ ghi attempt (KHÔNG đẩy
    verified_at). (2) Lượt này không verified, hoặc verified_at > STALE_DAYS ⇒ ĐÚNG 1 dòng nhắc
    vào Trading Daily (chạy tuần 1 lần ⇒ không spam hằng ngày)."""
    d = load_log()
    start = datetime.strptime(a.run_start, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    att = d.get("attempted_at")
    if not att or datetime.fromisoformat(att) < start:
        record_attempt(d, "no_verify_call",
                       f"không có lần gọi verify nào từ {a.run_start} (dispatch_rc={a.dispatch_rc})")
        save_log(d)
    la = d.get("last_attempt") or {}
    va = d.get("verified_at")
    age = (_now() - datetime.fromisoformat(va)).days if va else None
    print(f"sbv_policy: verified_at={va} (age={age}d) attempted_at={d.get('attempted_at')} "
          f"last_outcome={la.get('outcome')}")
    stale = age is None or age > STALE_DAYS
    # rate_change_detected đã có cảnh báo 🔴 riêng lúc verify — không nhắc lần 2.
    if (la.get("outcome") == "verified" and not stale) or la.get("outcome") == "rate_change_detected":
        return 0
    ok = _notify(f"⚠️ Lãi điều hành NHNN: lượt kiểm tuần KHÔNG xác nhận được "
                 f"({la.get('outcome')}: {str(la.get('detail'))[:160]}). Kiểm thật cuối "
                 f"{va or 'CHƯA CÓ'} ({age if age is not None else '?'} ngày"
                 f"{', QUÁ ' + str(STALE_DAYS) + ' ngày — STALE' if stale else ''}). "
                 f"Xác nhận tay: {OFFICIAL_URL} (DT5G vẫn dùng SBV_REFI_EVENTS, không đổi).")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("fetch").set_defaults(fn=cmd_fetch)
    v = sp.add_parser("verify")
    v.add_argument("--sources", required=True,
                   help='[{"publisher","url","date":"YYYY-MM-DD","refi":4.5,"rediscount":3.0,"omo":4.0?}]')
    v.add_argument("--note", default="")
    v.set_defaults(fn=cmd_verify)
    f = sp.add_parser("finalize")
    f.add_argument("--run-start", required=True, help="UTC %%Y-%%m-%%dT%%H:%%M:%%SZ của wrapper")
    f.add_argument("--dispatch-rc", default="?")
    f.set_defaults(fn=cmd_finalize)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
