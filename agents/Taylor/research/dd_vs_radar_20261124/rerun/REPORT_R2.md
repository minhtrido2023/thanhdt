# R2 — chạy lại R1 cho NHẤT QUÁN (theo QUANT_SKEPTIC_R1)

Job `Taylor_20261123_174703` · 24/11/2026 · dữ liệu tới 2026-11-23 · NGHIÊN CỨU/CHẨN ĐOÁN — không đổi radar/sổ DD/skill/luật, không wire.
Script `rerun/R2/analyze_r2.py` (tái dùng panel R1 đã khoá; không sửa file R1). Số đọc từ `R2/out/summary_r2.json`, `h3_consistent_grid.csv`, `h3_r_vs_roe_decomp.csv`, `h1_np5_coverage_by_year.csv`.
Chạy 2 lần, threads=1: md5 mọi output trùng (`R2/OUTPUTS.md5`). Đầu vào khoá ở `rerun/INPUTS.md5` (kể cả bản sao đóng băng sổ DD). Parity với R1: `pe_cap10` lệch tối đa 5,0e-5 (do R1 ghi CSV `%.6g`).

## Số cũ → số mới nhất quán

| Mục | R1 (cũ) | R2 (nhất quán) | Ghi chú |
|---|---|---|---|
| Phần độ rẻ (log gap so trung vị 10Y) do lợi nhuận đỉnh | 35% | **44–52%** (cap-weight, cùng tập mã; 4 cách tính) | R1 chia P/E chuẩn hoá (tập/trọng số A) cho tỷ lệ của tập B ⇒ 35% là lệch cơ sở |
| — bỏ Vingroup+BSR | — | **27%** | đỉnh lợi nhuận tập trung vào ít tên |
| — trung vị theo mã | — | **14%** | mã điển hình chỉ hơi trên trung vị (1,36 vs 1,28) |
| P/E phản thực (tỷ lệ về trung vị) | 11,20 (p7,5) | **11,67–12,02** (p12–17) | vẫn RẺ so với 10Y |
| "EPS/TB5Y = 1,58 là kỷ lục 227 tháng" | kỷ lục | **đỉnh cửa sổ 10Y**; toàn chuỗi p81 (2011-02→07 cao hơn, đỉnh 2011-03 = **1,71**) | 2011-03 đo trên **13%** vốn hoá top-100 (9% số mã) ⇒ không so được |
| Tỷ lệ bỏ Vingroup+BSR | — | 1,42, **p91,6** (10Y) | skeptic p92,5 (định nghĩa tập hơi khác) |
| Tỷ lệ trung vị theo mã | — | 1,36, **p74,8** | skeptic p77 |
| Độ phủ np5 (theo vốn hoá) | "94% nay" | 2012–20: **0,33–0,59**; 2022+: 0,86–0,96 | phân vị 10Y của tỷ lệ so với quá khứ phủ mỏng |
| H3 thị trường vs P/E công bằng DD (r 13,5%, g 6%) | +4% / +19% | ROE giữ TTM: **−2%** (g 4–8%: **+9…−15%**) · ROE khử đỉnh 14,7%: **+33%** (+24…+40%) · ROE = TB lợi nhuận 5Y/sổ hôm nay 11,3%: **+120%** (+106…+156%, cận trên) | "+19%" của R1 ghép P/E TTM với ROE chuẩn hoá; skeptic +48% dùng ROE trung vị rổ R1 14,0% |
| — ở r 12,3% | rẻ ~12% (ROE TTM) | ROE TTM **−5…−33%** · khử đỉnh **−3…+22%** · n5 **+80…+100%** | dấu đổi theo (g, ROE) |
| Phân rã khoảng cách mốc lịch sử ↔ mốc DD | 78% r / 22% ROE | **tách chính xác dạng P/B** (không phần dư): ROE khử đỉnh ⇒ phần ROE **1–6%** (r ≈ 95%+); ROE n5/sổ ⇒ phần ROE **42–80%**; ROE giữ TTM ⇒ khoảng cách ≈0 (−0,18…+0,30), tỷ phần **không xác định** | r ngầm định của lịch sử **9,5–11,6%** (g 4–8%) |
| Spread EY chuẩn hoá − lãi huy động | −0,39pp, p56 "trung tính" | Big-4 thuần: **+0,21pp, p72** | R1 trộn CCTG (chỉ có từ 2026-09-30) với Big-4 lịch sử |
| Composite chuẩn hoá (tháng) | 16,0 | **10,6** (RẺ, không trung tính) | |
| Composite TTM (tháng) | 2,2 | **1,1** | |
| Radar ngày (công thức radar, rolling 2500 phiên) | 2,3 | Big-4 thuần **1,0**; p_spread 4,6 → **0,6** | cùng P/E p0,16, P/B p2,2 |
| Bản backfill CCTG | — | **trùng Big-4 thuần** (kiểm số: chênh 0,000) | xem §3 |
| Sổ DD dùng cho R1 | `kb/dd_price_zones.json` sống | bản sao đóng băng `inputs/dd_price_zones_da6018d95.json` (md5 74539e4…) | D1 đã đọc bản KHÁC (e547cd7fc) — xem §5 |

## Kết luận (đã sửa, KHÔNG thêm kết luận mới)

1. **Rẻ so với lịch sử: ĐỨNG.** P/E 9,66 p0 (10Y); kể cả khi đưa tỷ lệ lợi nhuận đỉnh về trung vị, P/E tương đương 11,7–12,0 vẫn ở p12–17. Composite chuẩn hoá 10,6 vẫn RẺ.
2. **Lợi nhuận đỉnh giải thích 44–52% độ rẻ** (không phải 35%). Đỉnh này **tập trung**: bỏ Vingroup+BSR còn 27%, theo trung vị từng mã còn 14%. Hôm nay là đỉnh **cửa sổ 10Y**, không phải kỷ lục toàn chuỗi.
3. **H3: thị trường so với mức "công bằng kiểu DD" nhạy hoàn toàn với giả định ROE.** Giữ ROE hiện tại 17,8% ⇒ thị trường ≈ công bằng (r 13,5%: +9…−15%). Khử đỉnh ROE về 14,7% ⇒ thị trường **trên** công bằng +24…+40%. Hướng chung (ROE chuẩn hoá ⇒ thị trường đắt hơn theo thước DD) đứng; **độ lớn không chốt được**.
4. **Phân rã r vs ROE không phải một con số.** Khi ROE giả định ≈ ROE lịch sử (khử đỉnh), gần như toàn bộ khoảng cách là do r (lịch sử ngầm r 9,5–11,6% vs DD 12,3–13,5%). Khi ROE chuẩn hoá mạnh hơn, phần ROE lên 42–80%. Câu "78% r / 22% ROE" bị thay bằng dải này.
5. **Spread "trung tính" của R1 sai cơ sở.** Trên một cơ sở lãi huy động (Big-4 thuần), spread chuẩn hoá ở p72 (vẫn nghiêng rẻ), composite 10,6.

## 1. Phản thực lợi nhuận đỉnh (`cf_peak_earnings`)

Gap = ln(14,74/9,66) = 0,423. Tập S = top-100 radar có np5>0 và np_ttm>0 (cùng trọng số cap10 tái chuẩn).

| Cách | tỷ lệ nay | trung vị 10Y | P/E phản thực | % gap giải thích |
|---|---|---|---|---|
| A. P/E_ttm × tỷ lệ_nay/tỷ lệ_trung vị (tỷ lệ R1 tổng/tổng) | 1,584 | 1,272 | 12,02 | 51,8% |
| C. cùng tập S, tỷ lệ trọng số | 1,548 | 1,280 | 11,67 | 44,9% |
| D. cùng tập S, tỷ lệ tổng/tổng | 1,579 | 1,289 | 11,83 | 48,0% |
| F. trên chính tập S (neo trung vị S_pe_ttm 14,14) | 1,548 | 1,280 | 11,14 | 44,4% |
| G. như F, bỏ Vingroup+BSR | 1,423 | 1,288 | 10,25 | 27,1% |
| E. tỷ lệ trung vị theo mã | 1,360 | 1,281 | 10,25 | 14,2% |
| (B. R1 gốc, lệch cơ sở) | | | 11,21 | 35,3% |

Dải nhất quán (A, C, D, F) = **44,4–51,8%**.

## 2. H3 nhất quán (`h3_consistent_grid.csv`, `h3_r_vs_roe_decomp.csv`)

So ở dạng P/B: giá công bằng = P/B_công_bằng(ROE, r, g) × sổ sách. Dạng này không phải chọn "lợi nhuận nào" cho mẫu số P/E; ROE giả định là biến duy nhất. P/B_công_bằng = (ROE−g)(1+g)/(r−g). Cùng tập S: P/B 1,636, ROE_ttm 17,8%, ROE khử đỉnh 14,7% (= ROE_ttm × 1,280/1,548), ROE trung vị 10Y 14,8%, TB lợi nhuận 5Y/sổ hôm nay 11,3%. Kiểm: dạng P/E-TTM và dạng P/B trùng nhau tới 0,1%.

Thị trường so với công bằng (dương = thị trường cao hơn):

| r | g | ROE giữ TTM | ROE khử đỉnh | ROE trung vị 10Y | TB5Y/sổ nay (cận) |
|---|---|---|---|---|---|
| 12,3% | 4% | −5% | +22% | +21% | +80% |
| 12,3% | 6% | −17% | +12% | +11% | +85% |
| 12,3% | 8% | −33% | −3% | −4% | +100% |
| 13,5% | 4% | +9% | +40% | +39% | +106% |
| 13,5% | 6% | −2% | +33% | +32% | +120% |
| 13,5% | 8% | −15% | +24% | +23% | +156% |

"TB5Y/sổ nay" là **cận** vì chia lợi nhuận bình quân 5 năm cho sổ sách hôm nay (sổ đã tăng). Nó chứa kéo tụt do tăng trưởng, không phải ước lượng trung tâm.

**Phân rã** (trong script): ln P/B_công_bằng = ln(ROE−g) + ln(1+g) − ln(r−g) ⇒ tách CHÍNH XÁC, không phụ thuộc thứ tự (kiểm tổng: 0,0). Mốc lịch sử: P/B trung vị 10Y của S (2,04) với ROE trung vị 10Y ⇒ r_hist 9,5% (g 4%) … 11,6% (g 8%).

| ROE phía DD | r_DD | tỷ phần ROE theo g = 4 / 5 / 6 / 7 / 8% |
|---|---|---|
| khử đỉnh | 13,5% | 1 / 2 / 2 / 2 / 3% |
| khử đỉnh | 12,3% | 2 / 2 / 3 / 4 / 6% |
| TB5Y/sổ nay | 13,5% | 42 / 46 / 51 / 56 / 63% |
| TB5Y/sổ nay | 12,3% | 49 / 55 / 61 / 70 / 80% |
| giữ TTM | cả hai | khoảng cách −0,18…+0,30 ≈ 0 ⇒ tỷ phần không xác định (−979%…+512%) |

## 3. Spread + composite trên MỘT cơ sở lãi huy động (`spread_one_basis`)

- Radar hiện dùng `effective_deposit_events_df()` = max(Big-4 12M, CCTG). CCTG chỉ có từ 2026-09-30 ⇒ chuỗi đổi cơ sở giữa chừng (nay 7,4 so với Big-4 6,8).
- **Big-4 thuần suốt chuỗi**: spread TTM +3,56pp (p99 ⇒ đảo chiều 0,6–0,8). Spread chuẩn hoá +0,21pp p72. Composite tháng TTM 1,1, chuẩn hoá 10,6. Radar ngày 1,0.
- **Backfill CCTG**: không có lịch sử CCTG trước 2026-09-30. Cách dựng duy nhất = Big-4 + chênh hằng 0,6pp đo ở đoạn chồng lấn. Phân vị là hàm hạng nên cộng hằng cho cả chuỗi không đổi phân vị ⇒ **trùng Big-4 thuần** (chênh đo được 0,000 cả tháng lẫn ngày). Mức spread thì thấp hơn 0,6pp. Một backfill CCTG có biến thiên thật thì **không dựng được** từ dữ liệu hiện có.

## 4. H1 robustness (`h1`)

- Tỷ lệ 1,584 hôm nay là đỉnh **cửa sổ 10Y** (đỉnh trước trong 10Y: 1,507). Trên toàn chuỗi 2008+ chỉ ở p81: 6 tháng 2011-02→07 cao hơn, đỉnh 2011-03 = **1,709**. Nhưng 2011 có độ phủ np5 chỉ 15% vốn hoá (13% ở tháng đỉnh), nên không so được.
- Độ phủ np5 (vốn hoá top-100) theo năm: 2012 0,33 · 2014 0,46 · 2016 0,59 · 2018 0,53 · 2020 0,56 · 2022 0,86 · 2024 0,96 · nay 0,94. Phân vị 10Y của tỷ lệ so hôm nay (phủ rộng) với quá khứ phủ mỏng ⇒ **mô tả, không chặt**.
- Bỏ Vingroup (VIC/VHM/VRE/VPL) + BSR: tỷ lệ 1,42, p91,6. Trung vị từng mã: 1,36, p74,8.

## 5. Khoá đầu vào

- `inputs/dd_price_zones_da6018d95.json` = `git show da6018d95:kb/dd_price_zones.json`, md5 **74539e4c…**, đúng bản R1 đã băm.
- ⚠ **Phát hiện**: D1 đọc bản **e547cd7fc** (17:14Z, md5 9e4cab03…; PAT/TCH/VGS đã chuyển REFUTED_OPEN). R1 đọc da6018d95 (17:02Z; ba mã đó FIXED_UNVERIFIED). Tâm 36 mã **giống hệt** giữa hai bản (D2 assert), chỉ nhãn skeptic khác ⇒ R1/R2 không bị ảnh hưởng. Cả hai bản được đóng băng trong `inputs/`.
- `inputs/value_radar_series_frozen.csv` md5 11aa1526… (= bản R1 băm). Danh sách đầy đủ ở `rerun/INPUTS.md5`.

## N độc lập & điều KHÔNG kết luận được

- N = 227 tháng (2008-01→2026-11), cửa sổ 10Y = 120 tháng. Chuỗi định giá tự tương quan rất cao ⇒ N độc lập hiệu dụng **ước lượng 3–5 chu kỳ** trong 10 năm. Mọi phân vị là **mô tả vị trí**, không có p-value.
- **Không chốt được**: (a) độ lớn "thị trường vs công bằng kiểu DD": dấu đổi theo ROE giả định và g; (b) tỷ phần r-vs-ROE: 1% đến 80% tuỳ chuẩn hoá ROE; (c) "chế độ mới" sau FTSE (không chạy lại, ngoài phạm vi).
- Không đo lại H2 (cấu trúc rổ), H4-OShares, nhóm DD-like (ngoài phạm vi rerun): số R1 giữ nguyên, kèm caveat skeptic (OShares lệch ex-date 599 sự kiện; ticket F riêng).
