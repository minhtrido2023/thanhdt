---
kind: policy
group: _rules
title: Quy tắc thêm/sửa cron mới — 4 câu hỏi bắt buộc + chống xung đột + buffer
enforced_by: kb/coding_guidelines.md §11
---

# Quy tắc thêm/sửa cron mới

> RULE áp dụng khi THÊM/SỬA 1 dòng cron (không phải lịch hiện tại — lịch hiện tại ở bảng chính
> [`../cron_registry.md`](../cron_registry.md)). Cùng nội dung được §11 `coding_guidelines.md`
> enforce. Đọc file này TRƯỚC khi chọn giờ cho job mới.

## Quy tắc thêm cron mới — 4 câu hỏi bắt buộc trả lời TRƯỚC khi chọn giờ

1. **ĐỌC gì, vintage nào?** Phân loại: BQ live / BQ local cache (luôn T-1, không sync cuối tuần,
   ⚠️ có thể ẨN — mọi script source `wc_env.sh` và đi qua `simulate_holistic_nav.bq` là consumer
   cache dù code không nhắc chữ "cache"; phải grep CHUỖI IMPORT, không chỉ tên biến — bài học C1:
   `publish_gated_state.py` tưởng đọc live suốt ~2.5 tuần) / DNSE live API (bắt buộc cho MTM
   same-day) / file local (ghi rõ ai ghi, lúc nào) / web external (retry bao lâu).
2. **Nguồn đó TƯƠI lúc nào?** Đo thật bằng log/query khi nghi ngờ — KHÔNG dùng mốc trong comment
   cũ (đã sai nhiều lần). Mốc đã đo (2026-07): ticker/ticker_prune ingest same-day ≤~17:30 ICT;
   DT5G tươi sau daily_refresh 18:30 (đọc live); recommendations/plan tươi sau pipeline 19:00;
   cache tươi-T-1 sau 23:45.
3. **Job cần T hay T-1?** T-1 đúng cho planning-trước-mở-cửa/paper report → cache OK, giờ nào
   cũng được miễn sau 23:45 đêm trước. Cần T (regime EOD, MTM same-day, freshness gate) → BẮT BUỘC
   nguồn live VÀ chạy sau mốc nguồn có T.
4. **Ai tiêu thụ, deadline của họ?** Vẽ chuỗi job→consumer→deadline cuối (thường preflight 08:45
   sáng hôm sau).

## Chống xung đột tài nguyên
- ≥2 writer cùng đích → atomic write (tmp+`os.replace`) hoặc append-only+tag nguồn hoặc tách giờ.
- File đọc-sửa-ghi (kiểu `events_buffer.md`) → flock cùng lock với writer khác.
- Không đặt 2 job nặng CPU/network trùng phút — lệch tối thiểu 5' (tiền lệ rubber 18:30→18:35).
- pkill trong cron: pattern không tự khớp chính nó (`[b]ot_execute` — bài học 07-06).

## Buffer — nguyên tắc "buffer + VERIFY ARTIFACT, không tin giờ"
Buffer tối thiểu = runtime upstream đo thật (gồm retry) + ≥10' dự phòng. Buffer KHÔNG BAO GIỜ là
bảo chứng duy nhất — downstream production PHẢI verify artifact (mtime, ngày trong file, MAX(time)
BQ) trước khi dùng. Publish bảng production (regime/giá/plan) PHẢI đọc nguồn live — `env -u
BQ_LOCAL_CACHE` nếu import chain có thể dính cache (bài học C1).

## Ghi lại ở đâu
- Comment crontab: giờ ICT + "sau X vì Y, trước Z vì W" + ngày đổi + commit.
- **Bảng chính [`../cron_registry.md`](../cron_registry.md)** — cập nhật CÙNG COMMIT với mọi thay
  đổi crontab; đồng thời ghi 1 dòng vào [`CHANGELOG.md`](CHANGELOG.md).
- Đổi giờ 1 job giữa ngày → kiểm tra job có bị nhảy khe hôm đó không, chạy tay bù nếu cần
  (bài học C1b, 07-10 daily_refresh miss vì đổi giờ giữa ngày).
- Cuối tuần/lễ: khai báo rõ job chạy 1-5/6/0-4/daily; nhớ cache không sync cuối tuần, lễ VN chưa
  encode đủ trong `vn_market.py`.

↩ [Về cron_registry (bảng chính)](../cron_registry.md) · [index nhóm _rules](index.md)
