# A2 — BACKFILL_REPORT FINAL (22/11/2026, thay bản v1 sau 2 vòng arch-review; user duyệt merge + archive script 22/11 19:51, decided_by user)

**Trạng thái:** sổ `kb/dd_price_zones.json` trên master (merge `ded6b34e0`) = bản backfill v3. Script một-lần đã archive: `bin/archive/dd_ledger_backfill_skeptic_final.py.retired-20261122` (không còn là công cụ chạy; muốn tái tạo thì bỏ hậu tố; ca mới ghi sổ phải tự khai trường, selfcheck đòi từ 23/11).

## Số đo (đọc lại từ sổ master)
- Rev cuối mỗi mã (36 mã): **CONFIRMED 15 · FIXED_UNVERIFIED 21 · REFUTED_OPEN 0 · NONE 0**. Toàn sổ 95 entry: CONFIRMED 20 · FIXED_UNVERIFIED 63 · NONE 11 · REFUTED_OPEN 1.
- So baseline A0 (CONFIRMED 19 / REFUTED 16 / OTHER 1 theo từ khoá): lệch vì luật A2 chặt hơn — CONFIRMED chỉ khi vòng cuối CONFIRMED VÀ không đính chính sau đó. Mã hạ CONFIRMED→FIXED_UNVERIFIED: HHS, MSB, PNJ, SCL (đều kèm đính chính/phần không xác nhận). Bốn mã bắt buộc nêu: **PNJ, PAT, QTP, SZL = FIXED_UNVERIFIED, basis `ambiguous_backfill`** (PNJ: khối định giá KHÔNG được xác nhận, chưa vòng 2; PAT r5: chưa chạy skeptic; QTP: vòng 2 CONFIRMED + đính chính sau; SZL: r3c Mike kiểm cơ học, không skeptic vòng cuối).
- **Mã rev cuối mang `ambiguous_backfill` (7): HHS, MSB, PAT, PNJ, QTP, SCL, SZL** — Mike xác nhận tay; toàn bộ 20 entry mơ hồ (mọi rev): `kb/projects/dd-ledger-ambiguous-queue-20261122.md`, hạn 29/11. KHÔNG mã nào được gán CONFIRMED trong ca mơ hồ.
- `audited_fy_missing=true`: VLB (2 entry). PVT (ý kiến 2025 treo) và VCB (số KT 2025 chưa đối chiếu PDF) không gán, chỉ nhắc.
- `skeptic_verdict_path`: KHÔNG đoán (vòng 2 bỏ lọc mtime vì phụ thuộc TZ/checkout) — chỉ điền khi đúng 1 ứng viên (với CONFIRMED: file chứa chữ CONFIRMED); nhiều ứng viên ⇒ null. A4 (runner) sẽ cho path thật từ DD kế tiếp.

## Kiểm
Selfcheck `dd_price_zones_selfcheck.py`: 95 entry/36 mã, lỗi 0 dưới `env -u TZ`, `TZ=Pacific/Kiritimati`, `TZ=America/Los_Angeles`. Backfill tái chạy 4 TZ cho output md5 trùng (trước khi archive). Sổ chỉ THÊM trường (kiểm bằng so JSON với bản `a3f59094b`: 0 entry đổi trường cũ).
