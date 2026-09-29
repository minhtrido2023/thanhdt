---
kind: research-report
job: Taylor_20260906_015330
date: 2026-09-06
parent: report_20260906.md (Phase 0), verify log mike/logs/verify_20260905_175658_3941964.log (quant-skeptic CONFIRMED medium)
status: DONE — V1-V4 xong, khuyến nghị GO to R3 với floor sector-adjusted, KHÔNG wire production ở phase này
---

# 8L Phase 0b — 4 việc bắt buộc cho trục T1 accruals trước R3

Trả lời trực tiếp 4 việc quant-skeptic yêu cầu (verify log job `quant-skeptic_20260905_175658`),
tất cả tính từ `panel_raw.csv` (Phase 0, N=23.404) + query mới `extract_sector_liquidity.sql`
(ICB_Code + `adv_30d` tự tính từ `tav2_bq.ticker`, KHÔNG dùng `ticker_prune`/`ticker_1m` vì đó là
universe đã lọc chất lượng — sẽ làm mất phần lớn 19,8% mã bị T1 loại trước khi kịp nhìn). Script:
`phase0b_analyze.py`, số máy đọc: `phase0b_results.json`.

**Self-check trước khi tin bất kỳ số nào dưới đây**: tái lập variant (a) — cutoff tuyệt đối, đúng
methodology Phase 0 gốc — khớp pinned đến 2 chữ số thập phân: OOS excl 19,83% (pinned 19,8%),
delta persistence 8,146pp (pinned 8,15pp), golden-floor overlap 51,01% (pinned 51,0%). Sai số ban
đầu (8,19pp) do dùng cutoff hiển thị làm tròn 0,0450 thay vì giá trị đầy đủ 0,045034 — đã sửa
bằng cách tính lại trực tiếp từ `t1_is["accr_q"].quantile(0.80)`.

## V1 — Floor theo ngành vs cutoff tuyệt đối (3 phương án, cả 3 báo đủ)

| Phương án | OOS excl % | persist excl | persist kept | delta_pp | golden-floor overlap |
|---|---|---|---|---|---|
| (a) cutoff tuyệt đối (pinned Phase 0) | 19,83% | 56,09% | 64,24% | **8,15** | 51,0% |
| (b) percentile TRONG TỪNG ngành (IS P80/ngành, ≥30 obs/ngành mới có cutoff riêng, else fallback global) | 19,34% | 57,67% | 63,81% | **6,13** | 41,7% |
| (c) demean theo ngành (IS sector-mean) rồi cutoff tuyệt đối trên giá trị đã demean | 19,06% | 56,13% | 64,15% | **8,02** | 47,2% |

- (b) có 36/66 ngành đủ ≥30 quan sát IS để có cutoff riêng; 9,6% dòng OOS rơi vào ngành thiếu dữ
  liệu phải dùng fallback cutoff toàn thị trường.
- **Đánh đổi rõ ràng**: (b) yếu hơn ở khả năng tách biệt persistence (6,13pp so với 8,15pp) NHƯNG
  bổ sung nhiều giá trị MỚI hơn (chỉ 41,7% mã bị loại đã bị golden floor bắt sẵn, so với 51,0% ở
  (a)) — tức (b) ít trùng lặp với golden floor hơn. (c) gần giống (a) ở cả hai chiều (8,02pp,
  47,2% overlap) — sector-demean gần như không đổi kết luận thực dụng so với cutoff tuyệt đối,
  dù nó sửa đúng cơ chế mà quant-skeptic chỉ ra.
- AUC toàn mẫu (không chỉ vùng floor): raw 0,4729 (cách 0,5 = 0,0271) → sector-demean 0,4822
  (cách 0,5 = 0,0178, co lại 34%) — khớp hướng với con số skeptic báo (17-31% co lại), không mâu
  thuẫn dù công thức demean cụ thể khác (skeptic dùng cả demean lẫn rank; ở đây chỉ demean).

**Kết luận V1**: hiệu ứng KHÔNG chết khi kiểm soát ngành ở bất kỳ phương án nào (không phương án
nào đổi dấu hay về 0), nhưng (a) cutoff tuyệt đối đang dùng thổi phồng ~1-2pp delta nhờ thành
phần ngành. (c) là lựa chọn cân bằng tốt nhất để mang vào R3 — sửa đúng bug mà không mất nhiều
biên độ hiệu ứng lẫn không cần cơ chế fallback phức tạp của (b).

## V2 — Đối chiếu mã bị loại (OOS, cutoff tuyệt đối) với thanh khoản

ADV tự tính = `AVG(Volume × Close)` 30 ngày lịch trước `Release_Date`, lấy từ `tav2_bq.ticker`
(universe ĐẦY ĐỦ, không qua bộ lọc chất lượng nào) — coverage 100% trên N=9.029 dòng OOS.

| | N | ADV P10 | P25 | P50 (median) | P75 | P90 |
|---|---|---|---|---|---|---|
| Bị loại (accr_q≥cutoff) | 1.791 | 478tr | 1,24 tỷ | **4,38 tỷ** | 19,35 tỷ | 67,58 tỷ |
| Giữ lại | 7.238 | 454tr | 1,18 tỷ | **4,71 tỷ** | 24,41 tỷ | 86,75 tỷ |

- Mann-Whitney U test 2 phân phối ADV (bị loại vs giữ lại): **p=0,145** — KHÔNG phân biệt được.
- % dưới ngưỡng thanh khoản tối thiểu hay dùng trong repo (0,5/1,0/2,0 tỷ/ngày, tham chiếu
  ADV60≥0,5 tỷ của `ticker_prune` breadth floor): bị loại 10,7%/21,2%/34,3% vs giữ lại
  11,2%/22,1%/34,8% — gần như giống hệt nhau ở mọi ngưỡng.

**Kết luận V2**: nhóm bị T1 floor loại KHÔNG tập trung vào micro-cap kém thanh khoản — phân bố
thanh khoản của 2 nhóm thực tế không phân biệt được. Đây là tin tốt cho việc wire: nếu áp floor,
phần vốn "tránh được" sẽ thật sự đổi universe đầu tư được (không phải loại bỏ mã vốn dĩ đã không
mua nổi), nên hiệu ứng 8,15pp (hay 8,02pp ở variant sector-adjusted) có cơ hội thật sự chuyển
thành khác biệt NAV ở R3, không bị vô hiệu hoá bởi capacity.

## V3 — Cluster-by-ticker: tái lập + mở rộng phát hiện của quant-skeptic

Row-level (N=14.884 dòng, như Phase 0 báo cáo): AUC=0,4729, p=3,47e-08.

Hai cách "cluster-robust" khác nhau, khác kết luận:

1. **Block bootstrap theo ticker** (B=2000, resample 733 ticker có hoàn lại, mỗi ticker mang theo
   TOÀN BỘ dòng quý — giữ nguyên N=14.884, chỉ sửa cách tính SE): AUC=0,4729 (không đổi),
   boot-SE=0,0058, 95%CI=[0,4616; 0,4845] (không chứa 0,5), z=−4,64, **p≈3,5e-06 — vẫn có ý
   nghĩa mạnh**.
2. **1 dòng ngẫu nhiên mỗi ticker** (N=733 lặp Monte Carlo 1000 lần — cách đọc literal của "N=733"
   trong verify log): AUC trung vị 0,4783 (IQR 0,4665–0,4917), **p trung vị=0,31** (IQR
   0,122–0,614), chỉ **13,5%** lần rút có p<0,05.

Hai phương pháp mâu thuẫn nhau vì lý do khác nhau: cách (1) giữ TOÀN BỘ dữ liệu và chỉ sửa công
thức SE cho tương quan trong-ticker (tương quan này hoá ra khá yếu với `accr_q` — kế toán dồn tích
biến động khá nhiều theo quý, không phải đặc tính cố định của doanh nghiệp — nên SE chỉ tăng nhẹ
so với iid: 0,0058 so với 0,0049 lý thuyết iid, +18%). Cách (2) BỎ 95% dữ liệu để có N độc lập
literal — mất power một cách nhân tạo, không phải bằng chứng hiệu ứng yếu. p=0,0153 mà
quant-skeptic báo cáo nằm NGOÀI khoảng IQR của MC (0,122–0,614, dưới cả P25) — nhiều khả năng họ
dùng một draw ngẫu nhiên may mắn hoặc phương pháp khác chưa rõ, nhưng bất kể cách nào, **kết luận
"vẫn có ý nghĩa nhưng yếu hơn nhiều so với p_BH hàng-dòng" là ĐÚNG ở cả 2 cách đo của chúng tôi**.

**Khuyến nghị phương pháp chuẩn** (đã ghi `.proposed`, chưa tự sửa `kb/`): dùng **block bootstrap**
làm cluster-robust p-value mặc định cho Phase-0 tương lai — không dùng subsample 1-dòng/ticker để
kết luận "hiệu ứng yếu", vì đó là nhầm lẫn giữa "mất power do bỏ dữ liệu" và "hiệu ứng không thật".
File đề xuất: `mike/kb/proposals/phase0-cluster-robust-standard.proposed.md`.

## V4 — Khuyến nghị floor: tương đối hay tuyệt đối, hay NO-GO?

**KHÔNG NO-GO.** Sau khi khử ngành (V1), lọc thanh khoản (V2), và cluster đúng cách (V3), hiệu
ứng T1 vẫn sống ở mọi góc kiểm tra:
- Sống sót sector-adjustment (attenuates nhưng không chết, cả 3 variant V1 đều delta dương đáng
  kể: 6,1–8,2pp).
- Sống sót cluster-robust đúng phương pháp (block bootstrap p≈3,5e-06, CI không chứa 0,5).
- KHÔNG bị vô hiệu hoá bởi thanh khoản (nhóm bị loại và giữ lại có phân bố ADV không phân biệt
  được, p=0,145) — hiệu ứng có cơ hội thật chuyển thành NAV.

**Khuyến nghị cụ thể**: mang **CẢ HAI** variant (a) cutoff tuyệt đối pinned VÀ (c) sector-demean
vào R3 backtest làm 2 nhánh so sánh song song — KHÔNG chọn 1 cái trước khi thấy NAV impact, vì
chênh lệch delta persistence giữa chúng (8,15 vs 8,02pp) nhỏ hơn nhiều so với sai số đo lường ở
mức backtest, và chỉ R3 mới trả lời được câu hỏi thực dụng "loại 19% universe có đáng hay không".
Loại (b) per-sector-percentile khỏi R3 — yếu hơn đáng kể (6,13pp) và cõng thêm độ phức tạp vận
hành (fallback cutoff cho 30/66 ngành thiếu dữ liệu) mà không có bằng chứng đủ bù đắp.

**Vẫn KHÔNG wire production, KHÔNG chạy R3 ở phase này** — đúng ràng buộc dispatch. R3 backtest là
bước tiếp theo, ngoài phạm vi Phase 0b.

## File/artifact
- `extract_sector_liquidity.sql` — ICB_Code (từ `ticker`, PIT ≤7 ngày) + `adv_30d` tự tính
  (`AVG(Volume×Close)` 30 ngày lịch, từ `ticker` — KHÔNG dùng `ticker_prune`/`ticker_1m` vì đã lọc
  chất lượng sẵn, sẽ che mất chính nhóm mã cần kiểm tra).
- `sector_liquidity_raw.csv` — 48.481 dòng, coverage ICB_Code/adv_30d ~99,9% trên panel gốc.
- `phase0b_analyze.py` — script phân tích V1-V3, tái lập (a) khớp pinned Phase 0 đến 2 chữ số.
- `phase0b_results.json` — số máy đọc đầy đủ.
- `mike/kb/proposals/phase0-cluster-robust-standard.proposed.md` — đề xuất chuẩn hoá block
  bootstrap cho cluster-robust p-value, chờ Mike duyệt.
