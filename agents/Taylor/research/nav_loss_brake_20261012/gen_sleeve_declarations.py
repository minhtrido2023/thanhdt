#!/usr/bin/env python3
"""Sinh bản khai `market_only` cho managed_sleeve_flows.json ở những ngày mà bẫy DUY NHẤT là
"KHÔNG kiểm được lịch corp-action" (snapshot corp_action_daily thiếu / không dùng được) — và CHỈ
khi có bằng chứng độc lập rằng mã loại trừ không có sự kiện quyền nào trong các phiên đó:
tỉ số Close/Price (giá điều chỉnh / giá chưa điều chỉnh) của mã trong CSV giá BQ KHÔNG đổi qua
từng phiên. Cổ tức tiền hay chia tách đều làm tỉ số này nhảy đúng ngày GDKHQ (ca DGC 2026-09-14:
0,8546 → 1,0000), nên "không đổi" = không có sự kiện. Ngày có bẫy KHÁC (KL đổi, giá nhảy, lịch
có sự kiện) KHÔNG được khai hộ — để người xem.

Đây là công cụ dựng SEED cho lịch sử, chạy tay một lần; bản khai sinh ra ghi rõ là kiểm bằng máy.
Dùng: python3 gen_sleeve_declarations.py --price-csv <csv> --state-dir <seed> [--write]
"""
import argparse
import csv
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "bin")))
import nav_loss_brake_monitor as m  # noqa: E402

TRAP = "KHÔNG kiểm được lịch corp-action"
# Close (giá điều chỉnh) của BQ làm tròn theo bước giá ⇒ tỉ số Close/Price dao động vài phần vạn
# giữa hai phiên KHÔNG có sự kiện (đo trên CSV DGC 07-06→10-09: lớn nhất 0,027%, ngày 07-24). Sự kiện quyền
# nhỏ hơn TOL (0,1% giá ≈ 46đ/cp ở giá 46.000) KHÔNG phát hiện được bằng cách này — ghi rõ vào
# bằng chứng của từng bản khai.
TOL = 0.001
ap = argparse.ArgumentParser()
ap.add_argument("--price-csv", required=True)
ap.add_argument("--state-dir", required=True)
ap.add_argument("--now", required=True, help="đồng hồ ICT giả lập (ISO) — để kết quả tái lập được")
ap.add_argument("--write", action="store_true")
args = ap.parse_args()

ratio = {}
with open(args.price_csv, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        ratio[(r["ticker"], r["time"])] = float(r["Close"]) / float(r["Price"])
now = datetime.datetime.fromisoformat(args.now).replace(tzinfo=m.ICT)
ctx = m.Ctx(state_dir=os.path.abspath(args.state_dir), now=now)
profiles = m.load_profiles(ctx.secrets_path)
flows = m._read_json(ctx.sleeve_flows_path, {})
added = 0
for account in [k for k in m._read_json(ctx.inception_path, {}) if not k.startswith("_")]:
    chain = m.build_chain(ctx, account, profiles[account], now.date())
    if chain["error"]:
        sys.exit(f"❌ {account}: {chain['error']}")
    dates = [r["date"] for r in chain["ledger"] if r["date"] in chain["excl"]]
    prev_of = dict(zip(dates[1:], dates))
    for cur, why in sorted(chain["unexplained"].items()):
        parts = why.split("; ")
        if not all(p.startswith(TRAP) for p in parts):
            print(f"  {account} {cur}: có bẫy khác ⇒ KHÔNG khai hộ — {why[:160]}")
            continue
        held = sorted(t for t in set(chain["excl"][prev_of[cur]]["detail"]) | set(chain["excl"][cur]["detail"]))
        proof, ok = [], True
        for s in m.sessions_between(prev_of[cur], cur):
            p = m.prev_session(s)
            for t in held:
                a, b = ratio.get((t, p.isoformat())), ratio.get((t, s.isoformat()))
                if a is None or b is None or abs(b / a - 1) > TOL:
                    ok = False
                    proof.append(f"{t} {p}→{s}: Close/Price {a} → {b} — KHÔNG chứng minh được")
                else:
                    proof.append(f"{t} {p}→{s}: Close/Price {a:.6f} → {b:.6f}")
        if not ok:
            print(f"  {account} {cur}: không đủ bằng chứng ⇒ KHÔNG khai — {'; '.join(proof)}")
            continue
        flows.setdefault(account, []).append({
            "date": cur.isoformat(), "amount_vnd": 0, "kind": "market_only",
            "evidence": ("KIỂM BẰNG MÁY (gen_sleeve_declarations.py, job Taylor_20261012_120049): "
                         f"không đọc được lịch corp-action ({'; '.join(p[len(TRAP):].split(': ', 1)[-1] for p in parts)}); "
                         f"thay bằng tỉ số giá điều chỉnh/chưa điều chỉnh của BQ ticker "
                         f"({os.path.basename(args.price_csv)}) không đổi quá {TOL:.1%} ⇒ không có sự kiện quyền "
                         f"làm giá tham chiếu đổi từ {TOL:.1%} trở lên: "
                         + "; ".join(proof))})
        added += 1
    flows[account] = sorted(flows.get(account, []), key=lambda r: (r["date"], r.get("time_ict") or ""))
print(f"{added} bản khai market_only sinh ra" + ("" if args.write else " (chưa ghi — thêm --write)"))
if args.write:
    m._write_json_atomic(ctx.sleeve_flows_path, flows)
