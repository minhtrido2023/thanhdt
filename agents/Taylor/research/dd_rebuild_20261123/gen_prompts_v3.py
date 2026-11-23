#!/usr/bin/env python3
"""Sinh prompt VÒNG 3 (23/11/2026) cho DCM DBC SZL VCP HHS. Chạy: cd mike && python3 agents/Taylor/research/dd_rebuild_20261123/gen_prompts_v3.py
Khuôn = gen_prompts.py (lô 1-4) + 9 điểm LEDGER_PROPOSAL (skill due-diligence §E14)."""
import glob, os, sys
ROOT = "/home/trido/thanhdt/WorkingClaude/mike"
sys.path.insert(0, ROOT + "/bin")
import dd_reconfirm_batch as B
OUT = os.path.dirname(os.path.abspath(__file__)) + "/prompts_v3/"
R = "agents/Taylor/research/"
DIRS = {"DCM": R+"dd_DCM_20261104", "DBC": R+"dd_DBC_20261118", "SZL": R+"dd_redo_20261105/SZL",
        "VCP": R+"dd_VCP_20261112", "HHS": R+"dd_dilution_update_20261110/HHS"}
MISSING = {
 "DCM": "quỹ KH&CN trích 100% vs số dư 11% (tâm −1…−2,5k); ND 320/2025 + TT 20/2026 từ nguồn gốc; hạn thuế đất/giấy phép Cà Mau vs chân trời vĩnh viễn; đối chiếu chi từ quỹ với capex LCTT mã 21; tra tin pháp lý sau 05/11",
 "DBC": "BĐS dở dang ~1.186 tỷ chưa tách khỏi vốn hoạt động (+5,4…+28,9%, tâm có thể quá THẤP); ưu đãi thuế TNDN chưa kiểm (~−13%); trích lập TSSH (−1,5…−3%); chi tuân thủ môi trường không kiểm chứng",
 "SZL": "KTPL 2026 = 20% (BCTC Q3 tr.26) chưa áp (−1.688); NQ76 5,846 không qua P&L (trừ −708 sai); cơ sở 19,85 tr cp thưởng chưa đăng ký; CP trả trước thuê đất Châu Đức/Tân Đức 217 tỷ; ý kiến KT FY2025; tổng mức Long Phước 920",
 "VCP": "k=1,0 vs 1,127 (−9,9%); hạn PPA Cửa Đạt (−7,5…−14,2%); bảo lãnh vay Đắk Lô 1–3; NQ ĐHĐCĐ 2026; tiền cấp quyền tài nguyên nước; bản chất pool 1.000 tỷ",
 "HHS": "biên cao tầng HH1–HH4 trong NC-II chưa tách (skeptic: −10…−18%); quỹ KTPL chưa tìm lại; nội dung lấy ý kiến cổ đông 14–25/12 (NQ 10/NQ-HĐQT 20/11). GIỮ BẢN SONG SONG CK holding 0% (headline, theo V4) và 27% (vùng 8.624–13.207) — user CHƯA chốt quy ước, KHÔNG tự chọn/gộp; forensic_flags EXCLUDE ⇒ loại khỏi candidate plan",
}
for t, d in DIRS.items():
    e = B.last_entry(t)
    sk = sorted(glob.glob(f"{ROOT}/{d}/skeptic/r[0-9]*.json"))
    n = int(os.path.basename(sk[-1])[1:-5])
    cur = e.get("source_file") or "(xem entry cuối sổ)"
    txt = f"""Dựng REV MỚI (VÒNG 3) cho DD {t} theo skill due-diligence (~/.claude/skills/due-diligence/SKILL.md + SKILL_ext.md; ĐỌC KỸ §E14 'Đặc tả LEDGER_PROPOSAL' — 9 lỗi định dạng đã chặn các lô trước; sizing chuẩn V8 = 2–4% NAV/mã). KHÔNG đặt lệnh, KHÔNG gửi email, KHÔNG ghi kb/dd_price_zones.json.

BỐI CẢNH: rev hiện hành vừa dựng 23/11, skeptic DD_GENERAL vòng cuối (r{n}) KHÔNG CONFIRMED. User DUYỆT chạy vòng 3 (23/11 17:03 ICT) — đây là cơ hội CUỐI.
- Thư mục DD: {d}; entry cuối sổ: dd_date={e['dd_date']} rev={e.get('rev')}, tâm={e.get('center')}, vùng {e.get('zone_low')}–{e.get('zone_high')}, price_ref={e.get('price_ref')}, skeptic_final={e.get('skeptic_final')}, source_file={cur}
- Verdict skeptic vòng cuối (ĐỌC KỸ missing_items + data_provenance): {d}/skeptic/r{n}_raw.md  và  {d}/skeptic/r{n}.json ; LEDGER_PROPOSAL cũ: {d}/LEDGER_PROPOSAL_{t}.json
- Hạng mục còn thiếu (tóm tắt của Mike, nguồn gốc = r{n}_raw.md): {MISSING[t]}

VIỆC:
1. Đọc báo cáo hiện hành + verdict r{n}. Lập danh sách từng hạng mục skeptic nêu.
2. Chỉ XỬ LÝ hạng mục SỬA ĐƯỢC từ nguồn độc lập (BCTC gốc trong src/ hoặc tải lại từ website công ty/HOSE-HNX; BQ ticker_financial; CBTT). (a) có cơ sở độc lập nêu nguồn ⇒ định lượng + vào base; (b) không có cơ sở ⇒ kịch bản có xác suất/độ nhạy, KHÔNG nhồi vào base; (c) không kiểm chứng được ⇒ ghi thẳng 'không kiểm chứng được' + ảnh hưởng ước lượng. TUÂN THỦ luật user: điều chỉnh GIẢM cần cơ sở độc lập, đầu tư mới/dự án tăng trưởng base NPV=0, capex tuân thủ là dòng tiền ra (V4), vụ án chỉ WARNING không vào base, định giá MÙ GIÁ thị trường (không truy vấn giá trước khi KHOÁ giả định; tệp đầu vào bị mất thì dựng lại từ nguồn + ghi md5).
3. Viết REV MỚI trong CÙNG thư mục DD (REPORT_rev<N+1>.md, KHÔNG ghi đè bản cũ), khoá giả định (assumptions + md5; chạy bin/dd_assumptions_lint.py nếu có), mục 'Đính chính so với rev trước' liệt kê từng hạng mục skeptic → xử lý thế nào; V1 (r gắn lãi huy động), V3 (thanh khoản), V5 (5F nếu >12 tháng), V6 nếu áp.
4. Chạy phản biện ĐÚNG 1 VÒNG (tệp tiếp theo skeptic/r{n+1}.json — vòng 3): `cd {ROOT} && python3 bin/dd_skeptic_run.py --dir {d} --report <đường dẫn REPORT rev mới>` (DD_GENERAL; trần 3 USD). KHÔNG sửa báo cáo sau khi skeptic đã chạy; KHÔNG chạy vòng nào nữa. Nếu vẫn không CONFIRMED ⇒ DỪNG, nêu hạng mục còn thiếu, báo user.
5. SỔ GIÁ (5 ca song song ⇒ KHÔNG ghi kb/dd_price_zones.json, KHÔNG chạy dd_ledger_append_confirmed.py --write): ghi `LEDGER_PROPOSAL_{t}.json` = {{"entry": {{…}}}} theo ĐÚNG §E14 SKILL_ext.md (9 điểm): (1) giữ nguyên dd_date entry cuối sổ, rev=rev cuối+1, supersedes='{t}@{e['dd_date']}#{e.get('rev')}', expires_on+expires_basis lấy của entry cuối; (2) evidence.quote = chuỗi NGUYÊN VĂN có trong source_file (lấy bằng grep -n), mọi số trong fields phải nằm trong chính quote đó; (3) fields chỉ trường SỐ (zone_low, center, zone_high, price_ref, center_alt, center_range); (4) center_alt ⇒ center_alt_kind ∈ {{expected_weighted, base_scenario, blend, median, zone_midpoint, point}} + evidence phủ center_alt; (5) center_range=[center,hi] bắt đầu ĐÚNG center, nếu không thì null + ghi vào notes; (6) price_ref có evidence phủ; (7) zone nguyên số của nguồn, không làm tròn; (8) nhãn skeptic_final: vòng cuối không CONFIRMED & bản sửa chưa áp ⇒ REFUTED_OPEN (KHÔNG FIXED_UNVERIFIED; FIXED_UNVERIFIED chỉ khi bản sửa đã áp mà chưa vòng nào chạy lại; KHÔNG tự nâng CONFIRMED), kèm skeptic_verdict_path thật (r{n+1}.json), skeptic_final_basis='skeptic_run', audited_fy_missing; (9) không ghi sổ. Trước khi báo xong: chép kb/dd_price_zones.json ra /tmp, chèn entry, chạy `python3 bin/dd_price_zones_selfcheck.py --ledger <bản tạm>` ⇒ phải 0 lỗi (ghi output vào finding).
6. Bus finding: bin/append_event.sh Taylor finding "dd-rebuild-v3-{t}-20261123" '<json: verdict mới, tâm cũ→mới, vùng, đổi nhãn?, hạng mục còn thiếu, đường dẫn rev, md5 report, selfcheck rc, cost>' ngay khi xong, và post tóm tắt 5–8 dòng vào topic hiện tại bằng bin/notify_thread.sh (topic 1574365262965121136). KHÔNG commit vào repo chính — để file trong thư mục DD.

Ràng buộc: threads=1 cho tính toán nặng; chỉ chạm thư mục DD của {t}; không đụng ca khác (4 ca khác chạy song song); chi phí skeptic ≤3 USD."""
    open(OUT + f"{t}.txt", "w", encoding="utf-8").write(txt)
    print(t, "r%d" % n, len(txt))
