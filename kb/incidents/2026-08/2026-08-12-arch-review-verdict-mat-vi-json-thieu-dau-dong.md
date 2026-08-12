# 2026-08-12 — Verdict CONFIRMED của arch-reviewer bị vứt đi vì JSON thiếu ĐÚNG MỘT dấu `}` → question `wags-arch-review-inconclusive` GIẢ

**Hiện tượng.** `wags_autofix` vòng coord-2026-08-11 báo `INCONCLUSIVE` + post question
`Wags/wags-arch-review-inconclusive: coord-2026-08-11`. Đọc bus thì tưởng chuỗi kiểm chứng
không chạy được.

**Chẩn đoán (artifact thật).** `logs/arch_review_20260811_055220.log` cho thấy arch-reviewer
đã audit ĐẦY ĐỦ và kết luận:

```
{"finding_topic": "wags-fix: coord-2026-08-11 — ack triaged-needs-human phu topic TAI PHAT
 (suppress_days)", "verdict": "CONFIRMED", "confidence": "high", "summary": "Fix đúng root...
```

Khối VERDICT_JSON dài 4100 ký tự. Quét cấu trúc: object `"checks"` mở ở char 660 **không bao
giờ được đóng**; dấu `}` cuối cùng (char 4099) bị dùng để đóng `checks`, để hở object ngoài
cùng ⇒ `json.loads` ném `Expecting ',' delimiter: line 1 column 4101`. **Thiếu đúng 1 dấu `}`.**

**Root cause.** Không phải bug logic — là **hỏng đường ĐỌC kết quả bị trình bày y như kết quả
xấu** (skill `close-the-loop` root-cause-B). Parser trong `bin/wags_autofix.sh` dùng
`json.loads` nghiêm ngặt; hỏng 1 ký tự ở giữa ⇒ vứt cả verdict, kể cả khi field `verdict` nằm
ngay ĐẦU khối, TRƯỚC vùng hỏng, hoàn toàn cứu được. Cùng họ với bug đã ghi:
`verify_finding.sh` JSON trailing-comma (bus báo INCONCLUSIVE trong khi verdict thật là
CONFIRMED) và sự cố 2026-07-08 (`{"status":"sent"}` chen vào stdout).

**Fix.** Tách parser ra `bin/wags_verdict_parse.py` (heredoc không test được ⇒ không có
selfcheck ⇒ đúng thứ arch-reviewer từng bắt lỗi). Thêm nhánh vá: nếu `json.loads` fail, suy ra
dãy dấu đóng còn thiếu theo stack cấu trúc rồi **chỉ THÊM vào CUỐI** và parse lại.

An toàn vì phép vá **không sửa/xoá/chèn giữa** ký tự nào ⇒ không thể biến `NEEDS_CHANGES` thành
`CONFIRMED`; `verdict` đọc nguyên văn. Ba chốt chặn: trần `MAX_REPAIR=6`; verdict phải thuộc
`ALLOWED_VERDICTS`; kết quả gắn cờ `parse_repaired`/`parse_error` để phân biệt "CONFIRMED sạch"
với "CONFIRMED cứu từ JSON hỏng" — không giấu việc đã phải vá. Nháy kép chưa đóng / dấu đóng
lệch loại / thừa ⇒ **bỏ cuộc, giữ INCONCLUSIVE**, không đoán.

**Verify.** `bin/wags_verdict_parse_selfcheck.py` **37 PASS / 0 FAIL**, trong đó ca 15 chạy lại
trên CHÍNH log 08-11 đã fail: `json.loads` nghiêm ngặt vẫn fail (tái lập được sự cố), parser
mới cứu ra `CONFIRMED` + `confidence=high` + `parse_repaired="}"` + khối `checks` nguyên vẹn.
Mutation (bỏ nhánh vá) ⇒ selfcheck đỏ. `bash -n` + `shellcheck -S error` OK.

**Hệ quả.** Fix `suppress_days` của coord-2026-08-11 (commit `bdfedc8a`) THỰC TẾ đã được
arch-reviewer duyệt CONFIRMED/high từ 08-11 — không hề treo.

**Lesson.** Verdict của reviewer là dữ liệu VÔ GIÁ và KHÔNG TÁI TẠO ĐƯỢC (chạy lại tốn 1 lượt
opus ~1500s và có thể ra khác). Đừng để một ký tự hỏng ở cuối chuỗi hủy cả lượt audit — nhưng
cũng đừng "sửa cho parse được" theo kiểu tự do: chỉ chấp nhận phép biến đổi **đơn điệu, chứng
minh được là không đổi nội dung sẵn có**, và luôn gắn cờ đã vá.
