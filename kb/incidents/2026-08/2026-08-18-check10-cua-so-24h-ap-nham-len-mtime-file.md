# 2026-08-18 — check #10 báo "TIN NHẮN ĐÃ BỊ NUỐT trong 24h qua" bằng một lỗi 6 ngày trước

**Triệu chứng.** `ops_health_check.sh --account SpaceX` 02:58 ICT in:
`⚠️ [WARN-ONLY] notify_thread.sh có lỗi gửi Discord trong 24h qua — TIN NHẮN ĐÃ BỊ NUỐT.
Dòng cuối: 2026-08-12T18:46:56+07:00 ...`. Mốc trong chính câu báo động là **6 ngày trước**,
không phải trong 24h — nhưng không ai đọc kỹ tới đó, và dispatch ops-autofix vẫn nổ.

**Root cause.** `logs/notify_thread_errors.log` là file **append-only, không xoay vòng**. Check
#10 lọc cửa sổ 24h bằng **mtime của FILE**, rồi đọc **TOÀN BỘ lịch sử** bản ghi bên trong. Ngày
2026-08-17T19:31 có một bản ghi loại `DA TU SUA VA GUI` (caller đảo thứ tự đối số, script tự sửa,
**tin ĐÃ đến nơi**) được ghi vào ⇒ file "tươi" ⇒ check quét cả file ⇒ vớ phải lỗi thật ngày 08-12
(đã xử lý xong) và báo như thể vừa xảy ra.

Hai hệ quả, cái thứ hai nặng hơn:
1. Sai sự kiện + sai mốc thời gian.
2. Nhánh `_nte_hard` **che mất** kết luận ĐÚNG của bản ghi mới. Bản ghi 08-17 nói "KHÔNG mất
   tin"; báo cáo lại nói "TIN NHẮN ĐÃ BỊ NUỐT" — đúng cái lỗi mà vòng sửa 2026-08-16
   (arch-review coord-2026-08-12 required_change #3) đã sửa cho ca *cùng-thời-điểm*, nhưng
   không phủ ca *khác-thời-điểm*.

**Fix** (`bin/ops_health_check.sh`, khối `CHECK10_BEGIN/END`): cửa sổ 24h áp lên **TỪNG BẢN GHI**
(parse timestamp đầu dòng), mtime file chỉ còn là bộ lọc thô rẻ tiền. Bản ghi không parse được
timestamp thì **GIỮ** (fail-loud — không loại được khả năng nó vừa xảy ra). Tách rõ 2 ca từng bị
gộp: "có bản ghi nhưng đều cũ >24h" ⇒ **OK thật**; "file tươi mà không có bản ghi nào có
timestamp" ⇒ vẫn WARN "không kết luận được".

**Verify.** `ops_health_check_selfcheck.py`: 2 ca hồi quy MỚI —
`case_c10_old_hard_error_not_reported_as_recent` (tái hiện đúng ca hôm nay: lỗi thật cũ + bản ghi
tự-sửa mới ⇒ KHÔNG được nói "BỊ NUỐT") và `case_c10_fresh_file_all_records_old_is_ok`. Toàn bộ
assertion PASS dưới `env -u TZ`, `TZ=America/New_York`, `TZ=UTC` (§16/§19). Chạy lại checker
thật: dòng báo động đổi thành *"1 call site ĐẢO THỨ TỰ đối số — tin ĐÃ ĐƯỢC GỬI, KHÔNG mất tin"*,
kết luận **4 → 3 điểm cần chú ý**.

**Hệ luận đã sửa luôn (coding_guidelines §23 hệ luận 1).** Fixture của các ca c10 cũ ghi **ngày
cứng** (`2026-08-02`, `2026-08-16`). Cửa sổ 24h nay áp lên từng bản ghi ⇒ những ngày cứng đó sẽ
tụt ra ngoài cửa sổ vài ngày sau khi viết và ca test **lặng lẽ đổi nghĩa** thay vì đỏ. Đã đổi sang
`_nte_ts(hours_ago)` sinh timestamp tương đối `now`.

**Bài học (thuộc họ `coding_guidelines` §28).** *mtime của một file append-only trả lời câu "có ai
vừa ghi không", KHÔNG trả lời "bản ghi nào mới".* Checker nào lọc thời gian bằng mtime rồi đọc cả
file là đang trộn hai câu hỏi đó — và vì file chỉ dài thêm, nó **hỏng dần theo thời gian**: càng
nhiều lịch sử thì xác suất vớ nhầm càng cao. Lọc thời gian phải áp lên đơn vị mình đang kết luận
(bản ghi), không lên vật chứa (file).

**Trạng thái commit — CHƯA COMMIT, cố ý.** `bin/ops_health_check.sh` và
`bin/ops_health_check_selfcheck.py` tại thời điểm sửa **đã mang sẵn thay đổi chưa commit của một
phiên khác** (khối check #12 ccdb-wakeup, không có trong HEAD `1dbf866e`), và hunk đăng ký ca test
là hunk TRỘN cả hai bên. Theo quy tắc 2b (sự cố thật 2026-08-02: 2 job Wags cùng sửa file này),
Winston **không** `git add` file mang việc dở của người khác. Bản vá **đã có hiệu lực vận hành
ngay** (cron đọc file trong worktree, không đọc git). Chủ phiên kia commit là gộp luôn.
