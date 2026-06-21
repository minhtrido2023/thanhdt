---
name: repro_results_registry_2026
description: "Cách KHỬ vấn đề 'session trước không tái tạo được kết quả backtest' — registry pin config+snapshot+CSV"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9db4a8d3-af8f-423f-8d4c-e1e32d8b77bb
---

**VẤN ĐỀ (user nêu [REDACTED]19):** hỏi lại cùng một kết quả backtest ở session khác → không tái tạo được. Gốc rễ: backtest chạy live-forward, `END_DATE=detect_end_date()` (data mới nhất) DỊCH mỗi ngày + bảng as-of (`custom30v_8l`/`fa_ratings_8l`) republish → CÙNG config KHÁC số (vd baseline 30.96→31.69 sau 5 phiên). Không phải bug, là data window trôi.

**GIẢI PHÁP (deployed [REDACTED]19) = `data/results_registry.md`** (trong repo). Mỗi số công bố được PIN: lệnh chạy đầy đủ (argv+env) + `AUDIT_END` cố định + đường dẫn CSV đông cứng + metric + self-check. **Quy tắc:**
1. Số công bố PHẢI pin `AUDIT_END` (vd `AUDIT_END=[REDACTED]19`) — không pin = trôi, vô nghĩa đối chứng.
2. **CSV = artifact đông cứng** (bất biến, mỗi TX dò vs BQ thô được). Đối chứng = `$DNA_PYEXE extract_peryear.py <csv>` (recompute, không trôi). Tái lập = chạy lại lệnh đã pin.
3. Nếu re-run lệch do as-of-table republish → **CSV mới là chuẩn**.
4. Số mới đáng nhớ → THÊM 1 dòng vào registry (bắt buộc). Self-check 0 VND là điều kiện cần.

**HÀNH VI BẮT BUỘC cho session sau:** khi user hỏi "kết quả X bao nhiêu / có audit không / tái tạo được không" → **MỞ `data/results_registry.md` TRƯỚC**, đừng tái dựng config từ trí nhớ. Nếu có dòng → trỏ CSV + recompute. Nếu chưa có → chạy với AUDIT_END pin rồi GHI dòng mới. Mở rộng [[simulation_[REDACTED]_audit_default]] (audit mặc định) + [[settled_decisions_capit_8l_2026]] (sổ quyết định). Harness = `pt_v23_audit_2014.py`; helper recompute = `extract_peryear.py`.
