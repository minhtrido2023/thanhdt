# Rà lại DD theo skill mới — Đợt 1 (user duyệt 24/11/2026 16:42 ICT)

Nguồn lệnh: user "Đồng ý kế hoạch 3 đợt, duyệt đợt 1 trước". Luật hiện hành: `~/.claude/skills/due-diligence/SKILL.md` (đọc kỹ V1–V8, D3/D4/D5, E15, E16) + `SKILL_ext.md` khi cần.
Worktree làm việc (ghi MỌI output ở đây, KHÔNG ghi vào master): `/home/trido/thanhdt/WorkingClaude/wt-1574720404268912680` (nhánh `session/1574720404268912680`). Thư mục output: `agents/Taylor/research/dd_recheck_20261124/<MÃ>/`.

## Đợt 1 = 8 mã; chạy PILOT 1 mã trước (luật "fan-out ≥5 ⇒ pilot 1 mã + skeptic")
Pilot = **HHS** (cần phản biện lại đầy đủ; tâm dịch −22,7% giữa r6→r7; giá đang dưới đáy vùng). Xong pilot + Mike duyệt quy trình mới fan-out 7 mã còn lại: VGS, TCH (xác nhận cơ học), FPT, NNC, DGC, DRI, SIP (CONFIRMED cũ, soát lại theo luật mới).

## Việc cho MỖI mã (không làm lại từ đầu — tái dùng báo cáo + file khoá giả định hiện có, chỉ cập nhật phần luật mới đụng tới)
1. **Đọc**: báo cáo cuối của mã (đường dẫn = `source_file` entry cuối trong `kb/dd_price_zones.json`), file khoá `assumptions_file`, mọi `skeptic/rN.json` có sẵn. Ghi lại tâm/vùng/nhãn hiện tại.
2. **D4**: terminal RONIC = Ke ở base? Nếu báo cáo đặt RONIC > Ke trong base mà không có lý do WIDE ⇒ ghi lệch + tính lại tâm (qua script calc có sẵn; không có script ⇒ nói thẳng "chưa tính lại được", đừng ước).
3. **D3**: capex TUÂN THỦ (chi bắt buộc theo quy định, không tạo doanh thu) có là dòng tiền ra trong base không? Thiếu ⇒ ghi lệch + ước tác động bằng độ nhạy (nguồn cụ thể hoặc "cần kiểm chứng").
4. **V1/D4 r**: r=13,5% neo 03/11 + β×Δ lãi huy động; có báo dải Ke 12,3–13,4% không.
5. **E15**: chạy lại mô hình với r = 12,3% (giữ nguyên tham số khác) ⇒ dòng "Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): X đ/cp (+Y% so với tâm base)". KHÔNG đổi tâm base.
6. **E16**: `source /home/trido/thanhdt/WorkingClaude/wc_env.sh; /home/trido/thanhdt/wc_venv/bin/python /home/trido/thanhdt/WorkingClaude/mike/bin/dd_history_label.py --ticker <MÃ> --out-dir /tmp/dd_hist_<MÃ>` ⇒ in nguyên văn dòng nhãn (thường "KHÔNG CHẮC"), không làm tròn, không "×tâm", không dùng làm cổng.
7. **V3** (giá trị trước/sau chiết khấu thanh khoản theo ADV), **V6** (V_ngắn/V_dài/D, chỉ hiển thị), **V5** (moat_tier có bằng chứng), **V8** (sizing đề xuất trong 2–4% NAV; >4% ⇒ nêu rõ chờ user duyệt riêng; FPT/NNC/VGS có ngoại lệ 5% đã duyệt riêng) — mục nào thiếu ⇒ bổ sung; đủ rồi ⇒ ghi "đã đủ" (một dòng).
8. **Phạm vi skeptic** (§E4): moat/cân bằng/thiếu hạng mục. Chuẩn bị bản báo cáo MỚI (đặt tên `REPORT_recheck_<MÃ>.md`, KHÔNG sửa đè báo cáo cũ) gồm: mục tóm tắt thay đổi so với bản cũ + dòng E15/E16 ngay dưới dòng TÂM + các bổ sung ở trên. Tâm đổi >5% hoặc đổi lớp nhãn ⇒ nói rõ (cần phản biện lại đầy đủ).
9. **Phản biện**: `python3 bin/dd_skeptic_run.py --dir agents/Taylor/research/dd_recheck_20261124/<MÃ> --report <REPORT_recheck>.md` (mặc định chế độ DD_GENERAL; trần 3 USD/ca; chạy trong worktree; brief tự qua blind lint). KHÔNG tự ghi verdict. Trần chi phí tổng pilot ~4 USD.

## Bài học pilot HHS (24/11 16:5x) — ÁP CHO FAN-OUT
- **Bước 0 (trước bước 1, rẻ hơn một vòng skeptic): kiểm "tham số nền đã bị phép đo/luật mới hơn phủ lên chưa".** Đọc báo cáo xem tâm có phụ thuộc: chiết khấu holding/CK (v5 24/11: `kb/projects/ck-hhs-reference-range-20261124.md`, chỉ liên quan mã có tầng holding), lãi huy động/r (neo 03/11), RONIC terminal, độ nhạy r. Ghi "có/không + tham số". Nếu CÓ và báo cáo cũ dùng bản đã bị phủ ⇒ KHÔNG chạy skeptic, ghi vào SUMMARY và dừng mã đó cho Mike.
- Độ nhạy r phải TÍNH từ mô hình (pv(y,Ke)), không viết "≈0" (lỗi thật của HHS rev7).
- Selfcheck ledger trong worktree: `MIKE_SRC_ROOT=<worktree> python3 bin/dd_price_zones_selfcheck.py --ledger <bản tạm>`.
- Báo cáo recheck chỉ thêm E15/E16 + sửa lệch luật mới; tâm không đổi thì nói "0%" rõ ràng. Mỗi mã SUMMARY ≤1 trang.
- Commit CHỈ thư mục của mình (`git add agents/Taylor/research/dd_recheck_20261124/<MÃ>`); nếu commit gate báo job khác LIVE, đợi 30s thử lại.

## Cấm
- KHÔNG ghi `kb/dd_price_zones.json` (chỉ ghi `LEDGER_PROPOSAL_<MÃ>.json` theo §E14, thử bằng `dd_price_zones_selfcheck.py --ledger <bản tạm>`); Mike duyệt rồi mới ghi sổ (CONFIRMED chỉ qua `dd_ledger_append_confirmed.py`).
- KHÔNG email, KHÔNG đặt lệnh, KHÔNG wire. Pháp lý chỉ WARNING (user 27/09).
- Pha mù giá: không đưa giá thị trường vào bước 1–5; giá chỉ để cập nhật `price_ref`/nhãn SAU khi khoá (nếu cần, dùng DNSE, không BQ).
- Không sửa giả định đã khoá vì thấy giá. Muốn sửa ⇒ nêu lý do + rev mới.

## Bàn giao
`agents/Taylor/research/dd_recheck_20261124/<MÃ>/SUMMARY.md`: (a) lệch D3/D4/E15/E16/V-nào, (b) tâm/vùng cũ→mới (Δ%), nhãn, (c) verdict skeptic (đường dẫn rN.json), (d) rủi ro/việc mở, (e) khuyến nghị lớp: giữ/MECH/FULL. Commit trong worktree (không merge master — Mike merge). Ghi bus finding khi xong.
