#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nhận diện sự kiện doanh nghiệp LÀM TĂNG SỐ LƯỢNG chỉ từ BROKER (DNSE) — đường lùi khi feed
vendor `tav2_bq.corporate_action` đứng/thiếu ngày.

VÌ SAO CÓ FILE NÀY
------------------
`corp_action_auto_confirm.py` đòi NGUỒN 1 = lịch vendor (`upcoming_events_held`). Feed vendor chết
từ 2026-09-26 ⇒ ca TPB 2026-10-01 (ISS 15% + DIV 500đ) không được tự xác nhận, sổ lô lệch 200 vs
230, park-trim/active_nav bị chặn tới khi user ghi tay `data/corp_actions.json`. User duyệt
2026-10-01 (memory `feedback-broker-as-corp-action-source`) và 2026-10-03 (phương án B, tự động
hoá): broker là nguồn xác định khi vendor đứng.

⚠️ `corp_actions.py` ghi "KHÔNG BAO GIỜ tự suy corp action từ việc thấy qty lệch" — một lệnh bị
bỏ sót khỏi journal, GHOST_ORDER hay chuyển khoản chứng khoán cũng làm KL lệch. Module này KHÔNG
suy từ KL lệch. Nó đòi BA đại lượng broker ghi ĐỘC LẬP nhau cùng kể một câu chuyện, và mỗi đại
lượng loại được một lớp giả mạo khác nhau:

  (1) KHỐI LƯỢNG `openQuantity` tăng, `closedQuantity` đứng yên (không bán), `tradeQuantity`
      đứng yên (CP mới chưa được bán — đúng mẫu credit quyền, 8/8 ca thật), `accumulateQuantity`
      tăng ĐÚNG bằng phần tăng KL.
  (2) TỔNG GIÁ VỐN `Σ openQuantity × costPrice` KHÔNG TĂNG. Mua (kể cả lệnh ma ngoài journal) và
      chuyển khoản vào LUÔN làm tổng giá vốn tăng ⇒ bị loại ngay ở bước lọc ứng viên. Phần giảm
      (nếu có) chia cho KL trước sự kiện = chân cổ tức tiền mặt đi kèm (TPB: đúng 500đ/cp).
  (3) GIÁ `marketPrice` đêm đó = (giá đóng cửa cum − chân tiền) / hệ số — giá tham chiếu sở công
      bố cho phiên GDKHQ. Kiểm bằng CHÍNH `exdate_frame.verify_post_event_price` (dung sai
      200đ/0,5%) mà park_holdings/compute_active_nav đang dùng — không có phép thử thứ hai.
  + Hệ số KL suy từ (1) và hệ số giá suy từ (3) PHẢI giao nhau; mọi tài khoản đang giữ mã PHẢI
    cùng được credit và cho cùng chân tiền, cùng giá; trạng thái sau credit PHẢI đứng yên qua
    ≥ 2 bản ghi; mọi lô (loan package) phải đổi đồng thời (DNSE điều chỉnh KHÔNG NGUYÊN TỬ theo
    gói vay — BID 2026-08-14, `price_frame.py` §G4).

EX-DATE — KHÔNG đoán. Bằng chứng duy nhất được dùng: broker credit VÀ hạ giá tham chiếu trong cửa
sổ SAU GIỜ ĐÓNG CỬA (≥ 15:00 ICT) của phiên D ⇒ sở đã công bố giá tham chiếu điều chỉnh cho phiên
KẾ TIẾP ⇒ ex_date = `next_trading_day(D)`. Credit ngoài cửa sổ đó (giữa phiên, sau nửa đêm) ⇒
không có bằng chứng ex-date ⇒ MƠ HỒ, không ghi. 8/8 sự kiện thật trong registry khớp mẫu này.

Fail-closed: bất kỳ điều kiện nào hỏng ⇒ AMBIGUOUS (không ghi, caller escalate). Thiếu dữ liệu
(chưa đủ bản ghi, không có giá cum) ⇒ INSUFFICIENT (không ghi). Hàm phát hiện là PURE: nhận
chuỗi bản ghi đã đọc + giá cum, không gọi mạng, không đọc TZ host.

CLI (chỉ ĐỌC, không ghi gì):
    python3 mike/bin/corp_action_broker_detect.py --replay 2026-08-01 2026-10-02
"""
import argparse
import datetime as dt
import glob
import json
import math
import os
import sys
from zoneinfo import ZoneInfo

MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MIKE_BIN)
import wc_paths  # noqa: E402

WC_ROOT = wc_paths.find_wc_root(__file__)
if WC_ROOT not in sys.path:
    sys.path.append(WC_ROOT)                      # trading_bot.vn_market — CUỐI, không shadow bin/
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
LEDGER_FILE = os.path.join(WC_ROOT, "data", "corp_action_broker_ledger.jsonl")

ICT = ZoneInfo("Asia/Ho_Chi_Minh")

# Credit quyền + hạ giá tham chiếu chỉ được tin là "cho phiên kế tiếp" khi xảy ra SAU giờ đóng cửa.
# 8/8 ca thật: 18:45–19:00 ICT. 15:00 = hết ATC HOSE; không nới về giữa phiên.
CREDIT_WINDOW_START = dt.time(15, 0)
MIN_POST_SNAPSHOTS = 2       # trạng thái sau credit phải lặp lại ≥ 2 bản ghi (không phải 1 lần đọc)
CASH_TOL_VND = 0.5           # sai số làm tròn costPrice (4 chữ số thập phân) quy về đ/cp
CASH_LEG_MIN_VND = 1.0       # |chân tiền| < 1đ/cp ⇒ coi như không có chân tiền
MAX_DECIMALS = 7             # vendor ghi tỉ lệ 7 chữ số (VPB 0,2604104)

# Verdict
NOT_CANDIDATE = "NOT_CANDIDATE"   # không có hình dạng credit (không tăng KL, hoặc tổng giá vốn TĂNG)
CONFIRMABLE = "CONFIRMABLE"
AMBIGUOUS = "AMBIGUOUS"
INSUFFICIENT = "INSUFFICIENT"
DEFER_VENDOR = "DEFER_VENDOR"     # lịch vendor có sự kiện cổ phiếu cho mã này ⇒ nhánh vendor quyết


# ───────────────────────────────────────────────────────────────────────────── đọc dnse_raw ──

def _f(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    return v if math.isfinite(v) else 0.0


def modified_ict(md):
    """`modifiedDate` DNSE (UTC, hậu tố Z, tới nano giây) → datetime ICT; None nếu không parse."""
    s = str(md or "").strip()
    if not s:
        return None
    s = s.replace("Z", "")
    if "." in s:                                   # cắt nano giây về micro giây
        head, frac = s.split(".", 1)              # 3.10 fromisoformat chỉ nhận 3/6 chữ số:
        s = f"{head}.{(frac + '000000')[:6]}"      # VIB 2026-09-09 '…22.23138Z' (5 chữ số)
    try:
        t = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t.astimezone(ICT)


def aggregate(rows):
    """Gộp các lô (loan package) của MỘT mã trong MỘT bản ghi positions."""
    live = [r for r in rows if _f(r.get("openQuantity")) > 0]
    return {
        "qty": sum(_f(r.get("openQuantity")) for r in rows),
        "trade": sum(_f(r.get("tradeQuantity")) for r in rows),
        "closed": sum(_f(r.get("closedQuantity")) for r in rows),
        "accum": sum(_f(r.get("accumulateQuantity")) for r in rows),
        "cost": sum(_f(r.get("openQuantity")) * _f(r.get("costPrice")) for r in rows),
        "mkts": sorted({_f(r.get("marketPrice")) for r in live}),
        "mods": [str(r.get("modifiedDate") or "") for r in live],
        "lots": {str(r.get("id")): (_f(r.get("openQuantity")), _f(r.get("costPrice")))
                 for r in rows},
    }


def read_series(path, account_no):
    """[(ts, {sym: [rows]})] theo thời gian, CHỈ bản ghi positions của ĐÚNG account (§12).
    Bản ghi positions rỗng bị bỏ (lần đọc hỏng ≠ "không giữ gì")."""
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if d.get("kind") != "positions" or str(d.get("account_no")) != str(account_no):
                continue
            pos = (d.get("payload") or {}).get("positions") or []
            if not pos:
                continue
            by = {}
            for p in pos:
                if str(p.get("accountNo")) != str(account_no):
                    continue
                by.setdefault(p.get("symbol"), []).append(p)
            out.append((str(d.get("ts") or ""), by))
    out.sort(key=lambda x: x[0])
    return out


def accounts_in(path):
    """[(account_no, label)] xuất hiện trong file."""
    seen = {}
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            a = d.get("account_no")
            if a and d.get("kind") == "positions" and a not in seen:
                seen[a] = d.get("account_label") or a
    return sorted(seen.items())


def previous_file(day, exec_dir=EXEC_DIR):
    """dnse_raw của NGÀY CÓ FILE gần nhất trước `day` (None nếu không có)."""
    best = None
    for p in glob.glob(os.path.join(exec_dir, "dnse_raw_*.jsonl")):
        d = os.path.basename(p)[len("dnse_raw_"):-len(".jsonl")]
        if d < day and (best is None or d > best[0]):
            best = (d, p)
    return best[1] if best else None


def same_day_fills(path, account_no, ticker, day):
    """[(modified_ict, fillQuantity, side)] lệnh của mã có khớp trong ngày `day` theo sổ lệnh
    broker (kind=orders). Rỗng KHÔNG có nghĩa "chắc chắn không khớp" (sổ lệnh không phải lúc nào
    cũng được đọc) — nó chỉ là bằng chứng BỔ SUNG; chốt chặn chính là tổng giá vốn không tăng."""
    out = {}
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if d.get("kind") != "orders" or str(d.get("account_no")) != str(account_no):
                continue
            for o in (d.get("payload") or {}).get("orders") or []:
                if (o.get("symbol") == ticker and str(o.get("accountNo")) == str(account_no)
                        and str(o.get("transDate") or "")[:10] == day
                        and _f(o.get("fillQuantity")) > 0):
                    out[o.get("id")] = (modified_ict(o.get("modifiedDate")),
                                        _f(o.get("fillQuantity")), o.get("side"))
    return list(out.values())


# ───────────────────────────────────────────────────────────── phát hiện cấp TÀI KHOẢN (PURE) ──

def _key(s):
    return (s["qty"], s["closed"], s["accum"], round(s["cost"], 2))


def cost_tol(a, b):
    """Sai số TỔNG giá vốn chỉ do làm tròn `costPrice` (≤ 4 chữ số thập phân ⇒ ≤ 5e-5đ/cp mỗi
    lô). Tính trên TỔNG, không trên đ/cp: lệnh ma 1cp giá 100đ làm tổng tăng 100đ — chia cho KL
    thì còn 0,5đ/cp, lọt mọi sàn đ/cp (selfcheck A5)."""
    return 1e-4 * max(a["qty"], b["qty"]) + 0.01


def _credit_like(a, b):
    """a → b có hình dạng credit quyền (KL không giảm, giá vốn không tăng, không bán, không
    thêm CP bán được) — dùng để lùi qua trạng thái credit DỞ (DNSE credit từng gói vay)."""
    return (b["qty"] >= a["qty"] and b["cost"] - a["cost"] <= cost_tol(a, b)
            and b["closed"] == a["closed"] and b["trade"] == a["trade"])


def account_evidence(series, ticker, day, fills=()):
    """PURE. Một tài khoản, một mã, phiên `day`. `series` = [(ts, {sym: rows})] gồm bản ghi CUỐI
    của file ngày trước + mọi bản ghi của `day` (đã sắp). Trả dict có `verdict`.

    Trạng thái TRƯỚC = đoạn (chuỗi bản ghi cùng KL/giá vốn) ngay trước đoạn cuối, lùi tiếp qua
    các đoạn TRUNG GIAN bắt đầu SAU 15:00 ICT nếu bước chuyển là credit-dở (BID 2026-08-14
    ZaloPay: 400 → 407 lúc 19:10 (1 gói) → 427 lúc 20:15 (gói còn lại)). Không lùi thì phần
    credit thứ hai bị so với trạng thái đã credit một nửa ⇒ hệ số sai.
    """
    segs = []                                       # [first_ts, state_cuối, số bản ghi]
    for ts, by in series:
        rows = by.get(ticker)
        st = aggregate(rows) if rows else aggregate([])
        if segs and _key(segs[-1][1]) == _key(st):
            segs[-1][1], segs[-1][2] = st, segs[-1][2] + 1
        else:
            segs.append([ts, st, 1])
    if not segs or segs[-1][1]["qty"] <= 0:
        return {"verdict": NOT_CANDIDATE, "why": "không giữ mã ở bản ghi cuối"}
    post_first, s1, n_post = segs[-1]
    if not series[-1][0].startswith(day):
        return {"verdict": NOT_CANDIDATE, "why": f"không có bản ghi nào của {day}"}
    if len(segs) == 1:
        return {"verdict": NOT_CANDIDATE, "why": "KL/giá vốn không đổi trong cửa sổ quan sát"}
    j = len(segs) - 2
    close_mark = f"{day}T{CREDIT_WINDOW_START.isoformat()}"
    while (j >= 1 and segs[j][0] >= close_mark
           and _credit_like(segs[j - 1][1], segs[j][1]) and _credit_like(segs[j][1], s1)):
        j -= 1
    ts0, s0 = segs[j][0], segs[j][1]
    # mốc "bản ghi trước credit": bản ghi CUỐI của đoạn trước — dùng để xét lệnh khớp muộn
    ts0_last = max(ts for ts, by in series if ts < segs[j + 1][0]) if j + 1 < len(segs) else ts0
    q0, q1 = s0["qty"], s1["qty"]
    if q1 <= q0 or q0 <= 0:
        return {"verdict": NOT_CANDIDATE, "why": f"KL {q0:,.0f}→{q1:,.0f} không phải tăng từ vị thế có sẵn"}
    cash = (s0["cost"] - s1["cost"]) / q0
    if s1["cost"] - s0["cost"] > cost_tol(s0, s1):
        return {"verdict": NOT_CANDIDATE,
                "why": f"tổng giá vốn TĂNG {s1['cost'] - s0['cost']:+,.0f}đ ⇒ hình dạng mua/chuyển vào, không phải quyền"}

    ev = {"verdict": AMBIGUOUS, "q0": q0, "q1": q1, "ts_pre": ts0_last, "ts_post_first": post_first,
          "n_post": n_post, "cost0": round(s0["cost"], 4), "cost1": round(s1["cost"], 4),
          "trade0": s0["trade"], "trade1": s1["trade"], "mkt0": s0["mkts"], "mkt1": s1["mkts"],
          "lots": len(s1["lots"]), "segments_walked": len(segs) - 2 - j}
    hard, soft = [], []                     # hard ⇒ AMBIGUOUS; soft (đang điều chỉnh dở) ⇒ INSUFFICIENT
    if s1["closed"] != s0["closed"]:
        hard.append(f"closedQuantity {s0['closed']:,.0f}→{s1['closed']:,.0f} (có bán trong cửa sổ)")
    if abs((s1["accum"] - s0["accum"]) - (q1 - q0)) > 1e-9:
        hard.append(f"accumulateQuantity tăng {s1['accum'] - s0['accum']:+,.0f} ≠ KL tăng {q1 - q0:+,.0f}")
    if s1["trade"] > q0:
        # CP quyền mới credit CHƯA bán được (8/8 ca thật). Không đòi trade đứng yên tuyệt đối:
        # CP mua T−2 có thể về tài khoản (sellable) giữa bản ghi trước và sau — nhưng không bao
        # giờ vượt KL TRƯỚC sự kiện.
        hard.append(f"tradeQuantity {s1['trade']:,.0f} > KL trước sự kiện {q0:,.0f} (CP mới đã bán "
                    f"được — không phải mẫu credit quyền)")
    mods = [modified_ict(m) for m in s1["mods"]]
    if not mods or any(m is None for m in mods):
        hard.append(f"modifiedDate không parse được {s1['mods']}")
    else:
        inside = [m for m in mods if m.date().isoformat() == day and m.time() >= CREDIT_WINDOW_START]
        off = [m.isoformat() for m in mods if m not in inside]
        if off and inside:
            soft.append(f"{len(off)}/{len(mods)} lô CHƯA đổi trong cửa sổ credit ({off}) — DNSE "
                        f"đang điều chỉnh dở theo gói vay")
        elif off:
            hard.append(f"lô đổi NGOÀI cửa sổ sau đóng cửa {day} ≥15:00 ICT: {off} ⇒ không có bằng "
                        f"chứng ex-date = phiên kế tiếp")
        ev["credit_ict"] = min(mods).isoformat()
        ev["credit_utc"] = (min(mods).astimezone(dt.timezone.utc).replace(tzinfo=None)
                            .isoformat(timespec="seconds"))
    if len(s1["mkts"]) != 1:
        soft.append(f"các lô mang marketPrice khác nhau {s1['mkts']} — điều chỉnh dở theo gói vay")
    if set(s0["lots"]) != set(s1["lots"]):
        hard.append(f"id lô đổi {sorted(s0['lots'])}→{sorted(s1['lots'])}")
    elif not soft:
        for lid, (lq0, lc0) in sorted(s0["lots"].items()):
            lq1, lc1 = s1["lots"][lid]
            if lq0 <= 0:
                continue
            lcash = (lq0 * lc0 - lq1 * lc1) / lq0
            if lq1 < lq0 or abs(lcash - cash) > 1.0:
                hard.append(f"lô {lid}: {lq0:,.0f}@{lc0:,.4f}→{lq1:,.0f}@{lc1:,.4f} (chân tiền lô "
                            f"{lcash:,.2f} ≠ vị thế {cash:,.2f}) — các lô KHÔNG đổi đồng thời")
    late = [f for f in fills if f[0] is None or f[0].isoformat()[:19] >= ts0_last[:19]]
    if late:
        hard.append(f"sổ lệnh broker có {len(late)} lệnh KHỚP mã này sau bản ghi trước credit {ts0_last}")
    c = round(cash)
    if abs(cash - c) > CASH_TOL_VND:
        hard.append(f"chân tiền suy từ giá vốn {cash:,.4f}đ/cp không tròn đồng")
    ev["cash_leg"] = float(c) if abs(c) >= CASH_LEG_MIN_VND else 0.0
    ev["m_lo"], ev["m_hi"] = q1 / q0, (q1 + 1) / q0          # floor(q0·m) == q1 — đúng park_holdings
    if hard:
        ev["why"] = "; ".join(hard + soft)
        return ev
    if soft:
        ev["verdict"], ev["why"] = INSUFFICIENT, "; ".join(soft)
        return ev
    if n_post < MIN_POST_SNAPSHOTS:
        ev["verdict"] = INSUFFICIENT
        ev["why"] = f"trạng thái sau credit mới có {n_post} bản ghi (< {MIN_POST_SNAPSHOTS})"
        return ev
    ev["verdict"] = CONFIRMABLE
    ev["why"] = "khớp mẫu credit quyền"
    return ev


# ─────────────────────────────────────────────────────────────── gộp cấp MÃ + hệ số (PURE) ──

def simplest_in(lo, hi):
    """Số thập phân ÍT CHỮ SỐ nhất trong [lo, hi). None nếu không có (≤ MAX_DECIMALS chữ số)."""
    for k in range(0, MAX_DECIMALS + 1):
        s = 10 ** k
        cand = math.ceil(lo * s - 1e-9) / s
        if lo - 1e-12 <= cand < hi:
            return round(cand, k)
    return None


def decide(ticker, day, ex_date, per_account, holders_not_credited, px_cum, vendor_event=None):
    """PURE. Gộp bằng chứng mọi tài khoản → quyết định cấp mã.

    per_account           {label: account_evidence(...)} — chỉ tài khoản có ứng viên (≠ NOT_CANDIDATE)
    holders_not_credited  [label] tài khoản ĐANG GIỮ mã ở bản ghi trước mà KHÔNG thấy credit
    px_cum                giá đóng cửa phiên `day` (hệ CÒN quyền) hoặc None
    vendor_event          sự kiện của mã trên lịch vendor cho `ex_date` (nếu lịch đọc được), hoặc None
    """
    from exdate_frame import FRAME_TOL_PCT, FRAME_TOL_VND, verify_post_event_price
    out = {"ticker": ticker, "credit_day": day, "ex_date": ex_date, "accounts": per_account,
           "px_cum": px_cum}
    reasons = []
    if not per_account:
        return dict(out, verdict=NOT_CANDIDATE, why="không tài khoản nào có ứng viên")
    for lbl, ev in sorted(per_account.items()):
        if ev["verdict"] != CONFIRMABLE:
            reasons.append(f"{lbl}: {ev['verdict']} — {ev.get('why')}")
    if vendor_event is not None and vendor_event.get("price_adjusting") \
            and vendor_event.get("event_code") != "DIV":
        return dict(out, verdict=DEFER_VENDOR,
                    why=(f"lịch vendor CÓ sự kiện cổ phiếu {vendor_event.get('event_code')} cho "
                         f"{ex_date} ⇒ nhánh vendor quyết, broker không ghi đè"))
    if holders_not_credited:
        reasons.append(f"tài khoản {holders_not_credited} đang giữ mã mà CHƯA được credit cùng đêm")
    if reasons:
        verdict = (INSUFFICIENT if all(ev["verdict"] in (CONFIRMABLE, INSUFFICIENT)
                                       for ev in per_account.values()) else AMBIGUOUS)
        return dict(out, verdict=verdict, why="; ".join(reasons))

    evs = list(per_account.values())
    cash = {ev["cash_leg"] for ev in evs}
    if max(cash) - min(cash) > 1.0:
        return dict(out, verdict=AMBIGUOUS, why=f"chân tiền khác nhau giữa tài khoản {sorted(cash)}")
    c = evs[0]["cash_leg"]
    if vendor_event is not None:                                   # chỉ còn ca DIV
        v = _f(vendor_event.get("value_per_share"))
        if abs(v - c) > 1.0:
            return dict(out, verdict=AMBIGUOUS,
                        why=f"lịch vendor DIV {v:,.0f}đ/cp ≠ chân tiền suy từ giá vốn {c:,.0f}đ/cp")
    mkts = {ev["mkt1"][0] for ev in evs}
    if len(mkts) != 1:
        return dict(out, verdict=AMBIGUOUS, why=f"marketPrice sau credit khác nhau giữa tài khoản {sorted(mkts)}")
    m1 = mkts.pop()
    lo = max(ev["m_lo"] for ev in evs)
    hi = min(ev["m_hi"] for ev in evs)
    out.update(cash_leg=c, market_price_post=m1, m_qty_interval=[round(lo, 8), round(hi, 8)])
    if lo >= hi:
        return dict(out, verdict=AMBIGUOUS, why=f"hệ số KL các tài khoản không giao nhau [{lo:.6f}, {hi:.6f})")
    if not px_cum or px_cum <= 0:
        return dict(out, verdict=INSUFFICIENT, why="không có giá đóng cửa cum của phiên credit")
    tol = max(FRAME_TOL_VND, m1 * FRAME_TOL_PCT)
    if m1 - tol <= 0 or px_cum - c <= 0:
        return dict(out, verdict=AMBIGUOUS, why=f"giá vô nghĩa (px_cum {px_cum}, chân tiền {c}, mkt {m1})")
    plo, phi = (px_cum - c) / (m1 + tol), (px_cum - c) / (m1 - tol)
    out["m_price_interval"] = [round(plo, 8), round(phi, 8)]
    lo2, hi2 = max(lo, plo), min(hi, phi + 1e-12)
    if lo2 >= hi2:
        return dict(out, verdict=AMBIGUOUS,
                    why=(f"hệ số KL [{lo:.6f}, {hi:.6f}) KHÔNG giao hệ số giá [{plo:.6f}, {phi:.6f}] "
                         f"(giá cum {px_cum:,.0f}, chân tiền {c:,.0f}, marketPrice {m1:,.0f}) — "
                         f"KL và giá không kể cùng một sự kiện (quyền mua? gói vay chưa xong?)"))
    m = simplest_in(lo2, hi2)
    if m is None or m <= 1.0:
        return dict(out, verdict=AMBIGUOUS, why=f"không chọn được hệ số hợp lý trong [{lo2}, {hi2})")
    from corp_actions import QTY_MULT_MAX
    if m > QTY_MULT_MAX:
        return dict(out, verdict=AMBIGUOUS, why=f"hệ số {m} > {QTY_MULT_MAX} (biên chặn registry) — người xác nhận")
    for lbl, ev in per_account.items():
        if int(math.floor(ev["q0"] * m + 1e-9)) != int(ev["q1"]):
            return dict(out, verdict=AMBIGUOUS,
                        why=f"{lbl}: floor({ev['q0']:,.0f}×{m}) ≠ {ev['q1']:,.0f}")
    px_ok, pwhy = verify_post_event_price(px_cum, m1, m, c)
    if px_ok is None:
        return dict(out, verdict=AMBIGUOUS, why=f"cổng giá: {pwhy}")
    return dict(out, verdict=CONFIRMABLE, qty_multiplier=m, price_evidence=pwhy,
                why=f"KL+giá vốn+giá cùng kể sự kiện ×{m} chân tiền {c:,.0f}đ/cp")


# ──────────────────────────────────────────────────────────── điều phối 1 phiên (đọc file) ──

def scan_day(day, px_cum_fn, vendor_event_fn=lambda tk, ex: None, exec_dir=EXEC_DIR, cutoff=None):
    """Mọi mã có ứng viên credit quyền ở phiên `day`, mọi tài khoản. Trả [decide(...)].

    px_cum_fn(ticker, day) → giá đóng cửa cum hoặc None. vendor_event_fn(ticker, ex) → ev | None.
    `cutoff` ("HH:MM", chỉ cho replay) — bỏ bản ghi của `day` sau giờ đó, để mô phỏng đúng cái
    cron 19:25 nhìn thấy.
    """
    from trading_bot.vn_market import next_trading_day
    path = os.path.join(exec_dir, f"dnse_raw_{day}.jsonl")
    prev = previous_file(day, exec_dir)
    ex_date = next_trading_day(dt.date.fromisoformat(day)).isoformat()
    per_ticker, held_before = {}, {}
    for acct, label in accounts_in(path):
        series = read_series(path, acct)
        if cutoff:
            series = [x for x in series if x[0] <= f"{day}T{cutoff}"]
        if prev:
            pre = read_series(prev, acct)
            series = pre[-1:] + series
        if not series:
            continue
        tickers = set()
        for _ts, by in series:
            tickers |= {t for t, rows in by.items() if any(_f(r.get("openQuantity")) > 0 for r in rows)}
        for tk in sorted(tickers):
            fills = same_day_fills(path, acct, tk, day)
            ev = account_evidence(series, tk, day, fills)
            if ev["verdict"] != NOT_CANDIDATE:
                per_ticker.setdefault(tk, {})[label] = ev
            else:
                first, last = series[0][1].get(tk), series[-1][1].get(tk)
                if first and last and aggregate(first)["qty"] > 0 and aggregate(last)["qty"] > 0:
                    held_before.setdefault(tk, []).append(label)
    out = []
    for tk, per in sorted(per_ticker.items()):
        holders = [lbl for lbl in held_before.get(tk, []) if lbl not in per]
        px = px_cum_fn(tk, day)
        out.append(decide(tk, day, ex_date, per, holders, px, vendor_event_fn(tk, ex_date)))
    return out


# ─────────────────────────────────────────────────────────────── record + ledger (ghi file) ──

def build_record(dec, now_ict):
    """Record `data/corp_actions.json` cho một quyết định CONFIRMABLE — provenance=broker."""
    tk, ex, m, c = dec["ticker"], dec["ex_date"], dec["qty_multiplier"], dec["cash_leg"]
    ev_lines = []
    for lbl, ev in sorted(dec["accounts"].items()):
        ev_lines.append(
            f"BROKER {lbl}: KL {ev['q0']:,.0f}→{ev['q1']:,.0f} (closed/trade đứng yên, "
            f"{ev['n_post']} bản ghi sau credit từ {ev['ts_post_first']}), tổng giá vốn "
            f"{ev['cost0']:,.2f}→{ev['cost1']:,.2f} (chân tiền {ev['cash_leg']:,.0f}đ/cp), "
            f"marketPrice {ev['mkt0']}→{ev['mkt1']}, credit {ev.get('credit_ict')}")
    ev_lines.append(f"GIÁ: {dec['price_evidence']}; giá cum = đóng cửa {dec['credit_day']} "
                    f"{dec['px_cum']:,.0f}; hệ số KL {dec['m_qty_interval']} ∩ hệ số giá "
                    f"{dec['m_price_interval']} ⇒ chọn {m}")
    ev_lines.append(f"EX-DATE SUY RA: credit + hạ giá tham chiếu sau 15:00 ICT phiên {dec['credit_day']}"
                    f" ⇒ GDKHQ = phiên kế tiếp {ex} (mẫu 8/8 sự kiện registry). KHÔNG từ công bố sàn.")
    rec = {
        "id": f"{tk}-{ex}-BROKER-SHARE-EVENT",
        "ticker": tk,
        "event_type": "BONUS_ISSUE",
        "ratio_text": (f"Sự kiện tăng KL ×{m} suy từ broker (thưởng/cổ tức CP/chia tách KHÔNG phân "
                       f"biệt được từ broker)"
                       + (f", kèm chân tiền mặt {c:,.0f}đ/cp" if c else "")),
        "qty_multiplier": m,
        "ex_date": ex,
        "record_date": None,
        "broker_effective_ts": min(ev["credit_utc"] for ev in dec["accounts"].values()),
        "_status": (f"CONFIRMED — corp_action_auto_confirm.py nhánh BROKER {now_ict} "
                    f"(provenance=broker: KL + tổng giá vốn + giá tham chiếu, vendor feed không có "
                    f"sự kiện). Thu hồi: đổi _status thành 'REVOKED ...'"),
        "provenance": "broker",
        "confirmed_by": "corp_action_auto_confirm.py (agent, nhánh broker)",
        "decided_by": "agent",
        "confirmed_at": now_ict,
        "evidence": ev_lines,
        "verify_against_bq": (f"PENDING — chạy sau {ex}: python3 mike/bin/corp_actions.py "
                              f"--verify {tk}-{ex}-BROKER-SHARE-EVENT"),
        "note": "ex_date SUY RA từ thời điểm broker credit; đối chiếu lại khi vendor có exright_date.",
    }
    if c:
        rec["cash_leg_vnd_per_share"] = c
    return rec


def ledger_keys(path=LEDGER_FILE):
    keys = set()
    if not os.path.exists(path):
        return keys
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            keys.add((d.get("mode"), d.get("ticker"), d.get("credit_day"), d.get("verdict")))
    return keys


def ledger_append(entries, path=LEDGER_FILE):
    """Ghi thêm vào sổ, ATOMIC (đọc cũ + tmp + os.replace) — kill giữa chừng không để lại dòng dở."""
    old = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = f.read()
        if old and not old.endswith("\n"):
            old += "\n"
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(old)
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False, default=str) + "\n")
    os.replace(tmp, path)


# ───────────────────────────────────────────────────────────────────────────── replay CLI ──

def bq_unadjusted_close(pairs):
    """{(ticker, day): Price} — cột `Price` CHƯA điều chỉnh (Close đã điều chỉnh hồi tố sẽ nằm
    ở hệ SAU sự kiện ⇒ sai hệ). CHỈ cho replay ngày QUÁ KHỨ (§6)."""
    import subprocess
    if not pairs:
        return {}
    tks = sorted({t for t, _ in pairs})
    days = sorted({d for _, d in pairs})
    sql = (f"SELECT t.ticker, CAST(t.time AS STRING) AS d, t.Price FROM tav2_bq.ticker AS t "
           f"WHERE t.ticker IN ({','.join(repr(t) for t in tks)}) "
           f"AND t.time IN ({','.join(f'DATE {d!r}' for d in days)})")
    env = dict(os.environ)
    r = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--format=json",
                        "--project_id=lithe-record-440915-m9", "--max_rows=100000", sql],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"bq lỗi: {(r.stderr or r.stdout).strip()[:300]}")
    return {(x["ticker"], x["d"]): _f(x["Price"]) for x in json.loads(r.stdout or "[]")}


def replay(start, end, exec_dir=EXEC_DIR, px_map=None, cutoff=None):
    """Chạy `scan_day` trên mọi phiên có dnse_raw trong [start, end]. Chỉ ĐỌC."""
    days = sorted(os.path.basename(p)[len("dnse_raw_"):-len(".jsonl")]
                  for p in glob.glob(os.path.join(exec_dir, "dnse_raw_*.jsonl")))
    days = [d for d in days if start <= d <= end]
    first = {d: scan_day(d, lambda t, dd: None, exec_dir=exec_dir, cutoff=cutoff) for d in days}
    if px_map is None:
        px_map = bq_unadjusted_close({(r["ticker"], d) for d, rs in first.items() for r in rs})
    out = []
    for d in days:
        if first[d]:
            out.extend(scan_day(d, lambda t, dd: px_map.get((t, dd)), exec_dir=exec_dir,
                                cutoff=cutoff))
    return days, out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--replay", nargs=2, metavar=("START", "END"), required=True)
    ap.add_argument("--cutoff", default=None, help="HH:MM — mô phỏng lượt cron chạy lúc đó")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    days, res = replay(*a.replay, cutoff=a.cutoff)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
        return 0
    print(f"replay {a.replay[0]}→{a.replay[1]}: {len(days)} phiên có dnse_raw, {len(res)} ứng viên")
    for r in res:
        print(f"  {r['credit_day']} {r['ticker']:4s} ex {r['ex_date']} {r['verdict']:12s} "
              f"×{r.get('qty_multiplier', '-')} cash {r.get('cash_leg', '-')} — {r['why'][:220]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
