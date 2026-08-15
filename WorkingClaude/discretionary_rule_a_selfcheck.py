"""Selfcheck: LUẬT A cho book DISCRETIONARY_SPECIAL (`dynamic_ceiling.ceiling_rule = "A"`).

Việc 2 của job Taylor_20260815_022340. User chốt 2026-08-15: "Đổi luôn sang rule A. Tôi thích
ý tưởng adaptive hơn là fix cứng."

`sessions=5` (mean-5) CHÍNH LÀ luật B: trần theo cửa sổ cố định nên TỤT LẠI khi giá đi lên liên
tục — đúng cơ chế đã khiến TV1 kẹt 3 tuần. Luật A neo vào MỘT phiên đã đóng gần nhất và tái lập
mỗi lần lập plan.

Bất biến được khoá ở đây, theo thứ tự quan trọng:
  1. KHÔNG khai `ceiling_rule` ⇒ hành vi mean-N cũ GIỮ NGUYÊN TỪNG ĐỒNG (state production hôm
     nay chưa lật, code này phải vô hình với nó).
  2. Mọi đường hỏng ⇒ fail-safe về band CỐ ĐỊNH, KHÔNG BAO GIỜ âm thầm rơi về mean-N (rơi về
     mean-N sẽ khiến việc lật state file trông như đã ăn trong khi nó đang chạy luật khác).
  3. Provenance chỉ được khai khi trần ĐÚNG BẰNG công thức luật A — bị `max_no_chase_ceiling`
     kẹp thì KHÔNG khai, nếu không `resolve_buy_ceiling()` fail-closed rồi XOÁ SẠCH trần
     (lệnh discretionary không có `entry_anchor_price` để rơi về) = fail-OPEN.
  4. Anchor phải là phiên ĐÃ ĐÓNG TRƯỚC `plan_date`.
"""
import copy
import os
import sys

# §5b coding_guidelines — đặt TRƯỚC mọi import có thể dựng Executor. Selfcheck này chỉ dùng hàm
# thuần, nhưng đặt vô điều kiện là cách duy nhất để lần sau thêm test chạm Executor không rò
# event thật lên bus.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

from trading_bot.discretionary_accumulation import (          # noqa: E402
    compute_session_order, resolve_price_band, validate_state)
from trading_bot.no_chase_ceiling import ANCHOR_BASIS_OFFICIAL_REF  # noqa: E402
from trading_bot.no_chase_ceiling import (                    # noqa: E402
    check_ref_vs_live, resolve_buy_ceiling, rule_a_ceiling, rule_a_in_force)

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


# ───────────────────────────────────────────────────────────────────────────── FIXTURE ĐÓNG BĂNG
# §23 hệ luận 1: KHÔNG đọc `data/trade_plans/discretionary/state_TV1_*.json` sống — state đó sẽ
# bị Mike lật `ceiling_rule` trong một commit riêng, và một test assert lên nó sẽ tự vô hiệu
# đúng lúc nó cần bắt lỗi nhất. Đây là BẢN SAO cấu trúc, không phải tham chiếu.
BASE = {
    "ticker": "TV1", "account": "SpaceX", "status": "active", "lot_size": 100,
    "target_qty": 2300, "baseline_qty_before_program": 0,
    "price_band": {"resting_limit": 19900, "no_chase_ceiling": 20000,
                   "max_no_chase_ceiling": 25000},
    "adv_ref_vnd": 720_000_000, "per_session_cap_pct_adv": 0.1,
    "opportunistic": {"k": 2.0, "m": 2.0},
    "dynamic_ceiling": {"enabled": True, "tau": 0.03, "sessions": 5},
}
# Giá đóng TV1 THẬT 5 phiên tới 2026-08-12 (feed DNSE, cũ→mới) — chính chuỗi sinh ra trần
# 20.497 ghi trong plan LIVE 2026-08-13 của CẢ HAI account.
ANCHORS = [19_500.0, 19_700.0, 20_000.0, 20_000.0, 20_300.0]
DATES = ["2026-08-06", "2026-08-07", "2026-08-10", "2026-08-11", "2026-08-12"]
PLAN_DATE = "2026-08-13"
MEAN5 = sum(ANCHORS) / len(ANCHORS)              # 19.900
LATEST = 20_300.0


def st(rule=None, **over):
    s = copy.deepcopy(BASE)
    if rule is not None:
        s["dynamic_ceiling"]["ceiling_rule"] = rule
    for k, v in over.items():
        if k in ("price_band", "dynamic_ceiling"):
            s[k].update(v)
        else:
            s[k] = v
    return s


def band_a(state, anchors=ANCHORS, dates=DATES, plan_date=PLAN_DATE, latest=LATEST,
           basis=ANCHOR_BASIS_OFFICIAL_REF, exchange="UPCOM"):
    """TV1 = UPCOM (đo từ DNSE `marketId`=UPX, 2026-08-15) — mặc định của mọi ca ở đây."""
    return resolve_price_band(state, anchors, latest, anchor_dates=dates, plan_date=plan_date,
                              anchor_basis=basis, anchor_exchange=exchange)


print(__doc__.splitlines()[0])
print("=" * 78)

# ═══════════════════════════════ A. KHÔNG khai ceiling_rule ⇒ hành vi cũ GIỮ NGUYÊN TỪNG ĐỒNG
print("\nA. Tương thích ngược — state production hôm nay (chưa lật) không được đổi 1 đồng nào")
c_old, r_old, i_old = resolve_price_band(st(), ANCHORS, LATEST)
check("A1 mean-5 vẫn ra đúng trần cũ 20.497 (= trần plan LIVE 08-13 thật)",
      int(c_old) == 20_497 and i_old["mode"] == "dynamic",
      f"trần={int(c_old):,} mode={i_old['mode']} mean5={MEAN5:,.0f}")

# Tham số MỚI truyền vào nhánh CŨ phải trơ hoàn toàn — nếu không, chỉ riêng việc wire
# `anchor_dates` ở inject.py đã đổi hành vi LIVE trước khi ai kịp duyệt luật A.
c_i, r_i, i_i = band_a(st())
check("A2 truyền anchor_dates/plan_date vào state CHƯA khai luật A ⇒ TRƠ, y hệt A1",
      (int(c_i), int(r_i), i_i["mode"]) == (int(c_old), int(r_old), i_old["mode"]),
      f"{int(c_i):,}/{int(r_i):,} vs {int(c_old):,}/{int(r_old):,}")

o_old, _ = compute_session_order(st(), 0, 1_500_000_000, LATEST, PLAN_DATE,
                                 f"{PLAN_DATE}T00:00:00", anchor_prices=ANCHORS,
                                 anchor_dates=DATES, active_nav_vnd=973_647_205,
                                 anchor_basis=ANCHOR_BASIS_OFFICIAL_REF,
                                 anchor_exchange="UPCOM")
check("A3 lệnh sinh từ nhánh cũ KHÔNG mang nhãn luật A (không provenance rơi vãi)",
      isinstance(o_old, dict) and "ceiling_rule" not in o_old,
      f"khoá ceiling_*: {[k for k in o_old if k.startswith('ceiling_')] if isinstance(o_old, dict) else o_old}")

# ══════════════════════════════════════════════════════════════════ B. Luật A — công thức lõi
print("\nB. Luật A: anchor = giá đóng phiên đã hoàn tất gần nhất, KHÔNG phải mean-N")
c_a, r_a, i_a = band_a(st("A"))
expect_a = int(rule_a_ceiling(20_300.0, 0.03)[0])            # 20.300 × 1,03 → 20.909
check("B1 trần = floor(close_phiên_trước × (1+τ)) = 20.909", int(c_a) == expect_a == 20_909,
      f"trần={int(c_a):,} mode={i_a['mode']} anchor={i_a['anchor_vnd']:,.0f}")
check("B2 mode = 'rule_a' (phân biệt được với 'dynamic' trong log/audit)",
      i_a["mode"] == "rule_a", i_a["mode"])

# `sessions` phải MẤT HẲN vai trò — nếu còn ăn, việc lật state mà quên sửa `sessions` sẽ ra
# một luật thứ ba không ai định nghĩa.
c_s1, _, _ = band_a(st("A", dynamic_ceiling={"sessions": 1}))
c_s20, _, _ = band_a(st("A", dynamic_ceiling={"sessions": 20}))
check("B3 `sessions` bị BỎ QUA hoàn toàn (1 và 20 cho cùng một trần)",
      int(c_s1) == int(c_s20) == int(c_a), f"{int(c_s1):,} / {int(c_s20):,} / {int(c_a):,}")

check("B4 resting kéo theo cùng tỉ lệ và KHÔNG BAO GIỜ vượt trần (bất biến no-chase)",
      r_a <= c_a and int(r_a) == 20_804,
      f"resting={int(r_a):,} ≤ trần={int(c_a):,} (tỉ lệ gốc 0,995)")

# Đây là LÝ DO đổi luật: giá đi lên liên tục thì mean-5 tụt lại phía sau.
check("B5 TÍNH ADAPTIVE: giá tăng ⇒ trần luật A CAO hơn mean-5 (+412đ trên chính ngày 08-13)",
      int(c_a) - int(c_old) == 412, f"{int(c_a):,} − {int(c_old):,} = {int(c_a)-int(c_old):+,}đ")

# ...và ĐỐI XỨNG khi giá đi xuống — luật A không phải "luôn nới trần".
down = [20_500.0, 20_400.0, 20_300.0, 20_200.0, 19_800.0]
c_dn_a, _, _ = resolve_price_band(st("A"), down, 19_800.0, anchor_dates=DATES,
                                  anchor_basis=ANCHOR_BASIS_OFFICIAL_REF,
                                  anchor_exchange="UPCOM",
                                  plan_date=PLAN_DATE)
c_dn_o, _, _ = resolve_price_band(st(), down, 19_800.0)
check("B6 ĐỐI XỨNG: giá giảm ⇒ trần luật A THẤP hơn mean-5 (không phải luật nới một chiều)",
      int(c_dn_a) < int(c_dn_o), f"luật A {int(c_dn_a):,} < mean-5 {int(c_dn_o):,}")

# ═══════════════════════════════════════════════ C. Bất biến #4 — anchor phải là phiên ĐÃ ĐÓNG
print("\nC. Bất biến #4: anchor phải là phiên ĐÃ ĐÓNG TRƯỚC plan_date")
for label, d in (("anchor_date == plan_date", PLAN_DATE),
                 ("anchor_date > plan_date (nến tương lai)", "2026-08-20")):
    _, _, i_bad = band_a(st("A"), dates=DATES[:-1] + [d])
    check(f"C{1 if d == PLAN_DATE else 2} {label} ⇒ FAIL-SAFE về band cố định",
          i_bad["mode"] == "fixed_failsafe", i_bad.get("reason", "")[:88])
_, _, i_ok = band_a(st("A"))
check("C3 anchor_date < plan_date ⇒ chạy bình thường", i_ok["mode"] == "rule_a")

# ══════════════════════════ D. Fail-safe: KHÔNG BAO GIỜ âm thầm rơi về mean-N khi luật A hỏng
print("\nD. Đường hỏng ⇒ band CỐ ĐỊNH, KHÔNG rơi về mean-N (nếu rơi, việc lật state trông như"
      " đã ăn trong khi chạy luật khác)")
CASES = [
    ("D1 thiếu anchor_dates", dict(dates=None)),
    ("D2 anchor_dates lệch độ dài anchor_prices", dict(dates=DATES[:3])),
    ("D3 anchor_date rác không parse được", dict(dates=DATES[:-1] + ["hôm-qua"])),
    ("D4 thiếu plan_date", dict(plan_date=None)),
    ("D5 plan_date rác", dict(plan_date="15/08/2026")),
    # SỬA LỖI 2026-08-15 (job Taylor_20260815_034407): TV1 là mã **UPCOM**, nơi giá tham chiếu
    # là bình quân gia quyền chứ không phải giá đóng cửa (đo 259 phiên TV1: median lệch 0,389%,
    # p90 1,333%, max 7,041%). Người gọi phải KHAI cơ sở giá; không khai ⇒ fail-safe.
    ("D6 KHÔNG khai anchor_basis (vintage cũ dùng giá đóng cửa)", dict(basis=None)),
    ("D7 anchor_basis SAI ('prev_close')", dict(basis="prev_close")),
    ("D8 KHÔNG xác định được sàn (feed câm ⇒ Quote.exchange fail-OPEN về 'HOSE')",
     dict(exchange=None)),
    ("D9 sàn không hợp lệ", dict(exchange="XXX")),
]
for name, kw in CASES:
    c_f, r_f, i_f = band_a(st("A"), **kw)
    ok = (i_f["mode"] == "fixed_failsafe" and int(c_f) == 20_000 and int(r_f) == 19_900
          and int(c_f) != int(c_old))          # ← khoá "không rơi về mean-N 20.497"
    check(name + " ⇒ band cố định 20.000", ok,
          f"trần={int(c_f):,} mode={i_f['mode']}")

_, _, i_b = band_a(st("B"))
check("D6 ceiling_rule='B' (luật không tồn tại) ⇒ FAIL-SAFE, không im lặng chạy mean-N",
      i_b["mode"] == "fixed_failsafe", i_b.get("reason", "")[:88])
_, _, i_lc = band_a(st("a"))
check("D7 ceiling_rule='a' thường ⇒ vẫn nhận (chuẩn hoá hoa/thường, không bẫy chính tả)",
      i_lc["mode"] == "rule_a")

# ═══════════════════════════════════ E. Provenance — vòng tròn khép kín với load_plan/executor
print("\nE. Provenance: trần phải TÁI LẬP được ở tầng nạp plan, và KHÔNG khai khi bị kẹp")
o_a, dec_a = compute_session_order(st("A"), 0, 1_500_000_000, LATEST, PLAN_DATE,
                                   f"{PLAN_DATE}T00:00:00", anchor_prices=ANCHORS,
                                   anchor_dates=DATES, active_nav_vnd=973_647_205,
                                   anchor_basis=ANCHOR_BASIS_OFFICIAL_REF,
                                 anchor_exchange="UPCOM")
check("E1 lệnh mang đủ 4 field provenance", isinstance(o_a, dict) and all(
    k in o_a for k in ("ceiling_rule", "ceiling_anchor_price", "ceiling_anchor_date",
                       "ceiling_tau")),
    {k: o_a.get(k) for k in ("ceiling_rule", "ceiling_anchor_price", "ceiling_anchor_date",
                             "ceiling_tau")} if isinstance(o_a, dict) else o_a)
check("E2 trần trong lệnh = trần luật A", int(o_a["hard_no_chase_ceiling_vnd"]) == 20_909)

o_raw = dict(o_a, side="buy")
c_rt, i_rt = resolve_buy_ceiling(o_raw, plan_date=PLAN_DATE)
check("E3 resolve_buy_ceiling() TÁI LẬP đúng trần (mode rule_a, không fail-closed)",
      i_rt.get("mode") == "rule_a" and int(c_rt) == 20_909,
      f"{i_rt.get('mode')} trần={c_rt}")


class _O:                    # shim tối thiểu thay PlannedOrder (rule_a_in_force đọc attribute)
    def __init__(self, d):
        self.__dict__.update(d)


check("E4 rule_a_in_force() = True ⇒ cổng fail-safe cơ sở giá (việc 1) SOI được lệnh TV1 này",
      rule_a_in_force(_O(o_raw)) is True)

# Bị `max_no_chase_ceiling` kẹp ⇒ trần KHÔNG còn tái lập được từ anchor×(1+τ) ⇒ CẤM khai nhãn.
capped = st("A", price_band={"max_no_chase_ceiling": 20_500})
c_cap, _, i_cap = band_a(capped)
check("E5 bị trần tuyệt đối kẹp ⇒ trần = cận trên user duyệt (20.500), KHÔNG phải 20.909",
      int(c_cap) == 20_500 and i_cap["capped_by_max"] is True, f"trần={int(c_cap):,}")
check("E6 ...và KHÔNG khai provenance (khai vào ⇒ load_plan fail-closed rồi XOÁ SẠCH trần = fail-OPEN)",
      i_cap.get("rule_a_provenance") is None)
o_cap, _ = compute_session_order(capped, 0, 1_500_000_000, LATEST, PLAN_DATE,
                                 f"{PLAN_DATE}T00:00:00", anchor_prices=ANCHORS,
                                 anchor_dates=DATES, active_nav_vnd=973_647_205,
                                 anchor_basis=ANCHOR_BASIS_OFFICIAL_REF,
                                 anchor_exchange="UPCOM")
check("E7 lệnh khi bị kẹp KHÔNG mang ceiling_rule ⇒ đi nhánh luật cũ, trần vẫn còn nguyên",
      isinstance(o_cap, dict) and "ceiling_rule" not in o_cap
      and int(o_cap["hard_no_chase_ceiling_vnd"]) == 20_500,
      f"trần lệnh={o_cap.get('hard_no_chase_ceiling_vnd') if isinstance(o_cap, dict) else o_cap}")
c_cap_rt, i_cap_rt = resolve_buy_ceiling(dict(o_cap, side="buy"), plan_date=PLAN_DATE)
check("E8 ...và load_plan giữ ĐÚNG trần 20.500 (không bị xoá thành None)",
      c_cap_rt is not None and int(c_cap_rt) == 20_500, f"{c_cap_rt}")

# ══════════════════════════════════════ F. Ghép với việc 1 — cổng fail-safe cơ sở giá lúc đặt
print("\nF. Ghép với cổng fail-safe cơ sở giá (việc 1): TV1 giờ cũng là lệnh luật A")
# `check_ref_vs_live`/`rule_a_in_force` đọc bằng getattr — chúng nhận `PlannedOrder` từ
# executor, KHÔNG phải dict thô. Truyền dict vào sẽ "CHẶN" ở mọi ca vì đọc ra None hết, tức
# F2/F3 sẽ PASS vì SAI LÝ DO. F1 là ca duy nhất phân biệt được hai tình huống đó — giữ nó.
o_guard = _O(dict(o_raw, ref_price=20_394))
ok_g, i_g = check_ref_vs_live(o_guard, live_reference_price=20_300.0, chase_pct=0.03)
check("F1 anchor khớp giá tham chiếu phiên sống ⇒ CHO ĐI", ok_g is True, i_g.get("reason", "")[:80])
ok_b, i_b2 = check_ref_vs_live(o_guard, live_reference_price=19_700.0, chase_pct=0.03)
check("F2 anchor lệch +3,05% so với giá đóng sống ⇒ CHẶN (plan trễ phiên/feed vỡ)",
      ok_b is False, i_b2.get("reason", "")[:80])
ok_n, i_n = check_ref_vs_live(o_guard, live_reference_price=None, chase_pct=0.03)
check("F3 thiếu giá sống ⇒ CHẶN (fail-closed, không bỏ qua)", ok_n is False,
      i_n.get("reason", "")[:80])

# ════════════════════════════════════════════════════════ G. State vẫn hợp lệ với khoá mới
print("\nG. Bất biến state")
check("G1 validate_state() chấp nhận state có ceiling_rule (không phá schema cũ)",
      validate_state(st("A")) is True)
check("G2 resting ≤ trần ở CẢ hai luật",
      r_old <= c_old and r_a <= c_a, f"cũ {int(r_old):,}≤{int(c_old):,} | A {int(r_a):,}≤{int(c_a):,}")

# ═════════════════════════════════════════════════════════════════════════════════════ KẾT
print("\n" + "=" * 78)
n_total = 8 + 6 + 3 + 7 + 8 + 3 + 2
if fails:
    print(f"❌ FAIL {len(fails)}/{n_total}: {fails}")
    sys.exit(1)
print(f"✅ ALL PASS — {n_total}/{n_total} — luật A cho book DISCRETIONARY_SPECIAL "
      f"(mean-5 → anchor 1 phiên, adaptive)")
print("   Đối chứng số THẬT: mean-5 20.497 = trần plan LIVE 2026-08-13; luật A cho 20.909 (+412đ).")
