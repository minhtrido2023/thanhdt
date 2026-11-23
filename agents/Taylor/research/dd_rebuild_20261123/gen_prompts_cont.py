#!/usr/bin/env python3
"""Sinh prompt TIẾP THEO (23/11/2026 19:00, user duyệt) cho 9 ca còn mở. Chạy: cd mike && python3 agents/Taylor/research/dd_rebuild_20261123/gen_prompts_cont.py
Khuôn = gen_prompts.py (lô 1-4) + 9 điểm LEDGER_PROPOSAL (skill due-diligence §E14)."""
import glob, os, sys
ROOT = "/home/trido/thanhdt/WorkingClaude/mike"
sys.path.insert(0, ROOT + "/bin")
import dd_reconfirm_batch as B
OUT = os.path.dirname(os.path.abspath(__file__)) + "/prompts_cont/"
R = "agents/Taylor/research/"
DIRS = {"BSR": R+"dd_lagcand_20261109/BSR", "CST": R+"dd_CST_20261111", "CSV": R+"dd_lagcand_20261109/CSV",
        "LLM": R+"dd_LLM_20261118", "PNJ": R+"dd_PNJ_20261114", "SCL": R+"dd_dilution_update_20261110/SCL",
        "TTA": R+"dd_TTA_20261120", "VCB": R+"dd_VCB_20261117", "VLB": R+"dd_VLB_20261122"}
import re as _re
def _killer(d,n):
    raw=open(f"{ROOT}/{d}/skeptic/r{n}_raw.md",encoding="utf-8").read()
    m=_re.search(r'"killer_objection"\s*:\s*"(.*?)"\s*,',raw,_re.S)
    return (m.group(1) if m else "(xem r%d_raw.md)"%n)[:700]
for t, d in DIRS.items():
    e = B.last_entry(t)
    sk = sorted(glob.glob(f"{ROOT}/{d}/skeptic/r[0-9]*.json"))
    n = int(os.path.basename(sk[-1])[1:-5])
    cur = e.get("source_file") or "(xem entry cuối sổ)"
    txt = f"""Dựng REV MỚI (vòng skeptic kế tiếp) cho DD {t} theo skill due-diligence (~/.claude/skills/due-diligence/SKILL.md + SKILL_ext.md; ĐỌC KỸ §E14 'Đặc tả LEDGER_PROPOSAL' — 9 lỗi định dạng đã chặn các lô trước; sizing chuẩn V8 = 2–4% NAV/mã). KHÔNG đặt lệnh, KHÔNG gửi email, KHÔNG ghi kb/dd_price_zones.json.

BỐI CẢNH: rev hiện hành vừa dựng 23/11, skeptic DD_GENERAL vòng cuối (r{n}) KHÔNG CONFIRMED. User DUYỆT xử lý tiếp (23/11 19:00 ICT: 'ca nào đủ thông tin thì tiếp tục xử lý') — đây là vòng CUỐI của ca này.
- Thư mục DD: {d}; entry cuối sổ: dd_date={e['dd_date']} rev={e.get('rev')}, tâm={e.get('center')}, vùng {e.get('zone_low')}–{e.get('zone_high')}, price_ref={e.get('price_ref')}, skeptic_final={e.get('skeptic_final')}, source_file={cur}
- Verdict skeptic vòng cuối (ĐỌC KỸ missing_items + data_provenance): {d}/skeptic/r{n}_raw.md  và  {d}/skeptic/r{n}.json ; LEDGER_PROPOSAL cũ: {d}/LEDGER_PROPOSAL_{t}.json
- Phản đối chính (killer_objection, trích r{n}_raw.md — còn missing_items/checks khác, ĐỌC ĐỦ): {_killer(d,n)}

VIỆC:
1. Đọc báo cáo hiện hành + verdict r{n}. Lập danh sách từng hạng mục skeptic nêu.
2. Chỉ XỬ LÝ hạng mục SỬA ĐƯỢC từ nguồn độc lập (BCTC gốc trong src/ hoặc tải lại từ website công ty/HOSE-HNX; BQ ticker_financial; CBTT). (a) có cơ sở độc lập nêu nguồn ⇒ định lượng + vào base; (b) không có cơ sở ⇒ kịch bản có xác suất/độ nhạy, KHÔNG nhồi vào base; (c) không kiểm chứng được ⇒ ghi thẳng 'không kiểm chứng được' + ảnh hưởng ước lượng. TUÂN THỦ luật user: điều chỉnh GIẢM cần cơ sở độc lập, đầu tư mới/dự án tăng trưởng base NPV=0, capex tuân thủ là dòng tiền ra (V4), vụ án chỉ WARNING không vào base, định giá MÙ GIÁ thị trường (không truy vấn giá trước khi KHOÁ giả định; tệp đầu vào bị mất thì dựng lại từ nguồn + ghi md5).
3. Viết REV MỚI trong CÙNG thư mục DD (REPORT_rev<N+1>.md, KHÔNG ghi đè bản cũ), khoá giả định (assumptions + md5; chạy bin/dd_assumptions_lint.py nếu có), mục 'Đính chính so với rev trước' liệt kê từng hạng mục skeptic → xử lý thế nào; V1 (r gắn lãi huy động), V3 (thanh khoản), V5 (5F nếu >12 tháng), V6 nếu áp.
4. Chạy phản biện ĐÚNG 1 VÒNG (tệp tiếp theo skeptic/r{n+1}.json — vòng cuối): `cd {ROOT} && python3 bin/dd_skeptic_run.py --dir {d} --report <đường dẫn REPORT rev mới>` (DD_GENERAL; trần 3 USD). KHÔNG sửa báo cáo sau khi skeptic đã chạy; KHÔNG chạy vòng nào nữa. Nếu vẫn không CONFIRMED ⇒ DỪNG, nêu hạng mục còn thiếu, báo user.
5. SỔ GIÁ (5 ca song song ⇒ KHÔNG ghi kb/dd_price_zones.json, KHÔNG chạy dd_ledger_append_confirmed.py --write): ghi `LEDGER_PROPOSAL_{t}.json` = {{"entry": {{…}}}} theo ĐÚNG §E14 SKILL_ext.md (9 điểm): (1) giữ nguyên dd_date entry cuối sổ, rev=rev cuối+1, supersedes='{t}@{e['dd_date']}#{e.get('rev')}', expires_on+expires_basis lấy của entry cuối; (2) evidence.quote = chuỗi NGUYÊN VĂN có trong source_file (lấy bằng grep -n), mọi số trong fields phải nằm trong chính quote đó; (3) fields chỉ trường SỐ (zone_low, center, zone_high, price_ref, center_alt, center_range); (4) center_alt ⇒ center_alt_kind ∈ {{expected_weighted, base_scenario, blend, median, zone_midpoint, point}} + evidence phủ center_alt; (5) center_range=[center,hi] bắt đầu ĐÚNG center, nếu không thì null + ghi vào notes; (6) price_ref có evidence phủ; (7) zone nguyên số của nguồn, không làm tròn; (8) nhãn skeptic_final: vòng cuối không CONFIRMED & bản sửa chưa áp ⇒ REFUTED_OPEN (KHÔNG FIXED_UNVERIFIED; FIXED_UNVERIFIED chỉ khi bản sửa đã áp mà chưa vòng nào chạy lại; KHÔNG tự nâng CONFIRMED), kèm skeptic_verdict_path thật (r{n+1}.json), skeptic_final_basis='skeptic_run', audited_fy_missing; (9) không ghi sổ. Trước khi báo xong: chép kb/dd_price_zones.json ra /tmp, chèn entry, chạy `python3 bin/dd_price_zones_selfcheck.py --ledger <bản tạm>` ⇒ phải 0 lỗi (ghi output vào finding).
6. Bus finding: bin/append_event.sh Taylor finding "dd-continue-{t}-20261123" '<json: verdict mới, tâm cũ→mới, vùng, đổi nhãn?, hạng mục còn thiếu, đường dẫn rev, md5 report, selfcheck rc, cost>' ngay khi xong, và post tóm tắt 5–8 dòng vào topic hiện tại bằng bin/notify_thread.sh (topic 1574365262965121136). KHÔNG commit vào repo chính — để file trong thư mục DD.

LƯU Ý RIÊNG: chỉ xử lý hạng mục SỬA ĐƯỢC từ dữ liệu/nguồn độc lập; hạng mục thiếu thông tin thật (không có nguồn) thì ghi thẳng "không kiểm chứng được" + ảnh hưởng — ĐỪNG bịa nguồn, ĐỪNG nhồi vào base. Nếu rev mới đổi tâm, nêu rõ chiều và lý do theo từng hạng mục.

Ràng buộc: threads=1 cho tính toán nặng; chỉ chạm thư mục DD của {t}; không đụng ca khác (8 ca khác chạy song song); chi phí skeptic ≤3 USD."""
    open(OUT + f"{t}.txt", "w", encoding="utf-8").write(txt)
    print(t, "r%d" % n, len(txt))
