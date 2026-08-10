# Audit: bao nhiêu job của Taylor thật sự route được sang `--provider opencode`?

**Job** `Taylor_20260810_063457` · 2026-08-10 · CHỈ ĐỌC, không sửa code/BQ/plan.
**Nguồn**: `mike/bus/jobs/Taylor_*.json` (field `prompt_summary`, `status`, `provider`, `model`,
`started_at`) + mtime của `logfile` làm proxy thời lượng. Cửa sổ: **2026-07-27 → 2026-08-10**,
**163 job**.

## Định nghĩa dùng để phân loại (nói rõ vì nó quyết định con số)
- **(A) có GHI** — sửa code/KB/config, chạy backtest hoặc query BQ mới, sinh/sửa plan, gửi báo cáo
  ra ngoài (email/Discord), commit. → **giữ nguyên `claude`** theo MIKE.md "Bước 1", không đề xuất đổi.
- **(B) chỉ đọc/tổng hợp** — đầu vào là báo cáo/kết luận/log đã có sẵn, đầu ra chỉ là **1 file
  research .md + 1 bus event**, không đụng BQ, không chạm production artifact.
  (Bus event + file research tự nó không tính là "ghi" theo nghĩa rủi ro — nếu tính, nhóm B = 0 và
  câu hỏi vô nghĩa.)

## Kết quả

| Nhóm | Số job | Giờ tính (proxy) | % compute-hour |
|---|---:|---:|---:|
| **A — có ghi (giữ `claude`)** | **144** | 40,48 | **98,1%** |
| **B — chỉ đọc/tổng hợp (ứng viên opencode)** | **11** | 0,74 | **1,8%** |
| ping/echo test (no-op hạ tầng) | 8 | 0,03 | 0,1% |
| **Tổng** | 163 | 41,2 | 100% |

**Ví dụ nhóm B**: `Taylor_20260728_012414` + `_012451` (auto-callback đọc kết quả Wendy/Spyros rồi
tóm tắt), `Taylor_20260802_020316` (auto-callback Winston), `Taylor_20260810_033152` + `_032850`
(relay + xác minh kết quả fix của Mafee qua journal), `Taylor_20260731_154624` (audit đọc log thực
thi CAPIT 07-21), `Taylor_20260810_032034` (trả lời "khi nào chốt được khung giờ vào lệnh"),
`Taylor_20260806_081258` (phản hồi cảnh báo giá cao su), `Taylor_20260803_082241` (job PLAN-ONLY,
đã ghi rõ "KHÔNG chạy backtest/BQ").

**Ví dụ nhóm A** (điển hình, đều là job đắt nhất): `Taylor_20260803_154258` (98 phút, wire CAPIT
margin lever), `Taylor_20260810_024323` (57 phút, fix funding-gate double-count), `_20260809_161845`
(38 phút, sửa `compute_active_nav.py`), `_20260804_080547` (36 phút, gate ADV + backtest),
`_20260802_163657` (39 phút, sửa `rating_8l.py`/`custom_basket.py`).

## Đề xuất: **KHÔNG** tự động route nhóm (B) sang opencode

Ba lý do, theo thứ tự sức nặng:

1. **Tiết kiệm tối đa 1,8% compute-hour** — nằm dưới mức nhiễu của chính phép đo (proxy mtime, job
   timeout/retry). Chi phí xây + bảo trì bộ định tuyến tự động (heuristic phân loại prompt trước khi
   biết job sẽ làm gì) lớn hơn phần tiết kiệm.
2. **Không phân loại được TRƯỚC khi chạy.** 4/11 job nhóm B chỉ *hoá ra* là read-only: chúng bắt đầu
   như "xem cảnh báo/kết quả rồi xử lý" và hoàn toàn có thể rẽ sang sửa code (ca `_20260810_033152`
   suýt phải restart bot; ca `_20260806_081258` là tiền đề của job wire TREND_BREAK hôm sau). Route
   theo prompt = route mù. Đúng tinh thần [[feedback-prefer-natural-observation-over-auto-recovery]]:
   đừng tự động hoá một thứ mà đọc output là thấy.
3. **Nhóm B lệch về việc rẻ nhất, không phải việc lặp nhiều nhất.** Trung vị nhóm B ≈ 190 giây/job;
   nhóm A ≈ 840 giây/job. Cắt nhóm B không chạm được vào phần đuôi dài (5 job dài nhất = 3,7 giờ
   ≈ 9% tổng, tất cả đều là job SỬA CODE production).

**Việc nên làm thay thế** (rẻ hơn, đúng chỗ tốn kém thật): cắt phần lãng phí của nhóm A —
14 job trong cửa sổ này ở trạng thái `failed`/`timeout`/`maxturns_pending`/`aborted`, trong đó
**7 job phải re-dispatch làm lại từ đầu** vì hết `--max-turns`/timeout (ví dụ chuỗi
`_20260731_085810`→`_094324`, `_20260802_141725`→`_150945`, `_20260808_075933`→`_075939`,
`_20260809_150316`→`_161845`). Đó là compute trả 2 lần cho cùng 1 việc, quy mô lớn hơn hẳn 1,8%.

**Nếu vẫn muốn dùng opencode**: dùng **thủ công tại điểm dispatch** — Mike (hoặc tôi) thêm
`--provider opencode` cho đúng loại "đọc file X, tóm tắt lại", không xây tầng route tự động.

*Giới hạn của số liệu*: thời lượng là **proxy** (mtime logfile − `started_at`), không phải token
thật; nó ước lượng wall-clock chứ không phải chi phí. Xếp hạng A≫B thì vững, còn con số 1,8%
nên đọc là "cỡ vài phần trăm", không phải số đo chính xác.
