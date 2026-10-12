#!/usr/bin/env python3
"""Nghiệm thu 4 (vòng 2): áp proposed_acks.json trên BẢN SAO dữ liệu.

Dựng hai cây sandbox giống hệt nhau (bin/ của nhánh + bản sao data/, dnse_raw là symlink chỉ-đọc):
  NOACK — không có data/cash_identity_acks.json;  ACK — có, = proposed_acks.json.
So với cây master (canonical, đọc data/ thật) trên MỌI ngày báo cáo của hai tài khoản:
  · mọi trường của nav_period_returns ngoài `cash_flow_*` phải bằng nhau từng byte JSON;
  · dòng nhà đầu tư của báo cáo ngày (daily_nav_snapshot.cash_identity_report) ở ACK / NOACK.
Không ghi gì vào data/ thật.
Dùng: python3 4_acks_on_copy.py <worktree_bin> <WC_ROOT thật> <proposed_acks.json>
"""
import csv
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

BIN, WC, ACKS = sys.argv[1:4]
MASTER_BIN = os.path.join(WC, "mike", "bin")
BOX = "/tmp/fcf_r2/acks_copy"
ACCOUNTS = ("SpaceX", "ZaloPay")
ENV = {k: v for k, v in os.environ.items() if k not in ("TZ", "WC_ROOT", "MIKE_ROOT", "ACCOUNT_CASH_FLOWS_PATH")}
ENV["MIKE_BOT_TEST_MODE"] = "1"


def build(name, with_acks):
    root = os.path.join(BOX, name, "WC")
    shutil.rmtree(os.path.join(BOX, name), ignore_errors=True)
    os.makedirs(os.path.join(root, "mike"))
    shutil.copytree(BIN, os.path.join(root, "mike", "bin"), ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(os.path.join(WC, "trading_bot"), os.path.join(root, "trading_bot"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    open(os.path.join(root, "wc_env.sh"), "w").close()
    open(os.path.join(root, "mike", "MIKE.md"), "w").close()
    logs = os.path.join(root, "data", "execution_logs")
    os.makedirs(logs)
    src = os.path.join(WC, "data", "execution_logs")
    for fn in os.listdir(src):
        if fn.startswith("dnse_raw_") and fn.endswith(".jsonl"):
            os.symlink(os.path.join(src, fn), os.path.join(logs, fn))
        elif fn.startswith("nav_history_") and fn.endswith(".csv"):
            shutil.copy2(os.path.join(src, fn), logs)
    for fn in ("account_inception.json", "account_cash_flows.json", "account_seed_capital.json", "corp_actions.json"):
        if os.path.exists(os.path.join(WC, "data", fn)):
            shutil.copy2(os.path.join(WC, "data", fn), os.path.join(root, "data", fn))
    if with_acks:
        shutil.copy2(ACKS, os.path.join(root, "data", "cash_identity_acks.json"))
    return root


def cli(bin_dir, account, date):
    p = subprocess.run([sys.executable, os.path.join(bin_dir, "nav_period_returns.py"), "--account", account,
                        "--report-date", date], capture_output=True, text=True, env=ENV)
    return json.loads(p.stdout) if p.returncode == 0 else {"__rc__": p.returncode, "__err__": p.stderr[-200:]}


def strip(blob):
    return {k: v for k, v in blob.items() if not k.startswith("cash_flow_")}


def count_numbers(value):
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return 1
    if isinstance(value, dict):
        return sum(count_numbers(v) for v in value.values())
    if isinstance(value, list):
        return sum(count_numbers(v) for v in value)
    return 0


def main():
    noack, ack = build("NOACK", False), build("ACK", True)
    dates = {}
    for account in ACCOUNTS:
        with open(os.path.join(WC, "data", "execution_logs", f"nav_history_{account}.csv"), encoding="utf-8") as f:
            dates[account] = [r["date"] for r in csv.DictReader(f) if r.get("date")]
    jobs = [(a, d) for a in ACCOUNTS for d in dates[a]]
    with ThreadPoolExecutor(8) as ex:
        master = list(ex.map(lambda j: cli(MASTER_BIN, *j), jobs))
        got_no = list(ex.map(lambda j: cli(os.path.join(noack, "mike", "bin"), *j), jobs))
        got_ack = list(ex.map(lambda j: cli(os.path.join(ack, "mike", "bin"), *j), jobs))
    for account in ACCOUNTS:
        idx = [i for i, j in enumerate(jobs) if j[0] == account]
        n_num = sum(count_numbers(master[i]) for i in idx)
        diff_no = [jobs[i][1] for i in idx if json.dumps(strip(got_no[i]), sort_keys=True) != json.dumps(master[i], sort_keys=True)]
        diff_ack = [jobs[i][1] for i in idx if json.dumps(strip(got_ack[i]), sort_keys=True) != json.dumps(master[i], sort_keys=True)]
        extra = sorted({k for i in idx for k in got_ack[i] if k not in master[i]})
        last = idx[-1]
        print(f"== {account}: {len(idx)} ngày báo cáo, {n_num} trường số trên master")
        print(f"   nhánh KHÔNG áp acks vs master (bỏ cash_flow_*): {len(diff_no)} ngày lệch {diff_no[:5]}")
        print(f"   nhánh CÓ áp acks    vs master (bỏ cash_flow_*): {len(diff_ack)} ngày lệch {diff_ack[:5]}")
        print(f"   khoá nhánh thêm so với master: {extra}")
        for label, got in (("KHÔNG áp", got_no), ("CÓ áp", got_ack)):
            n_open = [len([x for x in got[i]["cash_flow_warnings"] if "CHỜ KHAI" in x]) for i in idx]
            print(f"   {label}: ngày cuối {jobs[last][1]} — cash_flow_investor_line = {got[last]['cash_flow_investor_line']!r}; "
                  f"cash_flow_warnings {len(got[last]['cash_flow_warnings'])} dòng; số ngày có dòng nhà đầu tư = "
                  f"{sum(1 for i in idx if got[i]['cash_flow_investor_line'])}/{len(idx)} (max dòng CHỜ KHAI/ngày {max(n_open)})")
    # Dòng của báo cáo ngày (đúng hàm mà daily_nav_snapshot.main gọi), lượt chụp 2026-10-12.
    code = ("import sys, json; sys.path.insert(0, sys.argv[1]); import daily_nav_snapshot as d\n"
            "for a in ('SpaceX', 'ZaloPay'):\n"
            "    r = d.cash_identity_report(a, '2026-10-12', nav_dir=d.EXEC_DIR, raw_dir=d.EXEC_DIR)\n"
            "    print(json.dumps({'account': a, 'investor_line': r['investor_line'], 'ops_today': r['ops_today'], 'n_ops_lines': len(r['ops_lines']), 'error': r['error']}, ensure_ascii=False))\n")
    for label, root in (("KHÔNG áp acks", noack), ("CÓ áp acks", ack)):
        p = subprocess.run([sys.executable, "-c", code, os.path.join(root, "mike", "bin")], capture_output=True,
                           text=True, env=ENV, cwd=os.path.join(root, "mike"))
        print(f"== báo cáo ngày 2026-10-12, {label}:")
        print(p.stdout.strip() or p.stderr[-800:])
    real_acks = os.path.join(WC, "data", "cash_identity_acks.json")
    print(f"== data/cash_identity_acks.json THẬT tồn tại: {os.path.exists(real_acks)} (phải là False — vòng này không tạo)")


if __name__ == "__main__":
    main()
