#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chuỗi "phần bot quản lý" (chuỗi b) của một tài khoản có vị thế NGOÀI bot (quỹ mở bước 4, SPEC B).

ĐỊNH NGHĨA (một chỗ: `outside_value` + `transfer_flows`; nguyên mẫu hành vi tham chiếu
`agents/Taylor/research/fund_step4_20261014/zalopay_bot_series.py`)
  ngoài_bot_t = Σ_{mã ∈ sleeve_scope ngày t} KL_t × giá_t  +  cổ tức GỘP phải thu của mã ngoài bot đang
                nằm trong tiền của dòng nav_history ngày t (từ ngày GDKHQ tới trước ngày tiền về)
  NAV_b_t     = NAV_a_t − ngoài_bot_t                    (NAV_a = cột `nav` của nav_history)
  Tiền mặt, Trứng vàng, nợ thuộc TRỌN chuỗi b. Dòng tiền của chuỗi b = dòng tiền của cả tài khoản
  (`account_cash_flows.json`) + dòng tiền ĐÃ NGƯỜI XÁC NHẬN giữa phần ngoài bot ↔ bot
  (`data/sleeve_transfers.json`): cổ tức về tiền (+ròng, thuế 5% là chi phí phần ngoài), bán mã ngoài
  (+tiền bán ròng tại ngày khớp), mua thêm mã ngoài bằng tiền của bot (−).
  Tỉ suất = `nav_unit_ledger.build_ledger` (KHÔNG viết lại công thức) trên NAV_b, mốc
  `starting_capital − ngoài_bot(mốc)`.

PHẠM VI ngoài bot đọc `data/sleeve_scope.json`, KHÔNG đọc `excluded_tickers` (đó là danh sách cấm giao
dịch — có PNJ vị thế 0, và đổi được mà không ai nghĩ tới chuỗi hiệu suất).

VÌ SAO KHÔNG TỰ ĐOÁN dòng tiền: `dnse_raw` cho biết đã bán bao nhiêu, giá nào, nhưng không cho biết tiền ở
lại cho bot hay bị rút, giờ tiền dùng được, phí/thuế thật ⇒ `detect_transfers` chỉ ĐỀ XUẤT; một khoản
chỉ có hiệu lực khi có bản ghi `decision: confirmed` (hoặc `rejected`) mang đúng `proposal_id`.

CỔNG (SPEC §B3): S1 đề xuất chưa xử lý / S2 KL đổi không được giải thích ⇒ chuỗi b từ ngày đó `chưa có
số` (chuỗi a không ảnh hưởng) · S3 thiếu giá mã ngoài ⇒ từ chối · S4 (phía consumer, file lịch sử b) dòng có NAV_a − NAV_b − ngoài
≠ 0 = file bị sửa tay ⇒ `chưa có số` — lúc DỰNG thì NAV_b ĐỊNH NGHĨA bằng NAV_a − ngoài nên không có
gì để kiểm (vòng 2: bỏ kiểm tra hằng đúng); đối soát ĐỘC LẬP duy nhất lúc dựng là S5 ·
S5 `recon_diff` > 0,05% NAV (dòng không ước tính) ⇒ cảnh báo, không chặn · S6 `sleeve_scope` đổi so với
lần dựng trước ⇒ từ chối tới khi dựng lại + ghi chú đính chính · S7 NAV_b ≤ 0 hoặc mốc b < 5% NAV_a ⇒
từ chối.

Dùng:
  python3 mike/bin/nav_sleeve.py --account ZaloPay --asof 2026-10-13            # dựng + đối soát (JSON)
  python3 mike/bin/nav_sleeve.py --account ZaloPay --propose                    # đề xuất dòng tiền
  python3 mike/bin/nav_sleeve.py --account ZaloPay --write                      # ghi nav_sleeve_history
  python3 mike/bin/nav_sleeve_selfcheck.py
"""
import argparse
import csv
import datetime
import glob
import hashlib
import io
import json
import math
import os
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from account_cash_flows import NavRow, _parse_time_ict, load_flows  # noqa: E402
from nav_unit_ledger import build_ledger, load_inception  # noqa: E402
from wc_paths import find_wc_root  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
WC_ROOT = find_wc_root(__file__)
DATA_DIR = os.path.join(WC_ROOT, "data")
EXEC_DIR = os.path.join(DATA_DIR, "execution_logs")
SCOPE_PATH = os.path.join(DATA_DIR, "sleeve_scope.json")
TRANSFERS_PATH = os.path.join(DATA_DIR, "sleeve_transfers.json")
SEED_PATH = os.path.join(DATA_DIR, "account_seed_capital.json")
INCEPTION_PATH = os.path.join(DATA_DIR, "account_inception.json")

DIV_TAX_RATE = 0.05                # thuế TNCN cổ tức tiền mặt (cùng hằng số với vnindex_total_return)
POS_WINDOW_S = 600                 # bản ghi vị thế phải trong ±10 phút quanh balance_ts (luật N3 cash_identity)
RECON_WARN_FRAC = 0.0005           # S5: 0,05% NAV
MIN_BASE_FRAC = 0.05               # S7: mốc b phải >= 5% NAV_a
PRICE_BACK_DAYS = 7                # dòng nav_history ngày nghỉ ⇒ giá phiên gần nhất trước đó
SOURCES = ("dividend", "sale", "purchase", "corporate")
HIST_COLUMNS = ["date", "nav_a", "outside_mv", "outside_recv", "nav_b", "outside_qty_json",
                "price_source", "balance_ts", "positions_ts", "recon_diff", "nav_is_estimate",
                # ngoài danh sách cột của SPEC — cần cho S1/S2/S6 ở phía consumer:
                "positions_stale", "blocked_reason", "scope_md5"]


class SleeveError(Exception):
    """Từ chối dựng (S3/S4/S6/S7, đầu vào hỏng) — rc≠0."""


def _d(s) -> datetime.date:
    return s if isinstance(s, datetime.date) else datetime.date.fromisoformat(str(s)[:10])


# ─────────────────────────────────────────────────────────── phạm vi + bản ghi xác nhận

def load_scope(account: str, path: str = SCOPE_PATH) -> list:
    """[{ticker, from, to}] của account (rỗng nếu account không có mục). File thiếu ⇒ SleeveError."""
    if not os.path.exists(path):
        raise SleeveError(f"thiếu {path} — không biết phạm vi 'ngoài bot' (KHÔNG suy từ excluded_tickers)")
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    out = []
    for i, e in enumerate(cfg.get(account, [])):
        if not e.get("ticker") or not e.get("from"):
            raise SleeveError(f"{path}[{account}][{i}] thiếu ticker/from: {e}")
        out.append({"ticker": e["ticker"], "from": _d(e["from"]),
                    "to": _d(e["to"]) if e.get("to") else None})
    return out


def scope_md5(scope: list) -> str:
    canon = json.dumps([[e["ticker"], e["from"].isoformat(), e["to"].isoformat() if e["to"] else None]
                        for e in sorted(scope, key=lambda e: (e["ticker"], e["from"]))])
    return hashlib.md5(canon.encode()).hexdigest()


def scope_tickers(scope: list, d: datetime.date) -> set:
    return {e["ticker"] for e in scope if e["from"] <= d and (e["to"] is None or d <= e["to"])}


def load_transfers(account: str, path: str = TRANSFERS_PATH) -> list:
    """Bản ghi NGƯỜI đã xử lý (confirmed|rejected). File thiếu = chưa có bản ghi nào."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    out = []
    for i, r in enumerate(cfg.get(account, [])):
        w = f"{path}[{account}][{i}]"
        for k in ("proposal_id", "source", "ticker", "decision", "confirmed_by", "evidence"):
            if not r.get(k):
                raise SleeveError(f"{w}: thiếu '{k}'")
        if r["source"] not in SOURCES or r["decision"] not in ("confirmed", "rejected"):
            raise SleeveError(f"{w}: source {r['source']!r} ∉ {SOURCES} hoặc decision {r['decision']!r}")
        rec = dict(r)
        rec["date"] = _d(r["date"]) if r.get("date") else None
        rec["ex_date"] = _d(r["ex_date"]) if r.get("ex_date") else None
        if r["decision"] == "confirmed":
            gross, fee = float(r.get("gross_vnd") or 0), float(r.get("fee_tax_vnd") or 0)
            if r["source"] == "dividend":
                if rec["ex_date"] is None or gross <= 0:
                    raise SleeveError(f"{w}: cổ tức cần ex_date và gross_vnd > 0")
                want = gross - fee
            elif r["source"] == "sale":
                want = gross - fee
            elif r["source"] == "purchase":
                want = -(gross + fee)
            else:
                want = 0.0
            if rec["date"] is not None or r["source"] != "dividend":
                if rec["date"] is None or not r.get("time_ict"):
                    raise SleeveError(f"{w}: {r['source']} cần date + time_ict")
                rec["time_ict"] = _parse_time_ict(r["time_ict"])
                if abs(float(r.get("amount_vnd", 0)) - want) > 0.5:
                    raise SleeveError(f"{w}: amount_vnd {r.get('amount_vnd')} ≠ {want:.0f} "
                                      f"(gross {gross:.0f}, phí/thuế {fee:.0f}, source {r['source']})")
            if r["source"] in ("sale", "purchase", "corporate") and not r.get("qty"):
                raise SleeveError(f"{w}: {r['source']} cần qty (KL đổi, có dấu)")
            rec["gross_vnd"], rec["fee_tax_vnd"] = gross, fee
            rec["amount_vnd"] = want
        out.append(rec)
    return out


def transfer_flows(transfers: list) -> list:
    """Dòng tiền của chuỗi b từ bản ghi confirmed đã có ngày tiền (định dạng của `load_flows`)."""
    out = []
    for r in transfers:
        if r["decision"] != "confirmed" or r["date"] is None or not r["amount_vnd"]:
            continue
        out.append({"date": r["date"], "amount_vnd": r["amount_vnd"],
                    "kind": "deposit" if r["amount_vnd"] > 0 else "withdraw",
                    "evidence": f"sleeve {r['proposal_id']} ({r['source']} {r['ticker']}; "
                                f"xác nhận: {r['confirmed_by']}) — {r['evidence']}",
                    "timing": None, "time_ict": r["time_ict"]})
    return sorted(out, key=lambda f: (f["date"], f["time_ict"]))


# ─────────────────────────────────────────────────────────── vị thế + giá trị phần ngoài

def positions_at(account_no: str, date, balance_ts: str, logs_dir: str = EXEC_DIR) -> tuple:
    """({mã: KL}, positions_ts, gap_s, stale). Bản ghi `positions` gần `balance_ts` nhất trong file của
    ngày dòng + ngày của balance_ts. KL CỘNG mọi lô cùng mã (một mã có thể ở nhiều lô khác
    loanPackageId — đọc ghi đè từng làm thiếu 24,4tr MBB/BID/VCB). Lệch > ±10 phút ⇒ stale."""
    t0 = datetime.datetime.fromisoformat(balance_ts)
    best, gap = None, None
    for day in sorted({_d(date).isoformat(), balance_ts[:10]}):
        p = os.path.join(logs_dir, f"dnse_raw_{day}.jsonl")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                if str(rec.get("account_no")) != str(account_no):
                    continue
                if rec.get("kind") != "positions":
                    continue
                g = abs((datetime.datetime.fromisoformat(rec["ts"]) - t0).total_seconds())
                if gap is None or g < gap:
                    best, gap = rec, g
    if best is None:
        return None, None, None, True
    qty = {}
    for p in best["payload"]["positions"]:
        if p.get("openQuantity"):
            qty[p["symbol"]] = qty.get(p["symbol"], 0) + p["openQuantity"]
    return qty, best["ts"], gap, gap > POS_WINDOW_S


def outside_value(d, qty: dict, tickers: set, price_fn, transfers: list) -> tuple:
    """(mv, recv, {mã: (giá, nguồn)}) của phần ngoài bot ngày d. Thiếu giá ⇒ SleeveError (S3).
    recv = cổ tức GỘP đã xác nhận của mã ngoài, ex_date <= d < ngày tiền về (chưa về ⇒ tới nay)."""
    d = _d(d)
    mv, used = 0.0, {}
    for tk in sorted(tickers):
        q = qty.get(tk, 0)
        if not q:
            continue
        got = price_fn(d, tk)
        if got is None or not (got[0] and math.isfinite(got[0])):
            raise SleeveError(f"S3: {d} không có giá {tk} (KL {q}) — từ chối dòng")
        used[tk] = got
        mv += q * got[0]
    recv = sum(r["gross_vnd"] for r in transfers
               if r["decision"] == "confirmed" and r["source"] == "dividend" and r["ticker"] in tickers
               and r["ex_date"] <= d and (r["date"] is None or d < r["date"]))
    return mv, recv, used


# ─────────────────────────────────────────────────────────── đề xuất dòng tiền

def _drop_persists(series: list, i: int, old_level: float) -> bool:
    """Khoản giảm ở `series[i]` là thật nếu KHÔNG bản ghi nào trong 24 giờ sau đọc lại >= mức cũ.
    Ca thật ZaloPay 2026-09-24 19:07:17 → 19:17:49: DNSE trả 5 bản ghi số dư TOÀN 0 (totalCash 0,
    cashDividendReceiving 0) rồi 19:17:59 trở lại 81,9tr — tiền cổ tức về thật 25/09 (04:51 → 19:07)."""
    t1 = datetime.datetime.fromisoformat(series[i][0])
    for ts, v in series[i + 1:]:
        if datetime.datetime.fromisoformat(ts) - t1 > datetime.timedelta(hours=24):
            break
        if v >= old_level - 0.5:
            return False
    return True


def detect_transfers(rows: list, scope: list, divs: list, div_recv: list, fills: dict) -> list:
    """ĐỀ XUẤT, không tự ghi. `rows`: [(date, {mã ngoài: KL})] theo dòng nav_history (dòng 0 = mốc);
    `divs`: [{ticker, ex_date, per_share}] (corporate_action DIV); `div_recv`: [(ts, cashDividendReceiving)]
    tăng dần (balances của ĐÚNG account); `fills`: {date: [{symbol, side, fillQuantity, averagePrice}]}."""
    from dnse_fee_rates import FEE_RATE_BUY_PCT, FEE_RATE_SELL_PCT, SELL_TAX_RATE
    out = []
    last_date = rows[-1][0] if rows else None
    for ev in sorted(divs, key=lambda e: (e["ex_date"], e["ticker"])):
        ex = _d(ev["ex_date"])
        if not any(e["ticker"] == ev["ticker"] and e["from"] <= ex and (e["to"] is None or ex <= e["to"])
                   for e in scope) or last_date is None or ex > last_date:
            continue
        before = [q for d, q in rows if d < ex]
        qty = (before[-1] if before else {}).get(ev["ticker"], 0)
        if not qty:
            continue
        gross = ev["per_share"] * qty
        settle, window = None, None
        for i, ((t0, v0), (t1, v1)) in enumerate(zip(div_recv, div_recv[1:])):
            if _d(t1[:10]) >= ex and v0 - v1 >= gross - 0.5 and _drop_persists(div_recv, i + 1, v0):
                settle, window = _d(t1[:10]), (t0, t1)
                break
        p = {"proposal_id": f"dividend:{ev['ticker']}:{ex.isoformat()}", "source": "dividend",
             "ticker": ev["ticker"], "ex_date": ex.isoformat(), "qty_record": qty,
             "per_share": ev["per_share"], "gross_vnd": gross, "fee_tax_vnd": gross * DIV_TAX_RATE,
             "amount_vnd": gross * (1 - DIV_TAX_RATE)}
        if settle:
            p.update({"date": settle.isoformat(), "settle_window": list(window),
                      "time_ict": None, "note": "giờ tiền về KHÔNG đo được — người khai trong cửa sổ"})
        else:
            p["note"] = "chưa thấy cashDividendReceiving giảm ⇒ chưa về tiền (recv tính từ ex_date)"
        out.append(p)
    for (d0, q0), (d1, q1) in zip(rows, rows[1:]):
        for tk in sorted(set(q0) | set(q1)):
            dq = q1.get(tk, 0) - q0.get(tk, 0)
            if not dq:
                continue
            got = [(dd, f) for dd, fs in sorted(fills.items()) if d0 < _d(dd) <= d1
                   for f in fs if f["symbol"] == tk and f.get("fillQuantity")]
            net = sum((f["fillQuantity"] if f["side"] == "NB" else -f["fillQuantity"]) for _, f in got)
            if got and net == dq and all(f["side"] == got[0][1]["side"] for _, f in got):
                gross = sum(f["fillQuantity"] * f["averagePrice"] for _, f in got)
                sale = dq < 0
                fee = gross * ((FEE_RATE_SELL_PCT / 100 + SELL_TAX_RATE) if sale else FEE_RATE_BUY_PCT / 100)
                fd = max(_d(dd) for dd, _ in got)
                out.append({"proposal_id": f"{'sale' if sale else 'purchase'}:{tk}:{fd.isoformat()}",
                            "source": "sale" if sale else "purchase", "ticker": tk, "qty": dq,
                            "date": fd.isoformat(), "time_ict": None, "gross_vnd": gross,
                            "fee_tax_vnd": fee, "amount_vnd": (gross - fee) if sale else -(gross + fee),
                            "note": "phí/thuế ƯỚC (dnse_fee_rates); tiền ở lại cho bot hay bị rút — "
                                    "người xác nhận (rút = dòng tiền tài khoản, khai account_cash_flows)"})
            else:
                out.append({"proposal_id": f"needs_human:{tk}:{d1.isoformat()}", "source": "needs_human",
                            "ticker": tk, "qty": dq, "date": d1.isoformat(),
                            "note": f"KL đổi {dq:+d} giữa {d0} và {d1}, lệnh khớp cộng {net:+d} — "
                                    f"thưởng CP/quyền mua/chuyển khoản? Không mang số tiền"})
    return out


def unresolved(proposals: list, transfers: list, rows: list) -> list:
    """[(ngày, lý do)] — S1: đề xuất chưa có bản ghi confirmed/rejected; S2: KL đổi mà bản ghi confirmed
    (sale/purchase/corporate) không cộng ra đúng."""
    done = {r["proposal_id"]: r for r in transfers}
    out = []
    for p in proposals:
        r = done.get(p["proposal_id"])
        if r is None:
            out.append((_d(p.get("ex_date") or p.get("date")),
                        f"S1: đề xuất {p['proposal_id']} chưa được xác nhận/bác ({p.get('note', '')})"))
        elif (p["source"] == "dividend" and p.get("date") and r["decision"] == "confirmed"
              and r["date"] is None):
            # đã xác nhận lúc chưa về tiền; tiền đã về mà bản ghi chưa có ngày ⇒ recv bị trừ mãi
            out.append((_d(p["date"]), f"S1: cổ tức {p['proposal_id']} đã về tiền ngày {p['date']} "
                                       f"nhưng bản ghi xác nhận chưa có date/time_ict"))
    for (d0, q0), (d1, q1) in zip(rows, rows[1:]):
        for tk in sorted(set(q0) | set(q1)):
            dq = q1.get(tk, 0) - q0.get(tk, 0)
            if not dq:
                continue
            got = sum(int(r["qty"]) for r in transfers
                      if r["decision"] == "confirmed" and r["ticker"] == tk
                      and r["source"] in ("sale", "purchase", "corporate")
                      and r["date"] is not None and d0 < r["date"] <= d1)
            if got != dq:
                out.append((d1, f"S2: {tk} KL đổi {dq:+d} ({d0}→{d1}) nhưng bản ghi xác nhận cộng {got:+d}"))
    return sorted(out)


# ─────────────────────────────────────────────────────────── dựng chuỗi

def _f(r, k):
    v = r.get(k)
    return float(v) if v not in (None, "") else 0.0


def build_sleeve_rows(account: str, nav_rows: list, inception: dict, scope: list, transfers: list,
                      positions_fn, price_fn, all_price_fn=None, proposals=None, seed=None) -> dict:
    """Bảng chuỗi b. `nav_rows` = dict của nav_history (date, nav, cash, egg_assets, offbook_assets,
    margin_debt, balance_ts, nav_is_estimate); `positions_fn(date, balance_ts)` → như `positions_at`;
    `price_fn(date, mã)` → (giá, nguồn) cho mã NGOÀI; `all_price_fn` (tuỳ chọn) cho mã trong bot ⇒
    dựng-từ-dưới-lên (`recon_diff`)."""
    inc_d = _d(inception["inception_date"])
    cap = float(inception["starting_capital"])
    tick0 = scope_tickers(scope, inc_d)
    seed_pos = (seed or {}).get("legacy_positions", {})
    if tick0 and all(t in seed_pos for t in tick0):
        q0 = {t: seed_pos[t]["qty"] for t in tick0}
        out0 = sum(seed_pos[t]["qty"] * seed_pos[t]["price"] for t in tick0)
        out0_src = "account_seed_capital.legacy_positions"
    else:
        q_all, _, _, _ = positions_fn(inc_d, inception.get("balance_ts") or f"{inc_d}T21:00:00")
        q0 = {t: (q_all or {}).get(t, 0) for t in tick0}
        out0 = outside_value(inc_d, q0, tick0, price_fn, transfers)[0]
        out0_src = "positions_at(mốc) × giá"
    base_b = cap - out0
    if base_b <= 0 or base_b < MIN_BASE_FRAC * cap:
        raise SleeveError(f"S7: mốc chuỗi b {base_b:,.0f} = {cap:,.0f} − ngoài bot {out0:,.0f} "
                          f"(< {100 * MIN_BASE_FRAC:g}% NAV_a) — tỉ suất trên mẫu số gần 0, từ chối")
    table, qrows = [], [(inc_d, q0)]
    for r in nav_rows:
        d = _d(r["date"])
        if d <= inc_d:
            continue
        qty, pts, gap, stale = positions_fn(d, r["balance_ts"])
        if qty is None:
            raise SleeveError(f"{d}: không có bản ghi vị thế {account} quanh {r['balance_ts']}")
        tk = scope_tickers(scope, d)
        oq = {t: qty.get(t, 0) for t in tk if qty.get(t, 0)}
        mv, recv, used = outside_value(d, oq, tk, price_fn, transfers)
        nav_a = float(r["nav"])
        nav_b = nav_a - mv - recv
        if nav_b <= 0:
            raise SleeveError(f"S7: {d} NAV_b = {nav_b:,.0f} <= 0 (NAV_a {nav_a:,.0f}, ngoài {mv + recv:,.0f})")
        recon = None
        if all_price_fn is not None:
            in_mv = 0.0
            for s, q in qty.items():
                q_in = q - oq.get(s, 0)
                if q_in:
                    p = all_price_fn(d, s)
                    in_mv += q_in * (p[0] if p else float("nan"))
            bottom = in_mv + _f(r, "cash") + _f(r, "egg_assets") + _f(r, "offbook_assets") \
                - _f(r, "margin_debt") - recv
            recon = nav_b - bottom
        table.append({"date": d.isoformat(), "nav_a": nav_a, "outside_mv": mv, "outside_recv": recv,
                      "nav_b": nav_b, "outside_qty_json": json.dumps(oq, sort_keys=True),
                      "price_source": ";".join(f"{t}={p[0]:g}@{p[1]}" for t, p in sorted(used.items())),
                      "balance_ts": r["balance_ts"], "positions_ts": pts or "",
                      "recon_diff": recon, "nav_is_estimate": "True" if r.get("nav_is_estimate") == "True" else "",
                      "positions_stale": "True" if stale else "", "blocked_reason": "",
                      "scope_md5": scope_md5(scope), "_gap_s": gap})
        qrows.append((d, oq))
    blocks = unresolved(proposals or [], transfers, qrows)
    if blocks:
        first = blocks[0][0]
        why = "; ".join(b for _, b in blocks)
        for t in table:
            if _d(t["date"]) >= first:
                t["blocked_reason"] = why
    return {"table": table, "base_b": base_b, "outside0": out0, "outside0_source": out0_src,
            "q0": q0, "qrows": qrows, "blocks": blocks}


def build_sleeve_ledger(table: list, inception: dict, base_b: float, flows_b: list) -> tuple:
    """`nav_unit_ledger.build_ledger` trên các dòng chưa bị chặn (S1/S2) — KHÔNG viết lại công thức."""
    rows_b = [NavRow(_d(t["date"]), float(t["nav_b"]), is_estimate=(t["nav_is_estimate"] == "True"),
                     balance_ts=t["balance_ts"] or None)
              for t in table if not t["blocked_reason"] and t["nav_b"] not in (None, "")]
    return build_ledger(rows_b, flows_b, _d(inception["inception_date"]), base_b)


def reconcile(built: dict, ledger_flows: list, inception: dict) -> dict:
    """Đối soát lúc dựng: (1) dựng từ dưới lên (`recon_diff`, S5 — phép ĐỘC LẬP duy nhất: cộng mã trong
    bot × giá BQ + tiền − nợ, không đi qua NAV_a); (2) lãi/lỗ cộng được cả kỳ (chỉ kiểm phần dòng tiền —
    NAV_b định nghĩa từ NAV_a nên a = b + ngoài từng dòng là hằng đúng, không báo như một phép kiểm)."""
    t = built["table"]
    if not t:
        return {"rows": 0}
    rec = [x for x in t if x["recon_diff"] is not None]
    warn = [{"date": x["date"], "recon_diff": round(x["recon_diff"]), "nav_is_estimate": x["nav_is_estimate"]}
            for x in rec if abs(x["recon_diff"]) > RECON_WARN_FRAC * x["nav_a"]]
    last = t[-1]
    cap = float(inception["starting_capital"])
    fl = sum(f["amount_vnd"] for f in ledger_flows)
    pa = last["nav_a"] - cap
    pb = last["nav_b"] - built["base_b"] - fl
    po = last["outside_mv"] + last["outside_recv"] - built["outside0"] + fl
    return {"rows": len(t),
            "recon_rows": len(rec), "recon_zero_rows": sum(1 for x in rec if abs(x["recon_diff"]) < 1),
            "recon_warn_S5": warn,
            "pnl_vnd": {"a": pa, "b": pb, "outside": po, "residual": pa - pb - po}}


# ─────────────────────────────────────────────────────────── lịch sử trên đĩa (consumer đọc)

def history_path(account: str, exec_dir: str = EXEC_DIR) -> str:
    return os.path.join(exec_dir, f"nav_sleeve_history_{account}.csv")


def _hist_bytes(table: list) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(HIST_COLUMNS)
    for t in table:
        w.writerow([("" if t.get(c) is None else (repr(t[c]) if isinstance(t[c], float) else t[c]))
                    for c in HIST_COLUMNS])
    return buf.getvalue().encode("utf-8")


def write_history(path: str, table: list, scope: list, allow_scope_change: str = None) -> bool:
    """Ghi atomic. S6: scope_md5 của file cũ khác scope hiện tại ⇒ SleeveError trừ khi có
    `allow_scope_change` = đường dẫn ghi chú đính chính (bước 3) đã tồn tại."""
    new_md5 = scope_md5(scope)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = list(csv.DictReader(f))
        olds = {r.get("scope_md5") for r in old}
        if old and olds != {new_md5}:
            if not (allow_scope_change and os.path.exists(allow_scope_change)):
                raise SleeveError(f"S6: sleeve_scope đổi (md5 cũ {sorted(olds)} ≠ {new_md5}) — từ chối; "
                                  f"dựng lại cả chuỗi + ghi chú đính chính (--allow-scope-change <file>)")
    data = _hist_bytes(table)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    return True


class SleeveUnavailable(Exception):
    """Chuỗi b không có số cho kỳ hỏi — consumer in `chưa có số (<lý do>)`, không chặn chuỗi a."""


def sleeve_inputs_for_report(account: str, report_date, nav_rows: list, inception: dict, flows: list,
                             exec_dir: str = EXEC_DIR, scope_path: str = SCOPE_PATH,
                             transfers_path: str = TRANSFERS_PATH, seed_path: str = SEED_PATH) -> dict:
    """Đầu vào ledger b cho `nav_period_returns --sleeve bot`, CHỈ từ file đã dựng (không BQ/broker).
    Freshness thật (§14): mọi dòng nav_history ≤ report_date sau mốc phải có trong lịch sử b với
    `nav_a` bằng đúng `nav` hiện tại; scope phải trùng md5 lúc dựng (S6); không dòng nào bị chặn."""
    report_date = _d(report_date)
    scope = load_scope(account, scope_path)
    if not scope:
        raise SleeveUnavailable(f"{account} không có mục trong sleeve_scope.json — không có phần ngoài bot")
    hp = history_path(account, exec_dir)
    if not os.path.exists(hp):
        raise SleeveUnavailable(f"chưa có {os.path.basename(hp)} (chuỗi b chưa được dựng)")
    with open(hp, encoding="utf-8") as f:
        hist = {r["date"]: r for r in csv.DictReader(f)}
    md5s = {r["scope_md5"] for r in hist.values()}
    if md5s != {scope_md5(scope)}:
        raise SleeveUnavailable(f"S6: sleeve_scope đổi sau lần dựng (md5 lịch sử {sorted(md5s)} ≠ "
                                f"{scope_md5(scope)}) — dựng lại chuỗi b")
    inc_d = _d(inception["inception_date"])
    rows_b = []
    for nr in nav_rows:
        d, nav = nr[0], nr[1]
        if d <= inc_d or d > report_date:
            continue
        h = hist.get(d.isoformat())
        if h is None:
            raise SleeveUnavailable(f"nav_sleeve_history thiếu dòng {d} (nav_history có) — chưa dựng lại")
        if abs(float(h["nav_a"]) - nav) > 0.5:
            raise SleeveUnavailable(f"{d}: nav_history nav {nav:,.0f} ≠ nav_a {float(h['nav_a']):,.0f} lúc "
                                    f"dựng chuỗi b (nav_history đổi/đính chính sau đó) — dựng lại")
        if h["blocked_reason"]:
            raise SleeveUnavailable(f"{d}: {h['blocked_reason']}")
        # S4 — file lịch sử b phải tự nhất quán (sửa tay nav_b/outside_* ⇒ không dùng)
        resid = float(h["nav_a"]) - float(h["nav_b"]) - float(h["outside_mv"]) - float(h["outside_recv"])
        if abs(resid) > 0.5:
            raise SleeveUnavailable(f"S4: {d} trong {os.path.basename(hp)}: nav_a {h['nav_a']} − nav_b "
                                    f"{h['nav_b']} − ngoài ({h['outside_mv']} + {h['outside_recv']}) = "
                                    f"{resid:+,.0f} đ ≠ 0 — file bị sửa sau khi dựng, dựng lại")
        rows_b.append(NavRow(d, float(h["nav_b"]), is_estimate=nr.is_estimate if hasattr(nr, "is_estimate") else False,
                             balance_ts=getattr(nr, "balance_ts", None)))
    transfers = load_transfers(account, transfers_path)
    seed = {}
    if os.path.exists(seed_path):
        with open(seed_path, encoding="utf-8") as f:
            seed = json.load(f).get(account, {})
    tick0 = scope_tickers(scope, inc_d)
    seed_pos = seed.get("legacy_positions", {})
    if not (tick0 and all(t in seed_pos for t in tick0)):
        raise SleeveUnavailable(f"không định giá được phần ngoài bot tại mốc {inc_d} từ account_seed_capital")
    out0 = sum(seed_pos[t]["qty"] * seed_pos[t]["price"] for t in tick0)
    cap = float(inception["starting_capital"])
    base_b = cap - out0
    if base_b <= 0 or base_b < MIN_BASE_FRAC * cap:
        raise SleeveUnavailable(f"S7: mốc chuỗi b {base_b:,.0f} < {100 * MIN_BASE_FRAC:g}% NAV_a")
    return {"rows": rows_b, "flows": sorted(list(flows) + transfer_flows(transfers),
                                            key=lambda f: (f["date"], f["time_ict"] or "")),
            "inception_from": inc_d, "nav0": base_b,
            "outside_scope": [{"ticker": e["ticker"], "from": e["from"].isoformat(),
                               "to": e["to"].isoformat() if e["to"] else None} for e in scope],
            "outside0_vnd": out0}


# ─────────────────────────────────────────────────────────── nguồn thật (CLI)

def read_nav_rows(account: str, exec_dir: str = EXEC_DIR) -> list:
    with open(os.path.join(exec_dir, f"nav_history_{account}.csv"), encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("date") and r.get("nav")]


def snapshot_price_fn(account: str, exec_dir: str, fallback):
    """Giá đúng như `daily_nav_snapshot` đã dùng (trường `sleeve_outside` của nav_snapshot JSON);
    không có ⇒ `fallback` (BQ Price — đường backfill lịch sử)."""
    def fn(d, tk):
        p = os.path.join(exec_dir, f"nav_snapshot_{account}_{_d(d).isoformat()}.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                so = (json.load(f).get("sleeve_outside") or {}).get(tk)
            if so and so.get("price"):
                return float(so["price"]), "nav_snapshot"
        return fallback(d, tk)
    return fn


def bq_price_fn(tickers, start, end):
    """Giá THÔ `tav2_bq.ticker.Price`; ngày không có phiên ⇒ phiên gần nhất trước đó ≤ 7 ngày (đúng
    cách nav_history định giá dòng ngày nghỉ, vd 2026-08-31)."""
    if WC_ROOT not in sys.path:
        sys.path.insert(0, WC_ROOT)
    from corp_action_lib import TABLE, bq
    proj = TABLE.split(".")[0]
    tl = ",".join(f"'{t}'" for t in sorted(tickers))
    px = {}
    for r in bq(f"SELECT CAST(t.time AS STRING) d, t.ticker, t.Price FROM `{proj}.tav2_bq.ticker` AS t "
                f"WHERE t.ticker IN ({tl}) AND t.time BETWEEN '{start}' AND '{end}'"):
        if r["Price"] is not None:
            px[(r["d"], r["ticker"])] = float(r["Price"])

    def fn(d, tk):
        d = _d(d)
        for k in range(0, PRICE_BACK_DAYS + 1):
            p = px.get(((d - datetime.timedelta(days=k)).isoformat(), tk))
            if p is not None:
                return p, "bq_price" if k == 0 else f"bq_price_T-{k}"
        return None
    return fn


def dedupe_dividends(rows: list) -> list:
    """Cùng luật với `vnindex_total_return.dividends`: bỏ trùng HOÀN TOÀN trên (mã, ex-date, số tiền,
    năm, đợt), CỘNG các đợt khác nhau cùng ngày (DGC 14/09/2026: 3.000 + 5.000)."""
    seen, agg = set(), {}
    for r in rows:
        v = float(r.get("value_per_share") or 0)
        if v <= 0 or not r.get("exright_date"):
            continue
        key = (r["ticker"], str(r["exright_date"])[:10], v, r.get("dividend_year"), r.get("dividend_stage_vi"))
        if key in seen:
            continue
        seen.add(key)
        agg[key[:2]] = agg.get(key[:2], 0.0) + v
    return [{"ticker": t, "ex_date": x, "per_share": v} for (t, x), v in sorted(agg.items())]


def bq_dividends(tickers, since) -> list:
    """DIV của `corporate_action` cho mã ngoài bot, mọi trạng thái TRỪ `not_executed` (đề xuất phải có
    từ ngày GDKHQ — dòng lật `executed` ~22:2x ICT ngày đó)."""
    if WC_ROOT not in sys.path:
        sys.path.insert(0, WC_ROOT)
    from corp_action_lib import TABLE, bq
    tl = ",".join(f"'{t}'" for t in tickers)
    return dedupe_dividends(bq(
        f"SELECT c.ticker, CAST(c.exright_date AS STRING) exright_date, c.value_per_share, "
        f"c.dividend_year, c.dividend_stage_vi FROM `{TABLE}` AS c WHERE c.event_code = 'DIV' "
        f"AND c.event_status != 'not_executed' AND c.ticker IN ({tl}) AND c.exright_date >= '{since}'"))


def raw_div_recv_and_fills(account_no: str, exec_dir: str = EXEC_DIR, since=None) -> tuple:
    """(div_recv [(ts, cashDividendReceiving)], fills {date: [...]}) từ dnse_raw — lọc account ở dòng đầu."""
    recv, fills = [], {}
    for p in sorted(glob.glob(os.path.join(exec_dir, "dnse_raw_*.jsonl"))):
        day = os.path.basename(p)[9:19]
        if since and day < str(since):
            continue
        last_orders = None
        with open(p, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                if str(rec.get("account_no")) != str(account_no):
                    continue
                k = rec.get("kind")
                if k == "balances":
                    v = (rec.get("payload", {}).get("stock") or {}).get("cashDividendReceiving")
                    if v is not None:
                        recv.append((rec["ts"], float(v)))
                elif k == "orders":
                    last_orders = rec.get("payload", {}).get("orders") or last_orders
        if last_orders:
            fills[day] = [o for o in last_orders if o.get("fillQuantity")]
    return sorted(recv), fills


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--account", required=True)
    ap.add_argument("--asof", help="YYYY-MM-DD; mặc định dòng cuối nav_history")
    ap.add_argument("--propose", action="store_true", help="in đề xuất dòng tiền (không ghi)")
    ap.add_argument("--write", action="store_true", help="ghi nav_sleeve_history_<account>.csv")
    ap.add_argument("--allow-scope-change", help="ghi chú đính chính (S6)")
    ap.add_argument("--exec-dir", default=EXEC_DIR)
    a = ap.parse_args(argv)
    try:
        inception = load_inception(a.account, INCEPTION_PATH)
        scope = load_scope(a.account)
        transfers = load_transfers(a.account)
        nav_rows = [r for r in read_nav_rows(a.account, a.exec_dir) if not a.asof or r["date"] <= a.asof]
        acct_no = inception["account_no"]
        start, end = inception["inception_date"], nav_rows[-1]["date"]
        cache = {}

        def pos_fn(d, ts):
            k = (str(d), ts)
            if k not in cache:
                cache[k] = positions_at(acct_no, d, ts, a.exec_dir)
            return cache[k]
        held = set()
        for r in nav_rows:
            held |= set(pos_fn(r["date"], r["balance_ts"])[0] or {})
        bqp = bq_price_fn(held | {e["ticker"] for e in scope}, start, end)
        price_fn = snapshot_price_fn(a.account, a.exec_dir, bqp)
        with open(SEED_PATH, encoding="utf-8") as f:
            seed = json.load(f).get(a.account, {})
        built0 = build_sleeve_rows(a.account, nav_rows, inception, scope, transfers, pos_fn, price_fn,
                                   seed=seed)
        if WC_ROOT not in sys.path:
            sys.path.insert(0, WC_ROOT)
        divs = bq_dividends(sorted({e["ticker"] for e in scope}), start)
        recv, fills = raw_div_recv_and_fills(acct_no, a.exec_dir, since=start)
        proposals = detect_transfers(built0["qrows"], scope, divs, recv, fills)
        if a.propose:
            print(json.dumps(proposals, ensure_ascii=False, indent=1, default=str))
            return 0
        built = build_sleeve_rows(a.account, nav_rows, inception, scope, transfers, pos_fn, price_fn,
                                  all_price_fn=bqp, proposals=proposals, seed=seed)
        flows_b = sorted(load_flows(a.account, require_file=True) + transfer_flows(transfers),
                         key=lambda f: (f["date"], f["time_ict"] or ""))
        ledger, info = build_sleeve_ledger(built["table"], inception, built["base_b"], flows_b)
        rec = reconcile(built, [f for f in flows_b if f["date"] > _d(start)], inception)
        if a.write:
            write_history(history_path(a.account, a.exec_dir), built["table"], scope, a.allow_scope_change)
        print(json.dumps({"account": a.account, "base_b": built["base_b"], "outside0": built["outside0"],
                          "last": built["table"][-1]["date"] if built["table"] else None,
                          "unit_price_last": ledger[-1]["unit_price"], "blocks": built["blocks"],
                          "pending_flows": len(info["pending"]), "reconcile": rec,
                          "written": bool(a.write)}, ensure_ascii=False, indent=1, default=str))
        for w in rec.get("recon_warn_S5", []):
            if w["nav_is_estimate"] != "True":
                print(f"⚠️ nav_sleeve S5 ({a.account}) {w['date']}: dựng-từ-dưới-lên lệch NAV_b "
                      f"{w['recon_diff']:+,} đ (> {100 * RECON_WARN_FRAC:g}% NAV)", file=sys.stderr)
        return 0
    except SleeveError as exc:
        print(f"LỖI nav_sleeve: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
