---
kind: local-file
status: NOT-YET-CREATED (công cụ ghi có từ 2026-10-14, nhánh feat/fund-history-lock-20261014; file thật xuất hiện ở lần đính chính đầu tiên Mike áp)
source: data/execution_logs/nav_history_corrections.jsonl
group: trading-bot
role: nhật ký chỉ-thêm của mọi lần SỬA TAY nav_history (đính chính số đã công bố — chính sách quỹ mở điểm 4)
writer: "mike/bin/fund_restatement.py apply --real-data (chạy TAY, Mike, sau khi user duyệt)"
---

# data/execution_logs/nav_history_corrections.jsonl

DÙNG CHUNG cho mọi tài khoản — mỗi dòng có `account`; **lọc `account` ở dòng đầu tiên khi đọc (§12)**.

## Là gì
Mỗi dòng = một lần `fund_restatement.py apply`: `account, applied_at_ict, approved_by, correction_md5,
impact_report_md5, md5_before, md5_after` (md5 của `nav_history_<account>.csv` trước/sau),
`changes[]` = `{op: replace|insert|delete, date, old, new, reason, evidence}`.

- `backup` = đường (tương đối) tới bản sao lưu NGUYÊN BYTE nav_history trước khi áp:
  `restatement_backups/<account>_<giờ ICT YYYYmmddTHHMMSS>_<md5 trước>.csv` (chỉ-thêm, mở bằng `x`, không
  bao giờ ghi đè; áp lại cùng byte ⇒ dùng lại bản cũ).
- Bản ghi `status: "aborted"` (`md5_seen`, `aborted_at_ict`): md5 nav_history đọc lại NGAY trước
  `os.replace` khác lúc bắt đầu (snapshot vừa ghi chen) ⇒ KHÔNG ghi file; lần áp sau ghi bản ghi mới.

## Ai ghi / ai đọc
- Ghi: chỉ `fund_restatement.py apply`, chỉ trong khung 09:00–18:30 ICT (nav_history thật bị ghi lúc
  19:00–21:45 `nav_sync_retry` mỗi 15', 19:10 EOD, 19:50 +2 retry; không có khoá chung). Nhật ký TRƯỚC,
  nav_history SAU; chạy lại sau khi chết giữa chừng nhận ra bản ghi đang dở (cùng account +
  correction_md5 + cặp md5, không phải `aborted`) và KHÔNG ghi bản ghi thứ hai.
- Đường lui TRƯỚC khi chốt sổ đơn vị: áp một đính chính NGƯỢC lên file HIỆN TẠI (impact → apply: có sao lưu +
  nhật ký). CHỈ khi công cụ hỏng: chép `restatement_backups/<file>` về `nav_history_<account>.csv` rồi ghi
  tay một dòng nhật ký `{"status":"rolled_back_manual", md5_before, md5_after, by}` (KHÔNG áp đính chính
  ngược sau khi chép tay — mọi mục đã có sẵn ⇒ công cụ từ chối "ĐÃ ÁP" vì nhật ký không có bản ghi của file
  đó). SAU khi chốt: chỉ còn `nav_unit_ledger.py --restate`.
- "ĐÃ ÁP từ trước" (rc=0, không ghi gì) chỉ khi nhật ký có bản ghi đã áp của (tài khoản, md5 file đính chính,
  md5 sau); không có ⇒ lỗi (gõ nhầm ngày, hoặc chép tay bản sao lưu).
- Đọc: chưa có consumer; để người/auditor tra "dòng nav_history này từng bị sửa chưa, ai duyệt, vì sao".

## Bẫy
- Thư mục có `dnse_raw_*.jsonl` (kể cả bản sao trong /tmp) là "dữ liệu thật" ⇒ `apply` cần `--real-data`;
  biến giờ giả `FUND_RESTATEMENT_TEST_NOW_ICT` (chỉ selfcheck) bị TỪ CHỐI ở thư mục canonical và ở
  NAV_HISTORY_DIR suy từ WC_ROOT (vẫn được nhận ở bản sao có dnse_raw khác — vô hại, không cron nào ghi vào đó).
- **`daily_nav_snapshot.py --from-raw` và việc chạy lại snapshot KHÔNG ghi vào nhật ký này** — chúng sửa
  nav_history theo đường riêng. Nhật ký chỉ phủ đính chính đi qua `fund_restatement.py`.
- File không nằm trong git (`.gitignore` chặn `data/`).
- Dòng cuối hỏng (JSON cắt cụt) ⇒ `apply` từ chối ghi tiếp, phải kiểm tay.
