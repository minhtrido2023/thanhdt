# -*- coding: utf-8 -*-
"""Self-check + DIỄN TẬP cho đòn bẩy margin sleeve CAPIT (chính sách `capit_margin_lever`).

Chính sách (user John duyệt 2026-08-03, đúng phạm vi chuỗi nghiên cứu p1–p5 cùng ngày):
vay margin CHỈ trên rổ CAPIT, hệ số CỐ ĐỊNH f=1,3, cổng `dd52<=−20%`, gói vay DNSE 1840
"RocketX", CHỈ account SpaceX. **MẶC ĐỊNH TẮT** (`data/trading_rules.json` →
`capit_margin_lever.enabled=false`); bật lên cần một bước xác nhận RIÊNG của user.

VÌ SAO CẦN DIỄN TẬP RIÊNG, không chỉ unit test từng hàm: hôm nay KHÔNG có sự kiện washout
nào đạt cổng thật (dd52 hiện tại còn xa −20%), nên đường đi của cờ vay chưa từng chạy sống
một lần nào. Cái phải chứng minh là cờ `lever_f`/`loan_package_id` đi TRỌN đường
tín hiệu → artifact → plan → cascade → lệnh broker mà KHÔNG rớt mất ở lớp trung gian nào —
và, quan trọng ngang thế, rằng với cấu hình THẬT (đang TẮT) thì KHÔNG lệnh nào mang cờ vay.

Bốn tầng được kiểm, mỗi tầng chạy trên CODE PRODUCTION THẬT (không phải bản chép):
  A. Chính sách   — golive_recommend_v23.py :: capit_lever_policy()   (trích bằng AST)
  B. Tín hiệu     — golive_recommend_v23.py §6a  (trích nguyên văn giữa CAPIT_LEVER_BEGIN/END)
  C. Cascade plan — trading_bot/plan.py :: apply_capit_lever()
  D. Broker       — trading_bot/brokers.py :: DNSEBroker._validate_lever_package / place_order
  E. Lưới an toàn — trading_bot/executor.py :: _lever_package_audit()
  F. DIỄN TẬP đầu-cuối trên PaperBroker: washout GIẢ LẬP (bật) vs cấu hình THẬT (tắt)
  G. Chốt chặn   — cấu hình THẬT trên đĩa phải còn enabled=false

Tầng A/B trích source thật giữa hai mốc `CAPIT_LEVER_BEGIN`/`CAPIT_LEVER_END` rồi exec —
nếu ai sửa §6a mà làm lệch hành vi, test này fail; nếu ai xoá mốc, test cũng fail. Đó là chủ
đích: một test chép lại logic sẽ trôi khỏi production mà vẫn xanh (§17 extract-and-test).

Phụ thuộc môi trường (khai theo skill verify-before-done): test này KHÔNG đọc giờ/ngày hệ
thống cho bất kỳ khẳng định nào, nhưng `trading_bot.brokers` có dùng `today_ict()` khi lọc
sổ lệnh paper theo ngày → CHẠY LẠI DƯỚI `env -u TZ` LÀ BẮT BUỘC (đúng bài học §16). Xem
dòng ENV ở cuối output.

Run: python capit_lever_selfcheck.py     (exit 0 = all pass)
"""
import ast
import copy
import datetime as _dt
import glob
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from trading_bot.brokers import OrderUpdate, PaperBroker, DNSEBroker  # noqa: E402
import trading_bot.plan as _planmod  # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan, apply_capit_lever  # noqa: E402
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.config import load_config, EXEC_DIR  # noqa: E402

GOLIVE = os.path.join(HERE, "deploy_golive_dt5g_v4", "golive_recommend_v23.py")
REAL_RULES = os.path.join(HERE, "data", "trading_rules.json")

# Executor.__init__ nạp state.json theo (account, plan_date) NGAY trong constructor, trước
# khi test kịp trỏ sang tmpdir → file sót của lần chạy trước làm bẩn state khởi đầu. Tag
# riêng + dọn sạch trước mỗi lần chạy (đúng khuôn ghost_order_selfcheck.py).
TAG = "selfcheck-lever"
for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(_f)

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def section(t):
    print(f"\n{t}")


# ───────────────────────── trích code production thật ─────────────────────────

def _golive_src():
    with open(GOLIVE, encoding="utf-8") as f:
        return f.read()


def extract_func(src, name):
    """Source của đúng 1 def top-level trong `src` (AST, không regex)."""
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node)
    raise AssertionError(f"không tìm thấy def {name}() trong {GOLIVE}")


def extract_consts(src, prefix="CAPIT_LEVER_", allow_empty=False):
    """Mọi hằng số top-level `CAPIT_LEVER_*` → dict, đọc THẲNG từ source production.

    Không chép giá trị vào test: ngưỡng cổng là tham số quyết định vay tiền, một bản sao
    trong test sẽ âm thầm trôi khỏi production và test vẫn xanh. Đọc từ nguồn ⇒ ai sửa
    ngưỡng thì test chạy trên ngưỡng mới, còn ai THÊM hằng số mà quên thì §6a NameError
    ngay tại đây (đã xảy ra thật khi thêm SANITY_FLOOR — đó là hàng rào đang làm việc).
    """
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id.startswith(prefix):
            out[node.targets[0].id] = ast.literal_eval(node.value)
    if not out and not allow_empty:
        raise AssertionError(f"không tìm thấy hằng số {prefix}* nào trong {GOLIVE}")
    return out


def extract_marked(src, begin="# CAPIT_LEVER_BEGIN", end="# CAPIT_LEVER_END"):
    if src.count(begin) != 1 or src.count(end) != 1:
        raise AssertionError(f"mốc {begin}/{end} phải xuất hiện ĐÚNG 1 lần trong {GOLIVE}")
    body = src.split(begin, 1)[1].split(end, 1)[0]
    if "capit_lever = {" not in body:
        raise AssertionError("đoạn giữa 2 mốc không chứa việc dựng dict capit_lever — "
                             "mốc đã bị di chuyển sai chỗ")
    return body


def write_rules(path, **over):
    """Ghi 1 trading_rules.json tối giản chỉ có khối capit_margin_lever (giá trị mặc định
    = ĐÚNG chính sách đã duyệt; `over` để bẻ từng trục một khi thử fail-closed)."""
    blk = {"enabled": True, "f": 1.3, "gate": "dd52<=-0.20", "loan_package_id": 1840,
           "scope": "capit_only", "accounts": ["SpaceX"]}
    blk.update(over)
    if blk.pop("_drop_block", False):
        doc = {}
    else:
        doc = {"capit_margin_lever": blk}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False)


SRC = _golive_src()
POLICY_SRC = extract_func(SRC, "capit_lever_policy")
BLOCK_SRC = extract_marked(SRC)
# Ngưỡng cổng vẫn khai trong golive; PHẠM VI DUYỆT (APPROVED_*) đã dời sang trading_bot/plan.py
# — tầng THỰC THI — và golive IMPORT lại, nên phải ghép 2 nguồn để dựng namespace cho §6a.
# Ghép chứ không chép: nếu ai đó khai lại APPROVED_* trong golive, A11b dưới đây fail.
CONSTS = dict(extract_consts(SRC))
CONSTS.update({"CAPIT_LEVER_APPROVED_F": _planmod.CAPIT_LEVER_APPROVED_F,
               "CAPIT_LEVER_APPROVED_PACKAGE": _planmod.CAPIT_LEVER_APPROVED_PACKAGE,
               "CAPIT_LEVER_APPROVED_ACCOUNTS": _planmod.CAPIT_LEVER_APPROVED_ACCOUNTS})


class _FakePd:
    """`pd.notna` là thứ duy nhất §6a dùng từ pandas — stub để khỏi kéo cả pandas vào."""
    @staticmethod
    def notna(v):
        return v is not None and v == v


def run_policy(workdir):
    """`workdir` = thư mục CHỨA data/trading_rules.json (hàm production tự nối 'data/…').

    Nhận WORKDIR chứ không nhận thẳng đường dẫn file: bản đầu của test này truyền file rồi
    lấy dirname làm WORKDIR, thành ra hàm đi tìm `…/data/data/trading_rules.json` — 4 ca
    fail-closed PASS vì FileNotFoundError chứ không vì điều đang được kiểm. Lỗi lộ ra ngay
    lần chạy thật đầu tiên; giữ ghi chú này để không ai "đơn giản hoá" lại chữ ký hàm.
    """
    ns = {"os": os, "json": json, "WORKDIR": workdir, **CONSTS}
    exec(POLICY_SRC, ns)
    return ns["capit_lever_policy"]()


def run_block(rules_dir, *, dd52, signal, size, basket, targets):
    """Chạy §6a THẬT với đầu vào giả lập → (capit_lever dict, capit_targets sau khi chạy)."""
    ns = {"os": os, "json": json, "pd": _FakePd, "WORKDIR": rules_dir,
          "dd52_now": dd52, "capit_signal_today": signal, "capit_size": size,
          "basket": list(basket), "capit_targets": copy.deepcopy(targets),
          **CONSTS}
    exec(POLICY_SRC, ns)
    exec(BLOCK_SRC, ns)
    return ns["capit_lever"], ns["capit_targets"]


def base_targets():
    return {"SpaceX": {"nav_book_lag_vnd": 500_000_000, "capit_total_target_vnd": 250_000_000,
                       "capit_slot_target_vnd": 50_000_000, "n_slots": 5},
            "ZaloPay": {"nav_book_lag_vnd": 200_000_000, "capit_total_target_vnd": 100_000_000,
                        "capit_slot_target_vnd": 20_000_000, "n_slots": 5}}


BASKET5 = ["SAB", "SIP", "VNM", "PVT", "NCT"]


def _rules_dir(tmp, name, **over):
    """Tạo <tmp>/<name>/data/trading_rules.json → trả thư mục đóng vai WORKDIR."""
    d = os.path.join(tmp, name, "data")
    os.makedirs(d, exist_ok=True)
    write_rules(os.path.join(d, "trading_rules.json"), **over)
    return os.path.dirname(d)


# ══════════════════════════════════════════════════════════════════════════════
with tempfile.TemporaryDirectory() as TMP:

    # ─────────────────── A. Tầng chính sách: capit_lever_policy() ───────────────────
    section("A. Chính sách (golive_recommend_v23.py :: capit_lever_policy)")

    def bad(err):
        """Lỗi ĐÚNG loại: do tham số chính sách sai, KHÔNG phải do không tìm thấy file.
        Chốt này tồn tại vì bản đầu của test đã PASS 4 ca fail-closed bằng FileNotFoundError."""
        return bool(err) and "FileNotFoundError" not in str(err)

    pol, err = run_policy(_rules_dir(TMP, "a_ok"))
    check("A1 đọc được khối hợp lệ, không lỗi",
          err is None and pol["f"] == 1.3 and pol["loan_package_id"] == 1840
          and pol["scope"] == "capit_only" and pol["accounts"] == ["SpaceX"],
          detail=f"{pol} err={err}")

    pol, err = run_policy(_rules_dir(TMP, "a_none", _drop_block=True))
    check("A2 thiếu khối capit_margin_lever → báo lỗi, KHÔNG mặc định bật",
          bad(err) and not pol.get("enabled"), detail=str(err))

    pol, err = run_policy(_rules_dir(TMP, "a_f", f=0.5))
    check("A3 f<1 → coi như TẮT (không 'chạy tạm' với tham số vô lý)", bad(err),
          detail=str(err))

    pol, err = run_policy(_rules_dir(TMP, "a_scope", scope="whole_account"))
    check("A4 scope ≠ capit_only → TẮT (không cho nới phạm vi bằng cách sửa 1 chữ)",
          bad(err), detail=str(err))

    pol, err = run_policy(_rules_dir(TMP, "a_lp", loan_package_id=None))
    check("A5 thiếu loan_package_id → TẮT", bad(err), detail=str(err))

    # H1 (arch-reviewer 2026-08-03, chứng minh bằng chạy thật): `bool("false")` là True ⇒
    # một lỗi gõ JSON tầm thường từng BẬT được đòn bẩy. Công tắc chính là thứ duy nhất
    # KHÔNG được fail-open; chỉ literal boolean `true` mới tính.
    for junk in ("false", "no", "0", "true", 1, 0, "yes"):
        pol_j, err_j = run_policy(_rules_dir(TMP, f"a_junk_{junk}", enabled=junk))
        ok = pol_j.get("enabled") is False and bad(err_j)
        check(f"A8[{junk!r}] enabled không phải boolean JSON → TẮT + báo lỗi "
              f"(không bao giờ đọc thành BẬT)", ok,
              detail=f"enabled={pol_j.get('enabled')!r} err={err_j}")

    pol_t, err_t = run_policy(_rules_dir(TMP, "a_true", enabled=True))
    check("A9 …còn literal true THẬT thì vẫn bật được (sàn trên không chặn nhầm)",
          pol_t["enabled"] is True and err_t is None, detail=str(err_t))

    # H3: phạm vi duyệt phải được ghim trong CODE, vì trading_rules.json bị gitignore
    # (không diff/blame/backup) — sửa f hay thêm account ở đó là đổi tiền thật không dấu vết.
    for name, over in (("f=5.0", {"f": 5.0}),
                       ("thêm ZaloPay", {"accounts": ["SpaceX", "ZaloPay"]}),
                       ("gói 9999", {"loan_package_id": 9999})):
        pol_s, err_s = run_policy(_rules_dir(TMP, f"a_scope_{abs(hash(name))}", **over))
        check(f"A10[{name}] JSON tự nới phạm vi → TẮT (nới thật phải sửa CODE + review)",
              bad(err_s) and "phạm vi" in str(err_s), detail=str(err_s))

    check("A11 hằng phạm vi trong code == đúng bản user duyệt (f 1,3 · gói 1840 · SpaceX)",
          CONSTS["CAPIT_LEVER_APPROVED_F"] == 1.3
          and CONSTS["CAPIT_LEVER_APPROVED_PACKAGE"] == 1840
          and CONSTS["CAPIT_LEVER_APPROVED_ACCOUNTS"] == ["SpaceX"],
          detail=str({k: v for k, v in CONSTS.items() if "APPROVED" in k}))

    # A11b: MỘT nguồn chuẩn tắc, không hai bản sao trôi khỏi nhau. Hằng phạm vi sống ở
    # trading_bot/plan.py (tầng THỰC THI — nơi giữ tiền); golive phải IMPORT, không khai lại.
    check("A11b golive IMPORT hằng phạm vi từ trading_bot.plan, KHÔNG tự khai lại (1 nguồn)",
          not extract_consts(SRC, prefix="CAPIT_LEVER_APPROVED", allow_empty=True)
          and "from trading_bot.plan import" in SRC,
          detail=f"golive tự khai APPROVED_*: "
                 f"{sorted(extract_consts(SRC, 'CAPIT_LEVER_APPROVED', allow_empty=True))}")

    # Cấu hình THẬT trên đĩa
    real_pol, real_err = run_policy(HERE)
    check("A6 data/trading_rules.json THẬT: đọc được, tham số đúng chính sách đã duyệt",
          real_err is None and real_pol["f"] == 1.3 and real_pol["loan_package_id"] == 1840
          and real_pol["accounts"] == ["SpaceX"] and real_pol["scope"] == "capit_only",
          detail=f"{real_pol} err={real_err}")
    check("A7 …và đang TẮT (enabled=false) — ĐIỀU KIỆN CỨNG của job này",
          real_pol["enabled"] is False, detail=f"enabled={real_pol['enabled']!r}")

    # ─────────────────── B. Tầng tín hiệu: §6a với washout giả lập ───────────────────
    section("B. Tín hiệu §6a (source production giữa CAPIT_LEVER_BEGIN/END)")

    d_on = _rules_dir(TMP, "b_on")
    lev, tgt = run_block(d_on, dd52=-25.0, signal=True, size=0.50,
                         basket=BASKET5, targets=base_targets())
    check("B1 BẬT + dd52 −25% + CAPIT đang fire → active=True",
          lev["active"] is True and lev["gate_pass"] is True, detail=str(lev["reason"]))
    check("B2 …slot levered = slot gốc × 1,3 (50tr → 65tr), tổng 250tr → 325tr",
          tgt["SpaceX"]["capit_slot_target_vnd_levered"] == 65_000_000
          and tgt["SpaceX"]["capit_total_target_vnd_levered"] == 325_000_000,
          detail=str({k: v for k, v in tgt["SpaceX"].items() if "lever" in k}))
    check("B3 …trường GỐC (chưa đòn bẩy) giữ NGUYÊN giá trị — tầng dưới không đổi nghĩa",
          tgt["SpaceX"]["capit_slot_target_vnd"] == 50_000_000
          and tgt["SpaceX"]["capit_total_target_vnd"] == 250_000_000)
    check("B4 …ZaloPay (ngoài danh sách account) KHÔNG bị gắn trường đòn bẩy nào",
          not any("lever" in k for k in tgt["ZaloPay"]), detail=str(list(tgt["ZaloPay"])))

    lev, tgt = run_block(d_on, dd52=-15.0, signal=True, size=0.50,
                         basket=BASKET5, targets=base_targets())
    check("B5 cổng chưa đạt (dd52 −15% > −20%) → active=False, không levered field",
          lev["active"] is False and lev["gate_pass"] is False
          and not any("lever" in k for k in tgt["SpaceX"]), detail=lev["reason"])

    lev, tgt = run_block(d_on, dd52=-25.0, signal=False, size=0.0,
                         basket=[], targets=base_targets())
    check("B6 dd52 đạt nhưng KHÔNG có sự kiện CAPIT → active=False "
          "(đòn bẩy bám sự kiện, không bám chỉ số)", lev["active"] is False,
          detail=lev["reason"])

    lev, tgt = run_block(d_on, dd52=-25.0, signal=True, size=0.001,
                         basket=BASKET5, targets=base_targets())
    check("B7 capit_size ~0 (sự kiện rỗng) → active=False", lev["active"] is False,
          detail=lev["reason"])

    d_gate = _rules_dir(TMP, "b_gate", gate="dd52<=-0.10")
    lev, tgt = run_block(d_gate, dd52=-25.0, signal=True, size=0.50,
                         basket=BASKET5, targets=base_targets())
    check("B8 ngưỡng file (−0.10) ≠ ngưỡng code (−20%) → TẮT + nêu lỗi "
          "(không tự hoà giải 2 nguồn)",
          lev["active"] is False and lev["policy_error"] and "gate" in lev["policy_error"],
          detail=str(lev["policy_error"]))

    lev, tgt = run_block(d_on, dd52=-99.0, signal=True, size=0.50,
                         basket=BASKET5, targets=base_targets())
    check("B8b dd52 = sentinel −99.0 (chuỗi VNINDEX rỗng) → TẮT, KHÔNG đọc thành "
          "'washout sâu kỷ lục' (sự cố dữ liệu không được mở đường vay tiền)",
          lev["active"] is False and lev["gate_pass"] is False
          and lev["policy_error"] and "sentinel" in lev["policy_error"],
          detail=str(lev["policy_error"]))

    lev, tgt = run_block(d_on, dd52=-60.0, signal=True, size=0.50,
                         basket=BASKET5, targets=base_targets())
    check("B8c dd52 −60% (sụp thật, vẫn trên sàn tỉnh táo) → VẪN cấp đòn bẩy "
          "(sàn chống sentinel, không được cắt mất washout thật)", lev["active"] is True,
          detail=lev["reason"])

    d_off = _rules_dir(TMP, "b_off", enabled=False)
    lev_off, tgt_off = run_block(d_off, dd52=-25.0, signal=True, size=0.50,
                                 basket=BASKET5, targets=base_targets())
    check("B9 TẮT + mọi điều kiện khác ĐỀU ĐẠT → vẫn active=False, 0 trường levered "
          "(đây là trạng thái production hôm nay)",
          lev_off["active"] is False and lev_off["gate_pass"] is True
          and not any("lever" in k for k in tgt_off["SpaceX"]), detail=lev_off["reason"])
    check("B10 …artifact VẪN công bố loan_package_id khi tắt → lưới an toàn E vẫn có gì để soi",
          lev_off["loan_package_id"] == 1840, detail=str(lev_off["loan_package_id"]))

    # ─────────────────── C. Tầng cascade plan: apply_capit_lever ───────────────────
    section("C. Cascade plan (trading_bot/plan.py :: apply_capit_lever)")

    ART_ON = os.path.join(TMP, "status_on.json")
    ART_OFF = os.path.join(TMP, "status_off.json")
    lev_on, _ = run_block(d_on, dd52=-25.0, signal=True, size=0.50,
                          basket=BASKET5, targets=base_targets())
    _, tgt_on_art = run_block(d_on, dd52=-25.0, signal=True, size=0.50,
                              basket=BASKET5, targets=base_targets())
    # `capit_adv_caps` = rổ CAPIT của phiên theo account ({mã: trần VND}). apply_capit_lever
    # kiểm thành viên rổ NGAY TẠI CHỖ (arch-reviewer F5) chứ không mượn thứ tự cascade, nên
    # fixture phải có khoá này — trần đặt rất cao để chỉ TƯ CÁCH THÀNH VIÊN được kiểm ở đây,
    # còn giới hạn %ADV là việc của cap_capit_orders (chạy TRƯỚC trong cascade).
    ADV_CAPS5 = {"SpaceX": {t: 10 ** 12 for t in BASKET5}}
    for p, blob in ((ART_ON, lev_on), (ART_OFF, lev_off)):
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"signal_date": "2099-01-01", "capit_lever": blob,
                       "capit_adv_caps": ADV_CAPS5,
                       "capit_slot_targets": tgt_on_art}, f, ensure_ascii=False)

    # CÔNG TẮC VẬN HÀNH đọc NGAY LÚC THỰC THI (arch-reviewer F1): `apply_capit_lever` mở lại
    # `data/trading_rules.json` trước khi cấp cờ vay. Nhóm C kiểm logic ARTIFACT, nên phải trỏ
    # vào một file chính sách BẬT ở tmpdir — nếu không, mọi ca "được cấp" sẽ đỏ vì công tắc
    # production đang TẮT chứ không vì điều đang được kiểm (đúng cái bẫy "PASS/FAIL vì lý do
    # SAI" mà E6a phòng ở nhóm E). CHÍNH file thật (đang TẮT) được kiểm riêng ở C20 + G1.
    RULES_ON = os.path.join(_rules_dir(TMP, "c_pol_on"), "data", "trading_rules.json")
    RULES_OFF = os.path.join(_rules_dir(TMP, "c_pol_off", enabled=False),
                             "data", "trading_rules.json")

    def mkplan(orders, account="SpaceX"):
        return TradePlan(plan_date="2099-01-02", signal_date="2099-01-01",
                         strategy="selfcheck", strategy_version="0", state=1,
                         state_name="CRISIS", nav_basis={"account_nav": 1e9, "scale": 1.0},
                         orders=orders, account=account, created_at="2099-01-01T00:00:00")

    def o(oid, tk, book="CAPIT", side="buy", **kw):
        return PlannedOrder(id=oid, ticker=tk, side=side, qty=1000, ref_price=20000,
                            book=book, **kw)

    plan = mkplan([o("B1", "SAB"), o("B2", "VNM"), o("B3", "FPT", book="BAL"),
                   o("B4", "TRC", book="LAG"), o("B5", "SIP", side="sell")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON)
    by = {x.ticker: x for x in plan.orders}
    check("C1 BẬT: lệnh MUA book CAPIT được gắn f=1,3 + gói 1840",
          by["SAB"].lever_f == 1.3 and by["SAB"].loan_package_id == 1840
          and by["VNM"].loan_package_id == 1840)
    check("C2 …lệnh BAL/LAG KHÔNG được gắn (phạm vi chỉ CAPIT)",
          by["FPT"].loan_package_id is None and by["TRC"].loan_package_id is None)
    check("C3 …lệnh BÁN CAPIT KHÔNG được gắn (chỉ chiều mua mới vay)",
          by["SIP"].loan_package_id is None)
    check("C4 …báo cáo thay đổi đúng 2 dòng APPLIED",
          sorted(x["ticker"] for x in adj if x["action"] == "APPLIED") == ["SAB", "VNM"],
          detail=str(adj))

    # Chiều GỠ — lý do thật sự hàm này nằm ở cascade
    plan = mkplan([o("B1", "FPT", book="BAL"), o("B2", "SAB")])
    plan.orders[0].lever_f, plan.orders[0].loan_package_id = 1.3, 1840
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON)
    by = {x.ticker: x for x in plan.orders}
    check("C5 plan TỰ VIẾT cờ vay vào lệnh BAL → bị GỠ SẠCH "
          "(nơi sinh plan không có quyền cấp đòn bẩy)",
          by["FPT"].lever_f is None and by["FPT"].loan_package_id is None
          and any(x["action"] == "STRIPPED" and x["ticker"] == "FPT" for x in adj),
          detail=str(adj))

    plan = mkplan([o("B1", "SAB"), o("B2", "FPT", book="BAL")])
    plan.orders[0].lever_f, plan.orders[0].loan_package_id = 9.9, 1234
    plan.orders[1].loan_package_id = 1840
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON)
    by = {x.ticker: x for x in plan.orders}
    check("C6 giá trị plan tự khai bị GHI ĐÈ bằng artifact (f 9.9→1.3, gói 1234→1840)",
          by["SAB"].lever_f == 1.3 and by["SAB"].loan_package_id == 1840
          and any(x["action"] == "OVERRIDDEN" for x in adj), detail=str(adj))
    check("C7 …đồng thời gói 1840 lén trên lệnh BAL vẫn bị gỡ",
          by["FPT"].loan_package_id is None)

    # Fail-closed
    plan = mkplan([o("B1", "SAB")])
    plan.orders[0].loan_package_id = 1840
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_OFF, rules_path=RULES_ON)
    check("C8 chính sách TẮT → CAPIT buy KHÔNG được cấp, cờ tự khai bị gỡ",
          plan.orders[0].loan_package_id is None
          and adj and adj[0]["action"] == "STRIPPED", detail=str(adj))

    plan = mkplan([o("B1", "SAB")])
    plan.orders[0].loan_package_id = 1840
    plan, adj = apply_capit_lever(plan, "SpaceX",
                                  status_path=os.path.join(TMP, "khong-ton-tai.json"),
                                  rules_path=RULES_ON)
    check("C9 artifact THIẾU FILE → fail-closed (gỡ, không đoán 'chắc là bật')",
          plan.orders[0].loan_package_id is None and "không đọc được" in adj[0]["reason"],
          detail=adj[0]["reason"][:90])

    stale = os.path.join(TMP, "status_stale.json")
    with open(stale, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2098-12-25", "capit_lever": lev_on}, f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan.orders[0].loan_package_id = 1840      # cờ có sẵn ⇒ ép nhánh GỠ phải thật sự chạy
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=stale, rules_path=RULES_ON)
    check("C10 artifact của signal_date KHÁC plan (stale) → KHÔNG cấp + GỠ cờ có sẵn",
          plan.orders[0].loan_package_id is None
          and adj and adj[0]["action"] == "STRIPPED" and "signal_date" in adj[0]["reason"],
          detail=str(adj))

    plan = mkplan([o("B1", "SAB")], account="ZaloPay")
    plan.orders[0].loan_package_id = 1840
    plan, adj = apply_capit_lever(plan, "ZaloPay", status_path=ART_ON, rules_path=RULES_ON)
    check("C11 account NGOÀI phạm vi (ZaloPay cash-only) → không cấp + gỡ cờ lạ",
          plan.orders[0].loan_package_id is None, detail=str(adj))

    plan = mkplan([o("B1", "TV1", cash_only=True)])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON)
    check("C12 lệnh cash_only KHÔNG bị gắn đòn bẩy (2 cơ chế chọn gói vay không chồng nhau)",
          plan.orders[0].loan_package_id is None, detail=str(adj))

    plan = mkplan([o("B1", "FPT", book="BAL"), o("B2", "TRC", book="LAG")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_OFF, rules_path=RULES_ON)
    check("C13 TẮT + plan sạch → KHÔNG có thay đổi nào (0 nhiễu vào log vận hành hằng ngày)",
          adj == [], detail=str(adj))

    # Trần VND của quyền vay (arch-reviewer H4). Slot levered = 65tr ⇒ trần = 71,5tr.
    big = o("B1", "SAB")
    big.qty, big.ref_price = 10_000, 20_000        # 200tr ≫ trần
    plan = mkplan([big, o("B2", "VNM")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON)
    by = {x.ticker: x for x in plan.orders}
    check("C14 lệnh CAPIT vượt trần VND (200tr > 71,5tr) → GỠ đòn bẩy nhưng VẪN GIỮ lệnh "
          "(under-deploy là sai số lành; vay quá mức là margin call)",
          by["SAB"].loan_package_id is None and len(plan.orders) == 2
          and any(x["action"] == "DENIED" and x["ticker"] == "SAB" for x in adj),
          detail=str([x["action"] for x in adj]))
    check("C15 …lệnh CAPIT đúng cỡ trong CÙNG plan vẫn được cấp bình thường",
          by["VNM"].loan_package_id == 1840)

    edge = o("B1", "SAB")
    edge.qty, edge.ref_price = 3_500, 20_000       # 70tr < 71,5tr (trong đệm làm tròn lô)
    plan = mkplan([edge])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON)
    check("C16 lệnh nhỉnh hơn slot nhưng trong đệm 10% (70tr) → VẪN cấp "
          "(đệm cho làm tròn lô, không chặt tay)", plan.orders[0].loan_package_id == 1840,
          detail=str(adj))

    no_tgt = os.path.join(TMP, "status_notgt.json")
    with open(no_tgt, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5}, f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=no_tgt, rules_path=RULES_ON)
    check("C17 artifact BẬT nhưng THIẾU capit_slot_targets → fail-closed, không cấp "
          "(không có trần thì không cho vay)",
          plan.orders[0].loan_package_id is None
          and adj and adj[0]["action"] == "DENIED", detail=str(adj))

    # M8: tên khoá của fixture phải khớp schema THẬT mà golive công bố — nếu §6 đổi tên
    # khoá, đây là chỗ vỡ, thay vì production âm thầm hết đòn bẩy còn test vẫn xanh.
    live_status = os.path.join(HERE, "data", "golive_v23_status.json")
    if os.path.exists(live_status):
        with open(live_status, encoding="utf-8") as f:
            live_tgts = (json.load(f) or {}).get("capit_slot_targets") or {}
        live_keys = set().union(*[set(v) for v in live_tgts.values()]) if live_tgts else set()
        check("C18 khoá fixture khớp schema capit_slot_targets THẬT của golive",
              (not live_keys) or {"capit_total_target_vnd", "capit_slot_target_vnd"} <= live_keys,
              detail=f"live_keys={sorted(live_keys) or '(rỗng — chưa có phiên CAPIT)'}")
    else:
        check("C18 khoá fixture khớp schema THẬT", False, detail="thiếu golive_v23_status.json")

    # CÔNG TẮC VẬN HÀNH ở tầng THỰC THI (arch-reviewer F1). Chuỗi thời gian thật: golive công
    # bố artifact ~19:03 → plan 21:00 → đặt lệnh 09:05 hôm sau. Nếu quyền cấp chỉ đọc artifact
    # thì trong ~14h đó `enabled=false` KHÔNG tắt được gì (công tắc duy nhất còn tác dụng là
    # BOT_STOP — dừng TOÀN BỘ giao dịch, quá tay). Hai ca dưới đây là bằng chứng: CÙNG artifact
    # BẬT của C1, chỉ đổi file chính sách ⇒ không cấp.
    plan = mkplan([o("B1", "SAB")])
    plan.orders[0].loan_package_id = 1840
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_OFF)
    check("C19 artifact BẬT nhưng trading_rules.json TẮT → KHÔNG cấp + gỡ cờ có sẵn "
          "(công tắc vận hành có tác dụng LÚC ĐẶT LỆNH, không chỉ lúc sinh tín hiệu)",
          plan.orders[0].loan_package_id is None
          and adj and adj[0]["action"] == "STRIPPED" and "enabled" in adj[0]["reason"],
          detail=(adj[0]["reason"][:90] if adj else "(không có adj)"))

    plan = mkplan([o("B1", "SAB")])
    plan.orders[0].loan_package_id = 1840
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON)   # rules_path=None ⇒ FILE THẬT
    check("C20 artifact BẬT + file chính sách THẬT (mặc định, đang TẮT) → KHÔNG cấp — "
          "trạng thái production hôm nay, kiểm bằng chính đường mặc định chứ không bằng fixture",
          plan.orders[0].loan_package_id is None and adj and adj[0]["action"] == "STRIPPED",
          detail=(adj[0]["reason"][:90] if adj else "(không có adj)"))

    # TRẦN TỔNG (arch-reviewer F4). Trần slot là PER-ORDER, `cap_capit_orders` cũng per-order,
    # còn `Executor.state["parents"]` khoá theo `o.id` chứ không theo mã ⇒ N lệnh trùng mã, mỗi
    # lệnh vừa đúng trần slot, sẽ chạy CẢ N. Tổng levered 325tr × đệm 1,10 = 357,5tr, mỗi lệnh
    # 65tr ⇒ 5 lệnh đầu (325tr) được cấp, lệnh thứ 6 (390tr) bị chặn.
    six = []
    for i in range(6):
        od = o(f"B{i}", "SAB")
        od.qty, od.ref_price = 3_250, 20_000       # 65tr = đúng slot levered
        six.append(od)
    plan = mkplan(six)
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON)
    acts = [x["action"] for x in adj]
    check("C21 6 lệnh cùng mã, mỗi lệnh ĐÚNG trần slot → 5 lệnh đầu được cấp, lệnh thứ 6 bị "
          "trần TỔNG chặn (trần slot đơn lẻ KHÔNG chặn được N lệnh trùng mã)",
          acts == ["APPLIED"] * 5 + ["DENIED"]
          and sum(1 for x in plan.orders if x.loan_package_id == 1840) == 5,
          detail=str(acts))
    check("C22 …và tổng giá trị được cấp đòn bẩy ≤ trần tổng levered × đệm (325tr ≤ 357,5tr)",
          sum(x.value for x in plan.orders if x.loan_package_id == 1840) == 325_000_000,
          detail=f"{sum(x.value for x in plan.orders if x.loan_package_id == 1840):,.0f} VND")

    no_tot = os.path.join(TMP, "status_nototal.json")
    _t_notot = copy.deepcopy(tgt_on_art)
    _t_notot["SpaceX"].pop("capit_total_target_vnd_levered", None)
    with open(no_tot, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "capit_lever": lev_on,
                   "capit_adv_caps": {"SpaceX": {t: 10 ** 12 for t in BASKET5}},
                   "capit_slot_targets": _t_notot}, f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=no_tot, rules_path=RULES_ON)
    check("C23 artifact BẬT nhưng THIẾU trần TỔNG → fail-closed (có trần slot vẫn không đủ)",
          plan.orders[0].loan_package_id is None
          and adj and adj[0]["action"] == "DENIED", detail=str(acts and adj[0]["action"]))

    # RỔ CAPIT kiểm TẠI CHỖ (arch-reviewer F5). Trước đây tính chất "chỉ mã trong rổ" chỉ đúng
    # nhờ cap_capit_orders() chạy TRƯỚC trong cascade — một hợp đồng ngầm theo thứ tự gọi ở
    # bot_execute.py, không có gì trong hàm cấp quyền vay bảo đảm. Hàm cấp tiền vay phải tự đủ.
    plan = mkplan([o("B1", "SAB"), o("B2", "HAG")])       # HAG mang nhãn CAPIT nhưng ngoài rổ
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON)
    by = {x.ticker: x for x in plan.orders}
    check("C24 lệnh nhãn book CAPIT nhưng mã NGOÀI rổ artifact → KHÔNG cấp đòn bẩy "
          "(không mượn thứ tự cascade để suy ra tư cách thành viên)",
          by["HAG"].loan_package_id is None and by["SAB"].loan_package_id == 1840
          and any(x["action"] == "DENIED" and x["ticker"] == "HAG" for x in adj),
          detail=str([(x["ticker"], x["action"]) for x in adj]))

    no_bskt = os.path.join(TMP, "status_nobasket.json")
    with open(no_bskt, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "capit_lever": lev_on,
                   "capit_slot_targets": tgt_on_art}, f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan.orders[0].loan_package_id = 1840
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=no_bskt, rules_path=RULES_ON)
    check("C25 artifact BẬT nhưng THIẾU capit_adv_caps → fail-closed toàn plan "
          "(không xác định được rổ thì không cho vay)",
          plan.orders[0].loan_package_id is None
          and adj and adj[0]["action"] == "STRIPPED" and "capit_adv_caps" in adj[0]["reason"],
          detail=(adj[0]["reason"][:90] if adj else "(không có adj)"))

    # ── TRẦN VND NEO VÀO TRƯỜNG GỐC (arch-reviewer vòng 2, phát hiện #1 — lỗ hổng CAO) ──
    # Bản vòng 1 đọc thẳng `capit_*_target_vnd_levered` của artifact làm trần. Nhưng đó CHÍNH
    # LÀ file mà F2 tuyên bố không đáng tin (bị .gitignore ⇒ không diff/blame/backup). Envelope
    # ghim trong code chỉ ép f/gói/account = ép TỶ LỆ, không ép ĐỘ LỚN. arch-reviewer probe:
    # để nguyên `f: 1.3` (qua sạch mọi cổng envelope), chỉ thổi 2 trường VND ⇒ được cấp đòn bẩy
    # 10.000.000.000 VND trên mốc 325.000.000 VND (30,8 lần). Trần giờ neo vào TRƯỜNG GỐC
    # (chưa nhân f) × CAPIT_LEVER_APPROVED_F — sửa trường gốc thì mọi con số CAPIT khác trong
    # artifact (báo cáo duyệt plan, cổng WARN 07-21) cũng lệch theo, nên nó không sửa lén được.
    blown = os.path.join(TMP, "status_blown.json")
    _t_blown = copy.deepcopy(tgt_on_art)
    _t_blown["SpaceX"]["capit_slot_target_vnd_levered"] = 10 ** 10
    _t_blown["SpaceX"]["capit_total_target_vnd_levered"] = 10 ** 10
    with open(blown, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5,
                   "capit_slot_targets": _t_blown}, f, ensure_ascii=False)
    big = o("B1", "SAB")
    big.qty, big.ref_price = 50_000, 20_000            # 1 tỷ VND — vượt xa mốc neo 65tr
    plan = mkplan([big])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=blown, rules_path=RULES_ON)
    check("C26 artifact THỔI PHỒNG trần VND (10 tỷ) trong khi f=1,3 vẫn đúng envelope → trần "
          "NEO theo trường gốc × f duyệt vẫn chặn (lỗ hổng CAO vòng 2: ép tỷ lệ ≠ ép độ lớn)",
          plan.orders[0].loan_package_id is None
          and adj and adj[0]["action"] == "DENIED",
          detail=(adj[0]["reason"][:110] if adj else "(không có adj)"))
    small = o("B1", "SAB")
    small.qty, small.ref_price = 3_250, 20_000         # 65tr = đúng mốc neo (50tr × 1,3)
    plan = mkplan([small])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=blown, rules_path=RULES_ON)
    check("C27 …nhưng lệnh ĐÚNG cỡ neo (65tr) vẫn được cấp bình thường — trần neo chặn cái "
          "phồng, KHÔNG chặn nhầm cái hợp lệ",
          plan.orders[0].loan_package_id == 1840, detail=str([x["action"] for x in adj]))

    no_base = os.path.join(TMP, "status_nobase.json")
    _t_nobase = copy.deepcopy(tgt_on_art)
    _t_nobase["SpaceX"].pop("capit_total_target_vnd", None)
    with open(no_base, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5,
                   "capit_slot_targets": _t_nobase}, f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=no_base, rules_path=RULES_ON)
    check("C28 artifact THIẾU trường GỐC `capit_total_target_vnd` → fail-closed (không có mốc "
          "độc lập nào để soi trần vay thì không cho vay, dù trường levered vẫn có)",
          plan.orders[0].loan_package_id is None
          and adj and adj[0]["action"] == "DENIED" and "GỐC" in adj[0]["reason"],
          detail=(adj[0]["reason"][:100] if adj else "(không có adj)"))

    # GIỚI HẠN CÒN LẠI, ĐƯỢC GHI NHẬN CÓ CHỦ ĐÍCH (quant-skeptic 2026-08-03, verify_20260803_143700):
    # mốc neo dùng TRƯỜNG GỐC của chính artifact, nên nó chỉ chặn được ca sửa MỘT trường
    # (thổi `_levered`, để `_gốc` trung thực) — đúng ca arch-reviewer probe hỏng. Một lần sửa
    # ĐỒNG BỘ CẢ HAI trường (gốc ×3, levered = gốc ×3 ×1,3) vẫn qua được cổng envelope lẫn
    # cổng neo, vì mọi tỷ lệ đều đúng. Cross-check duy nhất trên trường GỐC hiện nay là cổng
    # WARN 07-21 ở send_plan_report.sh, chạy lúc DUYỆT PLAN (~21:00) chứ không phải lúc THỰC
    # THI (~09:05 hôm sau) ⇒ còn khe ~12h.
    # KIỂM Ở ĐÂY ĐỂ NÓ LÀ MỘT RANH GIỚI ĐÃ BIẾT VÀ CÓ TEST, không phải một giả định êm ái:
    # nếu ai đó về sau đóng được khe này thì test này sẽ FAIL và buộc phải đọc lại đoạn văn
    # trên. Đây là lý do `capit_margin_lever.known_limits` liệt kê nó như ĐIỀU KIỆN TIÊN
    # QUYẾT phải xử lý TRƯỚC khi `enabled=true` (tính năng đang TẮT nên rủi ro chưa hiện thực).
    both = os.path.join(TMP, "status_bothfields.json")
    _t_both = copy.deepcopy(tgt_on_art)
    _t_both["SpaceX"]["capit_slot_target_vnd"] = 150_000_000          # gốc ×3
    _t_both["SpaceX"]["capit_slot_target_vnd_levered"] = 195_000_000  # = ×3 ×1,3 (tỷ lệ ĐÚNG)
    _t_both["SpaceX"]["capit_total_target_vnd"] = 750_000_000
    _t_both["SpaceX"]["capit_total_target_vnd_levered"] = 975_000_000
    with open(both, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5,
                   "capit_slot_targets": _t_both}, f, ensure_ascii=False)
    infl = o("B1", "SAB")
    infl.qty, infl.ref_price = 9_750, 20_000                          # 195tr = trần đã thổi
    plan = mkplan([infl])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=both, rules_path=RULES_ON)
    check("C29b GIỚI HẠN ĐÃ BIẾT: sửa ĐỒNG BỘ cả trường gốc lẫn levered (mọi tỷ lệ vẫn đúng) "
          "VẪN qua được — mốc neo là kiểm soát PHÁT HIỆN, không phải kiểm soát NGĂN CHẶN. "
          "Phải đóng bằng integrity-check artifact lúc thực thi TRƯỚC khi enabled=true",
          plan.orders[0].loan_package_id == 1840,
          detail="đây là hành vi ĐANG CÓ, được ghim lại để không ai tưởng khe này đã đóng")

    # ĐỆM TỔNG tách khỏi đệm per-order (#5). Giữ 1,10 ở tầng tổng biến envelope f=1,3 thành
    # 1,43 thực tế: sai số làm tròn lô của N lệnh triệt tiêu lẫn nhau chứ không cộng dồn.
    six2 = []
    for i in range(6):
        od = o(f"B{i}", "SAB")
        od.qty, od.ref_price = 3_250, 20_000
        six2.append(od)
    plan = mkplan(six2)
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON)
    _levered_total = sum(x.value for x in plan.orders if x.loan_package_id == 1840)
    check("C29 đệm TỔNG là 1,02 (không phải 1,10) → tổng cấp đòn bẩy ≤ 331,5tr, KHÔNG phải "
          "357,5tr — envelope thực tế bám f=1,3 thay vì trôi lên 1,43",
          _levered_total <= 325_000_000 * 1.02 + 1,
          detail=f"{_levered_total:,.0f} VND (trần 331.500.000)")

    # KHÔNG ĐƯỢC IM LẶNG khi plan đã sizing levered mà đòn bẩy lại TẮT (#3a). Kịch bản thật:
    # artifact có đòn bẩy lúc 19:03 → plan sizing 1,3× lúc 21:00 → người vận hành tắt
    # `enabled=false` trong đêm. Lệnh không mang cờ sẵn nên vòng lặp không có gì để "GỠ" ⇒
    # adj rỗng ⇒ bot_execute in 0 dòng, và triệu chứng duy nhất là WAIT_CASH "thiếu tiền".
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_OFF)
    check("C30 chính sách TẮT nhưng artifact ĐÃ có mục tiêu nhân f → cảnh báo cấp-PLAN "
          "(trước đây im lặng 0 dòng: plan sizing 1,3× chạy bằng vốn 1,0×, chỉ hiện ra dưới "
          "dạng WAIT_CASH không phân biệt được với thiếu tiền thường)",
          any(x["action"] == "PLAN_SIZED_LEVERED_BUT_OFF" for x in adj)
          and plan.orders[0].loan_package_id is None,
          detail=str([x["action"] for x in adj]))
    check("C31 …và cảnh báo đó chỉ ra BOT_STOP là công cụ dừng giữa phiên, không phải "
          "enabled=false (tắt cấp vốn KHÔNG đổi khối lượng plan đã chốt)",
          any("BOT_STOP" in x["reason"] for x in adj
              if x["action"] == "PLAN_SIZED_LEVERED_BUT_OFF"))

    # ─────────────────── D. Tầng broker ───────────────────
    section("D. Broker (brokers.py :: _validate_lever_package / place_order)")

    class _FakeDNSEClient:
        loan_package_id = 1841        # gói default account

        def __init__(self, pkgs=(1840, 1841), boom=False):
            self.pkgs, self.boom, self.calls = pkgs, boom, []

        def loan_packages(self, acc, symbol=None):
            if self.boom:
                raise RuntimeError("mạng lỗi")
            return [{"id": p} for p in self.pkgs]

        def place_order(self, acc, symbol, qty=None, side=None, order_type=None,
                        price=None, loan_package_id=None):
            self.calls.append({"symbol": symbol, "loan_package_id": loan_package_id})
            return {"id": f"D{len(self.calls)}"}

    def mkbroker(**kw):
        b = DNSEBroker.__new__(DNSEBroker)
        b.account_id = "0002023347"
        b.label = "SpaceX"
        b.client = _FakeDNSEClient(**kw)
        b._lever_pkg_cache = {}
        b._loan_pkg_cache = {}
        b._raw_log = os.path.join(TMP, "raw.jsonl")
        return b

    b = mkbroker()
    got, ok, note = b._validate_lever_package("SAB", 1840)
    check("D1 gói 1840 hợp lệ cho mã → dùng đúng 1840", got == 1840 and ok is True)

    b = mkbroker(pkgs=(1841,))
    got, ok, note = b._validate_lever_package("SAB", 1840)
    check("D2 gói 1840 KHÔNG hợp lệ cho mã → rơi về gói default 1841, KHÔNG đòn bẩy "
          "(chiều fail-safe đúng)", got == 1841 and ok is False, detail=note)

    b = mkbroker(boom=True)
    got, ok, note = b._validate_lever_package("SAB", 1840)
    check("D3 không kiểm được danh sách gói (mạng lỗi) → default 1841, không đòn bẩy",
          got == 1841 and ok is False, detail=note)

    b = mkbroker()
    b.place_order("SAB", 1000, "buy", price=20000, loan_package_id=1840)
    check("D4 place_order truyền ĐÚNG gói 1840 xuống client khi hợp lệ",
          b.client.calls[-1]["loan_package_id"] == 1840, detail=str(b.client.calls[-1]))

    b = mkbroker(pkgs=(1841,))
    b.place_order("SAB", 1000, "buy", price=20000, loan_package_id=1840)
    check("D5 gói không hợp lệ → vẫn GỬI trường (default 1841), KHÔNG bỏ trắng "
          "(bug TV1 07-28: thiếu trường = HTTP 400)",
          b.client.calls[-1]["loan_package_id"] == 1841, detail=str(b.client.calls[-1]))

    b = mkbroker()
    b.place_order("FPT", 1000, "buy", price=20000)
    check("D6 lệnh THƯỜNG (không đòn bẩy, không cash_only) → loan_package_id=None, "
          "hành vi cũ nguyên vẹn", b.client.calls[-1]["loan_package_id"] is None)

    # ─────────────────── E. Lưới an toàn runtime ───────────────────
    section("E. Lưới an toàn runtime (executor.py :: _lever_package_audit)")

    class _NullBroker:
        name = "null"

        def get_quote(self, *a, **k):
            raise AssertionError("get_quote không được chạm tới — guard phải chặn trước")

        def place_order(self, *a, **k):
            raise AssertionError("place_order chạy trên mã ĐÃ bị tạm dừng — guard hỏng!")

        def cancel_order(self, *a, **k):
            return None

        def get_cash(self):
            return 10 ** 12

        def poll_orders(self):
            return {}

    def mkexec(orders, tmpdir, account=TAG):
        cfg = load_config()
        cfg["mode"] = "paper"
        ex = Executor(mkplan(orders, account=account), _NullBroker(), cfg, shared={})
        ex.state_file = os.path.join(tmpdir, f"state_{account}.json")
        ex.journal_file = os.path.join(tmpdir, f"journal_{account}.csv")
        return ex

    lev_orders = [o("B1", "SAB"), o("B2", "FPT", book="BAL")]
    lev_orders[0].lever_f, lev_orders[0].loan_package_id = 1.3, 1840
    ex = mkexec(lev_orders, TMP)

    upd = {"1": OrderUpdate("1", "Filled", 1000, 20000,
                            raw={"symbol": "SAB", "loanPackageId": 1840})}
    pause, warns = ex._lever_package_audit(upd)
    check("E1 lệnh mang gói 1840 trên mã ĐƯỢC CẤP PHÉP → không tạm dừng", pause == set(),
          detail=str(pause))

    upd = {"2": OrderUpdate("2", "Filled", 1000, 20000,
                            raw={"symbol": "FPT", "loanPackageId": 1840})}
    pause, warns = ex._lever_package_audit(upd)
    check("E2 gói 1840 trên mã KHÔNG được cấp phép → TẠM DỪNG mã đó "
          "(đòn bẩy không ai duyệt, dù KL/mã đều khớp plan)", pause == {"FPT"},
          detail=str(warns))

    upd = {"3": OrderUpdate("3", "Filled", 1000, 20000,
                            raw={"symbol": "FPT", "loanPackageId": 1841})}
    pause, warns = ex._lever_package_audit(upd)
    check("E3 gói DEFAULT 1841 trên lệnh thường → không tạm dừng (không báo động giả)",
          pause == set(), detail=str(pause))

    # LỆNH ĐÃ CHẾT, CHƯA KHỚP GÌ → không có nợ vay nào phát sinh (arch-reviewer vòng 2, #4).
    # Đối xứng với _ghost_tickers, vốn đã bỏ qua ca này từ lâu. Thiếu dòng bỏ qua đó thì một
    # lệnh 1840 bị HUỶ với 0 CP khớp vẫn treo mã đó hết ngày — mất giao dịch vì một lệnh
    # không hề tồn tại về mặt tiền bạc.
    upd = {"5": OrderUpdate("5", "Cancelled", 0, None,
                            raw={"symbol": "FPT", "loanPackageId": 1840})}
    pause, warns = ex._lever_package_audit(upd)
    check("E3b lệnh gói 1840 ĐÃ HUỶ và 0 CP khớp → KHÔNG tạm dừng (không phát sinh nợ vay; "
          "đối xứng với _ghost_tickers)", pause == set(), detail=str(pause))

    # Chỉ TẠM DỪNG mã CÓ trong plan: pause một mã hôm nay không giao dịch thì không chặn được
    # gì (không có lệnh nào để chặn) mà chỉ gây nhiễu. Vẫn phải CẢNH BÁO để người thật biết
    # có đòn bẩy lạ trên tài khoản.
    upd = {"6": OrderUpdate("6", "Filled", 1000, 20000,
                            raw={"symbol": "VIC", "loanPackageId": 1840})}
    pause, warns = ex._lever_package_audit(upd)
    check("E3c gói 1840 trên mã NGOÀI plan hôm nay → không tạm dừng (vô ích) NHƯNG vẫn cảnh "
          "báo (người thật cần biết có đòn bẩy lạ trên tài khoản)",
          pause == set() and any(w["ticker"] == "VIC" and w["in_plan"] is False for w in warns),
          detail=str(warns))

    # Guard phải còn hiệu lực NGAY CẢ KHI plan không xin đòn bẩy (trạng thái hôm nay)
    art_dir = os.path.join(TMP, "wk", "data")
    os.makedirs(art_dir, exist_ok=True)
    with open(os.path.join(art_dir, "golive_v23_status.json"), "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "capit_lever": lev_off}, f, ensure_ascii=False)
    import trading_bot.config as _cfgmod
    _real_workdir = _cfgmod.WORKDIR
    _cfgmod.WORKDIR = os.path.dirname(art_dir)
    try:
        ex_clean = mkexec([o("B1", "FPT", book="BAL")], TMP, account=TAG + "2")
        upd = {"4": OrderUpdate("4", "Filled", 1000, 20000,
                                raw={"symbol": "FPT", "loanPackageId": 1840})}
        pause, warns = ex_clean._lever_package_audit(upd)
        check("E4 plan KHÔNG xin đòn bẩy (chính sách đang tắt) nhưng broker hiện lệnh gói "
              "1840 → VẪN tạm dừng (guard vũ trang cả khi tính năng tắt)", pause == {"FPT"},
              detail=str(warns))
    finally:
        _cfgmod.WORKDIR = _real_workdir

    # Tích hợp: mã bị guard bắt phải không được đặt lệnh mới
    ex3 = mkexec([o("B1", "FPT", book="BAL")], TMP, account=TAG + "3")
    try:
        ex3._place_slices(_dt.datetime(2099, 1, 2, 9, 20), "MORNING", ghost_tickers={"FPT"})
        check("E5 _place_slices BỎ QUA mã bị tạm dừng, không gọi broker", True)
    except AssertionError as e:
        check("E5 _place_slices BỎ QUA mã bị tạm dừng, không gọi broker", False, detail=str(e))

    # E6 — MỐI NỐI, phần arch-reviewer chỉ ra là chỗ DUY NHẤT chưa có test: E1–E4 gọi thẳng
    # _lever_package_audit, E5 tự tay bơm ghost_tickers. Bản thân dòng nối
    # `ghost_tickers |= lever_pause` trong step() thì chưa ai chứng minh. Ở đây chạy step()
    # THẬT với broker trả về đúng 1 lệnh mang gói 1840 trên mã KHÔNG được cấp phép, rồi
    # bắt xem step() có chuyển mã đó xuống _place_slices dưới dạng bị tạm dừng hay không
    # (khuôn H1 của ghost_order_selfcheck.py).
    class _LeverPollBroker(_NullBroker):
        # Lệnh con còn SỐNG, chưa khớp: parent vẫn còn phần dư ⇒ step() thật sự đi tới
        # _place_slices (nếu để Filled đủ KL thì plan coi như xong và tầng đặt lệnh không
        # bao giờ được gọi — bài test sẽ "xanh" mà chẳng kiểm được mối nối nào).
        def poll_orders(self):
            return {"9": OrderUpdate("9", "New", 0, None,
                                     raw={"symbol": "FPT", "loanPackageId": 1840})}

    ex4 = mkexec([o("B1", "FPT", book="BAL")], TMP, account=TAG + "4")
    ex4.broker = _LeverPollBroker()
    # Đăng ký oid "9" là lệnh con ĐÃ BIẾT ⇒ lưới ghost bỏ qua nó (ghost_order_selfcheck A1).
    # Không có bước này thì ghost guard cũng tạm dừng FPT và bài test PASS vì lý do SAI —
    # đúng cái bẫy đã xảy ra thật ở bản nháp đầu: `_lever_package_audit` trả (set(), []) mà
    # test vẫn xanh vì ghost guard che mất. Ở đây chỉ lưới ĐÒN BẨY mới có thể tạm dừng.
    ex4.state["parents"]["B1"]["children"].append(
        {"oid": "9", "qty": 300, "price": 20000, "filled": 0, "status": "open",
         "ts": "2099-01-02T09:15:00"})
    check("E6a tiền đề: lưới GHOST KHÔNG bắt lệnh này (oid đã biết) — nên mọi lần tạm dừng "
          "dưới đây chỉ có thể đến từ lưới đòn bẩy",
          ex4._ghost_tickers(_LeverPollBroker().poll_orders()) == set(),
          detail=str(ex4._ghost_tickers(_LeverPollBroker().poll_orders())))
    seen = {}
    ex4._place_slices = lambda now, phase, ghost_tickers=(), positions=None: \
        seen.update(place_slices=set(ghost_tickers))
    ex4._atc_sweep = lambda ghost_tickers=(), positions=None: \
        seen.update(atc_sweep=set(ghost_tickers))
    ex4.step(_dt.datetime(2099, 1, 2, 9, 20), "MORNING", True)
    check("E6 step() THẬT chuyển mã bị lưới đòn bẩy bắt xuống tầng đặt lệnh dưới dạng TẠM "
          "DỪNG (mối nối `ghost_tickers |= lever_pause`, trước đây chỉ có văn xuôi bảo đảm)",
          seen.get("place_slices") == {"FPT"}, detail=str(seen))
    check("E7 …và sự cố được ghi ra bus dưới dạng LEVER_PACKAGE_UNAUTHORIZED",
          "_lever_warned" in ex4.state and "FPT" in ex4.state["_lever_warned"],
          detail=str(ex4.state.get("_lever_warned")))

    # ─────────────────── F. DIỄN TẬP ĐẦU–CUỐI trên PaperBroker ───────────────────
    section("F. DIỄN TẬP đầu–cuối (paper): tín hiệu → artifact → plan → lệnh")

    def rehearse(rules_dir, tag):
        """Chạy trọn: §6a THẬT → artifact → apply_capit_lever → PaperBroker.place_order.
        Trả (capit_lever, {ticker: loanPackageId trên sổ lệnh paper})."""
        lever, targets = run_block(rules_dir, dd52=-25.0, signal=True, size=0.50,
                                   basket=BASKET5, targets=base_targets())
        art = os.path.join(TMP, f"art_{tag}.json")
        with open(art, "w", encoding="utf-8") as f:
            json.dump({"signal_date": "2099-01-01", "capit_lever": lever,
                       "capit_adv_caps": ADV_CAPS5,
                       "capit_slot_targets": targets}, f, ensure_ascii=False)
        orders = [o(f"B{i}", tk) for i, tk in enumerate(BASKET5)]
        orders.append(o("BX", "FPT", book="BAL"))
        plan = mkplan(orders)
        # CÙNG file chính sách chạy CẢ HAI tầng (tín hiệu §6a qua `rules_dir`, thực thi qua
        # `rules_path`) — đúng như production, nơi hai tầng đọc chung `data/trading_rules.json`.
        plan, adj = apply_capit_lever(
            plan, "SpaceX", status_path=art,
            rules_path=os.path.join(rules_dir, "data", "trading_rules.json"))

        pb = PaperBroker(label=f"{TAG}-{tag}", init_cash=10 ** 10)
        pb.state_file = os.path.join(TMP, f"paper_{tag}.json")
        pb.state = {"cash": 10 ** 10, "positions": {}, "open_orders": {},
                    "fills": [], "next_id": 1}
        for od in plan.orders:
            pb.place_order(od.ticker, od.qty, od.side, price=od.ref_price,
                           loan_package_id=od.loan_package_id)
        book = {v["symbol"]: v.get("loanPackageId") for v in pb.state["open_orders"].values()}
        return lever, book, targets, adj

    lever_on, book_on, tgt_on, adj_on = rehearse(d_on, "on")
    check("F1 [BẬT] tín hiệu công bố active=True", lever_on["active"] is True)
    check("F2 [BẬT] cả 5 lệnh CAPIT tới broker mang gói 1840 — cờ KHÔNG rớt ở lớp nào",
          all(book_on.get(t) == 1840 for t in BASKET5),
          detail=str({t: book_on.get(t) for t in BASKET5}))
    check("F3 [BẬT] lệnh BAL cùng plan vẫn KHÔNG mang gói vay",
          book_on.get("FPT") is None, detail=str(book_on.get("FPT")))
    check("F4 [BẬT] mục tiêu vốn levered = 65tr/mã (50tr × 1,3)",
          tgt_on["SpaceX"]["capit_slot_target_vnd_levered"] == 65_000_000)

    lever_off2, book_off, tgt_off2, adj_off = rehearse(d_off, "off")
    check("F5 [TẮT — cấu hình production hôm nay] active=False",
          lever_off2["active"] is False)
    check("F6 [TẮT] KHÔNG lệnh nào mang gói vay (kể cả 5 lệnh CAPIT)",
          all(v is None for v in book_off.values()), detail=str(book_off))
    check("F7 [TẮT] KHÔNG có trường sizing levered nào → tầng dưới thấy hệ y hệt V2.4",
          not any("lever" in k for k in tgt_off2["SpaceX"]))
    check("F8 [TẮT] cascade không sinh thay đổi nào (0 dòng adj)", adj_off == [],
          detail=str(adj_off))

    # ─────────────────── G. Chốt chặn cấu hình thật ───────────────────
    section("G. Chốt chặn: cấu hình THẬT trên đĩa")
    with open(REAL_RULES, encoding="utf-8") as f:
        real_blk = json.load(f)["capit_margin_lever"]
    check("G1 data/trading_rules.json :: capit_margin_lever.enabled == false",
          real_blk["enabled"] is False, detail=f"enabled={real_blk['enabled']!r}")
    check("G2 …live_requires_user_approval == true",
          real_blk.get("live_requires_user_approval") is True)
    check("G3 …phạm vi đúng bản duyệt: f=1,3 · gói 1840 · capit_only · chỉ SpaceX",
          real_blk["f"] == 1.3 and real_blk["loan_package_id"] == 1840
          and real_blk["scope"] == "capit_only" and real_blk["accounts"] == ["SpaceX"])

    # ───────── H. Cổng đối chiếu cỡ deploy ở BƯỚC DUYỆT (mike/bin/send_plan_report.sh) ─────────
    # Trích NGUYÊN VĂN đoạn python trong heredoc production rồi chạy (§17 extract-and-test):
    # đây là dòng chữ người duyệt đọc lúc 21:00 trước khi bấm duyệt, không phải log nội bộ.
    section("H. Cổng WARN cỡ deploy lúc duyệt plan (bin/send_plan_report.sh)")

    SPR = os.path.join(HERE, "mike", "bin", "send_plan_report.sh")
    with open(SPR, encoding="utf-8") as f:
        _spr = f.read()
    _beg = "# ── CAPIT: Σ lệnh mua thật vs VND mục tiêu đã publish"
    _end = 'lines = [f"📋'
    check("H0 trích được đoạn đối chiếu CAPIT từ send_plan_report.sh production",
          _spr.count(_beg) == 1 and _spr.count(_end) == 1)
    CAPIT_NOTE_SRC = _spr.split(_beg, 1)[1].split(_end, 1)[0]

    def run_note(art_blob, orders_vnd, acct="SpaceX"):
        """Chạy đoạn production thật trong tmpdir có data/golive_v23_status.json giả lập."""
        d = os.path.join(TMP, f"spr_{abs(hash(json.dumps(art_blob, sort_keys=True)))}")
        os.makedirs(os.path.join(d, "data"), exist_ok=True)
        with open(os.path.join(d, "data", "golive_v23_status.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(art_blob, fh, ensure_ascii=False)
        cwd0 = os.getcwd()
        ns = {"json": json, "os": os, "acct": acct,
              "orders": [{"book": "CAPIT", "side": "buy", "qty": 1, "ref_price": v}
                         for v in orders_vnd],
              "_order_price": lambda o: o.get("ref_price", o.get("mtm_price_ref",
                                                                 o.get("price")))}
        try:
            os.chdir(d)
            exec(_beg + CAPIT_NOTE_SRC, ns)
        finally:
            os.chdir(cwd0)
        return ns["capit_note"]

    _tg_lev = {"SpaceX": {"capit_slot_target_vnd": 50_000_000,
                          "capit_slot_target_vnd_levered": 65_000_000}}
    _art_lever_on = {"capit_lever": {"active": True, "accounts": ["SpaceX"], "f": 1.3,
                                     "loan_package_id": 1840},
                     "capit_slot_targets": _tg_lev}
    _art_lever_off = {"capit_lever": {"active": False, "accounts": ["SpaceX"]},
                      "capit_slot_targets": {"SpaceX": {"capit_slot_target_vnd": 50_000_000}}}

    n_on = run_note(_art_lever_on, [65_000_000] * 5)
    check("H1 đòn bẩy BẬT + lệnh sizing theo slot ĐÃ nhân f → KHÔNG có cảnh báo sai "
          "(mốc so cùng cơ sở với mốc đã sizing)",
          n_on.startswith("✅") and "nhân capit_size hai lần" not in n_on, detail=n_on[:110])
    check("H2 …và nói rõ mốc so là slot đã nhân f (người duyệt biết mình đang đọc cơ sở nào)",
          "đòn bẩy CAPIT ĐANG BẬT" in n_on and "1840" in n_on, detail=n_on[-95:])

    n_off = run_note(_art_lever_off, [65_000_000] * 5)
    check("H3 đòn bẩy TẮT + CÙNG bộ lệnh 65tr → VẪN cảnh báo lệch +30% "
          "(cổng 07-21 không bị fix này làm cùn đi)",
          n_off.startswith("⚠️") and "nhân capit_size hai lần" in n_off, detail=n_off[:100])

    n_bad = run_note({"capit_lever": {"active": True, "accounts": ["SpaceX"], "f": 1.3},
                      "capit_slot_targets": {"SpaceX": {"capit_slot_target_vnd": 50_000_000}}},
                     [65_000_000] * 5)
    check("H4 BẬT nhưng artifact thiếu trường levered → nói thẳng 'lệch dương ~f là bình "
          "thường', KHÔNG lặng lẽ in cảnh báo sai với vẻ chắc chắn",
          "thiếu `capit_slot_target_vnd_levered`" in n_bad, detail=n_bad[-110:])

    n_real = run_note(_art_lever_on, [40_000_000] * 5)
    check("H5 BẬT nhưng lệnh sizing SAI cỡ thật (40tr vs 65tr) → vẫn cảnh báo "
          "(fix này chỉ đổi MỐC SO, không tắt cổng)",
          n_real.startswith("⚠️") and "-38" in n_real, detail=n_real[:100])

print(f"\nENV: TZ={os.environ.get('TZ', '(không đặt)')!r} · "
      f"python={sys.version.split()[0]} · cwd={os.getcwd()}")
if fails:
    print(f"\n❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("\n✅ tất cả PASS — đòn bẩy CAPIT đã wire trọn đường và ĐANG TẮT")
