#!/usr/bin/env python3
"""Dựng hồ sơ DD khủng hoảng cho ca HT1 (kích hoạt 2026-10-30 14:00, bản cũ AWAITING_REPLY, hạn trả lời
2026-11-02 09:15) theo định dạng MỚI — nếu không, code mới bỏ rơi ca này im lặng (state cũ không carry).
Idempotent (create_dossier theo id). Chỉ GHI file mới dưới data/intraday_watch/crisis_dd/ — bản master đang
chạy cron không đọc thư mục này. Chạy: $DNA_PYEXE -I migrate_ht1.py [--state-dir D]"""
import json, os, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/wt-cutloss-crisis-dd-20261101/bin")
import intraday_price_watch as W

sd = sys.argv[sys.argv.index("--state-dir") + 1] if "--state-dir" in sys.argv else W.STATE_DIR
old = json.load(open(os.path.join(sd, "state_2026-10-30.json")))["cases"]["HT1"]
assert old["status"] == "AWAITING_REPLY" and old["verdict"]["label"] == "NOISE"
case = {k: old[k] for k in ("ticker", "t0", "trigger", "t0_quote")}
case["holdings"] = {a: {k: v for k, v in h.items() if k != "no_auto_sell"} for a, h in old["holdings"].items()}
dos = W.create_dossier(sd, case)
if "quick" not in dos["jobs"]:
    dos["jobs"]["quick"] = {"kind": "quick", "day": 1, "job": old["investigation"]["job"],
                            "dispatch_attempted_at": old["investigation"]["dispatch_attempted_at"],
                            "migrated_from": "state_2026-10-30.json (bản cũ: phán quyết NHIỄU, không tự bán)"}
    note = {"kind": "quick", "day": 1, "summary": old["verdict"]["summary"][:1500], "label": None,
            "major_event": False, "at": old["verdict"]["at"]}
    W._atomic_json(os.path.join(dos["dir"], "notes", "quick.json"), note)
    with open(os.path.join(dos["dir"], "DOSSIER.md"), "a", encoding="utf-8") as f:
        f.write(f"\n## Ngày 1 — tóm tắt nhanh (chuyển từ phán quyết bản cũ, {old['verdict']['at']} ICT)\n\n"
                f"{old['verdict']['summary']}\n")
    dos["relayed"].append("quick.json")        # user ĐÃ nhận tin phán quyết này từ bản cũ ⇒ không gửi lại
    W.save_dossier(sd, dos)
print(dos["id"], dos["status"], dos["jobs"]["quick"]["job"], dos["relayed"])
