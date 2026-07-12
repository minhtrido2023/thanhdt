
## 2026-07-12 — Audit cron-order (Winston_20260712_142100) bắt 2 bug production-blocking
## cùng lúc: C1 CRITICAL publish DT5G qua cache T-1 thay vì live, H2 HIGH freshness-check
## miscalibrated

**Hiện tượng:** user yêu cầu Mike rà lại thứ tự ~45+ dòng cron. Dispatch Winston (fable)
audit toàn bộ → thứ tự ĐÚNG, nhưng lộ ra 2 bug NỘI DUNG khẩn cấp, cả 2 sẽ tự kích hoạt
trong tuần từ hành động KHÔNG LIÊN QUAN đã làm ngày hôm trước (siết `MAX_STATE_LAG=0`
07-11):

- **C1 CRITICAL** — `deploy_golive_dt5g_v4/publish_gated_state.py` đọc DT5G base qua
  `BQ_LOCAL_CACHE` (luôn T-1, do `wc_env.sh` export biến này toàn cục) thay vì BigQuery
  live, dù comment trong script tự khai "SOURCE OF TRUTH = BigQuery... NOT a local CSV" —
  ý định đúng, code không enforce. Với `MAX_STATE_LAG=0` (mới siết hôm trước), thứ Hai
  07-13 19:00 ICT sẽ FAIL cứng, chặn luôn dispatch DollarBill lập plan T+1 (thứ Ba
  07-14 không có plan).
- **H2 HIGH** — check `shares_outstanding_live` giả định có 1 writer cập nhật
  `updated_at` hàng ngày, nhưng cron thực tế chỉ chạy `--scan` (detection-only, không ghi
  `updated_at`) → check tự BLOCK giả ~thứ Tư 07-15 dù dữ liệu không hề stale thật.

**Root cause C1:** biến môi trường cache được thiết kế cho mọi script MUỐN cache (đa số
script research/backtest) bị kế thừa vô điều kiện vào publish script — script duy nhất
BẮT BUỘC phải đọc live vì nó chính là nguồn công bố cho các consumer khác. Không có bước
nào từng kiểm tra lại "publish script có thực sự đọc live không" cho tới khi ngưỡng gate
bị siết đủ chặt (0 ngày) để biến sai lệch tiềm ẩn (T-1 vs T) thành fail cứng.

**Fix C1:** `os.environ.pop('BQ_LOCAL_CACHE', None)` process-local ngay trước import
`macro_state_live` (commit `4995262`, repo WorkingClaude). Lưu ý vận hành: 2 lần dispatch
Taylor để fix đều timeout (tự mở rộng phạm vi sang backfill C1b không cần thiết) — Mike
tự đọc code, tự sửa, tự commit, rồi dispatch quant-skeptic bằng `--claim` (không có finding
event chính thức từ Taylor vì job không hoàn tất). **quant-skeptic CONFIRMED** (high
confidence, tự tái lập cơ chế bằng Python replica độc lập: pop env → cache branch bypass →
live path; xác nhận process-local, không leak sang sibling process; 1 ghi chú tùy chọn về
`LOCAL_SNAPSHOT_DIR` — hiện vô hại vì biến chưa từng được export).

**Fix H2:** đổi từ BLOCK → WARN cho check `shares_outstanding_live` (commit `6459b6d`,
repo mike, `bin/bq_freshness_check.sh`) — job `Winston_20260712_155038`. **quant-skeptic
CONFIRMED** (3 lần verify độc lập qua `--claim`, chạy `freshness_ops_selfcheck.py` 42/45 —
3 FAIL còn lại đến từ probe khác mới thêm cùng ngày, không liên quan H2).

**Verify:** cả 2 fix đã qua quant-skeptic CONFIRMED trong ngày; còn 3 mục chờ xác nhận
qua lần chạy cron thật thứ Hai 07-13 18:30/19:00 ICT (đã ghi ở `kb/current_ops.md`, không
lặp lại ở đây).

**Bài học:** một publish/production script đọc input qua bất kỳ biến env cache nào kế
thừa từ script dùng chung (`wc_env.sh`) là rủi ro tiềm ẩn — không lộ ra cho tới khi có 1
thay đổi KHÔNG LIÊN QUAN (siết gate) biến nó thành fail cứng. `coding_guidelines.md` §11
đã được thêm cùng ngày để bắt buộc tra `kb/cron_registry.md` (đọc gì+vintage) trước khi
đổi lịch/ngưỡng cron.

## 2026-07-12 — Audit sẵn sàng BCTC Q2/2026 bắt LAG live-candidate pipeline mù sự kiện
## mới <30 phiên (R1 CRITICAL) + freshness ticker_financial bị 1 mã early-filer reset
## đồng hồ cả bảng (F1 MEDIUM)

**Hiện tượng:** user yêu cầu rà soát sau khi phát hiện MBS đã công bố BCTC Q2 (08/07) —
xác nhận mùa Q2 đã bắt đầu thật. Dispatch song song Taylor (góc tín hiệu) + Winston (góc
hạ tầng).

- **R1 CRITICAL (Taylor_20260712_121642)** — sổ LAG (PEAD, 50-65% NAV khi active) tính
  candidate LIVE từ nguồn không biết sự kiện BCTC mới <30 phiên, trong khi entry thật là
  T+5 — nghĩa là **100% entry LAG mùa Q2 sẽ bị bỏ lỡ trong im lặng** nếu không sửa trước
  khi mùa cao điểm tới (~cuối 07).
- **F1 MEDIUM (Winston_20260712_122313)** — freshness-check `ticker_financial` đo bằng
  `MAX(time)` toàn bảng; 1 mã early-filer (MBS) đủ để cả check báo "xanh" dù 1254/1255 mã
  còn lại chưa công bố gì — nguy cơ vendor stall giữa mùa im lặng tới 90 ngày mà không ai
  biết.

**Fix R1:** module mới `lag_live_schedule.py` (commit `f7463e3`, repo WorkingClaude) tách
nguồn — identity/NP_R từ pkl fresh-daily (biết ngay tại ngày release), điều kiện phụ vẫn
từ CSV cũ (luôn đủ dữ liệu vì nhìn về quá khứ). Backtest pin R3 byte-identical (không đổi
số). Bonus: fix còn dọn thêm 1 look-ahead 30-phiên ẩn khác trong logic cũ (sibling cùng
ngày dùng giá trị tương lai) mà không ai từng phát hiện trước đó.

**Fix F1:** breadth-probe WARN-only theo mùa BCTC vào `bq_freshness_check.sh` (commit
`1b2fd13`, repo mike, job `Winston_20260712_124928`) — đếm `COUNT(DISTINCT ticker)` của
quý vừa kết thúc, WARN nếu đứng yên ≥5 ngày trong cửa sổ mùa, có guard chống false-positive
đầu/cuối mùa.

**Review vòng 2 (Spyros/risk-auditor, job `Spyros_20260712_131501`) phát hiện thêm 3 mục
nhỏ, cả 3 đã xử lý trong ngày:**
- M1 MEDIUM: field `lag_source_error` mới trong `golive_v23_status.json` (commit
  `a5f3810`) phân biệt "0 upcoming vì thật không có gì" vs "0 vì pkl lỗi" + probe
  `lag-pkl` WARN-only (commit `f84b995`, dùng stateful catch-up để tránh báo giả lệch giờ
  refresh).
- L2 LOW: nhãn "Đã vào"/`ENTERED` đổi thành "Cửa sổ entry đã qua — đối chiếu vị thế thực"/
  `WINDOW_PASSED` (commit `853080d`), tránh DollarBill hiểu nhầm đã có vị thế.
- L1 LOW: không cần code, chỉ document — quant-skeptic tự tái hiện được đúng lỗi pandas
  hệ thống không đọc được pkl format mới khi verify, xác nhận cảnh báo có căn cứ thật.

**Verify:** quant-skeptic CONFIRMED cho cả R1 fix và bộ fix M1/L2 (2 lần verify độc lập,
job `Taylor_20260712_135148` gộp cả 2). Spyros/risk-auditor review vòng 2 xác nhận KHÔNG
có rủi ro chặn còn lại.

**Bài học:** một pipeline "as-of correct" (không look-ahead) vẫn có thể bị **BLIND** với
dữ liệu vừa xuất hiện nếu nguồn phụ dùng cửa sổ lookback cố định (30 phiên) không tính
tới trường hợp sự kiện MỚI xảy ra bên trong cửa sổ đó — khác hẳn look-ahead (nhìn tương
lai), đây là "nhìn quá khứ nhưng khoảng nhìn quá hẹp cho case biên mùa vụ". Audit chủ động
TRƯỚC mùa cao điểm (thay vì đợi entry đầu tiên fail rồi mới điều tra) là điều làm đúng ở
đây — không có thiệt hại thật nào xảy ra.

## 2026-07-12 — `lag_edge_health.csv`: 2 tiền đề sai liên tiếp về "bug staleness/catch-up"
## bị bác bỏ sau điều tra sâu — không có bug thật, tốn 2 chu kỳ dispatch để xác nhận

**Hiện tượng:** trong ngày, `lag_edge_health.csv` (file tracking hiệu suất lịch sử LAG,
dùng để tính `mean12` cho allocator w_LAG) bị nghi ngờ có bug/staleness **2 lần độc lập**,
mỗi lần dẫn tới 1 dispatch "hãy sửa" trước khi có ai verify premise là đúng hay sai:

- **Tiền đề #1 (nguồn: dispatch ban đầu của Mike, KHÔNG verify trước)** — "không có lịch
  refresh tự động" cho file này. Dispatch Winston điều tra/sửa (`Winston_20260712_114800`)
  → **SAI**: `edge_health_monitor.py --refresh` đã là step [22] của `papertrade_daily.sh`,
  cron `30 8 * * 1-5` (15:30 ICT), chạy `[ok]` mọi ngày giao dịch, gần nhất 07-10. Data
  dừng ở 2026-05-11 là **hành vi ĐÚNG** — hết mùa BCTC Q1 (hạn nộp 30/04, entry hợp lệ
  cuối = release+5+25 phiên hold = 05-11), không phải thiếu refresh. Winston tự chạy thật
  `--refresh` bằng đúng env production để verify độc lập (CSV rewrite, nội dung
  byte-identical — đúng kỳ vọng không có event mới).
- **Tiền đề #2 (nguồn: chính audit `Winston_20260712_151206`, phát hiện phụ "F2" trong
  lúc dọn cron paper-trading)** — "cron có nhưng `--refresh` không catch-up chuỗi LAG
  edge, bug nằm TRONG script". Dispatch Taylor điều tra/sửa (`Taylor_20260712_155038`) →
  **CŨNG SAI**: `lag_edge_health()` chạy VÔ ĐIỀU KIỆN mỗi lần invoke (không phụ thuộc flag
  `--refresh`, chỉ ảnh hưởng `edge_panel.csv` khác), rebuild toàn bộ series từ cache
  daily-refreshed mỗi lần chạy. BQ live xác nhận **zero** sự kiện NP_R từ 05-05→07-07
  (khoảng trống thật giữa 2 mùa BCTC). Taylor báo cáo lại premise sai thay vì tự mở rộng
  sửa code (đúng kỷ luật `verify_finding.sh`/dispatch instruction #6) — **KHÔNG sửa code
  nào**.

**Kết luận cuối cùng:** verdict TROUGH hiện tại (mean12 +0.45%, n=631) là số đúng và tươi
nhất có thể có — không có gap production nào ở đây. Probe WARN-only mtime-check (commit
`f67e09a`, ra đời từ tiền đề #1, vẫn giữ vì bản thân nó vô hại và đúng đắn — cảnh báo khi
mtime quá cũ so ngưỡng) không liên quan gì tới 2 lần nhầm lẫn content này.

**Root cause (cả 2 lần):** một CLAIM về hành vi thực tế của 1 script/pipeline ("không có
refresh", "refresh không catch-up") được đưa vào dispatch dưới dạng tiền đề ĐÃ XÁC NHẬN,
trong khi thực ra chỉ là suy luận từ triệu chứng bề mặt (file dừng ở 1 ngày cũ trông giống
"stale"; tên flag `--refresh` gợi ý nó phải catch-up mọi thứ) — không ai đọc code thực thi
+ đối chiếu BQ ground-truth TRƯỚC khi dispatch "đi sửa". Cả 2 lần chỉ được bác bỏ khi
người nhận dispatch (Winston lần 1, Taylor lần 2) tự đọc code + tự verify độc lập thay vì
tin tiền đề và bắt đầu sửa ngay.

**Bài học:** đây là biến thể MỚI của nguyên tắc "trust the artifact, not self-report"
(MIKE.md #2) — không phải áp dụng cho TRẠNG THÁI JOB (đã biết, đã có cơ chế) mà cho
**CLAIM CHẨN ĐOÁN** ("có bug ở đây") được truyền xuống dispatch tiếp theo dưới dạng tiền
đề. Điểm tích cực: cả 2 lần agent nhận việc đều làm ĐÚNG — không âm thầm "sửa cho khớp
tiền đề", mà tự verify trước, phát hiện premise sai, báo cáo lại thay vì mở rộng phạm vi
tự chế ra 1 bug để sửa. Cái tốn kém duy nhất là 2 chu kỳ dispatch (khoảng 20-45 phút mỗi
lần) — không có rủi ro production nào phát sinh vì không code nào bị sửa sai.

## RETRO — 2026-07-12: 3 sự cố (2 bug thật production-blocking đã tự bắt+tự sửa trước khi
## gây hại, 1 chuỗi tiền đề chẩn đoán sai không gây hại nhưng tốn 2 chu kỳ dispatch), 1
## pattern xuyên suốt MỚI

**Bối cảnh ngày:** 2026-07-12 là ngày R&D rất nặng (momentum-deals đóng hoàn toàn +
production change, V2.5 lever NO-GO, Q-sleeve NO-GO, DVR-8L context — tất cả đã có entry
riêng ở `kb/current_ops.md`, không phải "sự cố") xen giữa 2 audit chủ động theo yêu cầu
user: (1) rà cron-order toàn hệ thống, (2) rà sẵn sàng mùa BCTC Q2/2026. Cả 2 audit đều
**tìm ra bug thật trước khi nó gây hại** — đúng đích của việc audit chủ động — và cả 2 đều
fix + verify (quant-skeptic CONFIRMED) trong cùng ngày.

| # | Sự cố | Phân loại | Nguồn gốc (bước/quy trình, không quy tội cá nhân) | Người ghi chép |
|---|---|---|---|---|
| 1 | C1 CRITICAL: `publish_gated_state.py` đọc DT5G qua `BQ_LOCAL_CACHE` (T-1) thay vì live BQ — sẽ FAIL cứng 19:00 thứ Hai 07-13, chặn dispatch DollarBill | data-registry-accuracy | Publish script kế thừa vô điều kiện biến cache toàn cục (`wc_env.sh`) thiết kế cho script research/backtest muốn cache — không có bước nào từng xác nhận "publish script có thực đọc live không" tách biệt khỏi mọi script khác; bug tiềm ẩn ~2.5 tuần, chỉ lộ khi 1 thay đổi KHÔNG LIÊN QUAN (siết `MAX_STATE_LAG=0`, 07-11) biến sai lệch T-1/T ẩn thành fail cứng | Chưa ai ghi trước retro này — bus event `error` do Winston tự `append_event.sh` lúc audit (job `Winston_20260712_142100`, 14:43:01), fix+verify đã lên bus (Taylor finding job `Taylor_20260712_151135` không hoàn tất do timeout, Mike tự dispatch quant-skeptic `--claim` thay); retro tự bổ sung thành entry đầy đủ |
| 2 | H2 HIGH: `shares_outstanding_live` freshness check giả định daily writer không tồn tại — sẽ false-BLOCK ~thứ Tư 07-15 | data-registry-accuracy | Bước viết freshness check giả định hành vi cron (daily `updated_at` write) mà không đối chiếu lại crontab thật tại thời điểm viết — cron thực tế chỉ `--scan` detection-only | Chưa ai ghi trước retro này — bus finding do Winston tự ghi (job `Winston_20260712_155038`, 15:56:47); retro tự bổ sung |
| 3 | R1 CRITICAL + F1 MEDIUM: LAG live-candidate pipeline mù sự kiện BCTC <30 phiên (100% entry Q2 sẽ miss) + freshness `ticker_financial` bị 1 mã early-filer reset đồng hồ cả bảng | data-registry-accuracy | Cả 2: thiết kế lookback cố định (30 phiên / `MAX(time)` toàn bảng) không tính trường hợp biên mùa vụ (sự kiện MỚI xuất hiện trong cửa sổ, hoặc 1 mã report sớm hơn 1254 mã còn lại) — gap kiến trúc từ lúc viết ban đầu, chỉ lộ khi mùa BCTC Q2 thật sự bắt đầu (MBS 08/07) | Chưa ai ghi trước retro này — bus finding Taylor (`Taylor_20260712_121642`, R1) + Winston (`Winston_20260712_122313`, F1) tự ghi lúc audit; fix verify qua job `Taylor_20260712_135148` (gộp cả R1 + M1/L2 residuals của Spyros); retro tự bổ sung |
| 4 | `lag_edge_health.csv`: 2 tiền đề chẩn đoán sai liên tiếp ("không có refresh" rồi "refresh không catch-up") — không có bug thật, tốn 2 chu kỳ dispatch để bác bỏ | audit-claim-accuracy (mới, chưa có trong danh sách nhóm cũ) | Lần 1: dispatch ban đầu của Mike đưa 1 claim CHƯA VERIFY vào làm tiền đề dispatch. Lần 2: chính audit `Winston_20260712_151206` tự sinh ra 1 claim MỚI (khác lần 1) từ suy luận tên-flag (`--refresh` "phải" catch-up mọi thứ) thay vì đọc code thực thi — cả 2 lần đều là bước "khẳng định có bug" thiếu bước "đọc code + đối chiếu ground-truth trước khi dispatch đi sửa" | Chưa ai ghi trước retro này — bus finding Winston (`Winston_20260712_114800`, bác tiền đề #1) + Taylor (`Taylor_20260712_155038`, bác tiền đề #2) tự ghi khi điều tra; retro tự bổ sung |

**Sự cố 1 (C1) — 3 câu hỏi bắt buộc:**
a. **MỚI hay TÁI DIỄN?** Cùng HỌ với sự cố `2026-07-11` (SIGNAL_V11 đọc bảng `vnindex_5state`
   BASE thay vì `vnindex_5state_dt5g_live` — cũng là "đọc sai vintage/nguồn cho 1 script
   production") nhưng cơ chế cụ thể MỚI: lần trước là sai TÊN BẢNG (chọn nhầm bảng), lần
   này là sai NGUỒN TRUY XUẤT (bảng đúng, nhưng đọc qua cache thay vì live) — biến thể mới
   của cùng nhóm lỗi "data-registry-accuracy".
b. **Fix hoàn chỉnh hay còn hở?** HOÀN CHỈNH cho chính bug này (process-local `pop`, quant-
   skeptic CONFIRMED tái lập độc lập) — còn 1 điều kiện xác nhận thật qua cron sống thứ Hai
   07-13 18:30/19:00 ICT (chưa xảy ra tại thời điểm viết retro này).
c. **Đơn lẻ hay pattern?** PATTERN — đây là lần THỨ HAI trong 2 ngày liên tiếp (07-11, 07-12)
   một script production đọc SAI NGUỒN cho market-state/regime data. `coding_guidelines.md`
   §9 (data_registry.md) đã ra đời sau lần 1; §11 (cron_registry.md, "4 câu hỏi bắt buộc"
   gồm cả "đọc gì+vintage") ra đời NGAY SAU lần này, CÙNG NGÀY — đúng tinh thần "sửa gốc
   ngay khi phát hiện", không đợi RETRO.

**Sự cố 2 (H2) — 3 câu hỏi bắt buộc:**
a. MỚI — chưa có tiền lệ "freshness-check tự nó miscalibrated" trong INCIDENTS.md trước đây
   (khác các lần "freshness-check bug logic" như 2026-07-06 tối, đây là SAI GIẢ ĐỊNH về hành
   vi cron, không phải bug code trong chính check).
b. Fix hoàn chỉnh (BLOCK→WARN, verify sandbox PASS, quant-skeptic CONFIRMED 3 lần độc lập).
c. PATTERN — cùng nhóm với sự cố 1 và 3 (data-registry-accuracy): cả 3 đều là "code/check
   giả định 1 hành vi pipeline mà không đối chiếu lại thực tế tại thời điểm viết/dùng".

**Sự cố 3 (R1+F1) — 3 câu hỏi bắt buộc:**
a. MỚI (dạng lỗi "lookback cố định mù sự kiện mới trong cửa sổ" chưa từng ghi trong
   INCIDENTS.md — khác look-ahead đã biết nhiều lần).
b. Fix hoàn chỉnh, quant-skeptic CONFIRMED + Spyros/risk-auditor review vòng 2 xác nhận
   không rủi ro chặn còn lại.
c. PATTERN — cùng nhóm data-registry-accuracy (giả định sai về độ đầy đủ/tính đại diện của
   1 nguồn dữ liệu tại 1 thời điểm biên).

**Sự cố 4 (lag_edge_health) — 3 câu hỏi bắt buộc:**
a. MỚI — biến thể chưa từng ghi của nguyên tắc "trust the artifact" (MIKE.md #2), lần này
   áp dụng cho CLAIM CHẨN ĐOÁN thay vì TRẠNG THÁI JOB.
b. Không có "fix" vì không có bug — nhưng CƠ CHẾ PHÁT HIỆN (2 agent nhận dispatch đều tự
   verify trước khi sửa, không tự chế bug để khớp tiền đề) đã hoạt động đúng cả 2 lần. Còn
   hở: KHÔNG có bước nào ở TẦNG DISPATCH (trước khi giao việc) yêu cầu verify claim trước —
   toàn bộ gánh nặng verify đang dồn hết vào agent NHẬN việc.
c. Thuộc PATTERN rộng "trust the artifact" nhưng là NHÁNH MỚI của pattern đó, chưa có
   prevention riêng.

**Pattern xuyên suốt QUAN TRỌNG NHẤT — "data-registry-accuracy" chiếm 3/4 sự cố hôm nay,
và đây là ngày THỨ HAI LIÊN TIẾP (07-11 → 07-12) nhóm này là nguồn incident chính:**
07-11 có 1 sự cố nhóm data-registry-accuracy (SIGNAL_V11 base-leak); hôm nay có 3 (C1, H2,
R1+F1). Đây KHÔNG phải bằng chứng prevention 07-11 (§9 data_registry.md) sai — cả 3 sự cố
hôm nay đều được BẮT bởi audit CHỦ ĐỘNG (không phải do production tự fail rồi mới phát
hiện), đúng mục tiêu §9/§11 đặt ra là "kiểm tra sớm hơn". Nhưng tần suất cho thấy bề mặt
rủi ro (bao nhiêu script/check đang đọc sai vintage/nguồn) LỚN HƠN những gì 1-2 lần sự cố
đã lộ ra — mỗi audit mới lại tìm thêm case mới (cron-order audit tìm C1+H2; Q2-readiness
audit tìm R1+F1), gợi ý đây không phải "vài case cá biệt đã dọn xong" mà là 1 LỚP RỦI RO
CÒN CHƯA QUÉT HẾT.

**Prevention MẠNH HƠN được đề xuất (không lặp lại "cần quét thêm" suông):**
- Thay vì đợi audit ad-hoc (dispatch theo yêu cầu user hoặc theo lịch KB review thứ Sáu)
  tìm ra từng case một, cân nhắc 1 **script quét tĩnh 1 lần** (không phải cron định kỳ —
  đây là dọn nợ tồn, không phải giám sát liên tục) rà TOÀN BỘ script trong
  `deploy_golive_dt5g_v4/`, `mike/bin/`, và mọi script đọc `tav2_bq.*`/local cache: với mỗi
  script, xác định (a) nó có ý định đọc LIVE hay CACHE (từ role: publish/production-money-
  path = phải live; research/backtest = cache OK), (b) nó CÓ THỰC SỰ làm đúng ý định đó
  không (grep `BQ_LOCAL_CACHE` có bị pop trước query hay không, với mọi publish/execute
  script). Đây là việc 1-lần, quét diện rộng, khác hẳn audit ad-hoc từng lần chỉ quét 1 góc
  hẹp theo yêu cầu cụ thể — nên KHÔNG cần chờ lần audit tiếp theo tình cờ đi qua đúng script
  đó mới phát hiện.
- Cho sự cố 4 (lag_edge_health): thêm 1 dòng chuẩn vào MIKE.md/coding_guidelines khi dispatch
  1 việc "đi sửa bug X" — người dispatch (Mike hoặc agent audit) nên tự hỏi "tôi đã ĐỌC CODE
  thật hay chỉ suy luận từ triệu chứng/tên biến trước khi khẳng định có bug?" — không chặn
  cứng (đôi khi dispatch đúng là để người khác điều tra sâu hơn), nhưng nêu rõ trong prompt
  dispatch khi bản thân người dispatch CHƯA tự verify, để agent nhận việc biết cần verify
  trước khi sửa (2 lần hôm nay agent nhận việc đã TỰ LÀM ĐÚNG điều này dù không có hướng dẫn
  — ghi nhận đây là thực hành tốt cần strengthen thành thói quen chuẩn, không phải may mắn).

**Escalation (bước 10):** pattern data-registry-accuracy đã xuất hiện ở CẢ RETRO 07-11 (dưới
dạng entry SIGNAL_V11 base-leak trong `current_ops.md`, dù không có RETRO 07-11 riêng nào
gọi thẳng tên nhóm này — RETRO 07-11 focus vào 2 sự cố process khác) LẪN hôm nay — nhưng vì
đây là LẦN ĐẦU nhóm này được gọi tên tường minh làm "pattern xuyên suốt" trong 1 entry RETRO
(chưa có RETRO trước nào dùng đúng nhãn `data-registry-accuracy` làm pattern chính), điều
kiện bước 10 (2 RETRO LIÊN TIẾP CÙNG PATTERN đã nêu, prevention cũ không hiệu quả) **CHƯA
đạt theo nghĩa đen** — chưa escalate bus question. Nhưng đề xuất theo dõi: nếu audit TIẾP
THEO (bất kỳ góc nào) vẫn tìm thêm 1 case data-registry-accuracy mới, RETRO ngày đó nên
escalate thật (đủ 2+ lần với cùng nhãn tường minh).

**Ghi nhận tích cực đáng nêu:** cả 4 sự cố hôm nay đều là "audit chủ động bắt lỗi TRƯỚC khi
gây hại" (không có sự cố nào là production đã fail thật/user phải báo) — khác hẳn phần lớn
RETRO trước (07-06 đến 07-10) nơi đa số sự cố là lỗi ĐÃ XẢY RA rồi mới phát hiện qua báo cáo
sai/user chỉ ra. Đây là tín hiệu tích cực về hiệu quả của mandate "tự phát hiện → tự sửa"
(MIKE.md, mandate 2026-07-07) đang hoạt động đúng hướng.

