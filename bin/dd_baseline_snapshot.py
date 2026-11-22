#!/usr/bin/env python3
"""dd_baseline_snapshot.py — chụp SỐ NỀN quy trình DD (A0, 22/11/2026). Chỉ đọc; cùng đầu vào ⇒ cùng số.

Dùng: python3 bin/dd_baseline_snapshot.py [--root ROOT] [--out kb/projects/dd-baseline-20261122.json]
Nguồn: kb/dd_price_zones.json (sổ giá) + bus/jobs/*.json (chi phí).
Phân loại skeptic_status là LUẬT CỐ ĐỊNH theo thứ tự (xấp xỉ, đọc văn bản tự do):
  NONE      : chứa 'CHƯA qua skeptic' / 'CHƯA chạy fundamental-skeptic'
  REFUTED   : chứa REFUTED hoặc INCONCLUSIVE (kể cả đã áp)
  CONFIRMED : chứa CONFIRMED (và không REFUTED/INCONCLUSIVE)
  OTHER     : còn lại (không có chữ verdict)
Vòng 1 của một mã = entry rev nhỏ nhất của mã đó; 'qua vòng 1' = vòng 1 phân loại CONFIRMED.
"""
import argparse, collections, glob, json, os, re, statistics

def classify(s):
    s = s or ""
    if re.search(r"CHƯA (qua skeptic|chạy fundamental-skeptic)", s): return "NONE"
    if re.search(r"REFUTED|INCONCLUSIVE", s): return "REFUTED"
    if "CONFIRMED" in s: return "CONFIRMED"
    return "OTHER"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--out")
    ap.add_argument("--since", default="2026-11-09", help="cohort DD mới cho tỷ lệ qua vòng 1")
    a = ap.parse_args()
    d = json.load(open(os.path.join(a.root, "kb/dd_price_zones.json"), encoding="utf-8"))
    E = d["entries"]
    by = collections.defaultdict(list)
    for e in E: by[e["ticker"]].append(e)
    revs = {t: len(v) for t, v in by.items()}
    last = {t: max(v, key=lambda e: (e.get("rev", 1), e.get("recorded_at", ""))) for t, v in by.items()}
    first = {t: min(v, key=lambda e: (e.get("rev", 1), e.get("recorded_at", ""))) for t, v in by.items()}
    dist_last = collections.Counter(classify(e.get("skeptic_status")) for e in last.values())
    dist_all = collections.Counter(classify(e.get("skeptic_status")) for e in E)
    def r1(since):
        ts = [t for t in first if (first[t].get("dd_date") or "") >= since]
        ok = [t for t in ts if classify(first[t].get("skeptic_status")) == "CONFIRMED"]
        return {"n_tickers": len(ts), "pass": len(ok), "rate": round(len(ok)/len(ts), 4) if ts else None, "passed": sorted(ok)}
    # chi phí job DD (lọc theo từ khoá prompt_summary — xấp xỉ, không gồm agent gọi trực tiếp)
    costs = []
    for f in glob.glob(os.path.join(a.root, "bus/jobs/*.json")):
        try: j = json.load(open(f))
        except Exception: continue
        if j.get("to") != "Taylor": continue
        if not re.search(r"\bDD\b|due.diligence", j.get("prompt_summary", ""), re.I): continue
        try: costs.append(float(j.get("total_cost_usd") or 0))
        except ValueError: pass
    out = {
        "generated_for": "A0 nâng cấp DD 22/11/2026 (decided_by user 19:07)",
        "so_entries": len(E), "so_ma": len(by),
        "rev_moi_ma": {"tong": sum(revs.values()), "trung_binh": round(sum(revs.values())/len(revs), 3),
                        "phan_bo": dict(sorted(collections.Counter(revs.values()).items())),
                        "top": sorted(revs.items(), key=lambda x: -x[1])[:5]},
        "skeptic_status_rev_cuoi_moi_ma": dict(dist_last),
        "skeptic_status_moi_entry": dict(dist_all),
        "ti_le_qua_vong1_toan_so": r1("0000-00-00"),
        "ti_le_qua_vong1_cohort_tu_" + a.since: r1(a.since),
        "chi_phi_job_DD_usd": {"n_job": len(costs), "tong": round(sum(costs), 1),
                                "trung_vi": round(statistics.median(costs), 2) if costs else None,
                                "ghi_chu": "lọc từ khoá prompt_summary; chưa gồm agent gọi trực tiếp (Opus/skeptic inline)"},
        "so_lan_gui_lai_email": {"gia_tri": 1, "nguon": "thủ công: ca QTP 17/11 gửi lần 2 (kb/projects/qtp-dd-20261117.md; review F13). Không có ledger máy đọc cho email DD — số này phải cập nhật tay.", "dang": "manual"},
        "lenh_tai_lap": "python3 bin/dd_baseline_snapshot.py --out kb/projects/dd-baseline-20261122.json",
    }
    s = json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(s + "\n")
    print(s)

if __name__ == "__main__":
    main()
