#!/usr/bin/env python3
"""E2E: chạy THẬT `process_account()` của injector ĐÃ VÁ (patch A2) trên plan tạm + state
tạm + broker giả, replay đúng con số sự cố 2026-07-24 SpaceX.

Vì sao cần file này ngoài selfcheck module: selfcheck chỉ gọi hàm gate trực tiếp. Cái chưa
được chứng minh là **đường dây thật** — patch có gọi gate đúng chỗ không, order sau khi
SHRINK có ghi đúng vào plan JSON không, ledger có ghi `cash_gate` không, và ca SKIP có để
lại vết cho báo cáo 21:00 không. Đó chính là loại lỗi mà đọc patch không thấy được
(skill verify-before-done).

Chạy:  python3 mike/agents/Taylor/research/inject_cash_gate_e2e_test.py
       (tự áp patch vào bản COPY trong tmpdir — KHÔNG đụng file production)
KHÔNG mạng, KHÔNG broker thật, KHÔNG ghi vào data/ production.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types

_here = os.path.abspath(__file__)          # .../mike/agents/Taylor/research/<file>.py
WC = _here
for _ in range(5):                          # file → research → Taylor → agents → mike → WC
    WC = os.path.dirname(WC)
sys.path.insert(0, WC)

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


class FakeBroker:
    def __init__(self, cash, pp=None, positions=None, quote=(19900, 40000)):
        self.cash, self.pp = cash, pp or {}
        self._pos = positions or {}
        self._q = quote
        self.client = types.SimpleNamespace(loan_package_id=1841)

    def connect(self):
        return True

    def get_positions(self):
        return self._pos

    def get_quote(self, symbol):
        return types.SimpleNamespace(last=self._q[0], day_volume=self._q[1])

    def get_cash(self):
        return self.cash

    def get_buying_power(self, symbol, price, loan_package_id=None):
        key = self.client.loan_package_id if loan_package_id is None else loan_package_id
        return self.pp.get(key)

    def _resolve_loan_package_id(self, symbol):
        return 1122 if symbol == "TV1" else self.client.loan_package_id


def load_patched_injector(tmp):
    """Áp patch vào bản copy trong tmpdir rồi import module đó."""
    work = os.path.join(tmp, "wc")
    os.makedirs(os.path.join(work, "mike", "bin"))
    shutil.copy(os.path.join(WC, "mike", "bin", "discretionary_accumulation_inject.py"),
                os.path.join(work, "mike", "bin"))
    patch = os.path.join(WC, "mike", "agents", "Taylor", "research",
                         "discretionary_inject_cash_gate.patch")
    # cwd=work (KHÔNG dùng --directory): `git apply --directory <abs>` trả rc=0 nhưng ghi ra
    # chỗ khác, file đích không hề đổi — đúng loại "chạy xong ≠ có tác dụng" mà
    # verify-before-done cảnh báo. Nên phải KIỂM CHỨNG nội dung sau khi áp, không tin rc.
    r = subprocess.run(["git", "apply", patch], cwd=work, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"không áp được patch: {r.stderr}")
    path = os.path.join(work, "mike", "bin", "discretionary_accumulation_inject.py")
    if "gate_injected_order" not in open(path, encoding="utf-8").read():
        raise SystemExit("git apply trả rc=0 nhưng file KHÔNG hề được vá — test vô nghĩa.")
    spec = importlib.util.spec_from_file_location("inject_patched", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_fixtures(tmp, mod, v24_cost_vnd):
    """plan chứa lệnh V2.4 + state TV1 active, trong tmpdir."""
    mod.PLAN_DIR = os.path.join(tmp, "plans")
    mod.DISC_DIR = os.path.join(tmp, "disc")
    os.makedirs(mod.PLAN_DIR)
    os.makedirs(mod.DISC_DIR)
    plan_date = "2026-08-05"
    plan = {"plan_date": plan_date, "account": "SpaceX", "orders": [
        {"id": "BUY-PVT-00", "ticker": "PVT", "side": "buy", "qty": 1000,
         "ref_price": v24_cost_vnd // 1000, "book": "CAPIT",
         "estimated_cost_vnd": v24_cost_vnd}]}
    with open(os.path.join(mod.PLAN_DIR, f"plan_SpaceX_{plan_date}.json"), "w",
              encoding="utf-8") as f:
        json.dump(plan, f)
    src = json.load(open(os.path.join(WC, "data", "trade_plans", "discretionary",
                                      "state_TV1_SpaceX.json"), encoding="utf-8"))
    src.update({"status": "active", "target_qty": 400,
                "baseline_qty_before_program": 0, "ledger": []})
    src.pop("completed_at", None)
    src.pop("completed_reason", None)
    with open(os.path.join(mod.DISC_DIR, "state_TV1_SpaceX.json"), "w",
              encoding="utf-8") as f:
        json.dump(src, f)
    return plan_date


def read_plan(mod, plan_date):
    return json.load(open(os.path.join(mod.PLAN_DIR, f"plan_SpaceX_{plan_date}.json"),
                          encoding="utf-8"))


def read_state(mod):
    return json.load(open(os.path.join(mod.DISC_DIR, "state_TV1_SpaceX.json"),
                          encoding="utf-8"))


def scenario(label, v24_cost, cash, pp=None, expect_qty=None, expect_action=None):
    print(f"\n[{label}]")
    with tempfile.TemporaryDirectory() as tmp:
        mod = load_patched_injector(tmp)
        plan_date = make_fixtures(tmp, mod, v24_cost)
        br = FakeBroker(cash=cash, pp=pp)
        # broker giả thay cho DNSE thật; account_mode ép "live" để gate thực sự chạy
        mod.broker_filled_qty = lambda acct, aid, tk, base: (0, br)
        mod.live_dnse_labels = lambda: ["SpaceX", "ZaloPay"]
        # profile account: dùng file secrets thật chỉ để lấy account_id — thay bằng stub
        rc = None
        orig_process = mod.process_account
        # vá đường đọc secrets bằng cách chèn profile giả vào cwd tạm
        secrets = os.path.join(tmp, "secrets")
        os.makedirs(secrets)
        with open(os.path.join(secrets, "trading_bot_accounts.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"accounts": [{"label": "SpaceX", "account_id": "0002023347"}]}, f)
        mod.WC_ROOT = tmp
        rc = orig_process("SpaceX", plan_date, dry_run=False)
        plan = read_plan(mod, plan_date)
        state = read_state(mod)
        disc = [o for o in plan["orders"] if o.get("book") == "DISCRETIONARY_SPECIAL"]
        qty = disc[0]["qty"] if disc else 0
        check(f"rc = 0", rc == 0, rc)
        check(f"qty chèn = {expect_qty} (thực tế {qty})", qty == expect_qty, qty)
        if expect_action == "SKIP":
            check("có cash_gate_notes trong plan cho báo cáo 21:00",
                  bool(plan.get("cash_gate_notes")), plan.get("cash_gate_notes"))
            check("state ghi history_noninject skip_cash_gate",
                  any(h.get("action") == "skip_cash_gate"
                      for h in state.get("history_noninject", [])),
                  state.get("history_noninject"))
        else:
            check("ledger ghi cash_gate để audit",
                  bool(state["ledger"]) and "cash_gate" in state["ledger"][0],
                  state.get("ledger"))
        if expect_action == "SHRINK":
            check("order ghi lại qty gốc (cash_gate_shrunk_from_qty)",
                  disc and disc[0].get("cash_gate_shrunk_from_qty") == 400, disc)
            check("note của order nêu CASH-GATE",
                  disc and "[CASH-GATE]" in disc[0].get("note", ""), disc)
        return plan, state


def main():
    print("=" * 78)
    print("E2E injector ĐÃ VÁ — replay sự cố 2026-07-24 trên đường dây thật")
    print("=" * 78)

    # 1) REPLAY 07-24: V2.4 45,9M, cash 49.125.163đ, pp0Buy không đo được.
    #    Không gate: engine muốn 400cp (remaining=400, cap không bind) = 7,96M → tổng vượt.
    #    Có gate: headroom = 49.125.163 − 45.934.425 = 3.190.738đ → mua nổi 100cp (1,99M).
    scenario("1. REPLAY 07-24 — cash chỉ đủ 1 lô", v24_cost=45_900_000,
             cash=49_125_163, pp=None, expect_qty=100, expect_action="SHRINK")

    # 2) Cash dư dả → gate không cản trở, chèn đủ 400cp.
    scenario("2. cash dư dả → PASS nguyên vẹn", v24_cost=10_000_000,
             cash=500_000_000, pp={1122: 500_000_000}, expect_qty=400,
             expect_action="PASS")

    # 3) V2.4 đã tiêu gần hết → không đủ 1 lô → BỎ PHIÊN + để lại vết cho người.
    scenario("3. V2.4 ăn hết tiền → SKIP + vết cho báo cáo 21:00", v24_cost=48_000_000,
             cash=49_125_163, pp=None, expect_qty=0, expect_action="SKIP")

    print("\n" + "=" * 78)
    print(f"KẾT QUẢ E2E: {PASS} PASS / {FAIL} FAIL")
    print("=" * 78)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
