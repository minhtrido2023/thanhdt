# data/_quarantine — file stale đã cách ly, KHÔNG ĐỌC

Tạo 2026-07-11 (Winston, job `Winston_20260711_023903`, theo audit `Winston_20260710_173031`
— hậu quả bug reorg 06-21: writer ghi WORKDIR root trong khi chain/reader đọc `data/`,
EW-leg đóng băng 3 tuần → BULL candidate giả 07-10).

Các file ở đây là bản ĐÓNG BĂNG cũ, giữ lại làm bằng chứng audit. Bản tươi canonical
nằm ở `data/` (được `daily_refresh_v34b_linux.sh` ghi mới mỗi đêm + assertion step [8b]
đảm bảo mtime tươi):

| File cách ly | Đóng băng từ | Bản tươi thay thế |
|---|---|---|
| `vnindex_5state_ew_staging_FROZEN_20260619.csv` | 2026-06-19 | `data/vnindex_5state_ew_staging.csv` |
| `vnindex_5state_tam_quan_v3_4b_full_history_FROZEN_20260630.csv` | 2026-06-30 | `data/vnindex_5state_tam_quan_v3_4b_full_history.csv` (mirror từ root mỗi đêm) |
| `vnindex_5state_ew_full_ROOT_ORPHAN_20260709.csv` | 2026-07-09 (orphan root sau fix 498c3a6) | `data/vnindex_5state_ew_full.csv` |

Không script nào được trỏ vào thư mục này. Sau ~1 tháng không ai cần đối chiếu nữa thì xoá được.
