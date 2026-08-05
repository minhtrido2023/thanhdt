# -*- coding: utf-8 -*-
"""lag_governance_order_gate_selfcheck.py — self-check cho
trading_bot.plan.filter_lag_governance_orders (lưới an toàn tầng ORDER cho gate quản trị book
LAG: BANNED vĩnh viễn + LAG_USER_EXCLUDED + cờ forensic severity=exclude).

Chạy:  $DNA_PYEXE lag_governance_order_gate_selfcheck.py          (unit, offline — không cần BQ)
       $DNA_PYEXE lag_governance_order_gate_selfcheck.py --live   (thêm REPLAY plan THẬT:
           ca IVS 2026-07-23 CẢ 2 ACCOUNT, và toàn bộ plan thật 07-20→08-04 để xác nhận
           0 lệnh nào KHÁC bị đổi)

Khác `lag_forensic_filter_selfcheck.py`: file kia kiểm hàm lọc ỨNG VIÊN ở tầng tín hiệu
(DataFrame candidate); file này kiểm việc áp cùng gate đó lên TỪNG ORDER trong TradePlan ở tầng
executor — tức tầng mà sự cố 2026-07-23 thật sự xảy ra.

Không phụ thuộc TZ/đồng hồ hệ thống: mọi mốc thời gian truyền tường minh (coding_guidelines §16;
kiểm lại bằng `env -u TZ` + một TZ ngoại lai — xem phần cuối README của skill verify-before-done).
"""
import os
import re
import sys

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

import pandas as pd

from trading_bot import plan as plan_mod
from trading_bot.plan import (PlannedOrder, TradePlan,  # noqa: E402
                              filter_lag_governance_orders)
from lag_forensic_filter import BANNED, LAG_USER_EXCLUDED  # noqa: E402

ASOF = "2026-08-04"
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def mk_plan(specs, plan_date=ASOF):
    """specs: list (ticker, book, side). qty/ref_price cố định — gate không phụ thuộc chúng."""
    orders = [PlannedOrder(id=f"{sd.upper()}-{tk}-{i:02d}", ticker=tk, side=sd, qty=1000,
                           ref_price=20000.0, book=bk)
              for i, (tk, bk, sd) in enumerate(specs)]
    return TradePlan(plan_date=plan_date, signal_date=plan_date, strategy="test",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account="SELFCHECK")


def run(specs, plan_date=ASOF, asof=None):
    return filter_lag_governance_orders(mk_plan(specs, plan_date), asof=asof)


print("=== lag_governance_order_gate self-check ===")

# --- 1. Ca sự cố THẬT 2026-07-23: IVS vào plan LAG (đây là lý do hàm này tồn tại) ---
pl, blk = run([("IVS", "LAG", "buy")])
check("IVS lệnh MUA book LAG bị CHẶN (ca sự cố 07-23)",
      len(pl.orders) == 0 and len(blk) == 1 and blk[0]["action"] == "BLOCKED"
      and blk[0]["kind"] == "user_exclude", f"blk={blk}")
check("bản ghi chặn có order_id + qty_before + ngày quyết định (audit trail)",
      blk and blk[0]["order_id"] == "BUY-IVS-00" and blk[0]["qty_before"] == 1000
      and blk[0]["flag_date"] == "2026-07-21")

pl, blk = run([("TMG", "LAG", "buy")])
check("TMG lệnh MUA book LAG bị CHẶN", len(pl.orders) == 0 and blk[0]["kind"] == "user_exclude")

# Ca sự cố ĐẦY ĐỦ: cả 2 account trong cùng một plan-shape + một lệnh sạch đi kèm
pl, blk = run([("IVS", "LAG", "buy"), ("TRC", "LAG", "buy"), ("TMG", "LAG", "buy")])
check("plan hỗn hợp: chặn IVS+TMG, GIỮ TRC (không kêu oan)",
      [o.ticker for o in pl.orders] == ["TRC"] and len(blk) == 2)

# --- 2. Ba nguồn đều có hiệu lực ở tầng lệnh ---
pl, blk = run([("VVS", "LAG", "buy")])
check("BANNED (VVS) bị chặn ở tầng lệnh", len(pl.orders) == 0 and blk[0]["kind"] == "banned")
pl, blk = run([("BFC", "LAG", "buy")])
check("cờ forensic exclude (BFC) bị chặn ở tầng lệnh",
      len(pl.orders) == 0 and blk[0]["kind"] == "forensic")
pl, blk = run([("POW", "LAG", "buy")])
check("mã sạch (POW) KHÔNG bị chặn", len(pl.orders) == 1 and not blk)

# --- 3. PHẠM VI: chỉ lệnh MUA, chỉ book LAG ---
pl, blk = run([("IVS", "LAG", "sell")])
check("lệnh BÁN IVS book LAG KHÔNG bị chặn (thoát vị thế phải luôn đi được)",
      len(pl.orders) == 1 and not blk)
pl, blk = run([("IVS", "BAL", "buy")])
check("IVS book BAL KHÔNG bị chặn (phạm vi CHỈ LAG — không nới hộ sang book khác)",
      len(pl.orders) == 1 and not blk)
pl, blk = run([("IVS", "CAPIT", "buy"), ("IVS", "custom30V_parking", "buy")])
check("IVS book CAPIT/parking KHÔNG bị chặn (phạm vi CHỈ LAG)",
      len(pl.orders) == 2 and not blk)
pl, blk = run([("IVS", "lag", "BUY")])
check("book/side không phân biệt hoa-thường ('lag'/'BUY') vẫn chặn", len(pl.orders) == 0)
pl, blk = run([("POW", "BAL", "buy"), ("VNM", "CAPIT", "buy")])
check("plan KHÔNG có lệnh LAG buy → no-op, không gọi nguồn nào", len(pl.orders) == 2 and not blk)

# --- 4. Ngày hiệu lực: KHÔNG hồi tố (replay quá khứ không mang hindsight 07-21) ---
pl, blk = run([("IVS", "LAG", "buy")], asof="2026-07-20")
check("asof 07-20 (TRƯỚC ngày user quyết) → KHÔNG chặn IVS",
      len(pl.orders) == 1 and not blk)
pl, blk = run([("IVS", "LAG", "buy")], asof="2026-07-21")
check("asof 07-21 (ĐÚNG ngày user quyết) → chặn (biên <=)", len(pl.orders) == 0)
pl, blk = run([("VVS", "LAG", "buy")], asof="2020-01-01")
check("BANNED không phụ thuộc asof (chặn cả ở asof rất cũ)", len(pl.orders) == 0)

# asof mặc định = plan.plan_date (không đọc đồng hồ máy)
pl, blk = run([("IVS", "LAG", "buy")], plan_date="2026-07-20")
check("asof mặc định lấy từ plan.plan_date, KHÔNG từ đồng hồ hệ thống",
      len(pl.orders) == 1 and not blk)

# --- 5. Fail-mode ---
_real_deps = plan_mod._governance_gate_deps


def _boom_deps():
    raise RuntimeError("import lag_forensic_filter failed")


plan_mod._governance_gate_deps = _boom_deps
pl, blk = run([("IVS", "LAG", "buy"), ("POW", "LAG", "buy")])
check("gate không chạy được → fail-OPEN (giữ lệnh) + bản ghi FAIL_OPEN báo động",
      len(pl.orders) == 2 and len(blk) == 1 and blk[0]["action"] == "FAIL_OPEN"
      and "CẦN NGƯỜI KIỂM TRA" in blk[0]["reason"])
plan_mod._governance_gate_deps = _real_deps
pl, blk = run([("IVS", "LAG", "buy")])
check("phục hồi deps thật → chặn lại bình thường (monkeypatch không rò)",
      len(pl.orders) == 0)


def _no_csv_deps():
    """CSV forensic hỏng: 2 hằng số VẪN áp, cờ forensic thì không → FAIL_OPEN_FORENSIC."""
    real = _real_deps()

    def _wrapped(cand, asof, workdir=None, csv_path=None):
        return real(cand, asof, csv_path="/nonexistent/forensic.csv")
    return _wrapped


plan_mod._governance_gate_deps = _no_csv_deps
pl, blk = run([("IVS", "LAG", "buy"), ("VVS", "LAG", "buy"), ("POW", "LAG", "buy")])
_kinds = {b["kind"] for b in blk if b["action"] == "BLOCKED"}
check("CSV forensic hỏng → user_exclude + BANNED VẪN chặn (fail-closed tuyệt đối)",
      [o.ticker for o in pl.orders] == ["POW"] and _kinds == {"user_exclude", "banned"},
      f"orders={[o.ticker for o in pl.orders]} kinds={_kinds}")
check("CSV forensic hỏng → có bản ghi FAIL_OPEN_FORENSIC để báo to",
      any(b["action"] == "FAIL_OPEN_FORENSIC" for b in blk))
pl, blk = run([("BFC", "LAG", "buy")])
check("CSV forensic hỏng → BFC (chỉ có cờ forensic) KHÔNG bị chặn = fail-open đúng nguồn",
      len(pl.orders) == 1)
plan_mod._governance_gate_deps = _real_deps

# --- 6. Biên ---
pl, blk = run([])
check("plan rỗng → no-op", len(pl.orders) == 0 and not blk)
pl, blk = run([("IVS", "LAG", "buy"), ("IVS", "LAG", "buy")])
check("2 lệnh cùng mã bị loại → chặn CẢ HAI (không chỉ lệnh đầu)",
      len(pl.orders) == 0 and len(blk) == 2)
_p = mk_plan([("POW", "LAG", "buy")])
_n_before = len(_p.orders)
filter_lag_governance_orders(_p)
check("lệnh sạch: plan.orders không bị đổi", len(_p.orders) == _n_before)

# --- 7. Guard nối dây: bot_execute.py có thật sự gọi gate này không ---
_be = open(os.path.join(WORKDIR, "bot_execute.py"), encoding="utf-8").read()
check("bot_execute.py import filter_lag_governance_orders",
      "filter_lag_governance_orders" in _be.split("def ")[0] or
      "filter_lag_governance_orders," in _be)
check("bot_execute.py GỌI filter_lag_governance_orders(plan) trong cascade",
      "plan, gov_blocked = filter_lag_governance_orders(plan)" in _be)
check("bot_execute.py in ra CẢ 2 nhánh fail-open (không im lặng)",
      'FAIL_OPEN_FORENSIC' in _be and 'gate quản trị KHÔNG ĐẦY ĐỦ' in _be)
_i_rating = _be.find("plan, rating_blocked = filter_lag_rating_orders(plan)")
_i_gov = _be.find("plan, gov_blocked = filter_lag_governance_orders(plan)")
_i_appr = _be.find("apply_capit_lever(plan")
check("thứ tự cascade: rating → governance → lever",
      0 < _i_rating < _i_gov < _i_appr, f"{_i_rating}/{_i_gov}/{_i_appr}")

# --- 8. Không nhân bản nguồn: hàm phải DÙNG LẠI gate tầng tín hiệu ---
_pl_src = open(os.path.join(WORKDIR, "trading_bot", "plan.py"), encoding="utf-8").read()
_fn = _pl_src.split("def filter_lag_governance_orders")[1].split("\n# ──")[0]
# Chỉ xét THÂN HÀM (sau docstring) — docstring CÓ quyền nhắc IVS vì nó kể lại ca sự cố 07-23;
# điều phải cấm là một danh sách mã khai LẠI trong code (nguồn thứ hai sẽ trôi lệch âm thầm).
_body = _fn.split('"""')[2] if _fn.count('"""') >= 2 else _fn
# … và bỏ luôn mọi CHUỖI trong thân hàm: nhắc tên nguồn trong thông điệp log là ĐÚNG (người đọc
# log cần biết nguồn nào vẫn áp khi CSV hỏng), chỉ khai lại DỮ LIỆU mới là lỗi.
_code = re.sub(r'(?s)f?"(?:[^"\\]|\\.)*"|f?\'(?:[^\'\\]|\\.)*\'', '""', _body)
check("THÂN HÀM (bỏ chuỗi) KHÔNG khai lại danh sách BANNED/IVS/TMG (dùng lại nguồn tầng tín hiệu)",
      not any(t in _code for t in ("IVS", "TMG", "frozenset", "LAG_USER_EXCLUDED", "BANNED")),
      f"thân hàm {len(_body)} ký tự, sau khi bỏ chuỗi {len(_code)}")
check("_governance_gate_deps import từ lag_forensic_filter (một nguồn duy nhất)",
      "from lag_forensic_filter import lag_filter_forensic_banned" in _pl_src)

# --- 9. (--live) REPLAY plan THẬT ---
# ⚠️ KHÔNG assert "gate chặn được IVS trên plan thật": ĐO ĐƯỢC 2026-08-04 rằng KHÔNG plan nào
# trên đĩa còn chứa lệnh IVS/TMG. `plan_SpaceX_2026-07-23.json` — chính artifact của sự cố — đã
# bị GHI LẠI (`regenerated_note`, `orders: []`); IVS chỉ còn sống trong `lag_upcoming_notes`
# (`effective_buy_vnd: 18000000`, ref 6.200đ). Đây đúng hiện tượng re-plan-ghi-đè mà việc A2 đã
# nêu. ⇒ Ca sự cố được replay bằng đơn hàng DỰNG LẠI từ chính các field note đó (phần 9b), còn
# phần 9a chỉ dùng plan thật cho việc nó CHỨNG MINH ĐƯỢC: gate không đổi lệnh nào đang chạy tốt.
if "--live" in sys.argv:
    print("--- live: replay plan THẬT ---")
    import glob
    import json

    n_plan = n_ivs_blocked = n_other_changed = 0
    _pat = os.path.join(WORKDIR, "data", "trade_plans", "plan_*_2026-0[78]-*.json")
    _files = sorted(glob.glob(_pat))
    # Nếu glob không khớp file nào thì mọi assert dưới sẽ "pass vì không tìm thấy gì" — đúng
    # cái bẫy mà skill verify-before-done nêu. Chặn ngay tại đây.
    check(f"tìm được file plan THẬT để replay ({len(_files)} file)", len(_files) >= 10,
          f"pattern={_pat}")
    for fp in _files:
        try:
            raw = json.load(open(fp, encoding="utf-8"))
        except Exception:
            continue
        specs = [(o.get("ticker"), o.get("book") or "", o.get("side") or "")
                 for o in (raw.get("orders") or [])]
        if not specs:
            continue
        n_plan += 1
        pdate = str(raw.get("plan_date") or "")[:10] or ASOF
        pl, blk = run(specs, plan_date=pdate)
        for b in blk:
            if b["action"] != "BLOCKED":
                continue
            if b["ticker"] in LAG_USER_EXCLUDED:
                n_ivs_blocked += 1
                print(f"    {os.path.basename(fp)}: CHẶN {b['ticker']} "
                      f"({b['qty_before']:,} cp, {b['kind']})")
            else:
                n_other_changed += 1
                print(f"    {os.path.basename(fp)}: chặn mã KHÁC {b['ticker']} ({b['kind']})")
    # Bằng chứng hồi quy CHÍNH của phần live: gate KHÔNG đổi một lệnh nào trên plan thật đang
    # chạy tốt (cùng mẫu bằng chứng mà gate rating P1 đã dùng: "0 lệnh khác đổi trên 21 plan").
    check(f"replay {n_plan} plan THẬT có lệnh: 0 lệnh bị đổi ngoài ý muốn",
          n_other_changed == 0 and n_ivs_blocked == 0,
          f"n_ivs_blocked={n_ivs_blocked} n_other_changed={n_other_changed}")
    print(f"    ({n_plan} plan có lệnh; 0 lệnh bị chặn — đúng kỳ vọng: không plan nào trên đĩa "
          f"còn chứa lệnh IVS/TMG/BANNED/forensic)")

    # --- 9b. Dựng lại ĐÚNG đơn hàng của sự cố 07-23 từ chính field note của plan thật ---
    _fp23 = os.path.join(WORKDIR, "data", "trade_plans", "plan_SpaceX_2026-07-23.json")
    _r23 = json.load(open(_fp23, encoding="utf-8"))
    _note = ((_r23.get("lag_upcoming_notes") or {}).get("entry_07_24") or {}).get("IVS") or {}
    check("plan 07-23 thật: xác nhận artifact đã bị ghi lại (orders rỗng, IVS chỉ còn trong note)",
          not (_r23.get("orders") or []) and _note.get("type") == "LAG_HI"
          and "regenerated_note" in _r23,
          f"note={_note}")
    # qty dựng từ số tiền + giá tham chiếu THẬT trong note (18.000.000đ @ 6.200đ ≈ 2.903cp);
    # KHÔNG bịa số — nếu note đổi thì con số này đổi theo.
    _buy_vnd = float(_note.get("effective_buy_vnd") or 0)
    check("note 07-23 có effective_buy_vnd của IVS (số tiền THẬT định mua)", _buy_vnd > 0,
          f"effective_buy_vnd={_buy_vnd}")
    _qty = int(_buy_vnd // 6200)
    _p23 = mk_plan([("IVS", "LAG", "buy")], plan_date="2026-07-24")
    _p23.orders[0].qty = _qty
    _p23, _b23 = filter_lag_governance_orders(_p23)
    check(f"REPLAY sự cố: lệnh MUA IVS {_qty:,}cp (≈{_buy_vnd/1e6:.0f}M) ngày 07-24 bị CHẶN",
          len(_p23.orders) == 0 and len(_b23) == 1
          and _b23[0]["kind"] == "user_exclude" and _b23[0]["qty_before"] == _qty,
          f"blk={_b23}")
    # Hai account như sự cố ghi lại (SpaceX 1800cp + ZaloPay 2750cp) — nguồn:
    # mike/kb/context_planning_mini.md §"LAG entry EXCLUDE list".
    for _acct, _q in (("SpaceX", 1800), ("ZaloPay", 2750)):
        _pp = mk_plan([("IVS", "LAG", "buy")], plan_date="2026-07-24")
        _pp.orders[0].qty = _q
        _pp.account = _acct
        _pp, _bb = filter_lag_governance_orders(_pp)
        check(f"REPLAY sự cố {_acct}: IVS {_q:,}cp bị CHẶN",
              len(_pp.orders) == 0 and _bb[0]["kind"] == "user_exclude")

print(f"\n=== {PASS} PASS / {FAIL} FAIL ===")
sys.exit(1 if FAIL else 0)
