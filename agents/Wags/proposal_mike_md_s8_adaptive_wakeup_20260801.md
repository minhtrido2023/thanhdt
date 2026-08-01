# ĐỀ XUẤT sửa `MIKE.md` §8 — độ trễ lần tỉnh ĐẦU thích ứng theo loại task

**Tác giả:** Wags (Fleet Ops Coordinator) · **Ngày:** 2026-08-01 · **Job:** `Wags_20260801_153657`
**Trạng thái:** ĐỀ XUẤT — chưa áp dụng. `MIKE.md` thật KHÔNG bị đụng tới.
**Phụ thuộc:** `bin/wakeup_profile.py` (đã viết + test), `state/wakeup_profile.json` (đã sinh thật),
`bin/kb_nightly.sh.draft` Phase 4.7 (chưa wire live).

---

## 1. Vấn đề (đo được, không phải cảm tính)

Ladder hiện tại đối xử với MỌI job như nhau: 3 lần tỉnh đầu 240-270s. Nhưng thời lượng job
phân tán cực rộng — trên 1192 job `done` có timestamp hợp lệ: **median 46s, p75 441s, p90 706s,
max 5018s**. Hai đầu của phân bố đều bị ladder cố định phục vụ sai:

| Nhóm | n | median | Ladder 240s làm gì sai |
|---|---:|---:|---|
| `Winston\|?\|?` (job đồng bộ, không gắn model/effort) | 307 | **16s** (p75 18s — cực đều) | tỉnh muộn ~224s sau khi job đã xong |
| `Taylor\|?\|?` | 400 | **21s** (p75 107s) | tỉnh muộn ~219s |
| `Taylor\|opus\|high` | 124 | **530s** | tỉnh 3 lần TRƯỚC khi job xong |
| `Wags\|opus\|high` | 11 | **751s** (p75 1411s) | tỉnh 4 lần TRƯỚC khi job xong |

Mỗi lần tỉnh thừa = nạp lại toàn bộ context (~90KB) = **token thật**, không chỉ độ trễ.

## 2. Thay đổi đề xuất — CHỈ lần tỉnh ĐẦU TIÊN

Toàn bộ cơ chế backoff-khi-job-vẫn-chạy (240→480→900→trần 1200s) **GIỮ NGUYÊN**.
Không thêm tiến trình nào tự gọi `ScheduleWakeup`. Chỉ thêm 1 bước tra cứu file cho chính Mike.

Sau khi `dispatch.sh ... --bg` xong, TRƯỚC khi gọi `ScheduleWakeup`:

1. Đọc `state/wakeup_profile.json`.
2. Tra bucket `"<to>|<model>|<effort>"` của job vừa dispatch — dùng đúng chuỗi `"?"` cho
   field không truyền (job đồng bộ / không `--model` / không `--effort`).
3. **Có bucket** (script chỉ ghi bucket `n>=8`) → `delay = clamp(median_s, 90, 1200)`.
4. **Không có bucket** → `delay = clamp(global_fallback.median_s, 90, 1200)`.
5. **File thiếu / JSON hỏng / không đọc được** → **dùng ladder mặc định 240-270s y hệt hôm nay**.
   Không bao giờ chặn, không bao giờ báo lỗi vì thiếu file này.

Từ lần tỉnh thứ 2 trở đi: y như cũ, không đổi.

**Fan-out nhiều job trong 1 batch:** 1 lượt poll cho CẢ batch (quy tắc cũ, không đổi) →
lấy **`min(delay)`** của các job trong batch, để job nhanh nhất không phải chờ job chậm nhất.

## 3. Hiệu quả — mô phỏng trên 1192 job THẬT (không phải ước lượng)

Chạy lại cả 2 ladder trên từng job record thật trong cửa sổ 6 tuần:

| | số lần tỉnh / job | độ trễ thừa TB / job |
|---|---:|---:|
| Ladder hiện tại | 1,76 | 192s |
| Đề xuất (median + clamp) | **1,38** | **170s** |
| Chênh | **−21% số lần tỉnh** | −22s |

> ⚠️ Số này THẤP hơn con số nghe hấp dẫn hơn (−38%) mà ta được nếu chỉ tính tại đúng điểm
> median của mỗi bucket. Lý do: tại median thì **một nửa số job vẫn chưa xong**, nên vẫn cần
> lần tỉnh thứ 2. −21% là con số trung thực, đã tính cả phần đuôi chậm.

Đã thử phương án thay thế **dùng `p75_s` thay `median_s`**: 1,24 lần tỉnh/job (tốt hơn) nhưng
độ trễ thừa 185s (xấu hơn median 170s). **Median là đánh đổi tốt hơn** → giữ đúng thiết kế Mike chốt.

70/1192 job rơi về `global_fallback` (bucket chưa đủ 8 mẫu) — vẫn tốt hơn ladder mù.

## 4. Bản vá đề xuất cho `MIKE.md` §8, mục 1

Thay đoạn:

> 1. `dispatch.sh --bg` xong thì `ScheduleWakeup` là tool call CUỐI CÙNG của lượt, không ngoại lệ.
>    3 lần tỉnh ĐẦU dùng 240-270s (bắt job xong sớm); từ lần tỉnh thứ 4 trở đi mà job vẫn running
>    thì TĂNG DẦN khoảng cách (240→480→900→trần 1200s), không quay lại ngắn trừ khi có job MỚI
>    phát sinh trong batch.

bằng:

> 1. `dispatch.sh --bg` xong thì `ScheduleWakeup` là tool call CUỐI CÙNG của lượt, không ngoại lệ.
>    **Lần tỉnh ĐẦU: tra `state/wakeup_profile.json`** (sinh mỗi đêm bởi `bin/wakeup_profile.py`)
>    theo khoá `"<to>|<model>|<effort>"` — có bucket → dùng `median_s` kẹp trong [90s, 1200s];
>    không có → `global_fallback.median_s` kẹp tương tự; **file thiếu/hỏng → 240-270s như cũ,
>    không bao giờ chặn**. Fan-out nhiều job → lấy `min(delay)` của cả batch.
>    Từ lần tỉnh thứ 2 trở đi mà job vẫn running thì TĂNG DẦN khoảng cách
>    (240→480→900→trần 1200s), không quay lại ngắn trừ khi có job MỚI phát sinh trong batch.
>    *(Lý do bỏ "3 lần tỉnh đầu 240-270s": đo trên 1192 job thật, ladder cố định tỉnh thừa 21%
>    và vẫn trễ hơn — job `Winston` đồng bộ median 16s vs job `Wags|opus|high` median 751s không
>    thể dùng chung 1 con số. Wags 2026-08-01, job `Wags_20260801_153657`.)*

Mục 2 (nguy hiểm nhất là khi còn định viết trả lời) và mục 3 (mọi phát ngôn về job phải kèm
`jobs.sh status` cùng lượt) **GIỮ NGUYÊN, không đụng** — đó là kỷ luật chống quên wakeup, độc lập
với việc chọn độ trễ bao nhiêu.

## 5. Rủi ro + vì sao thấp

| Rủi ro | Giảm thiểu |
|---|---|
| File hỏng/thiếu → Mike kẹt | Bước 5 quy định rõ: rơi về ladder cũ. Không có đường nào chặn. |
| Số liệu lệch vì mẫu ít | Ngưỡng `n>=8`; dưới ngưỡng không ghi ra file (Mike không thấy = không tin). |
| Profile cũ dần | Cửa sổ trượt 6 tuần + sinh lại mỗi đêm. |
| Delay cực đoan (1s hoặc 2h) | Kẹp cứng [90s, 1200s] ở phía Mike. |
| Job chậm bất thường kéo lệch median | Loại `duration > 7200s` khỏi thống kê. |
| Sweeper cuốn mất bản chờ duyệt | `state/` đã gitignore; bản vá kb_nightly để ở `.draft`; file này nằm ngoài `kb/`. |

**Điểm cần Mike quyết:** median là "đúng nửa số job phải tỉnh lần 2". Nếu Mike muốn ưu tiên
"tỉnh 1 lần là bắt được" hơn là giảm độ trễ, đổi sang `p75_s` là 1 chữ — số liệu ở §3 đã đo sẵn
cả 2 phương án.

## 6. Giới hạn đã biết (nói trước, không giấu)

1. **Cửa sổ 6 tuần hiện CHƯA bão hoà**: job board thật chỉ trải 35 ngày (2026-06-27 → 2026-08-01),
   nên hôm nay cửa sổ 6 tuần == toàn bộ lịch sử. Cơ chế cắt cửa sổ đã được test bằng record giả
   timestamp cũ (test `(c)`), nhưng chưa từng cắt dữ liệu thật. Phase 1b3 của `kb_nightly.sh`
   **move** record cũ sang `archive/` chứ không xoá, và script đọc CẢ hai thư mục → khi lịch sử
   dài ra, cửa sổ sẽ hoạt động thật.
2. **Bucket `?`** gộp job đồng bộ và job cũ chưa gắn model/effort. Nhóm này rất lớn
   (`Taylor|?|?` n=400, `Winston|?|?` n=307) và rất nhanh — nhưng nếu sau này `dispatch.sh` bắt
   đầu luôn gắn model/effort thì các bucket `?` sẽ teo dần và tự rơi dưới ngưỡng n=8. Không cần
   làm gì, chỉ cần biết trước.
3. Profile mô tả job ĐÃ XONG bình thường. Job `timeout`/`orphaned`/`usage_limited` bị loại khỏi
   thống kê — đúng ý (không muốn job treo kéo dài median), nhưng nghĩa là profile **không** dự
   báo được job sắp treo. Việc đó là của `jobs.sh` HB_AGE + circuit breaker, không phải file này.
