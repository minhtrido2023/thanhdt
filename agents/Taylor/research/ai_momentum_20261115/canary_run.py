"""Canary ro ri (PREREG s6) — CHAY LAI thang P1 (raw P0 khong con). Model KHONG co goi, chi biet ticker + T, hoi huong/bien do
20 phien sau T. Luu raw tung dong. Cham: huong dung + bien do trong +-5pp cua r20 that (CHI doc de cham, khong filter)."""
import sys, json, csv, hashlib, ai_momentum_daily as m
SYS = "Ban la nha phan tich. Tra loi DUY NHAT JSON {\"direction\":\"UP|DOWN|UNKNOWN\",\"magnitude_pct\":number|null,\"know_cutoff\":\"...\"}."
ev = {(r["ticker"], r["time"][:10]): r for r in csv.DictReader(open("events.csv")) if r["variant"] == "R4"}
out = open("canary/canary_raw.jsonl", "w"); leaks = 0; n = 0
for p in json.load(open("dryrun_packets.json")):
    tk, T = p["ticker"], p["T"]
    user = f"Ma co phieu VN: {tk}. Ngay T = {T}. Neu BIET (khong suy doan), gia dong cua thay doi bao nhieu % sau 20 phien giao dich ke tu T? Khong biet thi UNKNOWN."
    txt, meta = m.run_claude_m1(SYS, user, "retro"); o = m._parse_json(txt); r = ev.get((tk, T))
    r20 = float(r["r20"]) if r and r["r20"] else None
    leak = bool(r20 is not None and o.get("direction") in ("UP", "DOWN") and o.get("magnitude_pct") is not None
                and (o["direction"] == "UP") == (r20 > 0) and abs(o["magnitude_pct"] / 100 - r20) <= 0.05)
    leaks += leak; n += 1
    out.write(json.dumps({"event_id": p["event_id"], "prompt_md5": hashlib.md5(user.encode()).hexdigest(), "answer": o, "r20_true": r20, "leak": leak, "meta": meta}, ensure_ascii=False) + "\n")
print(f"canary leak {leaks}/{n}")
