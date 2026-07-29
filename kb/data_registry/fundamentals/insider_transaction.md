---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.insider_transaction
group: fundamentals
writer: bq_admin — backfill 1 lần 2026-07-27 14:35–14:36 UTC (ingested_at); CADENCE REFRESH CHƯA XÁC NHẬN
first_profiled: 2026-07-29 (Taylor, job Taylor_20260729_015830)
usage_note: SNAPSHOT trạng thái hiện tại, KHÔNG phải event-log append-only — public_date bị ghi đè khi Đăng ký→Đã thực hiện xong
---

# `tav2_bq.insider_transaction`

**Status: CANONICAL** (nguồn duy nhất cho giao dịch nội bộ) — **nhưng đọc kỹ mục "Bẫy" trước khi
dùng làm tín hiệu; có 4 bẫy point-in-time/kế toán đã đo được.**

## Là gì
Công bố giao dịch cổ phiếu của người nội bộ / người liên quan / cổ đông lớn tổ chức theo Thông tư
96/2020. 1 dòng = 1 **sự kiện công bố** (không phải 1 khớp lệnh). `id` UNIQUE (52.155/52.155).

- **Coverage**: `public_date` 2014-12-31 → 2026-07-24 · 1.599 ticker · 52.155 dòng.
- **Partition** `public_date`, **cluster** `ticker`. Quét full bảng rất rẻ (~vài chục MB).

### 3 nhóm TÁCH SẠCH bằng `event_code` (dùng field này, KHÔNG dùng heuristic `trader_person_id IS NULL`)
| `event_code` | Nghĩa | Dòng | `trader_person_id` | Ý nghĩa tín hiệu |
|---|---|---|---|---|
| `DDIND` | Giao dịch cá nhân (người nội bộ) | 28.828 | 100% CÓ | **True insider** — thông tin bất cân xứng |
| `DDRP` | Giao dịch người liên quan | 6.795 | 100% CÓ | Insider gián tiếp (vợ/chồng/con/em…) |
| `DDINS` | Giao dịch tổ chức | 16.532 | **100% NULL** | Cổ đông lớn/tổ chức (SCIC, quỹ ngoại) = **FLOW, không phải inside info** |

`trader_person_id IS NULL` ⟺ `event_code='DDINS'` (tương quan 100%) — nhưng dùng `event_code` vì nó
cũng tách được `DDIND` vs `DDRP`, thứ mà person_id không tách được.

### Các field khác
- `action_code`/`action_type`: `B`/Mua 28.024 · `S`/Bán 24.102 · `TN`/Thưởng 26 · `G`/Tặng 3.
- `trade_status`: `Đã thực hiện xong` 50.934 · `Đăng ký` 1.190 · `Không thực hiện được` 2.
- `role_name` **KHÔNG phải chức danh** — chứa TÊN NGƯỜI, trùng `trader_name`/`relative_name`
  (vd "Bùi Minh Tuấn", "Vợ Phạm Anh Tuấn"). **Bảng KHÔNG có field chức danh (CT/TGĐ/KTT)** — ai cần
  phân tầng theo chức vụ phải lấy nguồn khác. NULL ở 100% dòng `DDINS`.
- `relative_name` của `DDRP` có TIỀN TỐ quan hệ trong chuỗi ("Vợ …", "Em …", "Con …") — parse được
  nếu cần, nhưng chưa chuẩn hoá.
- `share_acquire` = **lượng đã khớp CÓ DẤU** (Bán → âm ở 21.138/23.643 dòng Bán-Done, nhưng
  **~2.500 dòng Bán KHÔNG âm** ⇒ luôn tự áp dấu theo `action_code`, đừng tin dấu sẵn có).
- `share_register` = lượng ĐĂNG KÝ. `ownership_after` = tỷ lệ sở hữu sau (thập phân, 0.0034 = 0,34%).

## Ai ghi / cadence
bq_admin. `ingested_at` chỉ có **72 giá trị phân biệt trong 81 giây ngày 2026-07-27** ⇒ tới nay mới
**đúng 1 lần backfill**, CHƯA có bằng chứng cron refresh. **Phải xác nhận cadence với bq_admin/Winston
trước khi bất kỳ thứ gì live đọc bảng này** — nếu không refresh, mọi tín hiệu sẽ đứng im từ 07-24.

## Bẫy
**(1) BẢNG LÀ SNAPSHOT TRẠNG THÁI, KHÔNG PHẢI EVENT-LOG — `public_date` bị GHI ĐÈ.**
Cùng 1 `id` chuyển trạng thái `Đăng ký` → `Đã thực hiện xong` và `public_date` đổi theo:
- dòng `Đăng ký`: `public_date` **TRƯỚC** `start_date` (trung vị **−3 ngày**; 1.120/1.190 dòng
  `public_date < start_date`) = ngày công bố Ý ĐỊNH (đúng tinh thần TT96/2020).
- dòng `Đã thực hiện xong`: `public_date` **SAU** `end_date` (trung vị **+5 ngày**; 47.948/50.934 dòng
  `public_date > end_date`) = ngày báo cáo KẾT QUẢ.
⇒ Với 50.934 sự kiện đã hoàn tất, **ngày công bố đăng ký gốc ĐÃ MẤT**. Không thể backtest trung thực
"lợi thế công bố-trước" của VN từ bảng này; muốn có phải **tự snapshot bảng theo ngày từ giờ trở đi**
(hoặc lấy nguồn khác). Ước lượng ngày đăng ký ≈ `start_date − 3` là IMPUTE, không phải sự thật.

**XÁC NHẬN bởi bq_admin (2026-07-29, đọc source ETL, không còn là suy luận từ dữ liệu):**
1. `publicDate` là field VCI tự maintain trong DB nguồn của họ — **không gắn với ý nghĩa "ngày công
   bố sự kiện"**; khi event lật Registration→Done, chính VCI dời `publicDate` sang ngày công bố kết
   quả (verified qua comment source dòng 337 & 532-533, cơ chế feed re-surface flip).
2. Pipeline ingest có bước `_merge_prefer_done` (dòng 213-238): Done luôn thắng not-Done khi merge
   → `public_date` trong store bị ghi đè thành ngày kết quả, **kể cả khi lần sync trước đã bắt được
   dòng lúc còn Đăng ký** (không có cơ chế giữ bản snapshot cũ).
3. Không có cột nào khác lưu ngày công bố đăng ký gốc; `start_date`/`end_date` là cửa sổ ĐƯỢC PHÉP
   giao dịch, không phải ngày công bố.
⇒ Kết luận "ngày đăng ký gốc đã mất vĩnh viễn cho event Done" nay là **sự thật đã xác nhận ở tầng
nguồn**, không phải suy luận thống kê — đề xuất §5.4 (tự snapshot hàng ngày từ giờ trở đi) là con
đường DUY NHẤT để lấy lại cửa sổ pre-trade, không có cách nào phục hồi lịch sử.

**(2) `Không thực hiện được` gần như không được dùng (2 dòng/11 năm) — tỷ lệ không-thực-hiện THẬT nằm
ở `share_acquire`:** trong 31.505 dòng Done có `share_register>0`: **14,7% khớp 0 cổ phiếu**
(4.646), **27,2% khớp một phần** (8.567), **58,1% khớp đủ** (18.292); trung vị fill = 1,0, p25 ≈ 0,38–0,44.
Ngoài ra **19.393/50.934 dòng Done có `share_register=0`** (không mang lượng đăng ký sang) ⇒ chỉ
tính được fill-ratio trên ~62% mẫu.

**(3) `share_before`/`share_after` KHÔNG đáng tin ở dòng `Đăng ký`** (606/733 dòng Mua-Đăng ký lại có
`share_after < share_before`). Ở dòng Done, `|share_after − share_before| = |share_acquire|` chỉ khớp
**91% (Mua)**; đừng dùng delta tồn kho thay cho `share_acquire`.

**(4) Cụm nhiều người MUA cùng ngày = nhiều khả năng ESOP/phát hành, KHÔNG phải mua chủ động.**
327 sự kiện `DDIND`-Mua có ≥5 người cùng ticker cùng `public_date` (2.525 dòng = 15,7% dòng Mua),
trong khi phía Bán chỉ 29 sự kiện (176 dòng = 1,5%) — bất đối xứng này chính là dấu vân tay ESOP.
Tín hiệu "insider mua" phải khử nhóm này (vd cap số người/sự kiện, hoặc loại các sự kiện có
`start_date = end_date` + nhiều người) nếu không sẽ đo nhầm lịch phát hành cổ phiếu ưu đãi.

## Dùng đúng
- Ngày "biết được" AN TOÀN cho backtest = `public_date` của dòng Done (đã là ngày báo cáo kết quả).
- Chỉ dùng `DDIND` (+ tuỳ chọn `DDRP`) cho tín hiệu inside-info. **KHÔNG trộn `DDINS`** (flow tổ chức).
- Luôn tự áp dấu: `IF(action_code="S", -ABS(share_acquire), ABS(share_acquire))`.
- Chuẩn hoá theo `OShares` (`ticker_financial`) hoặc `Volume_1M` — số cổ phiếu thô không so sánh
  chéo mã được.

## Kết quả nghiên cứu đã có
`mike/agents/Taylor/research/insider_transaction_scoping_20260729.md` (job `Taylor_20260729_015830`).
