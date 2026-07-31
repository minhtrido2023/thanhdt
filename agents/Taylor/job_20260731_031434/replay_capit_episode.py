# -*- coding: utf-8 -*-
"""Replay 2026-07-13 → 07-30 qua capit_episode.update() — self-check Bước 2 (job Taylor_20260731_031434).

Hai câu hỏi phải trả lời:
  A. PARITY: capit_episode có làm đổi basket/size/n_capit_basket của bất kỳ ngày nào không?
     (input lịch sử lấy từ artifact đã ghi: deploy_golive_dt5g_v4/out/*.csv, book=CAPIT)
  B. Sổ episode có tái hiện đúng sự thật đã biết không? (mở 07-20, rổ gốc 5 mã gồm NCT,
     size 0.75, còn MỞ tới 07-30 vì vị thế thật chưa thoát — báo cáo §1/§2)

Ledger ghi vào sandbox trong thư mục job, KHÔNG đụng data/capit_episode.json.
"""
import os, sys, csv, glob, json
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
import capit_episode

HERE = os.path.dirname(os.path.abspath(__file__))
SANDBOX = os.path.join(HERE, "replay_capit_episode.json")
if os.path.exists(SANDBOX):
    os.remove(SANDBOX)

# ── input lịch sử: rổ/size mỗi ngày, đọc từ artifact CSV đã ghi ──
days = []
for p in sorted(glob.glob(os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "out",
                                       "golive_v23_recommendations_*.csv"))):
    d = os.path.basename(p)[len("golive_v23_recommendations_"):-len(".csv")]
    if d < "2026-07-13":
        continue
    basket, w = [], 0.0
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("book") == "CAPIT":
                basket.append(r["ticker"])
                w = float(r["weight_pct"])
    days.append({"date": d, "basket": sorted(basket),
                 "size": round(w * len(basket) / 100.0, 4), "fired": bool(basket)})

SESSIONS = [d["date"] for d in days]
before = [{k: v for k, v in d.items()} for d in days]   # bản sao "quyết định" TRƯỚC khi gọi module

print("=== A. PARITY: decision fields trước/sau khi chạy capit_episode ===")
rows, diffs = [], 0
for d in days:
    out = capit_episode.update(d["date"], d["fired"], d["basket"], d["size"], SESSIONS,
                               workdir=WORKDIR, ledger_path=SANDBOX)
    rows.append((d, out))
for b, (a, _) in zip(before, rows):
    if b != a:
        diffs += 1
        print(f"  DIFF {b['date']}: {b} -> {a}")
print(f"  {len(days)} ngày replay | decision-field diffs = {diffs}  "
      f"{'PASS (0 diff)' if diffs == 0 else 'FAIL'}")

print("\n=== B. Sổ episode tái hiện ===")
for d, out in rows:
    print(f"  {d['date']} fired={str(d['fired']):5} n_basket={len(d['basket'])} size={d['size']:.2f} "
          f"| episode_open={out['capit_episode_open']} id={out['capit_episode_id']} "
          f"held={out['capit_sessions_held']}")

led = json.load(open(SANDBOX, encoding="utf-8"))
print("\n=== Ledger cuối kỳ ===")
print(json.dumps(led, ensure_ascii=False, indent=2))

# ── assertion cứng ──
eps = led["episodes"]
fails = []
if diffs != 0:
    fails.append("decision fields bị đổi")
if len(eps) != 1:
    fails.append(f"kỳ vọng đúng 1 episode, có {len(eps)}")
else:
    ep = eps[0]
    if ep["entry_signal_date"] != "2026-07-20":
        fails.append(f"entry_date={ep['entry_signal_date']} != 2026-07-20")
    if ep["basket"] != ["NCT", "PVT", "SAB", "SIP", "VNM"]:
        fails.append(f"basket gốc sai: {ep['basket']}")
    if abs(ep["size"] - 0.75) > 1e-6:
        fails.append(f"size={ep['size']} != 0.75")
    if ep["status"] != "open":
        fails.append(f"status={ep['status']} — không được auto-close khi vị thế thật còn")
    # vị thế thật 07-31 (báo cáo §1): SpaceX & ZaloPay còn đủ 5 mã
    rem = ep.get("remaining_qty_broker") or {}
    for lb, exp in {"SpaceX": {"NCT": 500, "PVT": 3500, "SAB": 1100, "SIP": 1700, "VNM": 900},
                    "ZaloPay": {"NCT": 373, "PVT": 2071, "SAB": 744, "SIP": 749, "VNM": 601}}.items():
        got = rem.get(lb)
        if got != exp:
            fails.append(f"remaining {lb}: {got} != {exp} (báo cáo §1)")

print("\n=== KẾT LUẬN ===")
print("SELF-CHECK PASS" if not fails else "SELF-CHECK FAIL: " + "; ".join(fails))
sys.exit(0 if not fails else 1)
