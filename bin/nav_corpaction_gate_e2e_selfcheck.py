#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""End-to-end selfcheck cho corp_action_gate_v2 — chạy THẬT `daily_nav_snapshot.main()` ở chế độ
`--from-raw` trên fixture SANDBOX, không chạm file thật, không gọi BQ/broker.

Chạy:  python3 mike/bin/nav_corpaction_gate_e2e_selfcheck.py
       cd /tmp && env -u TZ python3 <repo>/mike/bin/nav_corpaction_gate_e2e_selfcheck.py

Vì sao cần E2E chứ không chỉ unit test (arch-review vòng 2, mục [1] + [3]): killer objection của
vòng 1 KHÔNG nằm trong bất kỳ hàm nào — nó nằm ở THỨ TỰ trong main(). `return 5` chạy TRƯỚC
`if args.from_raw:`, nên nhánh `early_credit` (đường DUY NHẤT quy ngược KL theo qty_multiplier
CONFIRMED) vĩnh viễn không tới được. Mọi hàm đều "đúng" khi test riêng.

Ca gốc có thật: VIB bonus-issue 9,5%, ex-date 2026-09-10, DNSE credit sớm 1 phiên (SpaceX
500→547, ZaloPay 200→219). Đường tự lành đã chạy thật ngày đó: gate → corp_action_auto_confirm.py
19:25 ghi CONFIRMED mult=1.095 → `--from-raw` quy ngược KL → NAV 09-09 tái dựng được.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import daily_nav_snapshot as D  # noqa: E402
import corp_action_daily as CAD  # noqa: E402
import verify_account_snapshot as V  # noqa: E402

PASS, FAIL = [], []
ACCT, ACCT_NO, DATE, PREV = "SpaceX", "0002023347", "2026-09-09", "2026-09-08"
EX_DATE, MULT, PRICE = "2026-09-10", 1.095, 21_000.0


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


def build_fixture(tmp, qty_now, qty_prev=500.0, fills=(), event=True, confirmed=True,
                  mkt=None, act_ex_date=None, ratio="0.095", prev_holds=True, mults=None):
    """dnse_raw (2 ngày) + journal + corp_actions.json + corp_action_daily snapshot.

    `act_ex_date` — ex_date ghi trong corp_actions.json khi KHÁC ex-date trên lịch (ca [g]).
    `ratio`       — exercise_ratio của sự kiện trên lịch (ca [i3] dùng 1%).
    `prev_holds`  — False ⇒ bản ghi vị thế ngày trước CÓ THẬT nhưng KHÔNG chứa VIB (ca [i3]/[i4]).
    `mults`       — danh sách qty_multiplier ghi vào corp_actions.json (mặc định [MULT]). Nhiều
                    phần tử = NHIỀU action CONFIRMED cùng mã cùng ex-date (ca hỗn hợp [j2]).
    """
    def pos(ts, qty, holds=True):
        return {"kind": "positions", "ts": ts, "account_no": ACCT_NO, "payload": {"positions": (
            [{"symbol": "VIB", "openQuantity": qty,
              "marketPrice": PRICE / MULT if mkt is None else mkt}] if holds else
            [{"symbol": "ZZZ", "openQuantity": 10.0, "marketPrice": 1_000.0}])}}
    with open(os.path.join(tmp, f"dnse_raw_{PREV}.jsonl"), "w") as f:
        f.write(json.dumps(pos(f"{PREV}T19:00:00", qty_prev, prev_holds)) + "\n")
    with open(os.path.join(tmp, f"dnse_raw_{DATE}.jsonl"), "w") as f:
        f.write(json.dumps(pos(f"{DATE}T19:00:00", qty_now)) + "\n")
        f.write(json.dumps({"kind": "balances", "ts": f"{DATE}T19:05:00", "account_no": ACCT_NO,
                            "payload": {"stock": {"totalCash": 5_000_000.0, "totalDebt": 0.0}}}) + "\n")
    hdr = ("ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n")
    with open(os.path.join(tmp, f"exec_{ACCT}_{DATE}_journal.csv"), "w") as f:
        f.write(hdr)
        for i, (side, q) in enumerate(fills):
            f.write(f"{DATE}T09:20:0{i},FILL,P{i},VIB,{side},{9000+i},{q},{PRICE},0,BAL,X,\n")
    acts = {"actions": [{"id": f"VIB-TEST-{i}", "ticker": "VIB",
                         "ex_date": act_ex_date or EX_DATE,
                         "qty_multiplier": m,
                         "_status": ("CONFIRMED — corp_action_auto_confirm.py test"
                                     if confirmed else "PROPOSED — chưa ai ký")}
                        for i, m in enumerate(mults or [MULT])]}
    with open(os.path.join(tmp, "corp_actions.json"), "w") as f:
        json.dump(acts, f)
    snap = {"asof": DATE, "status": "OK", "usable": True, "feed_status": "FRESH",
            "upcoming_events_held": ([{"ticker": "VIB", "date": EX_DATE, "event_code": "ISS",
                                       "price_adjusting": True, "exercise_ratio": ratio}]
                                     if event else [])}
    with open(os.path.join(tmp, f"corp_action_daily_{DATE}.json"), "w") as f:
        json.dump(snap, f)


def load_block(tmp):
    """corp_action_gate_v2 trong artifact chặn, hoặc {} nếu KHÔNG chặn.

    ⚠️ HARNESS (arch-review vòng 3): `json.load(open(blk))` trần làm cả script CHẾT bằng
    FileNotFoundError khi một mutation biến rc=5 thành rc=0 — ca đó "fail" nhờ script nổ chứ
    KHÔNG bằng assertion, và mọi check SAU nó không bao giờ chạy. Trả {} để check kế tiếp vẫn
    fail đúng chỗ của nó.
    """
    blk = os.path.join(tmp, f"nav_gate_block_{ACCT}_{DATE}.json")
    if not os.path.exists(blk):
        return {}
    return json.load(open(blk, encoding="utf-8")).get("corp_action_gate_v2") or {}


def run(tmp):
    """Chạy main() --from-raw trong sandbox; trả (rc, stderr, snapshot_json_hoặc_None)."""
    import io
    import contextlib
    old = (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path,
           D.bq_raw_prices, D.cum_dividend_double_count, sys.argv,
           os.environ.get("NAV_SANITY_MAX_PCT"), V.EXEC_DIR)
    D.EXEC_DIR = V.EXEC_DIR = tmp
    D.CORP_ACTIONS_FILE = os.path.join(tmp, "corp_actions.json")
    D.HISTORY_FILE_TMPL = os.path.join(tmp, "nav_history_{account}.csv")
    CAD.snapshot_path = lambda d: os.path.join(tmp, f"corp_action_daily_{d}.json")
    D.bq_raw_prices = lambda tickers, date: ({t: PRICE for t in tickers},
                                             {t: PRICE for t in tickers}, None)
    D.cum_dividend_double_count = lambda *a, **k: {
        "amount": 0.0, "delta": 0.0, "expected_bq": None, "tickers": [], "bq_max_date": None,
        "note": "", "warnings": []}
    os.environ["NAV_SANITY_MAX_PCT"] = "1000000"
    sys.argv = ["daily_nav_snapshot.py", "--account", ACCT, "--account-no", ACCT_NO,
                "--date", DATE, "--from-raw", "--starting-capital", "10000000"]
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = D.main()
    finally:
        (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path,
         D.bq_raw_prices, D.cum_dividend_double_count, sys.argv, _env, V.EXEC_DIR) = old
        if _env is None:
            os.environ.pop("NAV_SANITY_MAX_PCT", None)
        else:
            os.environ["NAV_SANITY_MAX_PCT"] = _env
    snap_p = os.path.join(tmp, f"nav_snapshot_{ACCT}_{DATE}.json")
    snap = json.load(open(snap_p, encoding="utf-8")) if os.path.exists(snap_p) else None
    return rc, err.getvalue(), snap


print("1. [1] Đường PHỤC HỒI --from-raw cho corp-action ĐÃ CONFIRMED (killer objection vòng 1)")
with tempfile.TemporaryDirectory() as tmp:
    build_fixture(tmp, qty_now=547.0, confirmed=True)
    rc, err, snap = run(tmp)
    check("(1a) VIB 500→547, corp_actions.json CONFIRMED mult=1.095 ⇒ rc=0 (KHÔNG chặn)",
          rc == 0, (rc, err[-400:]))
    check("(1b) KL được quy NGƯỢC về trước sự kiện (547/1,095 ≈ 499,5)",
          snap is not None and abs(snap["corp_action_qty_adj"].get("VIB", 0) - MULT) < 1e-9
          and abs(snap["mtm_stock"] - 547.0 / MULT * PRICE) < 1.0,
          (snap or {}).get("mtm_stock"))
    check("(1c) có dòng nav_history được ghi",
          os.path.exists(os.path.join(tmp, f"nav_history_{ACCT}.csv")))
    check("(1d) gate ghi lại việc đã phục hồi (audit được)",
          bool((snap or {}).get("corp_action_gate_v2", {}).get("corp_action_recovered")), snap)
    check("(1e) KHÔNG sinh file nav_gate_block_* khi không chặn",
          not os.path.exists(os.path.join(tmp, f"nav_gate_block_{ACCT}_{DATE}.json")))

print("2. Mô hình TIN CẬY không đổi — CHƯA CONFIRMED thì vẫn CHẶN (bỏ điều kiện ⇒ case này chết)")
with tempfile.TemporaryDirectory() as tmp:
    build_fixture(tmp, qty_now=547.0, confirmed=False)
    rc, err, snap = run(tmp)
    check("(2a) corp_actions.json PROPOSED ⇒ rc=5", rc == 5, (rc, err[-400:]))
    check("(2b) thông điệp nói ĐÚNG bằng chứng (phần dư khớp tỉ lệ), không đoán",
          "KHỚP tỉ lệ 0.095" in err and "CREDIT SỚM" in err, err[-500:])
    blk = os.path.join(tmp, f"nav_gate_block_{ACCT}_{DATE}.json")
    check("(2c) [3] bằng chứng chặn ghi ra tên RIÊNG nav_gate_block_*, KHÔNG đè nav_snapshot_*",
          os.path.exists(blk) and snap is None, os.listdir(tmp))
    check("(2d) artifact chặn có đủ số liệu đối soát",
          json.load(open(blk))["corp_action_gate_v2"]["share_event_blocks"][0]["detail"]["residual"] == 47.0)

print("3. [3] §8 — chạy lại tay sau ngày ĐÃ có NAV không được ĐÈ MẤT artifact audit")
with tempfile.TemporaryDirectory() as tmp:
    build_fixture(tmp, qty_now=547.0, confirmed=False)
    keep = {"account": ACCT, "date": DATE, "nav": 987_654_321.0, "mtm_stock": 1.0}
    with open(os.path.join(tmp, f"nav_snapshot_{ACCT}_{DATE}.json"), "w") as f:
        json.dump(keep, f)
    rc, err, snap = run(tmp)
    check("(3a) rc=5 nhưng nav_snapshot_* CŨ còn nguyên (nav != null)",
          rc == 5 and snap == keep, snap)

print("4. [2] §29 — KL đổi do LỆNH KHỚP THẬT không được báo 'credit sớm' (rc=5 giả)")
with tempfile.TemporaryDirectory() as tmp:
    # Không có corp-action nào ⇒ marketPrice khớp giá BQ; cú đổi KL hoàn toàn do lệnh mua.
    build_fixture(tmp, qty_now=600.0, fills=[("buy", 100)], confirmed=False, mkt=PRICE)
    rc, err, snap = run(tmp)
    check("(4a) mua 100 đúng phiên cum, KL 500→600 ⇒ rc=0, KHÔNG chặn", rc == 0, (rc, err[-400:]))
with tempfile.TemporaryDirectory() as tmp:
    # Vừa mua 100 VỪA bị credit sớm 47 ⇒ phần dư vẫn lộ ra, phải chặn.
    build_fixture(tmp, qty_now=647.0, fills=[("buy", 100)], confirmed=False)
    rc, err, snap = run(tmp)
    check("(4b) mua 100 + credit 47 ⇒ vẫn rc=5, phần dư +47", rc == 5 and "+47" in err, err[-400:])

print("5. [2] gap D — KL đổi thật nhưng LỊCH thiếu sự kiện: trước đây KHÔNG ai chặn")
with tempfile.TemporaryDirectory() as tmp:
    build_fixture(tmp, qty_now=547.0, event=False, confirmed=False)
    rc, err, snap = run(tmp)
    check("(5a) lịch rỗng + KL +47 không lệnh khớp ⇒ rc=5", rc == 5, (rc, err[-400:]))
    check("(5b) thông điệp nói THẲNG 'CHƯA GIẢI THÍCH ĐƯỢC', KHÔNG khẳng định credit sớm",
          "CHƯA GIẢI THÍCH ĐƯỢC" in err and "KHÔNG có sự kiện nào" in err, err[-500:])

print("6. [5] §14 — mất snapshot lịch: gate phải NÓI, và trục KHỐI LƯỢNG vẫn sống")
with tempfile.TemporaryDirectory() as tmp:
    build_fixture(tmp, qty_now=547.0, confirmed=False)
    os.remove(os.path.join(tmp, f"corp_action_daily_{DATE}.json"))
    rc, err, snap = run(tmp)
    check("(6a) thiếu corp_action_daily ⇒ vẫn chặn rc=5 (trục KL không phụ thuộc lịch)", rc == 5,
          (rc, err[-400:]))
    check("(6b) in ⚠️ nói rõ gate đang thiếu lịch", "KHÔNG xác nhận được lịch corp-action" in err,
          err[-500:])
with tempfile.TemporaryDirectory() as tmp:
    # KL không đổi + giá khớp ⇒ đường THÀNH CÔNG (rc=0), để kiểm bản ghi gate ở nhánh đó.
    build_fixture(tmp, qty_now=500.0, confirmed=False, mkt=PRICE)
    os.remove(os.path.join(tmp, f"corp_action_daily_{DATE}.json"))
    rc, err, snap = run(tmp)
    check("(6c) ngày bình thường vẫn ghi corp_action_gate_v2.active=false vào nav_snapshot",
          rc == 0 and snap["corp_action_gate_v2"]["active"] is False, (rc, (snap or {}).get("corp_action_gate_v2")))

print("7. [B1] arch-review vòng 3 — đường PHỤC HỒI phải có BẰNG CHỨNG mult giải thích phần dư,")
print("   không chỉ 'có action CONFIRMED tồn tại' (§29 dạng 2: chữ 'khớp' phải đọc bằng chứng)")
with tempfile.TemporaryDirectory() as tmp:
    # (g) LỊCH MẤT (snapshot corp_action_daily chỉ có từ 2026-08-13 ⇒ mọi backfill cũ hơn chạy
    # KHÔNG có ev) + corp_actions.json giữ một action CONFIRMED ex-date CÁCH 5 TUẦN. Bản trước
    # vá: ex_date=None ⇒ vơ bừa mult 1.095 ⇒ rc=0, KL 547→499,54, mtm=10.490.411 ghi thẳng
    # nav_history. data/corp_actions.json thật đang giữ VHM mult 2.0 — cùng lớp lỗi = lệch 50%.
    build_fixture(tmp, qty_now=547.0, confirmed=True, act_ex_date="2026-10-15")
    os.remove(os.path.join(tmp, f"corp_action_daily_{DATE}.json"))
    rc, err, snap = run(tmp)
    check("(g1) lịch mất + CONFIRMED ex-date KHÁC phiên kế tiếp ⇒ rc=5 (KHÔNG vơ bừa mult)",
          rc == 5, (rc, err[-400:]))
    check("(g2) KHÔNG ghi NAV — mtm_stock sai 10.490.411 không tồn tại",
          snap is None and not os.path.exists(os.path.join(tmp, f"nav_history_{ACCT}.csv")),
          (snap or {}).get("mtm_stock"))
with tempfile.TemporaryDirectory() as tmp:
    # (h) ex-date ĐÚNG phiên kế tiếp + CONFIRMED, nhưng KL +200 (kỳ vọng +47,5) ⇒ mult KHÔNG
    # tái tạo được KL trước sự kiện. Bản trước vá: rc=0, KL 700→639,27, mtm=13.424.657.
    build_fixture(tmp, qty_now=700.0, confirmed=True)
    rc, err, snap = run(tmp)
    check("(h1) ex-date khớp nhưng phần dư KHÔNG khớp mult ⇒ rc=5", rc == 5, (rc, err[-400:]))
    check("(h2) KHÔNG ghi NAV — mtm_stock sai 13.424.657 không tồn tại",
          snap is None and not os.path.exists(os.path.join(tmp, f"nav_history_{ACCT}.csv")),
          (snap or {}).get("mtm_stock"))
    g = load_block(tmp)
    check("(h3) artifact chặn ghi đúng phần dư +200 ở nhánh 'chưa giải thích được'",
          [d["detail"]["residual"] for d in g.get("qty_unexplained") or []] == [200.0],
          (g.get("qty_unexplained"), os.listdir(tmp)))
    check("(h4) đường phục hồi KHÔNG chạy (không có corp_action_recovered)",
          bool(g) and not g.get("corp_action_recovered"), g.get("corp_action_recovered"))
with tempfile.TemporaryDirectory() as tmp:
    # Đối chứng KHÔNG-ĐƯỢC-CHẾT: VIB thật KỂ CẢ KHI LỊCH MẤT vẫn phải phục hồi đúng — bản vá
    # [B1] neo ex-date vào PHIÊN KẾ TIẾP nên guard sống cả khi ev=None, tức CỨU thêm ca backfill
    # ngày không có snapshot lịch mà (g)/(h) vẫn chặn.
    build_fixture(tmp, qty_now=547.0, confirmed=True)
    os.remove(os.path.join(tmp, f"corp_action_daily_{DATE}.json"))
    rc, err, snap = run(tmp)
    check("(g3) VIB THẬT + lịch mất + CONFIRMED ex-date = phiên kế tiếp ⇒ rc=0, vẫn phục hồi",
          rc == 0 and snap is not None
          and abs(snap["mtm_stock"] - 547.0 / MULT * PRICE) < 1.0,
          (rc, (snap or {}).get("mtm_stock"), err[-400:]))

print("8. [B2] arch-review vòng 3 — bản ghi ngày trước CÓ nhưng VẮNG mã này ⇒ qty_prev = 0,")
print("   không phải 'không biết' (fail-open cũ nuốt đúng lớp L4 mà gate sinh ra để đóng)")
with tempfile.TemporaryDirectory() as tmp:
    # (i3) mã chưa giữ ở bản ghi ngày trước + mua 500 hôm nay + ISS 1% credit sớm 5 cp.
    # Giá rơi 1% < PRICE_XCHECK_TOLERANCE_PCT=5% ⇒ trục GIÁ im lặng. Bản trước vá: qty_prev=None
    # ⇒ trục KL cũng im ⇒ rc=0, mtm = 505 × 21.000 thay vì 500 × 21.000.
    build_fixture(tmp, qty_now=505.0, fills=[("buy", 500)], confirmed=False, ratio="0.01",
                  prev_holds=False, mkt=PRICE / 1.01)
    rc, err, snap = run(tmp)
    check("(i3a) mã mới + ISS ~1% credit sớm 5cp ⇒ rc=5 (trước vá: rc=0)", rc == 5,
          (rc, err[-500:]))
    check("(i3b) KHÔNG ghi NAV — mtm_stock sai 505×21.000 = 10.605.000 không tồn tại",
          snap is None, (snap or {}).get("mtm_stock"))
    d = ([x["detail"] for x in load_block(tmp).get("qty_unexplained") or []] or [{}])[0]
    check("(i3c) bằng chứng ghi đúng: qty_prev=0, lệnh khớp thật +500, phần dư +5",
          d.get("qty_prev") == 0.0 and d.get("net_fill") == 500.0 and d.get("residual") == 5.0, d)
with tempfile.TemporaryDirectory() as tmp:
    # (i4) ĐỐI CHỨNG: mã mới mua BÌNH THƯỜNG (không sự kiện) phải rc=0 — siết [B2] không được
    # sinh false-block. Đo thật tháng 9: 1/600 ticker-day rơi vào ca này (VPI 09-17), phần dư
    # = 0,0 CHÍNH XÁC.
    build_fixture(tmp, qty_now=500.0, fills=[("buy", 500)], event=False, confirmed=False,
                  prev_holds=False, mkt=PRICE)
    rc, err, snap = run(tmp)
    check("(i4a) mã mới mua bình thường ⇒ rc=0 (siết [B2] KHÔNG sinh false-block)", rc == 0,
          (rc, err[-500:]))
    check("(i4b) mtm_stock = 500 × 21.000 = 10.500.000 CHÍNH XÁC",
          snap is not None and abs(snap["mtm_stock"] - 500.0 * PRICE) < 1e-6,
          (snap or {}).get("mtm_stock"))

print("9. [C1] arch-review vòng 4 — dung sai tương đối neo vào ĐỘ LỚN SỰ KIỆN, không phải độ")
print("   lớn vị thế: `qty_multiplier` ghi SAI ≤2% KHÔNG được coi là 'giải thích được' phần dư")
with tempfile.TemporaryDirectory() as tmp:
    # (j1) vị thế 10.000 + sự kiện THẬT 26% (credit 2.600) nhưng corp_actions.json ghi mult 1,24
    # (sai 1,6%). Bản vòng 3: |12.600/1,24 − 10.000| = 161,29 ≤ tol 2%×10.000 = 200 ⇒ rc=0, ghi
    # nav_history với KL 10.161,29 (lệch +1,61% giá trị vị thế) — lọt cổng sanity ±15%.
    build_fixture(tmp, qty_now=12_600.0, qty_prev=10_000.0, confirmed=True, ratio="0.26",
                  mults=[1.24])
    rc, err, snap = run(tmp)
    check("(j1a) mult ghi 1,24 cho sự kiện thật 1,26 ⇒ rc=5 (trước vá: rc=0)", rc == 5,
          (rc, err[-500:]))
    check("(j1b) KHÔNG ghi NAV — mtm_stock sai 10.161,29 × 21.000 không tồn tại",
          snap is None and not os.path.exists(os.path.join(tmp, f"nav_history_{ACCT}.csv")),
          (snap or {}).get("mtm_stock"))
    check("(j1c) đường phục hồi KHÔNG chạy", not load_block(tmp).get("corp_action_recovered"),
          load_block(tmp).get("corp_action_recovered"))
with tempfile.TemporaryDirectory() as tmp:
    # (j2) ca HỖN HỢP rất phổ biến ở VN: HAI action CONFIRMED cùng mã cùng ex-date (1,10 và
    # 1,005 ⇒ KL thật ×1,1055). `confirmed_share_event_multiplier` trả action ĐẦU TIÊN có
    # mult≠1,0 = 1,10. Bản vòng 3: |11.055/1,10 − 10.000| = 50 ≤ tol 200 ⇒ rc=0, KL 10.050
    # thay vì 10.000 ⇒ NAV +0,50% IM LẶNG. Sau vá: tol = 2%×1.055 = 21,1 ⇒ chặn.
    build_fixture(tmp, qty_now=11_055.0, qty_prev=10_000.0, confirmed=True, ratio="0.1055",
                  mults=[1.10, 1.005])
    rc, err, snap = run(tmp)
    check("(j2a) 2 action cùng ex-date (1,10 + 1,005), first-match 1,10 ⇒ rc=5 (trước vá: rc=0)",
          rc == 5, (rc, err[-500:]))
    check("(j2b) KHÔNG ghi NAV — mtm_stock sai 10.050 × 21.000 = 211.050.000 không tồn tại",
          snap is None and not os.path.exists(os.path.join(tmp, f"nav_history_{ACCT}.csv")),
          (snap or {}).get("mtm_stock"))
    check("(j2c) đường phục hồi KHÔNG chạy", not load_block(tmp).get("corp_action_recovered"),
          load_block(tmp).get("corp_action_recovered"))

print("10. [D1] arch-review vòng 5 — dung sai là GIAO của hai mẫu số: mult > 2,0 KHÔNG được")
print("   NỚI so với vòng 3 (residual > base ⟺ m > 2 ⇒ mẫu số 'độ lớn sự kiện' lớn hơn 'vị thế')")
with tempfile.TemporaryDirectory() as tmp:
    # (k1) VHM đang giữ qty_multiplier 2.0 CONFIRMED trong data/corp_actions.json THẬT. Ca hỗn
    # hợp first-match (cùng cơ chế [j2]): 2,0 + leg 2,05% ⇒ KL thật ×2,041. Bản vòng 4 lấy mẫu
    # số |qty_now − _base| = 10.410 ⇒ tol 208,2 > dev 205 ⇒ rc=0, KL 10.205 thay vì 10.000 ⇒
    # NAV +2,05% IM LẶNG — YẾU HƠN vòng 3 (tol 2%×10.000 = 200 đã chặn). GIAO min(residual,
    # base) giữ tol = 200 ⇒ chặn ở CẢ HAI nhánh.
    build_fixture(tmp, qty_now=20_410.0, qty_prev=10_000.0, confirmed=True, ratio="1.041",
                  mults=[2.0, 1.0205])
    rc, err, snap = run(tmp)
    check("(k1a) mult > 2 (2,0 + leg 2,05%) ⇒ rc=5 — KHÔNG BAO GIỜ yếu hơn vòng 3", rc == 5,
          (rc, err[-500:]))
    check("(k1b) KHÔNG ghi NAV — mtm_stock sai 10.205 × 21.000 = 214.305.000 không tồn tại",
          snap is None and not os.path.exists(os.path.join(tmp, f"nav_history_{ACCT}.csv")),
          (snap or {}).get("mtm_stock"))
    check("(k1c) đường phục hồi KHÔNG chạy", not load_block(tmp).get("corp_action_recovered"),
          load_block(tmp).get("corp_action_recovered"))

print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
sys.exit(1 if FAIL else 0)
