#!/usr/bin/env python3
"""
anomaly_escalate_selfcheck.py — end-to-end DGC 2026-03-17 (job Taylor_20260717_113024)
Xác nhận luồng: anomaly trip (giá/volume) → escalate due-diligence (Wendy+Spyros)
→ KHÔNG tự mua/bán. + idempotency + phân vai SECONDARY của trạng thái sàn.
Không side-effect thật: monkeypatch _notify/_dispatch_bg, ledger vào tmp.
"""
import os, sys, json, tempfile, subprocess

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, os.path.join(WC, "mike", "bin"))
import anomaly_escalate as AE

ok = True
def check(name, cond):
    global ok
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    ok &= bool(cond)

# ---- Part A: anomaly_scan detect DGC 2026-03-17 (price/volume PRIMARY) ----
print("A. anomaly_scan --selftest (DGC 2026-03-17 + PNJ + negative control):")
r = subprocess.run([sys.executable, os.path.join(WC, "mike/agents/Taylor/anomaly_scan.py"),
                    "--selftest"], capture_output=True, text=True)
print("   " + r.stdout.strip().replace("\n", "\n   "))
check("anomaly_scan selftest exit 0 (DGC 03-17 detected)", r.returncode == 0)

# ---- capture harness (no real notify/dispatch) ----
NOTIFIES, DISPATCHES = [], []
AE._notify = lambda msg, dry: (NOTIFIES.append(msg), True)[1]
AE._dispatch_bg = lambda target, prompt, dry: (DISPATCHES.append((target, prompt)), f"job_{target}")[1]

tmp_ledger = tempfile.NamedTemporaryFile(suffix=".json", delete=False).name
os.remove(tmp_ledger)  # bắt đầu KHÔNG có ledger
AE.LEDGER = tmp_ledger

# DGC 2026-03-17 trip thật (số đo từ BQ cache): ret -6.90%, VNI +1.01%, idio -7.91%
dgc_emit = {"asof": "2026-03-17", "tier_w_count": 0, "status_changes": [],
            "tier_h": [{"ticker": "DGC", "reasons": "IDIOCRASH", "ret": -6.90,
                        "vni_ret": 1.01, "idio": -7.91, "vol_x": 1.24, "close": 68800}]}

# ---- Part B: escalate → khởi động due-diligence, KHÔNG mua/bán ----
print("B. escalate DGC 2026-03-17 → due-diligence:")
nh, ns = AE.escalate(dgc_emit, dry=False)
check("1 tier-H mới escalate (DGC)", nh == ["DGC"])
check("post Trading Daily 1 alert", len(NOTIFIES) == 1)
check("alert nhắc 'due-diligence' + DGC", "due-diligence" in NOTIFIES[0] and "DGC" in NOTIFIES[0])
check("alert ghi rõ KHÔNG tự mua/bán", "KHÔNG tự mua/bán" in NOTIFIES[0])
targets = sorted(t for t, _ in DISPATCHES)
check("dispatch ĐÚNG Wendy + Spyros", targets == ["Spyros", "Wendy"])
check("KHÔNG dispatch agent giao dịch (Mafee/DollarBill)",
      all(t in ("Wendy", "Spyros") for t, _ in DISPATCHES))
check("KHÔNG lệnh mua/bán nào (không gọi bot/order/place)",
      not any(k in p for _, p in DISPATCHES for k in ("place_order", "đặt lệnh", "mua vào", "bán ra")))
led = json.load(open(tmp_ledger))
check("ledger ghi key DGC|2026-03-17", "DGC|2026-03-17" in led)

# ---- Part C: idempotency — chạy lại KHÔNG escalate trùng ----
print("C. idempotency (08:20 + 12:45 gọi trùng):")
NOTIFIES.clear(); DISPATCHES.clear()
nh2, ns2 = AE.escalate(dgc_emit, dry=False)
check("lần 2: 0 tier-H mới (deduped)", nh2 == [])
check("lần 2: 0 notify, 0 dispatch", len(NOTIFIES) == 0 and len(DISPATCHES) == 0)

# ---- Part D: trạng thái sàn RES = SECONDARY (theo dõi thực thi, KHÔNG escalate DD) ----
print("D. trạng thái sàn RES = SECONDARY:")
NOTIFIES.clear(); DISPATCHES.clear()
status_emit = {"asof": "2026-05-13", "tier_h": [], "tier_w_count": 0,
               "status_changes": [{"ticker": "DGC", "type": "STATUS_CHANGE",
                                   "was": {"admin": "NRM", "method": "NRM", "sanction": "NRM"},
                                   "now": {"admin": "RES", "method": "NRM", "sanction": "NRM"}}]}
nh3, ns3 = AE.escalate(status_emit, dry=False)
check("status change post Trading Daily", len(NOTIFIES) == 1)
check("nhãn 'THEO DÕI THỰC THI' rõ ràng", "THEO DÕI THỰC THI" in NOTIFIES[0])
check("nhãn 'KHÔNG phải cảnh báo sớm'", "KHÔNG phải cảnh báo sớm" in NOTIFIES[0])
check("status KHÔNG dispatch DD (secondary, không escalate)", len(DISPATCHES) == 0)

# ---- Part E: dry-run KHÔNG ghi ledger, KHÔNG side-effect ----
print("E. dry-run isolation:")
os.remove(tmp_ledger)
NOTIFIES.clear(); DISPATCHES.clear()
AE.escalate(dgc_emit, dry=True)
check("dry-run KHÔNG viết ledger", not os.path.exists(tmp_ledger))

print("\nSELFCHECK", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
