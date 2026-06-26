# -*- coding: utf-8 -*-
"""Executor — chạy xuyên phiên, thực thi TradePlan bằng các lệnh con nhỏ.

Đa tài khoản: mỗi account 1 Executor (state/journal riêng theo label), tất cả
chạy trong MỘT vòng lặp run_session() và dùng CHUNG sổ participation
(shared[ticker] = tổng KL bot đã khớp ở mã đó, mọi tài khoản cộng lại) —
quota ≤ max_participation × KL khớp lũy kế của mã tính trên TOÀN BỘ fleet,
tránh các tài khoản tự cạnh tranh đẩy giá.

Cơ chế mỗi parent order:
  • Tối đa 1 lệnh con sống tại 1 thời điểm (không bao giờ over-fill).
  • Mỗi slice_interval phút đặt 1 lệnh con: qty = min(còn lại, max_child_value/giá,
    quota tham gia còn lại của fleet).
  • Giá mua: ask (cross) hoặc bid+chase_ticks, nhưng KHÔNG vượt
    ref_plan×(1+max_chase_pct_buy) và trần sàn. Vượt → đặt nằm chờ tại trần đuổi.
  • Giá bán: bid, không thấp hơn ref_plan×(1−max_chase_pct_sell) và sàn.
  • Lệnh con treo quá slice_interval → hủy, vòng sau đặt lại theo giá mới.
  • Phiên ATC: phần bán còn sót quét ATC (config), phần mua mặc định bỏ.
  • File data/BOT_STOP xuất hiện → hủy mọi lệnh treo (mọi account) và thoát.

Trạng thái ghi liên tục → giết process giữa chừng chạy lại là resume tiếp.
"""

import csv
import datetime as dt
import json
import os
import time

from .config import EXEC_DIR, STOP_FILE
from .vn_market import session_phase, tick_size, round_price, round_lot, LOT


def _parse_hhmm(s):
    """'HH:MM' → dt.time."""
    h, m = s.split(":")
    return dt.time(int(h), int(m))


class Executor:

    def __init__(self, plan, broker, cfg, shared=None):
        self.plan = plan
        self.broker = broker
        self.cfg = cfg
        self.label = plan.account
        self.shared = shared if shared is not None else {}   # ticker -> KL fleet đã khớp
        os.makedirs(EXEC_DIR, exist_ok=True)
        tag = f"{self.label}_{plan.plan_date}"
        self.state_file = os.path.join(EXEC_DIR, f"exec_{tag}_state.json")
        self.journal_file = os.path.join(EXEC_DIR, f"exec_{tag}_journal.csv")
        self.report_file = os.path.join(EXEC_DIR, f"exec_{tag}_report.md")
        self.state = self._load_state()

    # ------------------------------------------------------------ state/journal

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, encoding="utf-8") as f:
                st = json.load(f)
            if st.get("plan_created_at") == self.plan.created_at:
                print(f"[exec:{self.label}] resume từ {self.state_file}")
                return st
            print(f"[exec:{self.label}] ⚠ plan đã đổi so với state cũ — state mới")
        return {"plan_date": self.plan.plan_date,
                "plan_created_at": self.plan.created_at,
                "px_hist": {},          # ticker -> [[ts, last], …] phục vụ r15 (dip-cross)
                "parents": {o.id: {"filled": 0, "done": False, "atc_sent": False,
                                   "children": [], "last_slice_ts": None}
                            for o in self.plan.orders}}

    def seed_shared(self):
        """Khôi phục sổ participation fleet khi resume.

        Bất biến: shared[ticker] = Σ (qty nếu child đang sống & chưa release,
        ngược lại = filled) — tức KL đã khớp + KL đang TREO (reservation),
        để account khác không vượt quota trong lúc lệnh chưa khớp.
        """
        for o in self.plan.orders:
            for c in self.state["parents"][o.id]["children"]:
                live = c["status"] == "open" and not c.get("released")
                add = c["qty"] if live else c.get("filled", 0)
                if add:
                    self.shared[o.ticker] = self.shared.get(o.ticker, 0) + add

    def _release_child(self, ticker, c):
        """Nhả phần reservation chưa khớp khi child đóng (hủy/từ chối/khớp hết)."""
        if not c.get("released"):
            c["released"] = True
            unfilled = c["qty"] - c.get("filled", 0)
            if unfilled:
                self.shared[ticker] = self.shared.get(ticker, 0) - unfilled

    def _save_state(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _journal(self, event, o=None, child_oid="", qty="", price="", note=""):
        new = not os.path.exists(self.journal_file)
        with open(self.journal_file, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["ts", "event", "parent_id", "ticker", "side",
                            "child_oid", "qty", "price", "filled_total", "note"])
            ps = self.state["parents"].get(o.id) if o else None
            w.writerow([dt.datetime.now().isoformat(timespec="seconds"), event,
                        o.id if o else "", o.ticker if o else "",
                        o.side if o else "", child_oid, qty, price,
                        ps["filled"] if ps else "", note])

    # ------------------------------------------------------------ pricing/sizing

    def _record_prices(self, now, phase):
        """Lấy mẫu giá last mỗi px_sample_sec cho các mã còn lệnh → px_hist (tính r15).
        get_quote có TTL cache 3s nên chi phí ~1 call/phút/mã."""
        if phase in ("PRE", "CLOSED"):
            return
        hist = self.state.setdefault("px_hist", {})
        keep_from = (now - dt.timedelta(minutes=40)).isoformat(timespec="seconds")
        for o in self.plan.orders:
            if self.state["parents"][o.id]["done"]:
                continue
            h = hist.setdefault(o.ticker, [])
            if h and (now - dt.datetime.fromisoformat(h[-1][0])).total_seconds() \
                    < self.cfg["px_sample_sec"]:
                continue
            q = self.broker.get_quote(o.ticker)
            if q and q.ok() and q.last:
                h.append([now.isoformat(timespec="seconds"), q.last])
                hist[o.ticker] = [s for s in h if s[0] >= keep_from]

    def _r15(self, ticker, now):
        """Return ~dip_window_min phút gần nhất từ px_hist; None = chưa đủ lịch sử."""
        h = self.state.get("px_hist", {}).get(ticker) or []
        if not h:
            return None
        # mẫu hiện tại phải tươi (≤2 chu kỳ sample)
        if (now - dt.datetime.fromisoformat(h[-1][0])).total_seconds() \
                > 2 * self.cfg["px_sample_sec"] + 5:
            return None
        win = self.cfg["dip_window_min"]
        best = None
        for ts, px in h:
            age = (now - dt.datetime.fromisoformat(ts)).total_seconds() / 60.0
            if 0.7 * win <= age <= 2.0 * win and \
                    (best is None or abs(age - win) < abs(best[0] - win)):
                best = (age, px)
        if best is None or best[1] <= 0:
            return None
        return h[-1][1] / best[1] - 1.0

    def _decide_cross(self, o, now, q=None):
        """→ (cross: bool, note).

        cross_mode="adaptive" (default): DIP khi order_value/ADV < threshold,
          TWAP (always cross) khi >=. ADV proxy = q.day_volume × giá hiện tại.
        cross_mode="always": cross mọi slice (TWAP, archived).
        cross_mode="dip": S2 mean-reversion 15' (archived).
        Urgency "high" → cross ngay bất kể mode.
        """
        if o.urgency == "high":
            return True, ""
        mode = self.cfg.get("cross_mode", "adaptive")
        if mode == "adaptive":
            return self._decide_cross_adaptive(o, now, q)
        if mode == "dip":
            r = self._r15(o.ticker, now)
            if r is None:
                return True, "dip:no-hist"
            side = 1 if o.side == "buy" else -1
            if r * side <= 0:
                return True, f"dip:cross r15={r*100:+.2f}%"
            return False, f"dip:passive r15={r*100:+.2f}%"
        # "always" or unknown → TWAP
        return (bool(self.cfg["buy_cross_spread"]) if o.side == "buy" else True), ""

    def _decide_cross_adaptive(self, o, now, q):
        """SIZE-ADAPTIVE: DIP khi order_value/ADV < threshold; TWAP khi >=.

        ADV proxy = q.day_volume (shares khớp hôm nay) × giá tham chiếu.
        Thiếu dữ liệu volume → TWAP (fail-safe, đảm bảo fill).
        DIP nhánh: dùng r15 mean-reversion; thiếu lịch sử → cross (safe).
        """
        ps = self.state["parents"][o.id]
        remaining = o.qty - ps["filled"]
        threshold = self.cfg.get("adaptive_cross_adv_threshold", 0.01)

        ref_px = ((q.ask or q.bid or q.last) if q else None) or o.ref_price
        order_value = remaining * ref_px if ref_px else 0

        use_twap = True
        ratio_str = "no-vol"
        if q and getattr(q, "day_volume", None) and q.day_volume > 0 and ref_px > 0:
            adv_value = q.day_volume * ref_px
            ratio = order_value / adv_value
            ratio_str = f"{ratio*100:.2f}%"
            use_twap = ratio >= threshold

        if use_twap:
            return True, f"adp:twap(ratio={ratio_str}>={threshold*100:.0f}%ADV)"

        # Small order → DIP (mean-reversion 15')
        r = self._r15(o.ticker, now)
        if r is None:
            return True, f"adp:dip(ratio={ratio_str},no-hist→cross)"
        side = 1 if o.side == "buy" else -1
        if r * side <= 0:
            return True, f"adp:dip(ratio={ratio_str},r15={r*100:+.2f}%→cross)"
        return False, f"adp:dip(ratio={ratio_str},r15={r*100:+.2f}%→passive)"

    def _limit_price(self, o, q, cross=True):
        """Giá LO cho lệnh con; None = không đặt được (thiếu quote)."""
        ex = q.exchange or "HOSE"
        last = q.last or q.ref or o.ref_price
        tick = tick_size(last, o.ticker, ex)
        if o.side == "buy":
            cap = o.ref_price * (1 + self.cfg["max_chase_pct_buy"])
            if q.ceiling:
                cap = min(cap, q.ceiling)
            desired = (q.ask if (cross and q.ask) else
                       (q.bid + self.cfg["chase_ticks"] * tick) if q.bid else last)
            px = min(desired, cap)
            px = round_price(px, o.ticker, ex, "down")
            if q.floor:
                px = max(px, q.floor)
        else:
            floor_cap = o.ref_price * (1 - self.cfg["max_chase_pct_sell"])
            if q.floor:
                floor_cap = max(floor_cap, q.floor)
            if cross:
                desired = q.bid if q.bid else last - self.cfg["chase_ticks"] * tick
            else:   # passive sell: nằm ở ask chờ nhịp hồi chạm tới
                desired = q.ask if q.ask else last + self.cfg["chase_ticks"] * tick
            px = max(desired, floor_cap)
            px = round_price(px, o.ticker, ex, "up")
            if q.ceiling:
                px = min(px, q.ceiling)
        return px if px and px > 0 else None

    def _child_qty(self, o, ps, q, px):
        remaining = o.qty - ps["filled"]
        by_value = int(self.cfg["max_child_value"] / px) if px else remaining
        qty = min(remaining, by_value)
        if q.day_volume:   # quota fleet: tổng đã khớp MỌI account ≤ p% KL ngày của mã
            fleet_filled = self.shared.get(o.ticker, 0)
            allowance = int(self.cfg["max_participation"] * q.day_volume) - fleet_filled
            if allowance < LOT:
                return 0
            qty = min(qty, allowance)
        qty = round_lot(qty)
        # mảnh cuối < 1 lô sau làm tròn nhưng remaining ≥ 1 lô → đẩy hết remaining nếu nhỏ
        if qty < LOT <= remaining and remaining * (px or 0) <= self.cfg["max_child_value"]:
            qty = round_lot(remaining)
        return qty

    # ------------------------------------------------------------ child lifecycle

    def _open_child(self, ps):
        for c in ps["children"]:
            if c["status"] == "open":
                return c
        return None

    def _sync_fills(self, updates):
        for o in self.plan.orders:
            ps = self.state["parents"][o.id]
            if ps["done"]:
                continue
            total = 0
            for c in ps["children"]:
                u = updates.get(c["oid"])
                if u is not None:
                    if u.filled_qty > c.get("filled", 0):
                        delta = min(u.filled_qty, c["qty"]) - c.get("filled", 0)
                        c["filled"] = min(u.filled_qty, c["qty"])
                        if c.get("released"):   # fill về muộn sau khi đã nhả quota
                            self.shared[o.ticker] = self.shared.get(o.ticker, 0) + delta
                        self._journal("FILL", o, c["oid"], c["filled"],
                                      u.avg_price or c["price"])
                    if c["status"] == "open" and u.is_dead:
                        c["status"] = "closed"
                        self._release_child(o.ticker, c)
                total += c.get("filled", 0)
            ps["filled"] = min(total, o.qty)
            if ps["filled"] >= o.qty:
                ps["done"] = True
                self._journal("DONE", o, note=f"khớp đủ {o.qty:,}")

    def _cancel_stale(self, now):
        max_age = self.cfg["slice_interval_min"] * 60
        for o in self.plan.orders:
            ps = self.state["parents"][o.id]
            c = self._open_child(ps)
            if not c:
                continue
            age = (now - dt.datetime.fromisoformat(c["ts"])).total_seconds()
            if age > max_age:
                try:
                    self.broker.cancel_order(c["oid"])
                    c["status"] = "cancelled"
                    self._release_child(o.ticker, c)
                    self._journal("CANCEL_STALE", o, c["oid"], c["qty"] - c.get("filled", 0),
                                  c["price"], note=f"treo {age/60:.0f}p")
                except Exception as e:
                    self._journal("CANCEL_FAIL", o, c["oid"], note=str(e))

    def _fill_timing_mult(self, o, now):
        """Fill-Timing Layer (Layer-3): trả interval multiplier theo cửa sổ tối ưu.
        1.0 = tốc độ bình thường (trong cửa sổ); N = interval × N (ngoài cửa sổ).
        BUY: tập trung 10:45-11:15 (đáy intraday); sáng sớm = slow; chiều = normal.
        SELL: tập trung Open 09:15-09:45 (morning premium); còn lại = slow.
        """
        if not self.cfg.get("fill_timing_enabled", True):
            return 1.0
        if o.urgency == "high":
            return 1.0
        if self.cfg.get("fill_timing_live_gate", True) and self.cfg.get("mode") != "paper":
            return 1.0
        t = now.time()
        mult = self.cfg.get("fill_timing_outside_mult", 4.0)
        if o.side == "buy":
            # Phiên chiều (13:00+): morning premium không còn → tốc độ bình thường
            if t >= dt.time(13, 0):
                return 1.0
            ws = _parse_hhmm(self.cfg.get("buy_window_start", "10:45"))
            we = _parse_hhmm(self.cfg.get("buy_window_end", "11:15"))
            return 1.0 if ws <= t < we else mult
        else:  # sell: tập trung ở Open
            ws = _parse_hhmm(self.cfg.get("sell_window_start", "09:15"))
            we = _parse_hhmm(self.cfg.get("sell_window_end", "09:45"))
            return 1.0 if ws <= t < we else mult

    def _place_slices(self, now, phase):
        base_interval = self.cfg["slice_interval_min"] * 60
        for o in sorted(self.plan.orders, key=lambda x: x.priority):
            ps = self.state["parents"][o.id]
            if ps["done"] or self._open_child(ps):
                continue
            interval = base_interval * self._fill_timing_mult(o, now)
            if ps["last_slice_ts"]:
                since = (now - dt.datetime.fromisoformat(ps["last_slice_ts"])).total_seconds()
                if since < interval and ps["children"]:
                    continue
            q = self.broker.get_quote(o.ticker)
            if q is None or not q.ok():
                self._journal("NO_QUOTE", o, note="thiếu quote — thử lại sau")
                continue
            cross, dip_note = self._decide_cross(o, now, q)
            px = self._limit_price(o, q, cross)
            if px is None:
                continue
            qty = self._child_qty(o, ps, q, px)
            if qty < LOT:
                self._journal("WAIT_QUOTA", o, note="hết quota participation/đợi KL")
                continue
            if o.side == "buy":
                need = qty * px * 1.0025
                if self.broker.get_cash() < need:
                    self._journal("WAIT_CASH", o, qty=qty, price=px,
                                  note="thiếu tiền — chờ lệnh bán khớp")
                    continue
            try:
                oid = self.broker.place_order(o.ticker, qty, o.side, price=px)
            except Exception as e:
                self._journal("PLACE_FAIL", o, qty=qty, price=px, note=str(e))
                continue
            ps["children"].append({"oid": oid, "qty": qty, "price": px, "filled": 0,
                                   "status": "open",
                                   "ts": now.isoformat(timespec="seconds")})
            self.shared[o.ticker] = self.shared.get(o.ticker, 0) + qty  # reserve quota
            ps["last_slice_ts"] = now.isoformat(timespec="seconds")
            capped = (o.side == "buy" and cross and q.ask and px < q.ask)
            ft_mult = self._fill_timing_mult(o, now)
            ft_note = (f"ft:in-window" if ft_mult == 1.0 and self.cfg.get("fill_timing_enabled")
                       else f"ft:out×{ft_mult:.0f}" if self.cfg.get("fill_timing_enabled")
                       else "")
            notes = [n for n in (dip_note,
                                 "nằm chờ tại trần đuổi" if capped else "",
                                 ft_note) if n]
            self._journal("PLACE", o, oid, qty, px, note="; ".join(notes))

    def _atc_sweep(self):
        for o in self.plan.orders:
            ps = self.state["parents"][o.id]
            if ps["done"] or ps["atc_sent"]:
                continue
            flag = (self.cfg["atc_remainder_sell"] if o.side == "sell"
                    else self.cfg["atc_remainder_buy"])
            if not flag:
                continue
            c = self._open_child(ps)
            if c:
                try:
                    self.broker.cancel_order(c["oid"])
                    c["status"] = "cancelled"
                    self._release_child(o.ticker, c)
                except Exception:
                    pass
            remaining = round_lot(o.qty - ps["filled"])
            if remaining < LOT:
                continue
            try:
                oid = self.broker.place_order(o.ticker, remaining, o.side,
                                              price=None, order_type="ATC")
                ps["children"].append({"oid": oid, "qty": remaining, "price": None,
                                       "filled": 0, "status": "open",
                                       "ts": dt.datetime.now().isoformat(timespec="seconds")})
                ps["atc_sent"] = True
                self._journal("ATC", o, oid, remaining, note="quét ATC phần còn lại")
            except Exception as e:
                self._journal("ATC_FAIL", o, note=str(e))

    def cancel_all_open(self, reason):
        for o in self.plan.orders:
            ps = self.state["parents"][o.id]
            c = self._open_child(ps)
            if c:
                try:
                    self.broker.cancel_order(c["oid"])
                    c["status"] = "cancelled"
                    self._release_child(o.ticker, c)
                    self._journal("CANCEL", o, c["oid"], note=reason)
                except Exception as e:
                    self._journal("CANCEL_FAIL", o, c["oid"], note=str(e))

    # ------------------------------------------------------------ một chu kỳ

    @property
    def all_done(self):
        return all(p["done"] for p in self.state["parents"].values())

    def step(self, now, phase, cont):
        """Một chu kỳ cho account này. → True nếu mọi parent đã xong."""
        try:
            self._sync_fills(self.broker.poll_orders())
        except Exception as e:
            self._journal("POLL_FAIL", note=str(e))
        if self.all_done:
            self._save_state()
            return True
        try:
            self._record_prices(now, phase)
        except Exception as e:
            self._journal("PX_HIST_FAIL", note=str(e))
        if cont:
            self._cancel_stale(now)
            self._place_slices(now, phase)
        elif phase == "ATC":
            self._atc_sweep()
        self._save_state()
        return self.all_done

    # ------------------------------------------------------------ report

    def write_report(self):
        lines = [f"# Execution report — [{self.label}] {self.plan.plan_date}",
                 f"*Strategy*: {self.plan.strategy} v{self.plan.strategy_version} | "
                 f"*Broker*: {self.broker.name} | "
                 f"*Generated*: {dt.datetime.now():%Y-%m-%d %H:%M}", "",
                 "| order | ticker | side | plan qty | filled | % | ref px | children |",
                 "|---|---|---|---:|---:|---:|---:|---:|"]
        tot_plan = tot_fill = 0
        for o in self.plan.orders:
            ps = self.state["parents"][o.id]
            pct = 100.0 * ps["filled"] / o.qty if o.qty else 0
            tot_plan += o.value
            fills = [c for c in ps["children"] if c.get("filled")]
            avg = (sum(c["filled"] * (c["price"] or o.ref_price) for c in fills) /
                   max(1, sum(c["filled"] for c in fills))) if fills else 0
            tot_fill += ps["filled"] * (avg or o.ref_price)
            lines.append(f"| {o.id} | {o.ticker} | {o.side} | {o.qty:,} | "
                         f"{ps['filled']:,} | {pct:.0f}% | {o.ref_price:,.0f} | "
                         f"{len(ps['children'])} |")
        lines += ["", f"*Plan gross*: {tot_plan/1e6:,.0f}M | "
                      f"*Executed*: {tot_fill/1e6:,.0f}M "
                      f"({100*tot_fill/tot_plan if tot_plan else 0:.0f}%)"]
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"[exec:{self.label}] report → {self.report_file}")
        return tot_plan, tot_fill


# ================================================================ session loop

def run_session(executors, once=False, max_cycles=None, force_phase=None):
    """Vòng lặp xuyên phiên cho 1..N account. Sổ participation dùng chung —
    truyền cùng 1 dict `shared` khi tạo các Executor (run_accounts lo việc này)."""
    poll = min(e.cfg["poll_interval_sec"] for e in executors)
    for e in executors:
        e.seed_shared()
        print(f"[exec:{e.label}] plan {e.plan.plan_date}: {len(e.plan.orders)} lệnh, "
              f"gross {e.plan.gross_value/1e6:,.0f}M — broker={e.broker.name}")
    cycles = 0
    while True:
        cycles += 1
        now = dt.datetime.now()
        phase, cont = (force_phase, force_phase in ("MORNING", "AFTERNOON")) \
            if force_phase else session_phase(now)

        if os.path.exists(STOP_FILE):
            print("[exec] 🛑 BOT_STOP — hủy lệnh treo mọi account và thoát")
            for e in executors:
                e.cancel_all_open("BOT_STOP")
                e._save_state()
            break

        statuses = []
        for e in executors:
            try:
                statuses.append(e.step(now, phase, cont))
            except Exception as ex:   # 1 account lỗi không kéo chết account khác
                e._journal("STEP_FAIL", note=str(ex))
                statuses.append(False)
        if all(statuses):
            print("[exec] ✅ tất cả account đã khớp đủ")
            break

        if phase == "CLOSED" and not force_phase:
            print("[exec] hết phiên — dừng")
            for e in executors:
                e.cancel_all_open("EOD")
                e._save_state()
            break

        if once or (max_cycles and cycles >= max_cycles):
            break
        time.sleep(poll)

    tot_plan = tot_fill = 0
    for e in executors:
        p, f = e.write_report()
        tot_plan += p
        tot_fill += f
    if len(executors) > 1:
        print(f"[exec] FLEET: plan {tot_plan/1e6:,.0f}M | executed {tot_fill/1e6:,.0f}M "
              f"({100*tot_fill/tot_plan if tot_plan else 0:.0f}%) "
              f"trên {len(executors)} account")
