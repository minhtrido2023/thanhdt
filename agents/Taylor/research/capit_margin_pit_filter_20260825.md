# PIT filter Loại 1/Loại 2 cho `capit_margin_lever` (2026-08-25)

**Job** `Taylor_20260825_042209` · Kế tiếp `macro-margin-review_20260825.md` (job `_040602`).
**Trạng thái**: implement XONG, wire vào code THẬT (đang LIVE-armed, xem cảnh báo ⚠️ cuối file).

## Bước 1 — Nguồn PIT thực tế: KHÔNG đầy đủ, nhưng đủ để thêm lớp phòng thủ

Kiểm cả 2 candidate của dispatch bằng cách đọc source thật, không đoán:

- **CPI YoY** (`cpi_vn.py`): Tier-1 THẬT (NSO) chỉ phủ **13 tháng rolling gần nhất** (hiện
  2025-06→2026-06). Tier-2 PROXY (nội suy tuyến tính giữa anchor) phủ **2011-01→2025-05**.
  **KHÔNG có anchor nào trước 2011-01.**
- **Lãi suất huy động Big-4 12M** (`deposit_rate_vn.py`): 26 mốc **frozen retroactive, hiệu
  chỉnh 1 LẦN DUY NHẤT ngày 2026-06-19** — registry của chính nó ghi rõ "KHÔNG phải point-in-
  time thật cho quá khứ". Anchor sớm nhất cũng là **2011-01-01**. Chỉ phần thêm mới từ
  2026-07-17 (live-refresh CSV) là PIT thật.
- **Kết luận Bước 1**: không nguồn nào đủ tiêu chuẩn PIT nghiêm ngặt cho backtest 2000-2026.
  NHƯNG cả hai đã là **CANONICAL-PROXY dùng sống trong production khác** (`rating_8l.py` đọc
  `deposit_rate_vn.py` mỗi ngày). Quyết định: dùng lại đúng 2 nguồn này cho bộ lọc — cùng
  chuẩn tin cậy hệ thống đã chấp nhận, KHÔNG tự chế chỉ báo mới, và **báo rõ giới hạn** thay vì
  im lặng dùng như đã verify đầy đủ.

## Bước 2 — Thiết kế + test thực nghiệm trên dữ liệu SẴN CÓ (2011-2026)

Tính lại 20 cluster dd52≤−20% trực tiếp từ `data/VNINDEX.csv` (rolling 252 phiên, gộp gap≤30
phiên — đúng quy ước washout của `pt_v23_audit_2014.py`), rồi merge_asof-backward CPI YoY +
lãi suất huy động tại NGÀY cluster BẮT ĐẦU:

| Cluster (bắt đầu) | Loại (Bobby) | CPI YoY | Deposit rate |
|---|---|---:|---:|
| 2007-04-23 … 2010-11-24 (6 cluster) | Loại 1 | **KHÔNG CÓ DỮ LIỆU** | KHÔNG CÓ DỮ LIỆU |
| 2011-05-23 | Loại 1 | 18,85% | 14,00% |
| 2011-07-12 | Loại 1 | 21,60% | 14,00% |
| 2011-10-05 | Loại 1 | 20,55% | 14,00% |
| 2012-08-27 | Loại 1 (đuôi) | 6,87% | 12,00% |
| 2018-05-28 / 2018-10-11 | Loại 2 | 4,34% / 3,57% | 6,80% / 6,80% |
| 2020-03-11 / 2020-07-27 | Loại 2 | 5,14% / 2,71% | 6,50% / 5,70% |
| 2022-05-13 / 2022-09-19 | Loại 2 | 3,09% / 3,98% | 5,50% / 5,50% |

**Khoảng trống sạch, không chồng lấn**: CPI Loại-2-max 5,14% ↔ Loại-1-min-đo-được 6,87%
(khoảng trống 1,73pp); deposit Loại-2-max 6,80% ↔ Loại-1-min-đo-được 12,00% (khoảng trống
5,2pp). Ngưỡng chọn = điểm giữa: **CPI ≥ 6,0%** (giữa 5,14/6,87) và **deposit ≥ 9,0%** (giữa
6,80/12,00), OR-logic. Trên tập 10 cluster CÓ dữ liệu (4 Loại-1 + 6 Loại-2): **phân tách
đúng 10/10**, kể cả ca biên 2012-08-27 (CPI 6,87% chỉ cách ngưỡng 0,87pp — vẫn đúng phía).

**⚠️ Giới hạn PHẢI mang theo — không phải chi tiết phụ**: 6/10 cluster con của Loại 1
(2007-04→2010-11, GỒM ĐÁY SÂU NHẤT lịch sử VNINDEX −71,0% năm 2008-2009) **hoàn toàn không
kiểm được** vì zero dữ liệu. Ngưỡng trên là điểm giữa thực nghiệm của N=4 (Loại 1) vs N=6
(Loại 2) — **KHÔNG phải một backtest đã xác nhận trên toàn bộ Loại 1**, chỉ là bằng chứng
định hướng trên phần đuôi muộn của mega-crisis + toàn bộ Loại 2. Filter này là **lớp phòng
thủ THÊM** (đúng tinh thần DT5G macro gate — "chốt rủi ro fail-safe, không phải công cụ tăng
lợi nhuận"), không phải luật đã chứng minh sẽ chặn được ngày ĐẦU của một khủng hoảng cơ cấu
mới bùng phát kiểu 2007 (CPI/lãi suất khi đó còn chưa kịp leo cao).

## Bước 2b — Bug phát hiện thêm: blind-spot ngoại suy CPI cho ngày TƯƠNG LAI

Đo thử `LATEST = hôm nay (2026-08-25)`: `cpi_vn.merge_cpi()` trả **3,40%** — nhưng tháng NSO
THẬT gần nhất (2026-06) là **4,69%**, với xu hướng 3 tháng trước đó leo 4,65→5,60→4,69%.
Nguyên nhân: nội suy Tier-2 chỉ có anchor tới 2025-05 (3,4%); ngoài cửa sổ NSO Tier-1 rolling
13 tháng, hàm forward-fill từ anchor Tier-2 CŨ đó thay vì tiếp tục từ số THẬT gần nhất — im
lặng, không NaN, không cảnh báo. Với **CỔNG CHẶN VAY**, đánh giá THẤP CPI là sai chiều
fail-safe (có thể để lọt một giai đoạn CPI đang thực sự leo cao). **Đã vá NGAY TRONG bộ lọc
của job này** (KHÔNG sửa `cpi_vn.py` — module dùng chung, ngoài phạm vi): lấy
`MAX(giá trị nội suy, số NSO thật gần nhất)` khi ngày hỏi đã qua tháng NSO thật cuối cùng.
Xác minh: floor đưa 3,40%→4,69% cho ngày 2026-08-25. **Cần báo cho ai sở hữu `cpi_vn.py`**
(refresh routine hiện "CHƯA có cron tự động" theo registry của chính nó) — đây là dạng lỗi
staleness-im-lặng CÙNG HỌ với caveat (a) đã ghi trong `kb/data_registry/macro/cpi_vn.md`,
chỉ khác vị trí (ngoại suy TƯƠNG LAI thay vì cửa sổ rolling trôi).

## Bước 3 — Implement

**Vị trí DUY NHẤT**: `deploy_golive_dt5g_v4/golive_recommend_v23.py`, bên trong khối
`# CAPIT_LEVER_BEGIN … # CAPIT_LEVER_END` (đoạn `capit_lever_selfcheck.py` trích nguyên văn
để test) — đúng nguyên tắc "ĐÚNG MỘT CHỖ" đã có sẵn của toàn bộ cơ chế lever. KHÔNG đụng
`trading_bot/plan.py::apply_capit_lever()` — nó chỉ đọc `capit_lever.active` từ artifact, và
`active=False` (do PIT chặn) đã tự động chảy đúng qua toàn bộ cascade GỠ đòn bẩy hiện có,
không cần sửa gì thêm ở tầng thực thi.

- 2 hằng số mới (git-tracked, cùng khuôn `CAPIT_LEVER_DD52_*`): `CAPIT_LEVER_PIT_CPI_THRESHOLD
  = 6.0`, `CAPIT_LEVER_PIT_DEPOSIT_THRESHOLD = 9.0`.
- **CỐ Ý KHÔNG thêm field vào `trading_rules.json`** — file đó khớp `.gitignore` (`*.json`),
  không diff/blame/review được; đúng lý do `capit_lever_policy()` đã ghim `CAPIT_LEVER_APPROVED_*`
  trong code thay vì JSON (comment sẵn có trong file, dòng ~483-491). Ngưỡng PIT là tham số
  quyết định vay tiền — cùng loại "phạm vi đã duyệt" đó, đi theo đúng khuôn.
- `_lever_active` giờ thêm điều kiện `and not _pit_structural`. `capit_lever` dict artifact
  thêm 6 field mới: `pit_filter_structural`, `pit_filter_reason`, `pit_cpi_yoy`,
  `pit_deposit_rate`, `pit_cpi_threshold`, `pit_deposit_threshold` — luôn công bố (kể cả ngày
  filter không chặn gì) để quan sát được liên tục, không chỉ lúc fire.
  NaN được chuẩn hoá về `None` trước khi vào dict (khớp quy ước `dd52_pct` sẵn có, tránh literal
  `NaN` phi-JSON lọt vào artifact).
- Fail-closed đầy đủ: lỗi đọc CPI/deposit (exception) hoặc NaN (ngoài phạm vi dữ liệu) ⇒ coi
  NHƯ Loại 1 ⇒ KHÔNG áp đòn bẩy — không đoán "chắc an toàn" khi thiếu thông tin.

## Bước 4 — Selfcheck + verify

Mở rộng `capit_lever_selfcheck.py::run_block()` thêm tham số `latest` (mặc định 2019-06-01 —
ngày PIT-pass, giữ nguyên MỌI ca B1-B10 cũ không bị ảnh hưởng). Thêm section **B-PIT** (6 ca
mới, B11/B11b/B11c/B12/B12b/B13/B14), dùng **NGÀY THẬT** (không mock giá trị CPI/deposit) để
chạy đúng `cpi_vn.py`/`deposit_rate_vn.py` thật — giống triết lý B1-B10 chạy đúng §6a thật:

- B11: 2011-07-15 (Loại 1 thật, CPI ~21,6%) → `active=False`, `pit_filter_structural=True`.
- B11c: 2012-08-27 (ca BIÊN, CPI ~6,87% chỉ cách ngưỡng 0,87pp) → vẫn chặn đúng.
- B12: 2022-06-01 (Loại 2 thật, giữa episode SCB, CPI ~3,4%) → `active=True`, PIT cho qua.
- B13: 2008-09-01 (trước 2011, đáy sâu nhất, dd52 thật −71,0%) → NaN → fail-closed, chặn.
- B14: fixture mặc định (không PIT date) → xác nhận PIT-pass, bảo vệ B1-B10 khỏi hồi quy im lặng.

**Kết quả chạy** (`env -u TZ python3 capit_lever_selfcheck.py`, cũng chạy lại dưới
`TZ=America/New_York` — không có phụ thuộc timezone trong code mới vì `LATEST` luôn được
truyền vào, không đọc đồng hồ hệ thống): **193 PASS / 5 FAIL**. Xác nhận bằng `git stash` +
chạy lại trên code TRƯỚC khi sửa: **CHÍNH XÁC 5 FAIL đó đã tồn tại từ trước** (A7, C20, G1,
L2, L3 — tất cả vì `data/trading_rules.json` thật hiện `capit_margin_lever.enabled=true`
trong khi các ca kiểm này giả định `enabled=false`; xem cảnh báo dưới). **0 selfcheck mới bị
fail, 6/6 ca B-PIT mới PASS.**

`bin/selfcheck_scope_map.sh deploy_golive_dt5g_v4/golive_recommend_v23.py` trả rỗng — không
phải vì không ai phụ thuộc, mà vì phụ thuộc thật (`capit_lever_selfcheck.py`) đi qua trích
nguồn AST/text (`extract_marked`/`extract_func`), không phải `import` (đúng khe mù §23 "module
có consumer gián tiếp"). Selfcheck liên quan DUY NHẤT đã chạy + xanh ở trên.

## ⚠️ Hai điều Mike/user cần biết trước khi coi task này "chỉ thêm filter thụ động"

1. **`capit_margin_lever.enabled` đã là `true`** (user xác nhận 2026-08-22, thread
   1521735922066919515) — KHÔNG phải `false` như dispatch giả định. Filter này vì vậy có tác
   dụng NGAY trên lần chạy `golive_recommend_v23.py` production tiếp theo (mỗi khi dd52 đạt
   cổng), không phải một bổ sung nằm chờ. Tác động vận hành hiện tại = 0 vì dd52 hôm nay còn
   rất xa −20%, nhưng đây không còn là thay đổi "dormant" như khung dispatch mô tả.
2. **5 selfcheck fail baseline (A7/C20/G1/L2/L3) đã lỗi thời từ trước job này** — giả định
   `enabled=false` không còn đúng với production. Đây KHÔNG phải lỗi do job này gây ra (xác
   nhận bisect), nhưng vẫn treo mở: `python capit_lever_selfcheck.py` sẽ tiếp tục báo đỏ
   (exit 1) cho tới khi có ai quyết định cập nhật lại 5 assertion đó cho khớp trạng thái LIVE
   hiện tại — quyết định đó KHÔNG thuộc phạm vi job này (đụng vào cổng chấp thuận, cần chủ ý
   riêng), chỉ báo lại để không ai tưởng nhầm exit=1 là do PIT filter.

## Việc CHƯA làm (đúng phạm vi dispatch)

- KHÔNG bật `enabled` (giữ nguyên trạng thái đọc từ JSON, không đụng).
- KHÔNG làm due-diligence audit-opinion-ngoại-trừ cho discretionary sleeve (dispatch nói rõ
  quy tắc "audit ngoại trừ = chặn margin" đã được cover bởi diện cảnh báo hiện có, không cần
  làm thêm ở job này).
