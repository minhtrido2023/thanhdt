# HYBRID fill-timing — review độc lập theo charter, 2026-08-14

Job `Taylor_20260814_092048` · dispatch Mike: đọc finding gate 11/08 + artifact paper thật, review
độc lập/quant-skeptic theo charter, kết luận READY_FOR_USER_SIGNOFF hay NOT_READY. Không đổi
`fill_timing_live_gate`, không chạm live.

## Kết luận: **NOT_READY** — đúng như charter đã tự đặt ra, chưa đủ dữ liệu theo mốc đã hẹn

Không phải vì phát hiện lỗi mới. Hai nhánh bằng chứng đều đứng vững hơn hôm 08-11, nhưng **điều
kiện định lượng gate 5 mà chính charter/checkpoint 08-11 đặt ra (≥5 phiên BUY hybrid) chưa đạt**:
mới có **2/5** (08-11, 08-13). 3 phiên còn lại theo cron T3/T5: 08-18, 08-20, 08-25.

## 1. Việc mới xảy ra từ checkpoint 08-11 tới nay — đã kiểm lại độc lập, không chỉ tin báo cáo

**(a) Sáng nay (job khác, cùng ngày) landed 1 fix thật lên `main` (commit `6952ed0`, cherry-pick từ
branch `867853b`)**: bật HYBRID trên PAPER (08-10) đã không chạy quét rộng §23 → 5 selfcheck (không
phải 3 như báo cáo đầu) đỏ ngầm 4 ngày vì test giả định trạng thái cấu hình toàn cục (đúng loại lỗi
§23 hệ luận 1). quant-skeptic đã CONFIRMED (medium) độc lập bản vá này, với 2 khuyến nghị còn treo:
tôi tự chạy lại cả hai ngay trong job này (không tin lại báo cáo cũ):

- **Chạy đủ 17 selfcheck phụ thuộc `executor.py`** (bản đồ mới nhất qua `selfcheck_scope_map.sh`,
  tăng từ 13 lên 17 vì có thêm `dynamic_no_chase_ceiling`/`expected_volume_pacing`/
  `plan_check_field_schema` từ các commit khác gần đây) trên **main worktree thật** (không phải
  worktree cụt thiếu `mike/`/`data/` như lần trước) — **17/17 rc=0, 0 dòng FAIL**, gồm cả 3 bộ mà
  báo cáo sáng nay bỏ sót do worktree thiếu file (`book_tagging`, `capit_lever`,
  `dynamic_no_chase_ceiling`) và `hard_no_chase_ceiling` (case bị che bởi HYBRID nuốt lệnh trước
  khi chạm trần giá — nay có nhóm J riêng, có case chứng minh ngược J3/J4).
- **Khuyến nghị còn treo, CHƯA làm** (đúng như quant-skeptic ghi, xác nhận lại bằng grep
  `trading_bot/config.py` hôm nay): **chưa có `fill_timing_hybrid_live_gate` riêng** — HYBRID vẫn
  dùng chung `fill_timing_live_gate` với toàn bộ layer fill-timing. Tắt cổng đó để đổi hành vi
  fill-timing gốc cho LIVE sẽ **vô tình** bật luôn HYBRID cho tiền thật. Đây là việc nên làm **trước
  khi** bất kỳ ai bấm nút live cho fill-timing (không chặn gate paper hiện tại vì
  `fill_timing_live_gate=True` vẫn đang chặn tất).

**(b) Phiên hybrid BUY thứ 2 (08-13) vừa cho bằng chứng thật đầu tiên về TRẢI BLOCK** — điều
checkpoint 08-11 nói còn thiếu ("qty probe 100cp khớp trọn ngay block đầu, chưa chứng minh trải").
Đối chiếu 2 journal thật:

| Phiên | Block 1 (11:00) | Block 2 (11:15) | Trải block? |
|---|---|---|---|
| 08-11 | 4 mã, 100cp/mã, **DONE ngay** ở block 1 | — | Không — mẫu quá nhỏ |
| 08-13 | 6 mã, 100cp/mã | **4/6 mã** (ACB/HDB/HPG/MBB) tiếp tục đặt thêm 100cp, DONE ở 200 | **Có** — 4/6 mã thật sự phải sang block 2 mới khớp đủ |

Đây là bằng chứng cơ chế thật (không phải mô phỏng `FakeBroker`/`paper_rehearsal`), tuy vẫn mới đi
tới block 2/5 — chưa có phiên nào chạm tới block 4-5 (13:00/13:15/13:30) hay yêu cầu spread hết
5 block.

Chiều BÁN: bằng chứng trải-block đã dày hơn từ trước (không phải điểm nghẽn) — phiên 08-12 tự nhiên
đi hết cả 4 block (09:15→10:00), filled_total tăng dần đúng lịch, khớp với thiết kế `_hybrid_block_cap`
+ tự sửa sai khi lỡ khớp không đều giữa các mã.

## 2. Gate cơ học 1-4 (đo lại 08-11) — vẫn đứng, không đo lại từ đầu trong job này

Không có thay đổi cơ chế nào từ 08-11 làm invalid lại gate 1-4 (BUY/SELL window adherence, 0
reject có giải thích, fill vs open ở mức sanity) — số liệu + phương pháp trong
`fill_timing_checkpoint_20260811.md` vẫn là nguồn chuẩn, không cần đo lại vì không có sự kiện mới
nào tác động (không có phiên fail mới, không đổi công thức đo). Việc CẦN đo lại đã đo (bên trên):
sức khoẻ selfcheck + bằng chứng trải-block.

## 3. Vì sao NOT_READY chứ không phải READY_FOR_USER_SIGNOFF

Charter tự đặt ngưỡng ĐỊNH LƯỢNG rõ ràng ngày 08-11 (phương án A, khuyến nghị của chính Taylor,
chưa bị user override): "gom đủ 5 phiên BUY hybrid (08-13, 08-18, 08-20, 08-25) → quant-skeptic
~08-26 → sign-off ~08-27". Phá vỡ mốc này bây giờ (mới 2/5, còn cách gần 2 tuần) mà không có chỉ
đạo mới từ user là tự ý hạ chuẩn đã công bố — đúng loại lỗi §28 (so sánh khi chưa chuẩn hoá ngưỡng)
nếu tôi tự nới. **Không có tín hiệu nào cho thấy nên đổi sang phương án B** (user chưa lên tiếng
chốt sớm).

Không có lỗi cơ chế mới nào cản trở — ngược lại, cả hai việc "nợ" từ checkpoint 08-11 đều đang tiến
triển đúng hướng (selfcheck coverage đã full xanh 17/17; trải-block đã có bằng chứng thật đầu
tiên). Đây là **NOT_READY vì CHƯA ĐỦ THỜI GIAN/MẪU theo đúng kế hoạch đã công bố**, không phải
NOT_READY vì phát hiện rủi ro mới.

## 4. Việc nên làm trước mốc 08-26/08-27 (không chặn, không tự làm trong job này)

1. Thêm `fill_timing_hybrid_live_gate` riêng (khuyến nghị treo từ quant-skeptic sáng nay) — nên
   xong trước ngày sign-off, không phải sau.
2. Không cần hành động gì thêm cho tới 08-18 (phiên hybrid BUY thứ 3) — chỉ theo dõi.
3. `fill_timing_live_gate` vẫn `True` trong suốt review này — không account live nào bị ảnh hưởng
   bởi bất kỳ điều gì trong review.
