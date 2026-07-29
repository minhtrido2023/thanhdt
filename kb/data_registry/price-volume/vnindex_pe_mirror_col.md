---
kind: bigquery-column
status: CANONICAL (có quy ước bắt buộc — đọc §"Sàn lịch sử 2008" trước khi tính percentile)
source: cột mirror t.VNINDEX_PE trên hàng CỔ PHIẾU (trong tav2_bq.ticker VÀ ticker_prune)
group: price-volume
issue: RESOLVED 2026-07-29 — bq_admin đã backfill về 2006-03-30. Cảnh báo MỚI: 2006-2007 không đại diện.
detected: 2026-07-29 (Taylor job Taylor_20260729_024754, verify sâu bởi Mike qua BQ Python SDK)
fixed: 2026-07-29 (backfill đáp sáng 07-29; verify MIN(time)=2006-03-30, 4.070.863 hàng non-null)
writer: bq_admin
---

# Cột mirror `t.VNINDEX_PE` (PE thị trường) trên các hàng CỔ PHIẾU (`tav2_bq.ticker` VÀ `ticker_prune`)

**Status: ✅ ĐÃ FIX** — bug NULL-trước-2016-07-01 đã được bq_admin backfill ngày 2026-07-29. Verify
trực tiếp trên BQ live cùng ngày: `MIN(time) WHERE VNINDEX_PE IS NOT NULL` = **2006-03-30**
(4.070.863 hàng non-null). Mốc non-null **cũ** (trước backfill, đo từ `data/bq_cache/ticker/*.parquet`)
là **2016-06-01** — dùng mốc này nếu cần tái lập hành vi của chuỗi nào build trước 2026-07-29.

## Là gì
Cột tiện ích gắn giá trị PE thị trường VNINDEX theo NGÀY lên mọi hàng cổ phiếu (mirror, giống cơ chế
`t.VNINDEX` — xem [[vnindex_mirror_col]]). Nay có dữ liệu 2006-03-30 → hiện tại, khớp file local
`data/VNINDEX.csv` (file đó dừng cập nhật ~2026-05-26 — không dùng cho giá trị hiện tại).

## ⚠️ Sàn lịch sử 2008 — quy ước BẮT BUỘC cho mọi percentile định giá

Dữ liệu 2006–2007 nay **hợp lệ về hình thức nhưng KHÔNG ĐẠI DIỆN**. Bằng chứng
(`tav2_bq.ticker`, loại VNINDEX/VN30):

| Năm | Số mã có dữ liệu | Số mã có **PE hợp lệ** | % |
|---|---|---|---|
| 2006 | 130 | **0** | **0%** |
| 2007 | 179 | 58 | 32% |
| **2008** | 242 | 202 | **83%** ← điểm gãy độ phủ |

Năm 2006 có 194 phiên `VNINDEX_PE` (giá trị 27,9–45,5) nhưng **không một mã nào có PE hợp lệ** để
kiểm chứng chéo. 2007 là vùng bong bóng (PE tới 59,9) trong khi đỉnh của cả kỷ nguyên 2014+ chỉ ~22,6.

**Quy ước**: mọi percentile/MA/SD định giá (PE, PB, EV/EBITDA — thị trường lẫn per-ticker) **floor ở
`2008-01-01`**. Đồng bộ quy ước `ticker_prune` đã có (`CLAUDE.md`: breadth/universe chỉ có nghĩa từ
~2008). Muốn dùng 2006–2007 thì phải nêu rõ lý do + cảnh báo trong báo cáo.

**Nếu bỏ qua quy ước này** (đo thực nghiệm,
`mike/agents/Taylor/research/pe_history_floor_2006_2008_20260729.md`): ngưỡng p90 expanding bị thổi
lên **21,18 vs 17,55 (+21%) hôm nay** và **35,30 vs 16,60 (+113%) năm 2017** ⇒ percentile PE báo thị
trường **rẻ hơn thực tế một cách có hệ thống**. Độ méo hạng suy giảm theo thời gian (17pp năm 2014 →
~5pp năm 2026) vì cửa sổ expanding dài ra.

## Ai đang dùng cột này (audit 2026-07-29, job Taylor_20260729_132056)

| Consumer | Cửa sổ | Có dính 2006–07 không |
|---|---|---|
| `vnindex_5state_dual_v3.py` — factor thứ 8 (`W_PE=0,03`) + override EX-BULL→BULL | **EXPANDING từ đầu chuỗi** | **CÓ** — kênh production duy nhất. Tác động đo được: 19/3.135 phiên DT5G (0,61%), **0 phiên trong 2026**, ~+0,05pp CAGR. Quyết định: **KHÔNG vá** (xem research file). |
| `vnindex_5state_ew_v1.py` — override EX-BULL→BULL | EXPANDING | **KHÔNG lan xuống** — `dual_v3` chỉ đọc `r_score` (7 factor, không PE) + `f_Breadth` từ `ew_full`; cột `state` của ew_v1 không ai tiêu thụ. |
| `pt_v23_audit_2014.py` — fed-gate (1/PE) + gate "rẻ tuyệt đối" | rolling **60 tháng FIXED**, query giới hạn `START_DATE..END_DATE` (2014+) | **KHÔNG.** Và inert ở cấu hình production (`RECOVERY_GATE_MODE=deposit`, `MGE_GATE=none`, `RECOVERY_STATE_BLIND=0`, `RECOVERY_PE_PCT_MAX=1.0` ⇒ `_PE_GATE_ON=False`). |
| `exp_market_prob/analyze.py` + `eventstudy*.py` | đã `>= 2008-01-01` | **KHÔNG** — đã tuân thủ sẵn. |

## Workaround cũ (giờ chỉ còn giá trị lịch sử)
Trước backfill, `market_regime_probability_20260729.md` tự dựng PE thị trường cap-weighted từ cột
`PE` per-ticker (`Σ Price×OShares / Σ EPS×OShares`), corr 0,945 với PE chính thức trên 2016+. Vẫn
dùng được làm nguồn kiểm chứng chéo độc lập. **Chưa ai đối chiếu nó với PE chính thức mới backfill
trên đoạn 2007–2016** — việc còn để ngỏ; lưu ý PE per-ticker cũng chỉ có độ phủ thật từ 2008 (bảng
trên), nên đối chiếu ở 2006–2007 sẽ vô nghĩa.
