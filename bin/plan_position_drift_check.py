#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cờ "VỊ THẾ ĐỔI SAU KHI LẬP PLAN" — HƯỚNG NHẸ cho rủi ro Q5 (user duyệt 2026-10-04 09:40).

CHỈ CỜ / BÁO. KHÔNG chặn, KHÔNG sửa plan, KHÔNG đụng bot_execute/executor/exdate_gate.

Vì sao: DollarBill lập plan T+1 lúc ~19:06-19:09 ICT, đọc vị thế DNSE 19:03-19:15 — nằm GIỮA cửa
sổ broker credit corp-action (VPB 09-23 ~18:58, TPB 10-01 trước 19:03, BID 08-14 lô thứ hai
20:15). Không có bước đối chiếu lại sau đó, còn `exdate_gate` dùng lịch BQ đã chết từ 09-26
(NO_EVENT ⇒ fail-open im lặng). Hệ quả tiềm ẩn: lệnh mai dùng KL/giá ref/trần TRƯỚC sự kiện,
tỷ lệ sự kiện lớn (VPB ×1,26) ⇒ giá lệnh nằm ngoài biên độ, không khớp.

Cách kiểm (mỗi account, filter `account_no` ở MỌI lần đọc — §12):
  BÂY GIỜ   = đọc DNSE SỐNG (§6 bright-line: dữ liệu cùng ngày PHẢI từ DNSE, KHÔNG BQ). Bản đọc
              được ghi `_log_raw("positions")` như mọi script đọc broker — để lượt
              `corp_action_auto_confirm.py` 21:00 (đề xuất) thấy credit muộn sau 20:15.
  CƠ SỞ PLAN = bản ghi `positions` SỚM NHẤT của account trong `dnse_raw_<ngày>.jsonl` thuộc cửa sổ
              lập plan [18:50, 19:30] — mọi lần đọc broker (kể cả của DollarBill) đều tự log vào
              file này, nên bản sớm nhất ≈ lần đọc ĐẦU của plan. Plan JSON KHÔNG chứa snapshot vị
              thế (chỉ có tổng NAV) và bị viết lại 20:20-20:40 ⇒ mtime vô dụng làm mốc.
              Không có bản ghi trong cửa sổ ⇒ FALLBACK bản ghi cuối trước 19:30 (ghi rõ nguồn).
  CƠ SỞ PHIÊN = bản ghi cuối TRƯỚC cửa sổ (thường ~11:5x). So thêm với mốc này để bắt credit xảy
              ra SAU PHIÊN nhưng TRƯỚC/TRONG lúc lập plan (VPB 09-23, TPB 10-01): plan thấy KL mới
              nhưng giá ref của plan vẫn là giá đóng cửa CŨ ⇒ cùng rủi ro lệnh ngoài biên độ.
  Thay đổi KL được trừ phần KHỚP LỆNH thật giữa mốc và bây giờ (diff `fillQuantity` từ sổ lệnh);
  không loại trừ được ⇒ vẫn cờ, kèm ghi chú "chưa loại trừ được khớp lệnh" (không im lặng).

Đầu ra: KHÔNG có đường all-clear im lặng (bài học Q6). Mọi nhánh lỗi/thiếu dữ liệu ⇒ status
CANNOT_CHECK + dòng "KHÔNG KIỂM ĐƯỢC — <lý do thật>" (§29: lý do nội suy từ lỗi đang cầm).

Chạy:
  plan_position_drift_check.py --account SpaceX                 # cron 20:50 (đề xuất)
  plan_position_drift_check.py --account SpaceX --report-block  # send_plan_report 21:00/23:00: kiểm
        # lại NGAY (tươi hơn 20:50); lần này hỏng mà lần trước kiểm được ⇒ in cả hai kết quả
  plan_position_drift_check.py --account SpaceX --date 2026-08-14 --sim-live-at 20:50 --no-bus --no-state
        # REPLAY: "bây giờ" = bản ghi dnse_raw cuối ≤ giờ đó (in rõ là MÔ PHỎNG)
rc: 0 = NO_DRIFT/DRIFT/SKIP (đã kiểm), 2 = CANNOT_CHECK, 3 = sai tham số/môi trường.
State: mike/state/plan_position_drift/<account>_<ngày>.json (atomic). Bus: `finding`
plan-position-drift-<account>-<ngày> khi DRIFT, `error` …-cannot-check-… khi không kiểm được —
mỗi nội dung 1 lần/ngày (post rồi mới đánh dấu: kill giữa chừng ⇒ có thể gửi trùng 1 lần, chọn
trùng thay vì mất cảnh báo).
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MIKE_BIN)
import wc_paths  # noqa: E402

WC_ROOT = wc_paths.find_wc_root(__file__)
sys.path.insert(0, WC_ROOT)
from trading_bot.vn_market import is_holiday, next_trading_day  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
PLAN_WIN_START = "18:50:00"   # DollarBill pipeline khởi động 19:00; chừa 10' cho EOD/park đọc sớm
PLAN_WIN_END = "19:30:00"
POST_CLOSE = "14:46:00"       # sau ATC HOSE 14:45 không còn khớp lệnh thường
BATCH_FRESH_FROM = "15:00:00"  # lô có modifiedDate (ICT) ≥ mốc này HÔM NAY = đã qua batch cuối ngày DNSE
PX_THR_FRESH = 0.01           # cả 2 bản đều sau batch: giá phải đứng yên; đo VPB 09-23 19:30→19:40 22100→22050 (0,23%)
PX_THR_STALE = 0.15           # mốc TRƯỚC batch: giá là của phiên trước ⇒ chỉ bắt đổi > biên độ rộng nhất (UPCOM ±15%)
BUS_TIMEOUT_S = 30

_PROD_EXEC = os.path.join(WC_ROOT, "data", "execution_logs")
_PROD_PLAN = os.path.join(WC_ROOT, "data", "trade_plans")
_PROD_STATE = os.path.join(WC_ROOT, "mike", "state", "plan_position_drift")
_PROD_APPEND = os.path.join(WC_ROOT, "mike", "bin", "append_event.sh")
_OVERRIDES = {"MIKE_DRIFT_EXEC_DIR": _PROD_EXEC, "MIKE_DRIFT_PLAN_DIR": _PROD_PLAN,
              "MIKE_DRIFT_STATE_DIR": _PROD_STATE, "MIKE_DRIFT_APPEND_EVENT": _PROD_APPEND}


class EnvError(Exception):
    pass


def paths():
    """Thư mục thật, hoặc sandbox khi selfcheck. Biến override thiếu MIKE_DRIFT_SELFCHECK=1 ⇒ TỪ
    CHỐI (một biến sót lại không được lặng lẽ chuyển hướng cron thật). Selfcheck mà trỏ state/
    append_event vào chỗ thật ⇒ TỪ CHỐI (test không được ghi dữ liệu production)."""
    set_ = {k: os.environ[k] for k in _OVERRIDES if os.environ.get(k)}
    sc = os.environ.get("MIKE_DRIFT_SELFCHECK") == "1"
    if set_ and not sc:
        raise EnvError(f"biến {sorted(set_)} chỉ dùng cho selfcheck (thiếu MIKE_DRIFT_SELFCHECK=1)")
    out = {k: os.path.abspath(set_.get(k, v)) for k, v in _OVERRIDES.items()}
    if sc:
        for k in ("MIKE_DRIFT_STATE_DIR", "MIKE_DRIFT_APPEND_EVENT"):
            if os.path.realpath(out[k]) == os.path.realpath(_OVERRIDES[k]):
                raise EnvError(f"selfcheck mà {k} trỏ vào production ({out[k]})")
    return out


def now_ict():
    return dt.datetime.now(ICT).replace(tzinfo=None)


def account_no_of(label):
    path = os.path.join(WC_ROOT, "secrets", "trading_bot_accounts.json")
    with open(path, encoding="utf-8") as f:
        accounts = json.load(f).get("accounts", [])
    for a in accounts:
        if a.get("label") == label and a.get("account_id"):
            return str(a["account_id"])
    return None


# ── đọc dnse_raw ────────────────────────────────────────────────────────────────────────────
def load_raw(exec_dir, date_str, account_no):
    """→ (positions [(ts, rows)], orders [(ts, orders)], n_bad). ts = 'YYYY-MM-DDTHH:MM:SS' ICT."""
    path = os.path.join(exec_dir, f"dnse_raw_{date_str}.jsonl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"không có {path}")
    pos, ords, bad = [], [], 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                bad += 1
                continue
            if str(rec.get("account_no")) != str(account_no):   # §12 — dòng đầu tiên
                continue
            ts = str(rec.get("ts") or "")[:19]
            if not ts.startswith(date_str):
                continue
            payload = rec.get("payload")
            if rec.get("kind") == "positions":
                rows = payload.get("positions") if isinstance(payload, dict) else None
                if isinstance(rows, list):
                    pos.append((ts, rows))
                else:
                    bad += 1
            elif rec.get("kind") == "orders":
                rows = payload.get("orders") if isinstance(payload, dict) else None
                if isinstance(rows, list):
                    ords.append((ts, rows))
    pos.sort(key=lambda x: x[0])
    ords.sort(key=lambda x: x[0])
    return pos, ords, bad


def _hms(ts):
    return ts[11:19]


def pick_baselines(pos):
    """→ (plan_base, session_base, nguồn). plan_base = bản SỚM NHẤT trong [18:50,19:30]; không có ⇒
    FALLBACK bản cuối trước 19:30. session_base = bản cuối TRƯỚC 18:50 (có thể None)."""
    in_win = [p for p in pos if PLAN_WIN_START <= _hms(p[0]) <= PLAN_WIN_END]
    before = [p for p in pos if _hms(p[0]) < PLAN_WIN_START]
    session = before[-1] if before else None
    if in_win:
        return in_win[0], session, (f"bản đọc DNSE đầu tiên trong cửa sổ lập plan "
                                    f"({_hms(in_win[0][0])[:5]})")
    if session:
        return session, None, (f"FALLBACK dnse_raw cuối trước 19:30 ({_hms(session[0])[:5]}) — "
                               f"không có bản đọc nào trong cửa sổ lập plan 18:50–19:30")
    return None, None, ""


def aggregate(rows, date_str):
    """{mã: {"qty": Σ openQuantity, "px": [marketPrice khác nhau], "fresh": bool}} — bỏ dòng
    CLOSED / qty≤0. `fresh` = MỌI lô của mã có modifiedDate (ICT) ≥ 15:00 hôm nay.
    Vì sao cần `fresh` (đo 60 phiên 08-01→10-02): `marketPrice` của positions KHÔNG đổi trong
    phiên — nó chỉ đổi khi DNSE chạy batch cuối ngày (18:52→20:15 tuỳ ngày), batch đó cập nhật
    modifiedDate của MỌI lô VÀ là lúc credit corp-action xuất hiện. Mốc trước batch mang giá của
    phiên TRƯỚC ⇒ so giá chặt với nó báo nhầm cả danh mục (replay 08-14: 14/14 mã "đổi giá").
    Giữ TẬP giá theo từng lô (không gộp 1 giá): đọc lẫn hệ giá giữa các gói vay chính là dấu
    hiệu credit đang dở (BID 08-14 19:10: lô 1826 @35.800, lô 1258 @38.850)."""
    out = {}
    for r in rows:
        if not isinstance(r, dict) or str(r.get("status") or "OPEN").upper() == "CLOSED":
            continue
        sym = r.get("symbol")
        try:
            q = int(float(r.get("openQuantity") or 0))
        except (TypeError, ValueError):
            q = 0
        if not sym or q <= 0:
            continue
        a = out.setdefault(sym, {"qty": 0, "px": [], "fresh": True})
        a["qty"] += q
        mod = _utc_z_to_ict(r.get("modifiedDate"))
        if not (mod and mod >= f"{date_str}T{BATCH_FRESH_FROM}"):
            a["fresh"] = False
        try:
            mp = float(r.get("marketPrice"))
        except (TypeError, ValueError):
            mp = None
        if mp and mp > 0 and mp not in a["px"]:
            a["px"].append(mp)
    for a in out.values():
        a["px"].sort()
    return out


def _utc_z_to_ict(s):
    """'2026-10-01T07:04:33.367799247Z' (UTC, DNSE) → '2026-10-01T14:04:33' ICT. Hỏng ⇒ None.
    Cắt 19 ký tự trước khi parse: fromisoformat của 3.10 không nhận phần lẻ 9 chữ số."""
    try:
        t = dt.datetime.strptime(str(s)[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None
    return t.astimezone(ICT).replace(tzinfo=None).isoformat(timespec="seconds")


def explained_fills(base_ts, ord_snaps, final_orders):
    """Thay đổi KL GIẢI THÍCH ĐƯỢC bởi khớp lệnh giữa mốc `base_ts` và bây giờ.
    → ({mã: Δqty có dấu}, {mã chưa loại trừ được; "*" = mọi mã}).
    fill tại mốc = bản ghi orders cuối ≤ mốc; lệnh không có trong bản đó mà tạo SAU mốc ⇒ 0;
    tạo TRƯỚC mốc (hoặc không rõ) mà có khớp ⇒ không loại trừ chắc được ⇒ đánh dấu, KHÔNG nuốt."""
    if _hms(base_ts) >= POST_CLOSE:
        return {}, set()              # mốc sau đóng cửa: không còn khớp lệnh nào sau đó
    if final_orders is None:
        return {}, {"*"}
    base = None
    for ts, rows in ord_snaps:
        if ts <= base_ts:
            base = rows
    base_fill = {str(o.get("id")): float(o.get("fillQuantity") or 0)
                 for o in (base or []) if isinstance(o, dict)}
    delta, unsure = {}, set()
    for o in final_orders:
        if not isinstance(o, dict):
            continue
        sym, oid = o.get("symbol"), str(o.get("id"))
        ff = float(o.get("fillQuantity") or 0)
        if oid in base_fill:
            fb = base_fill[oid]
        else:
            fb = 0.0
            created = _utc_z_to_ict(o.get("createdDate"))
            if ff and not (created and created > base_ts):
                unsure.add(sym)
        sign = 1 if str(o.get("side", "")).upper() in ("NB", "B", "BUY") else -1
        if ff != fb:
            delta[sym] = delta.get(sym, 0) + sign * (ff - fb)
    return delta, unsure


def _px_dev(px_b, px_n):
    if not px_b or not px_n:
        return None
    return max(abs(n / b - 1) for n in px_n for b in px_b)


def compare(base, now, explained, unsure):
    items = []
    for sym in sorted(set(base) | set(now)):
        b = base.get(sym, {"qty": 0, "px": []})
        n = now.get(sym, {"qty": 0, "px": []})
        exp = int(round(explained.get(sym, 0)))
        unexpl = n["qty"] - b["qty"] - exp
        dev = _px_dev(b["px"], n["px"])
        px_thr = PX_THR_FRESH if (b.get("fresh") and n.get("fresh")) else PX_THR_STALE
        mixed = len(n["px"]) > 1 and (n["px"][-1] / n["px"][0] - 1) > PX_THR_FRESH
        qty_flag = unexpl != 0
        px_flag = dev is not None and dev > px_thr
        if not (qty_flag or px_flag or mixed):
            continue
        items.append({"ticker": sym, "qty_before": b["qty"], "qty_after": n["qty"],
                      "qty_explained_by_fills": exp, "qty_unexplained": unexpl,
                      "ratio": (round(n["qty"] / b["qty"], 4) if b["qty"] else None),
                      "px_before": b["px"], "px_after": n["px"],
                      "px_dev": (round(dev, 4) if dev is not None else None),
                      "qty_flag": qty_flag, "px_flag": px_flag, "px_thr": px_thr,
                      "mixed_frame_now": mixed,
                      "fills_unsure": bool(qty_flag and (sym in unsure or "*" in unsure))})
    return items


def plan_orders_for(plan_dir, account, date_str):
    """{mã: [lệnh]} của plan T+1 (để gợi ý hành động). Lỗi đọc ⇒ (None, lý do)."""
    try:
        t1 = next_trading_day(dt.date.fromisoformat(date_str)).isoformat()
    except ValueError as e:
        return None, f"ngày sai ({e})"
    path = os.path.join(plan_dir, f"plan_{account}_{t1}.json")
    try:
        with open(path, encoding="utf-8") as f:
            plan = json.load(f)
    except FileNotFoundError:
        return None, f"chưa thấy plan_{account}_{t1}.json"
    except (OSError, json.JSONDecodeError) as e:
        return None, f"không đọc được plan_{account}_{t1}.json ({type(e).__name__}: {e})"
    out = {}
    for o in (plan.get("orders") or []):
        if isinstance(o, dict) and o.get("ticker"):
            out.setdefault(str(o["ticker"]).upper(), []).append(o)
    return out, ""


# ── đọc DNSE sống ───────────────────────────────────────────────────────────────────────────
def live_read(account_no, label):
    """(positions payload, orders list) từ DNSE SỐNG. Ghi `positions` vào dnse_raw như mọi script
    đọc broker (corp_action_auto_confirm lượt 21:00 cần bản ghi sau credit muộn). Lỗi ⇒ ném."""
    from trading_bot.brokers import DNSEBroker
    b = DNSEBroker(account_id=account_no, credentials_file=None, label=label)
    b.connect()
    pos = b.client.positions(account_no)
    b._log_raw("positions", pos)
    try:
        ords = b.client.orders(account_no)
        ords = ords.get("orders") if isinstance(ords, dict) else ords
        ords = ords if isinstance(ords, list) else None
    except Exception as e:   # sổ lệnh lỗi KHÔNG chặn kiểm KL; chỉ mất phần loại trừ khớp lệnh
        print(f"  ⚠ đọc sổ lệnh DNSE lỗi ({type(e).__name__}: {e}) — không loại trừ được khớp lệnh",
              file=sys.stderr)
        ords = None
    return pos, ords


def sim_read(pos, ords, sim_at):
    """REPLAY: 'bây giờ' = bản ghi positions cuối ≤ sim_at; sổ lệnh = bản cuối trong file."""
    cand = [p for p in pos if _hms(p[0]) <= sim_at]
    if not cand:
        raise LookupError(f"không có bản ghi positions nào ≤ {sim_at} để mô phỏng")
    ts, rows = cand[-1]
    final = ords[-1][1] if ords else None
    return {"positions": rows}, final, ts


# ── lõi ─────────────────────────────────────────────────────────────────────────────────────
def run_check(account, account_no, date_str, P, sim_at=None, now=None):
    now = now or now_ict()
    res = {"account": account, "account_no": account_no, "date": date_str,
           "checked_at": now.isoformat(timespec="seconds"), "status": None, "reason": "",
           "baseline_source": "", "now_source": "", "items": [], "notes": []}
    if sim_at:
        res["checked_at"] = f"{date_str}T{sim_at}"

    def cannot(why):
        res["status"], res["reason"] = "CANNOT_CHECK", why
        return res

    d = dt.date.fromisoformat(date_str)
    if d.weekday() >= 5 or is_holiday(d):
        res["status"], res["reason"] = "SKIP", "không phải ngày giao dịch"
        return res
    if not account_no:
        return cannot(f"không tìm thấy account_no của {account}")
    try:
        pos, ords, bad = load_raw(P["MIKE_DRIFT_EXEC_DIR"], date_str, account_no)
    except (OSError, FileNotFoundError) as e:
        return cannot(f"không đọc được dnse_raw hôm nay ({e})")
    if bad:
        res["notes"].append(f"{bad} dòng dnse_raw hỏng bị bỏ qua")
    plan_base, sess_base, src = pick_baselines(pos)
    if not plan_base:
        return cannot("không có cơ sở: chưa có bản ghi vị thế DNSE nào của account trước 19:30 "
                      "trong dnse_raw hôm nay")
    res["baseline_source"] = f"{src} [dnse_raw_{date_str}.jsonl]"
    res["baseline_ts"] = plan_base[0]
    if not sim_at and now.date().isoformat() != date_str:
        return cannot(f"đọc sống hôm nay {now.date()} ≠ ngày kiểm {date_str} — dùng --sim-live-at "
                      f"để replay ngày cũ")

    try:
        if sim_at:
            payload, final_orders, now_ts = sim_read(pos, ords, sim_at)
            res["now_source"] = (f"MÔ PHỎNG từ bản ghi dnse_raw {_hms(now_ts)} (không có bản đọc "
                                 f"sống lúc {sim_at})")
        else:
            payload, final_orders = live_read(account_no, account)
            now_ts = res["checked_at"]
            res["now_source"] = f"DNSE sống {_hms(now_ts)[:5]}"
    except Exception as e:
        return cannot(f"đọc DNSE lỗi ({type(e).__name__}: {str(e)[:200]})")
    if sim_at and now_ts <= plan_base[0]:
        return cannot(f"mô phỏng: không có bản ghi vị thế nào SAU mốc cơ sở {_hms(plan_base[0])} "
                      f"(bản cuối ≤ {sim_at[:5]} là {_hms(now_ts)})")
    if final_orders is not None:
        # Chỉ lệnh của CHÍNH ngày kiểm. Sổ lệnh rỗng KHÔNG phải bằng chứng "không khớp gì" (chưa
        # đo được DNSE trả gì lúc tối) ⇒ lùi về bản orders cuối trong dnse_raw, không có ⇒ None
        # (mọi thay đổi KL trước đóng cửa bị gắn "chưa loại trừ được khớp lệnh", vẫn cờ).
        final_orders = [o for o in final_orders if isinstance(o, dict)
                        and str(o.get("transDate") or date_str)[:10] == date_str]
        if not final_orders:
            final_orders = ords[-1][1] if ords else None
            if final_orders is not None:
                res["notes"].append(f"sổ lệnh DNSE lúc kiểm rỗng — dùng bản orders cuối trong "
                                    f"dnse_raw ({_hms(ords[-1][0])[:5]})")
    rows = payload.get("positions") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return cannot(f"DNSE trả payload vị thế sai dạng ({type(payload).__name__}: "
                      f"{str(payload)[:120]})")
    if sim_at:
        res["checked_at"] = now_ts
    now_agg = aggregate(rows, date_str)
    base_agg = aggregate(plan_base[1], date_str)
    if base_agg and not now_agg:
        return cannot(f"DNSE trả danh mục RỖNG trong khi cơ sở có {len(base_agg)} mã — nghi bản đọc "
                      f"lỗi, không kết luận")
    n_stale = sum(1 for v in now_agg.values() if not v["fresh"])

    seen = set()
    for kind, base in (("SAU_PLAN", plan_base), ("SAU_PHIEN", sess_base)):
        if base is None:
            continue
        exp, unsure = explained_fills(base[0], ords, final_orders)
        for it in compare(aggregate(base[1], date_str), now_agg, exp, unsure):
            if it["ticker"] in seen:
                continue
            seen.add(it["ticker"])
            it["kind"], it["base_ts"] = kind, base[0]
            res["items"].append(it)

    orders_map, why = plan_orders_for(P["MIKE_DRIFT_PLAN_DIR"], account, date_str)
    for it in res["items"]:
        it["plan_orders"] = ([{k: o.get(k) for k in ("side", "qty", "ref_price", "limit_price")}
                              for o in (orders_map or {}).get(it["ticker"].upper(), [])]
                             if orders_map is not None else None)
    if orders_map is None and res["items"]:
        res["notes"].append(f"không đối chiếu được lệnh plan: {why}")
    if n_stale:
        # Batch cuối ngày DNSE CHƯA chạy (xong) cho n_stale mã ⇒ credit của các mã đó có thể CHƯA
        # tới. Không được thành "không đổi" (Q6): có cờ ⇒ DRIFT kèm ghi chú; không cờ ⇒ CANNOT_CHECK.
        why = (f"DNSE chưa chạy xong cập nhật vị thế cuối ngày ({n_stale}/{len(now_agg)} mã còn "
               f"modifiedDate trước 15:00 hôm nay) — credit corp-action có thể CHƯA tới")
        if not res["items"]:
            return cannot(why + ", chưa kết luận được")
        res["notes"].append(why)
    res["status"] = "DRIFT" if res["items"] else "NO_DRIFT"
    return res


# ── render ──────────────────────────────────────────────────────────────────────────────────
def _n(x):
    return f"{int(round(x)):,}".replace(",", ".")


def _px(lst):
    return "/".join(_n(p) for p in lst) if lst else "?"


def render(res):
    st = res.get("status")
    hm = str(res.get("checked_at", ""))[11:16]
    acct = res.get("account")
    if st == "SKIP":
        return [f"ℹ️ Kiểm vị thế sau plan ({acct}): bỏ qua — {res.get('reason')}"]
    if st == "CANNOT_CHECK":
        return [f"⚠️ **Vị thế sau plan ({acct}): KHÔNG KIỂM ĐƯỢC** (kiểm {hm}) — {res.get('reason')}. "
                f"Tự xem vị thế DNSE các mã có sự kiện quyền trước khi duyệt."]
    if st == "NO_DRIFT":
        fb = " FALLBACK" if "FALLBACK" in str(res.get("baseline_source")) else ""
        sim = " — MÔ PHỎNG" if "MÔ PHỎNG" in str(res.get("now_source")) else ""
        return [f"✅ Vị thế không đổi sau plan (kiểm {hm}, mốc{fb} "
                f"{_hms(str(res.get('baseline_ts', '')))[:5]}{sim})"]
    if st != "DRIFT":
        return [f"⚠️ **Vị thế sau plan ({acct}): KHÔNG KIỂM ĐƯỢC** — trạng thái lạ {st!r}"]
    out = [f"⚠️ **VỊ THẾ ĐỔI SAU KHI LẬP PLAN (nghi corp-action credit muộn)** — tài khoản "
           f"{acct} {res.get('account_no')} (kiểm {hm}; {res.get('now_source')})"]
    for it in res["items"]:
        when = ("sau lần đọc đầu của plan" if it["kind"] == "SAU_PLAN"
                else "sau phiên, TRƯỚC/TRONG lúc lập plan")
        q = f"KL {_n(it['qty_before'])}→{_n(it['qty_after'])}"
        if it.get("ratio") and it["qty_before"] != it["qty_after"]:
            q += f" (×{it['ratio']:.4f})".replace(".", ",")
        if it.get("qty_explained_by_fills"):
            q += f", trong đó khớp lệnh {it['qty_explained_by_fills']:+d}"
        p = f"giá {_px(it['px_before'])}→{_px(it['px_after'])}"
        if it.get("px_dev") is not None:
            p += f" ({it['px_dev'] * 100:.1f}%)".replace(".", ",")
        extra = []
        if it.get("mixed_frame_now"):
            extra.append("đang lẫn 2 hệ giá giữa các lô — credit có thể CHƯA xong")
        if it.get("fills_unsure"):
            extra.append("chưa loại trừ được khớp lệnh trong phiên"
                         + (" — KL GIẢM: nhiều khả năng do BÁN (kể cả bán tay), không phải credit"
                            if it["qty_after"] < it["qty_before"] else ""))
        po = it.get("plan_orders")
        if po:
            act = "; ".join(f"{str(o.get('side')).upper()} {o.get('qty')}cp @"
                            f"{_n(o.get('limit_price') or o.get('ref_price') or 0)}" for o in po)
            extra.append(f"plan có lệnh {act} ⇒ XEM LẠI KL/giá/trần lệnh này")
        elif po is not None:
            extra.append("plan không có lệnh mã này — đối chiếu sổ lô/NAV")
        out.append(f"   • {it['ticker']} [{when}, mốc {_hms(it['base_ts'])[:5]}]: {q}; {p}"
                   + (f" — {'; '.join(extra)}" if extra else ""))
    out.append("   👉 Plan có thể dùng KL/giá ref/trần TRƯỚC sự kiện ⇒ lệnh có thể ngoài biên độ, "
               "không khớp. Xem lại lệnh các mã trên trước khi duyệt (cờ báo, KHÔNG tự chặn).")
    for nt in res.get("notes") or []:
        out.append(f"   · {nt}")
    return out


# ── state + bus ─────────────────────────────────────────────────────────────────────────────
def _state_path(P, account, date_str):
    return os.path.join(P["MIKE_DRIFT_STATE_DIR"], f"{account}_{date_str}.json")


def read_state(P, account, date_str):
    try:
        with open(_state_path(P, account, date_str), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def write_state(P, account, date_str, st):
    os.makedirs(P["MIKE_DRIFT_STATE_DIR"], exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=P["MIKE_DRIFT_STATE_DIR"], suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, _state_path(P, account, date_str))


def content_hash(res):
    key = [res.get("status"), res.get("reason") if res.get("status") == "CANNOT_CHECK" else ""]
    key += [(i["ticker"], i["kind"], i["qty_before"], i["qty_after"], i["px_before"], i["px_after"])
            for i in res.get("items") or []]
    return hashlib.md5(json.dumps(key, default=str).encode()).hexdigest()


def post_bus(P, res, lines):
    acct, d = res["account"], res["date"]
    if res["status"] == "DRIFT":
        kind, topic = "finding", f"plan-position-drift-{acct}-{d}"
    else:
        kind, topic = "error", f"plan-position-drift-cannot-check-{acct}-{d}"
    payload = {"account": acct, "account_no": res.get("account_no"), "date": d,
               "status": res["status"], "reason": res.get("reason"),
               "baseline_source": res.get("baseline_source"), "now_source": res.get("now_source"),
               "items": [{k: i.get(k) for k in ("ticker", "kind", "qty_before", "qty_after",
                                                 "ratio", "px_before", "px_after", "plan_orders")}
                         for i in res.get("items") or []],
               "report_lines": lines, "mode": "CHỈ CỜ — không chặn lệnh"}
    try:
        r = subprocess.run([P["MIKE_DRIFT_APPEND_EVENT"], "Mike", kind, topic,
                            json.dumps(payload, ensure_ascii=False, default=str)],
                           capture_output=True, text=True, timeout=BUS_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"  ❌ append_event {kind} {topic} lỗi: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    if r.returncode != 0:
        print(f"  ❌ append_event {kind} {topic} rc={r.returncode}: "
              f"{(r.stderr or r.stdout or '').strip()[:300]}", file=sys.stderr)
    return r.returncode


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--account", required=True)
    ap.add_argument("--account-no", default=None, help="override (mặc định đọc secrets)")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD (mặc định hôm nay ICT)")
    ap.add_argument("--sim-live-at", default=None, help="HH:MM — REPLAY từ dnse_raw, không gọi DNSE")
    ap.add_argument("--report-block", action="store_true",
                    help="cho send_plan_report: kiểm lại ngay; hỏng mà lần trước kiểm được ⇒ in cả hai")
    ap.add_argument("--no-bus", action="store_true")
    ap.add_argument("--no-state", action="store_true")
    a = ap.parse_args(argv)
    try:
        P = paths()
    except EnvError as e:
        print(f"⚠️ **Vị thế sau plan ({a.account}): KHÔNG KIỂM ĐƯỢC** — môi trường sai: {e}")
        return 3
    date_str = a.date or now_ict().date().isoformat()
    sim_at = (a.sim_live_at + ":59")[:8] if a.sim_live_at else None

    prev = None if a.no_state else read_state(P, a.account, date_str)

    try:
        acct_no = a.account_no or account_no_of(a.account)
    except (OSError, json.JSONDecodeError) as e:
        acct_no = None
        print(f"  ⚠ đọc secrets lỗi: {type(e).__name__}: {e}", file=sys.stderr)
    try:
        res = run_check(a.account, acct_no, date_str, P, sim_at=sim_at)
    except Exception as e:                      # không có đường all-clear im lặng (bài học Q6)
        res = {"account": a.account, "account_no": acct_no, "date": date_str,
               "checked_at": now_ict().isoformat(timespec="seconds"), "status": "CANNOT_CHECK",
               "reason": f"script lỗi ({type(e).__name__}: {str(e)[:200]})", "items": []}
    lines = render(res)
    pres = (prev or {}).get("result") or {}
    if (a.report_block and res["status"] == "CANNOT_CHECK"
            and pres.get("status") in ("DRIFT", "NO_DRIFT")):
        # Lần kiểm này hỏng nhưng lần trước (20:50) kiểm ĐƯỢC ⇒ hiện cả hai, không chọn im lặng.
        lines = lines + [f"   · kết quả lần kiểm trước ({str(pres.get('checked_at'))[11:16]}):"] + [
            "     " + x for x in render(pres)]
    print("\n".join(lines))

    if not a.no_state:
        st = {"result": res, "lines": lines,
              "bus_posted_hash": (prev or {}).get("bus_posted_hash")}
        h = content_hash(res)
        if res["status"] in ("DRIFT", "CANNOT_CHECK") and not a.no_bus and st["bus_posted_hash"] != h:
            if post_bus(P, res, lines) == 0:
                st["bus_posted_hash"] = h
        try:
            write_state(P, a.account, date_str, st)
        except OSError as e:
            print(f"  ⚠ ghi state lỗi: {type(e).__name__}: {e}", file=sys.stderr)
    elif res["status"] in ("DRIFT", "CANNOT_CHECK") and not a.no_bus:
        post_bus(P, res, lines)
    return 2 if res["status"] == "CANNOT_CHECK" else 0


if __name__ == "__main__":
    sys.exit(main())
