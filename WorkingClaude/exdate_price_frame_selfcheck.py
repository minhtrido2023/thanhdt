#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho cổng GDKHQ (ngày giao dịch không hưởng quyền) — D1/D2/D3.

Thiết kế: `mike/agents/Taylor/research/exdate_order_pipeline_20260815/README.md` §8-§9.
Code: `trading_bot/price_frame.py` (D1), `trading_bot/exdate_gate.py` (D2), 3 chỗ D3.

HAI CA CHỨNG MINH NGƯỢC (README §9.1) là lý do file này tồn tại — chúng KHÔNG phải test tổng
hợp mà là **hai sự cố có thật, dựng lại từ artifact nguyên bản trên đĩa**:

  A. Bản đọc `positions` của ZaloPay lúc **2026-08-14T19:10:23** (BID, ex-right 08-17): hai lô
     cùng mã, cùng một bản đọc, hai `marketPrice` khác nhau (35.800 gói vay 1826 / 38.850 gói
     1258). Yêu cầu: **G4 CHẶN**. Trước bản vá, không cổng nào thấy gì.
  B. `plan_main_2026-08-11.json` (`created_at` 08-52 SÁNG ngày GDKHQ) mang `ref_price = 24.250`
     trong khi giá tham chiếu chính thức là **20.200**. Yêu cầu: cổng mới BẮT ĐƯỢC, không cho
     qua. Trước bản vá, plan này chạy thẳng.

Cả hai fixture ĐÓNG BĂNG trong file này (§23 coding_guidelines: selfcheck không được assert
lên trạng thái SỐNG). Chạy được không cần DNSE, không cần BigQuery, không cần mạng.

Chạy: `python3 exdate_price_frame_selfcheck.py`   (exit 0 = PASS)
"""
import os
import subprocess
import sys
import tempfile

WC_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC_ROOT)
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")          # §5b coding_guidelines

from trading_bot import price_frame as pf                          # noqa: E402
from trading_bot.exdate_gate import apply_exdate_gate              # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan               # noqa: E402
from trading_bot import gdkhq_rollout                              # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


# ══════════════════════════════════════════════════════════════════════════════════════
# FIXTURE — artifact THẬT, chép nguyên văn, không sửa một ký tự nào của giá trị
# ══════════════════════════════════════════════════════════════════════════════════════

# `data/execution_logs/dnse_raw_2026-08-14.jsonl`, kind=positions, ts=2026-08-14T19:10:23,
# account ZaloPay (0001743768). Đây là bản đọc bắt được DNSE ĐANG GIỮA cú lật hệ quy chiếu.
BID_LOTS_191023 = [
    {"id": 2766555, "marketType": "STOCK", "symbol": "BID", "accountNo": "0001743768",
     "status": "OPEN", "loanPackageId": 1826, "side": "NB", "accumulateQuantity": 107,
     "tradeQuantity": 100, "closedQuantity": 0, "openQuantity": 107,
     "costPrice": 36962.6168, "marketPrice": 35800, "breakEvenPrice": 37071.7987},
    {"id": 2697547, "marketType": "STOCK", "symbol": "BID", "accountNo": "0001743768",
     "status": "OPEN", "loanPackageId": 1258, "side": "NB", "accumulateQuantity": 900,
     "tradeQuantity": 300, "closedQuantity": 600, "openQuantity": 300,
     "costPrice": 40316.6667, "marketPrice": 38850, "breakEvenPrice": 40436.1693},
]
# Bản đọc SAU cú lật (08-14 20:15 trở đi) — cùng mã, cùng account, đã đồng hệ.
BID_LOTS_AFTER = [
    dict(BID_LOTS_191023[0]),
    dict(BID_LOTS_191023[1], marketPrice=35800, openQuantity=320),
]

# `tav2_bq.corporate_action`, đọc 2026-08-15. Giữ nguyên `event_status` để ca "announced"
# là ca THẬT chứ không phải dựng lên.
EV_BID_0817 = {"ticker": "BID", "event_code": "ISS", "exright_date": "2026-08-17",
               "event_status": "announced", "value_per_share": None, "exercise_ratio": 0.068433,
               "issue_method_name_vi": "Cổ phiếu thưởng"}
EV_SSI_0817_DIV = {"ticker": "SSI", "event_code": "DIV", "exright_date": "2026-08-17",
                   "event_status": "announced", "value_per_share": 1000.0,
                   "exercise_ratio": 0.1, "issue_method_name_vi": None}
EV_SSI_0817_ISS = {"ticker": "SSI", "event_code": "ISS", "exright_date": "2026-08-17",
                   "event_status": "announced", "value_per_share": None, "exercise_ratio": 0.2,
                   "issue_method_name_vi": "Cổ phiếu thưởng"}
EV_MBB_0811_ISS = {"ticker": "MBB", "event_code": "ISS", "exright_date": "2026-08-11",
                   "event_status": "executed", "value_per_share": None, "exercise_ratio": 0.15,
                   "issue_method_name_vi": "Trả Cổ tức bằng Cổ phiếu"}
EV_MBB_0811_RIGHTS = {"ticker": "MBB", "event_code": "ISS", "exright_date": "2026-08-11",
                      "event_status": "executed", "value_per_share": None, "exercise_ratio": 0.1,
                      "issue_method_name_vi": "Quyền mua CP cho Cổ đông hiện hữu"}
EV_VHM_0806 = {"ticker": "VHM", "event_code": "ISS", "exright_date": "2026-08-06",
               "event_status": "executed", "value_per_share": None, "exercise_ratio": 1.0,
               "issue_method_name_vi": "Trả Cổ tức bằng Cổ phiếu"}
EV_ACB_0615_DIV = {"ticker": "ACB", "event_code": "DIV", "exright_date": "2026-06-15",
                   "event_status": "executed", "value_per_share": 700.0, "exercise_ratio": 0.07,
                   "issue_method_name_vi": None}
EV_ACB_0615_ISS = {"ticker": "ACB", "event_code": "ISS", "exright_date": "2026-06-15",
                   "event_status": "executed", "value_per_share": None, "exercise_ratio": 0.13,
                   "issue_method_name_vi": "Trả Cổ tức bằng Cổ phiếu"}
EV_MBS_0817 = {"ticker": "MBS", "event_code": "DIV", "exright_date": "2026-08-17",
               "event_status": "announced", "value_per_share": 1000.0, "exercise_ratio": 0.1,
               "issue_method_name_vi": None}
# ESOP — KHÔNG điều chỉnh giá (ca thật HAH 2026-07-28, corp_action_lib docstring).
EV_HAH_ESOP = {"ticker": "HAH", "event_code": "ISS", "exright_date": "2026-07-28",
               "event_status": "executed", "value_per_share": None, "exercise_ratio": 0.0186,
               "issue_method_name_vi": "Phát hành cho CBCNV"}


class FakeQuote:
    def __init__(self, ref, exchange="HOSE", band=0.07, known=True):
        self.ref, self.exchange, self.exchange_known = ref, exchange, known
        self.ceiling = round(ref * (1 + band))
        self.floor = round(ref * (1 - band))

    def ok(self):
        return True


class FakeBroker:
    """Broker tất định: quote + positions RAW + cum_prices (offline thay BQ)."""

    def __init__(self, quotes=None, rows=None, cum=None):
        self.quotes, self.rows, self.cum = quotes or {}, rows or [], cum or {}
        self.cum_prices = self.cum
        self.client = self

    def get_quote(self, tk):
        return self.quotes.get(tk)

    def positions_raw(self):
        return list(self.rows)


print("── 0. p_cum = tav2_bq.ticker.Price thô của phiên cum cuối (BID 08-14 = 38.250đ) ──")
got, info = pf.p_cum_from_broker(FakeBroker(cum={"BID": 38_250}), "BID", "2026-08-17")
check("BID phiên cum 08-14 trả 38.250đ — KHÔNG phải Close 35.800đ đã điều chỉnh",
      got == 38_250, f"got={got}, info={info}")
got_missing, info_missing = pf.p_cum_from_broker(FakeBroker(cum={}), "BID", "2026-08-17")
check("thiếu dữ liệu phiên cum ⇒ fail-closed như cũ", got_missing is None,
      info_missing["reason"][:80])
got_bq, info_bq = pf.p_cum_from_bq(
    "BID", "2026-08-17",
    bq_query=lambda sql: [{"d": "2026-08-14", "px": 38_250.0}])
check("đường BQ thật đọc đúng 1 dòng Price thô trước exright_date", got_bq == 38_250,
      f"got={got_bq}, info={info_bq}")
got_bad, info_bad = pf.p_cum_from_bq(
    "BID", "2026-08-17", bq_query=lambda sql: [{"d": "2026-08-17", "px": 35_900.0}])
check("BQ trả dòng đúng ngày GDKHQ ⇒ fail-closed, không lấy hệ mới", got_bad is None,
      info_bad["reason"][:80])


# ══════════════════════════════════════════════════════════════════════════════════════
print("── 1. Công thức sở giao dịch (G5) — 5 ca thật, hai loại sự kiện, khớp độc lập ──")
# ══════════════════════════════════════════════════════════════════════════════════════
for name, p_cum, evs, want, sym in (
        ("MBB 08-11 (CP 15% + quyền mua 10:1 @10.000) = ảnh chụp app DNSE",
         24_250, [EV_MBB_0811_ISS, EV_MBB_0811_RIGHTS], 20_200, "MBB"),
        ("SSI 08-17 (tiền 1.000 + thưởng 20%)", 24_500, [EV_SSI_0817_DIV, EV_SSI_0817_ISS],
         19_583.33, "SSI"),
        ("BID 08-17 (thưởng 6,8433%)", 38_250, [EV_BID_0817], 35_800.3, "BID"),
        ("VHM 08-06 (cổ tức CP 100%) — dịch −50,0%", 153_000, [EV_VHM_0806], 76_500, "VHM"),
        ("ACB 06-15 (tiền 700 + CP 13%) — gộp cùng ngày", 26_500,
         [EV_ACB_0615_DIV, EV_ACB_0615_ISS], 22_831.86, "ACB")):
    got, info = pf.expected_reference_price(p_cum, evs, symbol=sym)
    check(name, got is not None and abs(got - want) < 1.0,
          f"kỳ vọng {want:,.2f} — nhận {got if got is None else f'{got:,.2f}'}")

ok, info = pf.check_ref_vs_events(19_600, 24_500, [EV_SSI_0817_DIV, EV_SSI_0817_ISS],
                                  symbol="SSI")
check("G5 nuốt đúng chênh lệch làm tròn bước giá (SSI: q.ref 19.600 vs công thức 19.583)",
      ok, info["reason"][:90])
ok, _ = pf.check_ref_vs_events(24_500, 24_500, [EV_SSI_0817_DIV, EV_SSI_0817_ISS], symbol="SSI")
check("G5 CHẶN giá hệ CŨ (SSI 24.500 = giá đóng cum, lệch +25,1%)", not ok)
ok, _ = pf.check_ref_vs_events(35_800, 38_250, [EV_BID_0817], symbol="BID")
check("G5 chấp nhận BID 35.800 (đúng hệ mới)", ok)
ok, _ = pf.check_ref_vs_events(38_850, 38_250, [EV_BID_0817], symbol="BID")
check("G5 CHẶN BID 38.850 (giá hệ cũ, đúng con số lô 1258 mang lúc 19:10:23)", not ok)

# Quyền mua thiếu giá phát hành ⇒ FAIL-CLOSED, không coi như 0 (README §4 cảnh báo)
adj, info = pf.adjustment([dict(EV_MBB_0811_RIGHTS, ticker="XYZ", exright_date="2027-01-05")])
check("quyền mua KHÔNG có giá phát hành trong sổ tay ⇒ fail-closed, KHÔNG coi như 0",
      adj is None and "FAIL-CLOSED" in info["reason"], info["reason"][:80])

# ══════════════════════════════════════════════════════════════════════════════════════
print("\n── 2. CA CHỨNG MINH NGƯỢC A — bản đọc positions BID 2026-08-14T19:10:23 ──")
# ══════════════════════════════════════════════════════════════════════════════════════
ok, info = pf.check_same_frame(BID_LOTS_191023, "BID")
check("G4 CHẶN bản đọc trộn hai hệ quy chiếu (35.800 gói 1826 vs 38.850 gói 1258)",
      not ok, info["reason"][:110])
check("G4 nêu ĐÍCH DANH cả hai giá để người đọc log tái lập được kết luận",
      info.get("distinct_market_prices") == [35800.0, 38850.0],
      str(info.get("distinct_market_prices")))
ok_after, info_after = pf.check_same_frame(BID_LOTS_AFTER, "BID")
check("G4 KHÔNG chặn bản đọc sau cú lật (cùng 35.800, 20:15 trở đi) — không phải cổng mù quáng",
      ok_after, info_after["reason"][:70])
check("G4 no-op khi mã chưa nắm giữ (lệnh MUA mới, ca THƯỜNG)",
      pf.check_same_frame(BID_LOTS_191023, "FPT")[0])

# Cổng đầy đủ trên đúng bản đọc đó: phải dừng ở G4, KHÔNG được lọt xuống G5 rồi đi tiếp
br = FakeBroker(quotes={"BID": FakeQuote(35_800)}, rows=BID_LOTS_191023, cum={"BID": 38_250})
emap = pf.events_by_ticker_date([EV_BID_0817])
res = pf.resolve_reference(br, "BID", "2026-08-17", events_map=emap)
check("resolve_reference() dừng ở G4 trên đúng bản đọc 19:10:23 (dù q.ref đã đúng hệ mới)",
      res["ok"] is False and res["gate"] == "G4", f"gate={res['gate']}")
res_ok = pf.resolve_reference(br, "BID", "2026-08-17", events_map=emap,
                              position_rows=BID_LOTS_AFTER)
check("resolve_reference() CHO QUA khi cả 5 cổng sạch (bản đọc sau lật + q.ref 35.800)",
      res_ok["ok"] is True and res_ok["ex_today"] is True, res_ok["reason"][:80])
check("share_factor trả về đúng hệ số nhân số CP của sự kiện (BID ×1,068433)",
      abs((res_ok.get("share_factor") or 0) - 1.068433) < 1e-6, str(res_ok.get("share_factor")))

# ══════════════════════════════════════════════════════════════════════════════════════
print("\n── 3. CA CHỨNG MINH NGƯỢC B — plan_main_2026-08-11 (ref 24.250, đúng 20.200) ──")
# ══════════════════════════════════════════════════════════════════════════════════════
MBB_EVENTS = [EV_MBB_0811_ISS, EV_MBB_0811_RIGHTS]
emap_mbb = pf.events_by_ticker_date(MBB_EVENTS)


def plan_main_0811():
    """Dựng lại NGUYÊN VĂN hai lệnh MBB của `data/trade_plans/plan_main_2026-08-11.json`."""
    return TradePlan(
        plan_date="2026-08-11", signal_date="2026-08-10", strategy="paper_probe",
        strategy_version="1.1", state=-1, state_name="PROBE", account="main",
        nav_basis={}, orders=[
            PlannedOrder(id="SELL-MBB-04", ticker="MBB", side="sell", qty=1200,
                         ref_price=24250.0, book="PROBE", play_type="churn", priority=1),
            PlannedOrder(id="BUY-MBB-01", ticker="MBB", side="buy", qty=1300,
                         ref_price=24250.0, book="PROBE", play_type="churn", priority=5)])


br_mbb = FakeBroker(quotes={"MBB": FakeQuote(20_200)}, rows=[], cum={"MBB": 24_250})
plan, adj = apply_exdate_gate(plan_main_0811(), br_mbb, "2026-08-11", events_map=emap_mbb)
buys = [o for o in plan.orders if o.side == "buy"]
sells = [o for o in plan.orders if o.side == "sell"]
check("cổng BẮT ĐƯỢC ref_price 24.250 sai hệ và KHÔNG cho qua nguyên trạng",
      not any(o.ref_price == 24250.0 for o in plan.orders),
      f"còn lại: {[(o.id, o.ref_price) for o in plan.orders]}")
check("lệnh MUA được quy về giá tham chiếu chính thức 20.200",
      len(buys) == 1 and buys[0].ref_price == 20_200.0)
check("qty MUA tính lại giữ nguyên GIÁ TRỊ (1.300×24.250 = 31,525tr → 1.500cp @20.200)",
      len(buys) == 1 and buys[0].qty == 1500,
      f"qty={buys[0].qty if buys else None} (giá trị {1300 * 24250:,}đ → {1500 * 20200:,}đ)")
check("lệnh BÁN bị BỎ (sự kiện NHÂN số CP ×1,25 — cơ chế 'bán ảo' README §2)",
      not sells and any(a["action"] == "BLOCKED" and a.get("side") == "sell" for a in adj))
check("lý do BỎ được ghi vào plan.notes[] (người duyệt đọc được, không im lặng)",
      any("GDKHQ" in str(n) for n in (plan.notes or [])))

# Plan ĐÃ đứng sẵn ở hệ mới (ca thật MBB 08-11 của SpaceX/ZaloPay: ref 20.200) ⇒ NO-OP
plan_ok = TradePlan(plan_date="2026-08-11", signal_date="2026-08-10", strategy="V2.4",
                    strategy_version="1", state=3, state_name="NEUTRAL", account="SpaceX",
                    nav_basis={}, orders=[
                        PlannedOrder(id="BUY-MBB-01", ticker="MBB", side="buy", qty=300,
                                     ref_price=20200.0, book="LAG", priority=5)])
_, adj_ok = apply_exdate_gate(plan_ok, br_mbb, "2026-08-11", events_map=emap_mbb)
check("plan ĐÃ đúng hệ (ca thật 08-11: ref 20.200) ⇒ cổng KHÔNG đổi gì",
      not [a for a in adj_ok if a["action"] in ("REPRICED", "BLOCKED")],
      f"adjustments={[a['action'] for a in adj_ok]}")

# ══════════════════════════════════════════════════════════════════════════════════════
print("\n── 4. Bất biến 'KHÔNG đổi hành vi ngày THƯỜNG' ──")
# ══════════════════════════════════════════════════════════════════════════════════════
plan_norm = TradePlan(plan_date="2026-08-12", signal_date="2026-08-11", strategy="V2.4",
                      strategy_version="1", state=3, state_name="NEUTRAL", account="SpaceX",
                      nav_basis={}, orders=[
                          PlannedOrder(id="BUY-FPT-01", ticker="FPT", side="buy", qty=500,
                                       ref_price=73200.0, book="BAL", priority=5),
                          PlannedOrder(id="SELL-VNM-01", ticker="VNM", side="sell", qty=800,
                                       ref_price=54600.0, book="LAG", priority=1)])
snap = [(o.id, o.ticker, o.side, o.qty, o.ref_price) for o in plan_norm.orders]


class ExplodingBroker:
    """Ngày thường cổng KHÔNG được chạm broker — bất kỳ lời gọi nào cũng là lỗi thiết kế."""

    def __getattr__(self, name):
        raise AssertionError(f"cổng GDKHQ gọi broker.{name}() trong NGÀY THƯỜNG")


plan_norm, adj_norm = apply_exdate_gate(plan_norm, ExplodingBroker(), "2026-08-12",
                                        events_map=pf.events_by_ticker_date([]))
check("ngày không có sự kiện: 0 lệnh bị sửa, 0 lệnh bị bỏ",
      [(o.id, o.ticker, o.side, o.qty, o.ref_price) for o in plan_norm.orders] == snap)
check("ngày không có sự kiện: KHÔNG một lời gọi broker nào (không thêm chi phí/rủi ro)",
      [a["action"] for a in adj_norm] == ["NO_EVENT"])

# Sự kiện của mã KHÁC trong cùng plan không được ảnh hưởng mã lành
plan_mix = TradePlan(plan_date="2026-08-11", signal_date="2026-08-10", strategy="V2.4",
                     strategy_version="1", state=3, state_name="NEUTRAL", account="SpaceX",
                     nav_basis={}, orders=[
                         PlannedOrder(id="BUY-FPT-01", ticker="FPT", side="buy", qty=500,
                                      ref_price=73200.0, book="BAL", priority=5),
                         PlannedOrder(id="BUY-MBB-01", ticker="MBB", side="buy", qty=1300,
                                      ref_price=24250.0, book="LAG", priority=5)])
plan_mix, _ = apply_exdate_gate(plan_mix, br_mbb, "2026-08-11", events_map=emap_mbb)
fpt = [o for o in plan_mix.orders if o.ticker == "FPT"]
check("mã KHÔNG có sự kiện trong cùng plan giữ nguyên tuyệt đối",
      len(fpt) == 1 and fpt[0].qty == 500 and fpt[0].ref_price == 73200.0)

# ESOP không điều chỉnh giá ⇒ không được coi là ngày GDKHQ
check("ESOP (ca thật HAH 07-28) KHÔNG bị coi là sự kiện làm đổi giá",
      not pf.events_on(pf.events_by_ticker_date(
          [EV_HAH_ESOP] if __import__("corp_action_lib").is_price_adjusting(EV_HAH_ESOP) else []),
          "HAH", "2026-07-28"))

# ══════════════════════════════════════════════════════════════════════════════════════
print("\n── 5. Trần giá mua quy về hệ mới (D2 mục 3+4) ──")
# ══════════════════════════════════════════════════════════════════════════════════════
# Luật A: anchor 24.250 (hệ cũ) × 1,03 = 24.977 — CAO HƠN CẢ giá trần hợp lệ của phiên
# (20.200 × 1,07 = 21.614) ⇒ luật A bị vô hiệu hoá im lặng nếu không neo lại.
o_a = PlannedOrder(id="BUY-MBB-A", ticker="MBB", side="buy", qty=1300, ref_price=24250.0,
                   book="LAG", priority=5, hard_no_chase_ceiling_vnd=24977.0,
                   ceiling_rule="A", ceiling_anchor_price=24250.0,
                   ceiling_anchor_date="2026-08-10", ceiling_tau=0.03)
plan_a = TradePlan(plan_date="2026-08-11", signal_date="2026-08-10", strategy="V2.4",
                   strategy_version="1", state=3, state_name="NEUTRAL", account="SpaceX",
                   nav_basis={}, orders=[o_a])
plan_a, adj_a = apply_exdate_gate(plan_a, br_mbb, "2026-08-11", events_map=emap_mbb)
check("trần luật A neo lại vào giá tham chiếu phiên GDKHQ (24.977 → 20.806 = 20.200×1,03)",
      plan_a.orders and plan_a.orders[0].hard_no_chase_ceiling_vnd == 20_806.0,
      str(plan_a.orders[0].hard_no_chase_ceiling_vnd if plan_a.orders else None))
check("provenance đi cùng: ceiling_anchor_price cũng chuyển sang hệ mới (bất biến #3 còn tái lập được)",
      plan_a.orders and plan_a.orders[0].ceiling_anchor_price == 20_200.0)
check("trần MỚI thấp hơn giá trần hợp lệ của phiên (luật A trở lại là ràng buộc THẬT)",
      plan_a.orders and plan_a.orders[0].hard_no_chase_ceiling_vnd < 20_200 * 1.07)

# Trần LỊCH SỬ không khai luật A ⇒ quy đổi theo hệ số của chính sự kiện
o_l = PlannedOrder(id="BUY-MBB-L", ticker="MBB", side="buy", qty=1300, ref_price=24250.0,
                   book="LAG", priority=5, hard_no_chase_ceiling_vnd=24500.0)
plan_l = TradePlan(plan_date="2026-08-11", signal_date="2026-08-10", strategy="V2.4",
                   strategy_version="1", state=3, state_name="NEUTRAL", account="SpaceX",
                   nav_basis={}, orders=[o_l])
plan_l, _ = apply_exdate_gate(plan_l, br_mbb, "2026-08-11", events_map=emap_mbb)
want_l = float(int(24500.0 * (20200.0 / 24250.0)))
check("trần lịch sử (không phải luật A) quy đổi bằng hệ số sự kiện, KHÔNG bị dựng thành luật A",
      plan_l.orders and plan_l.orders[0].hard_no_chase_ceiling_vnd == want_l
      and plan_l.orders[0].ceiling_rule is None,
      f"{plan_l.orders[0].hard_no_chase_ceiling_vnd if plan_l.orders else None} (kỳ vọng {want_l})")

# ══════════════════════════════════════════════════════════════════════════════════════
print("\n── 6. Fail-closed: mọi hướng thiếu dữ liệu đều KHÔNG sinh lệnh ──")
# ══════════════════════════════════════════════════════════════════════════════════════
cases = [
    ("quote câm (không có q.ref)",
     FakeBroker(quotes={"MBB": None}, rows=[], cum={"MBB": 24_250})),
    ("không xác định được SÀN (G1 — Quote mặc định 'HOSE' khi feed câm)",
     FakeBroker(quotes={"MBB": FakeQuote(20_200, known=False)}, rows=[], cum={"MBB": 24_250})),
    ("biên độ trần/sàn không khớp sàn (G2 — snapshot trộn hai phiên)",
     FakeBroker(quotes={"MBB": FakeQuote(20_200, band=0.15)}, rows=[], cum={"MBB": 24_250})),
    ("không lấy được giá phiên cum cuối (G5 mất vế đối soát)",
     FakeBroker(quotes={"MBB": FakeQuote(20_200)}, rows=[], cum={})),
    ("q.ref đứng ở hệ CŨ 24.250 (G5 bắt được — chính ca plan_main)",
     FakeBroker(quotes={"MBB": FakeQuote(24_250)}, rows=[], cum={"MBB": 24_250})),
]
for name, b in cases:
    pl = TradePlan(plan_date="2026-08-11", signal_date="2026-08-10", strategy="V2.4",
                   strategy_version="1", state=3, state_name="NEUTRAL", account="SpaceX",
                   nav_basis={}, orders=[
                       PlannedOrder(id="BUY-MBB-01", ticker="MBB", side="buy", qty=1300,
                                    ref_price=24250.0, book="LAG", priority=5)])
    pl, ad = apply_exdate_gate(pl, b, "2026-08-11", events_map=emap_mbb)
    check(f"fail-closed: {name}", not pl.orders and any(a["action"] == "BLOCKED" for a in ad),
          (ad[0].get("gate") if ad else "?"))


def boom_resolver(*a, **k):
    raise RuntimeError("feed sập giữa chừng")


pl = TradePlan(plan_date="2026-08-11", signal_date="2026-08-10", strategy="V2.4",
               strategy_version="1", state=3, state_name="NEUTRAL", account="SpaceX",
               nav_basis={}, orders=[PlannedOrder(id="B", ticker="MBB", side="buy", qty=100,
                                                  ref_price=24250.0, book="LAG", priority=5)])
pl, ad = apply_exdate_gate(pl, br_mbb, "2026-08-11", events_map=emap_mbb, resolver=boom_resolver)
check("resolver NỔ ⇒ vẫn fail-closed (không có nhánh nào để ngoại lệ chui qua)",
      not pl.orders and ad and ad[0]["action"] == "BLOCKED")

# ══════════════════════════════════════════════════════════════════════════════════════
print("\n── 7. Bẫy `event_status` — `announced` PHẢI được tính, `not_executed` thì không ──")
# ══════════════════════════════════════════════════════════════════════════════════════
import corp_action_lib as cal                                       # noqa: E402
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "corp_action_lib.py"), encoding="utf-8").read()
check("pricing_events() lọc `!= not_executed`, KHÔNG phải `== executed`",
      'event_status != "not_executed"' in src and hasattr(cal, "pricing_events"))
check("events() cũ giữ NGUYÊN semantics `== executed` (3 caller cũ không đổi hành vi)",
      'event_status = "executed"' in src)
check("BID 08-17 ở trạng thái `announced` vẫn được cổng nhìn thấy (ca THẬT, đúng ngày cần nó)",
      bool(pf.events_on(pf.events_by_ticker_date([EV_BID_0817]), "BID", "2026-08-17")))
check("cửa sổ sự kiện phủ được cả khe CUỐI TUẦN T-1(T6 08-14) → T(T2 08-17) = 3 ngày lịch",
      pf.has_event_in_window(pf.events_by_ticker_date([EV_BID_0817]), "BID", "2026-08-14")[0]
      and pf.has_event_in_window(pf.events_by_ticker_date([EV_BID_0817]), "BID", "2026-08-17")[0]
      and not pf.has_event_in_window(pf.events_by_ticker_date([EV_BID_0817]),
                                     "BID", "2026-08-01")[0])

# ══════════════════════════════════════════════════════════════════════════════════════
print("\n── 8. D3 — ba chỗ đã đóng, kiểm bằng HÀNH VI chứ không phải bằng grep ──")
# ══════════════════════════════════════════════════════════════════════════════════════
from trading_bot.strategies import V23Strategy                      # noqa: E402


class DumbQuoteBroker:
    def get_quote(self, tk):
        class Q:
            ref = last = None

            def ok(self):
                return False
        return Q()


s = V23Strategy.__new__(V23Strategy)
notes = []
px = V23Strategy._price(s, DumbQuoteBroker(), "MBB", 24250.0, notes, ex_tickers={"MBB"})
check("D3#1 strategies._price(): quote câm + GDKHQ ⇒ TỪ CHỐI fallback `recs_close` hệ cũ",
      px is None and any("TỪ CHỐI fallback" in n for n in notes))
px2 = V23Strategy._price(s, DumbQuoteBroker(), "FPT", 73200.0, [], ex_tickers={"MBB"})
check("D3#1 ngày thường/mã thường: fallback `recs_close` GIỮ NGUYÊN hành vi cũ", px2 == 73200.0)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mike", "bin"))
import merge_park_orders as mpo                                     # noqa: E402

BASE_PLAN = {"plan_date": "2026-08-17", "account": "SpaceX", "orders": []}
# L1 chạy 19:04:15 (hệ CŨ 38.850), L2 chạy 19:40 (hệ MỚI 35.800) — ĐÚNG hai bên cú lật
# 19:10:23 đã xảy ra thật ngày 2026-08-14. Hôm đó L1 ra 0 lệnh nên không thiệt hại; ở đây
# dựng lại đúng tình huống đó với L1 CÓ lệnh, tức ca sát sạt đã không xảy ra.
L1 = {"account": "SpaceX", "plan_date": "2026-08-17", "generated_at": "2026-08-14T19:04:15",
      "decision": "TRIM", "reconcile_ok": True,
      "orders": [{"ticker": "BID", "side": "sell", "qty": 300, "ref_price": 38850,
                  "sellable": 427, "play_type": "PARK_TRIM"}]}
L2 = {"account": "SpaceX", "plan_date": "2026-08-17", "generated_at": "2026-08-14T19:40:00",
      "decision": "JIT", "reconcile_ok": True,
      "orders": [{"ticker": "BID", "side": "sell", "qty": 100, "ref_price": 35800,
                  "sellable": 427, "play_type": "JIT_UNPARK"}]}
_, rep = mpo.merge_park_orders(dict(BASE_PLAN), L1, L2,
                               ex_map=pf.events_by_ticker_date([EV_BID_0817]))
gen_bid = [g for g in rep.get("generated", []) if str(g).find("BID") >= 0]
check("D3#2 merge_park: L1/L2 lệch −6,4% + BID có sự kiện 08-17 ⇒ CHẶN mã, KHÔNG 'lấy giá thấp hơn'",
      rep.get("exdate_blocked") == ["BID"] or any("CHẶN" in e for e in rep.get("errors", [])),
      f"exdate_blocked={rep.get('exdate_blocked')}, errors={len(rep.get('errors', []))}")

L1b = dict(L1, orders=[dict(L1["orders"][0], ref_price=38850)])
L2b = dict(L2, orders=[dict(L2["orders"][0], ref_price=38800)])
_, rep_b = mpo.merge_park_orders({"plan_date": "2026-09-30", "account": "SpaceX", "orders": []},
                                 dict(L1b, plan_date="2026-09-30"),
                                 dict(L2b, plan_date="2026-09-30"),
                                 ex_map=pf.events_by_ticker_date([EV_BID_0817]))
check("D3#2 nhiễu giá thường ngoài cửa sổ sự kiện ⇒ hành vi CŨ nguyên vẹn (cảnh báo, không chặn)",
      not rep_b.get("exdate_blocked"),
      f"warnings={len(rep_b.get('warnings', []))}, blocked={rep_b.get('exdate_blocked')}")

# Cổng D3#2 phải sống ĐỘC LẬP VỚI THỨ TỰ GỌI. Khi caller TIÊM `ex_map` thì `_exdate_map()` —
# nơi duy nhất từng chèn repo root vào sys.path — KHÔNG chạy; nếu `_has_event_in_window` phải
# dựa vào nó thì import hỏng và hàm trả False ⇒ cổng TỰ TẮT TRONG IM LẶNG (đúng ca đã đo:
# bản trước bản vá trả `(False, [])` trong điều kiện dưới đây). Test phải chạy ở TIẾN TRÌNH
# RIÊNG từ cwd lạ — chạy trong tiến trình này thì sys.path đã sạch sẵn nên không tái hiện được.
_probe = subprocess.run(
    [sys.executable, "-c",
     "import importlib.util,sys;"
     f"assert {WC_ROOT!r} not in sys.path;"
     f"s=importlib.util.spec_from_file_location('mpo',{os.path.join(WC_ROOT, 'mike/bin/merge_park_orders.py')!r});"
     "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
     "print(m._has_event_in_window({('BID','2026-08-17'):"
     "[{'ticker':'BID','exright_date':'2026-08-17','event_code':'ISS'}]},'BID','2026-08-14')[0])"],
    cwd="/tmp", capture_output=True, text=True, timeout=120)
check("D3#2 cổng KHÔNG tự tắt im lặng khi ex_map được TIÊM từ cwd lạ (độc lập thứ tự gọi)",
      _probe.returncode == 0 and _probe.stdout.strip() == "True",
      f"rc={_probe.returncode}, stdout={_probe.stdout.strip()!r}, stderr={_probe.stderr.strip()[:200]!r}")

import paper_main_probe_plan as pmp                                 # noqa: E402

pl_probe = pmp.build_plan("2026-08-11", {"MBB": 1200, "FPT": 400}, {"MBB": 24250.0,
                          "FPT": 73200.0, "ACB": 26500.0, "HDB": 26000.0, "VNM": 54600.0,
                          "HPG": 26000.0}, "2026-08-10", ex_tickers={"MBB"})
check("D3#3 paper probe: mã GDKHQ bị BỎ khỏi plan (0 lệnh MBB, cả mua lẫn bán)",
      not [o for o in pl_probe.orders if o.ticker == "MBB"]
      and any("GDKHQ" in n for n in pl_probe.notes))
check("D3#3 các mã còn lại KHÔNG bị ảnh hưởng (harness vẫn sinh evidence như cũ)",
      len([o for o in pl_probe.orders if o.ticker != "MBB"]) >= 5)
pl_norm = pmp.build_plan("2026-08-12", {"FPT": 400}, {"FPT": 73200.0, "MBB": 20350.0,
                         "ACB": 26500.0, "HDB": 26000.0, "VNM": 54600.0, "HPG": 26000.0},
                         "2026-08-11")
check("D3#3 ngày thường: build_plan giữ NGUYÊN hành vi cũ (không tham số ⇒ không loại mã nào)",
      len(pl_norm.orders) == 7, f"{len(pl_norm.orders)} lệnh")

# ══════════════════════════════════════════════════════════════════════════════════════
print("\n── 9. README §6.1 — lag_entry_anchor: anchor vắt qua GDKHQ bị LOẠI ──")
# ══════════════════════════════════════════════════════════════════════════════════════
import corp_action_lib as _cal                                      # noqa: E402
import lag_entry_anchor as lea                                      # noqa: E402

_real_pricing = _cal.pricing_events
_cal.pricing_events = lambda tks, since=None, until=None, codes=None: [
    e for e in [EV_MBB_0811_ISS, EV_MBB_0811_RIGHTS] if e["ticker"] in set(tks)]
try:
    keep, dropped = lea._drop_pairs_crossing_exdate(
        [("MBB", lea._d("2026-08-10")), ("FPT", lea._d("2026-08-10"))], "2026-08-11")
    check("anchor MBB phiên chuẩn 08-10 dùng cho plan 08-11 (GDKHQ) ⇒ LOẠI "
          "(anchor là TRẦN: hệ cũ NỚI trần +20%, không siết)",
          [t for t, _ in keep] == ["FPT"] and len(dropped) == 1, dropped[0][:80] if dropped else "")
    check("mã KHÔNG vắt qua sự kiện giữ nguyên (không chặn oan cả rổ LAG)",
          ("FPT", lea._d("2026-08-10")) in keep)
    keep2, dropped2 = lea._drop_pairs_crossing_exdate(
        [("MBB", lea._d("2026-08-12"))], "2026-08-13")
    check("cửa sổ [entry_date, plan_date] đã QUA sự kiện ⇒ KHÔNG loại (anchor đã cùng hệ)",
          len(keep2) == 1 and not dropped2)
    keep3, _ = lea._drop_pairs_crossing_exdate([("MBB", lea._d("2026-08-10"))], None)
    check("không truyền plan_date ⇒ giữ hành vi CŨ (lời gọi tra cứu thủ công không đổi)",
          len(keep3) == 1)
finally:
    _cal.pricing_events = _real_pricing


# ══════════════════════════════════════════════════════════════════════════════════════
print("\n── 10. Rollout hai bước — pending chặn riêng mã GDKHQ, PASS marker bật atomically ──")
# ══════════════════════════════════════════════════════════════════════════════════════
with tempfile.TemporaryDirectory() as td:
    state_path = os.path.join(td, "rollout.json")
    check("thiếu marker ⇒ mặc định SHADOW_PENDING (fail-safe sau restore/deploy mới)",
          not gdkhq_rollout.enabled(state_path))
    trace_path = os.path.join(td, "trace.json")
    with open(trace_path, "w", encoding="utf-8") as f:
        f.write("{}\n")
    state = gdkhq_rollout.mark_enabled(trace_path, "2026-08-17", state_path)
    check("chỉ mark_enabled sau trace PASS mới bật rollout",
          gdkhq_rollout.enabled(state_path) and state.get("approved_by") == "user")

pending_plan, pending_adj = apply_exdate_gate(
    plan_main_0811(), br_mbb, "2026-08-11", events_map=emap_mbb,
    resolver=gdkhq_rollout.pending_resolver)
check("SHADOW_PENDING chặn RIÊNG mọi lệnh mã GDKHQ trước khi rollout",
      not pending_plan.orders and pending_adj
      and all(a.get("gate") == "ROLLOUT_PENDING" for a in pending_adj))

normal_plan = TradePlan(plan_date="2026-08-12", signal_date="2026-08-11",
                        strategy="fixture", strategy_version="1", state=2,
                        state_name="NEUTRAL", nav_basis={}, account="main", created_at="",
                        orders=[PlannedOrder("BUY-FPT", "FPT", "buy", 100, 73200)])
normal_after, normal_adj = apply_exdate_gate(
    normal_plan, br_mbb, "2026-08-12", events_map=pf.events_by_ticker_date([]),
    resolver=gdkhq_rollout.pending_resolver)
check("SHADOW_PENDING không đụng mã thường trong cùng cơ chế",
      len(normal_after.orders) == 1 and normal_adj[0].get("action") == "NO_EVENT")


# ══════════════════════════════════════════════════════════════════════════════════════
print()
if FAILS:
    print(f"FAILED {len(FAILS)}: {FAILS}")
    sys.exit(1)
print("OK — cổng GDKHQ (D1/D2/D3) PASS toàn bộ, gồm 2 ca chứng minh ngược từ artifact THẬT")
sys.exit(0)
