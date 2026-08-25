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
import builtins
import copy
import csv
import dataclasses
import datetime as _dt
import glob
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# Test-mode: KHÔNG cho Executor._publish_bot_event ghi event GIẢ vào bus production
# (retro-2026-08-07 Pattern 1 — 4 lần tái diễn 08-03/04/05/07). Xem coding_guidelines §5.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

sys.path.insert(0, HERE)

from trading_bot.brokers import OrderUpdate, PaperBroker, DNSEBroker  # noqa: E402
import trading_bot.plan as _planmod  # noqa: E402
from trading_bot.plan import (PlannedOrder, TradePlan, apply_capit_lever,  # noqa: E402
                             margin_day_approval, lever_live_preflight)
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.config import load_config, EXEC_DIR  # noqa: E402
from trading_bot.account_ids import SPACEX as SPACEX_ACCOUNT, ZALOPAY as ZALOPAY_ACCOUNT

GOLIVE = os.path.join(HERE, "deploy_golive_dt5g_v4", "golive_recommend_v23.py")
REAL_RULES = os.path.join(HERE, "data", "trading_rules.json")

# Executor.__init__ nạp state.json theo (account, plan_date) NGAY trong constructor, trước
# khi test kịp trỏ sang tmpdir → file sót của lần chạy trước làm bẩn state khởi đầu. Tag
# riêng + dọn sạch trước mỗi lần chạy (đúng khuôn ghost_order_selfcheck.py).
TAG = "selfcheck-lever"
for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(_f)

# NGUỒN `state` ĐỘC LẬP DÙNG CHO TEST — KHÔNG đọc file production.
# `_verify_targets_integrity` neo trần `capit_size`/`w_lag_target` theo `state` và chốt state
# đó bằng nguồn thứ hai (`deploy_golive_dt5g_v4/golive_state_today.json`). Nếu test đọc file
# THẬT thì mọi ca kiểm sẽ đổi kết quả theo regime của hôm chạy — đúng loại phụ thuộc môi
# trường mà skill verify-before-done bắt phải khai và loại bỏ. Fixture ghim state 3 (NEUTRAL,
# trần capit_size 0,75) nên các ca C* có nghĩa cố định mọi ngày.
_STATE_FIX = os.path.join(EXEC_DIR, f"exec_{TAG}_state_today.json")   # tiền tố `exec_` để
with open(_STATE_FIX, "w", encoding="utf-8") as _f:                  # glob dọn dẹp trên quét
    json.dump({"state": 3, "as_of": "2099-01-01",                    # được (vòng 4 #7)
               "source": "selfcheck-fixture"}, _f)

_apply_real = apply_capit_lever


def apply_capit_lever(*a, **kw):        # noqa: F811 — bọc để mọi ca kiểm dùng state fixture
    kw.setdefault("state_path", _STATE_FIX)
    return _apply_real(*a, **kw)


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


def extract_func(src, name, where=None):
    """Source của đúng 1 def top-level trong `src` (AST, không regex)."""
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node)
    raise AssertionError(f"không tìm thấy def {name}() trong {where or GOLIVE}")


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


# Ngày mặc định cho `LATEST` khi ca kiểm không cố tình test PIT filter (CPI ~3,9%/lãi suất
# huy động 7,0% theo anchor 2019 — cả hai đều dưới ngưỡng CAPIT_LEVER_PIT_*_THRESHOLD, PIT
# filter cho qua) — giữ MỌI ca kiểm A-F đã có tiếp tục kiểm ĐÚNG thứ chúng đang kiểm (dd52/
# công tắc/cổng), không bị PIT filter mới xen vào làm sai lệch kết quả.
_PIT_PASS_DEFAULT_DATE = _dt.datetime(2019, 6, 1)


def run_block(rules_dir, *, dd52, signal, size, basket, targets, latest=None):
    """Chạy §6a THẬT với đầu vào giả lập → (capit_lever dict, capit_targets sau khi chạy)."""
    ns = {"os": os, "json": json, "pd": _FakePd, "WORKDIR": rules_dir,
          "dd52_now": dd52, "capit_signal_today": signal, "capit_size": size,
          "basket": list(basket), "capit_targets": copy.deepcopy(targets),
          "LATEST": latest or _PIT_PASS_DEFAULT_DATE,
          **CONSTS}
    exec(POLICY_SRC, ns)
    exec(BLOCK_SRC, ns)
    return ns["capit_lever"], ns["capit_targets"]


def base_targets():
    """Fixture phải mang ĐỦ BA THỪA SỐ mà golive công bố (nav_basis × w_lag × capit_size), vì
    `_verify_targets_integrity` (2026-08-03, đóng khe C29b) đối chiếu chính ba đẳng thức đó.
    Số ở đây khớp nhau đúng như production: 1,0 tỷ × 0,50 = 500tr book → × 0,50 = 250tr tổng
    → / 5 slot = 50tr/slot."""
    return {"SpaceX": {"nav_basis_vnd": 1_000_000_000, "w_lag_target": 0.50,
                       "capit_size": 0.50,
                       "nav_book_lag_vnd": 500_000_000, "capit_total_target_vnd": 250_000_000,
                       "capit_slot_target_vnd": 50_000_000, "n_slots": 5},
            "ZaloPay": {"nav_basis_vnd": 400_000_000, "w_lag_target": 0.50,
                        "capit_size": 0.50,
                        "nav_book_lag_vnd": 200_000_000, "capit_total_target_vnd": 100_000_000,
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

    # ─── B-PIT. Bộ lọc PIT Loại 1 (STRUCTURAL) vs Loại 2 (CONTAINABLE) — job
    # Taylor_20260825_042209. Dùng NGÀY THẬT (không mock giá trị CPI/deposit_rate) để chạy
    # đúng cpi_vn.py/deposit_rate_vn.py thật, giống cách B1-B10 chạy đúng §6a thật — nếu ai
    # sửa ngưỡng hay đổi anchor mà đổi phân loại của 1 trong các ngày mốc này, test này fail.
    section("B-PIT. PIT filter Loại 1/Loại 2 (CPI YoY / lãi suất huy động)")

    lev, tgt = run_block(d_on, dd52=-25.0, signal=True, size=0.50,
                         basket=BASKET5, targets=base_targets(),
                         latest=_dt.datetime(2011, 7, 15))
    check("B11 ngày Loại-1 THẬT (2011-07-15, đuôi mega-crisis 2007-2012, CPI YoY thật ~21,6%) "
          "→ active=False dù dd52/cổng/tín hiệu đều ĐẠT, pit_filter_structural=True",
          lev["active"] is False and lev["pit_filter_structural"] is True
          and lev["gate_pass"] is True and "CƠ CẤU" in lev["pit_filter_reason"],
          detail=f"cpi={lev['pit_cpi_yoy']} deposit={lev['pit_deposit_rate']} "
                 f"reason={lev['pit_filter_reason']}")
    check("B11b …không trường lever nào bị gắn vào targets khi PIT chặn",
          not any("lever" in k for k in tgt["SpaceX"]), detail=str(list(tgt["SpaceX"])))

    lev, tgt = run_block(d_on, dd52=-25.0, signal=True, size=0.50,
                         basket=BASKET5, targets=base_targets(),
                         latest=_dt.datetime(2012, 8, 27))
    check("B11c ngày Loại-1 THẬT, đuôi cluster (2012-08-27, CPI YoY thật ~6,87% — sát ngưỡng "
          "6,0%) → VẪN active=False (chặn đúng ca biên, không lọt qua vì gần ngưỡng)",
          lev["active"] is False and lev["pit_filter_structural"] is True,
          detail=f"cpi={lev['pit_cpi_yoy']} deposit={lev['pit_deposit_rate']}")

    lev, tgt = run_block(d_on, dd52=-25.0, signal=True, size=0.50,
                         basket=BASKET5, targets=base_targets(),
                         latest=_dt.datetime(2022, 6, 1))
    check("B12 ngày Loại-2 THẬT (2022-06-01, giữa episode SCB/Fed-hiking, CPI YoY thật ~3,4%) "
          "→ active=True, PIT filter CHO QUA (không chặn oan khủng hoảng niềm tin/thanh khoản)",
          lev["active"] is True and lev["pit_filter_structural"] is False,
          detail=f"cpi={lev['pit_cpi_yoy']} deposit={lev['pit_deposit_rate']} "
                 f"reason={lev['pit_filter_reason']}")
    check("B12b …có trường lever khi PIT cho qua + mọi cổng khác đạt",
          tgt["SpaceX"].get("lever_f") == 1.3, detail=str(tgt["SpaceX"].get("lever_f")))

    lev, tgt = run_block(d_on, dd52=-25.0, signal=True, size=0.50,
                         basket=BASKET5, targets=base_targets(),
                         latest=_dt.datetime(2008, 9, 1))
    check("B13 ngày TRƯỚC 2011-01 (2008-09-01, chính đáy sâu nhất mega-crisis, dd52 thật "
          "-71,0%) → CPI/deposit_rate KHÔNG có anchor (NaN) → fail-closed COI NHƯ Loại 1, "
          "active=False. GIỚI HẠN PHẢI GHI RÕ: đây là fail-closed vì THIẾU DỮ LIỆU, KHÔNG "
          "phải bằng chứng bộ lọc đã được xác nhận trên chính ngày này",
          lev["active"] is False and lev["pit_filter_structural"] is True
          and lev["pit_cpi_yoy"] is None and lev["pit_deposit_rate"] is None
          and "NaN" in lev["pit_filter_reason"],
          detail=f"reason={lev['pit_filter_reason']}")

    lev, tgt = run_block(d_on, dd52=-25.0, signal=True, size=0.50,
                         basket=BASKET5, targets=base_targets())
    check("B14 fixture mặc định (không truyền `latest`, dùng _PIT_PASS_DEFAULT_DATE 2019-06) "
          "vẫn PIT-pass — bảo vệ ca B1-B10 phía trên khỏi bị PIT filter âm thầm đổi kết quả "
          "nếu sau này ai đó sửa ngưỡng/anchor",
          lev["pit_filter_structural"] is False, detail=str(lev["pit_filter_reason"]))

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
            json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": blob,
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

    # CỔNG DUYỆT RIÊNG TỪNG NGÀY CÓ VAY (user chốt 2026-08-03) là cổng NGƯỜI thứ hai, độc lập
    # với công tắc tổng. Nhóm C/F kiểm logic ARTIFACT/ENVELOPE, nên phải trỏ nó vào một bản
    # ghi duyệt HỢP LỆ ở tmpdir — cùng lý lẽ RULES_ON ở ngay trên: nếu không, mọi ca "được
    # cấp" sẽ đỏ vì thiếu duyệt chứ không vì điều đang được kiểm ("PASS/FAIL vì lý do SAI").
    # CHÍNH cổng duyệt được kiểm RIÊNG ở nhóm I, ở đó gọi thẳng `_apply_raw` KHÔNG qua wrapper.
    APPROVALS_OK = os.path.join(TMP, "approvals_ok")
    os.makedirs(APPROVALS_OK, exist_ok=True)

    def write_approval(d, account="SpaceX", plan_date="2099-01-02", **over):
        rec = {"account": account, "plan_date": plan_date,
               "approved_by": "user (selfcheck) — xác nhận trong hội thoại",
               "approved_at": "2099-01-01T21:37:00+07:00",
               "lever_f": _planmod.CAPIT_LEVER_APPROVED_F,
               "loan_package_id": _planmod.CAPIT_LEVER_APPROVED_PACKAGE,
               "max_lever_total_vnd": 10 ** 12,
               "tickers": sorted(set(BASKET5) | {"FPT", "TRC", "HAG", "TV1"})}
        rec.update(over)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, f"margin_approval_{rec['account']}_{rec['plan_date']}.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False)
        return p

    write_approval(APPROVALS_OK)
    write_approval(APPROVALS_OK, account="ZaloPay")     # để C11 đỏ vì PHẠM VI, không vì duyệt

    _apply_raw = apply_capit_lever

    def apply_capit_lever(plan, account_label, status_path=None, rules_path=None, **kw):
        kw.setdefault("approvals_dir", APPROVALS_OK)
        return _apply_raw(plan, account_label, status_path=status_path,
                          rules_path=rules_path, **kw)

    def mkplan(orders, account="SpaceX"):
        return TradePlan(plan_date="2099-01-02", signal_date="2099-01-01",
                         strategy="selfcheck", strategy_version="0", state=1,
                         state_name="CRISIS", nav_basis={"account_nav": 1e9, "scale": 1.0},
                         orders=orders, account=account,
                         # RỖNG = đúng production (vòng 6): plan thật do DollarBill/người sinh
                         # KHÔNG có khoá `created_at`; chỉ `TradePlan.save()` mới điền, mà
                         # production không đi qua đường đó. Fixture điền chuỗi ISO giả sẽ làm
                         # mọi ca `created_at` PASS mà không chứng minh được gì về đường thật.
                         created_at="")

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
        json.dump({"signal_date": "2098-12-25", "state": 3, "capit_lever": lev_on}, f, ensure_ascii=False)
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
        json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5}, f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=no_tgt, rules_path=RULES_ON)
    check("C17 artifact BẬT nhưng THIẾU capit_slot_targets → fail-closed, không cấp "
          "(không có trần thì không cho vay) VÀ để lại 1 dòng cho người đọc log — artifact "
          "hỏng không được trông giống một ngày không có sự kiện CAPIT",
          plan.orders[0].loan_package_id is None
          and adj and adj[0]["action"] == "LEVER_REFUSED_ARTIFACT_ACTIVE", detail=str(adj))

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
        json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_on,
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
        json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_on,
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
        json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_on,
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
        json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5,
                   "capit_slot_targets": _t_nobase}, f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=no_base, rules_path=RULES_ON)
    check("C28 artifact THIẾU trường GỐC `capit_total_target_vnd` → fail-closed (không có mốc "
          "độc lập nào để soi trần vay thì không cho vay, dù trường levered vẫn có)",
          plan.orders[0].loan_package_id is None
          and adj and "capit_total_target_vnd" in adj[0]["reason"],
          detail=(adj[0]["reason"][:110] if adj else "(không có adj)"))
    # Từ 2026-08-03 ca này bị `_verify_targets_integrity` bắt SỚM HƠN (trường gốc cũng là một
    # thừa số phải tự kiểm) nên `action` là cảnh báo cấp-plan chứ không còn là DENIED per-order.
    # Cả hai đều fail-closed; ghi rõ ở đây để lần sau không ai đọc nhầm là nới lỏng.
    check("C28b …và lý do nói thẳng THIẾU THỪA SỐ nào, không im lặng bỏ qua",
          any("thiếu thừa số" in x["reason"] for x in adj),
          detail=str([x["action"] for x in adj]))

    # KHE ĐÃ ĐÓNG 2026-08-03 (job Taylor_20260803_154258) — ca này TRƯỚC ĐÂY pin hành vi "khe
    # còn mở": mốc neo dùng TRƯỜNG GỐC của chính artifact nên chỉ chặn ca sửa MỘT trường; sửa
    # ĐỒNG BỘ cả hai (gốc ×3, levered = gốc ×3 ×1,3) thì mọi tỷ lệ vẫn đúng ⇒ qua sạch
    # (quant-skeptic verify_20260803_143700 thu hẹp tuyên bố đúng như vậy).
    # Đóng bằng `_verify_targets_integrity`: golive công bố CẢ BA THỪA SỐ sinh ra mục tiêu, nên
    # `capit_total_target_vnd` phải giải thích được bằng `nav_basis_vnd × w_lag_target ×
    # capit_size`. Sửa gốc ×3 mà không sửa thừa số ⇒ đẳng thức vỡ. Sửa cả thừa số ⇒ rơi vào
    # trần cơ học (w_lag/capit_size) hoặc vào neo NAV SỐNG đo ở tầng broker (nhóm J).
    both = os.path.join(TMP, "status_bothfields.json")
    _t_both = copy.deepcopy(tgt_on_art)
    _t_both["SpaceX"]["capit_slot_target_vnd"] = 150_000_000          # gốc ×3
    _t_both["SpaceX"]["capit_slot_target_vnd_levered"] = 195_000_000  # = ×3 ×1,3 (tỷ lệ ĐÚNG)
    _t_both["SpaceX"]["capit_total_target_vnd"] = 750_000_000
    _t_both["SpaceX"]["capit_total_target_vnd_levered"] = 975_000_000
    with open(both, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5,
                   "capit_slot_targets": _t_both}, f, ensure_ascii=False)
    infl = o("B1", "SAB")
    infl.qty, infl.ref_price = 9_750, 20_000                          # 195tr = trần đã thổi
    plan = mkplan([infl])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=both, rules_path=RULES_ON)
    check("C29b sửa ĐỒNG BỘ cả trường gốc lẫn levered (mọi tỷ lệ vẫn đúng) → BỊ CHẶN bởi kiểm "
          "nhất quán nội tại (tổng ≠ nav_basis × w_lag × capit_size) — khe hai-trường ĐÃ ĐÓNG",
          plan.orders[0].loan_package_id is None
          and any("TỰ MÂU THUẪN" in x["reason"] for x in adj),
          detail=(adj[0]["reason"][:130] if adj else "(không có adj)"))

    # Bước tiếp theo của CÙNG kẻ tấn công: sửa luôn thừa số cho ba đẳng thức khớp lại. Hai ca
    # dưới đây là hai lối duy nhất còn lại, và cả hai đều đụng trần CƠ HỌC ghim trong code.
    for _name, _over, _kw in (
            ("w_lag_target ×3 (1,50)", {"w_lag_target": 1.50}, "w_lag_target"),
            ("capit_size ×3 (1,50)", {"capit_size": 1.50}, "capit_size")):
        _t_fac = copy.deepcopy(tgt_on_art)
        _t_fac["SpaceX"].update(_over)
        _t_fac["SpaceX"]["nav_book_lag_vnd"] = (_t_fac["SpaceX"]["nav_basis_vnd"]
                                                * _t_fac["SpaceX"]["w_lag_target"])
        _t_fac["SpaceX"]["capit_total_target_vnd"] = (_t_fac["SpaceX"]["nav_book_lag_vnd"]
                                                      * _t_fac["SpaceX"]["capit_size"])
        _t_fac["SpaceX"]["capit_slot_target_vnd"] = (_t_fac["SpaceX"]["capit_total_target_vnd"]
                                                     / _t_fac["SpaceX"]["n_slots"])
        _t_fac["SpaceX"]["capit_slot_target_vnd_levered"] = \
            _t_fac["SpaceX"]["capit_slot_target_vnd"] * 1.3
        _t_fac["SpaceX"]["capit_total_target_vnd_levered"] = \
            _t_fac["SpaceX"]["capit_total_target_vnd"] * 1.3
        _p = os.path.join(TMP, f"status_fac_{_kw}.json")
        with open(_p, "w", encoding="utf-8") as f:
            json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_on,
                       "capit_adv_caps": ADV_CAPS5, "capit_slot_targets": _t_fac},
                      f, ensure_ascii=False)
        _big = o("B1", "SAB")
        _big.qty, _big.ref_price = 9_750, 20_000
        plan = mkplan([_big])
        plan, adj = apply_capit_lever(plan, "SpaceX", status_path=_p, rules_path=RULES_ON)
        check(f"C29c[{_name}] sửa THỪA SỐ cho ba đẳng thức khớp lại → vẫn bị TRẦN NEO THEO "
              f"STATE chặn (thừa số vượt bảng sizing của chính state phiên đó)",
              plan.orders[0].loan_package_id is None
              and any(_kw in x["reason"] and "ngoài biên của state" in x["reason"] for x in adj),
              detail=(adj[0]["reason"][:120] if adj else "(không có adj)"))

    # Lối cuối: giữ w_lag/capit_size hợp lệ, thổi `nav_basis_vnd` ×3 (ba đẳng thức vẫn khớp,
    # trần cơ học không đụng tới). Đó là ca mà CHỈ neo NAV sống bắt được → nhóm J. Ở tầng
    # offline, ca này ĐI QUA có chủ đích; ghim lại để ranh giới giữa hai tầng luôn tường minh.
    _t_nav = copy.deepcopy(tgt_on_art)
    for _k in ("nav_basis_vnd", "nav_book_lag_vnd", "capit_total_target_vnd",
               "capit_slot_target_vnd", "capit_total_target_vnd_levered",
               "capit_slot_target_vnd_levered"):
        _t_nav["SpaceX"][_k] = _t_nav["SpaceX"][_k] * 3
    NAV_INFLATED_ART = os.path.join(TMP, "status_navx3.json")
    with open(NAV_INFLATED_ART, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5, "capit_slot_targets": _t_nav},
                  f, ensure_ascii=False)
    _b3 = o("B1", "SAB")
    _b3.qty, _b3.ref_price = 9_750, 20_000                            # 195tr = trần đã thổi ×3
    plan = mkplan([_b3])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=NAV_INFLATED_ART,
                                  rules_path=RULES_ON)
    check("C29d thổi ĐỒNG BỘ cả nav_basis_vnd (ba đẳng thức vẫn khớp) → tầng OFFLINE cho qua "
          "ĐÚNG NHƯ THIẾT KẾ; ca này thuộc về neo NAV SỐNG ở nhóm J, không phải chỗ này",
          plan.orders[0].loan_package_id == 1840,
          detail="ranh giới hai tầng — J6 chứng minh nó bị chặn ở tầng broker sống")

    # ── C30: TRẦN NEO THEO STATE (arch-reviewer vòng 3 #2 — ca thật nó đo được) ──────────
    # Tấn công KHÔNG đụng `nav_basis_vnd` (nên neo NAV sống ở nhóm J MÙ hoàn toàn) và KHÔNG
    # vượt trần phẳng cũ: chỉ sửa `capit_size` từ 0,375 (NEUTRAL thường lệ = capit_base 0,75
    # × grind 0,5) lên 1,0 — đúng giá trị hợp lệ ở CRISIS. Trần phẳng `≤1,0` cho lọt 2,67×
    # mục tiêu. Trần neo theo state chặn vì state phiên là 3 ⇒ capit_size ≤ capit_base(3)=0,75.
    _t_st = copy.deepcopy(tgt_on_art)
    _t_st["SpaceX"]["capit_size"] = 1.0
    _t_st["SpaceX"]["capit_total_target_vnd"] = (_t_st["SpaceX"]["nav_book_lag_vnd"] * 1.0)
    _t_st["SpaceX"]["capit_slot_target_vnd"] = (_t_st["SpaceX"]["capit_total_target_vnd"]
                                                / _t_st["SpaceX"]["n_slots"])
    _t_st["SpaceX"]["capit_slot_target_vnd_levered"] = \
        _t_st["SpaceX"]["capit_slot_target_vnd"] * 1.3
    _t_st["SpaceX"]["capit_total_target_vnd_levered"] = \
        _t_st["SpaceX"]["capit_total_target_vnd"] * 1.3
    _p_st = os.path.join(TMP, "status_state_size.json")
    with open(_p_st, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5, "capit_slot_targets": _t_st},
                  f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=_p_st, rules_path=RULES_ON)
    check("C30 capit_size 0,375→1,0 (hợp lệ ở CRISIS, KHÔNG ở NEUTRAL), ba đẳng thức khớp, "
          "nav_basis KHÔNG đổi ⇒ neo NAV sống mù → TRẦN NEO THEO STATE chặn (trần phẳng cũ "
          "cho lọt 2,67×)",
          plan.orders[0].loan_package_id is None
          and any("capit_size" in x["reason"] and "state 3" in x["reason"] for x in adj),
          detail=(adj[0]["reason"][:130] if adj else "(không có adj)"))

    # …và kẻ tấn công đi tiếp: khai luôn `state=1` (CRISIS) để mở trần capit_size lên 1,0.
    # Chặn bằng nguồn state ĐỘC LẬP (golive_state_today.json do publish_gated_state.py ghi):
    # muốn lọt phải nói dối KHỚP NHAU ở HAI artifact do hai bước khác nhau sinh ra.
    _p_st2 = os.path.join(TMP, "status_state_lie.json")
    with open(_p_st2, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "state": 1, "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5, "capit_slot_targets": _t_st},
                  f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=_p_st2, rules_path=RULES_ON)
    check("C30b …khai luôn `state=1` để mở trần → nguồn state ĐỘC LẬP bác (artifact 1 vs "
          "golive_state_today 3): một lời nói dối phải khớp ở HAI artifact khác tiến trình",
          plan.orders[0].loan_package_id is None
          and any("nguồn độc lập" in x["reason"] for x in adj),
          detail=(adj[0]["reason"][:130] if adj else "(không có adj)"))

    _p_st3 = os.path.join(TMP, "status_state_missing.json")
    with open(_p_st3, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5, "capit_slot_targets": tgt_on_art},
                  f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=_p_st3, rules_path=RULES_ON)
    check("C30c artifact KHÔNG khai `state` → fail-closed (không biết state thì không biết "
          "trần nào đúng; fail-safe = không đòn bẩy, lệnh vẫn chạy vốn tự có)",
          plan.orders[0].loan_package_id is None and len(plan.orders) == 1,
          detail=(adj[0]["reason"][:110] if adj else "(không có adj)"))

    # C30d: `state` lạ (khai KHỚP ở cả hai nguồn) không được rơi về mặc định NEUTRAL — không
    # có trần nào áp được thì phải TỪ CHỐI (arch-reviewer vòng 4 #6).
    _st99 = os.path.join(TMP, "state_today_99.json")
    with open(_st99, "w", encoding="utf-8") as f:
        json.dump({"state": 99, "as_of": "2099-01-01"}, f)
    _p99 = os.path.join(TMP, "status_state99.json")
    with open(_p99, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "state": 99, "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5, "capit_slot_targets": tgt_on_art},
                  f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=_p99, rules_path=RULES_ON,
                                  state_path=_st99)
    check("C30d state=99 khai KHỚP ở CẢ HAI nguồn → vẫn TỪ CHỐI (không rơi về trần NEUTRAL): "
          "state ngoài bảng sizing nghĩa là không trần nào áp được",
          plan.orders[0].loan_package_id is None
          and any("không nằm trong bảng sizing" in x["reason"] for x in adj),
          detail=(adj[0]["reason"][:110] if adj else "(không có adj)"))

    # C30e: nguồn "độc lập" phải TƯƠI. Nếu publish_gated_state chết im lặng, file đứng lại ở
    # hôm qua và vẫn KHỚP giá trị — khớp do trùng, không phải do được xác nhận (§14, vòng 4 #5).
    _st_old = os.path.join(TMP, "state_today_stale.json")
    with open(_st_old, "w", encoding="utf-8") as f:
        json.dump({"state": 3, "as_of": "2098-12-31"}, f)      # as_of ≠ signal_date 2099-01-01
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                                  state_path=_st_old)
    check("C30e nguồn state độc lập STALE (as_of=2098-12-31 ≠ signal_date 2099-01-01) → TỪ "
          "CHỐI: nó khớp do TRÙNG giá trị hôm qua, không phải do xác nhận phiên này",
          plan.orders[0].loan_package_id is None
          and any("as_of" in x["reason"] for x in adj),
          detail=(adj[0]["reason"][:120] if adj else "(không có adj)"))

    # ── C31: thiếu ADV20 của 1 mã KHÔNG được đọc thành "artifact TỰ MÂU THUẪN" (#4) ──────
    # golive.capit_adv_caps() bỏ mã thiếu adv20 và tự in WARNING (mã đó bị cap_capit_orders
    # chặn riêng), trong khi n_slots vẫn chia theo rổ ĐẦY ĐỦ. So n_slots với số khoá
    # capit_adv_caps sẽ TẮT đòn bẩy cả phiên cho một lỗ hổng dữ liệu thường lệ.
    _caps4 = {k: v for k, v in ADV_CAPS5.items() if k != "NCT"}       # 4/5 mã có ADV20
    _p_adv = os.path.join(TMP, "status_adv_gap.json")
    with open(_p_adv, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_on,
                   "capit_adv_caps": _caps4, "n_capit_basket": 5,
                   "capit_slot_targets": tgt_on_art}, f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=_p_adv, rules_path=RULES_ON)
    check("C31 thiếu ADV20 của 1/5 mã (n_slots=5 vs 4 khoá adv_caps) → VẪN cấp đòn bẩy cho mã "
          "hợp lệ: đó là lỗ hổng dữ liệu thường lệ, không phải artifact bị giả mạo",
          plan.orders[0].loan_package_id == 1840,
          detail=str([(x["ticker"], x["action"]) for x in adj]))

    _p_adv2 = os.path.join(TMP, "status_nslots_bad.json")
    with open(_p_adv2, "w", encoding="utf-8") as f:
        json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_on,
                   "capit_adv_caps": ADV_CAPS5, "n_capit_basket": 9,
                   "capit_slot_targets": tgt_on_art}, f, ensure_ascii=False)
    plan = mkplan([o("B1", "SAB")])
    plan, adj = apply_capit_lever(plan, "SpaceX", status_path=_p_adv2, rules_path=RULES_ON)
    check("C31b …nhưng n_slots(5) ≠ n_capit_basket(9) VẪN chặn — rổ mà mục tiêu chia theo KHÁC "
          "rổ của phiên là mâu thuẫn thật, không phải thiếu ADV20",
          plan.orders[0].loan_package_id is None
          and any("n_capit_basket" in x["reason"] for x in adj),
          detail=(adj[0]["reason"][:110] if adj else "(không có adj)"))

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
        b.account_id = SPACEX_ACCOUNT
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

    # D6 — HỢP ĐỒNG MỚI (commit c22bd1c, 2026-08-07, ca DRI/UPCOM). Bản cũ khẳng định lệnh
    # THƯỜNG forward `loan_package_id=None`; chính hợp đồng ĐÓ là bug: None ⇒ dnse_api rơi về
    # gói default account (SpaceX 1841 = mainboard-only) ⇒ DNSE từ chối CẢ ppse LẪN place_order
    # với mã UPCOM, biểu hiện y hệt "thiếu tiền" ⇒ WAIT_CASH vô hạn. `c22bd1c` đã sửa 2 assert
    # cùng loại ở cash_only_loan_package_selfcheck.py nhưng BỎ SÓT D6 ở đây — vì file này lúc đó
    # chết `NameError` ở mục H trước khi in bảng tổng kết, nên D6 đỏ mà không ai thấy (đúng cái
    # giá của một harness hỏng: nó che mất một assert mốc thật).
    # Assert theo BẤT BIẾN, không theo giá trị: trường LUÔN được gửi, và no-op khi default hợp lệ.
    b = mkbroker()
    b.place_order("FPT", 1000, "buy", price=20000)
    check("D6a lệnh THƯỜNG mainboard: default 1841 hợp lệ cho mã → GIỮ NGUYÊN default "
          "(BAL/LAG/CAPIT không đổi hành vi)",
          b.client.calls[-1]["loan_package_id"] == 1841, detail=str(b.client.calls[-1]))

    b = mkbroker(pkgs=(1122,))
    b.place_order("DRI", 1000, "buy", price=20000)
    check("D6b lệnh THƯỜNG mã UPCOM: default KHÔNG hợp lệ → giải sang gói hợp lệ của MÃ "
          "(đây là bản vá WAIT_CASH vô hạn ca DRI 08-07)",
          b.client.calls[-1]["loan_package_id"] == 1122, detail=str(b.client.calls[-1]))

    b = mkbroker(boom=True)
    b.place_order("FPT", 1000, "buy", price=20000)
    check("D6c query gói lỗi → fail-safe về default, TUYỆT ĐỐI không bỏ trắng trường "
          "(thiếu loanPackageId = HTTP 400, bug TV1 07-28)",
          b.client.calls[-1]["loan_package_id"] == 1841, detail=str(b.client.calls[-1]))

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

    def mkexec(orders, tmpdir, account=TAG, cfg_over=None, broker=None):
        cfg = load_config()
        # HYBRID fill-timing GHIM TẮT làm nền (cfg_over vẫn bật lại được — nhóm E8-E10 dùng).
        # Vì sao: nhóm E đo LƯỚI ĐÒN BẨY (tạm dừng mã mang gói vay không ai duyệt), mà từ
        # 2026-08-10 `fill_timing_hybrid_enabled` mặc định True (bật trên paper, commit
        # 717307f). E5 chạy mode="paper" ở NOW=09:20 — NGOÀI block MUA của HYBRID
        # (11:00-13:45) ⇒ lệnh MUA bị hoãn theo LỊCH trước khi tới chỗ kiểm lưới.
        # ĐO THẬT (không suy luận), mutation gỡ `if o.ticker in ghost_tickers: continue` ở
        # `_place_slices` rồi A/B đúng MỘT cờ: hybrid=True ⇒ broker KHÔNG bị gọi ⇒ E5 VẪN
        # PASS; hybrid=False ⇒ get_quote bị gọi ⇒ E5 FAIL đúng như phải thế. Nghĩa là trước
        # bản vá này E5 PASS KỂ CẢ KHI lưới bị gỡ sạch — nó không đo được gì nữa. Nguy hiểm
        # hơn màu đỏ: "không gọi broker" không phân biệt được lưới AN TOÀN (chặn đòn bẩy
        # không ai duyệt — TIỀN THẬT) với lịch CHI PHÍ (HYBRID_DEFER, chỉ hoãn). §23 hệ luận
        # 1: selfcheck không assert lên trạng thái SỐNG (ở đây là cờ config toàn cục đang
        # trôi). Ca KẾT HỢP đo ở E8-E10.
        cfg["fill_timing_hybrid_enabled"] = False
        cfg.update(cfg_over or {})
        cfg["mode"] = "paper"
        ex = Executor(mkplan(orders, account=account), broker or _NullBroker(), cfg, shared={})
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
        json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lev_off}, f, ensure_ascii=False)
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

    # ── E8-E10: LƯỚI ĐÒN BẨY × HYBRID (đúng cấu hình paper THẬT từ 2026-08-10) ─────────────
    # Vì sao phải có: E1-E7 cố ý ghim HYBRID tắt để cô lập lưới. Nếu chỉ ghim mà không bù, bộ
    # test sẽ mô tả một cấu hình KHÔNG ai chạy (paper thật đang bật HYBRID) và lần đổi cờ tiếp
    # theo lại đi qua không ai thấy. Khi HYBRID bật, "broker không bị gọi" có HAI nguyên nhân
    # khác hẳn nhau — lưới TẠM DỪNG (an toàn, chặn đòn bẩy không ai duyệt) và HYBRID_DEFER
    # (lịch chi phí, chỉ hoãn). Đếm số lệnh không phân biệt được, nên phân biệt bằng JOURNAL
    # + một ca CHỨNG MINH NGƯỢC.
    NOW_HYB = _dt.datetime(2099, 1, 2, 11, 5)      # TRONG block MUA đầu tiên (11:00-11:15)
    NOW_OUT = _dt.datetime(2099, 1, 2, 9, 20)      # NGOÀI block MUA — đúng giờ E5 đang dùng
    HYB_ON = {"fill_timing_hybrid_enabled": True}

    class _ReachedBroker(_NullBroker):
        """Ghi lại việc luồng ĐI TỚI được tầng broker thay vì ném AssertionError. Quote None
        ⇒ `_place_slices` ghi NO_QUOTE rồi `continue`: quan sát được mà không đặt lệnh."""

        def __init__(self):
            self.quote_calls = []

        def get_quote(self, ticker, *a, **k):
            self.quote_calls.append(ticker)
            return None

    def _ev_hyb(ex):
        if not os.path.exists(ex.journal_file):
            return set()
        with open(ex.journal_file, encoding="utf-8") as f:
            return {row[1] for row in csv.reader(f) if len(row) > 1}

    def _mk_hyb(tag, paused, now):
        br = _ReachedBroker()
        exh = mkexec([o("B1", "FPT", book="BAL")], TMP, account=TAG + tag,
                     cfg_over=HYB_ON, broker=br)
        exh._place_slices(now, "MORNING", ghost_tickers=({"FPT"} if paused else set()))
        return exh, br

    # E8 — TRONG block MUA nên HYBRID KHÔNG hoãn; mã bị tạm dừng ⇒ thứ duy nhất còn có thể
    # chặn là lưới đòn bẩy. Lưới `continue` LẶNG (không ghi journal) nên bằng chứng "không
    # phải HYBRID" là: journal KHÔNG có HYBRID_DEFER và broker chưa hề bị chạm.
    ex_h1, br_h1 = _mk_hyb("h1", paused=True, now=NOW_HYB)
    check("E8 HYBRID bật, TRONG block MUA, mã bị TẠM DỪNG ⇒ chặn bởi lưới đòn bẩy, KHÔNG "
          "phải HYBRID_DEFER (broker chưa bị chạm)",
          "HYBRID_DEFER" not in _ev_hyb(ex_h1) and br_h1.quote_calls == [],
          detail=f"events={sorted(_ev_hyb(ex_h1))} quote_calls={br_h1.quote_calls}")

    # E9 — CHỨNG MINH NGƯỢC cho E8: cùng cấu hình, cùng giờ, đổi ĐÚNG MỘT biến (bỏ tạm dừng).
    ex_h2, br_h2 = _mk_hyb("h2", paused=False, now=NOW_HYB)
    check("E9 CHỨNG MINH NGƯỢC: cùng cấu hình/giờ, BỎ tạm dừng ⇒ luồng ĐI TỚI broker (lưới "
          "đòn bẩy mới là thứ chặn E8)",
          br_h2.quote_calls == ["FPT"] and "NO_QUOTE" in _ev_hyb(ex_h2),
          detail=f"quote_calls={br_h2.quote_calls} events={sorted(_ev_hyb(ex_h2))}")

    # E10 — chốt rằng ghim TẮT ở E1-E7 là cần thiết chứ không tuỳ tiện, và ghi lại ĐÚNG cơ chế
    # đã che mất E5: cùng lệnh KHÔNG bị tạm dừng, chỉ dời ra ngoài block (09:20 = giờ E5).
    ex_h3, br_h3 = _mk_hyb("h3", paused=False, now=NOW_OUT)
    check("E10 HYBRID bật, NGOÀI block ⇒ HYBRID_DEFER và broker KHÔNG bị chạm (đây chính là "
          "thứ làm E5 pass kể cả khi lưới đòn bẩy bị gỡ sạch)",
          "HYBRID_DEFER" in _ev_hyb(ex_h3) and br_h3.quote_calls == [],
          detail=f"events={sorted(_ev_hyb(ex_h3))} quote_calls={br_h3.quote_calls}")

    # ─────────────────── F. DIỄN TẬP ĐẦU–CUỐI trên PaperBroker ───────────────────
    section("F. DIỄN TẬP đầu–cuối (paper): tín hiệu → artifact → plan → lệnh")

    def rehearse(rules_dir, tag):
        """Chạy trọn: §6a THẬT → artifact → apply_capit_lever → PaperBroker.place_order.
        Trả (capit_lever, {ticker: loanPackageId trên sổ lệnh paper})."""
        lever, targets = run_block(rules_dir, dd52=-25.0, signal=True, size=0.50,
                                   basket=BASKET5, targets=base_targets())
        art = os.path.join(TMP, f"art_{tag}.json")
        with open(art, "w", encoding="utf-8") as f:
            json.dump({"signal_date": "2099-01-01", "state": 3, "capit_lever": lever,
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

    def _extract_exec_block(marker, n_stmts, expect_last, ns_keys, tag):
        """Trích một khối python của heredoc production theo CẤU TRÚC (ast), KHÔNG theo mốc-cuối chuỗi.

        Bản đầu (cả H lẫn L) cắt từ mốc-đầu tới `lines = [f"📋` — mốc-cuối cách vùng cần trích
        ~235 dòng, nên MỌI thứ chèn vào giữa đều bị cuốn theo. Khối "ĐÒN BẨY MARGIN" thêm ngày
        2026-08-03 lọt vào đoạn trích của H và `exec` chết `NameError: name 'plan' is not
        defined` (102 assert trước đó vẫn PASS ⇒ đỏ vì HARNESS, không phải production sai);
        chính khối đó rồi cũng cuốn tiếp phần sau nó vào L. Cùng họ bug CHECK5 (§17).

        Sửa bằng đúng thứ `ast` biết mà chuỗi không biết: khối cần trích là `n_stmts` statement
        TOP-LEVEL đầu tiên sau mốc, kết thúc đúng ở `end_lineno` của statement cuối. Chèn thêm
        bao nhiêu code phía sau cũng không với tới được. `expect_last` khoá lại HÌNH DẠNG của
        statement cuối, nên nếu ai chèn code vào GIỮA khối thì test đỏ NGAY ở tag-b kèm lý do,
        thay vì âm thầm trích nhầm.
        """
        check(f"{tag}a trích được khối từ send_plan_report.sh production",
              _spr.count(marker) == 1, detail=f"n_marker={_spr.count(marker)}")
        # thân heredoc python kết thúc ở dòng terminator `PY`; sau đó là bash, ast không parse được
        body = marker + _spr.split(marker, 1)[1].split("\nPY\n", 1)[0]
        tops = ast.parse(body).body[:n_stmts]
        ok_shape = len(tops) == n_stmts and expect_last(tops[-1])
        check(f"{tag}b khối = {n_stmts} statement top-level đầu, dạng statement cuối đúng như ghim",
              ok_shape, detail=f"dạng={[type(n).__name__ for n in tops]}")
        if not ok_shape:
            return ""
        blk = "\n".join(body.splitlines()[:tops[-1].end_lineno])

        # Cổng chống-trôi: khối chỉ được dùng những tên harness thật sự cấp. Thiếu một tên ⇒ báo
        # NGAY ở đây kèm tên còn thiếu, thay vì `NameError` khô khốc giữa một lần chạy sau.
        bound, used = set(), set()
        for n in ast.walk(ast.parse(blk)):
            if isinstance(n, ast.Name):
                (bound if isinstance(n.ctx, ast.Store) else used).add(n.id)
            elif isinstance(n, ast.ExceptHandler) and n.name:
                bound.add(n.name)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                bound.update((a.asname or a.name).split(".")[0] for a in n.names)
        free = sorted(used - bound - set(dir(builtins)))
        check(f"{tag}c khối khép kín trên namespace harness cấp (không cuốn theo khối lân cận)",
              set(free) <= ns_keys,
              detail=f"tên tự do={free}; thiếu={sorted(set(free) - ns_keys)}")
        return blk

    # Khối CAPIT = `capit_note = ""` · `_capit_buys = [...]` · `if _capit_buys:` (3 statement).
    CAPIT_NOTE_SRC = _extract_exec_block(
        "# ── CAPIT: Σ lệnh mua thật vs VND mục tiêu đã publish", 3,
        lambda n: isinstance(n, ast.If) and isinstance(n.test, ast.Name)
        and n.test.id == "_capit_buys",
        {"json", "os", "acct", "orders", "_order_price"}, "H0")

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
            exec(CAPIT_NOTE_SRC, ns)
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

    # ───────── I. CỔNG DUYỆT RIÊNG TỪNG NGÀY CÓ VAY (user chốt 2026-08-03) ─────────
    # "Khi DollarBill tạo plan dùng margin tôi sẽ phải đồng ý duyệt thì hệ thống mới được phép
    # vận hành": `enabled=true` là điều kiện CẦN, mỗi ngày có vay cần thêm 1 lần duyệt riêng.
    # Mọi ca ở đây gọi `_apply_raw` — KHÔNG qua wrapper mặc-định-có-duyệt của nhóm C.
    section("I. Cổng duyệt RIÊNG từng ngày có vay (margin_day_approval)")

    NO_APPROVAL = os.path.join(TMP, "approvals_empty")
    os.makedirs(NO_APPROVAL, exist_ok=True)

    plan = mkplan([o("B1", "SAB"), o("B2", "VNM")])
    plan, adj = _apply_raw(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                           approvals_dir=NO_APPROVAL)
    check("I1 mọi cổng KHÁC đều đạt nhưng CHƯA có duyệt riêng cho ngày này → KHÔNG lệnh nào "
          "mang cờ vay",
          all(x.loan_package_id is None for x in plan.orders),
          detail=str([(x.ticker, x.loan_package_id) for x in plan.orders]))
    check("I2 …và có ĐÚNG 1 dòng cấp-plan nói rõ thiếu duyệt + cách duyệt (không im lặng)",
          sum(1 for x in adj if x["action"] == "MARGIN_APPROVAL_REQUIRED") == 1
          and any("approve_margin_day.py" in x["reason"] for x in adj),
          detail=str([x["action"] for x in adj]))
    check("I3 …lệnh VẪN CÒN trong plan (fail-safe = không đòn bẩy, KHÔNG phải chặn lệnh)",
          len(plan.orders) == 2, detail=f"{len(plan.orders)} lệnh")

    plan = mkplan([o("B1", "SAB"), o("B2", "VNM")])
    plan, adj = _apply_raw(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                           approvals_dir=APPROVALS_OK)
    check("I4 có bản duyệt HỢP LỆ cho đúng ngày → cấp bình thường "
          "(cổng mới không chặn nhầm ca đã duyệt)",
          all(x.loan_package_id == 1840 for x in plan.orders)
          and not any(x["action"] == "MARGIN_APPROVAL_REQUIRED" for x in adj),
          detail=str([x["action"] for x in adj]))

    # Từng cách "duyệt giả" — đây đúng là chỗ quant-skeptic soi ở vòng trước.
    for _nm, _over, _why in (
            ("approved_by rỗng", {"approved_by": ""}, "duyệt trống"),
            ("approved_by='pending'", {"approved_by": "pending"}, "giữ chỗ"),
            ("approved_by='agent'", {"approved_by": "agent"}, "agent tự duyệt bị nhận diện"),
            ("plan_date của NGÀY KHÁC", {"plan_date": "2099-01-02", "_fname_date": "2099-01-02",
                                         "_inner_date": "2098-12-31"}, "duyệt ngày khác"),
            ("account của account KHÁC", {"account": "ZaloPay", "_fname_acct": "SpaceX"},
             "duyệt account khác"),
            ("lever_f = 3,0", {"lever_f": 3.0}, "hệ số ngoài bản duyệt"),
            ("gói vay 9999", {"loan_package_id": 9999}, "gói ngoài bản duyệt"),
            ("thiếu trần VND", {"max_lever_total_vnd": 0}, "duyệt khống"),
            ("tickers rỗng", {"tickers": []}, "duyệt khống rổ"),
            ("revoked=true", {"revoked": True, "revoked_reason": "user đổi ý 08:10"},
             "đã thu hồi"),
            # Cờ HUỶ phải fail-SAFE, ngược chiều cờ BẬT (arch-reviewer vòng 3 #3): đường thu
            # hồi được thiết kế cho người sửa gấp lúc 08:10, và người sửa tay JSON viết
            # `"revoked": "true"` hay `1` là chuyện thường. Với `is True` cả hai bị BỎ QUA im
            # lặng và 09:05 vẫn vay — một cờ huỷ fail-OPEN trong bản ghi ủy quyền vay tiền.
            ("revoked='true' (chuỗi, sửa tay)", {"revoked": "true"}, "thu hồi viết tay"),
            ("revoked=1 (int, sửa tay)", {"revoked": 1}, "thu hồi viết tay"),
            ("revoked='yes' (chuỗi lạ)", {"revoked": "yes"}, "giá trị lạ vẫn phải nghiêng "
                                                             "về HUỶ")):
        _d = os.path.join(TMP, f"appr_{abs(hash(_nm))}")
        os.makedirs(_d, exist_ok=True)
        _rec_over = {k: v for k, v in _over.items() if not k.startswith("_")}
        _p = write_approval(_d, **_rec_over)
        # Ca "đổi tên file": nội dung ghi ngày/account KHÁC nhưng file mang tên đúng ngày/
        # account đang chạy — chứng minh đổi tên file KHÔNG đủ để tái sử dụng một bản duyệt.
        if "_fname_date" in _over or "_fname_acct" in _over:
            with open(_p, encoding="utf-8") as fh:
                _r = json.load(fh)
            if "_inner_date" in _over:
                _r["plan_date"] = _over["_inner_date"]
            os.replace(_p, os.path.join(
                _d, f"margin_approval_{_over.get('_fname_acct', _r['account'])}_"
                    f"{_over.get('_fname_date', _r['plan_date'])}.json"))
            with open(os.path.join(_d, f"margin_approval_"
                                       f"{_over.get('_fname_acct', _r['account'])}_"
                                       f"{_over.get('_fname_date', _r['plan_date'])}.json"),
                      "w", encoding="utf-8") as fh:
                json.dump(_r, fh, ensure_ascii=False)
        plan = mkplan([o("B1", "SAB")])
        plan, adj = _apply_raw(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                               approvals_dir=_d)
        check(f"I5[{_nm}] bản duyệt không hợp lệ ({_why}) → KHÔNG cấp đòn bẩy",
              plan.orders[0].loan_package_id is None
              and any(x["action"] == "MARGIN_APPROVAL_REQUIRED" for x in adj),
              detail=str([x["action"] for x in adj]))

    # Trần Σ VND của bản duyệt: user duyệt MỘT SỐ TIỀN, không duyệt khống.
    _d_cap = os.path.join(TMP, "appr_cap")
    write_approval(_d_cap, max_lever_total_vnd=100_000_000)
    two = [o("B1", "SAB"), o("B2", "VNM")]
    for _od in two:
        _od.qty, _od.ref_price = 3_250, 20_000                # 65tr/lệnh ⇒ Σ 130tr > 100tr
    plan = mkplan(two)
    plan, adj = _apply_raw(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                           approvals_dir=_d_cap)
    check("I6 Σ lệnh được cấp (130tr) VƯỢT trần user duyệt (100tr) → gỡ SẠCH, không cấp một "
          "phần (cấp một phần = tự quyết hộ user vay bao nhiêu)",
          all(x.loan_package_id is None for x in plan.orders)
          and any("VƯỢT mức user đã duyệt" in x["reason"] for x in adj),
          detail=str([x["action"] for x in adj]))

    _d_tk = os.path.join(TMP, "appr_tk")
    write_approval(_d_tk, tickers=["SAB"])
    plan = mkplan([o("B1", "SAB"), o("B2", "VNM")])
    plan, adj = _apply_raw(plan, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                           approvals_dir=_d_tk)
    check("I7 plan cấp cho mã NGOÀI rổ user đã duyệt (VNM ∉ [SAB]) → gỡ sạch, đòi duyệt lại "
          "(rổ đổi sau khi duyệt là một quyết định mới)",
          all(x.loan_package_id is None for x in plan.orders)
          and any("KHÔNG có trong rổ user đã duyệt" in x["reason"] for x in adj),
          detail=str([x["action"] for x in adj]))

    # Chế độ PREVIEW — đường DUY NHẤT nhìn thấy tập lệnh đang chờ duyệt. Nó phải KHÔNG BAO GIỜ
    # trở thành đường vòng qua cổng duyệt.
    plan_src = mkplan([o("B1", "SAB"), o("B2", "FPT", book="BAL")])
    ret, adj_pv = _apply_raw(plan_src, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                             approvals_dir=NO_APPROVAL, preview=True)
    check("I8 preview trả về None thay cho plan → KHÔNG có đối tượng plan mang cờ vay nào "
          "thoát ra, kể cả khi caller gán lại biến",
          ret is None, detail=repr(ret)[:60])
    check("I9 preview KHÔNG sửa plan gốc của caller (chạy trên bản sao)",
          all(x.lever_f is None and x.loan_package_id is None for x in plan_src.orders),
          detail=str([(x.ticker, x.loan_package_id) for x in plan_src.orders]))
    check("I10 preview vẫn THẤY tập lệnh sẽ vay (dù chưa duyệt) — nếu không thì không ai "
          "duyệt được cái gì",
          [x["ticker"] for x in adj_pv if x["action"] == "APPLIED"] == ["SAB"],
          detail=str([(x["ticker"], x["action"]) for x in adj_pv]))
    _, adj_pv_off = _apply_raw(mkplan([o("B1", "SAB")]), "SpaceX", status_path=ART_ON,
                               rules_path=RULES_OFF, approvals_dir=APPROVALS_OK, preview=True)
    check("I11 preview bỏ qua ĐÚNG cổng duyệt-ngày, KHÔNG bỏ qua cổng nào khác "
          "(chính sách TẮT ⇒ preview cũng rỗng)",
          not any(x["action"] in ("APPLIED", "OVERRIDDEN") for x in adj_pv_off),
          detail=str([x["action"] for x in adj_pv_off]))

    check("I12 giá trị VND đi kèm từng dòng cấp (bước duyệt cần số tiền, không chỉ tên mã)",
          all(isinstance(x.get("value"), (int, float)) and x["value"] > 0
              for x in adj_pv if x["action"] == "APPLIED"),
          detail=str([(x["ticker"], x.get("value")) for x in adj_pv]))

    # HỢP ĐỒNG GHI↔ĐỌC: script duyệt và hàm đọc duyệt phải nói cùng một schema. Kiểm bằng AST
    # trên source THẬT của script (§17) thay vì chép tay danh sách khoá sang test.
    APPR_SCRIPT = os.path.join(HERE, "mike", "bin", "approve_margin_day.py")
    _appr_src = open(APPR_SCRIPT, encoding="utf-8").read()
    _keys = set()
    for _n in ast.walk(ast.parse(_appr_src)):
        if isinstance(_n, ast.Assign) and isinstance(_n.value, ast.Dict) \
                and any(getattr(t, "id", "") == "rec" for t in _n.targets):
            _keys = {k.value for k in _n.value.keys if isinstance(k, ast.Constant)}
    _need = {"account", "plan_date", "approved_by", "lever_f", "loan_package_id",
             "max_lever_total_vnd", "tickers"}
    check("I13 approve_margin_day.py ghi ĐỦ mọi khoá mà margin_day_approval() bắt buộc "
          "(hợp đồng ghi↔đọc, kiểm trên source thật)",
          _need <= _keys, detail=f"thiếu: {sorted(_need - _keys) or 'không'}")

    check("I13b …và dùng CHUNG danh sách 'không phải người duyệt thật' với hàm đọc "
          "(import, không chép) — hai bản sao là cách để một chuỗi qua bên này chặn bên kia",
          "from trading_bot.plan import APPROVAL_PLACEHOLDERS" in _appr_src,
          detail="APPROVAL_PLACEHOLDERS")

    # I13c: chạy THẬT `preview_margin_day` đầu-cuối (arch-reviewer vòng 4: nhóm I/L STUB hàm
    # này, nên thứ mà báo cáo 21:00 và approve_margin_day.py thực sự gọi chưa từng chạy trong
    # selfcheck). Nó phải tự `load_plan` từ PLAN_DIR ⇒ ghi 1 plan thật vào đó rồi dọn.
    _PLAN_F = os.path.join(_planmod.PLAN_DIR, "plan_SpaceX_2099-01-02.json")
    try:
        _pv_plan = mkplan([o("B1", "SAB"), o("B2", "FPT", book="BAL")])
        os.makedirs(_planmod.PLAN_DIR, exist_ok=True)
        with open(_PLAN_F, "w", encoding="utf-8") as _f:
            json.dump({"plan_date": "2099-01-02", "signal_date": "2099-01-01",
                       "strategy": "selfcheck", "strategy_version": "0", "state": 1,
                       "state_name": "CRISIS", "nav_basis": {"account_nav": 1e9},
                       "account": "SpaceX", "created_at": "2099-01-01T00:00:00",
                       "orders": [dataclasses.asdict(x) for x in _pv_plan.orders]},
                      _f, ensure_ascii=False)
        # dọn sổ do các ca KHÔNG-preview ở trên để lại, để khẳng định I13d nói về preview
        if os.path.exists(_planmod._lever_ledger_path("SpaceX", "2099-01-02")):
            os.remove(_planmod._lever_ledger_path("SpaceX", "2099-01-02"))
        _pv_real = _planmod.preview_margin_day("SpaceX", "2099-01-02", status_path=ART_ON,
                                               rules_path=RULES_ON, state_path=_STATE_FIX)
        check("I13c chạy THẬT preview_margin_day() đầu-cuối (không stub) → thấy ĐÚNG lệnh "
              "CAPIT sẽ vay, kèm Σ VND và phần vay — đây là số user nhìn thấy lúc duyệt",
              _pv_real["tickers"] == ["SAB"] and _pv_real["lever_f"] == 1.3
              and _pv_real["loan_package_id"] == 1840 and _pv_real["total_vnd"] > 0
              and abs(_pv_real["borrow_vnd"] - _pv_real["total_vnd"] * (1 - 1 / 1.3)) < 1,
              detail=f"{_pv_real['tickers']} Σ={_pv_real['total_vnd']:,.0f} "
                     f"vay={_pv_real['borrow_vnd']:,.0f}")
        check("I13d …và preview KHÔNG ghi sổ cấp phép ra đĩa (chế độ xem trước không được để "
              "lại dấu vết cấp phép nào)",
              not os.path.exists(_planmod._lever_ledger_path("SpaceX", "2099-01-02")))
    finally:
        for _p in (_PLAN_F, _planmod._lever_ledger_path("SpaceX", "2099-01-02")):
            if os.path.exists(_p):
                os.remove(_p)

    _rc = os.system(f"{sys.executable} {APPR_SCRIPT} --account SpaceX --date 2099-01-02 "
                    f"--dry-run >/dev/null 2>&1")
    check("I14 chạy THẬT approve_margin_day.py --dry-run trên cấu hình production (đang TẮT) "
          "→ TỪ CHỐI ghi bản duyệt khống, exit≠0",
          os.WEXITSTATUS(_rc) != 0, detail=f"exit={os.WEXITSTATUS(_rc)}")
    check("I15 …và KHÔNG tạo file duyệt nào trong data/margin_approvals/",
          not os.path.exists(os.path.join(HERE, "data", "margin_approvals",
                                          "margin_approval_SpaceX_2099-01-02.json")))

    # I16-I18: DẤU VẾT là lá chắn thật chống "agent tự duyệt hộ" (danh sách placeholder chỉ là
    # quy ước mềm — nó cho qua "system-auto"/"Claude"/"yes"). Nên nếu bus/Discord hỏng mà
    # script im lặng trả 0 thì lá chắn biến mất đúng lúc cần nhất (arch-reviewer vòng 3 #5).
    check("I16 _bus/_notify KIỂM returncode, không chỉ bắt exception — bus hỏng phải nói ra",
          _appr_src.count("r.returncode != 0") >= 2 and "check=False" in _appr_src,
          detail=f"{_appr_src.count('r.returncode != 0')} chỗ kiểm rc")
    check("I17 …và exit code phản ánh việc dấu vết KHÔNG để lại được (không nuốt im lặng)",
          "_trace_exit" in _appr_src and "return 3" in _appr_src)
    check("I18 `decided_by` KHÔNG hard-code 'user' — script chạy được bởi cả người lẫn agent "
          "nên phải KHAI, không TỰ NHẬN (coding_guidelines §20)",
          '"decided_by": "user"' not in _appr_src
          and '"decided_by": args.decided_by' in _appr_src
          and '"--decided-by"' in _appr_src)
    check("I19 đường --revoke ghi NGUYÊN TỬ như đường tạo (§5) — bản ghi ủy quyền vay tiền "
          "không được để lại JSON cụt khi bị kill giữa chừng",
          _appr_src.count("os.replace(tmp, path)") >= 2,
          detail=f"{_appr_src.count('os.replace(tmp, path)')} chỗ os.replace")

    # ───────── J. PREFLIGHT SỐNG: neo NAV + đọc thật pp0Buy (lever_live_preflight) ─────────
    section("J. Preflight sống trước lệnh đòn bẩy (neo NAV + pp0Buy@gói của lệnh)")

    class _Q:
        def __init__(self, px):
            self.last, self.ref = px, px

        def ok(self):
            return self.last is not None

    class _PFBroker:
        """Broker giả tối thiểu cho preflight: đủ cash/positions/quote/buying_power."""

        def __init__(self, cash=300_000_000, positions=None, prices=None, bp=10 ** 9,
                     bp_exc=False, cash_exc=False):
            self.cash, self.positions = cash, positions or {}
            self.prices = prices or {}
            self.bp, self.bp_exc, self.cash_exc = bp, bp_exc, cash_exc
            self.calls = []

        def get_cash(self):
            if self.cash_exc:
                raise RuntimeError("balances API lỗi")
            return self.cash

        def get_positions(self):
            return {k: {"total": v} for k, v in self.positions.items()}

        def get_quote(self, sym):
            px = self.prices.get(sym)
            return _Q(px) if px is not None else _Q(None)

        def get_buying_power(self, symbol, price, loan_package_id=None):
            self.calls.append({"symbol": symbol, "price": price,
                               "loan_package_id": loan_package_id})
            if self.bp_exc:
                raise RuntimeError("ppse timeout")
            return self.bp

    def mk_levered_plan(n=2, qty=3_250, px=20_000):
        ords = []
        for i, tk in enumerate(BASKET5[:n]):
            od = o(f"B{i}", tk)
            od.qty, od.ref_price = qty, px
            od.lever_f, od.loan_package_id = 1.3, 1840
            ords.append(od)
        return mkplan(ords)

    # NAV sống = tiền 300tr + 700tr cổ phiếu = 1,0 tỷ, khớp `nav_basis_vnd` của fixture.
    LIVE_OK = dict(cash=300_000_000, positions={"FPT": 10_000}, prices={"FPT": 70_000})

    p1 = mk_levered_plan()
    b1 = _PFBroker(**LIVE_OK)
    p1, a1 = lever_live_preflight(p1, "SpaceX", b1, "live", status_path=ART_ON)
    check("J1 NAV sống khớp artifact + đọc được pp0Buy → GIỮ đòn bẩy, 1 dòng log đọc được "
          "bằng mắt", all(x.loan_package_id == 1840 for x in p1.orders)
          and a1 and a1[0]["action"] == "LIVE_PREFLIGHT_OK",
          detail=(a1[0]["reason"][:120] if a1 else "(rỗng)"))
    check("J2 …và pp0Buy được đo bằng ĐÚNG gói vay của lệnh (1840), KHÔNG phải gói default "
          "1841 (đo sai gói ⇒ báo thiếu một nửa sức mua)",
          b1.calls and b1.calls[0]["loan_package_id"] == 1840, detail=str(b1.calls))

    p2 = mk_levered_plan()
    b2 = _PFBroker(bp=None, **LIVE_OK)
    p2, a2 = lever_live_preflight(p2, "SpaceX", b2, "live", status_path=ART_ON)
    check("J3 KHÔNG đọc được sức mua (None) → GỠ đòn bẩy, lệnh VẪN chạy bằng vốn tự có "
          "(diễn tập paper không phủ được tầng ppse ⇒ không đọc được là không tin)",
          all(x.loan_package_id is None for x in p2.orders) and len(p2.orders) == 2
          and a2[0]["action"] == "LIVE_PREFLIGHT_STRIP", detail=a2[0]["reason"][:110])

    p3 = mk_levered_plan()
    b3 = _PFBroker(bp_exc=True, **LIVE_OK)
    p3, a3 = lever_live_preflight(p3, "SpaceX", b3, "live", status_path=ART_ON)
    check("J4 ppse ném exception (mạng lỗi) → GỠ, không để exception thoát ra làm hỏng phiên",
          all(x.loan_package_id is None for x in p3.orders)
          and a3[0]["action"] == "LIVE_PREFLIGHT_STRIP", detail=a3[0]["reason"][:100])

    p4 = mk_levered_plan()
    b4 = _PFBroker(bp=50_000_000, **LIVE_OK)          # < Σ 130tr
    p4, a4 = lever_live_preflight(p4, "SpaceX", b4, "live", status_path=ART_ON)
    check("J5 pp0Buy đọc ĐƯỢC nhưng NHỎ HƠN Σ lệnh → CẢNH BÁO, KHÔNG gỡ "
          "(gỡ đòn bẩy lúc thiếu tiền làm lệnh cần NHIỀU tiền hơn — sai chiều fail-safe)",
          all(x.loan_package_id == 1840 for x in p4.orders)
          and any(x["action"] == "LIVE_PREFLIGHT_WARN" for x in a4),
          detail=str([x["action"] for x in a4]))

    p5 = mk_levered_plan()
    b5 = _PFBroker(**LIVE_OK)
    p5, a5 = lever_live_preflight(p5, "SpaceX", b5, "live", status_path=NAV_INFLATED_ART)
    check("J6 artifact thổi `nav_basis_vnd` ×3 (ca C29d mà tầng offline cho qua) → NEO NAV "
          "SỐNG chặn — đây là mảnh cuối đóng khe artifact hai-trường",
          all(x.loan_package_id is None for x in p5.orders)
          and a5[0]["action"] == "LIVE_PREFLIGHT_STRIP"
          and "NAV SỐNG" in a5[0]["reason"], detail=a5[0]["reason"][:130])

    p6 = mk_levered_plan()
    b6 = _PFBroker(cash=900_000_000, positions={"FPT": 10_000}, prices={"FPT": 70_000})
    p6, a6 = lever_live_preflight(p6, "SpaceX", b6, "live", status_path=ART_ON)
    check("J7 NAV sống LỚN HƠN artifact (1,6 tỷ vs 1,0 tỷ) → KHÔNG chặn: chiều đó chỉ là "
          "sizing thận trọng, không sinh vay vượt mức (cổng bất đối xứng có chủ đích)",
          all(x.loan_package_id == 1840 for x in p6.orders),
          detail=str([x["action"] for x in a6]))

    p7 = mk_levered_plan()
    b7 = _PFBroker(**LIVE_OK)
    p7, a7 = lever_live_preflight(p7, "SpaceX", b7, "paper", status_path=ART_ON)
    check("J8 mode=paper → bỏ qua có ghi log, KHÔNG gỡ (pp0Buy là khái niệm của broker thật; "
          "diễn tập paper nhóm F phải chạy được)",
          all(x.loan_package_id == 1840 for x in p7.orders)
          and a7[0]["action"] == "LIVE_PREFLIGHT_SKIPPED" and not b7.calls,
          detail=str([x["action"] for x in a7]))

    p8 = mkplan([o("B1", "FPT", book="BAL"), o("B2", "TRC", book="LAG")])
    b8 = _PFBroker(**LIVE_OK)
    p8, a8 = lever_live_preflight(p8, "SpaceX", b8, "live", status_path=ART_ON)
    check("J9 plan KHÔNG có lệnh đòn bẩy nào → 0 dòng log, 0 lệnh gọi broker "
          "(mọi phiên thường lệ không tốn thêm gì)",
          a8 == [] and not b8.calls, detail=str(a8))

    p9 = mk_levered_plan()
    b9 = _PFBroker(cash=300_000_000, positions={"FPT": 10_000, "HAG": 5_000},
                   prices={"FPT": 70_000})               # HAG không có giá
    p9, a9 = lever_live_preflight(p9, "SpaceX", b9, "live", status_path=ART_ON)
    check("J10 không định giá được một vị thế → GỠ (NAV sống không đủ tin cậy để làm mốc; "
          "KHÔNG đoán giá)",
          all(x.loan_package_id is None for x in p9.orders)
          and "HAG" in a9[0]["reason"], detail=a9[0]["reason"][:100])

    p10 = mk_levered_plan()
    b10 = _PFBroker(cash_exc=True, positions={"FPT": 10_000}, prices={"FPT": 70_000})
    p10, a10 = lever_live_preflight(p10, "SpaceX", b10, "live", status_path=ART_ON)
    check("J11 broker lỗi khi đo NAV → GỠ (fail-closed, không bỏ qua bước neo)",
          all(x.loan_package_id is None for x in p10.orders)
          and a10[0]["action"] == "LIVE_PREFLIGHT_STRIP", detail=a10[0]["reason"][:100])

    p11 = mk_levered_plan()
    b11 = _PFBroker(cash=300_000_000, positions={"FPT": 10_000, "DGC": 10_000},
                    prices={"FPT": 70_000, "DGC": 100_000})
    p11, a11 = lever_live_preflight(p11, "SpaceX", b11, "live", status_path=ART_ON,
                                    excluded_tickers=["DGC"])
    check("J12 vị thế excluded_tickers bị TRỪ khỏi NAV sống (đúng công thức active_nav mà "
          "golive dùng làm cơ sở) → 1,0 tỷ khớp artifact, không báo động giả",
          all(x.loan_package_id == 1840 for x in p11.orders),
          detail=str([x["action"] for x in a11]))

    p12 = mk_levered_plan()
    b12 = _PFBroker(cash=300_000_000, positions={"FPT": 10_000, "DGC": 10_000},
                    prices={"FPT": 70_000, "DGC": 100_000})
    p12, a12 = lever_live_preflight(p12, "SpaceX", b12, "live", status_path=ART_ON)
    check("J12b …và nếu KHÔNG khai excluded thì NAV sống là 2,0 tỷ (> artifact) → vẫn không "
          "chặn: chứng minh J12 kiểm phép TRỪ chứ không phải trùng hợp",
          all(x.loan_package_id == 1840 for x in p12.orders))

    # J13: `bp == 0` KHÔNG còn là điều kiện GỠ (arch-reviewer vòng 3 #1, chân thứ hai).
    # Hết sức mua là trạng thái BÌNH THƯỜNG sau khi sleeve giải ngân xong; gỡ đòn bẩy lúc đó
    # làm lệnh cần NHIỀU tiền hơn — cùng lý lẽ đã dùng cho nhánh `bp < total`.
    p13 = mk_levered_plan()
    b13 = _PFBroker(cash=300_000_000, positions={"FPT": 10_000}, prices={"FPT": 70_000}, bp=0)
    p13, a13 = lever_live_preflight(p13, "SpaceX", b13, "live", status_path=ART_ON)
    check("J13 pp0Buy ĐỌC ĐƯỢC nhưng = 0 (sleeve đã giải ngân hết) → CẢNH BÁO, KHÔNG gỡ — "
          "'hết sức mua' khác 'không đọc được', chỉ cái sau mới là bằng chứng chưa thông tuyến",
          all(x.loan_package_id == 1840 for x in p13.orders)
          and any(x["action"] == "LIVE_PREFLIGHT_WARN" for x in a13),
          detail=str([x["action"] for x in a13]))

    # ── J14-J19: HAI LƯỢT CRON CÙNG PHIÊN (09:05 + 13:00 ICT) — bug CRITICAL vòng 3+4 ──
    # crontab thật có 2 lượt `run_bot.sh --account SpaceX` mỗi ngày giao dịch (09:05 và 13:00
    # "khởi động lại sau nghỉ trưa"). Lượt 13:00 là tiến trình MỚI chạy lại TRỌN cascade.
    # Trước fix: preflight đo NAV sống giữa lúc đang giải ngân (availableCash đã trừ tiền giữ
    # cho lệnh treo) → thấp hơn cơ sở tối qua → GỠ sạch cờ vay → Executor._lever_package_audit
    # mất tập cấp phép → PAUSE cả rổ CAPIT cả buổi chiều kèm sự cố NÓI SAI ("đòn bẩy không ai
    # duyệt") cho đúng những lệnh đã qua CẢ HAI cổng người sáng hôm đó.
    _EXEC_STATE = os.path.join(EXEC_DIR, "exec_SpaceX_2099-01-02_state.json")
    _LEDGER = _planmod._lever_ledger_path("SpaceX", "2099-01-02")

    def _write_session_state(n_children, created_at="", parent_ids=("B0", "B1")):
        """Giả lập state của Executor sau lượt 09:05 (đã đặt n lệnh con, đã khớp một phần).

        `created_at` MẶC ĐỊNH RỖNG = đúng hiện trạng production (vòng 6): không plan thật nào
        có khoá `created_at`, nên state thật ghi `plan_created_at: ""`. Fixture trước đây điền
        một chuỗi ISO giả nên mọi ca `created_at` đều PASS trong khi đường thật không bao giờ
        chạm tới nhánh đó — đúng loại phụ thuộc môi trường mà `verify-before-done` bắt phải
        khai. `parent_ids` = tập id lệnh mà PHIÊN ĐANG CHẠY biết (state của plan v1).
        """
        with open(_EXEC_STATE, "w", encoding="utf-8") as f:
            json.dump({"plan_date": "2099-01-02", "plan_created_at": created_at, "parents": {
                pid: {"filled": 500 if pid == "B1" else 0, "done": False,
                      "children": [{"oid": f"P{i:06d}", "qty": 100, "filled": 100,
                                    "status": "closed"} for i in range(n_children)]
                                  if pid == "B1" else []}
                for pid in parent_ids}}, f)

    def _clean_session():
        for _p in (_EXEC_STATE, _LEDGER):
            if os.path.exists(_p):
                os.remove(_p)

    def _audit(plan, ticker, lp=1840):
        _ex = Executor(plan, PaperBroker(load_config()), load_config())
        return _ex._lever_package_audit({"P1": OrderUpdate(
            "P1", "Filled", 500, 20_000, {"symbol": ticker, "loanPackageId": lp})})

    try:
        # ── J14: lượt 09:05 — phiên SẠCH: neo NAV vẫn GỠ đầy đủ (bảo vệ chính không bị nới)
        _clean_session()
        p14 = mk_levered_plan()
        p14, a14 = lever_live_preflight(p14, "SpaceX", _PFBroker(**LIVE_OK), "live",
                                        status_path=NAV_INFLATED_ART)
        check("J14 [lượt 09:05, phiên SẠCH] artifact thổi NAV → VẪN GỠ đầy đủ: lớp bảo vệ "
              "chính (chặn khoản vay ĐẦU TIÊN đi ra trên cơ sở vốn giả) KHÔNG bị nới",
              all(x.loan_package_id is None for x in p14.orders)
              and a14[0]["action"] == "LIVE_PREFLIGHT_STRIP", detail=a14[0]["action"])

        # ── J15: lượt 13:00 — phiên ĐÃ đặt lệnh (state khớp created_at): KHÔNG gỡ nữa
        _clean_session()
        _write_session_state(5)
        p15 = mk_levered_plan()
        p15, a15 = lever_live_preflight(p15, "SpaceX", _PFBroker(**LIVE_OK), "live",
                                        status_path=NAV_INFLATED_ART)
        check("J15 [lượt 13:00, phiên ĐÃ đặt lệnh] CÙNG đầu vào → KHÔNG gỡ, chỉ CẢNH BÁO: NAV "
              "sống tụt giữa lúc giải ngân là bình thường, còn gỡ thì treo cả rổ CAPIT",
              all(x.loan_package_id == 1840 for x in p15.orders)
              and a15[0]["action"] == "LIVE_PREFLIGHT_WARN"
              and "ĐÃ đặt lệnh" in a15[0]["reason"], detail=a15[0]["reason"][:110])

        # ── J15b: CA CỦA ĐƯỜNG PRODUCTION THẬT (vòng 6, rủi ro dư #1 §11.10). Plan phát hành
        # lại giữa ngày mang lệnh vay MỚI, nhưng `created_at` hai bên đều RỖNG như production
        # ⇒ bản khoá-theo-`created_at` thấy `"" == ""` và kết luận "phiên đã bắt đầu" ⇒ lệnh
        # vay HOÀN TOÀN MỚI đi ra chỉ với WARN. Vân tay nội dung (id lệnh vay) thấy id lạ ⇒ GỠ.
        _clean_session()
        _write_session_state(5, parent_ids=("B0", "B1"))       # state của plan v1
        p15b = mk_levered_plan()
        p15b.orders[0].id = "B9-MOI"                           # plan v2: 1 lệnh vay MỚI TINH
        p15b, a15b = lever_live_preflight(p15b, "SpaceX", _PFBroker(**LIVE_OK), "live",
                                          status_path=NAV_INFLATED_ART)
        check("J15b [ĐƯỜNG THẬT: created_at RỖNG cả hai bên] plan phát hành lại giữa ngày có "
              "lệnh vay MỚI → VẪN GỠ nhờ vân tay id, không còn phụ thuộc `created_at` chết",
              all(x.loan_package_id is None for x in p15b.orders)
              and a15b[0]["action"] == "LIVE_PREFLIGHT_STRIP", detail=a15b[0]["action"])

        # ── J15c: chiều NGƯỢC lại phải KHÔNG gỡ oan — plan v2 BỚT lệnh (một fail-safe phía
        # trên loại bớt giữa 2 lượt chạy) không sinh khoản vay mới nào. Bắt "bằng nhau" thay vì
        # "bao hàm" sẽ GỠ đòn bẩy hợp lệ cả buổi chiều — đúng sự cố CRITICAL vòng 3.
        _clean_session()
        _write_session_state(5, parent_ids=("B0", "B1"))
        p15c = mk_levered_plan(n=1)                            # chỉ còn B0, đã có trong state
        p15c, a15c = lever_live_preflight(p15c, "SpaceX", _PFBroker(**LIVE_OK), "live",
                                          status_path=NAV_INFLATED_ART)
        check("J15c plan v2 BỚT lệnh (không thêm lệnh vay mới) → KHÔNG gỡ, chỉ CẢNH BÁO: "
              "so bao hàm (⊆) chứ không bằng nhau, chiều nguy hiểm chỉ là chiều THÊM",
              all(x.loan_package_id == 1840 for x in p15c.orders)
              and a15c[0]["action"] == "LIVE_PREFLIGHT_WARN", detail=a15c[0]["action"])

        # ── J15d: ghim tường minh rằng `created_at` KHÔNG còn là điều kiện. State mang chuỗi
        # ISO khác hẳn plan; id khớp ⇒ vẫn WARN. (Trước vòng 6 ca này GỠ — đổi hành vi CÓ CHỦ Ý:
        # `created_at` không phân biệt được gì trên production nên không được quyền quyết định.)
        _clean_session()
        _write_session_state(5, created_at="2099-01-01T09:30:00")
        p15d = mk_levered_plan()
        p15d, a15d = lever_live_preflight(p15d, "SpaceX", _PFBroker(**LIVE_OK), "live",
                                          status_path=NAV_INFLATED_ART)
        check("J15d `created_at` lệch nhưng tập id lệnh vay khớp → KHÔNG gỡ: quyết định nay "
              "dựa vào NỘI DUNG, và lệch chiều này chỉ có thể GỠ chứ không bao giờ CẤP",
              all(x.loan_package_id == 1840 for x in p15d.orders)
              and a15d[0]["action"] == "LIVE_PREFLIGHT_WARN", detail=a15d[0]["action"])

        # ── J16/J17: STRIP phải THU HỒI luôn khỏi sổ cấp phép (vòng 4 #1). Nếu không, đúng
        # lúc preflight nói "cơ sở vốn không có thật" thì audit tầng lệnh lại MÙ với chính
        # những mã đó.
        _clean_session()
        _pa = mkplan([o("B1", "SAB")])
        _pa, _ = apply_capit_lever(_pa, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                                   approvals_dir=APPROVALS_OK)
        _granted_before = copy.deepcopy(getattr(_pa, "_lever_authorized", None))
        _pa, _ = lever_live_preflight(_pa, "SpaceX", _PFBroker(**LIVE_OK), "live",
                                      status_path=NAV_INFLATED_ART)
        check("J16 preflight STRIP → THU HỒI khỏi sổ cấp phép (cả RAM lẫn đĩa), không chỉ gỡ "
              "cờ trên lệnh — nếu không, lưới an toàn tầng lệnh mù đúng lúc cần nhất",
              _granted_before == {"1840": {"SAB"}}
              and not getattr(_pa, "_lever_authorized", None)
              and _pa.orders[0].loan_package_id is None,
              detail=f"trước={_granted_before} sau={getattr(_pa, '_lever_authorized', None)}")

        _pause, _warns = _audit(_pa, "SAB")
        check("J17 …nên audit VẪN bắt được lệnh gói 1840 thật trên mã vừa bị GỠ (ca "
              "state.json hỏng/bị xoá: preflight tưởng phiên sạch mà broker đang có lệnh sống)",
              _pause == {"SAB"} and len(_warns) == 1,
              detail=f"pause={sorted(_pause)} warns={len(_warns)}")

        # ── J18: nhánh WARN (phiên đã đặt lệnh) thì GIỮ sổ — đây mới là ca chống sự cố giả
        _clean_session()
        _write_session_state(5)
        _pb = mkplan([o("B1", "SAB")])
        _pb, _ = apply_capit_lever(_pb, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                                   approvals_dir=APPROVALS_OK)
        _pb, _ = lever_live_preflight(_pb, "SpaceX", _PFBroker(**LIVE_OK), "live",
                                      status_path=NAV_INFLATED_ART)
        _pause18, _warns18 = _audit(_pb, "SAB")
        check("J18 nhánh WARN (phiên đã đặt lệnh) GIỮ sổ → audit KHÔNG dựng sự cố giả cho "
              "lệnh đã qua cả 2 cổng người sáng nay",
              _pause18 == set() and _warns18 == [],
              detail=f"pause={sorted(_pause18)} sổ={getattr(_pb, '_lever_authorized', None)}")

        # ── J19: sổ PERSIST QUA TIẾN TRÌNH (vòng 4 #3). Lượt 13:00 chạy với chính sách đã bị
        # TẮT giữa phiên (`enabled=false`) ⇒ apply_capit_lever cấp 0 mã. Nếu sổ chỉ nằm trong
        # RAM thì audit lại tuyên bố "được cấp: KHÔNG MÃ NÀO" và treo cả rổ CAPIT cả buổi
        # chiều — đúng sự cố giả mà vòng 3 tưởng đã đóng, chỉ qua một trigger khác.
        _clean_session()
        _p1 = mkplan([o("B1", "SAB")])                       # tiến trình 1 (09:05): cấp bình thường
        _p1, _ = apply_capit_lever(_p1, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                                   approvals_dir=APPROVALS_OK)
        _write_session_state(3)                              # …và đã đặt lệnh thật
        _p2 = mkplan([o("B1", "SAB")])                       # tiến trình 2 (13:00): chính sách TẮT
        _p2, _ = apply_capit_lever(_p2, "SpaceX", status_path=ART_ON, rules_path=RULES_OFF,
                                   approvals_dir=APPROVALS_OK)
        _pause19, _warns19 = _audit(_p2, "SAB")
        check("J19 tiến trình 13:00 với `enabled=false` (tắt giữa phiên) → sổ ĐỌC TỪ ĐĨA nên "
              "audit KHÔNG treo rổ CAPIT vì lệnh gói 1840 hợp lệ của buổi sáng (§5 idempotent)",
              _pause19 == set() and _warns19 == [],
              detail=f"pause={sorted(_pause19)} sổ={getattr(_p2, '_lever_authorized', None)}")

        _pause19b, _warns19b = _audit(_p2, "VNM")
        check("J19b …nhưng mã CHƯA TỪNG được cấp vẫn bị bắt — sổ không nới guard, nó chỉ vá "
              "chỗ guard đọc nhầm nguồn (đối chứng bắt buộc)",
              _warns19b and _warns19b[0]["ticker"] == "VNM",
              detail=str([w["ticker"] for w in _warns19b]))

        # ── J20: STRIP chỉ được thu hồi phần CHÍNH tiến trình này cấp (vòng 5 #1) ──────────
        # Sổ CỐ Ý day-scoped, còn điều kiện vào nhánh STRIP lại khoá theo vân tay của CHÍNH
        # tập lệnh vay lượt này (vòng 6; trước đó là `created_at`). Plan phát hành lại giữa
        # ngày ⇒ started=False dù lệnh 1840 buổi sáng vẫn sống trên sổ broker; trừ SẠCH sẽ xoá
        # đúng bản ghi đó và dựng lại sự cố giả.
        _clean_session()
        _q1 = mkplan([o("B1", "SAB")])                       # 09:05: cấp + đặt lệnh thật
        _q1, _ = apply_capit_lever(_q1, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                                   approvals_dir=APPROVALS_OK)
        _write_session_state(3)                              # state của plan v1
        _q2 = mkplan([o("B1-V2", "SAB")])                    # 13:00: plan v2, id lệnh vay MỚI
        _q2, _ = apply_capit_lever(_q2, "SpaceX", status_path=ART_ON, rules_path=RULES_ON,
                                   approvals_dir=APPROVALS_OK)
        _q2, _a20 = lever_live_preflight(_q2, "SpaceX", _PFBroker(**LIVE_OK), "live",
                                         status_path=NAV_INFLATED_ART)
        _pause20, _warns20 = _audit(_q2, "SAB")
        check("J20 plan phát hành lại giữa ngày + STRIP → sổ GIỮ bản ghi của lệnh tiến trình "
              "TRƯỚC đã đặt thật ⇒ audit KHÔNG treo rổ (thu hồi chỉ phần tiến trình này cấp)",
              _a20[0]["action"] == "LIVE_PREFLIGHT_STRIP" and _pause20 == set()
              and _warns20 == [],
              detail=f"{_a20[0]['action']} pause={sorted(_pause20)} "
                     f"sổ={getattr(_q2, '_lever_authorized', None)}")

        # ── J21: sổ hỏng mang khoá gói DEFAULT 1841 → phải bị LỌC khi đọc (vòng 5 #2) ─────
        # `_lever_package_audit` bơm thẳng khoá của sổ vào tập `packages` nó đi soi, nên một
        # khoá 1841 làm nó soi MỌI lệnh BAL/LAG thường lệ và pause sạch cả phiên.
        _clean_session()
        with open(_LEDGER, "w", encoding="utf-8") as f:
            json.dump({"granted": {"1841": ["ZZZ"], "1840": "SAB"}}, f)   # + value là CHUỖI
        _q3 = mkplan([o("B1", "SAB"), o("B2", "FPT", book="BAL")])
        _q3, _ = apply_capit_lever(_q3, "SpaceX", status_path=ART_ON, rules_path=RULES_OFF,
                                   approvals_dir=APPROVALS_OK)
        _pause21, _ = _audit(_q3, "FPT", lp=1841)
        check("J21 sổ hỏng chứa khoá gói DEFAULT 1841 → bị LỌC khi đọc, audit KHÔNG soi lệnh "
              "chạy gói mặc định (nếu không, 1 file hỏng đóng băng cả phiên BAL/LAG)",
              _pause21 == set()
              and set(getattr(_q3, "_lever_authorized", {})) <= {"1840"},
              detail=f"pause={sorted(_pause21)} sổ={getattr(_q3, '_lever_authorized', None)}")
        check("J21b …và value dạng CHUỖI được ép về tập 1 phần tử, không vỡ thành từng ký tự "
              "(set('SAB') = {'S','A','B'} là bẫy im lặng)",
              getattr(_q3, "_lever_authorized", {}).get("1840") == {"SAB"},
              detail=str(getattr(_q3, "_lever_authorized", None)))
    finally:
        _clean_session()

    # ───────── K. MỐI NỐI trong bot_execute.py (đúng vị trí, không chỉ 'có gọi') ─────────
    section("K. Mối nối cascade trong bot_execute.py")

    _bx = open(os.path.join(HERE, "bot_execute.py"), encoding="utf-8").read()
    # K1-K3 kiểm THỨ TỰ trong cascade thực thi, mà cascade nằm gọn trong `main()`. Phải cắt
    # nguồn về đúng thân `main()` TRƯỚC khi `.find()`: một hàm phụ đứng trước main mà tình cờ
    # chứa cùng chuỗi mốc sẽ làm `.find()` trả về vị trí của hàm phụ đó và thứ tự so ra SAI
    # (sự cố thật 2026-08-18: `_run_gdkhq_shadow` dòng 111 cũng gọi
    # `make_broker(cfg, otp=otp, profile=p).connect()` ⇒ K3 FAIL trong khi bot_execute.py đúng).
    _bx_main = extract_func(_bx, "main", where="bot_execute.py")
    _i_lever = _bx_main.find("apply_capit_lever(plan")
    _i_conn = _bx_main.find("make_broker(cfg, otp=otp, profile=p).connect()")
    _i_pref = _bx_main.find("lever_live_preflight(")
    _i_shadow = _bx_main.find("_log_plan_buying_power_shadow(p[")
    check("K1 bot_execute.py có gọi lever_live_preflight", _i_pref > 0)
    check("K2 …SAU connect() (cần sổ broker sống) và TRƯỚC shadow-log P0 (shadow phải đo "
          "theo trạng thái đòn bẩy CHUNG CUỘC, nếu không nó ghi would_block GIẢ)",
          0 < _i_conn < _i_pref < _i_shadow,
          detail=f"connect={_i_conn} preflight={_i_pref} shadow={_i_shadow}")
    check("K3 …và cascade vẫn gọi apply_capit_lever TRƯỚC đó (preflight chỉ GỠ, không cấp)",
          0 < _i_lever < _i_conn)
    check("K4 bot_execute.py KHÔNG BAO GIỜ gọi apply_capit_lever ở chế độ preview "
          "(preview bỏ qua cổng duyệt-ngày — đường thực thi tuyệt đối không được dùng)",
          "preview=True" not in _bx and "preview =" not in _bx)
    check("K5 …và in ra dòng riêng khi đòn bẩy bị gỡ vì thiếu duyệt riêng",
          "MARGIN_APPROVAL_REQUIRED" in _bx and "THIẾU DUYỆT RIÊNG" in _bx)

    # ───────── L. Khối MARGIN trong báo cáo duyệt plan (send_plan_report.sh) ─────────
    # Chạy CHÍNH đoạn source production (§17): người duyệt phải THẤY plan có vay, và thấy
    # đúng số tiền vay — không lẫn vào dòng duyệt plan thường lệ.
    section("L. Khối cảnh báo MARGIN trong báo cáo duyệt plan")

    # Khối MARGIN = `margin_note = []` · `try: … except` (2 statement) — cùng cách cắt theo cấu
    # trúc như H0 (xem docstring `_extract_exec_block`); mốc-cuối chuỗi cũ cuốn theo cả phần sau.
    MARGIN_SRC = _extract_exec_block(
        "# ── ĐÒN BẨY MARGIN: nêu BẬT LOẠT", 2, lambda n: isinstance(n, ast.Try),
        {"acct", "date"}, "L0")

    def run_margin(pv, rec, aerr=""):
        """exec khối production với preview/duyệt giả lập (vá ở tầng MODULE vì khối tự
        `from trading_bot.plan import ...` — vá namespace sẽ bị chính dòng import ghi đè)."""
        _o_pv, _o_ap = _planmod.preview_margin_day, _planmod.margin_day_approval
        _planmod.preview_margin_day = lambda a, d, **k: pv
        _planmod.margin_day_approval = lambda a, d, **k: (rec, aerr)
        ns = {"acct": "SpaceX", "date": "2099-01-02"}
        try:
            exec(MARGIN_SRC, ns)
        finally:
            _planmod.preview_margin_day, _planmod.margin_day_approval = _o_pv, _o_ap
        return "\n".join(ns["margin_note"])

    _PV_NONE = {"error": "", "orders": [], "tickers": [], "total_vnd": 0.0,
                "borrow_vnd": 0.0, "lever_f": None, "loan_package_id": None, "reasons": []}
    _PV_ON = {"error": "", "lever_f": 1.3, "loan_package_id": 1840,
              "orders": [{"order_id": "B1", "ticker": "SAB", "value_vnd": 65_000_000},
                         {"order_id": "B2", "ticker": "VNM", "value_vnd": 65_000_000}],
              "tickers": ["SAB", "VNM"], "total_vnd": 130_000_000,
              "borrow_vnd": 30_000_000, "reasons": []}

    m_none = run_margin(_PV_NONE, None, "chưa có duyệt")
    check("L1 plan KHÔNG có lệnh vay → KHÔNG thêm dòng nào (0 nhiễu vào báo cáo thường lệ)",
          m_none == "", detail=repr(m_none)[:80])

    m_wait = run_margin(_PV_ON, None, "CHƯA CÓ duyệt riêng cho ngày 2099-01-02")
    check("L2 plan CÓ vay + chưa duyệt riêng → nêu BẬT LOẠT: có margin, Σ tiền vay, và "
          "CẦN DUYỆT RIÊNG (không lẫn vào dòng duyệt plan thường)",
          "CÓ DÙNG MARGIN" in m_wait and "CẦN DUYỆT RIÊNG" in m_wait
          and "tiền VAY dự kiến" in m_wait, detail=m_wait[:130])
    check("L3 …và chỉ ra ĐÚNG lệnh phải chạy để duyệt (người duyệt không phải tự tra)",
          "approve_margin_day.py" in m_wait and "--date 2099-01-02" in m_wait,
          detail=m_wait[-150:])
    check("L4 …và nói rõ không duyệt thì KHÔNG bị chặn lệnh, chỉ chạy bằng vốn tự có",
          "VỐN TỰ CÓ" in m_wait)

    m_ok = run_margin(_PV_ON, {"approved_by": "user (John) 21:37",
                               "max_lever_total_vnd": 130_000_000}, "")
    check("L5 đã duyệt riêng → báo cáo xác nhận ai duyệt + trần Σ, không đòi duyệt lại",
          "ĐÃ ĐƯỢC DUYỆT RIÊNG" in m_ok and "John" in m_ok
          and "CẦN DUYỆT RIÊNG" not in m_ok, detail=m_ok[-120:])

    # L6: plan ĐÃ sizing 1,3× nhưng đòn bẩy sẽ KHÔNG được cấp — trước đây nhánh này IM LẶNG
    # (chỉ có `if error: pass` / `elif orders:`), nên người duyệt 21:00 chỉ thấy cảnh báo
    # "lệch +30%" của cổng 07-21, vốn quy sai nguyên nhân sang "nhân capit_size hai lần".
    # Đúng phát hiện #3a của vòng 2, dịch sang tầng báo cáo (arch-reviewer vòng 3 #7).
    _PV_OFF = dict(_PV_NONE, reasons=[
        "artifact CÓ mục tiêu đã nhân f (`capit_slot_target_vnd_levered`=65,000,000 VND/mã) "
        "nhưng đòn bẩy KHÔNG được cấp: chính sách đang TẮT. Lệnh CAPIT có thể đã được sizing "
        "theo mục tiêu ĐÃ NHÂN f trong khi chỉ có vốn tự có."])
    m_off = run_margin(_PV_OFF, None, "chưa có duyệt")
    check("L6 plan sizing theo ĐÒN BẨY nhưng sẽ chạy VỐN TỰ CÓ → báo cáo 21:00 PHẢI nói ra "
          "(trước đây im lặng, người duyệt chỉ thấy cảnh báo lệch +30% quy sai nguyên nhân)",
          "VỐN TỰ CÓ" in m_off and "sizing" in m_off.lower(), detail=m_off[:150])
    check("L7 …nhưng plan bình thường (không lý do nào) vẫn KHÔNG thêm dòng nào",
          run_margin(dict(_PV_NONE, reasons=[]), None, "x") == "")

# DỌN artifact của chính test khỏi thư mục PRODUCTION (arch-reviewer vòng 4 #7). Glob dọn ở
# đầu file chạy TRƯỚC khi các file này được tạo, nên nếu không dọn ở đây thì mỗi lần chạy để
# lại rác trong data/execution_logs/ — nơi người vận hành đọc để tìm state thật của phiên.
for _leftover in (glob.glob(os.path.join(EXEC_DIR, "exec_*_2099-01-02_lever_authorized.json"))
                  + glob.glob(os.path.join(EXEC_DIR, "exec_*_2099-01-02_state.json"))
                  + [_STATE_FIX]):
    try:
        os.remove(_leftover)
    except OSError:
        pass

print(f"\nENV: TZ={os.environ.get('TZ', '(không đặt)')!r} · "
      f"python={sys.version.split()[0]} · cwd={os.getcwd()}")
if fails:
    print(f"\n❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("\n✅ tất cả PASS — đòn bẩy CAPIT đã wire trọn đường và ĐANG TẮT")
