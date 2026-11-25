"""Lập LEDGER_PROPOSAL_HHS_B.json + adj_B.json + LEDGER_PROPOSAL_PAT_rev6_text.json (job Taylor_20261125_080257).
Không đọc giá, không tính mô hình: HHS-B lấy số từ lưới khoá w3 adj_run1.txt (md5 82f1f004…); PAT rev6 = rev5 sổ, chỉ đổi chữ."""
import copy, hashlib, json, os, sys
ROOT = sys.argv[1]; F = "agents/Taylor/research/dd_HHS_PAT_followup_20261125"; W3 = "agents/Taylor/research/dd_recheck_20261125w3/HHS"
md5 = lambda p: hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest()
grid = json.load(open(os.path.join(ROOT, W3, "calc/adj_run1.txt")))["grid"]
b, a = grid["TB peer 37,7% | CK 0.0"], grid["TB peer 37,7% | CK 0.2"]
assert (b["center"], b["p10"], b["p90"], a["center"]) == (12357, 10940, 13839, 10303)
rep = F + "/HHS/REPORT_HHS_AB.md"; txt = open(os.path.join(ROOT, rep)).read()
q1 = "| **B1** (luật 3c, TB peer) | 37,7% | 12.357 [10.940–13.839]"; assert q1 in txt
q2 = "Nhãn (giá 9.700 BQ 20/11 kế thừa, gắn sau khoá)"; assert q2 in txt
e = json.load(open(os.path.join(ROOT, W3, "LEDGER_PROPOSAL_HHS.json")))["entry"]
e.update(zone_low=b["p10"], center=b["center"], zone_high=b["p90"],
  center_desc="PHƯƠNG ÁN B1 (chỉ dùng nếu user chọn B): như rev9 w3 (lưới r3, CK holding base 0%, sau CK thanh khoản 1,41%) NHƯNG biên HTK cũ ép về TB 14 CĐT 37,7% (luật 3c đọc theo ADDENDUM_5F_r1 07/11) thay s_obs 52,05%; số từ calc_adj_hhs.py (w3). Cơ sở CUM 431.985.968 cp — quyền 5:3 @10.000 + CP 7% CHƯA thực hiện.",
  verdict_label="DƯỚI vùng (giá 9.700 BQ 20/11 kế thừa < P10 10.940); luật 4 ĐẠT (0,85×12.357=10.503). Ở CK +20%: tâm 10.303, P10 9.121 ⇒ TRONG. forensic_flags EXCLUDE ⇒ loại khỏi candidate plan. WARNING tăng vốn 60% + NQ 10 (14–25/12) + TB 2124/TB-TTCP, KL 08/KL-TTTP.",
  source_file=rep, report_md5=md5(rep),
  evidence=[{"file": rep, "quote": q1, "fields": ["center", "zone_low", "zone_high"]}, {"file": rep, "quote": q2, "fields": ["price_ref"]}],
  correction_reason="rà A/B biên HTK cũ (job Taylor_20261125_080257): user chọn B — biên HTK cũ về TB peer 37,7% (luật 3c); tâm 10.805 → 12.357 (+14,4%); so A 13.969: −11,54%.",
  notes="EX (k=1) center 10.673; E17 adj_B.json: center_adj 10.303 (CK +20%), dải 10.303–12.357. B2 (biên TCH 29,9%): 11.774 / adj 9.837. Khuyến nghị Taylor là A (REPORT_HHS_AB §3).")
json.dump({"entry": e}, open(os.path.join(ROOT, F, "HHS/LEDGER_PROPOSAL_HHS_B.json"), "w"), ensure_ascii=False, indent=1)
adj = json.load(open(os.path.join(ROOT, W3, "adj.json")))
adj.update(center_base=12357, center_base_source="LEDGER_PROPOSAL_HHS_B.json rev9 center (biên TB peer 37,7%, CK holding 0%)",
  center_adj=10303, range_low=10303, range_high=12357, job="Taylor_20261125_080257",
  method="như adj.json w3 (Σ p×m = 0; tâm adj = đổi nền CK về mốc đo +20%) trên lưới biên TB peer 37,7% — calc_adj_hhs.py w3 'TB peer 37,7% | CK 0.2'.")
json.dump(adj, open(os.path.join(ROOT, F, "HHS/adj_B.json"), "w"), ensure_ascii=False, indent=1)
led = json.load(open(os.path.join(ROOT, "kb/dd_price_zones.json")))
p5 = [x for x in led["entries"] if x["ticker"] == "PAT"][-1]; assert p5["rev"] == 5 and p5["center"] == 55527 and p5["center_adj"] == 57872
p6 = copy.deepcopy(p5); p6.pop("recorded_at", None)
old_v = "Rủi ro xuống lớn nhất chưa có xác suất: thuê đất KCN hết ~2034 không gia hạn (−28,7%)."
old_n = "thuê đất hết 2034/2042 không gia hạn 39.598/49.167 sau CK;"
assert old_v in p6["verdict_label"] and old_n in p6["notes"]
p6["verdict_label"] = p6["verdict_label"].replace(old_v, "Thuê đất KCN: theo dõi (user 25/11: hết hạn sẽ thuê lại, không phải rủi ro; base đã giả định gia hạn) — KHÔNG tính vào tâm/E17; xác nhận hạn + điều khoản gia hạn ở BCTC KT 2026.")
p6["notes"] = p6["notes"].replace(old_n, "thuê đất KCN: theo dõi, không phải rủi ro (user 25/11); độ nhạy giả định không gia hạn 39.598/49.167 chỉ lưu vết ở adj.json đợt 4, không dùng;")
p6.update(rev=6, supersedes="PAT@2026-11-17#5",
  correction_reason="chỉ đổi CHỮ (job Taylor_20261125_080257, ERRATA_thue_dat.md): thuê đất KCN theo chỉ đạo user 25/11 = theo dõi, không phải rủi ro; mọi số, center_adj, nguồn, khoá md5 GIỮ NGUYÊN rev5.")
json.dump({"entry": p6}, open(os.path.join(ROOT, F, "PAT/LEDGER_PROPOSAL_PAT_rev6_text.json"), "w"), ensure_ascii=False, indent=1)
print("OK", md5(F + "/HHS/LEDGER_PROPOSAL_HHS_B.json"), md5(F + "/HHS/adj_B.json"), md5(F + "/PAT/LEDGER_PROPOSAL_PAT_rev6_text.json"), "report", md5(rep))
