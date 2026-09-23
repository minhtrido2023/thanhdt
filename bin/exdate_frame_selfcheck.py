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
def run_nav(can, positions, prices, out, account="SpaceX", no_patch=False):
    """Chạy main() thật với broker/giá đã stub. Trả rc."""
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
    sys.argv = ["compute_active_nav.py", "--account", account, "--asof", DATE, "--out", out]
    try:
        with contextlib.redirect_stdout(io.StringIO()):     # bảng NAV dài, không phải kết quả test
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
    rc = run_nav(can, {"VPB": {"total": QTY_NOW["SpaceX"], "sellable": 0,
                               "marketPrice": PX_CUM}}, {"VPB": PX_CUM}, out)
    check(rc == 6, "E7 credit sớm mà không dựng nổi giá cùng hệ ⇒ rc=6", f"rc={rc}")
    check(json.load(open(out, encoding="utf-8")).get("sentinel"),
          "E8 fail-closed: file active_nav CŨ còn nguyên, không bị đè")


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

    # asof QUÁ KHỨ: nguồn giá là BQ Close (đã điều chỉnh hồi tố) ⇒ KHÔNG được sửa lần hai.
    PH.today_ict = lambda: "2026-09-25"
    r3 = run(PX_TERP)
    mv3 = sum(l["mv_vnd"] for l in r3["park_lots"])
    check(abs(mv3 - QTY_NOW["SpaceX"] * PX_CUM) < 1e-6,
          "K5 asof QUÁ KHỨ: giữ NGUYÊN hành vi cũ (giá BQ đã điều chỉnh hồi tố)", f"{mv3:,.0f}")


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
    finally:
        shutil.rmtree(sb, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)
    for f in FAILS:
        print(f"  ❌ {f}")
    print(f"{NCHK - len(FAILS)}/{NCHK} PASS" + (f", {len(FAILS)} FAIL" if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
