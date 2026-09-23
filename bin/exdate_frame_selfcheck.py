#!/usr/bin/env python3
"""exdate_frame_selfcheck.py — cửa sổ ĐÊM TRƯỚC GDKHQ: KL và giá phải cùng một hệ quy chiếu.

HERMETIC: dựng cây WorkingClaude giả trong tmpdir (`WC_ROOT` + `WORKDIR_8L`), symlink
`trading_bot` từ cây thật (chỉ đọc lịch phiên/tick), KHÔNG chạm `data/execution_logs` thật và
KHÔNG gọi DNSE. Vì vậy chạy được mọi lúc, kể cả trong cửa sổ cron.

Ca nền = ca THẬT đã cắn 2026-09-23 (VPB ISS 0,2604104, ex-date 24/09):
    SpaceX  KL 1.100→1.386, G1 close 27.800, marketPrice broker 22.050
    ZaloPay KL 1.200→1.512  (§12 — cùng file dnse_raw, PHẢI ra số khác nhau)

Chạy:  python3 bin/exdate_frame_selfcheck.py [--mutations]
"""
import contextlib
import datetime as _dt
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wc_paths  # noqa: E402
# Cây THẬT phải tìm bằng MARKER, không đếm cấp: file này chạy được từ cả checkout canonical
# (`mike/bin/`) lẫn worktree (`mike/wt-*/bin/`) — hai độ sâu khác nhau (wc_paths.py §sự cố
# 2026-09-12). Gọi TRƯỚC khi đặt env WC_ROOT=sandbox, nếu không nó tự trỏ về sandbox.
REAL_WC = wc_paths._walk_to_marker(__file__)
assert REAL_WC and os.path.isdir(os.path.join(REAL_WC, "trading_bot")), \
    f"không dựng được cây WorkingClaude thật từ {HERE}"

DATE = "2026-09-23"
PREV = "2026-09-22"
ACC = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
RATIO = 0.2604104
QTY_PREV = {"SpaceX": 1100, "ZaloPay": 1200}
QTY_NOW = {"SpaceX": 1386, "ZaloPay": 1512}
PX_CUM = 27800.0
PX_TERP = 22050.0

FAILS = []
NCHK = 0


def check(cond, label, detail=""):
    global NCHK
    NCHK += 1
    if not cond:
        FAILS.append(f"{label}" + (f" — {detail}" if detail else ""))


def _pos_rec(account_no, ts, rows):
    return json.dumps({"kind": "positions", "account_no": account_no, "ts": ts,
                       "payload": {"positions": rows}}, ensure_ascii=False)


def build_sandbox(qty_now=None, extra_ticker=("ACB", 900, 900)):
    """Cây giả. `qty_now` override KL hôm nay; `extra_ticker` = (sym, qty_prev, qty_now) — mặc
    định ACB 900→900 (mã ĐỨNG YÊN, làm chứng cứ chống hồi quy cho ngày thường); truyền
    ("ACB", 900, 1000) để dựng ca KL đổi KHÔNG giải thích được."""
    sb = tempfile.mkdtemp(prefix="exdate_sb_")
    open(os.path.join(sb, "wc_env.sh"), "w").close()
    ex = os.path.join(sb, "data", "execution_logs")
    ca = os.path.join(sb, "data", "corp_action_daily")
    os.makedirs(ex); os.makedirs(ca)
    os.symlink(os.path.join(REAL_WC, "trading_bot"), os.path.join(sb, "trading_bot"))
    # `corp_action_daily.py` dựng sys.path từ `WORKDIR_8L/mike/bin` — trỏ về CHÍNH cây đang
    # chạy (worktree hay canonical) để nạp đúng bản code đang kiểm, không phải bản khác.
    os.symlink(os.path.dirname(HERE), os.path.join(sb, "mike"))

    qty_now = qty_now or QTY_NOW

    for d, qmap, px in ((PREV, QTY_PREV, 28000), (DATE, qty_now, PX_TERP)):
        lines = []
        for label, no in ACC.items():                  # §12 — MỘT file, HAI account
            rows = [{"symbol": "VPB", "openQuantity": qmap[label], "marketPrice": px,
                     "status": "OPEN"}]
            if extra_ticker:
                sym, qp, qn = extra_ticker
                rows.append({"symbol": sym, "openQuantity": (qp if d == PREV else qn),
                             "marketPrice": 21800, "status": "OPEN"})
            lines.append(_pos_rec(no, f"{d}T12:00:00", rows))
        with open(os.path.join(ex, f"dnse_raw_{d}.jsonl"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    os.makedirs(os.path.join(sb, "secrets"))
    with open(os.path.join(sb, "secrets", "trading_bot_accounts.json"), "w",
              encoding="utf-8") as f:
        json.dump({"accounts": [{"label": k, "account_id": v} for k, v in ACC.items()]}, f)
    pl = os.path.join(sb, "data", "trade_plans")
    os.makedirs(pl)
    with open(os.path.join(pl, "bootstrap_book_snapshot_SpaceX_2026-09-01.json"), "w",
              encoding="utf-8") as f:
        json.dump({"_status": "APPROVED (selfcheck)", "reconcile_ok": True,
                   "day0_date": "2026-09-01", "broker_source": {"ts": "2026-09-01T12:00:00"},
                   "positions": [{"ticker": "VPB", "book": "PARK", "qty": QTY_PREV["SpaceX"],
                                  "cost_price_vnd": 27000.0, "entry_date": "2026-09-01"}]}, f)
    with open(os.path.join(ca, f"corp_action_daily_{DATE}.json"), "w", encoding="utf-8") as f:
        json.dump({"asof": DATE, "status": "OK", "usable": True, "feed_status": "FRESH",
                   "upcoming_events_held": [
                       {"ticker": "VPB", "date": "2026-09-24", "event_code": "ISS",
                        "price_adjusting": True, "exercise_ratio": str(RATIO)}]}, f)
    return sb


def fresh_modules(sb):
    """Import exdate_frame + compute_active_nav với WC_ROOT trỏ sandbox (module-level constant
    ⇒ phải nạp LẠI sạch mỗi lần đổi sandbox)."""
    for m in ("exdate_frame", "compute_active_nav", "daily_nav_snapshot", "corp_action_daily",
              "verify_account_snapshot", "wc_paths"):
        sys.modules.pop(m, None)
    os.environ["WC_ROOT"] = sb
    os.environ["WORKDIR_8L"] = sb
    sys.path.insert(0, HERE)
    # Thư viện dùng chung sống ở gốc cây THẬT (corp_action_lib.py, oshares_live.py) — sandbox
    # chỉ giả DỮ LIỆU, không giả code. Append (không insert) để sandbox vẫn thắng ở mọi tên trùng.
    if REAL_WC not in sys.path:
        sys.path.append(REAL_WC)
    import exdate_frame
    import compute_active_nav
    return exdate_frame, compute_active_nav


# ─────────────────────────── 1. verify_post_event_price (PURE) ───────────────────────────
def t_pure(ef):
    px, why = ef.verify_post_event_price(PX_CUM, PX_TERP, 1 + RATIO)
    check(px == PX_TERP, "P1 ca THẬT VPB: marketPrice 22.050 tái tạo được 27.800/1,2604104", why)
    check("22,056" in why, "P2 thông điệp trích BẰNG CHỨNG đã đọc (§29)", why)

    px, why = ef.verify_post_event_price(PX_CUM, PX_CUM, 1 + RATIO)
    check(px is None, "P3 marketPrice CÒN Ở HỆ CŨ (27.800) ⇒ từ chối, không đoán", str(why))

    px, _ = ef.verify_post_event_price(PX_CUM, 0, 1 + RATIO)
    check(px is None, "P4 broker không trả marketPrice ⇒ từ chối")
    px, _ = ef.verify_post_event_price(PX_CUM, None, 1 + RATIO)
    check(px is None, "P5 marketPrice None ⇒ từ chối")
    px, _ = ef.verify_post_event_price(PX_CUM, PX_TERP, 0)
    check(px is None, "P6 hệ số ≤ 0 ⇒ từ chối")
    px, _ = ef.verify_post_event_price("x", PX_TERP, 1.26)
    check(px is None, "P7 đầu vào không ép được về số ⇒ từ chối, KHÔNG ném")

    # Biên dung sai: 0,5% của 22.056,3 = 110,3 < sàn 200 ⇒ ngưỡng thật là 200đ.
    px, _ = ef.verify_post_event_price(PX_CUM, 22056.3 + 199, 1 + RATIO)
    check(px is not None, "P8 lệch 199đ (< sàn 200đ) vẫn nhận")
    px, _ = ef.verify_post_event_price(PX_CUM, 22056.3 + 201, 1 + RATIO)
    check(px is None, "P9 lệch 201đ (> sàn 200đ) bị từ chối")
    # Mã giá cao: 0,5% chiếm quyền thay cho sàn 200đ.
    px, _ = ef.verify_post_event_price(120000.0, 60000.0 + 310, 2.0)
    check(px is None, "P10 mã 120k: lệch 310đ > 0,5%×60.000 = 300đ ⇒ từ chối")
    px, _ = ef.verify_post_event_price(120000.0, 60000.0 + 290, 2.0)
    check(px is not None, "P11 mã 120k: lệch 290đ ≤ 300đ ⇒ nhận")
    # Quyền mua có nộp tiền: ref = (P+r·giá_ph)/(1+r) ≠ P/(1+r) ⇒ PHẢI fail-closed.
    rights_ref = (24250 + 0.1 * 10000) / 1.1
    px, _ = ef.verify_post_event_price(24250.0, rights_ref, 1.1)
    check(px is None, "P12 QUYỀN MUA (có dòng tiền vào) không khớp công thức thuần ⇒ từ chối")


# ─────────────────────── 2. classify_positions trên cây giả (§12) ────────────────────────
def t_classify(ef):
    for label in ("SpaceX", "ZaloPay"):
        cr, bl = ef.classify_positions(label, ACC[label], DATE,
                                       {"VPB": {"total": QTY_NOW[label], "marketPrice": PX_TERP}})
        check("VPB" in cr and not bl, f"C1[{label}] nhận diện credit sớm", f"{cr} {bl}")
        d = cr.get("VPB", {})
        check(d.get("qty_prev") == QTY_PREV[label] and d.get("qty_now") == QTY_NOW[label],
              f"C2[{label}] §12 đọc ĐÚNG account của mình trong file dùng chung", str(d))
    # Hai account phải ra hai số khác nhau — dấu hiệu rẻ nhất bắt lỗi thiếu lọc account_no.
    a = ef.classify_positions("SpaceX", ACC["SpaceX"], DATE, {"VPB": {"total": 1386}})[0]["VPB"]
    b = ef.classify_positions("ZaloPay", ACC["ZaloPay"], DATE, {"VPB": {"total": 1512}})[0]["VPB"]
    check(a["residual"] != b["residual"], "C3 §12 hai account cho KẾT QUẢ KHÁC nhau",
          f"{a['residual']} vs {b['residual']}")


# ───────────────────── 3. compute_active_nav end-to-end (giá trị THẬT) ──────────────────────
def run_nav(can, positions, prices, out, account="SpaceX", no_patch=False, asof=DATE,
            err_out=None):
    """Chạy main() thật với broker/giá đã stub. Trả rc.

    `out=None` ⇒ KHÔNG truyền `--out`, script tự trỏ vào tên file CANONICAL trong sandbox —
    đúng đường mà chốt chặn `--asof` quá khứ ([R4]) phải chặn. `err_out` (StringIO) bắt stderr
    để test ĐỌC ĐƯỢC thông điệp thay vì chỉ đếm rc.
    """
    import exdate_frame as ef
    orig_cls = ef.classify_positions
    if no_patch:
        ef.classify_positions = lambda *a, **k: ({}, {})    # MUTATION: gỡ bản vá
    can.live_balance_and_positions = lambda aid, lab: (
        1_000_000.0, positions,
        {"cash_total_vnd": 1_000_000.0, "cash_debt_vnd": 0.0, "cash_available_vnd": 1_000_000.0,
         "cash_dividend_receiving_vnd": 0.0, "cash_basis": "totalCash-totalDebt"}, 0.0)
    can.resolve_prices = lambda tks, asof: (dict(prices),
                                            {t: "dnse_g1_today" for t in prices}, None)
    can.today_ict = lambda: _dt.date.fromisoformat(DATE)
    can.get_account_profile = lambda lab: {"label": lab, "account_id": ACC[lab]}
    argv = sys.argv
    sys.argv = (["compute_active_nav.py", "--account", account, "--asof", asof]
                + (["--out", out] if out else []))
    try:
        with contextlib.redirect_stdout(io.StringIO()):     # bảng NAV dài, không phải kết quả test
            with (contextlib.redirect_stderr(err_out) if err_out is not None
                  else contextlib.nullcontext()):
                can.main()
        return 0
    except SystemExit as e:
        return int(e.code or 0)
    finally:
        sys.argv = argv
        ef.classify_positions = orig_cls


def t_e2e(ef, can, tmp):
    pos = {"VPB": {"total": QTY_NOW["SpaceX"], "sellable": 0, "marketPrice": PX_TERP}}
    out = os.path.join(tmp, "a.json")

    rc = run_nav(can, pos, {"VPB": PX_CUM}, out)
    d = json.load(open(out, encoding="utf-8"))
    row = d["positions"][0]
    check(rc == 0, "E1 ca THẬT: ghi được file", f"rc={rc}")
    check(row["value"] == QTY_NOW["SpaceX"] * PX_TERP,
          "E2 ca THẬT: value = 1.386 × 22.050 = 30.561.300",
          f"{row['value']:,.0f} (SAI nếu = 38.530.800)")
    check(row["value"] != QTY_NOW["SpaceX"] * PX_CUM, "E3 KHÔNG còn là 1.386 × 27.800")
    check(row["price_source"] == "dnse_position_marketprice_corpaction",
          "E4 provenance nói ĐÚNG nguồn giá", row["price_source"])

    # (a-mutation) gỡ bản vá ⇒ E2 phải CHẾT bằng ASSERTION, không phải crash.
    os.remove(out)
    rc = run_nav(can, pos, {"VPB": PX_CUM}, out, no_patch=True)
    d2 = json.load(open(out, encoding="utf-8"))
    check(rc == 0 and d2["positions"][0]["value"] == QTY_NOW["SpaceX"] * PX_CUM,
          "E5 MUTATION: gỡ bản vá ⇒ tái hiện ĐÚNG 38.530.800 (test cũ chết bằng assertion)",
          f"rc={rc} value={d2['positions'][0]['value']:,.0f}")

    # (b) ngày thường, không corp-action ⇒ giá KHÔNG đổi (chống hồi quy).
    os.remove(out)
    rc = run_nav(can, {"ACB": {"total": 900, "sellable": 900, "marketPrice": 21800.0}},
                 {"ACB": 21800.0}, out)
    d3 = json.load(open(out, encoding="utf-8"))
    check(rc == 0 and d3["positions"][0]["value"] == 900 * 21800.0
          and d3["positions"][0]["price_source"] == "dnse_g1_today",
          "E6 ngày thường: giá trị và provenance KHÔNG đổi", json.dumps(d3["positions"][0]))

    # (d) credit sớm nhưng marketPrice CÒN Ở HỆ CŨ ⇒ fail-closed, KHÔNG ghi đè file cũ.
    os.remove(out)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"sentinel": "file CŨ phải còn nguyên"}, f)
    err = io.StringIO()
    rc = run_nav(can, {"VPB": {"total": QTY_NOW["SpaceX"], "sellable": 0,
                               "marketPrice": PX_CUM}}, {"VPB": PX_CUM}, out, err_out=err)
    check(rc == 6, "E7 credit sớm mà không dựng nổi giá cùng hệ ⇒ rc=6", f"rc={rc}")
    check(json.load(open(out, encoding="utf-8")).get("sentinel"),
          "E8 fail-closed: file active_nav CŨ còn nguyên, không bị đè")
    # [R3] Đường phục hồi in ra phải là việc CHÍNH script này chạy được. `corp_action_auto_confirm
    # .py`/`--from-raw` đi qua `confirmed_share_event_multiplier`, thứ script này KHÔNG gọi ở bất
    # kỳ nhánh nào ⇒ khuyên vậy là bắt người vận hành lặp một vòng cho kết quả Y HỆT (§29).
    e = err.getvalue()
    check("chờ corp_action_auto_confirm.py rồi chạy lại" not in e,
          "E9 KHÔNG khuyên đường phục hồi mà script này không chạy được", e[-400:])
    check("NGƯỜI xác minh giá tham chiếu" in e and "--out" in e,
          "E10 nói ĐÚNG việc phải làm + cách xem số mà không đụng file sizing", e[-400:])


def t_unexplained(tmp):
    """(c) KL đổi KHÔNG giải thích được ⇒ FAIL-CLOSED."""
    sb = build_sandbox(extra_ticker=("ACB", 900, 1000))
    ef, can = fresh_modules(sb)
    out = os.path.join(tmp, "c.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"sentinel": "cũ"}, f)
    rc = run_nav(can, {"ACB": {"total": 1000, "sellable": 1000, "marketPrice": 21800.0}},
                 {"ACB": 21800.0}, out)
    check(rc == 6, "U1 KL đổi ngoài lệnh khớp & không khớp tỉ lệ nào ⇒ rc=6", f"rc={rc}")
    check(json.load(open(out, encoding="utf-8")).get("sentinel"),
          "U2 fail-closed: không ghi đè active_nav cũ")
    shutil.rmtree(sb, ignore_errors=True)


ACT_VPB = {"id": "VPB-2026-09-24-BONUS-ISSUE", "ticker": "VPB", "event_type": "BONUS_ISSUE",
           "ratio_text": "Trả Cổ tức bằng Cổ phiếu tỉ lệ 26.0%", "qty_multiplier": 1 + RATIO,
           "ex_date": "2026-09-24", "record_date": None,
           "broker_effective_ts": f"{DATE}T11:58:04", "_status": "CONFIRMED — selfcheck",
           "confirmed_by": "selfcheck", "decided_by": "agent",
           "confirmed_at": f"{DATE}T19:25:01+07:00",
           "evidence": ["NGUỒN 1 — selfcheck", "NGUỒN 2 — selfcheck"]}


def t_park(sb, tmp):
    """park_holdings — MẪU SỐ của PARK_TRIM. Cùng ca VPB, đường dữ liệu KHÁC (sổ lô + ledger)."""
    sys.modules.pop("park_holdings", None)
    import park_holdings as PH
    PH.today_ict = lambda: DATE          # neo ngày: nếu không, selfcheck đổi hành vi theo ngày chạy
    meta = {"source": "selfcheck", "asof": DATE, "total_cash_vnd": 0.0, "total_debt_vnd": 0.0,
            "egg_assets_vnd": 0.0, "balance_all_zero": False, "dividend_receiving_vnd": 0.0}

    def run(broker_mp):
        bk = ({"VPB": {"qty": QTY_NOW["SpaceX"], "market_price": PX_CUM, "sellable": 0,
                       "broker_market_price": broker_mp}}, 0.0, meta)
        return PH.park_holdings("SpaceX", asof=DATE, plan_dir=os.path.join(sb, "data", "trade_plans"),
                                exec_dir=os.path.join(sb, "data", "execution_logs"),
                                broker=bk, corp_actions=[ACT_VPB])

    r = run(PX_TERP)
    mv = sum(l["mv_vnd"] for l in r["park_lots"])
    check(abs(mv - QTY_NOW["SpaceX"] * PX_TERP) < 1e-6,
          "K1 park_mv = 1.386 × 22.050 = 30.561.300 (KHÔNG phải 38.530.800)", f"{mv:,.0f}")
    check(r["reconcile"]["ok"] and not r["unverified_tickers"],
          "K2 sổ vẫn đối soát khớp broker, không ticker nào UNVERIFIED", str(r["unverified_tickers"]))

    r2 = run(PX_CUM)          # marketPrice CÒN ở hệ cũ ⇒ không dựng nổi giá cùng hệ
    check("VPB" in r2["unverified_tickers"],
          "K3 không dựng được giá cùng hệ ⇒ VPB UNVERIFIED (cấm sinh lệnh)",
          str(r2["unverified_tickers"]))
    check(any("KHÔNG dựng được giá cùng hệ" in w for w in r2["warnings"]),
          "K4 cảnh báo nói ĐÚNG chuyện gì xảy ra (§29)")

    # [F4c] Nhánh verify-FAIL: `park_mv_vnd` KHÔNG sửa được (đó chính là ca fail) nên nó VẪN là
    # 38.530.800 — điều phải chặn là con số đó trở thành MẪU SỐ sizing. Cờ CẤP TÀI KHOẢN
    # `frame_blocked_tickers` + cổng BLOCKED_FRAME ở CẢ HAI lớp là chỗ chặn. Không có nó,
    # `unverified_tickers` chỉ cấm VPB sinh lệnh còn số phồng vẫn nằm trong pool ⇒ over-trim
    # các mã KHÁC thêm (1−target)×Δ, rồi chảy tiếp vào L2.
    check(r2.get("frame_blocked_tickers") == ["VPB"],
          "K6 verify-fail ⇒ phát cờ CẤP TÀI KHOẢN frame_blocked_tickers (không chỉ UNVERIFIED)",
          str(r2.get("frame_blocked_tickers")))
    check(not r["frame_blocked_tickers"],
          "K7 verify-OK ⇒ cờ RỖNG (không chặn nhầm ngày thường)", str(r["frame_blocked_tickers"]))
    mv2 = sum(l["mv_vnd"] for l in r2["park_lots"])
    check(abs(mv2 - QTY_NOW["SpaceX"] * PX_CUM) < 1e-6,
          "K8 (bối cảnh) mẫu số ở nhánh fail ĐÚNG LÀ số phồng 38.530.800 — nên phải chặn, không "
          "phải tin", f"{mv2:,.0f}")

    sys.modules.pop("compute_park_trim", None)
    sys.modules.pop("compute_jit_unpark", None)
    import compute_park_trim as L1
    import compute_jit_unpark as L2
    # Cổng đặt NGAY SAU reconcile, TRƯỚC cả cổng tiền/state ⇒ K9 đồng thời chứng minh thứ tự:
    # fixture này có mọi field tiền = 0 nên KHÔNG có gate ⇒ rơi vào BLOCKED_CASH_BASIS (đo thật
    # bằng mutation M-F3b). Nghĩa là K9 chứng minh CỜ THẮNG TRƯỚC, không chứng minh "nếu thiếu
    # gate thì sinh lệnh trim" — vế đó suy từ đường code :331 park_mv → :406 pool → :408 delta.
    t1 = L1.compute_trim("SpaceX", asof=DATE, holdings=r2)
    check(t1["decision"] == "BLOCKED_FRAME",
          "K9 L1 PARK_TRIM fail-closed BLOCKED_FRAME, KHÔNG trim trên mẫu số phồng",
          f"{t1['decision']} / {t1.get('orders')}")
    check(not t1["orders"] and "38,530,800" in " ".join(t1["notes"]),
          "K10 L1 không sinh lệnh nào và NÓI RA con số mẫu số bị từ chối (§29)",
          str(t1["notes"])[:200])
    t2 = L2.compute_jit_unpark("SpaceX", asof=DATE, holdings=r2, orders=[])
    check(t2["decision"] == "BLOCKED_FRAME" and not t2["orders"],
          "K11 L2 JIT_UNPARK fail-closed BLOCKED_FRAME (số phồng KHÔNG chảy xuống tầng 2)",
          f"{t2['decision']} / {t2.get('orders')}")
    t1ok = L1.compute_trim("SpaceX", asof=DATE, holdings=r)
    check(t1ok["decision"] != "BLOCKED_FRAME",
          "K12 verify-OK ⇒ L1 KHÔNG bị chặn (cổng không chặn nhầm ngày thường)",
          str(t1ok["decision"]))

    # asof QUÁ KHỨ: nguồn giá là BQ Close (đã điều chỉnh hồi tố) ⇒ KHÔNG được sửa lần hai.
    PH.today_ict = lambda: "2026-09-25"
    r3 = run(PX_TERP)
    mv3 = sum(l["mv_vnd"] for l in r3["park_lots"])
    check(abs(mv3 - QTY_NOW["SpaceX"] * PX_CUM) < 1e-6,
          "K5 asof QUÁ KHỨ: giữ NGUYÊN hành vi cũ (giá BQ đã điều chỉnh hồi tố)", f"{mv3:,.0f}")


def t_calendar_and_journal(tmp):
    """[R1]+[R2] — hai kênh bằng chứng (LỊCH corp-action, JOURNAL fill) đều fail được trong im
    lặng. Thông điệp blocked phải PHÂN BIỆT "lịch nói không có sự kiện" với "không đọc được
    lịch", và phải tự khai khi journal thiếu — nếu không, chẩn đoán là suy diễn từ SỰ VẮNG MẶT
    của một kênh (§28/§29), đúng lỗi replay vòng 1 in ra cho VHM 08-05 / MBB 08-11.

    Cả 4 assertion dưới đây CHẾT BẰNG TÊN (không phải crash) nếu ai gỡ `_corp_action_gate_status`
    hoặc `missing_out=` — đó là điểm V3 của arch-review vòng 2.
    """
    # (a) LỊCH KHÔNG ĐỌC ĐƯỢC (file không tồn tại — producer fail thật, xem _FAILED.json trên đĩa)
    sb = build_sandbox(extra_ticker=("ACB", 900, 1000))
    os.remove(os.path.join(sb, "data", "corp_action_daily", f"corp_action_daily_{DATE}.json"))
    ef, _can = fresh_modules(sb)
    msg = ef.classify_positions("SpaceX", ACC["SpaceX"], DATE,
                                {"ACB": {"total": 1000}})[1].get("ACB", "")
    check("KHÔNG ĐỌC ĐƯỢC LỊCH" in msg, "D1 thiếu file lịch ⇒ thông điệp nói ĐÚNG là không đọc "
          "được lịch", msg)
    check("KHÔNG có sự kiện nào" not in msg,
          "D2 thiếu file lịch ⇒ TUYỆT ĐỐI không khẳng định 'lịch không có sự kiện nào'", msg)
    check("thiếu/không đọc được corp_action_daily" in msg,
          "D3 note của _corp_action_gate_status đi kèm (bằng chứng, không phải phỏng đoán)", msg)
    check("journal KHÔNG đọc được" in msg,
          "J1 journal thiếu trong cửa sổ ⇒ caveat 'lệnh khớp thật' có thể THIẾU", msg)
    shutil.rmtree(sb, ignore_errors=True)

    # (b) LỊCH ĐỌC ĐƯỢC + OK ⇒ câu "không có sự kiện nào" mới hợp lệ, và phải kèm status=OK.
    sb = build_sandbox(extra_ticker=("ACB", 900, 1000))
    ef, _can = fresh_modules(sb)
    msg = ef.classify_positions("SpaceX", ACC["SpaceX"], DATE,
                                {"ACB": {"total": 1000}})[1].get("ACB", "")
    check("KHÔNG có sự kiện nào" in msg and "status=OK usable=True" in msg,
          "D4 lịch OK ⇒ kết luận 'không có sự kiện' kèm bằng chứng lịch tươi", msg)

    # (c) journal CÓ THẬT ⇒ caveat phải BIẾN MẤT (nếu không, nó là chuỗi hằng vô dụng).
    with open(os.path.join(sb, "data", "execution_logs", f"exec_SpaceX_{DATE}_journal.csv"),
              "w", encoding="utf-8") as f:
        f.write("ts,child_oid,event,ticker,side,qty,price\n")
    msg2 = ef.classify_positions("SpaceX", ACC["SpaceX"], DATE,
                                 {"ACB": {"total": 1000}})[1].get("ACB", "")
    check("journal KHÔNG đọc được" not in msg2,
          "J2 journal đọc được ⇒ KHÔNG còn caveat (caveat theo bằng chứng, không hằng số)", msg2)
    shutil.rmtree(sb, ignore_errors=True)


def t_asof_guard(tmp):
    """[R4] cổng §exdate_frame chỉ chạy ở nhánh asof=hôm nay ⇒ `--asof <quá khứ>` từng là LỐI
    VÒNG: vị thế vẫn đọc LIVE (get_positions không phụ thuộc --asof) nên vẫn là KL ĐÃ CREDIT,
    giá lại của ngày cũ, và file canonical vẫn bị ghi đè với rc=0."""
    sb = build_sandbox()
    ef, can = fresh_modules(sb)
    canonical = os.path.join(sb, "data", "execution_logs", "active_nav_SpaceX.json")
    with open(canonical, "w", encoding="utf-8") as f:
        json.dump({"sentinel": "canonical phải còn nguyên"}, f)
    pos = {"VPB": {"total": QTY_NOW["SpaceX"], "sellable": 0, "marketPrice": PX_TERP}}

    rc = run_nav(can, pos, {"VPB": PX_CUM}, None, asof=PREV)
    check(rc == 7, "A1 --asof quá khứ KHÔNG có --out ⇒ rc=7 (từ chối ghi canonical)", f"rc={rc}")
    check(json.load(open(canonical, encoding="utf-8")).get("sentinel"),
          "A2 file active_nav canonical KHÔNG bị đụng tới")

    err = io.StringIO()
    out = os.path.join(tmp, "asof.json")
    rc2 = run_nav(can, pos, {"VPB": PX_CUM}, out, asof=PREV, err_out=err)
    check(rc2 == 0, "A3 có --out ⇒ vẫn chạy được (khảo sát/đối chiếu)", f"rc={rc2}")
    check("§exdate_frame" in err.getvalue() and "KHÔNG chạy" in err.getvalue(),
          "A4 nhưng phải NÓI RA rằng cổng bị tắt cho bản chạy này", err.getvalue()[-300:])

    rc3 = run_nav(can, pos, {"VPB": PX_CUM}, None, asof=DATE)
    check(rc3 == 0 and json.load(open(canonical, encoding="utf-8")).get("active_nav"),
          "A5 asof=HÔM NAY vẫn ghi canonical bình thường (chốt chặn không chặn nhầm)", f"rc={rc3}")

    # [F4a] `--asof ""` — hình dạng `--asof "$ASOF"` với biến CHƯA SET. Chuỗi rỗng FALSY ⇒ trượt
    # qua cả chốt chặn này (`args.asof and ...`), cổng §exdate_frame (`args.asof is None`) lẫn
    # `bq_close_sql` (`if as_of_date else "TRUE"`). Mike chạy thật trên production: rc=0, canonical
    # ghi đè, VPB = 38.530.800, tín hiệu duy nhất là ⚠️ nên `cron_health_check.py` (`^\s*❌`) mù.
    # Sau chuẩn hoá, `""` ≡ None ⇒ CÙNG nhánh "hôm nay" ⇒ cổng §exdate_frame CHẠY và chặn.
    sb2 = build_sandbox()
    ef, can = fresh_modules(sb2)
    canon2 = os.path.join(sb2, "data", "execution_logs", "active_nav_SpaceX.json")
    with open(canon2, "w", encoding="utf-8") as f:
        json.dump({"sentinel": "canonical phải còn nguyên"}, f)
    pos_bad = {"VPB": {"total": QTY_NOW["SpaceX"], "sellable": 0, "marketPrice": PX_CUM}}
    rc4 = run_nav(can, pos_bad, {"VPB": PX_CUM}, None, asof="")
    check(rc4 == 6, "A6 `--asof \"\"` KHÔNG còn là lối vòng: chuẩn hoá về None ⇒ cổng "
                    "§exdate_frame chạy ⇒ rc=6 (❌, cron_health_check thấy)", f"rc={rc4}")
    check(json.load(open(canon2, encoding="utf-8")).get("sentinel"),
          "A7 `--asof \"\"` KHÔNG đụng tới file canonical")
    check(bq_empty_asof_rejected(can),
          "A8 lớp hai: bq_close_sql từ chối as_of_date rỗng, không âm thầm thành 'TRUE'")

    # [F4b] Chốt chặn từng kiểm `--out` CÓ/KHÔNG chứ không kiểm nó TRỎ ĐI ĐÂU — mà chính thông
    # điệp rc=6/rc=7 lại dạy người vận hành dùng `--out`. Cả đường dẫn thẳng lẫn đường qua `./`.
    for label, target in (("thẳng", canon2),
                          ("qua ./", os.path.join(os.path.dirname(canon2), ".",
                                                  os.path.basename(canon2)))):
        with open(canon2, "w", encoding="utf-8") as f:
            json.dump({"sentinel": "canonical phải còn nguyên"}, f)
        rc5 = run_nav(can, pos, {"VPB": PX_CUM}, target, asof=PREV)
        check(rc5 == 7, f"A9[{label}] `--out` trỏ vào CHÍNH file canonical ⇒ rc=7 (realpath, "
                        f"không phải kiểm có/không)", f"rc={rc5}")
        check(json.load(open(canon2, encoding="utf-8")).get("sentinel"),
              f"A10[{label}] canonical KHÔNG bị ghi đè qua đường `--out`")
    shutil.rmtree(sb2, ignore_errors=True)
    shutil.rmtree(sb, ignore_errors=True)


def bq_empty_asof_rejected(can):
    """`bq_close_sql("")` phải NÉM, không được sinh `WHERE ... AND TRUE` (= bỏ lọc ngày im lặng)."""
    try:
        can.bq_close_sql(["VPB"], "")
        return False
    except ValueError:
        return True


def main():
    tz = os.environ.get("TZ", "(không đặt)")
    print(f"== exdate_frame_selfcheck (TZ={tz}) ==")
    tmp = tempfile.mkdtemp(prefix="exdate_out_")
    sb = build_sandbox()
    try:
        ef, can = fresh_modules(sb)
        t_pure(ef)
        t_classify(ef)
        t_e2e(ef, can, tmp)
        t_park(sb, tmp)
        t_unexplained(tmp)
        t_calendar_and_journal(tmp)
        t_asof_guard(tmp)
    finally:
        shutil.rmtree(sb, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)
    for f in FAILS:
        print(f"  ❌ {f}")
    print(f"{NCHK - len(FAILS)}/{NCHK} PASS" + (f", {len(FAILS)} FAIL" if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
