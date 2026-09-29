# CASH_VENDOR gate — giữ ĐÓNG, theo dõi tới mốc rà soát

**Trạng thái: ĐÓNG (fail-closed), user xác nhận 2026-08-15.** Mở câu hỏi 2026-08-13 (job
`Taylor_20260813_041648`, bus topic `Taylor/can-user-quyet-mo-cong-CASH_VENDOR-va-kiem-freshness`).
Chủ: Taylor (code) / Mike (chính sách + tracking).

## Câu hỏi

`dividend_adjusted_return.py::DividendAdjustment.cash_per_share` (dòng ~177-191) chỉ nhả số cho
báo cáo khi `kind == "CASH_CONFIRMED"` (giải ra từ TIỀN BROKER THẬT). Từ 2026-08-13 script còn tính
thêm `vendor_cash`/`vendor_stock` — số cổ tức/tỉ lệ lấy từ `tav2_bq.corporate_action` khi tiền
broker KHÔNG giải được (mã giao dịch mỏng, không thấy dòng cash trong nhật ký lệnh). Số vendor
**hiện ra để đối soát** (`vendor_check`, `vendor_note`) nhưng **KHÔNG được cộng vào tỉ suất báo
cáo gửi NĐT** — đúng §21 (chỉ số đã đối soát broker mới vào báo cáo).

Bằng chứng ủng hộ mở cổng: 6/6 khớp TUYỆT ĐỐI với tiền broker thật (MBB 1.000, BID 450, CTG 450,
VCB 450, NCT 8.000, SAB 3.000). Bằng chứng CHƯA đủ: n=6, cùng 1 tháng (2026-07), toàn cổ tức tiền
mặt thuần — chưa có ca ISS (thưởng CP/quyền mua)/hỗn hợp, chưa đo được độ trễ công bố của vendor
so với ngày tiền về thật.

## Quyết định (user, 2026-08-15)

**Giữ CHƯA mở** — đồng ý đề xuất gốc của Taylor. Không đổi code (cổng đã fail-closed sẵn, dòng
191 `dividend_adjusted_return.py` không đổi). Đây là quyết định CHÍNH SÁCH, không phải kỹ thuật.

**Điều kiện mở lại** (CẢ HAI, không phải một):
1. Xuất hiện **≥1 sự kiện ISS hoặc hỗn hợp** (thưởng CP/quyền mua đi kèm ex-date) qua
   `tav2_bq.corporate_action` mà vendor và broker cùng xác nhận được — mở rộng bằng chứng ra
   ngoài "toàn cổ tức tiền mặt thuần".
2. Đã qua **≥1 tháng** kể từ đề xuất gốc (2026-08-13) → sớm nhất **2026-09-13**.

Không tự mở khi chỉ đạt 1 trong 2 điều kiện. Đạt cả hai → dispatch Taylor đối soát lại (mẫu lớn
hơn, có ca ISS/hỗn hợp) rồi mới trình user quyết mở/không mở — **không tự động mở**, vẫn cần
user xác nhận lần nữa (đây là chính sách gửi tiền thật cho NĐT).

## q2 (freshness `corporate_action`) — ĐÃ XÁC NHẬN, writer hoạt động bình thường

Lúc hỏi (2026-08-13 04:43): `MAX(ingested_at)=2026-08-12 15:48:52`, `n_ingest_days=1` (nghi ngờ
nạp 1 lần rồi đứng). Đo lại 2026-08-15:

```
max_ingested        n_ingest_days  max_public_date
2026-08-14 15:49:17  3             2026-08-13
```

3 ngày ingest liên tiếp (08-12→08-14) — writer chạy đều, KHÔNG kẹt. Không cần báo ai sửa.

## Cách check mốc 2026-09-13 (khi tới)

Schema thật (đo 2026-08-15): cột phân loại là `event_code`, giá trị quan sát được
`DIV/ISS/AIS/NLIS/SUSP/MOVE/MA` — KHÔNG có nhãn `MIXED` sẵn; "hỗn hợp" = cùng `(ticker, ex_date)`
có cả `DIV` và `ISS`.

```sql
-- sự kiện ISS thuần kể từ đề xuất gốc
SELECT COUNT(*) AS n_iss FROM tav2_bq.corporate_action
WHERE event_code = 'ISS' AND ex_date >= '2026-08-13';

-- sự kiện hỗn hợp (DIV + ISS cùng ex-date, cùng mã)
SELECT COUNT(*) AS n_mixed FROM (
  SELECT ticker, ex_date FROM tav2_bq.corporate_action
  WHERE event_code IN ('DIV', 'ISS') AND ex_date >= '2026-08-13'
  GROUP BY ticker, ex_date
  HAVING COUNT(DISTINCT event_code) = 2
);

SELECT MAX(ingested_at) FROM tav2_bq.corporate_action;  -- vẫn phải tươi
```
`n_iss + n_mixed > 0` + đã qua 09-13 ⇒ đủ điều kiện dispatch Taylor đối soát mở rộng.
