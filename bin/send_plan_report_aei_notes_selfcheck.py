#!/usr/bin/env python3
"""Self-check: send_plan_report.sh §29 khối ⛔/⚠️ auto_exit_inject_notes — PHẢI sống sót khi có
entry THỦ CÔNG (user sửa tay plan) nối SAU entry tự động, không bị `_aei_notes[-1]` che mất
(arch-review vòng 4, job Taylor_20261001_161827).

Sự cố thật: plan_ZaloPay_2026-10-02.json có 3 entry `auto_exit_inject_notes` — [0] manual (CSV,
22:59, sửa tay), [1] auto (SCL, 20:40), [2] manual (VPB, 22:59, capped_from=882→capped_to=600).
Bản cũ đọc `_aei_notes[-1]` = entry [2] (manual, KHÔNG có field "blocked"/"capped" top-level) ⇒
khối ⛔/⚠️ của lượt auto [1] biến mất hoàn toàn khỏi report dù plan ĐANG có mã bị chặn/cắt.

Sửa: `auto_exit_inject.py` tự gắn `entry["source"] = "auto_exit_inject"` cho MỌI entry nó ghi;
renderer gộp blocked/capped của MỌI entry có marker này (dedup theo ticker/book/nội dung), bỏ
qua entry không có marker (= entry thủ công) khi tìm blocked/capped tự động — nhưng vẫn quét
riêng entry thủ công để hiện phần CẮT (injected[].capped_from/capped_to) nếu có, không để mất
thông tin đó.

Chạy script THẬT trong sandbox (SEND_PLAN_WORKDIR_OVERRIDE + SEND_PLAN_MARKER_DIR + --dry-run) —
không gửi Telegram/Discord, không ghi marker thật.

Chạy: python3 mike/bin/send_plan_report_aei_notes_selfcheck.py
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import wc_paths  # noqa: E402

WC = wc_paths.find_wc_root(__file__)
# SEND_PLAN_SCRIPT: trỏ sang bản KHÁC của script để chạy đối chứng RED trên code cũ/mutant
# (mirror send_plan_report_state_gate_selfcheck.py) — kỷ luật verify-before-done: test này được
# tự chạy lại trên mutant tái lập đúng bug `_aei_notes[-1]` gốc để xác nhận nó THẬT SỰ đỏ trước
# khi tin PASS trên cây đã sửa.
SENDER = os.environ.get("SEND_PLAN_SCRIPT") or os.path.join(HERE, "send_plan_report.sh")
REAL_PLANS = os.path.join(WC, "data", "trade_plans")

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))


def expected_date(env=None):
    r = subprocess.run(
        [sys.executable, "-c",
         "import datetime as dt; from zoneinfo import ZoneInfo; "
         "from trading_bot.vn_market import next_trading_day; "
         "print(next_trading_day(dt.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()))"],
        cwd=WC, capture_output=True, text=True, env=env)
    return r.stdout.strip()


TODAY_ICT = subprocess.run(
    [sys.executable, "-c", "import datetime as dt; from zoneinfo import ZoneInfo; "
     "print(dt.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date())"],
    capture_output=True, text=True).stdout.strip()
LAST_RC = [None]  # Mblk_none_crash (vòng 5): rc entry sau cùng, để T7 phát hiện render_crashed


def run_sender(plan, account, extra=None):
    """`extra` = {đường dẫn tương đối trong sandbox: nội dung | callable(ngày_ICT_hôm_nay)}."""
    td = tempfile.mkdtemp()
    try:
        for sub in ("data/trade_plans", "state"):
            os.makedirs(os.path.join(td, sub), exist_ok=True)
        for rel, body in (extra or {}).items():
            fp = os.path.join(td, rel.format(today=TODAY_ICT))
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(body)
        os.symlink(os.path.join(WC, "trading_bot"), os.path.join(td, "trading_bot"))
        env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=td,
                   SEND_PLAN_MARKER_DIR=os.path.join(td, "state", "marker"))
        exp = expected_date(env)
        plan = dict(plan, plan_date=exp)
        with open(os.path.join(td, "data", "trade_plans",
                               f"plan_{account}_{exp}.json"), "w", encoding="utf-8") as fh:
            json.dump(plan, fh, ensure_ascii=False)
        r = subprocess.run(["bash", SENDER, "--account", account, "--dry-run"],
                           capture_output=True, text=True, env=env, timeout=600)
        LAST_RC[0] = r.returncode
        return r.stdout + r.stderr
    finally:
        shutil.rmtree(td, ignore_errors=True)


def load_real(account, date="2026-08-07"):
    with open(os.path.join(REAL_PLANS, f"plan_{account}_{date}.json"), encoding="utf-8") as fh:
        return json.load(fh)


SX = load_real("SpaceX")
SX.pop("auto_exit_inject_notes", None)
for key in ("park_trim_proposal", "jit_unpark_proposal"):
    if isinstance(SX.get(key), dict):
        SX[key].pop("_merged_into_orders", None)

AUTO_ENTRY = {
    "at": "2026-10-01T20:40:01+07:00",
    "source": "auto_exit_inject",
    "injected": [{"ticker": "SCL", "book": "LAG", "sessions_held": 35}],
    "blocked": [{"ticker": "BADTK", "book": "LAG", "reason": "reconcile lệch broker: sổ lô=1000 broker=900"}],
    "capped": [{"ticker": "VPB", "book": "LAG", "desired_qty": 882, "capped_qty": 600,
                "reason": "VPB book=LAG: Σ SELL kế hoạch > sellable 600cp"}],
}
MANUAL_BEFORE = {
    "at": "2026-10-01T19:54:36+07:00",
    "injected": [{"ticker": "CSV", "book": "LAG", "sessions_held": 44, "manual": True,
                 "decided_by": "user"}],
}
MANUAL_AFTER_PLAIN = {
    "at": "2026-10-01T22:59:11+07:00",
    "injected": [{"ticker": "VPB", "book": "LAG", "sessions_held": 45, "manual": True,
                 "decided_by": "user"}],
}
MANUAL_AFTER_CAPPED = {
    "at": "2026-10-01T23:05:00+07:00",
    "injected": [{"ticker": "VPB", "book": "LAG", "sessions_held": 45, "manual": True,
                 "decided_by": "user", "capped_from": 882, "capped_to": 600}],
}

# ── T1 (ca thật, bug gốc): manual TRƯỚC + auto + manual SAU + cùng auto entry có capped riêng —
# `[-1]` một mình = manual_after (KHÔNG có "blocked"/"capped") ⇒ khối ⛔/⚠️ của auto PHẢI biến
# mất trên bản cũ. Bản sửa phải hiện ĐỦ CẢ 2 — blocked (reconcile) + capped (VPB) đến từ auto.
print("[T1] manual TRƯỚC + auto (blocked+capped) + manual SAU — khối ⛔/⚠️ của auto PHẢI còn")
p1 = copy.deepcopy(SX)
p1["auto_exit_inject_notes"] = [MANUAL_BEFORE, AUTO_ENTRY, MANUAL_AFTER_PLAIN]
out1 = run_sender(p1, "SpaceX")
check("T1a: ⛔ khối BỊ CHẶN hiện ra (KHÔNG bị entry manual nối sau che mất — bug gốc)",
      "mã auto-exit (LAG/BAL/CAPIT) BỊ CHẶN" in out1 and "BADTK" in out1,
      [l.strip()[:150] for l in out1.splitlines() if "BỊ CHẶN" in l][:1])
check("T1b: ⚠️ khối BỊ CẮT hiện ra (VPB 882cp → 600cp, từ entry auto)",
      "mã auto-exit BỊ CẮT" in out1 and "882cp → 600cp" in out1,
      [l.strip()[:150] for l in out1.splitlines() if "BỊ CẮT" in l][:1])

# ── T2 (chứng minh ngược — đúng ca `[-1]` cũ): chỉ đổi thứ tự append (manual CUỐI = plain,
# không mang blocked/capped) — nếu khối ⛔/⚠️ KHÔNG hiện ra thì mới là bug `[-1]` thật, pin lại
# để lỡ ai revert fix cũng đỏ ngay.
print("\n[T2] Đối chứng: auto RỒI manual nối sau (plain) — [-1] CŨ sẽ che, bản sửa KHÔNG được che")
p2 = copy.deepcopy(SX)
p2["auto_exit_inject_notes"] = [AUTO_ENTRY, MANUAL_AFTER_PLAIN]
out2 = run_sender(p2, "SpaceX")
check("T2: entry manual plain nối SAU auto vẫn KHÔNG che khối ⛔/⚠️",
      "BỊ CHẶN" in out2 and "BỊ CẮT" in out2 and "BADTK" in out2)

# ── T3: entry manual mang capped_from/capped_to (ca VPB thật) → PHẢI hiện trong khối ⚠️, đánh
# dấu "(duyệt tay)" để phân biệt nguồn gốc cắt KHÁC với cắt tự động (sellable cap).
print("\n[T3] Entry manual có capped_from/capped_to (VPB, duyệt tay) → hiện trong khối ⚠️")
p3 = copy.deepcopy(SX)
p3["auto_exit_inject_notes"] = [MANUAL_AFTER_CAPPED]
out3 = run_sender(p3, "SpaceX")
check("T3: khối ⚠️ hiện cắt THỦ CÔNG (882cp → 600cp, đánh dấu duyệt tay)",
      "BỊ CẮT" in out3 and "882cp → 600cp (duyệt tay)" in out3,
      [l.strip()[:150] for l in out3.splitlines() if "duyệt tay" in l][:1])

# ── T4: auto entry + manual capped riêng mã KHÁC cùng lúc → đếm tổng = cả 2 nguồn (union, không
# OR-chọn-1-nguồn).
print("\n[T4] auto capped (VPB) + manual capped (mã khác) → đếm TỔNG CẢ 2 nguồn")
manual_other = copy.deepcopy(MANUAL_AFTER_CAPPED)
manual_other["injected"][0]["ticker"] = "OTHERTK"
p4 = copy.deepcopy(SX)
p4["auto_exit_inject_notes"] = [AUTO_ENTRY, manual_other]
out4 = run_sender(p4, "SpaceX")
check("T4: tổng mã BỊ CẮT = 2 (1 auto VPB + 1 manual OTHERTK)",
      "2 mã auto-exit BỊ CẮT" in out4 and "VPB" in out4 and "OTHERTK" in out4,
      [l.strip()[:150] for l in out4.splitlines() if "BỊ CẮT" in l][:1])

# ── T5: KHÔNG có auto_exit_inject_notes (ca thường, >99% ngày) → KHÔNG in dòng nào, không crash.
print("\n[T5] Không có auto_exit_inject_notes → không in dòng ⛔/⚠️ nào, không crash")
p5 = copy.deepcopy(SX)
p5.pop("auto_exit_inject_notes", None)
out5 = run_sender(p5, "SpaceX")
check("T5: không có field → KHÔNG in ⛔/⚠️, report vẫn render bình thường",
      "BỊ CHẶN" not in out5 and "BỊ CẮT" not in out5
      and "Kế hoạch giao dịch ngày mai" in out5)

# ── T6: chỉ entry manual (không auto nào) + injected KHÔNG có capped_from/capped_to → không in
# dòng ⚠️ nào (không bịa cắt khi không có).
print("\n[T6] Chỉ entry manual, không capped_from/capped_to → không in ⚠️ (không bịa)")
p6 = copy.deepcopy(SX)
p6["auto_exit_inject_notes"] = [MANUAL_BEFORE, MANUAL_AFTER_PLAIN]
out6 = run_sender(p6, "SpaceX")
check("T6: 2 entry manual không mang cắt nào → không in khối ⚠️",
      "BỊ CẮT" not in out6 and "BỊ CHẶN" not in out6)

# ── T7 (Mblk_none_crash, vòng 5): entry auto PHỔ BIẾN NHẤT trong thực tế (sandbox 10-01) — có
# "source" nhưng CHỈ mang "injected" (writer chỉ ghi key "blocked"/"capped" khi list không rỗng,
# auto_exit_inject.py:480-483) ⇒ key đó VẮNG MẶT hẳn, không phải list rỗng. Mutant bỏ `or []` ở
# `_n.get("blocked")`/`_n.get("capped")` làm `for b in None` → TypeError → rc≠0 → plan T+1 KHÔNG
# được gửi — không FAIL check nào trước đây dựng đúng entry thiếu hẳn key này.
print("\n[T7] Entry auto chỉ có 'injected' (không key blocked/capped) → không crash, rc=0")
AUTO_ONLY_INJECTED = {"at": "2026-10-01T20:40:01+07:00", "source": "auto_exit_inject",
                      "injected": [{"ticker": "SCL", "book": "LAG", "sessions_held": 35}]}
p7a = copy.deepcopy(SX)
p7a["auto_exit_inject_notes"] = [AUTO_ONLY_INJECTED]
out7a = run_sender(p7a, "SpaceX")
check("T7a: rc=0 (không TypeError khi thiếu hẳn key blocked/capped)", LAST_RC[0] == 0,
      f"rc={LAST_RC[0]}")
check("T7a: render bình thường, không in ⛔/⚠️ (không có gì bị chặn/cắt)",
      "BỊ CHẶN" not in out7a and "BỊ CẮT" not in out7a
      and "Kế hoạch giao dịch ngày mai" in out7a)

AUTO_ONLY_CAPPED = {"at": "2026-10-01T20:40:01+07:00", "source": "auto_exit_inject",
                    "injected": [{"ticker": "VPB", "book": "LAG", "sessions_held": 45}],
                    "capped": [{"ticker": "VPB", "book": "LAG", "desired_qty": 882,
                               "capped_qty": 600, "reason": "sellable cap"}]}
p7b = copy.deepcopy(SX)
p7b["auto_exit_inject_notes"] = [AUTO_ONLY_CAPPED]
out7b = run_sender(p7b, "SpaceX")
check("T7b: rc=0 (thiếu hẳn key 'blocked', chỉ có 'capped' — không TypeError)",
      LAST_RC[0] == 0, f"rc={LAST_RC[0]}")
check("T7b: khối ⚠️ BỊ CẮT vẫn hiện đúng dù entry không có key 'blocked'",
      "BỊ CẮT" in out7b and "882cp → 600cp" in out7b)

# ── T8 (N1 B1 vòng 2): `rights_locked` (CP quyền mua khoá chờ niêm yết) PHẢI hiện trong báo cáo —
# bản N1 vòng 1 ghi note vào plan nhưng renderer chỉ đọc blocked/capped ⇒ người duyệt không thấy.
print("\n[T8] Entry auto chỉ có rights_locked → khối ℹ️ khoá chờ niêm yết hiện ra; đối chứng không có → không in")
AUTO_LOCKED = {"at": "2026-10-01T20:40:01+07:00", "source": "auto_exit_inject",
               "rights_locked": [{"ticker": "SCL", "book": "LAG", "locked_qty": 5000,
                                  "reason": "SCL book=LAG: 5000cp CP quyền mua KHOÁ chờ niêm yết (fixture)"}]}
p8 = copy.deepcopy(SX)
p8["auto_exit_inject_notes"] = [AUTO_LOCKED]
out8 = run_sender(p8, "SpaceX")
check("T8a: rc=0 và khối ℹ️ quyền mua KHOÁ hiện đúng mã/KL",
      LAST_RC[0] == 0 and "quyền mua KHOÁ chờ niêm yết" in out8 and "SCL book=LAG: 5000cp" in out8,
      f"rc={LAST_RC[0]}")
check("T8b: đối chứng (T7a, không có rights_locked) không in khối khoá",
      "quyền mua KHOÁ chờ niêm yết" not in out7a)

# ── T9 (rights alert NB 25/10): mã có CP chờ niêm yết (_lk_pending) KHÔNG được hạ MỌI cắt xuống ℹ️ —
# chỉ khi phần cắt do khoá giải thích trọn (locked_shares.split_capped). Sandbox: positions SCL
# open 19.000 / trade 16.000 + registry CP thưởng CONFIRMED; corp_action_lib stub ném lỗi ⇒ đường
# fallback registry (không chạm BQ thật). Dòng ⚠️ phải in rights_diag (runbook bước 5).
print("\n[T9] CP chờ niêm yết: cắt do lệnh book khác / lô quyền hết khoá giữ ⚠️; cắt do khoá ⇒ ℹ️")
import datetime as _dt  # noqa: E402
_ex = (_dt.date.fromisoformat(TODAY_ICT) - _dt.timedelta(days=20)).isoformat()
_acc_no = str(SX.get("account_no"))
LK_FILES = {
    "corp_action_lib.py": "def pricing_events(*a, **k):\n    raise RuntimeError('stub selfcheck: no BQ')\n",
    "data/corp_actions.json": json.dumps({"actions": [
        {"ticker": "SCL", "event_type": "BONUS_ISSUE", "qty_multiplier": 1.2, "ex_date": _ex,
         "_status": "CONFIRMED — selfcheck"}]}),
    "data/execution_logs/dnse_raw_{today}.jsonl": json.dumps(
        {"ts": TODAY_ICT + "T20:30:00", "kind": "positions", "account_no": _acc_no,
         "payload": {"positions": [{"symbol": "SCL", "openQuantity": 19000, "tradeQuantity": 16000}]}}) + "\n",
}
CAP_SCL = {"ticker": "SCL", "book": "LAG", "desired_qty": 16000, "capped_qty": 14000, "reason": "SCL cap fixture"}
OTHER_SCL = {"id": "SELL-SCL-PARKMERGE-X", "ticker": "SCL", "side": "sell", "qty": 2000,
             "book": "custom30V_parking", "price": 25000}


def _p9(capped, extra_orders=()):
    p = copy.deepcopy(SX)
    p["orders"] = list(p.get("orders") or []) + list(extra_orders)
    p["auto_exit_inject_notes"] = [{"at": "2026-10-01T20:40:01+07:00", "source": "auto_exit_inject",
                                    "capped": [capped]}]
    return p


out9c = run_sender(_p9(CAP_SCL), "SpaceX", LK_FILES)
check("T9c ĐỐI CHỨNG: cắt 2.000 ≤ khoá 3.000, không lệnh book khác ⇒ ℹ️ CP chờ niêm yết, KHÔNG ⚠️ SCL",
      LAST_RC[0] == 0 and "CP chờ niêm yết bổ sung" in out9c and "SCL 3,000cp" in out9c
      and "16000cp → 14000cp" not in out9c, f"rc={LAST_RC[0]}")
out9a = run_sender(_p9(CAP_SCL, [OTHER_SCL]), "SpaceX", LK_FILES)
check("T9a: SELL book khác chiếm sellable (ca P13) ⇒ GIỮ ⚠️ BỊ CẮT SCL 16000→14000",
      LAST_RC[0] == 0 and "BỊ CẮT" in out9a and "SCL (LAG): 16000cp → 14000cp" in out9a, f"rc={LAST_RC[0]}")
_diag = "lô quyền mua 5000cp (event E1, credit_date 2026-11-20, CHƯA khai listing_date): đã 11 phiên > hạn 10 phiên"
out9b = run_sender(_p9(dict(CAP_SCL, rights_diag=_diag)), "SpaceX", LK_FILES)
check("T9b: lô quyền hết khoá (rights_diag) ⇒ GIỮ ⚠️ và dòng ⚠️ in chẩn đoán",
      LAST_RC[0] == 0 and "SCL (LAG): 16000cp → 14000cp — " + _diag in out9b, f"rc={LAST_RC[0]}")

_p9d = _p9(CAP_SCL)
_p9d["auto_exit_inject_notes"][0]["rights_locked"] = [{"ticker": "SCL", "book": "LAG", "locked_qty": 2500,
                                                         "reason": "SCL book=LAG: 2500cp KHOÁ fixture"}]
out9d = run_sender(_p9d, "SpaceX", LK_FILES)
check("T9d arch-review NB1: khoá 3.000 − 2.500 lô quyền đã tách = 500 < cắt 2.000 ⇒ GIỮ ⚠️ (không đếm khoá 2 lần)",
      LAST_RC[0] == 0 and "SCL (LAG): 16000cp → 14000cp" in out9d, f"rc={LAST_RC[0]}")

print(f"\n{'=' * 72}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
for f in FAIL:
    print(f"  ✗ {f}")
sys.exit(1 if FAIL else 0)
