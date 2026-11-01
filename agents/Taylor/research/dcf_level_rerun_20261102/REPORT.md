# REPORT — hiệu chuẩn MỨC ĐỊNH GIÁ (level) chạy lại trên đường LIVE · job Taylor_20261101_175734 · 02/11/2026
R&D thuần, không sửa `dcf_valuation.py`, không wire. Tiền đề: `dcf_vn_calibration_20261101/REPORT.md` đề xuất s=0 + g_T 4,5%; quant-skeptic REFUTED (medium).

## Kết luận
1. **Không có g_T duy nhất đáng tin. Giữ `domestic_v2` (g_T 5,5%) làm mặc định.** Tiêu chí hội tụ viết trước (PREREG): phân cách giữa nhóm ổn định/nhảy ≤1,0pp. Đo được **3,50pp** (s=0) và **2,75pp** (s=0,5) trên đường live.
2. **Đường live gần như trùng đường fin** (chỉ 5,37% dòng-tháng khác số CP): g_T* s=0 toàn kỳ **4,5% ở cả hai đường**, IS 4,0 / OOS 5,0. Giả thuyết "live sẽ kéo g_T về 3%" của skeptic **không đúng**; phản biện chính (nhóm tách đôi) **đúng**.
3. Nhóm OShares ổn định (62,7%) cần g_T* **3,0%** (chạm sàn lưới; mở rộng ngoài PREREG: 2,75% full, IS 1,5 / OOS 3,0); nhóm nhảy (37,3%) cần **6,5%**. 4,5% là trung bình của hai nhóm lệch ngược chiều — không nhóm nào thật sự ở 4,5%.
4. Cú nhảy P/FV tại bước OShares (+0,237 log, 450 bước) **biến mất trên đường live (+0,021)** — tức là phần "trễ vendor" được live vá. Nhưng **mức P/FV sau bước vẫn cao dai dẳng** (1,61 sau 0–3 tháng → 0,94 sau 36–60 tháng; mã chưa từng bước: 0,82, đường live). Đây là hiệu ứng cấu trúc (FCFE nền 3 năm / số CP mới), không phải restatement nhất thời; nó là thứ tạo ra hố giữa hai nhóm.
5. s=0 vẫn thắng về độ chính xác tăng trưởng: Δ MAE K=5 = **−0,027, CI95 [−0,045; −0,016]** (khối theo năm, 5.000 lần), s=0 tốt hơn ở 10/12 năm. Cái bị bác là **mức g_T**, không phải cấu trúc s=0.
6. SELFCHECK live: engine = `fair_value` (OSHARES_SOURCE=live) **0 lệch / 331 mã** (30/10/2026 và 31/10/2025, TZ mặc định / `env -u TZ` / NY).

## Việc 1+2 — g_T* (%), nguồn `out/level_gT_star.csv` (metric: TB năm của median log P/FV theo tháng; lưới 3,00–8,00% bước 0,25)
| Đường | s | Nhóm | n dòng | toàn kỳ | IS ≤2019 | OOS ≥2020 | LOYO min–max | median P/FV @4,5% | @5,5% |
|---|---|---|---|---|---|---|---|---|---|
| **live** | 0 | tất cả | 22.988 | **4,50** | 4,00 | 5,00 | 4,25–4,75 | 1,00 | 0,86 |
| live | 0 | (a) ổn định | 14.423 | 3,00* | 3,00* | 3,75 | 3,00–3,00 | 0,80 | 0,69 |
| live | 0 | (b) nhảy | 8.565 | 6,50 | 6,00 | 7,00 | 6,25–6,75 | 1,38 | 1,19 |
| live | 0 | (c) loại sau bước | 21.584 | 4,25 | 3,75 | 4,75 | 4,00–4,50 | 0,96 | 0,83 |
| fin | 0 | tất cả | 22.988 | 4,50 | 4,00 | 5,00 | 4,25–4,75 | 0,99 | 0,85 |
| fin | 0 | (a) / (b) / (c) | | 3,00* / 6,50 / 4,25 | 3,00* / 5,75 / 3,50 | 3,75 / 7,00 / 4,75 | | | |
| live | 0,5 | tất cả | 22.988 | 3,25 | 3,00* | 4,25 | 3,25–3,75 | 0,88 | 0,78 |
| live | 0,5 | (a) / (b) / (c) | | 3,00* / 5,75 / 3,00* | 3,00* / 5,00 / 3,00* | 3,00* / 6,25 / 4,00 | | | |
| fin | 0,5 | tất cả | 22.988 | 3,25 | 3,00* | 4,00 | 3,00–3,50 | 0,87 | 0,77 |
| fin | 0,5 | (a) / (b) / (c) | | 3,00* / 5,50 / 3,00* | 3,00* / 4,75 / 3,00* | 3,00* / 6,25 / 3,00–4,00 | | | |

`*` = chạm sàn lưới (giá trị thật ≤ số này). **Phân cách (b)−(a), toàn kỳ:** live s=0 **+3,50pp**, live s=0,5 **+2,75pp**, fin s=0 +3,50pp, fin s=0,5 +2,50pp.
Cờ ổn định = đúng `robust.py` (OShares quý đổi >10% trong ±4 quý, tâm) ⇒ **dùng quý tương lai, chỉ để chẩn đoán**, không dùng làm bộ lọc live. g_T thô (CPI5Y+GDP15Y) trong panel: min 8,77% ⇒ cap lưới luôn là g_T hiệu dụng.
Loại riêng các dòng ngay sau bước OShares (c) chỉ dịch g_T* 4,5→4,25: **bước đơn lẻ không giải thích hố giữa hai nhóm**; hố nằm ở tính chất dai dẳng của nhóm phát hành (Việc 3B).

**Tác động live 30/10/2026** (n=147; `out/level_live_impact_20261030.csv`; V0 = production live, s=0,5, g_T 5,5%: RẺ 66,0%, RICH sâu 27):
| Cấu hình (live) | FV trung vị vs V0 | %RẺ | RICH sâu (MoS<−100%) |
|---|---|---|---|
| s=0, g_T 4,5% (toàn kỳ) | −35,94% | 51,7% | 36 |
| s=0, g_T 3,0% (nhóm ổn định) | −47,10% | 46,9% | 42 |
| s=0, g_T 6,5% (nhóm nhảy) | −12,00% | 66,0% | 28 |
| s=0,5, g_T 3,25% (toàn kỳ) | −23,63% | 53,7% | 35 |
Cùng một cổ phiếu có thể RẺ hay ĐẮT tuỳ chọn g_T trong dải 3,0–6,5% — đó chính là độ bất định thật, không phải sai số làm tròn.

## Việc 3 — cú nhảy P/FV sau bước OShares: pha loãng vs restatement (`out/events_*.csv`)
450 bước quý (OShares đổi >10%, 2014+, FV hợp lệ cả hai tháng). Phân loại theo ISS/AIS executed (BQ `corporate_action`, shares_delta hoặc issue_volumn) trong (kỳ trước−45 ngày, ngày công bố]:
| Lớp | n | median ΔlogP/FV (fin) | (live) | median ΔlogOShares | median ΔlogP |
|---|---|---|---|---|---|
| Pha loãng: ISS/AIS khớp ≥80% | 171 | +0,224 | +0,008 | +0,182 | −0,008 |
| Tăng, giải thích một phần | 36 | +0,412 | +0,130 | +0,404 | +0,005 |
| Tăng, KHÔNG có sự kiện trong feed | 235 | +0,236 | +0,026 | +0,274 | −0,020 |
| Giảm (gộp/restate) | 8 | −0,073 | −0,073 | −0,132 | +0,057 |
Đồng nhất ΔlogP/FV = ΔlogP + ΔlogOShares − Δlog(FCFE nền·tăng trưởng): sai số tối đa 2,9e−15. **Median Δlog(FCFE nền) = 0** — FCFE nền (CF_OA_3Y, cập nhật theo năm) không tăng khi số CP tăng, nên FV/cp rơi cơ học đúng bằng ΔlogOShares, còn giá không rơi tương ứng (giá đã điều chỉnh ở ex-date trước, hoặc phát hành giá thị trường).
**10 sự kiện truy vết** (`out/events_10.csv`; 5 nhảy lớn nhất + 5 ngẫu nhiên seed 20261102):
| Mã | kỳ trước → kỳ mới | CP trước → sau | ΔlogP/FV | Nguồn |
|---|---|---|---|---|
| SLS | 25/10/2016 → 20/01/2017 | 6,80tr → 8,16tr | +4,12 | ISS cổ tức CP + AIS 16/01/2017 (khớp); base FCFE đổi −3,96 (nền nhỏ/âm) |
| CVT | 20/10/2014 → 21/01/2015 | 8,0tr → 16,0tr | +3,38 | ISS quyền mua + AIS 21/01/2015 (khớp) |
| KMR | 03/11/2014 → 02/02/2015 | 34,4tr → 44,4tr | +2,66 | ISS cổ phiếu thưởng + AIS 22/01/2015 (khớp 0,81) |
| HHS | 25/10/2019 → 22/01/2020 | 249,7tr → 274,7tr | +2,27 | KHÔNG có sự kiện trong feed (+10%); base đổi −1,97 |
| C47 | 27/10/2021 → 21/01/2022 | 21,5tr → 27,5tr | +1,98 | ISS thưởng + cổ tức CP + AIS 27/10/2021 (khớp 0,94) |
| DCL | 20/07/2016 → 20/10/2016 | 40,2tr → 56,3tr | +0,51 | ISS thưởng + AIS 07/09/2016 |
| C32 | 03/05/2017 → 01/08/2017 | 11,2tr → 13,7tr | +0,18 | không sự kiện trong feed |
| FPT | 04/05/2015 → 03/08/2015 | 343,9tr → 397,4tr | +0,08 | ISS cổ tức CP 21/07/2015 + AIS |
| FPT | 22/04/2022 → 01/08/2022 | 907,6tr → 1.097,0tr | +0,23 | ISS CBCN 01/04/2022 + cổ tức CP 19/07/2022 + AIS |
| KDH | 01/08/2016 → 28/10/2016 | 180,0tr → 234,0tr | −0,00 | không sự kiện trong feed; giá rơi −0,26 (giá đã phản ánh) |
Ba ca lớn nhất (SLS, CVT, KMR) có ΔlogP/FV +2,7…+4,1 vì **FCFE nền đổi cùng lúc** (−2,4…−4,0 log: nền gần 0 hoặc đổi dấu) — nhiễu của FCFE nền mỏng, KHÔNG phải sự kiện số CP thuần. Phần số CP thuần là ΔlogOShares cột trước.
**Trên đường live, cú nhảy biến mất** (+0,237 → +0,021 toàn bộ; cả lớp "không có sự kiện trong feed" +0,236 → +0,026): live đã biết số CP mới ngay khi giá điều chỉnh. Vậy cú nhảy là **trễ cập nhật số CP của `fin`**, không phải restatement; ≥52% bước không tìm thấy ISS/AIS khớp trong feed (không xác định được nguồn — có thể phát hành riêng lẻ/ESOP/chuyển đổi nằm ngoài cửa sổ).
**3B — dai dẳng** (live, s=0, g_T 4,5%; `out/events_persistence.csv`), median Price/FV theo tháng kể từ bước TĂNG OShares >10% gần nhất: 0–3t **1,61** (n=1.455) · 3–6t 1,53 · 6–12t 1,44 · 12–24t 1,22 · 24–36t 1,12 · 36–60t 0,94 · >60t 0,87 · chưa từng bước **0,82** (n=5.400). Mức cao kéo dài ~3 năm ngay cả khi số CP đã đúng ⇒ nhóm phát hành bị FV thấp có hệ thống (FCFE 3 năm chưa phản ánh vốn mới) HOẶC là nhóm tăng trưởng mà thị trường trả giá cao hơn FCFE quá khứ. **Hai cách đọc này không tách được bằng dữ liệu đã dùng.**

## Việc 4 — bootstrap MAE (`out/boot_mae_k.csv`)
Tái lập 0,502 vs 0,530 (K=5, n=4.293, 12 năm gốc). Δ = MAE(s=0) − MAE(s=0,5) = **−0,0274, CI95 [−0,0447; −0,0158]**; s=0 tốt hơn 10/12 năm. Phụ: K=3 Δ −0,0190 [−0,0273; −0,0104], 12/14 năm; so cặp theo dòng K=5 −0,0263 [−0,0320; −0,0199]. CI không chứa 0 ⇒ s=0 chính xác hơn s=0,5 về đường tăng trưởng NP (bài kiểm tra này không thay IC của MoS).

## Việc 5 — khuyến nghị
- **g_T: KHÔNG hội tụ ⇒ giữ `domestic_v2` (5,5%).** Đây là kết quả hợp lệ, không ép ra một con số. 5,5% cũng không "đúng" cho nhóm nào (median P/FV @5,5%: ổn định 0,69, nhảy 1,19, chung 0,78 trên live s=0,5) — nó chỉ nằm trong dải 3,0–6,5% mà dữ liệu không thu hẹp được.
- **s=0** được ủng hộ về độ chính xác (Việc 4) và IC trung tính (báo cáo trước, ΔIC12 −0,0035 CI chứa 0) nhưng **không đi kèm "level fix"**. Nếu về sau có quyết định đổi s, đừng đổi g_T cùng lúc theo báo cáo này.
- **Nhãn MoS (trung thực):** dù s nào, MoS = (FV−giá)/FV với g_T cố định là **chỉ số xếp hạng tương đối**, không phải "giá trị nội tại". Nhãn đề xuất: *"MoS (FCFE, g_T cố định) — so sánh giữa các mã, KHÔNG so với giá; trung vị thị trường đọc P/FV ≈ 0,8–1,0 tuỳ g_T"*. Chưa sửa code (ngoài phạm vi R&D); chờ quyết định.

## KHÔNG chứng minh được (đọc trước khi trích số)
1. **Nguyên nhân hố giữa hai nhóm**: nhóm phát hành vs nhóm tăng trưởng/vốn nặng không tách được; không có thử nghiệm nhân quả nào ở đây.
2. Cờ nhóm dùng quý tương lai (±4) — chẩn đoán, không phải tín hiệu dùng được; IS/OOS của từng nhóm không phản ánh phân loại PIT.
3. **Khoá khung ex-date R5/R8/R9 của production KHÔNG tái lập được cho lịch sử** (cần `event_status` tại thời điểm asof; BQ chỉ giữ trạng thái hôm nay). Đường "live" lịch sử = `oshares_pit` + R10 (live thuần). Kiểm chứng: tại 30/10/2026 và 31/10/2025 số CP dựng lại **trùng 331/331** số CP production thật, nên khoá khung hiếm khi cắn ở hai ngày này — nhưng chỉ 2 ngày, tỉ lệ rơi về số quý ở các năm khác chưa đo.
4. Chuẩn "median P/FV = 1" là giả định thị trường không định sai ở trung vị; bản thân nó là định giá tương đối (đúng điểm skeptic nêu). g_T* đo ở đây là g_T làm thị trường "đúng ở trung vị", không phải g_T đúng về kinh tế (3,0% < lạm phát 5%+ là dấu hiệu mô hình chứ không phải kết luận về tăng trưởng dài hạn).
5. Lưới 0,25pp; sàn lưới 3,0% làm nhiều ô (a) bị kiểm duyệt. Mở rộng 0–3% (`out/ext_grid_below3.csv`) là NGOÀI PREREG: s=0 nhóm ổn định 2,75% (IS 1,5 / OOS 3,0); s=0,5 nhóm ổn định 1,25% (IS 0,0) — phi thực tế, cho thấy s=0,5 làm hỏng mức của nhóm ổn định.
6. N độc lập thấp: 12–14 năm gốc (MAE), 155 tháng tương quan mạnh (level). Không tính DSR vì đây là hiệu chuẩn mức, không phải chọn tín hiệu theo lợi suất; số ô thử: 2 cấu trúc × 21 g_T × 2 đường × 4 nhóm = 336.
7. Panel tăng trưởng (Việc 4) chỉ gồm mã có NP>0 đầu kỳ — thiên lệch sống sót (đã nêu ở báo cáo trước, chống lại s=0 nên bảo thủ).
8. Dữ liệu vendor vintage 30/10/2026 (không PIT hoàn toàn); CPI tháng 09–12/2026 là forward-fill (cảnh báo `cpi_vn`), không ảnh hưởng g_T vì cap 5,5%/lưới chặn (g_T thô ≥8,77%).

## Tái lập (đường dẫn thư mục này; interpreter `/home/trido/thanhdt/wc_venv/bin/python`, `source wc_env.sh` trước)
`build_live.py` (BQ, ~3 phút) → `level.py` → `events.py` → `ext_grid.py` → `boot_mae.py` → `selfcheck_live.py 2026-10-30 2025-10-31`. Dữ liệu nền: `../dcf_vn_calibration_20261101/data/*` (dựng lại bằng `engine.py build`). Log: `out/run_*.txt`.
