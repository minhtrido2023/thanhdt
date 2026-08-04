#!/usr/bin/env python3
"""RECON READ-ONLY cho job Mafee_20260804_021040 — KHÔNG đặt lệnh.

Kiểm 4 tiền đề trước khi đặt lệnh thật MBB x100 gói 1840 trên SpaceX:
  1. có trading-token thật hay không (không có → không thể test, dừng)
  2. SpaceX đang giữ MBB bao nhiêu / sellable bao nhiêu (T+2: mua hôm nay
     KHÔNG bán được cùng phiên trừ khi đã có sẵn hàng sellable)
  3. quote MBB hiện tại (raw)
  4. balances hiện tại (raw) — mốc so sánh totalDebt trước/sau
"""
import json
import os
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.chdir("/home/trido/thanhdt/WorkingClaude")

from trading_bot.brokers import DNSEBroker  # noqa: E402

ACC = "0002023347"   # SpaceX


def dump(tag, obj):
    print(f"\n===== {tag} =====")
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


b = DNSEBroker(account_id=ACC, label="SpaceX_probe1840", loan_package_id=1841)
b.connect()

print(f"\n[recon] has_trading_token = {b.client.has_trading_token()}")
print(f"[recon] client.loan_package_id (default account) = {b.client.loan_package_id}")

dump("positions (parsed)", b.get_positions())
dump("positions (RAW)", b.client.positions(ACC))
dump("balances (RAW)", b.client.balances(ACC))

q = b.get_quote("MBB")
dump("quote MBB (RAW mapped)", getattr(q, "raw", None) or q.__dict__)
print(f"[recon] Quote.last={getattr(q,'last',None)} bid={getattr(q,'bid',None)} "
      f"ask={getattr(q,'ask',None)} ref={getattr(q,'ref',None)} "
      f"ceil={getattr(q,'ceiling',None)} floor={getattr(q,'floor',None)}")

dump("loan_packages MBB (RAW)", b.client.loan_packages(ACC, symbol="MBB"))
