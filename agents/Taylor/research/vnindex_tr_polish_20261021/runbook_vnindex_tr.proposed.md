## VN-Index có cổ tức (vnindex_total_return) — đọc 🔒, ack, đính chính, undo
_(đề xuất của Taylor 21/10 — Mike áp vào kb/ops_runbook.md; lệnh chạy từ gốc mike/, python = `$DNA_PYEXE`)_

- **🔒 "seal bị chặn"** (từ `fund_bench_cron.sh`): `--update` rc=0 nhưng cổng G1/G4 giữ dòng ở `provisional`. Đầu tin có dòng
  "Cặp cần ack (ngày + giá trị)" — đó là thứ cần xem; bên dưới là bằng chứng (cắt 900 ký tự). Cảnh báo **lặp mỗi ngày T3-T7**
  tới khi dòng được seal (BQ lấp dữ liệu) hoặc có ack. G1 (không nối được) KHÔNG ack được — điều tra dữ liệu.
- **Ack G4 số mã / G4_MC** — sửa `data/benchmark/vnindex_tr_acks.json` (người xác nhận, chỉ khi mã thiếu không có GDKHQ cổ tức
  tiền ở D và D+1). Khoá ràng NGÀY + đúng giá trị đã xem; dựng lại ra số khác ⇒ ack mất hiệu lực:
  `"G4": [{"date":"2026-10-14","n_prev":100,"n":94,"confirmed_by":"<tên, giờ>","reason":"<lý do>"}]`
  `"G4_MC": [{"date":"2026-10-14","mc_prev":123456789012,"mc":130000000000,"confirmed_by":"…","reason":"…"}]`
  Mỗi mục phải là list các object; sai dạng ⇒ ValueError rõ ràng (cron báo lỗi, không seal theo giả định).
- **Đính chính dòng sealed** (đường DUY NHẤT): `--restate-sealed DATE… --reason "<số thật>" --confirmed-by "<tên, giờ>"` (thử
  trước bằng `--dry-run`). Từ chối nếu thiếu lý do/người, ngày không phải dòng sealed, dòng sealed khác cũng lệch, hoặc còn
  nổ G1/G4. Sổ `vnindex_tr_restatements.jsonl` chỉ-thêm, ghi TRƯỚC khi thay file; chạy lại sau crash (cùng ngày+lý do+người)
  được gắn `retry_of`.
- **Undo**: `--undo-last-restatement --reason … --confirmed-by …` (`--dry-run` trước). Chỉ hoàn tác đính chính CUỐI trong sổ,
  và chỉ khi md5 file hiện tại == `md5_after` của nó ⇒ dùng được TRƯỚC lần `--update` kế tiếp (cron T3-T7 sẽ đổi file). Ghi dòng
  `{"kind":"undo",…,"undoes":<md5_after>}`; không undo chồng. ⚠️ Undo đưa lại **byte-exact** cả những dòng đang nổ G4/G1 trước đính chính (không chạy lại seal-guard) và `--confirmed-by` là
  chữ tự do — chỉ người thật được điền.
- **Undo dở dang** (chết giữa ghi sổ và `os.replace`): sổ có dòng `undo` nhưng file chưa đổi; lệnh báo "undo đã GHI SỔ nhưng file CHƯA
  được thay" và từ chối chạy lại. Dữ liệu KHÔNG hỏng (file vẫn là bản sau đính chính, đã duyệt). Kiểm bằng md5: với `rows` = các dòng
  sổ, `cur` = bytes file, `V._md5(V.undo_restatement(rows[-2], cur)) == rows[-1]["md5_after"]` (True ⇒ có thể hoàn tất undo). Việc hoàn tất
  làm tay bởi Mike/Taylor (ghi tmp + `os.replace` dưới flock `vnindex_tr_daily.csv.lock`), KHÔNG xoá dòng sổ. Tương tự, đính chính chết
  trước khi thay file: lệnh báo "CHƯA từng được áp" — chạy lại `--restate-sealed` cùng lý do/người (sẽ gắn `retry_of`).
- Sổ restatements chỉ-thêm và có thể phình: đính chính một ngày sealed CŨ lưu toàn bộ phần sealed phía sau vào `rechained_sealed_before`
  (hàng trăm KB/dòng) — chấp nhận vì hiếm.
- **Dòng sổ 12:34 21/10 KHÔNG undo được bằng hàm** (ghi trước khi sổ giữ byte cũ; lệnh từ chối rõ ràng). Khôi phục từ
  `data/benchmark/vnindex_tr_daily.csv.bak_pre_restate_20261021` — bản sao này dọn được sau 24/10.
