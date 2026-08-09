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
import glob
import json
import os
import subprocess
import time

from .config import EXEC_DIR, STOP_FILE
from .plan_funding_gate import _effective_loan_package

# Root of the Mike fleet (two levels up from trading_bot/).
_MIKE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "mike")
_APPEND_EVENT = os.path.join(_MIKE_ROOT, "bin", "append_event.sh")


def _publish_bot_event(event_type: str, topic: str, payload: dict) -> None:
    """Push a bot event to the Mike fleet bus (fire-and-forget, never raises).

    event_type: "error" | "status" | "finding"
    topic: short slug, e.g. "STEP_FAIL" or "fill_lagging"
    payload: dict serialised to JSON

    TEST-MODE GUARD (2026-08-08): selfcheck/pytest runs constructing an Executor
    reach these call sites and used to write FAKE events onto the production bus
    labelled `agent_id=Mafee` (232 events counted on the bus across 08-03/04/05/07:
    149 LEVER_PACKAGE_UNAUTHORIZED + 83 dd-redflag-fill — retro-2026-08-07
    Pattern 1). Existing fields (account label, plan_date sentinel,
    strategy) are NOT reliable test signals (inconsistent across selfcheck files),
    so the gate is an explicit env var: selfchecks set MIKE_BOT_TEST_MODE=1;
    pytest sets PYTEST_CURRENT_TEST by itself.
    MIKE_BOT_TEST_EVENT_SINK (optional) = path to append the suppressed events to,
    so a test can still assert an event WOULD have fired.
    """
    if os.environ.get("MIKE_BOT_TEST_MODE") == "1" or os.environ.get("PYTEST_CURRENT_TEST"):
        sink = os.environ.get("MIKE_BOT_TEST_EVENT_SINK")
        if sink:
            try:
                with open(sink, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"event_type": event_type, "topic": topic,
                                         "payload": payload}, ensure_ascii=False) + "\n")
            except Exception:
                pass
        return
    if not os.path.isfile(_APPEND_EVENT):
        return
    try:
        subprocess.Popen(
            [_APPEND_EVENT, "Mafee", event_type, topic, json.dumps(payload, ensure_ascii=False)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            close_fds=True,
        )
    except Exception:
        pass
from .vn_market import session_phase, tick_size, round_price, round_lot, LOT, now_ict
from .brokers import qget

_GAP_Z_DOWN_THRESHOLD = -2.0  # gap_z < this on a BUY → full-speed 09:15-09:45


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
        self._gap_ref = {}      # ticker -> {prior_close, rvol_20d}; loaded once at startup
        self._gap_z_cache = {}  # ticker -> gap_z or None (None = fail-safe, no override)
        self._last_gap_override = {}  # ticker -> gap_z; populated when override fires this tick
        self._extreme_state = {}      # ticker -> {"n": confirm-count, "until": iso}; EXTREME-regime gate
        self._extreme_cache = {}      # (ticker, now) -> bool; memoise _extreme_regime_raw so a
                                       # cycle where BOTH _cancel_stale (via _would_be_unchanged)
                                       # AND _place_slices ask only mutates the 2-poll counter once
        self._load_gap_ref_data()
        # ticker -> ADV20 causal (giá trị giao dịch VND, TỔNG cả fleet) cho lệnh CAPIT.
        # Rỗng {} = không phải phiên CAPIT, hoặc artifact thiếu/stale → _child_qty tự
        # fail-safe về guard realtime cũ. Xem _load_capit_adv20_basis().
        self._capit_adv20_vnd = self._load_capit_adv20_basis()
        # ticker -> ADV20 (adv_ref_vnd) cho lệnh DISCRETIONARY_SPECIAL — nguồn KHÁC CAPIT:
        # đọc từ state file riêng của từng case (state_<TICKER>_<account>.json). Rỗng/thiếu
        # → cùng fail-safe về guard realtime cũ. Xem _load_discretionary_adv20_basis().
        self._disc_adv20_vnd = self._load_discretionary_adv20_basis()
        self.state = self._load_state()
        self._step_fail_count = 0   # consecutive STEP_FAIL counter for escalation

    @staticmethod
    def _is_capit_buy(o):
        return (o.book or "").upper() == "CAPIT" and (o.side or "").lower() == "buy"

    def _load_capit_adv20_basis(self, status_path=None):
        """ticker -> ADV20 causal (giá trị giao dịch VND, TỔNG cả fleet) cho lệnh CAPIT.

        Đọc cùng artifact mà plan.cap_capit_orders() dùng (data/golive_v23_status.json).
        ADV20_vnd = capit_adv_caps_total[t] / (capit_adv_x · capit_adv_d) — đảo ngược đúng
        công thức golive_recommend_v23.py:132 (cap_vnd = X·ADV20·D), KHÔNG tính lại khác đi.
        Dùng caps_TOTAL (không chia account) vì self.shared = KL fleet đã khớp trên MỌI
        account, khớp đúng ngữ nghĩa guard fleet-level trong _child_qty.

        FAIL-SAFE (trả {} → _child_qty tự lùi về guard realtime cũ, KHÔNG mua vô hạn):
        không có lệnh CAPIT buy / thiếu file / signal_date artifact ≠ plan (artifact cũ) /
        thiếu capit_adv_caps_total / thiếu-sai capit_adv_x·d. Đây là lớp phòng thủ THỨ HAI:
        cap_capit_orders() đã CHẶN lệnh CAPIT ở tầng plan khi artifact hỏng trước khi tới đây.
        """
        if not any(self._is_capit_buy(o) for o in self.plan.orders):
            return {}
        from .config import WORKDIR
        path = status_path or os.path.join(WORKDIR, "data", "golive_v23_status.json")
        try:
            with open(path, encoding="utf-8") as f:
                st = json.load(f)
            if (st.get("signal_date") and self.plan.signal_date
                    and st["signal_date"] != self.plan.signal_date):
                return {}
            caps_total = st.get("capit_adv_caps_total") or {}
            x = st.get("capit_adv_x")
            d = st.get("capit_adv_d")
            if not (isinstance(x, (int, float)) and isinstance(d, (int, float))
                    and x > 0 and d > 0):
                return {}
            out = {}
            for t, v in caps_total.items():
                if isinstance(v, (int, float)) and v > 0:
                    out[t] = float(v) / (x * d)     # = ADV20_vnd
            return out
        except Exception:
            return {}

    @staticmethod
    def _is_discretionary_special_buy(o):
        return (o.book or "").upper() == "DISCRETIONARY_SPECIAL" and (o.side or "").lower() == "buy"

    def _load_discretionary_adv20_basis(self, base_dir=None):
        """ticker -> ADV20 (adv_ref_vnd, VND) cho lệnh DISCRETIONARY_SPECIAL buy.

        Đọc adv_ref_vnd từ state file RIÊNG của từng case theo quy ước playbook
        lowliq_execution_playbook_20260724.md: data/trade_plans/discretionary/
        state_<TICKER>_<account>.json. TỔNG QUÁT — không hardcode TV1; case sau (DGC/…)
        đăng ký state cùng convention là tự được nhận diện.

        Nguồn ADV20 KHÁC CAPIT: CAPIT lấy từ golive_v23_status.json (fleet-level, chia đảo
        ngược từ cap_vnd), còn DISCRETIONARY_SPECIAL lấy adv_ref_vnd đã đo sẵn trong state.
        adv_ref_vnd là turnover 1 phiên (median 20 phiên), dùng CHUNG ngữ nghĩa với ADV20
        CAPIT trong _child_qty (floor = max_participation × ADV20 / px).

        FAIL-SAFE (bỏ qua ticker → _child_qty tự lùi về guard %KL-ngày cũ, KHÔNG mua vô hạn):
        không có lệnh DISCRETIONARY_SPECIAL buy / thiếu file state / thiếu-sai adv_ref_vnd /
        state không có (order phát sinh thủ công không đăng ký playbook) → ticker vắng khỏi
        dict → nhánh elif q.day_volume cũ áp dụng như trước (không crash).
        """
        disc_orders = [o for o in self.plan.orders if self._is_discretionary_special_buy(o)]
        if not disc_orders:
            return {}
        from .config import WORKDIR
        base = base_dir or os.path.join(WORKDIR, "data", "trade_plans", "discretionary")
        out = {}
        for o in disc_orders:
            path = os.path.join(base, f"state_{o.ticker}_{self.label}.json")
            try:
                with open(path, encoding="utf-8") as f:
                    st = json.load(f)
                v = st.get("adv_ref_vnd")
                if isinstance(v, (int, float)) and v > 0:
                    out[o.ticker] = float(v)
            except Exception:
                continue
        return out

    def _adv20_basis_for(self, o):
        """ADV20 (turnover VND) cho lệnh cần pacing theo ADV20 thay vì %KL-ngày, hoặc None.

        None → KHÔNG phải lệnh cần ADV20-pacing (CAPIT/DISCRETIONARY_SPECIAL buy), HOẶC
        thiếu nguồn ADV20 → _child_qty fail-safe về guard %KL-ngày thật (KHÔNG mua vô hạn).
        Route theo book để 2 nguồn ADV20 (CAPIT vs DISCRETIONARY_SPECIAL) không lẫn nhau.
        """
        if self._is_capit_buy(o):
            return self._capit_adv20_vnd.get(o.ticker)
        if self._is_discretionary_special_buy(o):
            return self._disc_adv20_vnd.get(o.ticker)
        return None

    # ------------------------------------------------------------ state/journal

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, encoding="utf-8") as f:
                st = json.load(f)
            if st.get("plan_created_at") == self.plan.created_at:
                print(f"[exec:{self.label}] resume từ {self.state_file}")
                st.setdefault("exchange_override", {})  # state cũ (trước fix) chưa có key này
                # Reconcile: plan.orders có thể ĐÔNG hơn state cũ nếu 1 fail-safe (vd
                # cap_capit_orders) đã loại tạm vài order khi state được tạo lần đầu rồi sau
                # đó plan đầy đủ trở lại mà created_at KHÔNG đổi (incident ZaloPay 2026-07-21).
                # Backfill parent MỚI đúng format fresh-state cho order còn thiếu — KHÔNG động
                # vào parent đã tồn tại (giữ nguyên filled/done/children đã ghi nhận).
                st.setdefault("parents", {})
                for o in self.plan.orders:
                    st["parents"].setdefault(o.id, {"filled": 0, "done": False,
                                                    "atc_sent": False, "children": [],
                                                    "last_slice_ts": None,
                                                    "dcf_check": o.dcf_check})
                return st
            print(f"[exec:{self.label}] ⚠ plan đã đổi so với state cũ — state mới")
        return {"plan_date": self.plan.plan_date,
                "plan_created_at": self.plan.created_at,
                "px_hist": {},          # ticker -> [[ts, last], …] phục vụ r15 (dip-cross)
                "exchange_override": {},  # ticker -> "HOSE"|"HNX" học được sau 1 lần bị từ chối
                                          # tick-size (xem _is_invalid_tick_lot + _place_slices)
                "parents": {o.id: {"filled": 0, "done": False, "atc_sent": False,
                                   "children": [], "last_slice_ts": None,
                                   "dcf_check": o.dcf_check}  # audit trail Pha 2 DCF
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
        # Atomic write (tmp + os.replace): _save_state() now runs far more often (right
        # after every place_order, not just once per cycle — see _ghost_tickers), so a
        # kill mid-write is more likely to be hit; a direct overwrite could truncate
        # state.json exactly when the idempotency guard needs it most. os.replace is a
        # single atomic rename on POSIX — readers always see either the old or new file,
        # never a partial one.
        tmp = self.state_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
        os.replace(tmp, self.state_file)

    def _journal(self, event, o=None, child_oid="", qty="", price="", note=""):
        # `book`/`play_type` (P0 book-tagging, 2026-08-04): tag sổ TẠI THỜI ĐIỂM khớp, để
        # dựng lại được vị thế theo book (PARK/LAG/CAPIT/...) mà không phải suy luận theo tên
        # mã — suy-luận-theo-tên đã sai thật với VPB (nằm cả LAG lẫn PARK). Nguồn là
        # PlannedOrder.book/.play_type đã có sẵn (plan.py:24-25), không đổi plan, không đụng
        # đường đặt lệnh. Ghi ở đây (không ở chỗ gọi) ⇒ MỌI event được tag đồng nhất.
        # ⚠️ Chèn TRƯỚC `note`: `note` là trường tự do có thể chứa dấu phẩy, giữ nó ở cột
        # cuối là quy ước của file này; đồng thời chỉ số cột 0-8 giữ nguyên nên các reader
        # positional hiện có (row[1] == event) không vỡ. Journal CŨ có 10 cột, journal MỚI
        # có 12 ⇒ reader phải dùng csv.DictReader + row.get("book", ""), không đọc theo vị trí.
        new = not os.path.exists(self.journal_file)
        # File ĐANG MỞ DỞ do bản code CŨ tạo (10 cột) — chỉ xảy ra khi executor khởi động lại
        # giữa phiên ngay sau khi deploy thay đổi này. Ghi 12 giá trị dưới một header 10 cột sẽ
        # làm cả file lệch cột (DictReader đọc `note` thành `book`) ⇒ giữ nguyên layout CŨ cho
        # đúng file đó. Hệ quả: phiên đó không có tag ⇒ park_holdings coi là chưa xác định
        # (UNVERIFIED) và L1 tự chặn — fail-safe, không phải im lặng sai.
        legacy = False
        if not new:
            try:
                with open(self.journal_file, newline="", encoding="utf-8") as rf:
                    legacy = "book" not in (next(csv.reader(rf), []) or [])
            except (OSError, StopIteration):
                legacy = False
        with open(self.journal_file, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["ts", "event", "parent_id", "ticker", "side",
                            "child_oid", "qty", "price", "filled_total",
                            "book", "play_type", "note"])
            ps = self.state["parents"].get(o.id) if o else None
            row = [now_ict().isoformat(timespec="seconds"), event,
                   o.id if o else "", o.ticker if o else "",
                   o.side if o else "", child_oid, qty, price,
                   ps["filled"] if ps else ""]
            if not legacy:
                row += [(getattr(o, "book", "") or "") if o else "",
                        (getattr(o, "play_type", "") or "") if o else ""]
            w.writerow(row + [note])

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

    def _buy_chase_pct(self, ticker):
        """Buy chase-cap %: static max_chase_pct_buy, optionally widened by 20d realised vol
        (clamp(k*rvol_20d, static, ceil)) when chase_cap_vol_scale_enabled. Monotone-safe (never
        below the static cap) and fail-safe to static when disabled or rvol_20d absent/<=0."""
        static = self.cfg["max_chase_pct_buy"]
        if not self.cfg.get("chase_cap_vol_scale_enabled", False):
            return static
        ref = self._gap_ref.get(ticker)
        rvol = ref.get("rvol_20d") if ref else None
        if not rvol or rvol <= 0:
            return static
        k = self.cfg.get("chase_cap_vol_k", 2.0)
        ceil = self.cfg.get("chase_cap_vol_ceil", 0.04)
        return min(max(k * rvol, static), ceil)

    @staticmethod
    def _hard_buy_ceiling(o):
        """Trần giá MUA tuyệt đối (VND) của lệnh, hoặc None nếu không đặt trần.

        Chỉ áp cho side="buy" — lệnh BÁN không có khái niệm "mua đuổi". Giá trị rác
        (không parse được, ≤0) → None = hành vi cũ, KHÔNG bao giờ nới trần vì lỗi parse."""
        if o.side != "buy":
            return None
        try:
            v = float(getattr(o, "hard_no_chase_ceiling_vnd", None) or 0)
        except (TypeError, ValueError):
            return None
        return v if v > 0 else None

    def _limit_price(self, o, q, cross=True, extreme=False):
        """Giá LO cho lệnh con; None = không đặt được (thiếu quote).

        extreme=True (EXTREME-regime SELL only): nới sàn đuổi từ ref×(1−3%) xuống thẳng
        q.floor để bán tới sàn (thoát dứt điểm) thay vì nằm kẹt tại −3% khi giá gap thủng.

        BUY có `o.hard_no_chase_ceiling_vnd` (VND tuyệt đối, vd anchor entry-window LAG):
        trần đó là BẤT BIẾN — min() với trần đuổi %, và nếu kết quả cuối vẫn > trần (chỉ xảy
        ra khi chính giá SÀN phiên đã trên trần) thì trả None = KHÔNG đặt lệnh. Nhờ trần
        tuyệt đối này, `desired = q.ask` (giá đang chào THẬT, đọc lại mỗi chu kỳ) mới là thứ
        quyết định giá đặt — bám thị trường mà không bao giờ vượt trần.
        """
        ex = self.state.get("exchange_override", {}).get(o.ticker) or q.exchange or "HOSE"
        last = q.last or q.ref or o.ref_price
        tick = tick_size(last, o.ticker, ex)
        if o.side == "buy":
            cap = o.ref_price * (1 + self._buy_chase_pct(o.ticker))
            if q.ceiling:
                cap = min(cap, q.ceiling)
            hard = self._hard_buy_ceiling(o)
            if hard:
                cap = min(cap, hard)
            desired = (q.ask if (cross and q.ask) else
                       (q.bid + self.cfg["chase_ticks"] * tick) if q.bid else last)
            px = min(desired, cap)
            px = round_price(px, o.ticker, ex, "down")
            if q.floor:
                px = max(px, q.floor)
            if hard and px > hard:
                # giá sàn phiên đã > trần tuyệt đối → không tồn tại giá hợp lệ nào ≤ trần.
                # KHÔNG đặt lệnh (thà lỡ phiên còn hơn mua trên anchor).
                return None
        else:
            floor_cap = o.ref_price * (1 - self.cfg["max_chase_pct_sell"])
            if q.floor:
                floor_cap = max(floor_cap, q.floor)
            if extreme and q.floor:
                floor_cap = q.floor          # EXTREME sell-to-floor: bỏ trần −3%, đuổi xuống sàn
            if cross:
                desired = q.bid if q.bid else last - self.cfg["chase_ticks"] * tick
            else:   # passive sell: nằm ở ask chờ nhịp hồi chạm tới
                desired = q.ask if q.ask else last + self.cfg["chase_ticks"] * tick
            px = max(desired, floor_cap)
            px = round_price(px, o.ticker, ex, "up")
            if q.ceiling:
                px = min(px, q.ceiling)
        return px if px and px > 0 else None

    @staticmethod
    def _is_invalid_tick_lot(e):
        """True nếu lỗi broker là do giá không đúng bước giá (tick), KHÔNG phải lý do khác
        (hết tiền, sai mã, mất phiên...). Xác nhận thật từ log live 2026-07-01 (SHS/MBS):
        DNSE trả 'HTTP 400: Invalid price lot' khi giá tính theo bước giá HOSE (10/50/100 theo
        vùng giá) bị áp nhầm cho mã HNX/UPCOM (bước giá cố định 100đ) hoặc ngược lại."""
        if getattr(e, "status", None) != 400:
            return False
        return "price lot" in str(e).lower() or "invalid price" in str(e).lower()

    def _retry_tick_mismatch(self, o, q, cross, extreme_down, px, qty, err):
        """Khi place_order lỗi vì SAI BƯỚC GIÁ (xem `_is_invalid_tick_lot`): thử lại NGAY MỘT
        LẦN với quy ước bước giá còn lại (HOSE↔HNX/UPCOM — UPCOM dùng chung tick cố định 100đ
        với HNX nên chỉ cần đảo 2 chiều). Không tự đoán/khẳng định `exchange` thật của DNSE trả
        về gì — chỉ suy ra từ chính phản hồi CÓ THẬT của broker, không look-ahead, không giả định.
        Thành công → cache lại exchange đúng cho mã này (self.state, bền qua resume) để các lần
        sau tính đúng ngay từ đầu, không cần thử-sai lại. Trả (oid, px_mới) hoặc None nếu không
        áp dụng/không sửa được (caller giữ nguyên PLACE_FAIL cũ, không đổi hành vi)."""
        if not self._is_invalid_tick_lot(err):
            return None
        overrides = self.state.setdefault("exchange_override", {})
        if o.ticker in overrides:
            return None   # đã học rồi mà vẫn lỗi → không phải do tick, đừng thử vòng lặp vô hạn
        ex_used = q.exchange or "HOSE"
        ex_alt = "HNX" if ex_used == "HOSE" else "HOSE"
        overrides[o.ticker] = ex_alt          # tạm học để _limit_price dùng ngay bước giá thay thế
        px_alt = self._limit_price(o, q, cross, extreme=extreme_down)
        if px_alt is None or px_alt == px:
            overrides.pop(o.ticker, None)
            return None
        try:
            oid = self.broker.place_order(o.ticker, qty, o.side, price=px_alt,
                                          cash_only=getattr(o, "cash_only", False),
                                          loan_package_id=getattr(o, "loan_package_id", None))
        except Exception:
            overrides.pop(o.ticker, None)     # vẫn lỗi ở exchange thay thế → không phải do tick, bỏ học
            return None
        self._journal("TICK_RETRY_OK", o, oid, qty, px_alt,
                      note=f"'{ex_used}' tick sai ({err}) → thử '{ex_alt}' OK, cache lại cho {o.ticker}")
        return oid, px_alt

    def _child_qty(self, o, ps, q, px):
        remaining = o.qty - ps["filled"]
        if 0 < remaining < LOT:
            # Cổ phiếu lẻ (<1 lô, vd 10cp dư sau khi bán hết các lô chẵn) — DNSE nhận
            # đặt thẳng qua orderCategory=NORMAL/marketType=STOCK bình thường, KHÔNG
            # cần tham số riêng (verified 2026-07-09: lệnh thật id=172621, TCM 10cp,
            # orderCategory=NORMAL, orderStatus=New — user tự đặt qua app DNSE để xác
            # minh, user sau đó ủy quyền bot tự làm). round_lot() bên dưới chỉ áp cho
            # phần lô chẵn; phần lẻ luôn trả đúng số dư, không làm tròn về 0 (bug cũ:
            # mọi số dư <100 bị làm tròn xuống 0 và không bao giờ đặt được, kẹt vĩnh
            # viễn — xem kb/INCIDENTS.md 2026-07-09).
            return remaining
        by_value = int(self.cfg["max_child_value"] / px) if px else remaining
        qty = min(remaining, by_value)
        adv20_vnd = self._adv20_basis_for(o)
        if adv20_vnd and px:
            # LỆNH ADV20-PACED (CAPIT hoặc DISCRETIONARY_SPECIAL) — hybrid ADV20-floor +
            # realized-ceiling (job Taylor_20260721_053659 cho CAPIT; mở rộng sang
            # DISCRETIONARY_SPECIAL job Taylor_20260727_072910 — cùng lỗi WAIT_QUOTA oan như
            # NCT/TV1). CƠ SỞ pacing đổi từ q.day_volume real-time sang ADV20 causal (median
            # 20 phiên): một phiên mỏng bất thường của tên THỰC CHẤT thanh khoản không còn bị
            # WAIT_QUOTA oan. TRẦN PHỤ = capit_realized_participation_ceiling × KL khớp lũy kế
            # THẬT (dùng chung cho cả 2 book — cùng ngữ nghĩa "không thành đa số một phiên
            # mỏng", không có lý do tách): fleet không bao giờ thành đa số. allowance =
            # min(hai guard) → bị chặn bởi CẢ thanh khoản 20 phiên LẪN tape thật (fleet-level).
            fleet_filled = self.shared.get(o.ticker, 0)
            floor_allow = int(self.cfg["max_participation"] * adv20_vnd / px) - fleet_filled
            if q.day_volume:
                ceil_allow = int(self.cfg["capit_realized_participation_ceiling"]
                                 * q.day_volume) - fleet_filled
                allowance = min(floor_allow, ceil_allow)
            else:
                # halt / chưa có tape (Volume=0): chỉ còn ADV20-floor; khan người bán tự
                # giới hạn fill thực (không ai bán → lệnh treo, không đẩy giá — memo Result 2).
                allowance = floor_allow
            if allowance < LOT:
                return 0
            qty = min(qty, allowance)
        elif q.day_volume:   # non-CAPIT (hoặc CAPIT thiếu ADV20 → fail-safe guard cũ):
                             # tổng đã khớp MỌI account ≤ p% KL ngày của mã. GIỮ NGUYÊN.
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
                        # Audit-trail bus event khi mua mã DCF đang RICH+robust (Pha 2 DCF).
                        # Chỉ log — không chặn, không thay đổi execution logic.
                        _dcf = o.dcf_check
                        if (o.side == "buy" and _dcf and
                                _dcf.get("status") == "RICH" and _dcf.get("robust") is True):
                            _publish_bot_event("finding", "dcf-rich-fill", {
                                "ticker": o.ticker, "order_id": o.id,
                                "filled_delta": delta, "child_oid": c["oid"],
                                "dcf_check": _dcf,
                                "dcf_override_reason": o.dcf_override_reason or None,
                            })
                        # Audit-trail bus event khi mua mã có cờ ĐỎ due-diligence (2026-08-03,
                        # case DHD). Chỉ log — không chặn, không thay đổi execution logic; ĐÚNG
                        # cơ chế dcf-rich-fill ngay trên (kể cả khi ĐÃ có override, để đối chiếu
                        # sau: mã nào bị override, lý do gì, kết quả ra sao).
                        _dd = o.dd_check
                        if o.side == "buy" and _dd and _dd.get("has_red_flag") is True:
                            _publish_bot_event("finding", "dd-redflag-fill", {
                                "ticker": o.ticker, "order_id": o.id,
                                "filled_delta": delta, "child_oid": c["oid"],
                                "dd_check": _dd,
                                "dd_override_reason": o.dd_override_reason or None,
                            })
                    if c["status"] == "open" and u.is_dead:
                        c["status"] = "closed"
                        self._release_child(o.ticker, c)
                total += c.get("filled", 0)
            ps["filled"] = min(total, o.qty)
            if ps["filled"] >= o.qty:
                ps["done"] = True
                self._journal("DONE", o, note=f"khớp đủ {o.qty:,}")

    def _ghost_tickers(self, updates):
        """Idempotency guard — 2nd independent defense beyond fcntl.flock (added sau sự cố
        double-buy 2026-07-02: 2 process cùng khớp đủ 1 plan độc lập vì flock lúc đó chưa có).
        flock (bot_execute.py._acquire_account_lock) chặn 2 process CÙNG CHẠY; nhưng nếu process
        bị kill NGAY SAU broker.place_order() thành công nhưng TRƯỚC _save_state() kịp ghi (ví dụ
        OOM-kill/crash/reboot), lệnh đó tồn tại thật ở broker nhưng state.json không biết —
        lần chạy kế tiếp (dù chạy tuần tự, giữ lock đàng hoàng) sẽ đặt lệnh MỚI cho phần "còn
        thiếu" và double-buy lại, DNSE không hỗ trợ client idempotency-key nên không thể nhờ
        broker dedupe hộ.

        Vì vậy: mỗi step() đối chiếu sổ lệnh broker sống (updates = poll_orders(), gồi TOÀN BỘ
        lệnh trong ngày, không chỉ oid đã biết) với oid đã ghi trong state. Mã nào có lệnh
        broker KHÔNG nằm trong state (và lệnh đó có filled>0 hoặc còn sống — lệnh chết/0 fill an
        toàn bỏ qua) → trả về NGAY, KHÔNG tự suy đoán rồi gộp vào state (nguy cơ map sai field
        broker → filled/price sai còn tệ hơn); _place_slices/_atc_sweep phải TẠM DỪNG mã đó và
        báo người thật xử lý — cùng triết lý fail-safe-pause với WAIT_CASH/WAIT_QUOTA.

        UNPAUSE (thủ công, không có auto-resume — đúng chủ đích, human-in-the-loop): mã bị pause
        sẽ đứng cả ngày cho tới khi người thật thêm oid "ma" đó vào state["parents"][id]["children"]
        của mã tương ứng (đối soát bằng dnse_raw_<date>.jsonl hoặc broker.poll_orders() trực tiếp,
        rồi sửa exec_<label>_<date>_state.json tay hoặc script đối soát), sau đó _ghost_tickers sẽ
        không còn thấy oid đó "lạ" nữa ở chu kỳ kế tiếp. Không tự resume vì auto-reconcile rủi ro
        map sai field hơn là mất 1 ngày không mua/bán thêm mã đó."""
        known_oids = {c["oid"] for ps in self.state["parents"].values() for c in ps["children"]}
        plan_tickers = {o.ticker for o in self.plan.orders}
        ghosts = set()
        for oid, u in updates.items():
            if oid in known_oids:
                continue
            if u.filled_qty <= 0 and u.is_dead:
                continue  # chết, chưa khớp gì — không rủi ro tiền/CP, bỏ qua an toàn
            sym = qget(u.raw, "symbol", "instrument", "code") if isinstance(u.raw, dict) else None
            if sym in plan_tickers:
                ghosts.add(sym)
        return ghosts

    def _lever_package_audit(self, updates):
        """Lưới an toàn cho ĐÒN BẨY sleeve CAPIT — bắt đòn bẩy KHÔNG ĐƯỢC CẤP PHÉP.

        VÌ SAO CẦN, khi đã có _ghost_tickers: guard kia trả lời "có lệnh nào ở broker mà state
        không biết không" (chống double-buy) và nó ĐÃ phủ cả lệnh CAPIT vì nó xét theo mã của
        plan. Cái nó KHÔNG trả lời được — và là rủi ro MỚI mà tính năng đòn bẩy mang vào — là
        "lệnh đó đi ra bằng gói vay NÀO". Một lệnh đúng mã, đúng KL, nhưng mang gói 1840 trong
        khi chính sách đang TẮT (hoặc mang nó trên một mã ngoài rổ CAPIT) là đòn bẩy không ai
        duyệt: nợ vay thật, rủi ro margin call thật, mà mọi phép đối soát KL/mã đều PASS.

        Cơ chế: đọc gói vay THẬT trên sổ lệnh broker sống (`loanPackageId` có sẵn trong record
        đơn hàng DNSE — đã kiểm trên data/execution_logs/dnse_raw_*.jsonl) và so với tập mã mà
        cascade plan (trading_bot.plan.apply_capit_lever) đã cấp phép. Mã nào có lệnh mang gói
        đòn bẩy mà KHÔNG được cấp phép → trả về để step() TẠM DỪNG mã đó, y hệt đường xử lý
        ghost order (fail-safe-pause + người thật vào xem), KHÔNG tự huỷ lệnh (huỷ mù còn rủi ro
        hơn: có thể đã khớp một phần, và ta không biết vì sao nó ra như vậy).

        Chiều ngược lại — được cấp phép nhưng broker trả về gói KHÁC — KHÔNG pause: đó là chiều
        an toàn (lệnh chạy không đòn bẩy, xem DNSEBroker._validate_lever_package), chỉ ghi journal.

        Trả (set mã phải tạm dừng, list dict cảnh báo). KHÔNG raise: lỗi đọc/parse coi như không
        thấy gì ở CHÍNH guard này — nhưng poll_orders() hỏng đã được step() xử fail-safe riêng.
        """
        authorized, packages = {}, set()
        for o in self.plan.orders:
            lp = getattr(o, "loan_package_id", None)
            if lp is None:
                continue
            packages.add(str(lp))
            authorized.setdefault(str(lp), set()).add(o.ticker)
        # Sổ "ĐÃ ĐƯỢC CẤP PHÉP" do trading_bot.plan.apply_capit_lever ghi (xem chú thích ở đó).
        # PHẢI hợp vào `authorized`, nếu không lượt chạy 13:00 ICT sẽ dựng sự cố GIẢ: ở lượt
        # đó `lever_live_preflight` gỡ cờ vay khỏi plan (NAV sống đo giữa lúc đang giải ngân
        # thấp hơn cơ sở tối qua là chuyện bình thường), trong khi lệnh gói 1840 của lượt
        # 09:05 vẫn sống trên sổ broker ⇒ vòng lặp trên cho `authorized` RỖNG ⇒ guard này
        # PAUSE cả rổ CAPIT cả buổi chiều và báo "đòn bẩy không ai duyệt" cho đúng những lệnh
        # đã qua cả hai cổng người (arch-reviewer vòng 3 #1).
        #
        # KHÔNG làm yếu guard: sổ chỉ chứa mã mà `apply_capit_lever` đã cấp trong CHÍNH tiến
        # trình này sau khi qua đủ mọi cổng (artifact, chính sách, trần VND, duyệt-ngày). Ca
        # mà guard sinh ra để bắt — lệnh mang gói 1840 trên mã KHÔNG hề được cấp phép — vẫn
        # bị bắt y như cũ, vì mã đó không có trong sổ.
        for lp, tks in (getattr(self.plan, "_lever_authorized", None) or {}).items():
            packages.add(str(lp))
            authorized.setdefault(str(lp), set()).update(tks)
        # Không có lệnh đòn bẩy nào trong plan ⇒ MỌI gói lạ đều đáng ngờ, nhưng ta chỉ biết
        # "lạ" so với gói default account — cái đó là chuyện bình thường của BAL/LAG. Nên khi
        # plan không xin đòn bẩy, guard chỉ soi các gói mà chính sách đòn bẩy CÓ THỂ cấp.
        #
        # HAI nguồn, hợp lại, vì mỗi nguồn tự nó đều có lúc câm:
        #   · artifact `golive_v23_status.json` — chỉ có khoá `capit_lever` SAU khi golive chạy
        #     bằng code mới. Đo thật 2026-08-03: artifact của phiên hôm nay KHÔNG có khoá đó,
        #     nên nếu chỉ dựa vào nó thì lưới an toàn ĐANG TẮT trong production, đúng giai đoạn
        #     tính năng mới vào và rủi ro sai sót cao nhất (arch-reviewer bắt được).
        #   · `data/trading_rules.json` — file chính sách, có mặt từ trước khi golive chạy lần
        #     nào; ngay cả khi `enabled=false` nó vẫn khai gói vay mà chính sách có thể dùng.
        # Đọc CẢ HAI, không "hoặc": một lệnh mang gói 1840 là đáng ngờ bất kể hôm nay golive
        # đã kịp công bố gì. Không đọc được nguồn nào → mới chịu im lặng.
        if not packages:
            # CACHE 1 LẦN/PHIÊN (arch-reviewer vòng 2, #6): guard này chạy mỗi chu kỳ step()
            # trên MỌI account, kể cả ZaloPay cash-only vốn không bao giờ vay. Danh sách gói
            # mà chính sách CÓ THỂ cấp là hằng số trong phiên — mở+parse 2 file JSON mỗi vòng
            # là chi phí thuần. Đọc một lần rồi giữ (kể cả kết quả RỖNG, để không thử lại).
            cached = getattr(self, "_lever_policy_packages", None)
            if cached is None:
                from .config import WORKDIR
                cached = set()
                for _path, _dig in (
                        (os.path.join(WORKDIR, "data", "golive_v23_status.json"),
                         lambda d: (d.get("capit_lever") or {}).get("loan_package_id")),
                        (os.path.join(WORKDIR, "data", "trading_rules.json"),
                         lambda d: (d.get("capit_margin_lever") or {}).get("loan_package_id"))):
                    try:
                        with open(_path, encoding="utf-8") as f:
                            lp = _dig(json.load(f) or {})
                        if lp is not None:
                            cached.add(str(lp))
                    except Exception:
                        continue
                self._lever_policy_packages = cached
            packages = set(cached)
            if not packages:
                return set(), []      # không biết gói đòn bẩy là gì → không phán đoán
        plan_tickers = {o.ticker for o in self.plan.orders}
        pause, warns = set(), []
        for oid, u in updates.items():
            raw = u.raw if isinstance(u.raw, dict) else {}
            lp = qget(raw, "loanPackageId", "loanpackageid", "loan_package_id")
            if lp is None or str(lp) not in packages:
                continue
            # Lệnh ĐÃ CHẾT mà chưa khớp gì → không có nợ vay nào phát sinh, bỏ qua. Đối xứng
            # với _ghost_tickers (dòng ~601). Thiếu dòng này thì một lệnh 1840 bị HUỶ, 0 khớp
            # vẫn treo mã đó cả ngày (arch-reviewer vòng 2, #4 — đã probe).
            if u.filled_qty <= 0 and u.is_dead:
                continue
            sym = qget(raw, "symbol", "instrument", "code")
            if sym is None:
                continue
            if sym in authorized.get(str(lp), set()):
                continue                  # đúng mã đã được cấp phép, đúng gói
            # Chỉ TẠM DỪNG mã có trong plan — pause một mã ta không định giao dịch hôm nay
            # không ngăn được gì (không có lệnh nào để chặn) mà chỉ gây nhiễu. Vẫn CẢNH BÁO
            # để người thật biết có đòn bẩy lạ trên tài khoản.
            if sym in plan_tickers:
                pause.add(sym)
            warns.append({"ticker": sym, "oid": oid, "loan_package_id": lp,
                          "in_plan": sym in plan_tickers,
                          "reason": (f"lệnh broker {oid} trên {sym} mang gói vay ĐÒN BẨY {lp} "
                                     f"nhưng mã này KHÔNG được cấp phép đòn bẩy trong plan hôm "
                                     f"nay (được cấp: {sorted(authorized.get(str(lp), set())) or 'KHÔNG MÃ NÀO'})")})
        return pause, warns

    def _would_be_unchanged(self, o, ps, c, now):
        """True nếu huỷ lệnh con `c` ngay bây giờ rồi đặt lại (theo đúng logic _place_slices)
        sẽ cho ra CÙNG giá + KL — khi đó huỷ+đặt-lại là vô nghĩa, chỉ mất ưu tiên FIFO.
        Chỉ áp dụng khi lệnh con chưa khớp gì (an toàn: có fill rồi luôn refresh như cũ).
        Lỗi bất kỳ → False (fail-safe: hành vi cũ, cứ huỷ)."""
        if c.get("filled", 0) != 0:
            return False
        try:
            q = self.broker.get_quote(o.ticker)
            if q is None or not q.ok():
                return False
            extreme_down = self._extreme_regime(o, q, now)
            if o.side == "buy" and (extreme_down or self._floor_guard_buy(o, q)):
                return False  # sẽ EXTREME_PAUSE / EXTREME_FLOOR_GUARD (không đặt gì) — khác hẳn, phải huỷ
            cross, _ = self._decide_cross(o, now, q)
            if extreme_down:
                cross = True
            px = self._limit_price(o, q, cross, extreme=extreme_down)
            if px is None:
                return False
            qty = self._child_qty(o, ps, q, px)
            if qty < LOT:
                return False
            return px == c["price"] and abs(qty - c["qty"]) < LOT
        except Exception:
            return False

    def _cancel_stale(self, now):
        max_age = self.cfg["slice_interval_min"] * 60
        for o in self.plan.orders:
            ps = self.state["parents"][o.id]
            c = self._open_child(ps)
            if not c:
                continue
            age = (now - dt.datetime.fromisoformat(c["ts"])).total_seconds()
            if age > max_age * self._extreme_slice_mult(o, now):  # ×1.0 khi OFF (byte-identical)
                if self._would_be_unchanged(o, ps, c, now):
                    c["ts"] = now.isoformat(timespec="seconds")  # reset đồng hồ tuổi, GIỮ NGUYÊN lệnh
                    self._journal("REFRESH_SKIP", o, c["oid"], c["qty"], c["price"],
                                  note=f"giá/KL không đổi sau {age/60:.0f}p — giữ FIFO, không huỷ")
                    continue
                try:
                    self.broker.cancel_order(c["oid"])
                    c["status"] = "cancelled"
                    self._release_child(o.ticker, c)
                    self._journal("CANCEL_STALE", o, c["oid"], c["qty"] - c.get("filled", 0),
                                  c["price"], note=f"treo {age/60:.0f}p")
                except Exception as e:
                    self._journal("CANCEL_FAIL", o, c["oid"], note=str(e))

    # ------------------------------------------------------------ gap-adaptive helpers

    def _load_gap_ref_data(self):
        """Load prior_close + rvol_20d for buy tickers from local parquet at startup.
        Fail-safe: missing/stale/invalid data leaves _gap_ref empty (no override fires).
        """
        if not (self.cfg.get("gap_adaptive_enabled", False)
                or self.cfg.get("extreme_regime_enabled", False)
                or self.cfg.get("chase_cap_vol_scale_enabled", False)):
            return
        cache_dir = os.environ.get(
            "BQ_LOCAL_CACHE",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "data", "bq_cache"))
        # ticker_prune is chunked per-year since 2026-06-26 (the old monolith
        # ticker_prune.parquet froze at that date — never read it again)
        chunk_dir = os.path.join(cache_dir, "ticker_prune")
        chunk_files = sorted(glob.glob(os.path.join(chunk_dir, "*.parquet")))
        if not chunk_files:
            print(f"[exec:{self.label}] gap_adaptive: no chunks in {chunk_dir} — fail-safe")
            return
        try:
            import pandas as pd
            import pyarrow.parquet as _pq
            tickers = ([o.ticker for o in self.plan.orders]              # EXTREME: cả sell (sell-to-floor)
                       if self.cfg.get("extreme_regime_enabled", False)
                       else [o.ticker for o in self.plan.orders if o.side == "buy"])
            if not tickers:
                return
            today = pd.Timestamp(self.plan.plan_date)
            # ignore_metadata=True bypasses BQ dbdate pandas extension type annotation
            table = _pq.read_table(chunk_files, columns=["time", "ticker", "Close"])
            df = table.to_pandas(ignore_metadata=True)
            df["time"] = pd.to_datetime(df["time"])
            df = df[df["ticker"].isin(set(tickers))]
            df = df[df["time"] < today].sort_values("time")
            for ticker in tickers:
                tk = df[df["ticker"] == ticker].tail(22)  # need 21 prices → 20 returns
                if len(tk) < 2:
                    continue
                prior_close = float(tk["Close"].iloc[-1])
                rets = tk["Close"].pct_change().dropna()
                if len(rets) < 5:
                    continue
                rvol = float(rets.tail(20).std())
                if rvol > 0:
                    self._gap_ref[ticker] = {"prior_close": prior_close, "rvol_20d": rvol}
        except Exception as e:
            print(f"[exec:{self.label}] gap_adaptive: load error — {e}, fail-safe")

    def _cache_gap_z(self, ticker, q):
        """Compute + cache gap_z for ticker from first post-09:15 quote (once per session).
        None in cache = fail-safe (no override). Absent from cache = not yet computed.
        """
        ref = self._gap_ref.get(ticker)
        if not ref or ref.get("rvol_20d", 0) <= 0:
            self._gap_z_cache[ticker] = None  # no ref → fail-safe
            return
        today_open = q.last or q.ref
        if not today_open or today_open <= 0:
            return  # price not available yet; retry on next call
        prior_close = ref["prior_close"]
        rvol_20d = ref["rvol_20d"]
        gap_raw = today_open / prior_close - 1.0
        if abs(gap_raw) > 0.15:  # corp-action guard
            self._gap_z_cache[ticker] = None
            return
        # Floor guard: open at/near daily limit-down means one-way continuation (legal/regulatory
        # blowup), the OPPOSITE of the mean-reversion this override assumes → fail-safe suppress.
        limit_floor = (q.floor if (q.floor and q.floor > 0)
                       else prior_close * (1 - self.cfg.get("gap_floor_band", 0.07)))
        if today_open <= limit_floor * 1.005:  # within 0.5% of floor → treat as limit-down
            self._gap_z_cache[ticker] = None
            return
        self._gap_z_cache[ticker] = gap_raw / rvol_20d

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
            # Gap-adaptive override: abnormal DOWN-gap → full speed at open 09:15-09:45
            self._last_gap_override.pop(o.ticker, None)
            if self.cfg.get("gap_adaptive_enabled", False):
                gap_z = self._gap_z_cache.get(o.ticker)
                if gap_z is not None and gap_z < _GAP_Z_DOWN_THRESHOLD:
                    if dt.time(9, 15) <= t < dt.time(9, 45):
                        self._last_gap_override[o.ticker] = gap_z
                        return 1.0
                    # After 09:45: fall through to normal rule
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

    def _extreme_regime(self, o, q, now):
        """Wrapper memoize theo (ticker, now) quanh `_extreme_regime_raw` — trong 1 chu kỳ step(),
        cả `_would_be_unchanged` (qua _cancel_stale) LẪN `_place_slices` đều cần biết trạng thái
        EXTREME; nếu gọi thẳng hàm mutating bên dưới 2 lần sẽ đếm-đôi bộ đếm 2-poll-confirm (kích
        chỉ sau 1 chu kỳ thay vì 2, phá vỡ debounce chống nhiễu). Chỉ tính THẬT 1 lần/(ticker, now)."""
        key = (o.ticker, now)
        if key not in self._extreme_cache:
            self._extreme_cache[key] = self._extreme_regime_raw(o, q, now)
        return self._extreme_cache[key]

    def _extreme_regime_raw(self, o, q, now):
        """EXTREME_DOWN gate (proposal §3c) — ADDITIVE, gated by extreme_regime_enabled (default OFF).

        Trả True chỉ khi mã đang trong nhịp GIẢM bất thường đã xác nhận:
          (i)  last nằm trong extreme_band của SÀN ngày (cận limit-down) — chỉ cần quote, HOẶC
          (ii) r15 giảm mạnh hơn extreme_move_z × rvol_20d (rvol lấy từ _gap_ref nếu đã nạp).
        Cần 2 poll liên tiếp xác nhận mới kích; đã kích thì giữ active extreme_cooldown_min phút
        (debounce nhiễu). Fail-safe: thiếu dữ liệu → False (NORMAL). Không bao giờ raise.
        Gọi qua wrapper `_extreme_regime` — KHÔNG gọi trực tiếp (tránh đếm-đôi, xem docstring trên).
        """
        if not self.cfg.get("extreme_regime_enabled", False):
            return False
        st = self._extreme_state.setdefault(o.ticker, {"n": 0, "until": None})
        if st["until"] and now < dt.datetime.fromisoformat(st["until"]):
            return True                      # đang trong cooldown → giữ active
        try:
            last = q.last or q.ref
            if not last or last <= 0:
                st["n"] = 0
                return False
            trig = False
            floor = q.floor if (q.floor and q.floor > 0) else None
            if floor and last <= floor * (1 + self.cfg.get("extreme_band", 0.03)):
                trig = True                  # (i) cận sàn — trigger backtest đã validate
            if not trig:                     # (ii) nhịp giảm intraday bất thường vs rvol 20d
                ref = self._gap_ref.get(o.ticker)
                rvol = ref.get("rvol_20d") if ref else None
                if rvol and rvol > 0:
                    r = self._r15(o.ticker, now)
                    if r is not None and r < -self.cfg.get("extreme_move_z", 3.0) * rvol:
                        trig = True
            if not trig:
                st["n"] = 0
                return False
            st["n"] += 1
            if st["n"] >= 2:                 # 2-poll confirm → kích + đặt cooldown
                st["until"] = (now + dt.timedelta(
                    minutes=self.cfg.get("extreme_cooldown_min", 15))).isoformat(timespec="seconds")
                return True
            return False
        except Exception:
            return False

    def _floor_guard_buy(self, o, q):
        """Poll-1 floor-proximity BUY guard — đóng lỗ hổng PNJ (job Taylor_20260713_075836):
        2-poll confirm của `_extreme_regime` cố ý trễ 1 lần đánh giá, nhưng slice MUA đầu
        tiên vẫn được đặt trong cửa sổ đó; với NAV nhỏ (lệnh ≤ max_child_value = 1 slice)
        toàn bộ lệnh khớp tại sàn TRƯỚC khi gate arm — và vì đã có open child, gate không
        bao giờ được đánh giá lại cho lệnh đó.

        Guard này STATELESS (chỉ đọc quote hiện tại, không đếm, không cooldown, không đụng
        `_extreme_state`) và CHỈ chặn chiều MUA: cận-sàn là fact cứng từ quote (floor là
        ranh giới tuyệt đối), 1 quote lỗi chỉ làm trễ slice mua 1 chu kỳ (20s–8p) — không
        đặt lệnh sai giá, không kích sell-to-floor. Trigger (ii) 3-sigma (nhiễu thật) vẫn
        giữ nguyên 2-poll qua `_extreme_regime`. Fail-safe: thiếu floor/last → False.
        Gated bởi extreme_regime_enabled (paper `main` only) — LIVE byte-identical."""
        if not self.cfg.get("extreme_regime_enabled", False):
            return False
        try:
            last = q.last or q.ref
            floor = q.floor if (q.floor and q.floor > 0) else None
            return bool(floor and last and last > 0
                        and last <= floor * (1 + self.cfg.get("extreme_band", 0.03)))
        except Exception:
            return False

    def _extreme_slice_mult(self, o, now):
        """1.0 bình thường; extreme_slice_mult khi mã đang active EXTREME (rút ngắn nhịp
        cancel/reprice để đuổi kịp sổ lệnh tụt). Đọc state đã armed, KHÔNG gọi quote lại."""
        if not self.cfg.get("extreme_regime_enabled", False):
            return 1.0
        st = self._extreme_state.get(o.ticker)
        if st and st.get("until") and now < dt.datetime.fromisoformat(st["until"]):
            return self.cfg.get("extreme_slice_mult", 0.25)
        return 1.0

    def _place_slices(self, now, phase, ghost_tickers=(), positions=None):
        base_interval = self.cfg["slice_interval_min"] * 60
        for o in sorted(self.plan.orders, key=lambda x: x.priority):
            ps = self.state["parents"][o.id]
            if ps["done"] or self._open_child(ps):
                continue
            if o.ticker in ghost_tickers:
                continue  # idempotency guard — xem _ghost_tickers
            # Populate gap_z cache before interval decision (gap_adaptive BUY only)
            if (o.side == "buy" and self.cfg.get("gap_adaptive_enabled", False)
                    and o.ticker not in self._gap_z_cache
                    and now.time() >= dt.time(9, 15)):
                q_pre = self.broker.get_quote(o.ticker)
                if q_pre and q_pre.ok():
                    self._cache_gap_z(o.ticker, q_pre)
            interval = base_interval * self._fill_timing_mult(o, now)
            if ps["last_slice_ts"]:
                since = (now - dt.datetime.fromisoformat(ps["last_slice_ts"])).total_seconds()
                if since < interval and ps["children"]:
                    continue
            q = self.broker.get_quote(o.ticker)
            if q is None or not q.ok():
                self._journal("NO_QUOTE", o, note="thiếu quote — thử lại sau")
                continue
            extreme_down = self._extreme_regime(o, q, now)
            if extreme_down and o.side == "buy":
                self._journal("EXTREME_PAUSE", o, note="EXTREME_DOWN → tạm dừng mua, T+1 re-sync")
                continue
            if o.side == "buy" and not extreme_down and self._floor_guard_buy(o, q):
                # đóng cửa sổ poll-1: chặn slice mua NGAY khi quote cận sàn, không chờ
                # 2-poll confirm (xem _floor_guard_buy); _extreme_regime ở trên đã đếm
                # poll này nên nếu cận-sàn là thật, gate sẽ arm bình thường ở poll kế.
                self._journal("EXTREME_FLOOR_GUARD", o,
                              note="quote cận sàn (fact cứng) → chặn slice mua từ poll 1, "
                                   "thử lại chu kỳ sau")
                continue
            cross, dip_note = self._decide_cross(o, now, q)
            if extreme_down:                 # o.side == "sell" (buy đã pause ở trên)
                cross, dip_note = True, "EXTREME_DOWN sell-to-floor"
            px = self._limit_price(o, q, cross, extreme=extreme_down)
            if px is None:
                hard = self._hard_buy_ceiling(o)
                if hard:
                    # Phân biệt rõ với NO_QUOTE/WAIT_CASH: lỡ phiên vì TRẦN, không phải vì lỗi.
                    self._journal("HARD_CEILING_BLOCK", o, price=hard, note=(
                        f"giá thấp nhất đặt được (sàn {q.floor:,.0f}) > trần {hard:,.0f}đ "
                        f"— KHÔNG đặt lệnh mua, thử lại chu kỳ sau"))
                continue
            qty = self._child_qty(o, ps, q, px)
            if qty <= 0:
                self._journal("WAIT_QUOTA", o, note="hết quota participation/đợi KL")
                continue
            # qty < LOT past this point means _child_qty returned a genuine odd-lot
            # remainder (verified 2026-07-09 to place fine as a normal LO order — see
            # _child_qty) — falls through to the same place_order() call below as any
            # round-lot slice, no special-casing needed.
            if o.side == "sell" and positions is not None:
                # KL "total" có thể gồm cổ phiếu mua chưa qua T+2 (chưa bán được) —
                # broker phân biệt total vs sellable (xem BrokerBase.get_positions).
                # Cap theo sellable thay vì để place_order() tự trả HTTP 400 mỗi slice —
                # tránh lặp vô ích hàng trăm lần/phiên khi lô hàng vẫn đang chờ T+2 về
                # (quan sát 2026-07-06: ~2000 lần PLACE_FAIL "Trade quantity not enough"
                # trên đúng các mã mua T-2 phiên trước, tự hết khi sang phiên chiều T+2).
                sellable = (positions.get(o.ticker) or {}).get("sellable")
                if sellable is not None:
                    # qty<LOT ở đây là cổ phiếu lẻ (xem _child_qty) — so trực tiếp với
                    # sellable thật, KHÔNG round_lot() nó (round_lot(10)=0 sẽ lại zero-
                    # hoá đúng phần lẻ này, tái diễn cùng bug — xem kb/INCIDENTS.md
                    # 2026-07-09).
                    cap = sellable if qty < LOT else round_lot(sellable)
                    if cap < (qty if qty < LOT else LOT):
                        self._journal("WAIT_T2_SETTLEMENT", o, note=(
                            f"chỉ {sellable:,} cp sellable (có thể đang chờ T+2 về) — "
                            f"chưa đặt lệnh bán, thử lại chu kỳ sau"))
                        continue
                    qty = min(qty, cap)
            if o.side == "buy":
                need = qty * px * 1.0025
                if self.broker.get_cash() < need:
                    # availableCash chưa đủ ≠ hết sức mua: broker cộng tiền bán chờ về
                    # (T+0 reuse) vào sức mua ppse TRƯỚC KHI availableCash cập nhật —
                    # xác nhận thực nghiệm 2026-07-07 (ZaloPay: bán MSH 09:42, ppse đủ
                    # tiền lúc 09:56, availableCash vẫn đứng yên; user dự đoán đúng cơ
                    # chế). Hỏi CHÍNH broker trước khi kết luận thiếu tiền; broker không
                    # hỗ trợ/lỗi → None → giữ WAIT_CASH như cũ (fail-safe). Nếu ppse nói
                    # đủ mà thực tế không đủ, place_order sẽ bị broker từ chối → chỉ 1
                    # dòng PLACE_FAIL, không rủi ro tiền.
                    # Đo sức mua bằng ĐÚNG gói vay lệnh này sẽ dùng: lệnh đòn bẩy CAPIT đi ra
                    # bằng gói 1840 (initialRate 0,5 ⇒ sức mua gấp đôi 1841). Hỏi bằng gói
                    # default trong khi đặt bằng 1840 sẽ báo thiếu tiền ở đúng nửa phần vay
                    # (arch-reviewer 2026-08-03 #2) — và WAIT_CASH đó không phân biệt được
                    # với thiếu tiền thật.
                    # Gói vay HIỆU LỰC (đúng cách place_order giải: đòn bẩy chỉ định phải
                    # validate được, còn lại giải gói hợp lệ theo MÃ) — đo bằng gói thô của
                    # lệnh là bug DRI/UPCOM 2026-08-07: lp=None ⇒ ppse hỏi gói default 1841
                    # (mainboard-only) ⇒ reject ⇒ WAIT_CASH vô hạn dù thừa tiền.
                    _eff_lp, _ = _effective_loan_package(o, self.broker)
                    qmax = self.broker.get_max_buy_qty(o.ticker, px, loan_package_id=_eff_lp)
                    if qmax is None or qmax < qty:
                        self._journal("WAIT_CASH", o, qty=qty, price=px,
                                      note="thiếu tiền — chờ lệnh bán khớp"
                                      + (f" (sức mua broker {qmax} cp < {qty})" if qmax is not None else ""))
                        continue
            try:
                oid = self.broker.place_order(o.ticker, qty, o.side, price=px,
                                              cash_only=getattr(o, "cash_only", False),
                                              loan_package_id=getattr(o, "loan_package_id", None))
            except Exception as e:
                retry = self._retry_tick_mismatch(o, q, cross, extreme_down, px, qty, e)
                if retry is None:
                    self._journal("PLACE_FAIL", o, qty=qty, price=px, note=str(e))
                    continue
                oid, px = retry
            ps["children"].append({"oid": oid, "qty": qty, "price": px, "filled": 0,
                                   "status": "open",
                                   "ts": now.isoformat(timespec="seconds")})
            self.shared[o.ticker] = self.shared.get(o.ticker, 0) + qty  # reserve quota
            ps["last_slice_ts"] = now.isoformat(timespec="seconds")
            capped = (o.side == "buy" and cross and q.ask and px < q.ask)
            ft_mult = self._fill_timing_mult(o, now)
            gap_note = (f"GAP_OPEN_OVERRIDE gap_z={self._last_gap_override[o.ticker]:.2f}"
                        if o.ticker in self._last_gap_override else "")
            ft_note = (f"ft:in-window" if ft_mult == 1.0 and self.cfg.get("fill_timing_enabled")
                       else f"ft:out×{ft_mult:.0f}" if self.cfg.get("fill_timing_enabled")
                       else "")
            notes = [n for n in (dip_note,
                                 "nằm chờ tại trần đuổi" if capped else "",
                                 gap_note, ft_note) if n]
            self._journal("PLACE", o, oid, qty, px, note="; ".join(notes))
            # Idempotency: ghi state NGAY sau khi broker xác nhận đặt lệnh, không đợi hết
            # step() mới lưu — thu hẹp cửa sổ "lệnh đã đặt nhưng state chưa biết" (từ cả
            # 1 chu kỳ đa mã xuống 1 lần ghi JSON) nếu process bị kill giữa chừng.
            self._save_state()

    def _atc_sweep(self, ghost_tickers=(), positions=None):
        for o in self.plan.orders:
            ps = self.state["parents"][o.id]
            if ps["done"] or ps["atc_sent"]:
                continue
            if o.ticker in ghost_tickers:
                continue  # idempotency guard — xem _ghost_tickers
            flag = (self.cfg["atc_remainder_sell"] if o.side == "sell"
                    else self.cfg["atc_remainder_buy"])
            if not flag:
                continue
            if self._hard_buy_ceiling(o):
                # ATC khớp ở GIÁ ĐÓNG CỬA phiên xác định lúc ATC — không đặt được giá,
                # nên KHÔNG có cách nào đảm bảo ≤ trần. Lệnh có trần tuyệt đối chỉ đi
                # đường LO. (atc_remainder_buy mặc định False; guard này để lúc ai đó bật
                # lên thì trần vẫn còn hiệu lực ở MỌI bước, không hở đúng bước cuối phiên.)
                self._journal("HARD_CEILING_SKIP_ATC", o,
                              price=self._hard_buy_ceiling(o),
                              note="lệnh có trần giá tuyệt đối — ATC không đặt được giá, bỏ quét ATC")
                continue
            c = self._open_child(ps)
            if c:
                try:
                    self.broker.cancel_order(c["oid"])
                    c["status"] = "cancelled"
                    self._release_child(o.ticker, c)
                except Exception:
                    pass
            raw_remaining = o.qty - ps["filled"]
            remaining = round_lot(raw_remaining)
            if remaining < LOT:
                if 0 < raw_remaining < LOT:
                    # Cổ phiếu lẻ — ATC là loại lệnh phiên đóng cửa CHỈ xác nhận dùng
                    # được cho lô chẵn (lệnh lô lẻ thật verify 2026-07-09 là orderType=
                    # LO, không phải ATC) — KHÔNG đoán ATC cũng hoạt động cho lô lẻ.
                    # _place_slices đã tự đặt LO cho phần lẻ này mỗi chu kỳ trong phiên
                    # thường rồi (xem _child_qty); ATC sweep bỏ qua, để phiên sau tiếp
                    # tục qua đường LO bình thường thay vì thử ATC chưa kiểm chứng.
                    self._journal("ODD_LOT_SKIP_ATC", o, note=(
                        f"ATC: {raw_remaining}cp lẻ — bỏ qua ATC (chưa xác minh ATC cho "
                        f"lô lẻ), tiếp tục đặt qua LO ở phiên sau."))
                continue
            if o.side == "sell" and positions is not None:
                sellable = (positions.get(o.ticker) or {}).get("sellable")
                if sellable is not None:
                    cap = round_lot(sellable)
                    if cap < LOT:
                        self._journal("WAIT_T2_SETTLEMENT", o, note=(
                            f"ATC: chỉ {sellable:,} cp sellable (có thể đang chờ T+2 về) — bỏ qua"))
                        continue
                    remaining = min(remaining, cap)
            try:
                oid = self.broker.place_order(o.ticker, remaining, o.side,
                                              price=None, order_type="ATC",
                                              cash_only=getattr(o, "cash_only", False),
                                              loan_package_id=getattr(o, "loan_package_id", None))
                ps["children"].append({"oid": oid, "qty": remaining, "price": None,
                                       "filled": 0, "status": "open",
                                       "ts": now_ict().isoformat(timespec="seconds")})
                ps["atc_sent"] = True
                self._journal("ATC", o, oid, remaining, note="quét ATC phần còn lại")
                self._save_state()  # idempotency: ghi ngay, xem note ở _place_slices
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
        ghost_tickers = set()
        try:
            updates = self.broker.poll_orders()
            self._sync_fills(updates)
            ghost_tickers = self._ghost_tickers(updates)
            for t in ghost_tickers - self.state.setdefault("_ghost_warned", {}).keys():
                self.state["_ghost_warned"][t] = now.isoformat(timespec="seconds")
                self._journal("GHOST_ORDER", note=f"{t}: lệnh broker không có trong state — "
                                                   f"TẠM DỪNG mã này, cần người kiểm tra")
                _publish_bot_event("error", "GHOST_ORDER_DETECTED", {
                    "account": self.label, "ticker": t, "plan_date": self.plan.plan_date,
                    "note": "Lệnh tồn tại ở broker nhưng state.json không biết (khả năng crash "
                            "giữa place_order và _save_state). Bot ĐÃ TỰ DỪNG đặt lệnh mới cho "
                            "mã này để tránh double-buy — cần đối soát tay rồi mới cho tiếp tục."
                })
            # Lưới an toàn ĐÒN BẨY CAPIT — gói vay thật trên sổ broker vs tập mã được cấp phép.
            # Cùng đường TẠM DỪNG với ghost order (không tự huỷ lệnh, gọi người thật).
            lever_pause, lever_warns = self._lever_package_audit(updates)
            ghost_tickers |= lever_pause
            for w in lever_warns:
                seen = self.state.setdefault("_lever_warned", {})
                if w["ticker"] in seen:
                    continue
                seen[w["ticker"]] = now.isoformat(timespec="seconds")
                self._journal("LEVER_PACKAGE_UNAUTHORIZED", note=w["reason"])
                _publish_bot_event("error", "LEVER_PACKAGE_UNAUTHORIZED", {
                    "account": self.label, "ticker": w["ticker"],
                    "plan_date": self.plan.plan_date, "order_id": w["oid"],
                    "loan_package_id": w["loan_package_id"], "in_plan": w["in_plan"],
                    "note": w["reason"] + " — Bot ĐÃ TỰ DỪNG đặt lệnh mới cho mã này. Đây là "
                            "ĐÒN BẨY KHÔNG ĐƯỢC CẤP PHÉP (nợ vay thật): đối soát ngay với sổ "
                            "lệnh DNSE trước khi cho chạy tiếp."
                })
        except Exception as e:
            # Fail-safe, NOT fail-open: poll_orders() is what the ghost guard depends on to
            # see broker-side state. If it just errored, we have NO visibility this cycle —
            # blindly proceeding with an empty ghost_tickers would silently bypass the guard
            # (quant-skeptic killer objection, verify_finding.sh 2026-07-02). So on a poll
            # failure, block placement for EVERY plan ticker this cycle (same skip path as a
            # confirmed ghost) instead of assuming "no ghosts". _cancel_stale is unaffected
            # (age-based, doesn't need fresh poll data); next cycle's poll retries normally.
            self._journal("POLL_FAIL", note=str(e))
            ghost_tickers = {o.ticker for o in self.plan.orders}
        if self.all_done:
            self._save_state()
            return True
        try:
            self._record_prices(now, phase)
        except Exception as e:
            self._journal("PX_HIST_FAIL", note=str(e))
        positions = None
        if any(o.side == "sell" for o in self.plan.orders):
            try:
                positions = self.broker.get_positions()
            except Exception as e:
                # Degrade gracefully (not fail-safe-block): sellable-cap is a retry-noise
                # optimization, not a correctness guard like the ghost-order poll above —
                # on failure just fall back to today's existing behavior (attempt the sell,
                # let the broker's own HTTP 400 reject it if not actually sellable yet).
                self._journal("POSITIONS_FAIL", note=str(e))
        if cont:
            self._cancel_stale(now)
            self._place_slices(now, phase, ghost_tickers, positions)
        elif phase == "ATC":
            self._atc_sweep(ghost_tickers, positions)
        self._save_state()
        return self.all_done

    # ------------------------------------------------------------ report

    def write_report(self):
        lines = [f"# Execution report — [{self.label}] {self.plan.plan_date}",
                 f"*Strategy*: {self.plan.strategy} v{self.plan.strategy_version} | "
                 f"*Broker*: {self.broker.name} | "
                 f"*Generated*: {now_ict():%Y-%m-%d %H:%M}", "",
                 "| order | ticker | side | plan qty | filled | % | ref px | avg fill px | children |",
                 "|---|---|---|---:|---:|---:|---:|---:|---:|"]
        tot_plan = tot_fill = 0
        for o in self.plan.orders:
            ps = self.state["parents"][o.id]
            pct = 100.0 * ps["filled"] / o.qty if o.qty else 0
            tot_plan += o.value
            fills = [c for c in ps["children"] if c.get("filled")]
            avg = (sum(c["filled"] * (c["price"] or o.ref_price) for c in fills) /
                   max(1, sum(c["filled"] for c in fills))) if fills else 0
            tot_fill += ps["filled"] * (avg or o.ref_price)
            avg_disp = f"{avg:,.0f}" if avg else "-"
            lines.append(f"| {o.id} | {o.ticker} | {o.side} | {o.qty:,} | "
                         f"{ps['filled']:,} | {pct:.0f}% | {o.ref_price:,.0f} | "
                         f"{avg_disp} | {len(ps['children'])} |")
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
        now = now_ict()  # luôn giờ ICT thật, bất kể TZ của process gọi vào — xem vn_market.py
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
                s = e.step(now, phase, cont)
                e._step_fail_count = 0
                statuses.append(s)
            except Exception as ex:   # 1 account lỗi không kéo chết account khác
                e._journal("STEP_FAIL", note=str(ex))
                e._step_fail_count += 1
                # Escalate to Mike bus after 3 consecutive failures (transient errors are expected)
                if e._step_fail_count == 3:
                    _publish_bot_event("error", "STEP_FAIL", {
                        "account": e.label, "error": str(ex),
                        "consecutive": e._step_fail_count, "phase": phase,
                        "note": "Bot gặp lỗi liên tiếp — cần kiểm tra. Xem execution_logs/."
                    })
                statuses.append(False)
        if all(statuses):
            print("[exec] ✅ tất cả account đã khớp đủ")
            break

        # Fill-lagging check: 30 min before MORNING close (11:00), warn if <40% filled
        if phase == "MORNING" and now.time() >= dt.time(11, 0):
            for e in executors:
                ps = e.state.get("parents", {})
                if not ps:
                    continue
                total_plan = sum(p.get("qty", 0) for p in ps.values())
                total_fill = sum(p.get("filled", 0) for p in ps.values())
                fill_rate = total_fill / total_plan if total_plan else 1.0
                if fill_rate < 0.4 and not e.state.get("_fill_lag_warned"):
                    e.state["_fill_lag_warned"] = True
                    _publish_bot_event("status", "fill_lagging", {
                        "account": e.label, "fill_rate_pct": round(fill_rate * 100, 1),
                        "note": f"Chỉ fill {fill_rate*100:.0f}% trước 11:00 — còn phiên chiều nhưng cần chú ý.",
                        "action_hint": "Xem execution_logs để quyết định có chuyển ATC không."
                    })

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
