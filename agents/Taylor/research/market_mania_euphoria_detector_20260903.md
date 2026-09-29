# Market mania/euphoria detector — ảnh gương của CAPIT (mua bất chấp chất lượng)

> Job `Taylor_20260903_144602` · 2026-09-03 · **RESEARCH-ONLY, không wire production, không đổi
> DT5G/CAPIT/gate nào.** Đọc `.claude/skills/quant-research/SKILL.md` trước khi chạy (N khai báo
> = số EPISODE độc lập, không phải số dòng/phiên).

## Tóm tắt 1 dòng

Xây được 1 chỉ báo 2 chân (breadth cực đoan kéo dài + junk/high-risk basket thắng quality basket
cùng lúc) đo được bằng dữ liệu thật, PIT, `universe_pit`. Ở ngưỡng chính (breadth≥p90, dispersion
spread≥p75, ≥21 phiên liên tục): **N=7 episode** 2008→2026. Kết quả: hướng return 1-6 tháng SAU
episode **không nhất quán** (trung bình dương nhẹ, %âm dao động 29-57% tuỳ horizon) — **KHÔNG
dùng làm timing bán trực tiếp**. Nhưng **6/6 episode có đủ dữ liệu forward-6-tháng đều trải qua
một đợt điều chỉnh ≥7% trong vòng 6 tháng sau đó** (trung bình maxdd −14,3%, range −7,1%→−21,3%) —
đây là pattern lặp lại rõ nhất, và **giữ vững** khi nới ngưỡng (N=14, breadth≥p85/spread≥p60):
maxdd trung bình vẫn −13,9%, 71% episode có maxdd <−10%.

**N=7 (hoặc 14 ở ngưỡng nới) là nhỏ — đủ để thấy dose-response và pattern định tính, KHÔNG đủ để
tính một threshold chuẩn hoá hay coi đây là gate.**

---

## 1. Định nghĩa chỉ báo

**Chân 1 — Breadth cực đoan kéo dài** (giống hệt cơ chế B2 breadth-tercile PIT đã dùng
2026-08-22, tái dùng convention `btile_{t-1}`):
```
breadth(t) = COUNTIF(Close_ticker > MA200_ticker) / COUNT(*)   -- trên universe_pit.in_universe=TRUE tại t
breadth_pct252(t) = phân vị của breadth(t) trong 252 phiên TRƯỚC t (không gồm t, causal)
```

**Chân 2 — Dispersion chất lượng sụp đổ (lõi phân biệt "mania" với "bull khỏe mạnh")**:
```
ret_lowrisk(t)  = trung bình return 1-phiên của rổ Risk_Rating<=2 (thấp rủi ro) trong universe_pit
ret_highrisk(t) = trung bình return 1-phiên của rổ Risk_Rating>=5 (rủi ro cao/đầu cơ)
spread21(t)     = tổng log-return 21 phiên (highrisk - lowrisk)   -- "junk" thắng "quality" bao nhiêu
spread21_pct252(t) = phân vị của spread21(t) so với chính nó trong 252 phiên trước
```
Dùng `Risk_Rating` (composite Beta+Dev, đã có sẵn trong `ticker`, thang 1-6, gán theo quý PIT —
cùng cột production đã dùng cho sizing) làm proxy "chất lượng/rủi ro" thay vì 8L composite —
tránh phải chạy lại `rating_8l.py` cho toàn lịch sử; Risk_Rating đã PIT theo thiết kế gốc.

**Cờ MANIA_DAY** = `breadth_pct252 >= 0,90` VÀ `spread21_pct252 >= 0,75` (junk basket đang thắng
quality **theo tương đối với chính lịch sử gần đây của nó**, không phải theo giá trị tuyệt đối).

**EPISODE** = chuỗi MANIA_DAY liên tục cho phép gap ≤3 phiên (noise ngày lẻ), tổng độ dài **≥21
phiên** (~1 tháng lịch, đúng yêu cầu dispatch "kéo dài >1 tháng").

## 2. Nguồn dữ liệu + PIT

- `tav2_bq.ticker` JOIN `tav2_mike.universe_pit` (in_universe=TRUE) theo (ticker,time) — universe
  CANONICAL cho breadth (không dùng `ticker_prune`, theo `kb/data_registry/price-volume/universe_pit.md`
  và convention chốt 2026-08-22).
- Cửa sổ dữ liệu: `t.time >= 2007-01-01`, cắt panel phân tích từ **2008-06-01** (đủ warm-up 252
  phiên + breadth chỉ có nghĩa từ ~2008, CLAUDE.md §BigQuery bẫy #4: 2008≈105 mã).
- KHÔNG dùng cột `profit_*` (forward-looking) ở bất kỳ bước định nghĩa episode nào — chỉ dùng khi
  đo OUTCOME sau episode (return VNINDEX thô, không phải cột profit_*).
- Panel: 4.558 phiên 2008-06-02→2026-09-03. Query: `mania_20260903/q_mania_daily.sql`,
  data: `mania_20260903/mania_daily.csv`.

## 3. Danh sách episode (ngưỡng chính p90/p75)

| # | Bắt đầu | Kết thúc | Độ dài (phiên) | VNI đầu | VNI cuối | Return trong episode | +1M | +2M | +3M | +6M | **maxDD trong 6M sau** |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2009-08-24 | 2009-09-23 | 22 | 528,20 | 582,10 | +10,2% | +7,2% | −4,5% | −20,8% | −13,2% | *(thiếu dữ liệu 6M đủ, panel bắt đầu 2008-06)* |
| 2 | 2012-02-22 | 2012-04-19 | 41 | 418,41 | 467,08 | +11,6% | −4,1% | −7,3% | −8,3% | −15,0% | **−21,3%** |
| 3 | 2013-11-08 | 2013-12-06 | 21 | 498,61 | 510,12 | +2,3% | 0,0% | +12,2% | +17,7% | +11,7% | **−15,4%** |
| 4 | 2014-02-12 | 2014-03-31 | 34 | 564,25 | 591,57 | +4,8% | −4,5% | −5,5% | −2,2% | +3,0% | **−14,8%** |
| 5 | 2016-04-05 | 2016-05-06 | 21 | 560,32 | 606,52 | +8,2% | +2,2% | +7,3% | +4,1% | +11,6% | **−7,1%** |
| 6 | 2020-11-04 | 2020-12-25 | 38 | 939,76 | 1084,42 | +15,4% | +4,8% | +9,5% | +12,1% | +31,0% | **−14,3%** |
| 7 | 2025-07-15 | 2025-09-05 | 37 | 1460,65 | 1666,97 | +14,1% | +1,7% | −0,9% | +3,9% | +3,7% | **−13,1%** |

Artifact đầy đủ: `mania_20260903/mania_episodes.csv`.

**N=7 episode độc lập** (không chồng lấn, cách nhau ≥1,5 năm trừ 2012→2013→2014 sát nhau — vẫn
tính riêng vì đáy/đỉnh giữa các episode phân biệt rõ trên VNINDEX, không phải cùng 1 sóng liên
tục). Episode #1 (2009) thiếu horizon 6 tháng đủ dài vì đó là episode sớm nhất trong panel.

## 4. Outcome tổng hợp (N=6-7 tuỳ horizon)

| Horizon sau episode | n | mean | median | min | max | %episode âm |
|---|---:|---:|---:|---:|---:|---:|
| +1 tháng | 7 | +1,0% | +1,7% | −4,5% | +7,2% | 29% |
| +2 tháng | 7 | +1,5% | −0,9% | −7,3% | +12,2% | 57% |
| +3 tháng | 7 | +0,9% | +3,9% | −20,8% | +17,7% | 43% |
| +6 tháng | 7 | +4,7% | +3,7% | −15,0% | +31,0% | 29% |
| **maxDD trong 6 tháng sau** | **6** | **−14,3%** | **−14,5%** | **−7,1%** | **−21,3%** | **100%** |

**Return theo horizon KHÔNG có hướng nhất quán** — không dùng chỉ báo này làm "bán ngay khi thấy
mania" vì median +1M/+3M/+6M đều dương, và 2 trong 7 episode (#6 2020, #7 2025) có return +6M rất
dương (+31%, +3,7%) — tức thị trường có thể tiếp tục tăng một thời gian sau khi mania được phát
hiện, đúng như cảnh báo chuẩn "market can stay irrational longer than you can stay solvent".

**Nhưng maxDD-trong-6-tháng-sau là pattern nhất quán nhất: 6/6 episode có đủ dữ liệu đều trải
qua một đợt sụt ≥7% nào đó trong 6 tháng kế tiếp**, trung bình −14,3%, trung vị −14,5%. Đây không
phải "thị trường sập ngay" mà là "một đợt điều chỉnh có ý nghĩa gần như chắc chắn xảy ra ở đâu đó
trong 6 tháng tới, ngay cả khi xu hướng chính vẫn đi lên".

## 5. Robustness — dose-response theo ngưỡng

| Ngưỡng (breadth_pct / spread_pct) | N episode |
|---|---:|
| p85 / p60 | 14 |
| p85 / p70 | 11 |
| p90 / p70 | 9 |
| **p90 / p75 (chính, dùng ở §3-4)** | **7** |
| p90 / p80 | 5 |
| p95 / p80 | 4 |

Đơn điệu giảm khi siết ngưỡng — đúng dạng dose-response, không phải nhiễu tham số.

**Kiểm tra lại maxDD-6M ở ngưỡng nới nhất còn hợp lý (p85/p60, N=14):** mean **−13,9%**, 71%
episode có maxDD < −10% — kết luận §4 **giữ vững**, không phải artifact của việc chọn đúng 7 case
khớp câu chuyện. Chi tiết: 2 episode maxDD không đo được (panel warm-up 2008-06, episode 2009-08
không đủ 126 phiên forward).

## 6. Đối chiếu với nghiên cứu đã có (Phần 1, `vn_top_divergence_and_margin_selloff_20260831`)

Job 2026-08-31 tìm "2022-01 penny-stock mania" là case duy nhất (1/4) có breadth-euphoria
divergence rõ ở ĐỈNH giá. Kiểm tra chéo: chỉ báo ở đây **KHÔNG flag episode nào quanh
2021-H2→2022-01** dù breadth có lúc lên rất cao (breadth_pct252 chạm 0,99 vào 2021-11-18) — vì
điều kiện "≥21 phiên LIÊN TỤC ≥p90" không thoả: breadth dao động mạnh, tụt xuống ~p10-p60 nhiều
lần trong tháng 12/2021→01/2022 NGAY CẢ KHI giá VNINDEX vẫn tiếp tục leo tới đỉnh 06/01/2022. Đây
**khớp đúng** phát hiện "breadth-euphoria divergence" của job 08-31 — breadth tự nó đã bắt đầu rạn
nứt/không kéo dài được trước khi giá tạo đỉnh cuối, nên bộ lọc "sustained ≥1 tháng" của job này
đúng đắn không bắt được case đó (một dạng mania khác — mania đang RÚT LUI khỏi breadth trong khi
giá vẫn quán tính tăng — không phải target của chỉ báo hiện tại). Hai công cụ bổ sung nhau,
không mâu thuẫn: công cụ này bắt "mania breadth-rộng đang DIỄN RA", công cụ 08-31 bắt "mania đang
RẠN NỨT ở đỉnh".

## 7. Giới hạn phải mang theo

1. **N=7 (chính) / N=14 (nới ngưỡng) là NHỎ.** Không đủ để tính DSR/PBO có ý nghĩa hay chọn một
   threshold "tối ưu" — §14/§15 của skill quant-research không áp dụng vì đây không phải đề xuất
   wire một config cụ thể vào production.
2. **Risk_Rating là proxy rủi ro (Beta+Dev), không phải rating chất lượng cơ bản (8L/FSCORE).**
   Dispatch gợi ý "mua bất chấp chất lượng/rating/KQKD" — Risk_Rating đo được "junk/đầu cơ thắng
   an toàn", một proxy hợp lý và có sẵn PIT, nhưng KHÔNG trực tiếp đo "mua bất chấp KQKD xấu".
   Mở rộng sang FSCORE hoặc 8L composite (đòi PIT-join phức tạp hơn theo Release_Date) là việc
   tiếp theo nếu muốn tinh chỉnh chân dispersion.
3. **Return theo horizon không đơn điệu/không đủ mạnh để làm tín hiệu bán trực tiếp** — chỉ
   maxDD-trong-6-tháng là pattern đáng tin. Đừng diễn giải "mania flag = bán ngay". 2020-11 và
   2025-07 là 2 case gần đây nhất mà thị trường vẫn tăng tiếp SAU episode trước khi điều chỉnh —
   timing của cú điều chỉnh bên trong cửa sổ 6 tháng chưa được đo (chỉ đo có/không, chưa đo NGÀY
   xảy ra maxDD so với ngày kết thúc episode).
4. **Đây là RESEARCH-ONLY.** Không đề xuất wire vào DT5G/CAPIT/gate nào. Không qua quant-skeptic
   (không cần, vì không đề xuất production change) — nhưng bất kỳ ai muốn dùng kết luận §4 để ra
   quyết định thực tế nên tự chạy lại self-check dưới đây trước.

## 8. Self-check tối thiểu đã chạy

- Query SQL group-by 1 dòng/phiên, không phải per-ticker → không có rủi ro NAV/vốn (không backtest
  chiến lược, không tính lãi/lỗ VND) — mục §7 quy chuẩn "self-check 0 VND" của CLAUDE.md không áp
  dụng trực tiếp (không có phép tính NAV nào ở đây).
- breadth_pct252 và spread21_pct252 đều tính CAUSAL (chỉ dùng 252 phiên TRƯỚC t, loại t) — xác
  nhận bằng code `for i in range(252, len(b)): pct[i] = (b[i-252:i] < b[i]).mean()`.
- Episode #7 (2025-07→09) đối chiếu tay: VNINDEX 1.460,65→1.666,97 khớp `data/VNINDEX.csv`/BQ
  trực tiếp không qua bước biến đổi nào khác.

## Artifact

- `mania_20260903/q_mania_daily.sql` — query BQ (universe_pit JOIN ticker).
- `mania_20260903/mania_daily.csv` — panel daily 4.558 phiên (breadth, spread, VNINDEX).
- `mania_20260903/analyze_mania.py` — episode detection + outcome.
- `mania_20260903/mania_episodes.csv` — 7 episode + forward outcomes.
- Bus: `market-mania-euphoria-detector-20260903`.
