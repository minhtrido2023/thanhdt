#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck khối LOSSBRAKE của ops_health_check.sh: rc của `nav_loss_brake_monitor.py
--health-line` phải đổi thành ĐÚNG loại dòng — không đo được (rc=1) mang marker `[WARN-ONLY]`,
phanh chạm / tạm tính vượt (rc=5) là dòng 🔴 riêng; cả hai KHÔNG được để khối ROUTING đẩy sang
autofix (monitor chỉ cảnh báo, user quyết).

Chạy khối THẬT cắt từ ops_health_check.sh (giữa # LOSSBRAKE_BEGIN / # LOSSBRAKE_END) với
subprocess.run giả — không chạm mạng, không đọc dữ liệu thật.
    python3 mike/bin/ops_health_check_lossbrake_selfcheck.py
"""
import os
import re
import subprocess
import sys
import types

BIN = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(BIN, "ops_health_check.sh"), encoding="utf-8").read()
m = re.search(r"# LOSSBRAKE_BEGIN\n(.*?)# LOSSBRAKE_END\n", SRC, re.S)
if not m:
    sys.exit("FAIL: không tìm thấy khối LOSSBRAKE_BEGIN/END trong ops_health_check.sh")
BLOCK = m.group(1)
fails = 0
WARNS = []          # số warn sau mỗi lần chạy khối


def check(name, cond, detail=""):
    global fails
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + ("" if cond else f"  {detail}"))
    fails += 0 if cond else 1


def run_block(rc, stdout, stderr="", boom=None, account="ZaloPay", runonce="ZaloPay"):
    lines, calls = [], []

    def fake_run(cmd, **kw):
        calls.append((cmd, kw))
        if boom:
            raise boom
        return types.SimpleNamespace(returncode=rc, stdout=stdout, stderr=stderr)

    fake_sp = types.SimpleNamespace(run=fake_run, TimeoutExpired=subprocess.TimeoutExpired)
    env = {"subprocess": fake_sp, "sys": sys, "os": os, "wc_root": "/WC", "account": account, "runonce_label": runonce,
           "lines": lines, "warn": 0}

    def W(s):
        env["warn"] += 1
        lines.append("⚠️ " + s)

    env.update(W=W, OK=lambda s: lines.append("✅ " + s))
    exec(BLOCK, env)
    WARNS.append(env["warn"])
    return lines, calls


def routable(line):
    """Đúng phép lọc của khối ROUTING: dòng ⚠️/❌ không mang [WARN-ONLY]."""
    return bool(re.search("⚠️|❌", line)) and "[WARN-ONLY]" not in line


L, calls = run_block(0, "Phanh lỗ NAV [ZaloPay] phiên 09/10 (NAV toàn tài khoản): Lỗ một ngày: -0,06%\n")
check("rc=0 ⇒ đúng MỘT dòng ✅", len(L) == 1 and L[0].startswith("✅ Phanh lỗ NAV [ZaloPay]"), f"{L}")
cmd = calls[0][0]
check("gọi đúng script + --health-line + --account của lượt này",
      cmd[1] == "/WC/mike/bin/nav_loss_brake_monitor.py" and cmd[2:] == ["--health-line", "--account",
                                                                         "ZaloPay"], f"{cmd}")
check("có timeout", calls[0][1].get("timeout"), f"{calls[0][1]}")

L, _ = run_block(1, "Phanh lỗ NAV [ZaloPay] phiên 09/10: Lỗ một ngày: KHÔNG ĐO ĐƯỢC — x · tạm tính -1,00%\n")
check("rc=1 (không đo được) ⇒ ⚠️ mang [WARN-ONLY]",
      len(L) == 1 and L[0].startswith("⚠️ [WARN-ONLY] Phanh lỗ NAV"), f"{L}")
check("rc=1 ⇒ KHÔNG bị route sang autofix", not routable(L[0]), f"{L}")

L, _ = run_block(5, "Phanh lỗ NAV [ZaloPay] phiên 09/10: Lỗ một ngày: -5,20% (ĐÃ CHẠM) · ⚠️ ghi chú ❌ lạ\n")
check("rc=5 (phanh CHẠM / tạm tính vượt) ⇒ dòng 🔴 RIÊNG, KHÔNG mang nhãn [WARN-ONLY] chung",
      len(L) == 1 and L[0].startswith("🔴 PHANH LỖ NAV CHẠM NGƯỠNG") and "[WARN-ONLY]" not in L[0]
      and "ĐÃ CHẠM" in L[0] and "USER QUYẾT" in L[0], f"{L}")
check("rc=5 ⇒ KHÔNG bị route sang autofix (kể cả khi thân dòng có ⚠️/❌) nhưng VẪN tính 1 warn",
      not routable(L[0]) and WARNS[-1] == 1, f"{L} warn={WARNS[-1]}")

L, _ = run_block(2, "Phanh lỗ NAV [ZaloPay]: file trạng thái CŨ — đang ghi phiên 2026-10-08\n")
check("rc=2 (monitor không chạy) ⇒ ⚠️ thường, route được cho vận hành",
      len(L) == 1 and routable(L[0]) and "CŨ" in L[0], f"{L}")

L, _ = run_block(3, "Phanh lỗ NAV [ZaloPay] phiên 09/10 (NAV toàn tài khoản): ❌ MONITOR LỖI — Cả 3 phanh: "
                    "KHÔNG ĐO ĐƯỢC — monitor lỗi khi đo ZaloPay: ValueError: x\n")
check("rc=3 (monitor chạy nhưng LỖI / không gửi được cảnh báo) ⇒ ⚠️ thường, KHÔNG mang [WARN-ONLY] "
      "⇒ tới được autofix", len(L) == 1 and routable(L[0]) and "MONITOR LỖI" in L[0], f"{L}")

L, _ = run_block(5, "Phanh lỗ NAV [ZaloPay] phiên 09/10: Lỗ một ngày: TẠM TÍNH -8,00% ĐÃ VƯỢT ngưỡng -5%\n")
check("rc=5 số tạm tính vượt ngưỡng ⇒ dòng 🔴, không route (user quyết)",
      len(L) == 1 and L[0].startswith("🔴") and not routable(L[0]) and "ĐÃ VƯỢT" in L[0], f"{L}")

L, _ = run_block(2, "", stderr="python3: can't open file 'x.py': [Errno 2]")
check("không có stdout ⇒ ⚠️ kèm rc + stderr đọc được (§29)",
      len(L) == 1 and "rc=2" in L[0] and "can't open file" in L[0] and routable(L[0]), f"{L}")

L, _ = run_block(0, "")
check("rc=0 mà không in gì ⇒ KHÔNG được coi là ✅", len(L) == 1 and L[0].startswith("⚠️"), f"{L}")

L, _ = run_block(0, "", boom=subprocess.TimeoutExpired("x", 60))
check("timeout ⇒ ⚠️ nêu tên lỗi", len(L) == 1 and "TimeoutExpired" in L[0], f"{L}")

L, _ = run_block(7, "dòng lạ\n")
check("rc lạ ⇒ ⚠️, không ✅", len(L) == 1 and L[0].startswith("⚠️") and "rc=7" in L[0], f"{L}")

# --- lỗi cấp FLEET (rc=2) chỉ route ở lượt account đầu; account sau chỉ hiển thị -------------------
L, _ = run_block(2, "Phanh lỗ NAV [SpaceX]: file trạng thái CŨ — đang ghi phiên 2026-10-08\n", account="SpaceX", runonce="ZaloPay")
check("rc=2 ở account KHÔNG phải lượt RUNONCE ⇒ [WARN-ONLY] (không route lần 2)",
      len(L) == 1 and L[0].startswith("⚠️ [WARN-ONLY]") and not routable(L[0]), f"{L}")
L, _ = run_block(2, "Phanh lỗ NAV [ZaloPay]: file trạng thái CŨ — đang ghi phiên 2026-10-08\n", account="ZaloPay", runonce="ZaloPay")
check("rc=2 ở account RUNONCE ⇒ vẫn route", len(L) == 1 and routable(L[0]), f"{L}")
L, _ = run_block(2, "Phanh lỗ NAV [SpaceX]: file CŨ\n", account="SpaceX", runonce="")
check("rc=2 khi RUNONCE rỗng (không xác định) ⇒ vẫn route (kêu to, không im)", len(L) == 1 and routable(L[0]), f"{L}")
L, _ = run_block(3, "Phanh lỗ NAV [SpaceX]: ❌ MONITOR LỖI x\n", account="SpaceX", runonce="ZaloPay")
check("rc=3 (lỗi riêng từng account) ⇒ VẪN route ở account sau", len(L) == 1 and routable(L[0]), f"{L}")
L, _ = run_block(1, "", stderr="Traceback (most recent call last):\n  File x\nKeyError: 'foo'")
check("stderr nhiều dòng ⇒ gộp một dòng, giữ cả dòng lỗi cuối (ROUTING grep theo dòng)",
      len(L) == 1 and "\n" not in L[0] and "KeyError: 'foo'" in L[0], f"{L}")

check("khối ROUTING của ops_health_check.sh vẫn lọc bằng marker [WARN-ONLY]",
      "grep -vF '[WARN-ONLY]'" in SRC)
print(f"\n{'OK: toàn bộ assertion PASS' if not fails else f'FAIL: {fails} assertion'}")
sys.exit(1 if fails else 0)
