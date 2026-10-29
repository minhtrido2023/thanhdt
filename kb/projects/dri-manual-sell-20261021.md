# DRI — user bán tay 21/10/2026 (chuyển nguyên văn từ current_ops.md, 21/10 23:5x ICT)

## DRI — user BÁN TAY 21/10/2026 theo research discretionary sleeve (`decided_by: user`, 22:29 ICT) — ĐÃ XÁC NHẬN, MỌI AGENT KHÔNG HỎI LẠI
- DRI bán @15.400 ngày 21/10: **SpaceX −1.200cp (3.700→2.500)**, **ZaloPay −600cp (1.900→1.300)**. Bằng chứng broker: `data/execution_logs/dnse_khoplenh_broker_confirm_21-10-2026.csv` + `dnse_raw` positions. Bus question `DollarBill/spacex-dri-sell-ngoai-plan-20261021` đã ĐÓNG.
- **KHÔNG phải sự kiện bất thường**: không điều tra Mafee/Spyros, không escalate, không coi là corp-action (DRI không có sự kiện nào; `ADJFACTOR_PRICE_FIELD_MISMATCH|DRI|…|tick_offset` là chuyện khác, đã biết). Cờ `plan-position-drift` DRIFT SpaceX/ZaloPay 21/10 = đúng điều này (cờ-only).
- Vị thế DRI còn lại (2.500 + 1.300cp) vẫn là vị thế bot đang giữ; plan T+1 chỉ cần dùng số dư mới. **Lệnh bán tay của user ngoài plan là hợp lệ khi user đã nói** — chỉ hỏi lại nếu SỐ LƯỢNG broker khác số user xác nhận ở trên.
- ⚠️ **Còn treo (cần xử lý code, chưa làm):** `compute_active_nav.py` vẫn fail-closed (rc≠0) cho cả 2 account vì cổng KL chỉ đọc journal bot (`exec_*_journal.csv`), không đọc statement broker → `active_nav_*.json` KHÔNG làm mới. Không phải sự cố mới; sizing lùi về file cũ/`nav_history` (≤5 ngày). Đừng escalate lại — chờ user duyệt fix cho cổng đọc `dnse_khoplenh_broker_confirm_*.csv`.


## Chuyển nguyên văn từ current_ops.md (27/10)
- ✅ ĐÃ VÁ 22/10 (master `f0e293c30`, user duyệt): cổng KL `compute_active_nav.py` hợp nhất fill journal bot + statement DNSE (`dnse_khoplenh_broker_confirm_*.csv`); phần dư không giải thích được vẫn chặn. Chi tiết: `kb/projects/dri-manual-sell-20261021.md`.


## Chuyển nguyên văn từ kb/current_ops.md (29/10)
## DRI — user BÁN TAY 21/10/2026 (`decided_by: user`, 22:29 ICT) — ĐÃ XÁC NHẬN, MỌI AGENT KHÔNG HỎI LẠI
- Bán @15.400: SpaceX −1.200cp (→2.500), ZaloPay −600cp (→1.300). KHÔNG bất thường, không điều tra, không escalate; cờ `plan-position-drift` 21/10 = đúng việc này. Chỉ hỏi lại nếu SỐ LƯỢNG broker khác số trên.
- Cổng KL `compute_active_nav.py` đã vá 22/10 (chi tiết: `kb/projects/dri-manual-sell-20261021.md`).
