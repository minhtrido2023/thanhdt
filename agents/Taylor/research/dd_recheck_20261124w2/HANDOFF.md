# Rà lại DD theo skill mới — ĐỢT 2 (user duyệt 24/11/2026 20:11 ICT)

Luật hiện hành: `~/.claude/skills/due-diligence/SKILL.md` (đọc kỹ V1–V9, D3/D4/D5, E15, E16, E17) + `SKILL_ext.md` khi cần.
MẪU = đợt 1 (cùng quy trình, đã chạy 8 mã): `agents/Taylor/research/dd_recheck_20261124/HANDOFF.md` (việc 1–9, bài học HHS, cấm), `dd_recheck_20261124/FPT/` (REPORT_recheck, SUMMARY, LEDGER_PROPOSAL), và `agents/Taylor/research/dd_adjcenter_20261124/PREREG_adj.md` + `PREREG_adj_v2.md` (khoá phương pháp tâm điều chỉnh, md5 kèm theo) + `dd_adjcenter_20261124/FPT/` (ADJ_CENTER.md, adj.json). ĐỌC các file này TRƯỚC.

## Mã đợt 2 (Mike chia 2 job): PVP, MVC (job A) · MBB, DBC (job B). Mỗi job chỉ làm 2 mã của mình.
Đầu vào mỗi mã: entry CUỐI của mã trong `kb/dd_price_zones.json` (source_file = báo cáo cuối; assumptions_file; skeptic_verdict_path). Các mã này đang nhãn CONFIRMED (PVP, MVC, MBB: phản biện kiểu cũ, chưa qua DD_GENERAL) hoặc REFUTED_OPEN (DBC: skeptic r4 REFUTED chiều quá cao — giả định XDCB+BĐS 100% vốn chủ tài trợ).

## Quy trình MỖI mã = đợt 1 (việc 1–9) + E17 trong CÙNG job, theo thứ tự
0. **Bước 0** (SKILL, mục "Chống làm đi làm lại"): tham số nền của báo cáo cũ có bị phép đo/luật mới phủ không (CK holding v5, lãi huy động/r neo 03/11, RONIC terminal, độ nhạy r phải TÍNH từ mô hình). Có và báo cáo dùng bản bị phủ ⇒ DỪNG mã đó, ghi SUMMARY, không chạy skeptic.
1. Đọc, ghi tâm/vùng/nhãn hiện tại; D3/D4/V1/E15/E16/V3/V5/V6/V8 như đợt 1 → `agents/Taylor/research/dd_recheck_20261124w2/<MÃ>/REPORT_recheck_<MÃ>.md`.
2. Phản biện: `python3 bin/dd_skeptic_run.py --dir <dir mã> --report <REPORT_recheck>` (DD_GENERAL, trần 3 USD/ca; trong worktree).
3. Đính chính theo skeptic; tâm lệch >5% hoặc đổi nhãn ⇒ phản biện lại (B2), còn không là xác nhận cơ học.
4. **E17**: dựng tâm kỳ vọng điều chỉnh theo PREREG_adj_v2 (A/B/C/C+, p theo thang, cấm đếm hai lần, r 13,5% và RONIC ≤ Ke KHÔNG vào Σ, chiều lên ngang chiều xuống, bảng điều kiện đổi số bắt buộc, dải theo cực trị) → `<dir mã>/ADJ_CENTER.md` + `adj.json`. Đọc `~/.claude/skills/due-diligence/SKILL.md` V9. MÙ GIÁ: không đọc giá thị trường khi dựng.
   - schema adj.json: `ticker`, `dd_date`, `rev` (= `rev` của entry trong LEDGER_PROPOSAL của bạn — Mike sẽ ghi proposal TRƯỚC rồi mới ghi center_adj), `center_base` (= tâm trong proposal), `center_adj`, `range_low`, `range_high` (dương, low ≤ adj ≤ high), + items, sensitivity_only, trigger_table, prereg_md5.
   - `|Σ p×m| > 5%` ⇒ chạy lại mô hình với tổ hợp (không cộng tuyến tính).
5. `LEDGER_PROPOSAL_<MÃ>.json` theo §E14 (nhãn REFUTED_OPEN nếu skeptic không CONFIRMED; thử `dd_price_zones_selfcheck.py --ledger <bản tạm>` 0 lỗi, `MIKE_SRC_ROOT=<worktree>`).
6. Calc gốc có thể đã bị TRIM_DD xoá (bài học đợt 1): khôi phục bằng `git archive 14ad1c925^ <đường dẫn calc> | tar -x -C /tmp/ddrestore_<MÃ>`; so md5 với file khoá; KHÔNG ghi đè repo.

## Cấm (như đợt 1)
KHÔNG ghi `kb/dd_price_zones.json`; KHÔNG email, đặt lệnh, wire; KHÔNG merge master (Mike merge). Pháp lý chỉ WARNING. Pha mù giá. Không sửa giả định đã khoá vì thấy giá.

## Bàn giao
Mỗi mã `<dir mã>/SUMMARY.md` ≤1 trang: lệch D3/D4/E15/E16/V nào, tâm/vùng cũ→mới (Δ%), nhãn, verdict skeptic (đường dẫn rN.json), tâm kỳ vọng điều chỉnh (X, dải, Δ%) + bảng điều kiện đổi số, rủi ro/việc mở, khuyến nghị lớp. Commit CHỈ thư mục của mình trong worktree (`git add agents/Taylor/research/dd_recheck_20261124w2/<MÃ>`); commit gate báo job khác LIVE ⇒ đợi 30s thử lại. Ghi bus finding khi xong (mỗi mã 1 finding, đừng đợi hết cả job).
