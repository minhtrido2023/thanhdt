#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tự động xác nhận sự kiện doanh nghiệp (BONUS_ISSUE / SPLIT) khi DNSE credit cổ phiếu.

VÒNG LẶP 5 LẦN (VHM, MBB, BID, VIX, MSB) đều cùng mẫu:
  corp_action_daily biết sự kiện từ sáng (07:30) qua upcoming_events_held (days_ahead=1),
  nhưng DNSE credit trước ex_date 1 phiên (~18:30–19:00 ICT), trong khi DollarBill xây plan
  tại 19:00–19:10. Kết quả: sổ lô ≠ broker → BLOCKED_RECONCILE cho mã đó.

Script này chạy lúc 19:30 ICT (sau khi DNSE credit, trước DollarBill) và tự CONFIRMED khi
đủ bằng chứng 2 nguồn ĐỘC LẬP:
  (1) upcoming_events_held có event ex ∈ [hôm nay, phiên giao dịch kế tiếp] (lịch VN thật — m6 r2)
  (2) Broker: openQuantity và costPrice đổi đúng hệ số trong ngày

⚠️ CHỈ xác nhận sự kiện LÀM TĂNG số lượng (BONUS_ISSUE / SPLIT). Cổ tức tiền mặt không đi qua
đây. Gộp cổ phiếu (reverse split) chưa thiết kế (qty_multiplier > 1 là điều kiện cứng trong corp_actions.py).

NHÁNH BROKER (user duyệt 2026-10-03, phương án B — feed vendor chết từ 2026-09-26, ca TPB):
sau nhánh vendor, `run_broker()` quét MỌI mã đang giữ bằng `corp_action_broker_detect` — KL +
tổng giá vốn + giá tham chiếu cùng kể một sự kiện, credit sau 15:00 ⇒ ex-date = phiên kế tiếp.
Công tắc `MIKE_CA_BROKER_SOURCE`:
  off    — không chạy nhánh broker; nhánh vendor là bên ghi như trước 2026-10-03, CHỈ khác ở các chốt
           an toàn (đều chỉ biến "ghi sai im lặng" thành "không ghi + hỏi người", không bao giờ ngược lại):
           r3 I1 (≤1 record hiệu lực/(mã, ex) ở điểm ghi); r4: khoá registry đọc qua CA.validate (mã
           strip/upper, ex ISO — MAJOR-2), ứng viên vendor trùng gộp TRƯỚC vòng ghi (chỉ nhóm mâu thuẫn bị
           chặn — m7), registry đã có record CÙNG (mã, ex) ở MỌI trạng thái/provenance ⇒ đối chiếu
           `_record_vs_vendor` thay vì ghi thêm, record MỌI provenance ở ex gần ⇒ hỏi (m8), giá vốn/lịch
           vendor báo có chân tiền cùng ex ⇒ không tự ghi (record thiếu chân tiền làm cổng giá đêm FAIL).
  shadow — MẶC ĐỊNH: nhánh broker phát hiện + ghi sổ `data/corp_action_broker_ledger.jsonl` + ĐÚNG 1 bus
           finding tóm tắt/lượt (gộp pha KL + chỉ-giá); KHÔNG ghi `data/corp_actions.json`, nhánh broker
           KHÔNG hỏi/trả lời gì. Nhánh vendor vẫn ghi + hỏi người như off.
  ⚠ --dry-run (MỌI mode): 0 tác dụng ngoài — mọi bus/Discord/sổ/registry/marker đi qua MỘT cổng
           `_effects_blocked` (MAJOR-1 r4: bản r3 để writer vendor gửi validate-reject THẬT ở dry-run).
           Câu hỏi/câu trả lời lẽ ra gửi được IN ra ("[DRY-RUN] KHÔNG gửi …") để người đọc so.
  live   — BROKER LÀ NGUỒN CHÍNH (user nâng cấp 2026-10-03 23:08): nhánh broker chạy TRƯỚC và là
           nơi DUY NHẤT ghi — CONFIRMABLE ⇒ record CONFIRMED provenance=broker (validate() + atomic)
           BẤT KỂ vendor có sự kiện hay không; vendor chỉ đối chiếu (`vendor_check`): LỆCH (>1% hệ
           số / >1đ/cp / ex khác) ⇒ UNVERIFIED, KHÔNG ghi, bus question gọi tên Winston kèm CẢ HAI
           số; MƠ HỒ / CHƯA ĐỦ ⇒ question (1 lần / mã / phiên / verdict). Cổ tức tiền đã khớp
           cashDividendReceiving ⇒ finding (sổ không chứa cổ tức tiền). Nhánh vendor chạy SAU ở
           chế độ CHỈ-XÁC-NHẬN (`confirm_only`): không bao giờ ghi; lệch record broker ⇒ hỏi; vendor có
           sự kiện mà broker không thấy gì ⇒ hỏi (không im lặng, không tự ghi).
           r2 (2026-10-04): registry ĐÃ có (mã, ex) ⇒ đối chiếu record MỌI provenance với broker
           (trạng thái, hệ số, chân tiền nếu record khai) — lệch ⇒ UNVERIFIED + question Winston,
           KHÔNG ghi đè; ghi sự kiện KL TRƯỚC, sàng lọc chỉ-giá SAU trong ngân sách thời gian; record
           broker chưa được vendor xác nhận ⇒ đối chiếu lại SAU ex (`_reverify_broker_records`).
           r3 (2026-10-04, bảng bất biến ở agents/Taylor/research/broker-primary-20261004.md §r3):
           I1 ≤1 record HIỆU LỰC/(mã, ex) chốt ở ĐIỂM GHI (`_validate_for_write`, cả 2 writer) + trùng
           có sẵn ⇒ LỆCH + hỏi; I2 câu hỏi khi registry đã có record KHÔNG BAO GIỜ đề xuất record thứ
           hai (chỉ sửa/thu hồi); I3 chân tiền vắng = 0 như consumer đọc; I4 positions rỗng/cũ ⇒
           "không xác định", không "không giữ"; `_registry_sweep` (trùng + chờ/quá hạn credit).
           r4: I3 mạnh hơn — MỌI khoá (mã, ex, id) VÀ giá trị (hệ số, chân tiền, hiệu lực) của record
           registry lấy từ OUTPUT của CA.validate (`_reg_rows`), record validate() từ chối ⇒ LỆCH; I5 câu
           hỏi vendor-only / held-unknown / QUÁ HẠN được `answer` khi giải quyết (`_resolve_asks`), ghi
           CONFIRMED ⇒ câu hỏi cũ cùng mã/phiên chưa gửi bị bỏ (superseded), đã gửi được trả lời.
  shadow/off giữ nhánh vendor là bên ghi (chưa được duyệt bật live); shadow chỉ ghi sổ quyết định
           broker-primary SẼ làm để người so sánh.
Sổ 2 pha (intent → tác dụng ngoài → done khi bus rc=0): kill/bus lỗi ⇒ lượt sau GỬI BÙ.
⚠️ Phụ thuộc NGẦM: nhánh broker chỉ đọc dnse_raw do tiến trình khác ghi (EOD/park/verify chạy
19:0x–19:1x); không có bản ghi positions nào sau credit ⇒ INSUFFICIENT/không thấy.
Bật `live` cần user duyệt sau khi xem cửa sổ shadow.

Chạy: python3 mike/bin/corp_action_auto_confirm.py [--dry-run] [--date YYYY-MM-DD]
"""
import argparse
import contextlib
import datetime as dt
import json
import math
import os
import sys

# ── Paths ──────────────────────────────────────────────────────────────────
MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MIKE_BIN)
import wc_paths  # noqa: E402

WC_ROOT = wc_paths.find_wc_root(__file__)
MIKE_ROOT = os.path.join(WC_ROOT, "mike")

CORP_ACTIONS_FILE  = os.path.join(WC_ROOT, "data", "corp_actions.json")
CA_DAILY_DIR       = os.path.join(WC_ROOT, "data", "corp_action_daily")
EXEC_DIR           = os.path.join(WC_ROOT, "data", "execution_logs")

sys.path.insert(0, MIKE_ROOT)
import corp_actions as CA  # noqa: E402 — validate() tại điểm ghi, BLOCKER 1b arch-review vòng 8
import corp_action_broker_detect as BD  # noqa: E402 — nhánh broker (2026-10-03)
LEDGER_FILE = BD.LEDGER_FILE

# ── Constants ──────────────────────────────────────────────────────────────
RATIO_TOL       = 0.02   # ±2% chấp nhận giữa hệ số khai báo và hệ số suy từ broker
CONFIRMED_CODES = {"ISS", "SPLIT"}

APPEND_EVENT = os.path.join(MIKE_BIN, "append_event.sh")
NOTIFY_SH    = os.path.join(MIKE_BIN, "notify_thread.sh")


# ── Helpers ────────────────────────────────────────────────────────────────

def today_ict():
    from zoneinfo import ZoneInfo
    return dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()


def load_corp_actions_raw():
    """Đọc toàn bộ corp_actions.json, trả list thô. [] nếu file không tồn tại."""
    if not os.path.exists(CORP_ACTIONS_FILE):
        return []
    with open(CORP_ACTIONS_FILE, encoding="utf-8") as f:
        return json.load(f).get("actions") or []


def get_candidate_events(date_str):
    """Từ corp_action_daily_{date}.json → upcoming_events_held khớp điều kiện: sự kiện CP có ex
    trong [date_str, phiên giao dịch KẾ TIẾP] theo LỊCH GIAO DỊCH VN (`trading_bot.vn_market`) —
    broker có thể credit trong hôm nay. Bản cũ dùng `days_ahead ≤ 1` NGÀY LỊCH ⇒ credit thứ Sáu,
    ex thứ Hai (days_ahead=3) / qua kỳ nghỉ lễ bị bỏ sót (m6)."""
    from trading_bot.vn_market import next_trading_day
    path = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{date_str}.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    held = d.get("upcoming_events_held") or []
    last = next_trading_day(dt.date.fromisoformat(date_str)).isoformat()
    out = []
    for ev in held:
        if not (ev.get("price_adjusting") and ev.get("event_code") in CONFIRMED_CODES):
            continue
        try:
            ex = dt.date.fromisoformat(str(ev.get("date") or "")[:10]).isoformat()
        except ValueError:      # §29: nói ra, không lặng lẽ bỏ
            print(f"  [{ev.get('ticker')}] sự kiện vendor {ev.get('event_code')} có ngày không đọc được "
                  f"{ev.get('date')!r} ⇒ không xét")
            continue
        if date_str <= ex <= last:
            # MAJOR-2 r4: (mã, ex) ứng viên chuẩn hoá ĐÚNG quy tắc CA.validate ⇒ so được với khoá registry
            out.append(dict(ev, ticker=_norm_ticker(ev.get("ticker")), date=ex))
    return out


def _get_ticker_snapshots(account_no, ticker, date_str):
    """Đọc tất cả bản ghi positions cho (account_no, ticker) từ dnse_raw_{date}.jsonl.

    Trả (first_rec, last_rec) — rec là dict position của DNSE, có openQuantity / costPrice.
    Trả (None, None) nếu không có bản ghi nào.
    """
    path = os.path.join(EXEC_DIR, f"dnse_raw_{date_str}.jsonl")
    if not os.path.exists(path):
        return None, None

    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(d.get("account_no")) != str(account_no):  # §12
                continue
            if d.get("kind") != "positions":
                continue
            ts = d.get("ts") or ""
            positions = d.get("payload", {}).get("positions") or []
            for p in positions:
                if _norm_ticker(p.get("symbol")) == ticker and str(p.get("accountNo")) == str(account_no):
                    records.append((ts, p))
                    break  # chỉ 1 bản ghi / snapshot / ticker

    if not records:
        return None, None
    records.sort(key=lambda x: x[0])
    return records[0][1], records[-1][1]


def _get_account_nos(date_str):
    """Đọc danh sách account_no từ dnse_raw_{date}.jsonl."""
    path = os.path.join(EXEC_DIR, f"dnse_raw_{date_str}.jsonl")
    if not os.path.exists(path):
        return []
    seen = {}  # account_no → account_label
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ano = d.get("account_no")
            lbl = d.get("account_label") or ano
            if ano and ano not in seen:
                seen[ano] = lbl
    return list(seen.items())  # [(account_no, label), ...]


def check_ratio(first_rec, last_rec, expected_mult, tol=RATIO_TOL):
    """So hệ số thực tế với hệ số khai báo. Trả (ok, actual_qty_ratio, actual_cost_ratio).

    expected_mult = 1.2 với tỉ lệ thưởng 20%.
    """
    qty_before = int(first_rec.get("openQuantity") or 0)
    qty_after  = int(last_rec.get("openQuantity") or 0)
    cost_before = float(first_rec.get("costPrice") or 0)
    cost_after  = float(last_rec.get("costPrice") or 0)

    if qty_before <= 0 or qty_after <= qty_before or cost_after <= 0:
        return False, None, None

    actual_qty  = qty_after / qty_before
    actual_cost = cost_before / cost_after if cost_after > 0 else 0

    qty_ok  = abs(actual_qty  - expected_mult) <= tol * expected_mult
    cost_ok = abs(actual_cost - expected_mult) <= tol * expected_mult
    return (qty_ok and cost_ok), round(actual_qty, 4), round(actual_cost, 4)


def broker_modified_today(last_rec, today_str):
    """True nếu modifiedDate của record là hôm nay ICT (broker credit hôm nay)."""
    md = str(last_rec.get("modifiedDate") or "")
    # modifiedDate là UTC (Z suffix), quy về ICT (+7)
    if not md:
        return False
    try:
        from zoneinfo import ZoneInfo
        ts_utc = dt.datetime.fromisoformat(md.replace("Z", "+00:00"))
        ts_ict = ts_utc.astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
        return ts_ict.date().isoformat() == today_str
    except Exception:
        # fallback: so chuỗi thô (UTC date)
        return md[:10] == today_str


# ── CỔNG TÁC DỤNG NGOÀI DUY NHẤT (MAJOR-1 r4) ───────────────────────────────
# Bản r3 truyền `dry_run` bằng tay tới từng chỗ gửi ⇒ writer vendor quên kiểm ở validate-reject ⇒ dry-run
# shadow/off gửi bus question THẬT (cùng loại M5/X10). Nay: mọi lượt (`run`/`run_vendor`/`run_broker`) đặt
# cờ trong `_dry_scope`, và MỌI tác dụng ngoài — append_event (`_bus`), Discord (`_discord`), sổ broker
# (`_ledger_append`), registry (`write_corp_actions`), marker hỏi-1-lần/ngày (`_ask_day_once`) — hỏi
# `_effects_blocked` trước. Selfcheck r4 kiểm bằng AST rằng KHÔNG hàm nào khác chạm append_event/notify/
# ledger_append/os.replace — thêm đường gửi mới mà không qua cổng ⇒ selfcheck FAIL có tên.
_DRY = []      # cờ dry-run của các lượt đang lồng nhau; có một True ⇒ chặn


@contextlib.contextmanager
def _dry_scope(dry_run):
    _DRY.append(bool(dry_run))
    try:
        yield
    finally:
        _DRY.pop()


def _effects_blocked(what):
    """True (và in điều lẽ ra đã làm) khi đang trong lượt dry-run."""
    if any(_DRY):
        print(f"  [DRY-RUN] KHÔNG {what[:400]}")
        return True
    return False


def _discord(msg):
    """Discord notify (chỉ khi có DISCORD_THREAD_ID) — qua cổng dry-run."""
    import subprocess
    thread_id = os.environ.get("DISCORD_THREAD_ID", "")
    if not thread_id or not os.path.exists(NOTIFY_SH):
        return
    if _effects_blocked(f"gửi Discord: {msg}"):
        return
    subprocess.run([NOTIFY_SH, msg, thread_id], check=False)


def _ledger_append(entries):
    """Ghi sổ broker — qua cổng dry-run (sổ là tác dụng ngoài: lượt sau đọc nó để quyết gửi bù/im)."""
    if _effects_blocked(f"ghi {len(entries)} dòng sổ {LEDGER_FILE}"):
        return
    BD.ledger_append(entries, LEDGER_FILE)


# ── KHOÁ REGISTRY = OUTPUT CỦA CA.validate (MAJOR-2 r4) ─────────────────────
def _norm_ticker(x):
    """Mã KHÔNG đến từ registry (symbol DNSE, lịch vendor, dòng sổ) chuẩn hoá ĐÚNG quy tắc CA.validate
    (`str().strip().upper()`) để so được với khoá registry. Selfcheck r4 (K0) khoá 2 quy tắc vào nhau.
    r5 (minor-2): MỘT quy tắc dùng chung với detector — `BD.norm_ticker` (detector chuẩn hoá ngay khi đọc)."""
    return BD.norm_ticker(x)


def _iso(x):
    """Ngày ISO như CA._date đọc ([:10] → date.fromisoformat); không đọc được ⇒ chuỗi thô [:10]."""
    try:
        return dt.date.fromisoformat(str(x if x is not None else "")[:10]).isoformat()
    except ValueError:
        return str(x if x is not None else "")[:10]


def _reg_rows(actions):
    """MỌI khoá (mã, ex, id) VÀ giá trị (hệ số, chân tiền, hiệu lực) của record registry, lấy từ OUTPUT của
    CA.validate — đúng như consumer (park_holdings/load_corp_actions/exdate_frame) đọc: mã strip().upper(),
    ex ISO, id validate tự sinh nếu vắng, chân tiền vắng = 0. Bản r3 tự `.upper()` riêng ⇒ record 'TPB '
    CONFIRMED vô hình với script nhưng HIỆU LỰC với consumer ⇒ cả 2 writer ghi record thứ hai (MAJOR-2).
    Record validate() từ chối ⇒ khoá best-effort cùng quy tắc + `invalid` (lý do): consumer đang bị chặn
    CẢ FILE bởi chính record đó, đối chiếu coi là LỆCH. Mỗi phần tử: dict(i, rec, ticker, ex, id,
    effective, v (output validate | None), invalid)."""
    out = []
    for i, r in enumerate(actions):
        try:
            v = CA.validate(r, i)
        except CA.CorpActionError as e:
            out.append({"i": i, "rec": r, "ticker": _norm_ticker(r.get("ticker")), "ex": _iso(r.get("ex_date")),
                        "id": str(r.get("id")), "effective": _effective(r), "v": None, "invalid": str(e)})
            continue
        out.append({"i": i, "rec": r, "ticker": v["ticker"], "ex": v["ex_date"], "id": str(v["id"]),
                    "effective": v["_status"].upper().startswith(CA.CONFIRMED_PREFIX), "v": v, "invalid": None})
    return out


def write_corp_actions(actions_list, dry_run=False):
    """Ghi lại corp_actions.json với list actions mới. Atomic tmp+rename.

    BLOCKER 1b (arch-review vòng 8): validate() TỪNG record trước khi ghi — writer này là điểm
    duy nhất tạo record CONFIRMED tự động, không đi qua ai review tay. Một record vượt biên
    QTY_MULT_MAX (lỗi gõ tay ở `exercise_ratio` nguồn, hoặc bug tính `mult`) mà lọt vào registry
    sẽ làm MỌI consumer khác (park_holdings, verify_account_snapshot, reconcile_equity) ném
    CorpActionError cho TOÀN BỘ ticker trong file, không riêng ticker hỏng — validate ở đây chặn
    trước khi file bị đầu độc, thay vì để 3 consumer khác nhau tự phát hiện sau.
    r3 (I1): cùng chốt kiểm bất biến ≤1 record HIỆU LỰC/(mã, ex) — lượt này tạo nhóm trùng ⇒
    CorpActionError, 0 ghi (lưới cuối: r4 m7 đã gộp ứng viên vendor trùng TRƯỚC vòng ghi).
    r4 MAJOR-1: dry-run đi qua cổng `_effects_blocked` như mọi tác dụng ngoài khác.
    """
    _validate_for_write(actions_list, load_corp_actions_raw())
    if dry_run or _effects_blocked(f"ghi {len(actions_list)} record vào {CORP_ACTIONS_FILE}"):
        print(f"[DRY-RUN] would write {len(actions_list)} records to {CORP_ACTIONS_FILE}")
        return
    data = {"actions": actions_list}
    tmp = CORP_ACTIONS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, CORP_ACTIONS_FILE)


def post_bus(ticker, event_id, ex_date, multiplier, acct_evidence, dry_run=False):
    """Ghi bus finding và notify Discord."""
    summary = (f"AUTO-CONFIRMED {ticker} {event_id}: ×{multiplier} (ex {ex_date}), "
               f"broker evidence: {acct_evidence}")
    payload = ({
        "status": "AUTO_CONFIRMED",
        "event_id": event_id,
        "ticker": ticker,
        "qty_multiplier": multiplier,
        "ex_date": ex_date,
        "broker_evidence": acct_evidence,
        "decided_by": "agent",
        "note": "auto-confirmed by corp_action_auto_confirm.py (2-source rule)"
    })
    if dry_run:
        print(f"[DRY-RUN] bus finding: {summary}")
        return
    _bus("finding", f"corp-action-auto-confirm-{ticker}", payload)   # MAJOR-1 r4: qua cổng duy nhất
    _discord(f"✅ **Corp Action AUTO-CONFIRMED** — **{ticker}** ×{multiplier} "
             f"(ex {ex_date}): broker credit xác nhận, sổ lô tự đồng bộ, "
             f"DollarBill sẽ build plan sạch.")


# ── Main ───────────────────────────────────────────────────────────────────

def run(date_str, dry_run=False):
    with _dry_scope(dry_run):
        return _run(date_str, dry_run)


def _run(date_str, dry_run):
    mode = broker_mode()
    if mode == "off":
        return run_vendor(date_str, dry_run=dry_run)
    if not dry_run:
        _sandbox_guard()
    # Khoá bao CẢ nhánh vendor: hai nhánh cùng đọc-sửa-ghi data/corp_actions.json; cron + chạy tay
    # song song không được đè record của nhau (arch-review v2 N3). off ⇒ không khoá (như cũ).
    lk = None if dry_run else _lock(LEDGER_FILE)
    if not dry_run and lk is None:
        print(f"❌ không lấy được khoá {LEDGER_FILE}.lock sau {LOCK_WAIT_S}s — tiến trình khác đang "
              f"chạy; KHÔNG chạy nhánh nào.")
        _ask_lock_unavailable(date_str, mode)
        return 1
    global _LOCK_HELD
    _LOCK_HELD = lk is not None   # cả đời run(): 2 nhánh dùng chung khoá này, run_broker không xin lại
    try:
        return _run_both(date_str, dry_run, mode)
    finally:
        _LOCK_HELD = False
        if lk:
            lk.close()


def _run_branch(name, fn, date_str, dry_run, mode):
    """Chạy MỘT nhánh (vendor / broker) độc lập với nhánh kia: nhánh nổ ⇒ in traceback + bus
    `question` urgency high 1 lần/ngày (r5 M-B: `error` không được ops_health_check leo thang,
    rc bị bỏ qua — cùng lớp #3 vòng 4) + rc=1, nhánh còn lại VẪN chạy (r5 M-C: hai nhánh đọc
    nguồn khác nhau, chỉ chung khoá + registry; vendor nổ không có lý do làm mất lượt broker).
    SandboxMismatch KHÔNG bị nuốt (đang trỏ lệch production ⇒ dừng hẳn)."""
    try:
        return fn()
    except SandboxMismatch:
        raise
    except Exception as e:   # crash nhánh KHÔNG được chỉ nằm trong log cron (§29: lỗi thật)
        import traceback
        tb = traceback.format_exc()
        print(tb)
        _ask_day_once(f"{name}crash", date_str, f"corp-action-{name}-crash-{date_str}",
                      {"question": (f"Nhánh {name} của corp_action_auto_confirm NỔ lượt {date_str} "
                                    f"({type(e).__name__}: {e}) — nhánh còn lại vẫn chạy độc lập. "
                                    f"Cần người đọc log cron và chạy lại tay --date {date_str}."),
                       "error": f"{type(e).__name__}: {e}", "traceback_tail": tb[-1500:],
                       "mode": mode, "urgency": "high"})
        return 1


def _run_both(date_str, dry_run, mode):
    if mode == "live":
        # Broker là nguồn chính ⇒ ghi TRƯỚC; vendor sau, chỉ xác nhận (không bao giờ ghi).
        rc_b = _run_branch("broker", lambda: run_broker(date_str, dry_run=dry_run, mode=mode),
                           date_str, dry_run, mode)
        rc = _run_branch("vendor", lambda: run_vendor(date_str, dry_run=dry_run, confirm_only=True),
                         date_str, dry_run, mode)
        return rc_b or rc
    rc = _run_branch("vendor", lambda: run_vendor(date_str, dry_run=dry_run),
                     date_str, dry_run, mode)
    rc_b = _run_branch("broker", lambda: run_broker(date_str, dry_run=dry_run, mode=mode),
                       date_str, dry_run, mode)
    return rc or rc_b


def run_vendor(date_str, dry_run=False, confirm_only=False):
    """Nhánh vendor. `confirm_only` (live, broker-primary) ⇒ KHÔNG ghi registry, chỉ đối chiếu/hỏi. Lỗi ở đường hỏi người (N9 / tỉ lệ lệch broker) KHÔNG được làm mất lô vendor
    (arch-review v4 #6: bản cũ để ngoại lệ ledger_append/_bus thoát ⇒ mất cả lô, 0 bus event):
    gom lỗi, chạy hết lô, rồi báo 1 bus question (urgency high) + rc=1."""
    with _dry_scope(dry_run):
        return _run_vendor_outer(date_str, dry_run, confirm_only)


def _run_vendor_outer(date_str, dry_run, confirm_only):
    ask_failed = []
    rc = _run_vendor(date_str, dry_run, ask_failed, confirm_only)
    if ask_failed:
        print(f"  ❌ {len(ask_failed)} lần hỏi người lỗi trong nhánh vendor: {ask_failed}")
        try:
            _bus("question", f"corp-action-vendor-ask-failed-{date_str}",
                 {"question": (f"Nhánh vendor KHÔNG gửi được câu hỏi đối chiếu record broker "
                               f"({len(ask_failed)} mục) — lô vendor vẫn chạy hết. Cần người kiểm "
                               f"tay các mã dưới đây trong data/corp_actions.json."),
                  "failed": ask_failed, "urgency": "high"})
        except Exception as e:  # §29: kênh báo lỗi cũng hỏng ⇒ chỉ còn log cron, nói thật
            print(f"  ❌ không gửi được cả bus question báo lỗi: {type(e).__name__}: {e}")
        rc = 1
    return rc


def _ask_guarded(failed, fn, *args):
    """Gọi 1 hàm hỏi người; lỗi (trừ SandboxMismatch) ⇒ in traceback + ghi vào `failed`, không ném."""
    try:
        fn(*args)
    except SandboxMismatch:
        raise
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        failed.append({"call": fn.__name__, "ticker": args[0], "ex_date": args[1],
                       "error": f"{type(e).__name__}: {e}"})


def _run_vendor(date_str, dry_run, ask_failed, confirm_only=False):
    print(f"[corp_action_auto_confirm] date={date_str} dry_run={dry_run} confirm_only={confirm_only}")

    candidates = get_candidate_events(date_str)
    if not candidates:
        print("  → không có sự kiện nào trong upcoming_events_held cần kiểm.")
        return 0
    actions_raw = load_corp_actions_raw()
    rows = _reg_rows(actions_raw)
    view = _registry_view(actions_raw)
    # m7 r4: gộp ứng viên TRÙNG (cùng (mã, ex) chuẩn hoá) TRƯỚC vòng ghi — bản r3 để 1 dòng ISS lặp đi tới
    # chốt I1 ở write_corp_actions ⇒ TỪ CHỐI CẢ LÔ (mã hợp lệ khác cũng không được ghi). Trùng hệt ⇒ 1
    # ứng viên; mâu thuẫn (2 tỉ lệ/mã sự kiện) ⇒ CHỈ nhóm đó bị chặn + hỏi, mã khác đi tiếp.
    candidates, conflicts = _group_candidates(candidates)
    # MAJOR-1 r5 (I2, lần lọt thứ 3): câu hỏi KHẲNG ĐỊNH trạng thái registry quanh ex (conflict / cash-leg /
    # near-record) KHÔNG gửi trong vòng — gom vào `deferred`, gửi SAU khi biết lô ghi gì (`_flush_deferred`).
    deferred = []
    for (tk, ex), evs in sorted(conflicts.items()):
        print(f"  [{tk}] ❌ lịch vendor có {len(evs)} sự kiện CP KHÁC NHAU cùng ex {ex} — chỉ chặn mã này, hỏi người.")
        deferred.append(("conflict", tk, ex, evs))
    if confirm_only:      # live: nhánh vendor KHÔNG ghi ⇒ registry hiện tại CHÍNH là trạng thái sau lô
        _flush_deferred(ask_failed, deferred, actions_raw, date_str)
        return _vendor_confirm_only(date_str, ask_failed, candidates, actions_raw, rows, view)

    accounts = _get_account_nos(date_str)
    if not accounts:
        print(f"  → không đọc được account_no từ dnse_raw_{date_str}.jsonl.")
        _flush_deferred(ask_failed, deferred, actions_raw, date_str)
        return 1

    print(f"  {len(candidates)} candidate event(s), {len(accounts)} account(s): "
          f"{[a for _, a in accounts]}")

    new_confirms = []
    pending_bus_posts = []   # B-4 arch-review vòng 9: post_bus() BỊ DỜI ra sau write thành công —
                              # bản cũ post_bus() TRƯỚC write_corp_actions() nên trên đường bị
                              # reject (validate() ném CorpActionError) Discord/bus vẫn hiện
                              # "✅ AUTO-CONFIRMED" dù registry KHÔNG hề được ghi (tự mâu thuẫn
                              # artifact-vs-thực-tế, MIKE.md quy chuẩn #2).
    old_count = len(actions_raw)   # B-3: mốc phân biệt record CŨ (đã có trước lượt này) vs MỚI
    vfn = _vendor_events_fn(date_str)

    for ev in candidates:
        ticker, ex_date = ev["ticker"], ev["date"]
        mult = _vendor_mult(ev)
        if (ticker, ex_date) in view:
            # r4: registry ĐÃ có (mã, ex) — MỌI trạng thái/provenance — ⇒ KHÔNG BAO GIỜ ghi thêm (I1/I2), đối
            # chiếu như nhánh chỉ-xác-nhận. Bản cũ: chỉ so record BROKER (record người ký lệch tỉ lệ/chân tiền
            # ⇒ im "đã CONFIRMED rồi"), và record PROPOSED/REVOKED cùng (mã, ex) ⇒ ghi CONFIRMED thứ hai cạnh nó.
            ok, why, rid = _record_vs_vendor(view[(ticker, ex_date)], mult, _vendor_div_same_ex(vfn, ticker, ex_date))
            if ok:
                print(f"  [{ticker}] registry đã có ({ticker}, {ex_date}) — {why} — không ghi thêm.")
            else:
                print(f"  [{ticker}] ⚠ {why} — registry giữ nguyên, hỏi người.")
                _ask_guarded(ask_failed, _ask_registry_vs_vendor, ticker, ex_date, why, rid)
            continue
        near = _near_duplicate(rows, ticker, ex_date, date_str)
        if near:
            # m8 r4: record MỌI provenance/trạng thái cùng mã ở ex gần (bản cũ chỉ record broker) — có thể CÙNG
            # sự kiện với ex khác ⇒ ghi thêm là áp hệ số 2 lần ⇒ không ghi, hỏi người.
            print(f"  [{ticker}] ❌ {near[0]} — không tự xác nhận, cần người kiểm.")
            deferred.append(("near-record", ticker, ex_date, None))   # near có thể là record CỦA LÔ (chưa chắc ghi được)
            continue
        if mult is None:
            print(f"  [{ticker}] vendor KHÔNG khai tỉ lệ đọc được (exercise_ratio={ev.get('exercise_ratio')!r}) "
                  f"⇒ không tự xác nhận")
            continue
        ratio = mult - 1.0

        print(f"  [{ticker}] ex_date={ex_date}, ratio={ratio:.7g} (×{mult:.7g}) — kiểm broker ...")

        acct_results = {}
        for acct_no, acct_lbl in accounts:
            first, last = _get_ticker_snapshots(acct_no, ticker, date_str)
            if first is None:
                # account không giữ ticker này
                continue
            if not broker_modified_today(last, date_str):
                # broker chưa credit hôm nay cho ticker này
                acct_results[acct_lbl] = {
                    "verdict": "NOT_MODIFIED_TODAY",
                    "qty_before": first.get("openQuantity"),
                    "qty_after": last.get("openQuantity"),
                }
                continue
            ok, qty_r, cost_r = check_ratio(first, last, mult)
            acct_results[acct_lbl] = {
                "verdict": "MATCH" if ok else "MISMATCH",
                "qty_before": int(first.get("openQuantity") or 0),
                "qty_after":  int(last.get("openQuantity") or 0),
                "qty_ratio":  qty_r,
                "cost_ratio": cost_r,
                "cost_before": float(first.get("costPrice") or 0),
                "cost_after": float(last.get("costPrice") or 0),
                "modified_today": True,
            }

        print(f"  [{ticker}] broker results: {acct_results}")

        if not acct_results:
            print(f"  [{ticker}] không account nào giữ mã này → CANNOT_VERIFY, bỏ qua.")
            continue

        any_mismatch = any(v["verdict"] == "MISMATCH" for v in acct_results.values())
        has_match    = any(v["verdict"] == "MATCH"    for v in acct_results.values())
        # r4: KL khớp vendor ở MỌI tài khoản lệch, chỉ GIÁ VỐN lệch >2% ⇒ dấu hiệu chân tiền cùng ex (TPB 10-01:
        # 500đ ≈ 3% giá vốn) ⇒ đi tiếp tới cổng chân tiền (HỎI), không dừng im ở "MISMATCH".
        qty_only = any_mismatch and all(_qty_ok(v, mult) for v in acct_results.values() if v["verdict"] == "MISMATCH")

        if any_mismatch and not qty_only:
            print(f"  [{ticker}] ❌ MISMATCH — không tự xác nhận, cần người kiểm.")
            continue
        if not has_match and not qty_only:
            print(f"  [{ticker}] broker chưa credit hôm nay → bỏ qua.")
            continue
        cash_why = _writer_cash_hint(_vendor_div_same_ex(vfn, ticker, ex_date), acct_results, mult)
        if cash_why:
            print(f"  [{ticker}] ❌ {cash_why} — KHÔNG tự ghi (record thiếu chân tiền ⇒ cổng giá đêm FAIL), hỏi người.")
            deferred.append(("cash-leg", ticker, ex_date, (mult, cash_why)))
            continue
        if any_mismatch:      # bất biến cũ giữ nguyên: có tài khoản MISMATCH ⇒ KHÔNG BAO GIỜ tự ghi
            print(f"  [{ticker}] ❌ MISMATCH — không tự xác nhận, cần người kiểm.")
            continue

        # ── ĐỦ ĐIỀU KIỆN: tự CONFIRMED ─────────────────────────────────
        event_id = f"{ticker}-{ex_date}-BONUS-ISSUE"
        from zoneinfo import ZoneInfo
        now_ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%dT%H:%M:%S+07:00")

        ev_code = ev.get("event_code", "ISS")
        ev_type = "BONUS_ISSUE" if ev_code == "ISS" else "SPLIT"

        new_rec = {
            "id": event_id,
            "ticker": ticker,
            "event_type": ev_type,
            "ratio_text": ev.get("title", f"tỉ lệ {ratio*100:.0f}%"),
            "qty_multiplier": mult,
            "ex_date": ex_date,
            "record_date": ev.get("record_date"),
            "broker_effective_ts": f"{date_str}T00:00:00",  # placeholder; refined below
            "_status": (f"CONFIRMED — corp_action_auto_confirm.py {now_ict} "
                        f"(2-source: upcoming_events_held + broker qty/cost ratio match). "
                        f"Thu hồi: đổi _status thành 'REVOKED ...'"),
            "confirmed_by": "corp_action_auto_confirm.py (agent)",
            "decided_by": "agent",
            "confirmed_at": now_ict,
            "evidence": [
                (f"NGUỒN 1 — corp_action_daily {date_str} upcoming_events_held: "
                 f"ticker={ticker}, event_code={ev_code}, date={ex_date}, "
                 f"exercise_ratio={ratio}, price_adjusting=True, days_ahead={ev.get('days_ahead')}"),
            ] + [
                (f"NGUỒN 2 — broker {lbl}: qty {r['qty_before']}→{r['qty_after']} "
                 f"(×{r.get('qty_ratio')}), costPrice ratio ×{r.get('cost_ratio')}, "
                 f"modified_today=True")
                for lbl, r in acct_results.items() if r["verdict"] == "MATCH"
            ],
            "verify_against_bq": f"PENDING — chạy sau {ex_date}: "
                                  f"python3 mike/bin/corp_actions.py --verify {event_id}",
            "note": "Cùng mẫu broker credit 1 phiên trước ex_date như VHM/MBB/BID/VIX/MSB.",
        }

        # Refine broker_effective_ts từ modifiedDate account khớp đầu tiên
        for lbl, r in acct_results.items():
            if r["verdict"] == "MATCH":
                for acct_no, albl in accounts:
                    if albl == lbl:
                        _, last = _get_ticker_snapshots(acct_no, ticker, date_str)
                        if last and last.get("modifiedDate"):
                            # modifiedDate là UTC → bỏ .Z suffix
                            new_rec["broker_effective_ts"] = last["modifiedDate"].replace("Z", "")
                        break
                break

        print(f"  [{ticker}] ✅ AUTO-CONFIRMED ×{mult} (ex {ex_date})")
        if dry_run:
            print(f"  [DRY-RUN] new record: {json.dumps(new_rec, ensure_ascii=False)[:300]}")

        actions_raw.append(new_rec)
        rows += _reg_rows([new_rec])     # ứng viên sau cùng mã ở ex gần (cửa sổ [hôm nay, phiên kế]) ⇒ near-dup
        new_confirms.append((ticker, event_id))
        pending_bus_posts.append((ticker, event_id, ex_date, mult, acct_results))

    rc = 0
    if new_confirms:
        try:
            write_corp_actions(actions_raw, dry_run=dry_run)
        except CA.CorpActionError as e:
            # B-3 arch-review vòng 9: write_corp_actions() validate() TOÀN BỘ registry (record
            # CŨ + MỚI), nhưng bản cũ luôn quy kết "record vừa tạo" và trỏ candidates=CANDIDATE
            # MỚI — SAI khi record hỏng là record CŨ đã tồn tại từ TRƯỚC lượt này (vd VHM index 0
            # hỏng sẵn), khiến người xử lý đi kiểm nhầm candidate mới trong khi thủ phạm thật là
            # record cũ (và nếu vậy thì park_holdings/verify_account_snapshot/reconcile_equity
            # CŨNG đang bị chặn đồng thời — thông tin quan trọng bị mất nếu quy kết sai).
            import re
            m = re.search(r"corp_actions\[(\d+)\]", str(e))
            bad_idx = int(m.group(1)) if m else None
            new_tickers = [t for t, _ in new_confirms]
            # R9-4 arch-review vòng 10: write_corp_actions() → validate() DỪNG ở record hỏng
            # ĐẦU TIÊN gặp phải (không kiểm hết toàn bộ list) — khi record hỏng là record CŨ
            # (index < old_count), các candidate MỚI của lượt này CHƯA HỀ được validate() đọc
            # tới, nên không có bằng chứng để khẳng định chúng "không phải" thủ phạm hay
            # "chắc chắn lành". Chỉ nói điều ĐÃ ĐỌC được.
            bad_is_preexisting = bad_idx is not None and bad_idx < old_count
            bad_ticker = (actions_raw[bad_idx].get("ticker") if bad_idx is not None
                          and 0 <= bad_idx < len(actions_raw) else None)
            bad_label = f"{bad_ticker} (index {bad_idx})" if bad_ticker else f"index {bad_idx}"
            if bad_is_preexisting:
                print(f"\n❌ KHÔNG GHI — record cũ {bad_label}, đã tồn tại TỪ TRƯỚC lượt này, "
                      f"không qua validate(): {e}\n"
                      f"   ⚠ Registry đã hỏng TỪ TRƯỚC — mọi consumer khác "
                      f"(park_holdings/verify_account_snapshot/reconcile_equity) CŨNG đang bị "
                      f"chặn bởi CHÍNH record này.")
                note = (f"registry đã có record HỎNG TỪ TRƯỚC lượt chạy này ({bad_label}). "
                        f"validate() dừng ở record hỏng ĐẦU TIÊN nên các candidate mới của lượt "
                        f"này ({new_tickers}) CHƯA được kiểm tra — không khẳng định chúng có hỏng "
                        f"hay không. Mọi consumer khác "
                        f"(park_holdings/verify_account_snapshot/reconcile_equity) cũng đang bị "
                        f"chặn bởi cùng record cũ này — cần sửa/REVOKE record cũ trước, rồi chạy "
                        f"lại để biết candidate mới có qua được validate() hay không.")
                candidates_payload = []
            elif bad_idx is not None:
                print(f"\n❌ KHÔNG GHI — record vừa tạo {bad_label} không qua validate(): {e}")
                note = ("auto_confirm tạo record hỏng, KHÔNG ghi vào registry — cần người kiểm tay")
                candidates_payload = new_tickers
            else:
                # Không parse được index từ message lỗi — không đủ bằng chứng để nói "cũ" hay
                # "mới", tránh suy diễn.
                print(f"\n❌ KHÔNG GHI — không xác định được record nào hỏng từ message lỗi "
                      f"validate(): {e}")
                note = (f"validate() báo lỗi nhưng không parse được index record hỏng từ message "
                        f"({e!r}) — không xác định được record cũ hay candidate mới ({new_tickers}) "
                        f"là thủ phạm, cần kiểm tay toàn bộ registry.")
                candidates_payload = new_tickers
            _bus("question", "corp-action-auto-confirm-validate-reject",   # MAJOR-1 r4: qua cổng dry-run
                 {"error": str(e), "bad_record_index": bad_idx,
                  "bad_record_is_preexisting": bad_is_preexisting,
                  "candidates": candidates_payload,
                  "urgency": "high", "note": note})
            # B-4: KHÔNG post_bus() ở đây — pending_bus_posts chưa hề được gửi (bị dời ra sau
            # write thành công) nên không có gì cần rút lại; "✅ AUTO-CONFIRMED" sẽ KHÔNG BAO GIỜ
            # xuất hiện trên đường reject.
            rc = 1
    # MAJOR-1 r5: lô đã quyết — ghi được (hoặc dry-run: SẼ ghi) ⇒ registry sau lô = cũ + record lô; bị từ chối
    # ⇒ = cũ. Câu hỏi khẳng định "registry có/chưa có record quanh ex" tính trên ĐÚNG trạng thái đó.
    _flush_deferred(ask_failed, deferred, actions_raw if rc == 0 else actions_raw[:old_count], date_str)
    if rc:
        return rc
    if new_confirms:
        for ticker, event_id, ex_date, mult, acct_results in pending_bus_posts:
            post_bus(ticker, event_id, ex_date, mult, acct_results, dry_run=dry_run)
        print(f"\nXong: {len(new_confirms)} event(s) AUTO-CONFIRMED: "
              f"{[t for t, _ in new_confirms]}")
    else:
        print("Xong: không có event mới nào đủ điều kiện tự xác nhận.")

    return 0


def _vendor_confirm_only(date_str, ask_failed, candidates, actions_raw, rows, view):
    """LIVE broker-primary: nhánh vendor KHÔNG BAO GIỜ ghi registry. Mỗi sự kiện CP vendor sắp ex:
      · registry đã có (mã, ex) — record MỌI provenance/trạng thái — đối chiếu `_record_vs_vendor`:
        record chưa CONFIRMED / validate() từ chối, hệ số lệch >1%, chân tiền record (như consumer đọc) lệch
        Σ DIV vendor cùng ex ⇒ hỏi (không đè); vendor KHÔNG khai tỉ lệ/DIV ⇒ "không khai" (không so trục đó);
        khớp ⇒ in CẢ HAI số đã so + trạng thái credit broker;
      · record MỌI provenance cùng mã ở ex KHÁC gần đó (`_near_duplicate`, m2 r4: bản r3 chỉ record broker)
        ⇒ hỏi, nêu id + ONE_RECORD_RULE;
      · nhánh broker LIVE đã có mục sổ cho mã ở phiên này (đã ghi/hỏi theo verdict của nó) ⇒ thôi;
      · còn lại, mã đang giữ theo `BD.held_tickers` (RC2/M3/m5) ⇒ vendor có sự kiện mà sổ broker không có mục
        ⇒ hỏi. Có tài khoản KHÔNG xác định được mà mã không nằm ở tài khoản đã biết ⇒ hỏi INSUFFICIENT (I4).
        Chỉ "không giữ" khi MỌI tài khoản đã biết xác định.
    Hỏi QUÁ HẠN do `_registry_sweep` của nhánh broker lo (1 nơi hỏi); câu hỏi vendor-only/held-unknown được
    `_resolve_asks` trả lời khi registry có record hiệu lực / sổ broker thấy mã (m4 r4). Sổ broker đọc hỏng
    ⇒ coi như broker chưa thấy (hỏi thừa an toàn hơn im). Mọi lần hỏi qua cổng dry-run (`_bus`)."""
    ledger_note = "sổ broker đọc được"
    try:
        intents, _done = BD.ledger_state(LEDGER_FILE)
    except BD.CorpActionLedgerError as e:       # §29: nói lỗi thật
        print(f"  ⚠ sổ broker đọc hỏng ({e}) ⇒ coi như nhánh broker chưa thấy mã nào")
        intents = {}
        ledger_note = f"sổ broker ĐỌC HỎNG ({e}) — không biết nhánh broker đã thấy gì"
    broker_seen = {_norm_ticker(e.get("ticker")) for e in intents.values()
                   if e.get("mode") == "live" and e.get("credit_day") == date_str}
    held, unknown = _held_info(date_str)
    vfn = _vendor_events_fn(date_str)
    for ev in candidates:
        ticker, ex_date = ev["ticker"], ev["date"]
        mult = _vendor_mult(ev)
        shown = f"×{mult:.7g}" if mult is not None else f"KHÔNG khai tỉ lệ (exercise_ratio={ev.get('exercise_ratio')!r})"
        if (ticker, ex_date) in view:
            ok, why, rid = _record_vs_vendor(view[(ticker, ex_date)], mult, _vendor_div_same_ex(vfn, ticker, ex_date))
            if not ok:
                print(f"  [{ticker}] ⚠ {why} — registry giữ nguyên, hỏi người.")
                _ask_guarded(ask_failed, _ask_registry_vs_vendor, ticker, ex_date, why, rid)
            else:
                print(f"  [{ticker}] registry ({ticker}, {ex_date}) {why}; credit broker: "
                      f"{_credit_state(ticker, ex_date, date_str, intents)}")
            continue
        near = _near_duplicate(rows, ticker, ex_date, date_str)
        if near:
            print(f"  [{ticker}] ❌ {near[0]} — hỏi người.")
            _ask_guarded(ask_failed, _ask_vendor_near_record, ticker, ex_date, *near)
            continue
        if ticker in broker_seen:
            print(f"  [{ticker}] nhánh broker đã có mục sổ phiên {date_str} (đã ghi/hỏi theo verdict) — vendor không hỏi lặp.")
            continue
        if held is None or (ticker not in held and unknown):
            why_u = (f"không có file positions dnse_raw nào trong {BD.HELD_LOOKBACK_DAYS} ngày tới {date_str}"
                     if held is None else f"tài khoản KHÔNG xác định được: {'; '.join(unknown)}")
            print(f"  [{ticker}] ❌ {why_u} ⇒ không xác định được mã có đang giữ — hỏi người (không bỏ qua).")
            _ask_guarded(ask_failed, _ask_vendor_held_unknown, ticker, ex_date, shown,
                         ev.get("event_code"), date_str, why_u)
            continue
        if ticker not in held:
            print(f"  [{ticker}] bản ghi positions khác rỗng cuối của MỌI tài khoản đã biết ({date_str}/phiên "
                  f"trước) không có mã ⇒ không giữ — bỏ qua.")
            continue
        print(f"  [{ticker}] vendor {ev.get('event_code')} {shown} ex {ex_date}, đang giữ ở {held[ticker]}, "
              f"nhưng {ledger_note} và KHÔNG có mục nào cho mã phiên {date_str} ⇒ KHÔNG ghi (broker là "
              f"nguồn chính), hỏi người.")
        _ask_guarded(ask_failed, _ask_vendor_only, ticker, ex_date, shown, ev.get("event_code"),
                     date_str, held[ticker], ledger_note)
    return 0


def _held_info(date_str):
    """`BD.held_tickers` (mã đã chuẩn hoá ngay khi detector đọc symbol — minor-2 r5). (None, None) nếu không có file."""
    return BD.held_tickers(date_str, EXEC_DIR) or (None, None)


def _vendor_mult(ev):
    """Hệ số vendor = 1 + exercise_ratio. Vắng / không đọc được / ≤0 ⇒ None = vendor KHÔNG khai tỉ lệ (m6 r4:
    bản r3 đọc vắng thành 0 ⇒ "vendor khai ×1" — khẳng định điều vendor không nói, §29)."""
    try:
        r = float(ev.get("exercise_ratio"))
    except (TypeError, ValueError):
        return None
    return 1.0 + r if math.isfinite(r) and r > 0 else None


def _vendor_div_same_ex(vfn, ticker, ex):
    """Giá trị DIV vendor CÙNG ex của mã (đã bỏ dòng trùng hệt): [] = vendor không khai DIV; None = lịch
    vendor đọc hỏng."""
    vev = vfn(ticker)
    if vev == BD.VENDOR_UNREADABLE:
        return None
    return [e.get("value_per_share") for e in BD.dedup_vendor(vev)
            if str(e.get("event_code") or "").upper() == "DIV" and _iso(e.get("date")) == ex]


def _group_candidates(cands):
    """m7 r4: ứng viên vendor theo (mã, ex) đã chuẩn hoá. Dòng TRÙNG HỆT (BD.dedup_vendor — feed ghi lặp) ⇒ 1
    ứng viên; ≥2 sự kiện KHÁC nhau cùng (mã, ex) ⇒ `conflicts` (không biết cộng dồn hay ghi trùng ⇒ chỉ
    nhóm đó bị chặn). Trả (ứng viên, {(mã, ex): [sự kiện]})."""
    by = {}
    for ev in cands:
        by.setdefault((ev["ticker"], ev["date"]), []).append(ev)
    ok, conflicts = [], {}
    for k in sorted(by):
        u = BD.dedup_vendor(by[k])
        if len(u) == 1:
            ok.append(u[0])
        else:
            conflicts[k] = u
    return ok, conflicts


def _flush_deferred(ask_failed, deferred, final_actions, date_str):
    """MAJOR-1 r5 (I2 — lần lọt thứ 3, cùng lớp M2 v2 / m1 v3): bản r4 gửi vendor-conflict / vendor-cash-leg
    TRONG vòng, `_existing_id` tính trên registry TRƯỚC lô ⇒ câu hỏi khẳng định "registry chưa có record quanh
    ex" trong khi CHÍNH lô đó ghi record cùng mã ở ex kề (m7b) ⇒ người làm theo tạo record hiệu lực thứ 2.
    Nay mọi câu hỏi khẳng định trạng thái registry quanh ex được gửi ở đây, tính trên `final_actions` = registry
    SAU lô (cũ + record lô đã ghi / dry-run sẽ ghi; lô bị từ chối ⇒ chỉ cũ):
      conflict / cash-leg ⇒ id record cùng (mã, ex) hoặc near-dup (có thể là record của lô) ⇒ câu hỏi chỉ đề
        nghị SỬA/THU HỒI nó; không có ⇒ đề nghị ghi 1 record;
      near-record ⇒ record near-dup trong registry sau lô; lúc quyết near là record CỦA LÔ mà lô bị từ chối ⇒
        không có record nào để nêu ⇒ KHÔNG hỏi (câu validate-reject đã hỏi cả lô), in lý do; lượt sau xét lại."""
    rows, view = _reg_rows(final_actions), _registry_view(final_actions)
    for kind, tk, ex, extra in deferred:
        if kind == "conflict":
            _ask_guarded(ask_failed, _ask_vendor_conflict, tk, ex, extra, _existing_id(view, rows, tk, ex, date_str))
        elif kind == "cash-leg":
            _ask_guarded(ask_failed, _ask_vendor_cash_leg, tk, ex, *extra, _existing_id(view, rows, tk, ex, date_str))
        else:
            near = _near_duplicate(rows, tk, ex, date_str)
            if near:
                _ask_guarded(ask_failed, _ask_vendor_near_record, tk, ex, *near)
            else:
                print(f"  [{tk}] near-dup lúc quyết là record CỦA LÔ mà lô KHÔNG ghi được ⇒ registry sau lô không có "
                      f"record nào quanh ex {ex} để nêu — không hỏi near-record (validate-reject đã hỏi cả lô).")


def _existing_id(view, rows, tk, ex, credit_day):
    """id record registry cùng (mã, ex) hoặc ở ex gần (near-dup) — I2: câu hỏi chỉ được đề nghị SỬA/THU HỒI
    nó, không đề nghị ghi record thứ hai. None nếu registry trống quanh ex."""
    if (tk, ex) in view:
        return str(view[(tk, ex)].get("id"))
    near = _near_duplicate(rows, tk, ex, credit_day)
    return near[1] if near else None


def _qty_ok(r, mult):
    """Tài khoản có KL tăng đúng hệ số vendor (±RATIO_TOL) — bất kể giá vốn."""
    q = r.get("qty_ratio")
    return q is not None and abs(q - mult) <= RATIO_TOL * mult


def _writer_cash_hint(divs, acct_results, mult):
    """Writer vendor chỉ ghi hệ số KL; record thiếu chân tiền trong khi thật có cổ tức tiền cùng ex ⇒ consumer
    đọc 0 ⇒ cổng giá đêm FAIL (ca TPB 10-01, open #1 r3). `check_ratio` ±2% để lọt chân tiền tới ~2% giá ⇒
    kiểm thêm 2 bằng chứng đọc được: (a) lịch vendor có DIV cùng ex (hoặc lịch DIV đọc hỏng); (b) giá vốn
    broker giảm KHÁC hệ số KL thuần: chân tiền ngụ ý = giá vốn trước − giá vốn sau × hệ số KL ≥ 1đ/cp (tài
    khoản MATCH, và tài khoản MISMATCH chỉ vì giá vốn — KL vẫn đúng hệ số vendor). Trả lý do KHÔNG tự ghi (nêu
    số đã đọc, §29) hoặc None."""
    if divs is None:
        return "lịch DIV vendor cùng ex đọc hỏng ⇒ không biết có chân tiền"
    if divs:
        return f"lịch vendor có DIV cùng ex {divs}đ/cp ⇒ record cần chân tiền"
    for lbl, r in sorted(acct_results.items()):
        if r.get("verdict") not in ("MATCH", "MISMATCH") or not r.get("qty_before") or not _qty_ok(r, mult):
            continue
        q = r["qty_after"] / r["qty_before"]
        implied = r["cost_before"] - r["cost_after"] * q
        if abs(implied) >= BD.CASH_LEG_MIN_VND:
            return (f"giá vốn broker {lbl} {r['cost_before']:,.4f}→{r['cost_after']:,.4f} với KL ×{q:.7g}: lệch "
                    f"hệ số KL thuần {implied:+,.1f}đ/cp ⇒ có chân tiền chưa khai")
    return None


def _record_vs_vendor(rec, mult, vcash):
    """PURE. Record registry CÙNG (mã, ex) — MỌI provenance — vs sự kiện CP vendor ×`mult` (None = vendor KHÔNG
    khai tỉ lệ) và `vcash` (giá trị DIV vendor cùng ex: list, [] = vendor KHÔNG khai DIV, None = lịch hỏng).
    Trả (khớp?, lý do nêu CẢ HAI số đã so, id record). Hệ số/chân tiền record lấy từ OUTPUT CA.validate (như
    consumer đọc: chân tiền vắng = 0); validate() từ chối ⇒ LỆCH. Vendor không khai trục nào ⇒ trục đó "không
    so" (m5/m6 r4 — thống nhất PARTIAL của BD.vendor_crosscheck: vắng ≠ lệch; bản r3 coi vắng DIV là 0đ/cp,
    vắng tỉ lệ là ×1)."""
    rid = str(rec.get("id"))
    st = str(rec.get("_status", ""))
    prov = rec.get("provenance") or "người ký/vendor cũ"
    vshown = f"×{mult:.7g}" if mult is not None else "KHÔNG khai tỉ lệ"
    if rec.get("_dup_ids"):
        return False, _dup_why(rec), rid
    if rec.get("_invalid"):
        return False, (f"record {rid!r} ({prov}) bị CA.validate() từ chối: {rec['_invalid']} — consumer đang "
                       f"chặn CẢ registry; vendor {vshown}"), rid
    if not st.upper().startswith(CA.CONFIRMED_PREFIX):
        return False, (f"record {rid!r} ({prov}) trạng thái {st[:40]!r} — CHƯA áp dụng, trong khi "
                       f"vendor {vshown}"), rid
    rm = rec["_v"]["qty_multiplier"]
    if mult is None:
        qty_note = f"vendor KHÔNG khai tỉ lệ (không so hệ số; record ×{rm:.7g})"
    elif abs(rm - mult) > BROKER_VENDOR_MULT_TOL * mult:
        return False, f"vendor khai ×{mult:.7g} nhưng record {rid!r} ({prov}) là ×{rm:.7g}", rid
    else:
        qty_note = f"record ×{rm:.7g} vs vendor ×{mult:.7g}"
    rcv = rec["_v"]["cash_leg_vnd_per_share"]
    shown = ("KHÔNG khai (consumer đọc 0)" if rec.get("cash_leg_vnd_per_share") is None
             else f"{rcv:,.0f}đ/cp")
    if vcash is None:
        cash_note = f"chân tiền record {shown}, lịch vendor đọc hỏng (không so được)"
    elif not vcash:
        cash_note = f"chân tiền record {shown}, vendor KHÔNG khai DIV cùng ex (không so — PARTIAL)"
    else:
        vals = [BD._vnum(x) for x in vcash]
        if None in vals:
            return False, f"record {rid!r} chân tiền {shown} vs DIV vendor không đọc được {vcash}", rid
        if abs(sum(vals) - rcv) > BD.VENDOR_CASH_TOL_VND:
            return False, (f"record {rid!r} ({prov}) chân tiền {shown} vs DIV vendor cùng ex "
                           f"{sum(vals):,.0f}đ/cp"), rid
        cash_note = f"chân tiền record {rcv:,.0f} = vendor {sum(vals):,.0f}đ/cp"
    return True, f"khớp: record {rid!r} ({prov}): {qty_note}; {cash_note}", rid


def _ask_registry_vs_vendor(ticker, ex_date, why, rid):
    """CÙNG (mã, ex) với record registry (mọi provenance) nhưng vendor lệch / record chưa áp dụng —
    hỏi 1 lần / record. Gọi tên Winston (quy ước 09-24: lệch nguồn vendor ⇒ Winston kiểm)."""
    _ask_once(["vendor-vs-registry", ticker, ex_date, rid, "ASKED"],
              f"corp-action-vendor-vs-registry-{ticker}-{ex_date}",
              {"question": f"[Winston] {ticker} ex {ex_date}: {why}. Registry KHÔNG bị ghi đè. Cần "
                           f"người đối chiếu nguồn thật; record {rid} sai ⇒ {ONE_RECORD_RULE}.",
               "assignee": "Winston", "ticker": ticker, "ex_date": ex_date, "record_id": rid,
               "urgency": "high"})


def _ask_vendor_only(ticker, ex_date, shown, code, date_str, holders, ledger_note):
    """Vendor có sự kiện CP sắp ex cho mã đang giữ, sổ broker không có mục — 1 lần / (mã, ex).
    Chỉ nói điều ĐÃ đọc (§29): sổ broker không có mục cho mã phiên này — KHÔNG khẳng định 'DNSE
    không credit' (nhánh broker có thể chưa chạy/nổ, hoặc credit sau 19:25). `shown` = hệ số vendor
    ('×1.15') hoặc 'KHÔNG khai tỉ lệ' (m6 r4). Được `_resolve_asks` trả lời khi giải quyết (m4 r4)."""
    _ask_once(["vendor-only", ticker, ex_date, "ASKED"], f"corp-action-vendor-only-{ticker}-{ex_date}",
              {"question": (f"{ticker}: lịch vendor có {code} {shown} ex {ex_date} cho mã đang giữ "
                            f"({', '.join(holders)}) nhưng {ledger_note} và không có mục nào cho mã ở "
                            f"phiên {date_str} (nhánh broker chưa thấy ứng viên credit lúc chạy). Broker "
                            f"là nguồn chính ⇒ KHÔNG tự ghi. Kiểm DNSE sau 21:00 / xác nhận tay; nếu "
                            f"vendor sai ⇒ Winston."),
               "ticker": ticker, "vendor_ex_date": ex_date, "vendor_qty_multiplier": shown,
               "vendor_event_code": code, "credit_day": date_str, "holders": holders,
               "urgency": "normal"})


def _ask_vendor_held_unknown(ticker, ex_date, shown, code, date_str, why_u):
    """Không xác định được mã có đang giữ (không file / tài khoản positions rỗng / file cũ) — hỏi 1 lần
    / (mã, ex) (RC2, M3 r3). `why_u` = điều ĐÃ đọc (§29). Được `_resolve_asks` trả lời khi giải quyết."""
    _ask_once(["vendor-held-unknown", ticker, ex_date, "ASKED"],
              f"corp-action-vendor-held-unknown-{ticker}-{ex_date}",
              {"question": (f"{ticker}: lịch vendor có {code} {shown} ex {ex_date} nhưng {why_u} ⇒ không "
                            f"xác định được có đang giữ mã — INSUFFICIENT, KHÔNG tự ghi. Kiểm pipeline "
                            f"positions (phiên {date_str}) rồi xác nhận tay."),
               "ticker": ticker, "vendor_ex_date": ex_date, "verdict": BD.INSUFFICIENT,
               "credit_day": date_str, "urgency": "normal"})


def _ask_vendor_conflict(ticker, ex_date, evs, existing):
    """m7 r4: ≥2 sự kiện CP vendor KHÁC nhau cùng (mã, ex) — 1 lần / (mã, ex). Chỉ mã này bị chặn."""
    act = (f"registry đã có record {existing} cho mã quanh ex này ⇒ {ONE_RECORD_RULE}" if existing else
           "người ghi ĐÚNG MỘT record theo số thật (hệ số tổng nếu là nhiều sự kiện thật)")
    _ask_once(["vendor-conflict", ticker, ex_date, "ASKED"], f"corp-action-vendor-conflict-{ticker}-{ex_date}",
              {"question": (f"[Winston] {ticker} ex {ex_date}: lịch vendor có {len(evs)} sự kiện CP KHÁC NHAU cùng "
                            f"(mã, ex) {[BD._vsum(e) for e in evs]} — không biết là nhiều sự kiện thật (cộng dồn hệ "
                            f"số) hay feed ghi trùng sai. KHÔNG tự ghi mã này (mã khác trong lô vẫn chạy). "
                            f"Winston kiểm nguồn; {act}."),
               "assignee": "Winston", "ticker": ticker, "ex_date": ex_date,
               "vendor_events": [BD._vsum(e) for e in evs], "registry_record_id": existing,
               "urgency": "high"})


def _ask_vendor_cash_leg(ticker, ex_date, mult, why, existing):
    """Writer vendor (shadow/off): sự kiện CP khớp broker nhưng có dấu hiệu chân tiền cùng ex — 1 lần / (mã, ex).
    `existing` = id record registry SAU LÔ cùng (mã, ex)/near-dup (MAJOR-1 r5: có thể là record CHÍNH LÔ này vừa
    ghi cho ex kề) ⇒ chỉ đề nghị SỬA/THU HỒI nó (I2); None ⇒ đề nghị ghi 1 record. Không ai tự trả lời câu này
    (minor-3 r5): người ghi record chân tiền đóng nó."""
    act = (f"registry (kể cả lô vừa ghi) ĐÃ có record {existing} cho mã quanh ex này ⇒ {ONE_RECORD_RULE}; chân "
           f"tiền đúng phải SỬA vào chính record đó" if existing else
           "Người ghi 1 record CÓ cash_leg_vnd_per_share đúng (registry sau lô này chưa có record cho mã quanh ex này)")
    _ask_once(["vendor-cash-leg", ticker, ex_date, "ASKED"], f"corp-action-vendor-cash-leg-{ticker}-{ex_date}",
              {"question": (f"{ticker} ex {ex_date}: vendor ×{mult:.7g} và KL broker khớp, nhưng {why}. Writer vendor "
                            f"chỉ ghi hệ số KL — record thiếu chân tiền ⇒ park_holdings/exdate_frame đọc 0 ⇒ cổng giá "
                            f"đêm FAIL ⇒ KHÔNG tự ghi. {act}."),
               "ticker": ticker, "ex_date": ex_date, "vendor_qty_multiplier": mult, "why": why,
               "registry_record_id": existing, "urgency": "high"})


# ── Nhánh BROKER ───────────────────────────────────────────────────────────

BROKER_MODES = ("off", "shadow", "live")
BUS_TIMEOUT_S = 60
_LOCK_HELD = False        # run() đã giữ khoá ⇒ run_broker không xin lại (flock 2 fd cùng tiến trình = tự khoá)
# Gốc PRODUCTION tính ĐỘC LẬP với các biến module selfcheck hay đổi (LEDGER_FILE/EXEC_DIR/
# BD.LEDGER_FILE) — guard sandbox so với cái này (arch-review v2 N4).
_PROD_DATA = os.path.realpath(os.path.join(WC_ROOT, "data"))
BROKER_VENDOR_MULT_TOL = BD.VENDOR_MULT_TOL_PCT   # vendor vs record broker CÙNG ex: lệch >1% ⇒ hỏi (quy ước 09-24)
NEAR_DUP_DAYS = 10        # record CÙNG MÃ có ex_date cách credit_day ≤ N ngày lịch ⇒ không ghi, hỏi
LOCK_WAIT_S = 120
FEED_DEAD_TAG = "VENDOR_FEED_DEAD: vendor feed chết, broker là nguồn xác định"
DAYMARK_STALE_S = 300     # marker rỗng (claim) cũ hơn N giây = tiến trình đã bị kill trước khi gửi bus
DAYMARK_KEEP_DAYS = 30    # dọn marker `.{tag}-<ngày>` cũ hơn N ngày (chỉ marker, KHÔNG đụng sổ)
DAYMARK_TAGS = ("lockfail", "vendorcrash", "brokercrash")


def broker_mode():
    """`MIKE_CA_BROKER_SOURCE` — giá trị lạ ⇒ shadow (không bao giờ tự lên `live` do gõ nhầm)."""
    raw = os.environ.get("MIKE_CA_BROKER_SOURCE", "shadow").strip().lower()
    if raw not in BROKER_MODES:
        print(f"  ⚠ MIKE_CA_BROKER_SOURCE={raw!r} không hợp lệ {BROKER_MODES} ⇒ dùng 'shadow'")
        return "shadow"
    return raw


def _vendor_events_fn(date_str):
    """ticker → MỌI sự kiện của mã trong `upcoming_events_held` lịch vendor ngày `date_str`.
    Feed đứng vẫn ra file (feed_status STALE, ca TPB 10-01) ⇒ đọc bình thường.
    Không có file thường:
      · `_FAILED.json` đọc được với failed_gate=feed_dead (feed vendor CHẾT >5 ngày) ⇒ lịch vendor
        coi là RỖNG + hàm trả có thuộc tính `feed_dead=True` (caller gắn cờ VENDOR_FEED_DEAD vào
        sổ/log): đúng ý user 10-01 "vendor feed đứng thì broker là nguồn xác định" (r5 M-A, user
        chốt phương án A; vòng 4 #5 đã gộp ca này vào UNREADABLE ⇒ shadow chỉ ra AMBIGUOUS).
      · THIẾU file hoàn toàn / `_FAILED` gate KHÁC feed_dead (vd selfcheck) / file hỏng ⇒
        VENDOR_UNREADABLE + in lý do thật (§29) — KHÔNG coi là "vendor không có sự kiện" (status
        UNREADABLE ≠ NO_EVENT), nhưng từ broker-primary (2026-10-03) cũng KHÔNG chặn broker."""
    path = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{date_str}.json")
    if not os.path.exists(path):
        failed = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{date_str}_FAILED.json")
        if os.path.exists(failed):
            try:
                with open(failed, encoding="utf-8") as f:
                    gate = json.load(f).get("failed_gate")
            except (OSError, json.JSONDecodeError, AttributeError) as e:
                print(f"  ❌ lịch vendor {os.path.basename(failed)} đọc hỏng: {type(e).__name__}: {e}"
                      f" ⇒ VENDOR_UNREADABLE: không đối chiếu được — broker vẫn là nguồn chính, ghi 'chưa được vendor xác nhận'")
                return lambda tk: BD.VENDOR_UNREADABLE
            if gate == "feed_dead":
                print(f"  ⚠ VENDOR_FEED_DEAD: {os.path.basename(failed)} failed_gate=feed_dead ⇒ "
                      f"vendor feed chết, broker là nguồn xác định (lịch vendor coi là rỗng)")

                def dead(tk):
                    return []
                dead.feed_dead = True
                return dead
            why = f"chỉ có {os.path.basename(failed)} với failed_gate={gate!r} (không phải feed_dead)"
        else:
            why = "không có file"
        print(f"  ❌ lịch vendor {path}: {why} ⇒ VENDOR_UNREADABLE: không đối chiếu được — broker vẫn là "
          f"nguồn chính, ghi 'chưa được vendor xác nhận'")
        return lambda tk: BD.VENDOR_UNREADABLE
    try:
        with open(path, encoding="utf-8") as f:
            held = json.load(f).get("upcoming_events_held") or []
    except (OSError, json.JSONDecodeError, AttributeError) as e:
        print(f"  ❌ lịch vendor {path} đọc hỏng: {type(e).__name__}: {e} ⇒ VENDOR_UNREADABLE: không đối "
              f"chiếu được — broker vẫn là nguồn chính")
        return lambda tk: BD.VENDOR_UNREADABLE
    return lambda tk: [e for e in held if _norm_ticker(e.get("ticker")) == _norm_ticker(tk)]


def _exchange_fn():
    """ticker → sàn THẬT qua DNSE `marketId` (STO/STX/UPX). Không xác định được ⇒ None ⇒ detector
    MƠ HỒ (fail-closed; không mặc định HOSE như `Quote.exchange`).

    PHẢI `connect()` (arch-review v4 #1): `get_quote_source()` trả nguồn client=None; `get_quote`
    khi chưa connect nuốt AttributeError của từng lời gọi API ⇒ Quote rỗng ⇒ exchange_known=False
    ⇒ MỌI ứng viên MƠ HỒ (TPB 10-01 thật). Connect 1 lần/lượt như `bot_execute.py --probe` /
    `opening_window_l2_poll.py`; lỗi ⇒ None cho mọi mã. `_raw_log=None`: script này chỉ ĐỌC
    dnse_raw — không ghi quote_unmapped/quote_l2 vào file kế toán production (kể cả --dry-run)."""
    cache, src = {}, []

    def _source():
        if not src:
            try:
                from trading_bot.brokers import get_quote_source
                s = get_quote_source("dnse")
                s._raw_log = None
                s.connect()
                src.append(s)
            except Exception as e:  # §29: nói lỗi thật
                print(f"  không kết nối được nguồn quote DNSE: {type(e).__name__}: {e} ⇒ sàn None")
                src.append(None)
        return src[0]

    def fn(tk):
        if tk not in cache:
            s = _source()
            if s is None:
                cache[tk] = None
                return None
            try:
                q = s.get_quote(tk)
                cache[tk] = q.exchange if getattr(q, "exchange_known", False) else None
            except Exception as e:  # §29: nói lỗi thật
                print(f"  [{tk}] không xác định được sàn qua DNSE: {type(e).__name__}: {e}")
                cache[tk] = None
        return cache[tk]
    return fn


def _px_cum_fn(date_str):
    """Giá đóng cửa CÒN QUYỀN của phiên credit. Hôm nay ⇒ DNSE G1 (§6, BẮT BUỘC nguồn
    'dnse_g1_today' — giá phiên khác là sai hệ); ngày quá khứ ⇒ BQ `Price` chưa điều chỉnh.
    Lỗi/thiếu ⇒ None ⇒ detector trả INSUFFICIENT, KHÔNG đoán. `fn.prefetch(tickers, day, over)` —
    ngày quá khứ: MỘT truy vấn BQ cho cả lô; hôm nay: `dnse_close_prices` vốn gọi DNSE TUẦN TỰ từng
    mã (mỗi mã ≤3 endpoint, có timeout riêng) ⇒ gọi TỪNG mã và hỏi `over()` TRƯỚC mỗi lời gọi
    (m2 r3: ngân sách kiểm 1 lần trước lô không chặn được N×timeout). Hết ngân sách ⇒ dừng, mã chưa
    gọi không vào cache (caller xếp vào dòng 'hết ngân sách')."""
    cache = {}

    def prefetch(tickers, day, over=None):
        try:
            if day == today_ict():
                from verify_account_snapshot import dnse_close_prices
                for t in tickers:
                    if over is not None and over():
                        print(f"  hết ngân sách sàng lọc chỉ-giá trước khi gọi giá DNSE cho {t} ⇒ dừng prefetch")
                        break
                    px, src = dnse_close_prices([t], with_source=True)
                    ok = src.get(t) == "dnse_g1_today"
                    if not ok:
                        print(f"  [{t}] giá DNSE nguồn {src.get(t)!r} ≠ dnse_g1_today ⇒ không dùng")
                    cache[(t, day)] = px.get(t) if ok else None
            else:
                got = BD.bq_unadjusted_close({(t, day) for t in tickers})
                for t in tickers:
                    cache[(t, day)] = got.get((t, day))
        except Exception as e:  # §29: lỗi thật; mã chưa có trong cache sẽ thử lẻ ở fn()
            print(f"  không lấy được giá cum lô {len(tickers)} mã {day}: {type(e).__name__}: {e}")

    def fn(ticker, day):
        if (ticker, day) in cache:
            return cache[(ticker, day)]
        try:
            if day == today_ict():
                from verify_account_snapshot import dnse_close_prices
                px, src = dnse_close_prices([ticker], with_source=True)
                if src.get(ticker) != "dnse_g1_today":
                    print(f"  [{ticker}] giá DNSE nguồn {src.get(ticker)!r} ≠ dnse_g1_today ⇒ không dùng")
                    return None
                return px.get(ticker)
            return BD.bq_unadjusted_close({(ticker, day)}).get((ticker, day))
        except Exception as e:  # mạng/bq lỗi ⇒ INSUFFICIENT, nói rõ lỗi thật (§29)
            print(f"  [{ticker}] không lấy được giá cum {day}: {type(e).__name__}: {e}")
            return None
    fn.prefetch = prefetch
    return fn


def _bus(kind, topic, payload):
    """rc của append_event.sh (0 = bus đã nhận). rc≠0 ⇒ in lỗi THẬT, caller KHÔNG đánh dấu done.
    Hàm DUY NHẤT gọi append_event (MAJOR-1 r4) — dry-run ⇒ in điều lẽ ra gửi, trả 0 (đường code đi tiếp như
    đã gửi để người đọc thấy trọn lượt; mọi tác dụng kế tiếp — sổ/registry/marker — cũng bị cổng chặn)."""
    import subprocess
    if _effects_blocked(f"gửi bus {kind} {topic}: "
                        f"{payload.get('question') or payload.get('resolution') or payload.get('status') or ''}"):
        return 0
    try:
        r = subprocess.run([APPEND_EVENT, "Mike", kind, topic,
                            json.dumps(payload, ensure_ascii=False, default=str)],
                           capture_output=True, text=True, timeout=BUS_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        print(f"  ❌ append_event {kind} {topic} treo > {BUS_TIMEOUT_S}s — coi như CHƯA gửi")
        return 124
    if r.returncode != 0:
        print(f"  ❌ append_event {kind} {topic} rc={r.returncode}: "
              f"{(r.stderr or r.stdout or '').strip()[:300]}")
    return r.returncode


def _lock(path):
    """Khoá loại trừ (fcntl) quanh đọc-sửa-ghi sổ + registry của nhánh broker — cron và chạy tay
    đồng thời không đè nhau. Không lấy được trong LOCK_WAIT_S ⇒ None (caller rc=1, không ghi)."""
    import fcntl
    import time
    fh = open(path + ".lock", "a")
    t0 = time.monotonic()
    while True:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fh
        except BlockingIOError:
            if time.monotonic() - t0 > LOCK_WAIT_S:
                fh.close()
                return None
            time.sleep(1)


def _near_duplicate(rows, tk, ex, credit_day=None):
    """Record registry (MỌI provenance; mọi trạng thái TRỪ REVOKED) cùng mã, ex ≠ `ex` nhưng cách `ex` HOẶC
    `credit_day` ≤ NEAR_DUP_DAYS ngày lịch ⇒ rất có thể CÙNG sự kiện được ghi với ex khác (lịch thiếu ngày
    nghỉ…) — ghi thêm = áp hệ số 2 lần. PROPOSED/UNVERIFIED… tính (người ký là thành HIỆU LỰC ⇒ 2 record);
    REVOKED không tính: chỉ người sửa tay mới làm nó hiệu lực lại, khoá vì nó = chặn tự xác nhận mãi (quy ước
    arch-review v4). m8 r4: neo theo ex (bản r3 chỉ neo credit_day) + mọi provenance cho CẢ writer vendor.
    `rows` = `_reg_rows` (khoá từ CA.validate — MAJOR-2). Trả (lý do, id record) — id để câu hỏi chỉ đúng
    record cần SỬA/THU HỒI (I2) — hoặc None."""
    anchors = [dt.date.fromisoformat(x) for x in (ex, credit_day) if x]
    for w in rows:
        if (w["ticker"] != tk or w["ex"] == ex
                or str(w["rec"].get("_status", "")).strip().upper().startswith("REVOKED")):
            continue
        try:
            rex = dt.date.fromisoformat(w["ex"])
        except ValueError:
            return (f"record {w['id']!r} cùng mã có ex_date không đọc được {w['rec'].get('ex_date')!r}", w["id"])
        gap = min(abs((rex - d).days) for d in anchors)
        if gap <= NEAR_DUP_DAYS:
            return (f"registry đã có {w['id']!r} ({w['rec'].get('provenance') or 'người ký/vendor cũ'}, "
                    f"{str(w['rec'].get('_status', ''))[:30]!r}) ex {rex} cách ex {ex}"
                    + (f"/phiên credit {credit_day}" if credit_day else "")
                    + f" ≤ {NEAR_DUP_DAYS} ngày — có thể CÙNG sự kiện với ex khác ⇒ không ghi thêm (×hệ số 2 lần)",
                    w["id"])
    return None


class SandboxMismatch(RuntimeError):
    """Sổ PRODUCTION + dữ liệu sandbox — KHÔNG bao giờ bị nuốt (kể cả bởi _ask_guarded)."""


def _sandbox_guard():
    """Sổ là PRODUCTION mà dữ liệu vào/registry KHÔNG ⇒ đúng lớp lỗi B2 (selfcheck quên đổi
    LEDGER_FILE ghi rác vào sổ thật). Gọi TRƯỚC khi tạo bất kỳ file nào (kể cả .lock)."""
    def _in_prod(p):
        return os.path.realpath(p).startswith(_PROD_DATA + os.sep)
    if _in_prod(LEDGER_FILE) and not (_in_prod(EXEC_DIR) and _in_prod(CORP_ACTIONS_FILE)):
        # Sandbox LỆCH: dữ liệu vào/registry là sandbox mà sổ là PRODUCTION ⇒ đúng lớp lỗi B2
        # (selfcheck quên đổi LEDGER_FILE ghi rác vào sổ thật). Từ chối thay vì ghi.
        raise SandboxMismatch(f"LEDGER_FILE={LEDGER_FILE} là sổ PRODUCTION nhưng EXEC_DIR={EXEC_DIR} / "
                           f"CORP_ACTIONS_FILE={CORP_ACTIONS_FILE} đã bị đổi (sandbox?) — từ chối ghi")


REG_MATCH, REG_MISMATCH = "MATCH", "MISMATCH"
ONE_RECORD_RULE = ("KHÔNG thêm record thứ hai cho cùng (mã, ex) — chỉ SỬA hoặc THU HỒI (REVOKED) record "
                   "hiện có, hoặc đóng câu hỏi (bất biến ≤1 record hiệu lực/(mã, ex))")


def _effective(rec):
    """Record HIỆU LỰC = _status CONFIRMED* (đúng bộ lọc `corp_actions.load_corp_actions`)."""
    return str(rec.get("_status", "")).upper().startswith("CONFIRMED")


def _effective_groups(actions):
    """{(mã, ex): [index]} của record HIỆU LỰC — khoá từ CA.validate (`_reg_rows`, MAJOR-2 r4)."""
    g = {}
    for w in _reg_rows(actions):
        if w["effective"]:
            g.setdefault((w["ticker"], w["ex"]), []).append(w["i"])
    return g


def _validate_for_write(actions, base):
    """Chốt ĐIỂM GHI (I1 r3): validate() từng record + bất biến ≤1 record HIỆU LỰC/(mã, ex). Nhóm ≥2
    mà `base` (registry trên đĩa trước lượt ghi) KHÔNG có y hệt (cùng tập id) ⇒ do lượt này tạo ⇒
    CorpActionError (thông điệp `corp_actions[i]` = index record vi phạm cuối, cùng dạng validate()) ⇒ 0 ghi.
    Nhóm ≥2 CÓ SẴN (người gõ) không chặn ghi mã khác — đối chiếu coi nó là LỆCH và hỏi riêng (m6). Khoá
    nhóm và id lấy từ OUTPUT CA.validate: 'TPB ' và 'TPB' là MỘT nhóm như consumer thấy (MAJOR-2 r4)."""
    for i, rec in enumerate(actions):
        CA.validate(rec, i)  # ném CorpActionError nếu hỏng — KHÔNG bắt ở đây, để caller quyết định
    bw, aw = _reg_rows(base), _reg_rows(actions)
    old = {k: sorted(bw[i]["id"] for i in v) for k, v in _effective_groups(base).items()}
    for k, idx in sorted(_effective_groups(actions).items()):
        ids = sorted(aw[i]["id"] for i in idx)
        if len(idx) > 1 and ids != old.get(k):
            raise CA.CorpActionError(
                f"corp_actions[{idx[-1]}] vi phạm bất biến ≤1 record HIỆU LỰC/(mã, ex): {k[0]} ex {k[1]} sẽ "
                f"có {len(idx)} record CONFIRMED {ids} ⇒ park_holdings áp hệ số {len(idx)} lần — từ chối ghi")


def _registry_view(actions):
    """{(mã, ex): record đại diện} cho ĐỐI CHIẾU — khoá từ CA.validate (MAJOR-2 r4). Record đại diện là bản
    sao record thô + `_v` (output validate: hệ số/chân tiền như consumer đọc) hoặc `_invalid` (lý do validate
    từ chối), `id` = id validate. Đúng 1 hiệu lực ⇒ nó; ≥2 ⇒ record giả mang `_dup_ids` (đối chiếu coi là
    LỆCH — m6); 0 hiệu lực ⇒ record cuối (chưa áp dụng: PROPOSED/REVOKED…)."""
    by = {}
    for w in _reg_rows(actions):
        rep = dict(w["rec"], id=w["id"], _v=w["v"], _invalid=w["invalid"])
        by.setdefault((w["ticker"], w["ex"]), []).append((w["effective"], rep))
    out = {}
    for k, rs in by.items():
        eff = [r for e, r in rs if e]
        if len(eff) > 1:
            ids = [str(r.get("id")) for r in eff]
            out[k] = {"id": "+".join(ids), "ticker": k[0], "ex_date": k[1], "_dup_ids": ids,
                      "_status": f"CONFIRMED ×{len(eff)} (TRÙNG — vi phạm ≤1 record hiệu lực)"}
        else:
            out[k] = eff[0] if eff else rs[-1][1]
    return out


def _dup_why(rec):
    ids = rec["_dup_ids"]
    return (f"registry có {len(ids)} record HIỆU LỰC cho ({rec['ticker']}, {rec['ex_date']}) {ids} ⇒ "
            f"park_holdings áp hệ số {len(ids)} lần")


def _registry_reconcile(rec, r):
    """PURE (RC1). Record registry CÙNG (mã, ex) — MỌI provenance, MỌI trạng thái — vs kết luận
    broker `r`. Trả {status MATCH|MISMATCH, why (nêu CẢ HAI số), record_id, record_status}.
      MISMATCH: ≥2 record hiệu lực (m6); record bị CA.validate() từ chối (consumer chặn cả file); record chưa
                CONFIRMED (PROPOSED/UNVERIFIED/REVOKED… — chưa áp dụng mà broker thấy sự kiện); broker
                CHỈ-GIÁ (KL không đổi) trong khi registry khai sự kiện KL; hệ số lệch >1%; chân tiền lệch
                chân tiền broker >1đ/cp.
      MATCH:    còn lại.
    Hệ số/chân tiền registry lấy từ `_v` = OUTPUT CA.validate — ĐÚNG như consumer đọc (vắng chân tiền = 0;
    M1 r3: bản r2 coi vắng là "không so" ⇒ MATCH im mà cổng giá đêm FAIL). r4: bỏ phép đọc số riêng (NaN/
    chuỗi) — validate() đã từ chối những record đó ⇒ nhánh `_invalid`.
    Broker chưa quyết (INSUFFICIENT/AMBIGUOUS) ⇒ không gọi hàm này (caller giữ verdict + hỏi)."""
    rid, st = str(rec.get("id")), str(rec.get("_status", ""))
    prov = rec.get("provenance") or "người ký/vendor cũ"
    base = {"record_id": rid, "record_status": st[:60], "record_provenance": prov}
    bm, bc = r.get("qty_multiplier"), float(r.get("cash_leg") or 0.0)
    if rec.get("_dup_ids"):
        return dict(base, status=REG_MISMATCH, why=_dup_why(rec))
    if rec.get("_invalid"):
        return dict(base, status=REG_MISMATCH,
                    why=(f"registry {rid!r} ({prov}) bị CA.validate() từ chối: {rec['_invalid']} — consumer "
                         f"(park_holdings/load_corp_actions) đang chặn CẢ registry; broker thấy "
                         f"{r.get('kind') or 'SHARE_EVENT'} ×{bm or 1} chân tiền {bc:,.0f}đ/cp"))
    if not st.upper().startswith(CA.CONFIRMED_PREFIX):
        return dict(base, status=REG_MISMATCH,
                    why=(f"registry có {rid!r} ({prov}) trạng thái {st[:40]!r} — CHƯA áp dụng, trong khi "
                         f"broker thấy {r.get('kind') or 'SHARE_EVENT'} ×{bm or 1} chân tiền {bc:,.0f}đ/cp"))
    rm, rcv = rec["_v"]["qty_multiplier"], rec["_v"]["cash_leg_vnd_per_share"]
    if not bm:
        return dict(base, status=REG_MISMATCH,
                    why=(f"registry {rid!r} ({prov}) khai sự kiện KL ×{rm:.7g} ex {rec.get('ex_date')} nhưng "
                         f"broker KL KHÔNG đổi ({r.get('kind')}, chân tiền {bc:,.0f}đ/cp)"))
    if abs(rm - bm) > BROKER_VENDOR_MULT_TOL * bm:
        return dict(base, status=REG_MISMATCH,
                    why=f"broker ×{bm} vs registry {rid!r} ({prov}) ×{rm:.7g} (lệch {abs(rm - bm) / bm:.2%} > 1%)")
    absent = rec.get("cash_leg_vnd_per_share") is None
    shown = f"KHÔNG khai (consumer đọc {rcv:,.0f})" if absent else f"{rcv:,.0f}"
    if abs(rcv - bc) > BD.VENDOR_CASH_TOL_VND:
        return dict(base, status=REG_MISMATCH,
                    why=(f"chân tiền: broker {bc:,.0f}đ/cp vs registry {rid!r} ({prov}) {shown}đ/cp — "
                         f"park_holdings/exdate_frame sẽ dựng giá tham chiếu với chân tiền SAI ⇒ cổng giá đêm FAIL"))
    note = f"chân tiền broker {bc:,.0f} = registry {rcv:,.0f}đ/cp" + (" (không khai = 0)" if absent else "")
    return dict(base, status=REG_MATCH, why=f"broker ×{bm} = registry {rid!r} ({prov}) ×{rm:.7g}; {note}")


def _ask_vendor_near_record(ticker, ex_date, why, rid):
    """Vendor ex ≠ ex record registry (MỌI provenance — m2/m8 r4; bản cũ chỉ record broker) cùng mã ở gần đó.
    Khoá hỏi có id record (arch-review v4 #9): người REVOKE record cũ rồi có record MỚI ⇒ hỏi lại."""
    _ask_once(["vendor-near-record", ticker, ex_date, rid, "ASKED"],
              f"corp-action-vendor-near-record-{ticker}-{ex_date}",
              {"question": f"{ticker}: lịch vendor ex {ex_date} nhưng {why}. Cần người xác "
                           f"nhận ex thật; record {rid} sai ex ⇒ {ONE_RECORD_RULE}.",
               "ticker": ticker, "vendor_ex_date": ex_date, "registry_record_id": rid,
               "urgency": "high"})


def _prune_daymarks():
    """Marker ngày cũ hơn DAYMARK_KEEP_DAYS ngày thì xoá — chỉ marker `.{tag}-<ngày>` cạnh sổ."""
    import glob
    import time
    for tag in DAYMARK_TAGS:
        for p in glob.glob(f"{LEDGER_FILE}.{tag}-*"):
            try:
                if time.time() - os.stat(p).st_mtime > DAYMARK_KEEP_DAYS * 86400:
                    os.remove(p)
            except OSError:
                pass


def _ask_day_once(tag, date_str, topic, payload):
    """Bus `question` 1 lần/ngày/`tag` (ops_health_check leo thang question, KHÔNG leo thang `error`
    — arch-review v4 #3). Marker `{LEDGER_FILE}.{tag}-{date_str}` tạo nguyên tử O_EXCL (không cần
    khoá — có thể chính khoá đang bị giữ) như CLAIM RỖNG; chỉ khi bus rc=0 mới ghi nội dung
    "sent" (r5 M-D: bản cũ coi marker là đã báo ngay lúc tạo ⇒ kill giữa tạo marker và gửi bus làm
    ngày đó im vĩnh viễn). Bus lỗi/ném ⇒ xoá marker, lượt sau hỏi lại. Claim rỗng cũ hơn
    DAYMARK_STALE_S giây ⇒ tiến trình chủ đã chết, chiếm lại. r4: qua cổng dry-run TRƯỚC mọi file (marker,
    dọn marker cũ) và bus."""
    import time
    if _effects_blocked(f"hỏi 1 lần/ngày ({tag}) bus question {topic}: {payload.get('question', '')}"):
        return
    _prune_daymarks()
    marker = f"{LEDGER_FILE}.{tag}-{date_str}"
    fd = None
    for _ in range(3):
        try:
            fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                st = os.stat(marker)
            except FileNotFoundError:
                continue
            if st.st_size > 0 or time.time() - st.st_mtime <= DAYMARK_STALE_S:
                print(f"  đã hỏi người ({tag}) ngày {date_str} (hoặc tiến trình khác đang gửi) ⇒ không hỏi lại")
                return
            print(f"  claim {os.path.basename(marker)} rỗng quá {DAYMARK_STALE_S}s ⇒ tiến trình trước "
                  f"chết giữa claim và bus, chiếm lại")
            try:
                os.remove(marker)
            except FileNotFoundError:
                pass
    if fd is None:
        print(f"  ❌ không chiếm được marker {marker} sau 3 lần — bỏ qua lượt hỏi này")
        return
    try:
        rc = _bus("question", topic, payload)
    except Exception as e:  # §29
        print(f"  ❌ không gửi được bus question {topic}: {type(e).__name__}: {e}")
        rc = 1
    try:
        if rc == 0:
            os.write(fd, b"sent\n")
    finally:
        os.close(fd)
    if rc != 0:
        os.remove(marker)


def _ask_lock_unavailable(date_str, mode):
    """Không lấy được khoá ⇒ CẢ nhánh vendor lẫn broker không chạy (urgency high, 1 lần/ngày)."""
    _ask_day_once("lockfail", date_str, f"corp-action-lock-unavailable-{date_str}",
                  {"question": (f"Không lấy được khoá {LEDGER_FILE}.lock sau {LOCK_WAIT_S}s — nhánh "
                                f"vendor VÀ broker đều KHÔNG chạy lượt {date_str}. Kiểm tiến trình "
                                f"corp_action_auto_confirm đang treo rồi chạy lại tay --date {date_str}."),
                   "mode": mode, "urgency": "high"})


def _ask_once(key, topic, payload):
    """Hỏi người MỘT lần cho mỗi `key` (xem `_notify_once`)."""
    _notify_once("question", key, topic, payload)


def _notify_once(kind, key, topic, payload):
    """Gửi bus `kind` MỘT lần cho mỗi `key`: bus rc=0 ⇒ ghi dòng `done` vào sổ ⇒ lượt sau im. Bus
    lỗi ⇒ không đánh dấu (lượt sau gửi lại). Sổ đọc hỏng ⇒ vẫn gửi (an toàn), nói lỗi thật.
    Trả True khi đã gửi được hoặc đã gửi từ trước."""
    from zoneinfo import ZoneInfo
    ticker = key[1]
    _sandbox_guard()
    try:
        _intents, done = BD.ledger_state(LEDGER_FILE)
    except BD.CorpActionLedgerError as e:       # sổ hỏng ⇒ vẫn hỏi (an toàn), nói lỗi thật (§29)
        print(f"  ⚠ sổ broker đọc hỏng ({e}) ⇒ không kiểm được đã hỏi chưa, hỏi lại")
        done = set()
    if tuple(key) in done:
        print(f"  [{ticker}] đã gửi {kind} {key} ⇒ không gửi lại")
        return True
    rc = _bus(kind, topic, payload)
    if rc == 0:
        now_ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%dT%H:%M:%S+07:00")
        _ledger_append([{"kind": "done", "key": key, "at": now_ict}])
    return rc == 0


_OPEN_VERDICTS = (BD.INSUFFICIENT, BD.AMBIGUOUS, BD.DEFER_VENDOR, BD.UNVERIFIED)


def _close_resolved(tk, day, intents, done, regc, meta=None, answer=True):
    """§26 (m7 r3 + m4 r4): mã ở phiên `day` (live) đã được giải quyết — registry KHỚP broker (`regc` từ
    `_registry_reconcile`) HOẶC nhánh broker vừa ghi CONFIRMED (regc = {record_id, why}) — ⇒ câu hỏi cũ cùng
    mã/phiên (INSUFFICIENT/AMBIGUOUS/DEFER/UNVERIFIED) hết lý do mở:
      · đã GỬI (có `done` không phải superseded/observation) ⇒ `answer` đúng topic, 1 lần/khoá (sổ done), kèm
        bằng chứng record id — chỉ khi `answer`;
      · chưa gửi (việc dở lượt trước) ⇒ trả khoá để caller BỎ gửi bù + ghi done 'superseded'.
    Lỗi gửi chỉ in (câu hỏi vẫn mở = an toàn). Trả set khoá superseded."""
    sup = set()
    for k, old in intents.items():
        if (old.get("mode") != "live" or _norm_ticker(old.get("ticker")) != tk or old.get("credit_day") != day
                or old.get("verdict") not in _OPEN_VERDICTS or old.get("observation_only")):
            continue
        if k not in done:
            sup.add(k)
            continue
        m = (meta or {}).get(k) or {}
        if not answer or m.get("superseded") or m.get("observation_only"):
            continue          # không có câu hỏi nào trên bus để trả lời
        _notify_once("answer", ["closed", tk, day, old["verdict"], str(regc.get("record_id")), "|".join(map(str, k))],
                     f"corp-action-broker-{old['verdict'].lower()}-{tk}-{day}",
                     {"resolution": (f"lượt sau: {regc.get('why')} (record {regc.get('record_id')}) "
                                     f"⇒ câu hỏi {old['verdict']} đã giải quyết"),
                      "evidence": f"data/corp_actions.json id={regc.get('record_id')}", "decided_by": "agent"})
    return sup


# minor-3 r5: KHÔNG có "vendor-cash-leg" — câu đó chỉ phát ở writer vendor (off/shadow) mà resolver chỉ chạy ở live
# (off thậm chí không chạy `_registry_sweep`) ⇒ nhánh trả lời nó là code chết; người ghi record chân tiền đóng nó.
_RESOLVE_BY_REGISTRY = ("vendor-only", "vendor-held-unknown", "vendor-conflict")


def _resolve_asks(view, intents, done):
    """m4 r4 (§26): câu hỏi ĐÃ gửi (khoá `[loại, mã, ex, …, 'ASKED']` trong sổ done) mà nay hết lý do mở ⇒
    `answer` đúng topic, 1 lần/khoá, kèm bằng chứng ĐÃ đọc:
      vendor-only / vendor-held-unknown (mã, ex): registry có record HIỆU LỰC (mã, ex) [id], HOẶC sổ broker
        LIVE có mục (mã, ex) [verdict — câu hỏi riêng của nhánh broker theo dõi tiếp];
      vendor-conflict (mã, ex): registry có record HIỆU LỰC (mã, ex) [id];
      credit-overdue (mã, ex, id): sổ broker có mục (mã, ex) ở mode bất kỳ [credit đã thấy], HOẶC id không còn
        là record hiệu lực duy nhất của (mã, ex) [đã sửa/thu hồi].
    Chưa giải quyết ⇒ im (câu hỏi vẫn mở). Trả rc (1 nếu có answer gửi lỗi — lượt sau thử lại)."""
    rc = 0
    for k in sorted(done, key=str):
        if len(k) < 4 or k[-1] != "ASKED" or k[0] not in _RESOLVE_BY_REGISTRY + ("credit-overdue",):
            continue
        ck = ("closed",) + tuple(k[:-1])
        if ck in done:
            continue
        kind, tk, ex = k[0], k[1], k[2]
        rec = view.get((tk, ex))
        eff = (rec is not None and _effective(rec) and not rec.get("_dup_ids") and not rec.get("_invalid"))
        seen = sorted({f"{e.get('mode')}:{e.get('verdict')}" for e in intents.values()
                       if _norm_ticker(e.get("ticker")) == tk and e.get("ex_date") == ex
                       and (kind == "credit-overdue" or e.get("mode") == "live")})
        why = None
        if kind == "credit-overdue":
            if seen:
                why = f"sổ broker đã có mục ({tk}, {ex}): {seen} — credit đã được quan sát"
            elif not (eff and str(rec.get("id")) == k[3]):
                why = (f"record {k[3]} không còn là record hiệu lực duy nhất của ({tk}, {ex}) — registry hiện: "
                       f"{(str(rec.get('id')) + ' ' + str(rec.get('_status', ''))[:30]) if rec else 'không có record'}")
        elif eff:
            why = f"registry có record HIỆU LỰC {rec.get('id')} cho ({tk}, {ex})"
        elif seen and kind in ("vendor-only", "vendor-held-unknown"):
            why = (f"nhánh broker LIVE đã có mục sổ ({tk}, {ex}): {seen} — theo dõi tiếp ở câu hỏi/finding của "
                   f"nhánh broker")
        if why is None:
            continue
        ok = _notify_once("answer", list(ck), f"corp-action-{kind}-{tk}-{ex}",
                          {"resolution": f"{why} ⇒ câu hỏi {kind} ({tk}, ex {ex}) đã giải quyết",
                           "evidence": why, "decided_by": "agent"})
        rc = rc or (0 if ok else 1)
    return rc


CREDIT_WATCH_SESSIONS = 1   # cảnh báo QUÁ HẠN khi ex ≤ hôm nay ≤ ex + N phiên mà sổ broker chưa thấy credit


def _credit_state(tk, ex, date_str, intents, seen_now=None, ledger_err=None):
    """Trạng thái credit broker cho record registry (mã, ex) — đọc sổ broker (mọi mode, kể cả dòng
    `observation_only` của nhánh registry-khớp) + `seen_now` {(mã, ex): verdict} của CHÍNH lượt này
    (dry-run không ghi sổ): 'ĐÃ THẤY …' / 'CHỜ CREDIT …' (ex sau hôm nay) / 'QUÁ HẠN …'. m1 r3.
    m6 r4 (§29): câu QUÁ HẠN nêu điều ĐÃ đọc (số mục sổ ở phiên credit, sổ đọc hỏng) + MỌI nguyên nhân chưa
    phân biệt được, không chỉ 2."""
    seen = sorted({str(e.get("verdict")) for e in intents.values()
                   if _norm_ticker(e.get("ticker")) == tk and e.get("ex_date") == ex}
                  | ({str((seen_now or {})[(tk, ex)])} if (tk, ex) in (seen_now or {}) else set()))
    if seen:
        return f"ĐÃ THẤY ở sổ broker / kết quả lượt này ({', '.join(seen)})"
    if ex > date_str:
        return (f"CHỜ CREDIT — sổ broker chưa có mục ({tk}, {ex}); DNSE thường credit tối phiên liền "
                f"trước ex (18:30–20:15)")
    cday = BD.prev_trading_day(ex)
    n = sum(1 for e in intents.values() if e.get("credit_day") == cday)
    read = (f"sổ broker ĐỌC HỎNG ({ledger_err}) — không biết nhánh broker đã thấy gì" if ledger_err else
            f"sổ broker có {n} mục phiên credit {cday} (mã khác)"
            + ("" if n else " — KHÔNG có mục nào phiên đó"))
    return (f"QUÁ HẠN — ex {ex} ≤ {date_str} mà sổ broker KHÔNG có mục ({tk}, {ex}) ở mode nào. Đã đọc: {read}. "
            f"Nguyên nhân có thể (dữ liệu hiện có chưa phân biệt được): (1) DNSE chưa credit; (2) DNSE credit SAU "
            f"lượt quét 19:25 phiên {cday} (lượt này không quét lại phiên trước); (3) nhánh broker không chạy / nổ / "
            f"thiếu bản ghi positions sau credit phiên {cday}; (4) record sai (không có sự kiện thật, hoặc ex sai)")


def _registry_sweep(date_str, mode, seen_now=None):
    """Phủ các ô registry KHÔNG đi qua detector (I5 r3):
      (a) m6/I1 — (mã, ex) có ≥2 record HIỆU LỰC ⇒ log; live ⇒ question high 1 lần/(mã, ex, ids);
      (b) m1 — record HIỆU LỰC (mọi provenance) có ex = phiên KẾ TIẾP (chờ credit tối nay) hoặc ex ≤ hôm
          nay ≤ ex + CREDIT_WATCH_SESSIONS phiên, mã đang giữ / KHÔNG xác định được: sổ broker không có
          mục nào ⇒ log 'CHỜ CREDIT'; quá hạn ⇒ live question 1 lần/(mã, ex, id). Mã chắc chắn không
          giữ ⇒ log. shadow ⇒ chỉ in. Không bao giờ ghi data/corp_actions.json. Trả rc.
      (c) m4 r4 — live: `_resolve_asks` trả lời câu hỏi vendor-only/held-unknown/conflict/QUÁ HẠN đã
          hết lý do mở.
    r4: dry-run KHÔNG còn cờ riêng ở đây — cổng `_effects_blocked` chặn (và in) mọi câu hỏi lẽ ra gửi."""
    from trading_bot.vn_market import next_trading_day
    quiet = mode != "live"
    view = _registry_view(load_corp_actions_raw())
    rc = 0
    for (tk, ex), rec in sorted(view.items()):
        if not rec.get("_dup_ids"):
            continue
        print(f"  [registry] ❌ {_dup_why(rec)}")
        if not quiet:
            ok = _notify_once("question", ["registry-dup", tk, ex, "+".join(rec["_dup_ids"]), "ASKED"],
                              f"corp-action-registry-dup-{tk}-{ex}",
                              {"question": (f"{_dup_why(rec)} — vi phạm bất biến ≤1 record hiệu lực/(mã, ex). "
                                            f"Giữ ĐÚNG MỘT record (sửa nó theo số thật), THU HỒI (REVOKED) các "
                                            f"record còn lại. Không lượt tự động nào sửa registry."),
                               "ticker": tk, "ex_date": ex, "record_ids": rec["_dup_ids"], "urgency": "high"})
            rc = rc or (0 if ok else 1)
    ledger_err = None
    try:
        intents, done = BD.ledger_state(LEDGER_FILE)
    except BD.CorpActionLedgerError as e:      # §29: sổ hỏng ⇒ không biết broker đã thấy gì ⇒ coi chưa thấy
        print(f"  ⚠ sổ broker đọc hỏng ({e}) ⇒ credit-watch coi như sổ broker chưa thấy mục nào")
        intents, done, ledger_err = {}, set(), str(e)
    if not quiet:
        rc = _resolve_asks(view, intents, done) or rc
    nxt = next_trading_day(dt.date.fromisoformat(date_str)).isoformat()

    def _in_window(ex):
        try:
            return ex == nxt or (ex <= date_str and _sessions_since(ex, date_str) <= CREDIT_WATCH_SESSIONS)
        except ValueError:      # ex hỏng ⇒ validate() của consumer đã chặn cả registry; không đoán ở đây
            print(f"  [credit-watch] ex_date không đọc được {ex!r} ⇒ bỏ qua (validate() báo ở consumer)")
            return False
    watch = [(k, r) for k, r in sorted(view.items())
             if _effective(r) and not r.get("_dup_ids") and not r.get("_invalid") and _in_window(k[1])]
    if not watch:
        return rc
    held, unknown = _held_info(date_str)
    if held is None:
        held, unknown = {}, [f"không có file dnse_raw nào trong {BD.HELD_LOOKBACK_DAYS} ngày"]
    for (tk, ex), rec in watch:
        rid = str(rec.get("id"))
        st = _credit_state(tk, ex, date_str, intents, seen_now, ledger_err)
        if not st.startswith("QUÁ HẠN") and not st.startswith("CHỜ"):
            print(f"  [credit-watch {rid}] {st}")
            continue
        if tk not in held and not unknown:
            print(f"  [credit-watch {rid}] {st} — nhưng MỌI tài khoản đã biết không giữ {tk} ⇒ không chờ credit")
            continue
        holders = held.get(tk) or [f"không xác định: {'; '.join(unknown)}"]
        print(f"  [credit-watch {rid}] ex {ex}: {st}; giữ: {holders}")
        if not st.startswith("QUÁ HẠN") or quiet:
            continue
        ok = _notify_once("question", ["credit-overdue", tk, ex, rid, "ASKED"],
                          f"corp-action-credit-overdue-{tk}-{ex}",
                          {"question": (f"{tk}: registry có record HIỆU LỰC {rid} ×{rec.get('qty_multiplier')} ex "
                                        f"{ex} (park_holdings đang áp) nhưng {st}. Tài khoản: {holders}. Kiểm KL "
                                        f"DNSE thật so với record; sai ⇒ {ONE_RECORD_RULE}."),
                           "ticker": tk, "ex_date": ex, "record_id": rid, "holders": holders,
                           "urgency": "high"})
        rc = rc or (0 if ok else 1)
    return rc


def _finish_live(e, registry_ids):
    """Gửi thông báo cho MỘT mục sổ ở live. Trả rc bus. Không khẳng định điều chưa kiểm (§29)."""
    tk, day, v = e["ticker"], e["credit_day"], e["verdict"]
    vc = e.get("vendor_check") or {}
    if v == BD.CONFIRMABLE:
        rid = e["record"]["id"]
        if rid in registry_ids:
            return _bus("finding", f"corp-action-broker-confirm-{tk}",
                        {"status": "AUTO_CONFIRMED_BROKER", "event_id": rid, "ticker": tk,
                         "ex_date": e["ex_date"], "qty_multiplier": e["qty_multiplier"],
                         "cash_leg_vnd_per_share": e["cash_leg"],
                         "vendor_check": vc.get("status"), "vendor_why": vc.get("why"),
                         "verified_by_vendor": vc.get("status") == BD.V_VERIFIED,
                         "evidence": e["record"]["evidence"], "decided_by": "agent",
                         "note": "provenance=broker (nguồn chính); vendor chỉ xác nhận chéo; thu hồi: _status REVOKED"})
        upd = e.get("registry_update_proposed")
        # m1 r4 (I2): registry nay ĐÃ có record KHÁC cho mã quanh ex ⇒ KHÔNG đưa record này như thứ để ghi
        return _bus("question", f"corp-action-broker-write-incomplete-{tk}-{day}",
                    {"question": (f"{tk}: nhánh broker đã quyết CONFIRMABLE ×{e['qty_multiplier']} "
                                  f"ex {e['ex_date']} nhưng load_corp_actions() KHÔNG thấy record "
                                  f"{rid} trong registry (ghi dở/bị kill/đọc lại hỏng). Cần người "
                                  f"kiểm data/corp_actions.json"
                                  + (f"; registry ĐÃ có record {upd['record_id']} cho mã quanh ex này ⇒ "
                                     f"{ONE_RECORD_RULE}." if upd else ".")),
                     "ticker": tk, "credit_day": day, "record": None if upd else e["record"],
                     "registry_update_proposed": upd, "urgency": "high"})
    if v == BD.CASH_DIVIDEND:
        return _bus("finding", f"corp-action-broker-cashdiv-{tk}-{day}",
                    {"status": "CASH_DIVIDEND_BROKER", "ticker": tk, "credit_day": day,
                     "ex_date": e["ex_date"], "cash_vnd_per_share": e["cash_leg"],
                     "vendor_check": vc.get("status"), "vendor_why": vc.get("why"),
                     "accounts": e["accounts"], "decided_by": "agent",
                     "note": ("giá vốn DNSE giảm đúng KL×tiền + cashDividendReceiving tăng khớp; KHÔNG ghi "
                              "data/corp_actions.json (sổ chỉ chứa sự kiện đổi KL)")})
    if v == BD.UNVERIFIED:
        rg = e.get("registry_check") or {}
        causes = []
        if rg.get("status") == REG_MISMATCH:
            causes.append(f"LỆCH REGISTRY: {rg.get('why')} (registry KHÔNG bị ghi đè)")
        if vc.get("status") == BD.V_MISMATCH or vc.get("qty_unconfirmed"):
            causes.append(f"{'LỆCH' if vc.get('status') == BD.V_MISMATCH else 'THIẾU trục KL ở'} lịch "
                          f"vendor: {vc.get('why')}")
        if not causes:      # §29: không khẳng định nguyên nhân chưa đọc — lý do nằm ở 'Chi tiết'
            causes.append("bị hạ UNVERIFIED (lý do ở 'Chi tiết')")
        upd = e.get("registry_update_proposed")
        # I2 r3 (M2): registry/near-dup ĐÃ có record ⇒ KHÔNG BAO GIỜ dặn ghi record thứ hai (record_proposed
        # id khác + record cũ CONFIRMED = áp hệ số 2 lần) — chỉ sửa/thu hồi record hiện có hoặc đóng.
        # m3 r4: dặn ghi record_proposed CHỈ khi câu hỏi THẬT SỰ mang nó — chỉ-giá (KL không đổi) không có
        # record nào để ghi (sổ chỉ chứa sự kiện đổi KL).
        act = (f"registry ĐÃ có record {upd['record_id']} cho mã quanh ex này ⇒ {ONE_RECORD_RULE}; số "
               f"broker để sửa record đó: {upd['broker']}" if upd else
               "người chốt: ghi record_proposed (đổi _status thành CONFIRMED, giữ số broker), hoặc bỏ"
               if e.get("record_proposed") else
               "sự kiện KHÔNG đổi KL ⇒ không có record nào để ghi data/corp_actions.json; Winston kiểm nguồn "
               "rồi đóng câu hỏi")
        return _bus("question", f"corp-action-broker-unverified-{tk}-{day}",
                    {"question": (f"[Winston] {tk} phiên {day}: broker DNSE (nguồn chính) kết luận "
                                  f"{e.get('event_kind')} ×{e.get('qty_multiplier') or 1} chân tiền "
                                  f"{e.get('cash_leg') or 0:,.0f}đ/cp ex {e['ex_date']} nhưng "
                                  f"{'; '.join(causes)}. Đã hạ UNVERIFIED — KHÔNG ghi registry, KHÔNG "
                                  f"lấy số nguồn khác đè. Winston kiểm nguồn; {act}. Chi tiết: {e['why']}"),
                     "assignee": "Winston", "ticker": tk, "credit_day": day, "ex_date": e["ex_date"],
                     "registry_check": rg or None,
                     "broker": {"qty_multiplier": e.get("qty_multiplier"), "cash_leg": e.get("cash_leg")},
                     "vendor_check": vc, "record_proposed": e.get("record_proposed"),
                     "registry_update_proposed": upd,
                     "accounts": e["accounts"], "urgency": "high"})
    urgency = "normal" if v == BD.INSUFFICIENT else "high"
    hint = {BD.INSUFFICIENT: "chưa đủ bản ghi/giá để quyết (cron 19:25 có thể chạy trước khi DNSE "
                             "credit xong mọi gói vay) — chạy lại tay sau 21:00 hoặc xác nhận tay",
            BD.DEFER_VENDOR: "lịch vendor có sự kiện cổ phiếu cho mã nhưng nhánh vendor KHÔNG xác "
                             "nhận (MISMATCH/không khớp ngày) — nhánh vendor không tự hỏi",
            BD.AMBIGUOUS: "không đủ điều kiện tự xác nhận (lý do cụ thể ở 'Chi tiết')"}.get(v, v)
    upd = e.get("registry_update_proposed")
    act = (f"registry ĐÃ có record {upd['record_id']} cho mã quanh ex này ⇒ {ONE_RECORD_RULE}" if upd else
           "Cần người xác nhận sự kiện + ex-date trước khi ghi data/corp_actions.json")
    return _bus("question", f"corp-action-broker-{v.lower()}-{tk}-{day}",
                {"question": (f"{tk} phiên {day}: nhánh broker ({e.get('event_kind') or 'SHARE_EVENT'}) "
                              f"trả {v} — {hint}. Chi tiết: {e['why']}. Lịch vendor (chỉ tham khảo, "
                              f"KHÔNG tự ghi): {vc.get('status', '-')} {vc.get('vendor') or ''}. {act}."),
                 "ticker": tk, "credit_day": day, "ex_date_if_event": e["ex_date"],
                 "event_kind": e.get("event_kind"), "vendor_check": vc,
                 "registry_update_proposed": upd,
                 "verdict": v, "accounts": e["accounts"], "urgency": urgency})


def _flag_feed_dead(results, vfn):
    """r5 M-A: cờ feed chết đi vào log + sổ + record + bus."""
    if not getattr(vfn, "feed_dead", False):
        return results
    return [dict(r, vendor_feed_dead=True, why=f"{FEED_DEAD_TAG}; {r['why']}",
                 vendor_check=(dict(r["vendor_check"], status=BD.V_FEED_DEAD,
                                    why=f"{FEED_DEAD_TAG} — chưa được vendor xác nhận")
                               if (r.get("vendor_check") or {}).get("status") == BD.V_NO_EVENT
                               else r.get("vendor_check")))
            for r in results]


def run_broker(date_str, dry_run=False, mode="shadow"):
    """Hai pha (RC4): (1) sự kiện ĐỔI KL — quét, ghi registry/sổ, thông báo; (2) SAU ĐÓ mới sàng
    lọc CHỈ-GIÁ (gọi DNSE cho cả danh mục) trong ngân sách thời gian TỔNG
    `BD.PRICE_SCREEN_BUDGET_S` — DNSE chậm không thể đẩy lần ghi registry qua park_trim 19:30;
    hết ngân sách ⇒ dòng báo thiếu dữ liệu, KHÔNG chặn ghi. (3) Re-verify record broker sau ex (RC3).
    (4) `_registry_sweep`. shadow ⇒ ĐÚNG 1 finding tóm tắt cho cả lượt (m9 r4: bản r3 phát 1 finding/pha)."""
    with _dry_scope(dry_run):
        return _run_broker(date_str, dry_run, mode)


def _run_broker(date_str, dry_run, mode):
    import time
    print(f"[corp_action_auto_confirm] NHÁNH BROKER mode={mode} date={date_str} dry_run={dry_run}")
    vfn = _vendor_events_fn(date_str)
    qty, ctx = BD.scan_qty(date_str, _px_cum_fn(date_str), vfn, exec_dir=EXEC_DIR,
                           exchange_fn=_exchange_fn())
    qty = _flag_feed_dead([r for r in qty if r["verdict"] != BD.NOT_CANDIDATE], vfn)

    def _price_phase():
        t0 = time.monotonic()
        po = BD.scan_price_only(ctx, deadline=t0 + BD.PRICE_SCREEN_BUDGET_S)
        print(f"  sàng lọc chỉ-giá: {time.monotonic() - t0:.1f}s / ngân sách {BD.PRICE_SCREEN_BUDGET_S}s")
        return _flag_feed_dead([r for r in po if r["verdict"] != BD.NOT_CANDIDATE], vfn)
    def _all():
        sh = [] if mode != "live" else None      # shadow: gom mục của CẢ 2 pha ⇒ 1 finding
        rc = _run_broker_locked(date_str, mode, qty, resend=True, phase="qty", shadow_out=sh)
        po = _price_phase()
        rc = _run_broker_locked(date_str, mode, po, resend=False, phase="price_only", shadow_out=sh) or rc
        if sh:
            rc = _shadow_finding(date_str, sh) or rc
        rc = _reverify_broker_records(date_str, mode) or rc
        if not dry_run:
            return _registry_sweep(date_str, mode) or rc
        for r in qty + po:
            print(f"  [DRY-RUN] {r['ticker']} ex {r['ex_date']} {r['verdict']} ×"
                  f"{r.get('qty_multiplier', '-')} vendor={(r.get('vendor_check') or {}).get('status', '-')}"
                  f": {r['why'][:300]}")
        # dry-run không ghi sổ ⇒ credit-watch đọc kết quả CHÍNH lượt này (seen_now) thay cho dòng sổ lẽ ra đã ghi
        return _registry_sweep(date_str, mode,
                               seen_now={(_norm_ticker(r["ticker"]), r["ex_date"]): r["verdict"] for r in qty + po}) or rc
    if dry_run:
        # minor-4 r5: dry-run đi CÙNG đường quyết định (near-dup / I2 / lô / validate) với lượt thật — bản r4 có
        # đường in riêng ⇒ in "CONFIRMABLE" trong khi lượt thật hỏi broker-ambiguous. Mọi tác dụng qua cổng
        # `_effects_blocked`; KHÔNG khoá (không tạo file .lock), không sandbox guard ghi.
        return _all()
    _sandbox_guard()
    if _LOCK_HELD:
        return _all()
    lk = _lock(LEDGER_FILE)
    if lk is None:
        print(f"❌ không lấy được khoá {LEDGER_FILE}.lock sau {LOCK_WAIT_S}s — tiến trình khác đang "
              f"chạy nhánh broker; KHÔNG ghi gì.")
        return 1
    try:
        return _all()
    finally:
        lk.close()


# ── RC3: đối chiếu lại record broker SAU ex-date ────────────────────────────
REVERIFY_GIVEUP_SESSIONS = 5   # sau N phiên kể từ ex mà vendor vẫn không xác nhận ⇒ hỏi người 1 lần
REVERIFY_LOOKBACK_DAYS = 45    # m4 r3: đọc cả lịch asof TRƯỚC ex (sự kiện vendor nằm ở events_today ngày công bố)


def _vendor_events_post_ex(ticker, ex, upto):
    """Sự kiện vendor của `ticker` có GDKHQ trong ±VENDOR_EX_WINDOW_DAYS quanh `ex`, đọc từ
    `events_today` (+ `backfilled_events` nếu là list sự kiện) của MỌI lịch daily asof ∈
    [ex − REVERIFY_LOOKBACK_DAYS ngày lịch, upto] (m4 r3: bản r2 chỉ đọc asof ≥ ex ⇒ sự kiện vendor
    công bố trước ex — dòng events_today của ngày công bố — không bao giờ được thấy) mà feed TƯƠI
    (`feed_fresh_today` True — ngày STALE lặp lại sự kiện cũ, không phải bằng chứng).
    Chuẩn hoá về dạng vendor_crosscheck (`date` = exright_date, `price_adjusting` theo taxonomy
    CHUNG `corp_action_lib.is_price_adjusting`). Trả (events, n_file_tươi, đã_đọc_ngày_ex?)."""
    from corp_action_lib import is_price_adjusting
    ex_d, end = dt.date.fromisoformat(ex), dt.date.fromisoformat(upto)
    d = ex_d - dt.timedelta(days=REVERIFY_LOOKBACK_DAYS)
    evs, seen, n_fresh, ex_read = [], set(), 0, False
    while d <= end:
        path = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{d.isoformat()}.json")
        try:
            with open(path, encoding="utf-8") as f:
                snap = json.load(f)
        except (OSError, json.JSONDecodeError):
            snap = None
        if isinstance(snap, dict) and snap.get("feed_fresh_today") is True:
            n_fresh += 1
            ex_read = ex_read or d == ex_d
            rows = list(snap.get("events_today") or [])
            if isinstance(snap.get("backfilled_events"), list):
                rows += [x for x in snap["backfilled_events"] if isinstance(x, dict)]
            for e in rows:
                if _norm_ticker(e.get("ticker")) != ticker or not e.get("exright_date"):
                    continue
                k = e.get("id") or json.dumps(e, sort_keys=True, default=str)
                if k in seen:
                    continue
                seen.add(k)
                evs.append({"ticker": ticker, "event_code": e.get("event_code"),
                            "date": str(e.get("exright_date"))[:10],
                            "exercise_ratio": e.get("exercise_ratio"),
                            "value_per_share": e.get("value_per_share"),
                            "price_adjusting": is_price_adjusting(e),
                            "title": e.get("event_title_vi")})
        d += dt.timedelta(days=1)                   # ngày lịch: file chỉ có ở ngày có lịch
    return evs, n_fresh, ex_read


def _sessions_since(ex, day):
    from trading_bot.vn_market import next_trading_day
    d, n, end = dt.date.fromisoformat(ex), 0, dt.date.fromisoformat(day)
    while d < end:
        d = next_trading_day(d)
        n += 1
    return n


def _reverify_broker_records(date_str, mode):
    """RC3: record provenance=broker ĐANG CONFIRMED mà lúc ghi vendor CHƯA xác nhận (NO_EVENT /
    UNREADABLE / FEED_DEAD / PARTIAL) và ex ≤ date_str ⇒ đối chiếu LẠI với lịch vendor sau ex
    (vendor sống lại / lịch ngày ex). Kết quả, MỖI record MỘT lần (sổ `done`, bus rc=0):
      VERIFIED ⇒ finding; MISMATCH (hoặc thiếu trục KL) ⇒ question [Winston] (KHÔNG sửa record —
      người quyết REVOKED); sau REVERIFY_GIVEUP_SESSIONS phiên vẫn chưa xác nhận ⇒ question để
      user CHẤP NHẬN 'không đối chiếu lại' hoặc Winston kiểm. Chưa tới hạn ⇒ in trạng thái, chờ.
    shadow ⇒ CHỈ IN (không bus, không sổ); dry-run ⇒ cổng `_effects_blocked` (r4: bỏ cờ dry_run riêng — MỘT
    cơ chế). Không bao giờ ghi data/corp_actions.json.
    r4: khoá + hệ số/chân tiền từ OUTPUT CA.validate (`_reg_rows`); record validate() từ chối ⇒ MISMATCH."""
    rc = 0
    recs = [w for w in _reg_rows(load_corp_actions_raw())
            if str(w["rec"].get("provenance", "")).lower() == "broker" and w["effective"]
            and (w["rec"].get("vendor_check") or {}).get("status") != BD.V_VERIFIED
            and w["ex"] <= date_str]
    if not recs:
        return 0
    quiet = mode != "live"
    try:
        _intents, done = BD.ledger_state(LEDGER_FILE)
    except BD.CorpActionLedgerError as e:       # sổ hỏng ⇒ vẫn đối chiếu (hỏi thừa an toàn hơn im)
        print(f"  ⚠ sổ broker đọc hỏng ({e}) ⇒ không biết record nào đã đối chiếu lại, đối chiếu hết")
        done = set()
    for w in recs:
        r, rid, tk, ex = w["rec"], w["id"], w["ticker"], w["ex"]
        if any(tuple(["reverify", rid, x]) in done for x in ("VERIFIED", "MISMATCH", "GIVEUP")):
            continue
        try:
            n_sess = _sessions_since(ex, date_str)
        except ValueError:      # ex không đọc được ⇒ validate() đã từ chối; consumer chặn cả registry
            print(f"  [re-verify {rid}] ex_date không đọc được {r.get('ex_date')!r} — {w['invalid']} ⇒ bỏ qua")
            continue
        bad = w["invalid"] is not None
        m, cash = (float("nan"), float("nan")) if bad else (w["v"]["qty_multiplier"], w["v"]["cash_leg_vnd_per_share"])
        evs, n_fresh, ex_read = _vendor_events_post_ex(tk, ex, date_str)
        vc = (BD.vendor_crosscheck(ex, m, cash, evs) if n_fresh and not bad else
              {"status": BD.V_MISMATCH, "vendor": [],
               "why": f"record bị CA.validate() từ chối: {w['invalid']}"} if bad else
              {"status": BD.V_UNREADABLE, "vendor": [],
               "why": (f"chưa có lịch vendor TƯƠI nào từ {REVERIFY_LOOKBACK_DAYS} ngày trước ex {ex} tới "
                       f"{date_str} (feed chết/STALE/thiếu file)")})
        if vc["status"] == BD.V_MISMATCH or vc.get("qty_unconfirmed"):
            res = "MISMATCH"
        elif vc["status"] == BD.V_VERIFIED:
            res = "VERIFIED"
        elif n_sess >= REVERIFY_GIVEUP_SESSIONS:
            res = "GIVEUP"
        else:
            res = None
        print(f"  [re-verify {rid}] ex {ex} (+{n_sess} phiên, {n_fresh} lịch tươi, đọc được ngày ex: "
              f"{ex_read}): vendor {vc['status']} — {vc['why']} ⇒ {res or 'CHỜ'}")
        if res is None or quiet:
            continue
        cash_s = (repr(r.get("cash_leg_vnd_per_share")) if bad else
                  "KHÔNG khai (consumer đọc 0)" if r.get("cash_leg_vnd_per_share") is None else f"{cash:,.0f}")
        base = {"record_id": rid, "ticker": tk, "ex_date": ex, "qty_multiplier": r.get("qty_multiplier"),
                "cash_leg_vnd_per_share": r.get("cash_leg_vnd_per_share"),
                "vendor_check_at_write": (r.get("vendor_check") or {}).get("status"),
                "vendor_check_now": vc, "sessions_since_ex": n_sess, "fresh_calendars": n_fresh}
        if res == "VERIFIED":
            ok = _notify_once("finding", ["reverify", rid, res], f"corp-action-broker-reverify-{tk}-{ex}",
                              dict(base, status="VERIFIED_POST_EX", decided_by="agent",
                                   note="vendor xác nhận record broker SAU ex — record giữ nguyên"))
        elif res == "MISMATCH":
            ok = _notify_once("question", ["reverify", rid, res], f"corp-action-broker-reverify-{tk}-{ex}",
                              dict(base, assignee="Winston", urgency="high",
                                   question=(f"[Winston] {tk} ex {ex}: record broker {rid} ×{r.get('qty_multiplier')} "
                                             f"chân tiền {cash_s}đ/cp ĐÃ ÁP DỤNG, nay lịch vendor sau ex LỆCH: "
                                             f"{vc['why']}. KHÔNG tự sửa registry. Winston kiểm nguồn; người "
                                             f"quyết giữ hay REVOKED record.")))
        else:
            ok = _notify_once("question", ["reverify", rid, res], f"corp-action-broker-reverify-{tk}-{ex}",
                              dict(base, urgency="normal",
                                   question=(f"{tk} ex {ex}: record broker {rid} ×{r.get('qty_multiplier')} đã "
                                             f"áp dụng {n_sess} phiên mà vendor VẪN chưa xác nhận ({vc['status']}: "
                                             f"{vc['why']}). User chấp nhận 'không đối chiếu lại' (giữ record) "
                                             f"hay Winston kiểm nguồn vendor? Hỏi 1 lần, sẽ không nhắc lại.")))
        rc = rc or (0 if ok else 1)
    return rc


def _broker_reject(date_str, mode, rejected, base_err):
    """minor-5 r5: record broker bị validate()/I1 từ chối. Registry hỏng TỪ TRƯỚC (`base_err`) ⇒ 1 câu hỏi cho cả
    lô (không record nào ghi được, thủ phạm là record CŨ — B-3); ngược lại ⇒ 1 câu hỏi / record hỏng, mã hợp lệ
    cùng lô đã ghi. Cron lượt sau quét PHIÊN KHÁC ⇒ không tự thử lại; chạy TAY `--date` sau khi sửa (v2 N2). shadow
    ⇒ chỉ in (shadow không ghi registry). Trả rc."""
    for tk, rid, err in rejected:
        print(f"\n❌ NHÁNH BROKER KHÔNG GHI {rid} — validate() từ chối: {err}")
    if mode != "live":
        print(f"  (shadow) live sẽ hỏi validate-reject cho {[rid for _, rid, _ in rejected]}")
        return 0         # shadow: mục vẫn vào sổ/finding (kèm lý do) — rc theo đường thông báo
    rerun = (f"rồi chạy lại TAY: python3 mike/bin/corp_action_auto_confirm.py --date {date_str} (cron lượt sau "
             f"quét phiên khác, không tự thử lại)")
    if base_err is not None:
        return 1 if _bus("question", f"corp-action-broker-validate-reject-{date_str}",
                         {"question": (f"registry ĐÃ HỎNG TỪ TRƯỚC lượt này ({base_err}) ⇒ KHÔNG record broker nào "
                                       f"ghi được; mọi consumer (park_holdings/load_corp_actions) cũng đang bị chặn. "
                                       f"Sửa/REVOKE record cũ trong data/corp_actions.json {rerun}."),
                          "error": str(base_err), "bad_record_is_preexisting": True,
                          "candidates": [tk for tk, _, _ in rejected], "urgency": "high"}) else 1
    for tk, rid, err in rejected:
        _bus("question", f"corp-action-broker-validate-reject-{tk}-{date_str}",
             {"question": (f"validate() từ chối record broker {rid}: {err}. CHỈ record này không ghi — mã hợp lệ "
                           f"khác cùng lô đã ghi. Kiểm số broker, ghi tay nếu đúng, {rerun}."),
              "error": str(err), "ticker": tk, "record_id": rid, "bad_record_is_preexisting": False,
              "urgency": "high"})
    return 1


def _upd_proposed(existing, r):
    return {"record_id": str(existing), "rule": ONE_RECORD_RULE,
            "broker": {"ex_date": r.get("ex_date"), "qty_multiplier": r.get("qty_multiplier"),
                       "cash_leg_vnd_per_share": r.get("cash_leg")}}


def _i2_refresh(e, reg_recs, rows):
    """m1 r4 (I2 qua đường GỬI BÙ): mục sổ dở của lượt trước mang `record_proposed`/`record` đông cứng lúc
    đó; nay registry có thể ĐÃ có record khác cho mã quanh ex (người ghi, lượt khác ghi) ⇒ tính lại theo
    registry HIỆN TẠI: có record khác ⇒ bỏ đề xuất record, gắn `registry_update_proposed` (chỉ sửa/thu hồi).
    MAJOR-1 r5: gọi SAU vòng quyết cho CẢ mục mới lẫn gửi bù, trên registry + record lô sẽ ghi."""
    tk, ex = _norm_ticker(e.get("ticker")), e.get("ex_date")
    rrec = reg_recs.get((tk, ex))
    existing = rrec.get("id") if rrec is not None else None
    if existing is None and e.get("event_kind", "SHARE_EVENT") == "SHARE_EVENT":
        near = _near_duplicate(rows, tk, ex, e.get("credit_day"))
        existing = near[1] if near else None
    own = (e.get("record") or {}).get("id")
    if existing is None or str(existing) == str(own):
        return e
    print(f"  [{tk}] registry (sau lô) đã có record {existing} cho mã quanh ex {ex} ⇒ bỏ đề xuất record, chỉ "
          f"đề nghị sửa/thu hồi (I2)")
    out = {k: v for k, v in e.items() if k != "record_proposed"}
    out["registry_update_proposed"] = _upd_proposed(existing, e)
    return out


def _shadow_finding(date_str, entries):
    """m9 r4: shadow ⇒ ĐÚNG 1 finding tóm tắt/lượt cho mọi mục (cả 2 pha + gửi bù); bus rc=0 ⇒ done."""
    from zoneinfo import ZoneInfo
    now_ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%dT%H:%M:%S+07:00")
    rc = _bus("finding", f"corp-action-broker-shadow-{date_str}",
              {"mode": "shadow", "note": "KHÔNG ghi registry — cửa sổ quan sát chờ user duyệt bật live",
               "phases": sorted({str(e.get("phase")) for e in entries}),
               "results": [dict({k: e.get(k) for k in ("ticker", "credit_day", "ex_date", "verdict", "phase",
                                                        "event_kind", "qty_multiplier", "cash_leg",
                                                        "registry_has", "why")},
                                vendor_check=(e.get("vendor_check") or {}).get("status"),
                                registry_check=(e.get("registry_check") or {}).get("status"))
                           for e in entries]})
    if rc != 0:
        return 1
    _ledger_append([{"kind": "done", "key": e["key"], "at": now_ict} for e in entries])
    print(f"  shadow: 1 finding tóm tắt cho {len(entries)} mục")
    return 0


def _run_broker_locked(date_str, mode, results, resend=True, phase="qty", shadow_out=None):
    """`resend` — gửi bù mục sổ dở của lượt trước (chỉ pha đầu, tránh gửi 2 lần trong 1 lượt).
    `shadow_out` (list, shadow) — gom mục cần thông báo để `_shadow_finding` gửi 1 lần cho cả lượt."""
    meta = {}
    intents, done = BD.ledger_state(LEDGER_FILE, done_meta=meta)
    pending = ([e for k, e in intents.items() if k not in done and e.get("mode") == mode]
               if resend else [])
    actions_raw = load_corp_actions_raw()
    rows = _reg_rows(actions_raw)
    reg_recs = _registry_view(actions_raw)          # ≥2 record hiệu lực ⇒ record giả _dup_ids (m6)
    try:     # minor-5 r5: registry HỎNG TỪ TRƯỚC ⇒ mọi record bị từ chối; quy kết đúng thủ phạm (B-3) ở _broker_reject
        _validate_for_write(actions_raw, actions_raw)
        base_err = None
    except CA.CorpActionError as e:
        base_err = e
    from zoneinfo import ZoneInfo
    now_ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%dT%H:%M:%S+07:00")
    new, superseded, observed = [], set(), []
    # MAJOR-1 r5 (I2 ở writer broker): `batch` = record lô này SẼ ghi (live ghi thật; shadow mô phỏng y hệt). Mỗi
    # record vừa quyết vào `rows` ⇒ mục sau cùng mã ở ex gần / CÙNG (mã, ex) gặp near-dup với nó (bản r4: 2 mục
    # cùng mã ex kề đều CONFIRMABLE ⇒ ghi CẢ HAI = áp hệ số 2 lần). Mục quyết TRƯỚC record lô được tính lại I2
    # sau vòng (`_i2_refresh` trên registry + lô).
    batch, batch_keys, rejected = [], {}, []
    for r in results:
        r = dict(r, ticker=_norm_ticker(r["ticker"]))      # MAJOR-2 r4: khoá như CA.validate
        tk, ex, v = r["ticker"], r["ex_date"], r["verdict"]
        vc = r.get("vendor_check") or {}
        print(f"  [{tk}] ex {ex} {v} (vendor {vc.get('status', '-')}): {r['why']}")
        rrec = reg_recs.get((tk, ex))
        reg_has = str(rrec.get("_status", ""))[:40] if rrec is not None else None
        regc = None
        # chỉ sự kiện KL mới có thể thành record ⇒ chỉ nó cần chặn ×2 lần; tính TRƯỚC nhánh "registry
        # khớp": registry khớp mà CÒN record cùng mã ở ex khác gần đó ⇒ có thể đã áp 2 lần ⇒ hỏi.
        dup = None
        if r.get("kind") is None:
            dup = ((f"lô này đã quyết ghi {batch_keys[(tk, ex)]!r} cho CÙNG ({tk}, {ex}) — mục thứ hai cùng (mã, ex) "
                    f"⇒ không ghi thêm (×hệ số 2 lần)", batch_keys[(tk, ex)]) if (tk, ex) in batch_keys
                   else _near_duplicate(rows, tk, ex, date_str))
        if rrec is not None and v in (BD.CONFIRMABLE, BD.UNVERIFIED, BD.CASH_DIVIDEND):
            # RC1: đối chiếu record registry (MỌI provenance) với số broker — KHÔNG im lặng bỏ qua.
            regc = _registry_reconcile(rrec, r)
            print(f"  [{tk}] registry ĐÃ có ({tk}, {ex}) — đối chiếu: {regc['status']} — {regc['why']}")
            if regc["status"] == REG_MISMATCH:
                r = dict(r, verdict=BD.UNVERIFIED,
                         why=f"LỆCH REGISTRY: {regc['why']} ⇒ KHÔNG ghi đè, Winston kiểm; detector: {v} — {r['why']}")
                v = BD.UNVERIFIED
            elif v != BD.UNVERIFIED and not dup:
                print(f"  [{tk}] registry khớp broker ⇒ không ghi/hỏi lại")
                if mode == "live":
                    # m7 r3 (§26): câu hỏi cũ cùng mã/phiên nay đã được registry khớp broker giải quyết
                    superseded |= _close_resolved(tk, date_str, intents, done, regc, meta)
                    # Bằng chứng "broker ĐÃ thấy credit" cho credit-watch (m1) — dòng sổ CHỈ quan sát
                    # (intent + done cùng lúc, 0 bus): thiếu nó, phiên ex sau sẽ báo QUÁ HẠN giả.
                    obs = {"kind": "intent", "at": now_ict, "mode": mode, "ticker": tk, "credit_day": date_str,
                           "ex_date": ex, "verdict": v, "why": r["why"], "registry_has": reg_has,
                           "registry_check": regc, "phase": phase, "observation_only": True,
                           "qty_multiplier": r.get("qty_multiplier"), "cash_leg": r.get("cash_leg"),
                           "accounts": {}}
                    obs["key"] = BD.ledger_key(obs)
                    if not any(_norm_ticker(e.get("ticker")) == tk and e.get("ex_date") == ex
                               for e in intents.values()):
                        observed.append(obs)
                    continue
            # MATCH nhưng vendor LỆCH (UNVERIFIED) ⇒ vẫn đi tiếp để hỏi Winston về vendor.
        elif rrec is not None:
            print(f"  [{tk}] registry ĐÃ có ({tk}, {ex}) — {reg_has!r}; broker {v} chưa đối chiếu được ⇒ vẫn hỏi người")
        if reg_has is not None and mode != "live":
            print(f"  [{tk}] (shadow) registry đã có ({tk}, {ex}) — {reg_has!r}; vẫn ghi sổ để so sánh")
        if dup:
            # m7: UNVERIFIED (lệch vendor/registry) GIỮ verdict ⇒ câu hỏi vẫn gọi tên Winston.
            nv = BD.UNVERIFIED if v == BD.UNVERIFIED else BD.AMBIGUOUS
            r = dict(r, verdict=nv, why=f"{dup[0]}; detector: {v} — {r['why']}")
            v = nv
        entry = {"kind": "intent", "at": now_ict, "mode": mode, "ticker": tk,
                 "credit_day": date_str, "ex_date": ex, "verdict": v, "why": r["why"],
                 "event_kind": r.get("kind") or "SHARE_EVENT",
                 "qty_multiplier": r.get("qty_multiplier"), "cash_leg": r.get("cash_leg"),
                 "px_cum": r.get("px_cum"), "vendor_feed_dead": bool(r.get("vendor_feed_dead")),
                 "vendor_check": r.get("vendor_check"), "registry_has": reg_has,
                 "registry_check": regc, "phase": phase,
                 "accounts": {k: {kk: vv for kk, vv in a.items() if kk != "lots"}
                              for k, a in r["accounts"].items()}}
        entry["key"] = BD.ledger_key(entry)
        if tuple(entry["key"]) in intents:
            print(f"  [{tk}] sổ broker đã có {entry['key']} ⇒ không lặp (idempotent)")
            continue
        # I2 r3 (M2): record hiện có cho mã quanh ex ⇒ đường trả lời chỉ được SỬA/THU HỒI nó, KHÔNG mang
        # record_proposed. r5: tính MỘT NƠI — `_i2_refresh` sau vòng trên registry + lô (bỏ record_proposed, gắn
        # registry_update_proposed); bản r4 tính ở đây trên registry TRƯỚC lô (MAJOR-1).
        if v == BD.CONFIRMABLE or (v == BD.UNVERIFIED and r.get("qty_multiplier")):
            rec = BD.build_record(r, now_ict)
            if r.get("vendor_feed_dead"):
                rec["evidence"].append(FEED_DEAD_TAG)
            # UNVERIFIED: record chỉ là ĐỀ XUẤT trong câu hỏi cho người — KHÔNG BAO GIỜ ghi registry
            entry["record" if v == BD.CONFIRMABLE else "record_proposed"] = rec
            if v == BD.CONFIRMABLE and reg_has is None:
                # registry đã có (mã, ex) ⇒ KHÔNG BAO GIỜ ghi thêm (RC1: không ghi đè, không trùng; shadow ghi sổ để so).
                # minor-5 r5: validate + I1 TỪNG record trên registry + lô tới giờ — hỏng ⇒ CHỈ record này bị loại
                # (0 intent, câu hỏi riêng), mã hợp lệ cùng lô vẫn ghi. Bản r4 từ chối CẢ LÔ.
                err = None
                try:
                    _validate_for_write(actions_raw + batch + [rec], actions_raw)
                except CA.CorpActionError as e:
                    err = e
                if err is not None:
                    rejected.append((tk, rec["id"], err))
                    if mode == "live":
                        continue          # live: 0 intent ⇒ chạy tay --date sau khi sửa sẽ thử lại
                    entry["why"] = f"{entry['why']}; (shadow) live sẽ KHÔNG ghi — validate() từ chối: {err}"
                    new.append(entry)     # shadow: sổ/finding vẫn ghi điều broker thấy để so
                    continue
                batch.append(rec)
                batch_keys[(tk, ex)] = rec["id"]
                rows = rows + _reg_rows([rec])
        new.append(entry)
    rc = 0
    if rejected:
        rc = _broker_reject(date_str, mode, rejected, base_err)
    # MAJOR-1 r5: lô đã quyết ⇒ MỌI mục (mới + gửi bù) tính lại I2 trên registry SAU lô (cũ + record lô) — mục quyết
    # trước record lô, hay việc dở lượt trước mang record_proposed đông cứng, chỉ được đề nghị SỬA/THU HỒI record đó.
    fin = actions_raw + batch
    fview, frows = _registry_view(fin), _reg_rows(fin)
    new = [_i2_refresh(e, fview, frows) for e in new]
    pending = [_i2_refresh(e, fview, frows) for e in pending]
    new_recs = batch if mode == "live" else []
    if observed:
        _ledger_append(observed + [{"kind": "done", "key": o["key"], "at": now_ict, "observation_only": True}
                                   for o in observed])
    if new:
        _ledger_append(new)                              # pha 1: intent TRƯỚC mọi tác dụng ngoài
    if new_recs:
        write_corp_actions(actions_raw + new_recs)
    try:
        registry_ids = {a["id"] for a in CA.load_corp_actions(CORP_ACTIONS_FILE)}
    except CA.CorpActionError as e:
        # Registry hỏng (đã hỏi ở validate-reject) ⇒ KHÔNG đọc lại được: mục CONFIRMABLE dở (nếu
        # có) bị báo write-incomplete — đúng sự thật "không xác minh được", không giả là đã ghi.
        print(f"  ❌ load_corp_actions() lỗi khi đọc lại: {e}")
        registry_ids = set()
        rc = 1 if (pending or new) else rc
    if any(_DRY):       # minor-4 r5: dry-run đi CÙNG đường với lượt thật — record lô coi như ĐÃ ghi (cổng chặn ghi)
        registry_ids |= {x["id"] for x in new_recs}
    written = [e for e in new if e["verdict"] == BD.CONFIRMABLE and e["record"]["id"] in registry_ids]
    if mode == "live":
        # m4 r4 (§26): ghi CONFIRMED cũng giải quyết câu hỏi cũ cùng mã/phiên — việc dở chưa gửi bị bỏ
        # (superseded), không gửi bù câu hỏi đã hết thời (bản r3 chỉ làm ở nhánh registry-khớp).
        for e in written:
            superseded |= _close_resolved(e["ticker"], e["credit_day"], intents, done, {}, meta, answer=False)
    if superseded:      # việc dở lượt trước đã được giải quyết ⇒ KHÔNG gửi bù câu hỏi đã hết thời
        pending = [e for e in pending if tuple(e.get("key") or BD.ledger_key(e)) not in superseded]
        _ledger_append([{"kind": "done", "key": list(k), "at": now_ict, "superseded": True}
                        for k in sorted(superseded, key=str)])
    todo = pending + new
    for e in todo:
        e.setdefault("key", BD.ledger_key(e))          # dòng sổ định dạng cũ (không có key)
    if not todo:
        print("  → không mục mới / không việc dở.")
        return rc
    if pending:
        print(f"  ↻ gửi bù {len(pending)} mục sổ chưa có 'done' (lượt trước bị kill/bus lỗi)")
    if mode != "live" and shadow_out is not None:
        shadow_out.extend(todo)                          # m9 r4: 1 finding cho cả lượt (_shadow_finding)
        print(f"Xong nhánh broker pha {phase}: {len(new)} mục sổ mới, {len(pending)} gửi bù — gộp vào finding shadow cuối lượt.")
        return rc
    finished = []
    if mode == "live":
        for e in todo:
            if e["verdict"] == BD.CONFIRMABLE and e["record"]["id"] not in registry_ids:
                rc = 1                                       # §6 verify artifact: không thấy ⇒ lỗi
            if _finish_live(e, registry_ids) == 0:
                finished.append(e)
                if e["verdict"] == BD.CONFIRMABLE and e["record"]["id"] in registry_ids:
                    _close_resolved(e["ticker"], e["credit_day"], intents, done,
                                    {"record_id": e["record"]["id"],
                                     "why": (f"nhánh broker đã ghi CONFIRMED {e['record']['id']} ×{e['qty_multiplier']} "
                                             f"ex {e['ex_date']} (provenance=broker)")}, meta)
            else:
                rc = 1
    elif _shadow_finding(date_str, todo) == 0:
        finished = []                                    # done đã ghi trong _shadow_finding
    else:
        rc = 1
    if finished:
        _ledger_append([{"kind": "done", "key": e["key"], "at": now_ict} for e in finished])  # pha 2: sau bus
    print(f"Xong nhánh broker: {len(new)} mục sổ mới, {len(pending)} gửi bù, {len(new_recs)} "
          f"record ghi registry, {len(finished)}/{len(todo)} đã thông báo.")
    return rc


def main():
    ap = argparse.ArgumentParser(description="Tự động xác nhận corp action khi broker credit")
    ap.add_argument("--dry-run", action="store_true",
                    help="In kết quả nhưng KHÔNG ghi file / gửi bus")
    ap.add_argument("--date", default=None,
                    help="Ngày cần kiểm (mặc định: hôm nay ICT)")
    a = ap.parse_args()
    date_str = a.date or today_ict()
    sys.exit(run(date_str, dry_run=a.dry_run))


if __name__ == "__main__":
    main()
