#!/usr/bin/env python3
"""Selfcheck — cq-2026-09-20 hard-boundary (config.py load_accounts()/live_dnse_labels()).

Covers 2 fixes from commit ebb01238 (+ arch-reviewer follow-up), neither of which had any
selfcheck before this file — flagged in review as "the 24 passing selfchecks pass identically
with and without this commit, they are not coverage":

  1. Unknown key trong `overrides` per-account phải được cảnh báo (như load_config() đã làm cho
     config chung) — VÀ cảnh báo đó PHẢI đi ra stderr, không phải stdout. `live_dnse_labels()`
     (dùng `load_accounts()`) là nguồn 9 script cron parse THẲNG stdout thành danh sách account
     (`for_each_live_account.sh`, `bq_freshness_check.sh`...) — một dòng cảnh báo lẫn vào đó bị
     word-split thành account rác + (ca `bq_freshness_check.sh`) làm hỏng số OFFBOOK_VND bơm vào
     prompt lập plan của DollarBill. Bug thật do arch-reviewer sandbox-repro 2026-09-20.
  2. `live_dnse_labels()` phải giải broker CÙNG công thức `make_broker()` dùng
     (`p.get("broker") or cfg.get("broker") or "phs"`, case-insensitive) — không so trực tiếp
     field thô `p["broker"]` (None khi account kế thừa broker từ config chung). Account kế thừa
     `broker=dnse` từ global mà profile không khai `broker` bị loại ÂM THẦM khỏi mọi vòng cron
     dùng chung dù bot_execute.py vẫn giao dịch nó bằng DNSE thật.

Fixture accounts/config: tempfile riêng qua `TRADING_BOT_RUNTIME_ROOT`, KHÔNG đụng secrets thật.
Case E dùng secrets thật (chỉ đọc, best-effort skip nếu môi trường không có).

Chạy: source wc_env.sh && $DNA_PYEXE account_overrides_broker_resolution_selfcheck.py
"""
import importlib
import json
import os
import subprocess
import sys
import tempfile

WC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC)

FAILS, N = [], 0


def check(name, cond, detail=""):
    global N
    N += 1
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{(' — ' + str(detail)) if detail else ''}")
    if not cond:
        FAILS.append(name)


def _fresh_config_module():
    """load_config()/live_dnse_labels() đọc path module-level constants tại import time — cần
    reload sau khi đổi TRADING_BOT_RUNTIME_ROOT để CONFIG_FILE/ACCOUNTS_FILE trỏ đúng fixture."""
    if "trading_bot.config" in sys.modules:
        return importlib.reload(sys.modules["trading_bot.config"])
    import trading_bot.config as m
    return m


def _write_fixture(root, accounts, global_cfg=None):
    os.makedirs(os.path.join(root, "secrets"), exist_ok=True)
    with open(os.path.join(root, "secrets", "trading_bot_accounts.json"), "w") as f:
        json.dump({"accounts": accounts}, f)
    with open(os.path.join(root, "secrets", "trading_bot_config.json"), "w") as f:
        json.dump(global_cfg or {}, f)


def _run_capture(root, snippet):
    """Chạy snippet trong subprocess SẠCH (không import cache) — đúng cách for_each_live_account.sh
    thực sự gọi: `python3 -c "..."`, stdout/stderr tách riêng như shell capture thật."""
    env = dict(os.environ, TRADING_BOT_RUNTIME_ROOT=root, PYTHONPATH=WC)
    p = subprocess.run([sys.executable, "-c", snippet], env=env,
                       capture_output=True, text=True, timeout=30)
    return p.stdout, p.stderr


LABELS_SNIPPET = ("import sys; sys.path.insert(0, %r)\n"
                  "from trading_bot.config import live_dnse_labels\n"
                  "for l in live_dnse_labels():\n"
                  "    print(l)\n") % WC


def main():
    print("=== A/B/C: unknown override key — stderr-only, không lẫn vào stdout label list ===")
    with tempfile.TemporaryDirectory() as root:
        _write_fixture(root, [
            {"label": "InheritAcct", "mode": "live", "broker": None, "enabled": True,
             "overrides": {"fill_timing_live_gat": False}},   # typo cố ý — khóa lạ
        ], global_cfg={"broker": "dnse"})
        out, err = _run_capture(root, LABELS_SNIPPET)
        stdout_labels = [l for l in out.splitlines() if l.strip()]
        check("A1 stdout label list KHÔNG lẫn dòng cảnh báo (đúng 1 account thật)",
              stdout_labels == ["InheritAcct"], stdout_labels)
        check("A2 cảnh báo khóa lạ có xuất hiện, nhưng trên stderr",
              "khóa lạ" in err and "fill_timing_live_gat" in err, err.strip())
        check("A3 cảnh báo KHÔNG rò sang stdout",
              "khóa lạ" not in out, out)

    print("=== C: override key hợp lệ — KHÔNG cảnh báo giả ===")
    with tempfile.TemporaryDirectory() as root:
        _write_fixture(root, [
            {"label": "ValidOverride", "mode": "live", "broker": "dnse", "enabled": True,
             "overrides": {"fill_timing_live_gate": False, "max_orders_per_day": 10}},
        ])
        out, err = _run_capture(root, LABELS_SNIPPET)
        check("C1 override key hợp lệ (đã có trong DEFAULTS) không sinh cảnh báo",
              "khóa lạ" not in err, err.strip())
        check("C2 account vẫn được liệt kê đúng",
              out.strip().splitlines() == ["ValidOverride"], out)

    print("=== D: broker resolution == make_broker() (p.get('broker') or cfg.get('broker') or 'phs') ===")
    cases = [
        ("D1 profile broker=None kế thừa global broker=dnse -> CÓ trong live list",
         [{"label": "D1acc", "mode": "live", "broker": None, "enabled": True}],
         {"broker": "dnse"}, ["D1acc"]),
        ("D2 profile broker='DNSE' hoa -> CÓ trong live list (case-insensitive)",
         [{"label": "D2acc", "mode": "live", "broker": "DNSE", "enabled": True}],
         {}, ["D2acc"]),
        ("D3 profile broker='phs' tường minh -> KHÔNG trong live list dù global=dnse",
         [{"label": "D3acc", "mode": "live", "broker": "phs", "enabled": True}],
         {"broker": "dnse"}, []),
        ("D4 profile broker=None + global KHÔNG khai broker (fallback DEFAULTS='phs') "
         "-> KHÔNG trong live list",
         [{"label": "D4acc", "mode": "live", "broker": None, "enabled": True}],
         {}, []),
    ]
    for name, accounts, gcfg, expected in cases:
        with tempfile.TemporaryDirectory() as root:
            _write_fixture(root, accounts, global_cfg=gcfg)
            out, _ = _run_capture(root, LABELS_SNIPPET)
            got = [l for l in out.splitlines() if l.strip()]
            check(name, got == expected, f"got={got} expected={expected}")

    print("=== E: regression trên secrets THẬT (best-effort, skip nếu không có) ===")
    real_secrets = os.path.join(WC, "secrets", "trading_bot_accounts.json")
    if os.path.isfile(real_secrets):
        CFG = _fresh_config_module()
        real_labels = set(CFG.live_dnse_labels())
        check("E1 SpaceX vẫn trong live_dnse_labels() thật",
              "SpaceX" in real_labels, sorted(real_labels))
        check("E2 ZaloPay vẫn trong live_dnse_labels() thật",
              "ZaloPay" in real_labels, sorted(real_labels))
    else:
        print("  SKIP  không có secrets/trading_bot_accounts.json trong môi trường này")

    print(f"\n===== account_overrides_broker_resolution_selfcheck: "
         f"{N - len(FAILS)}/{N} PASS =====")
    if FAILS:
        print("FAILED:", FAILS)
        sys.exit(1)


if __name__ == "__main__":
    main()
