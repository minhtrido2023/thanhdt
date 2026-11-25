# Dự báo earnings quý ↔ khoảng cách tâm-giá — REPORT (job Taylor_20261125_011012, 25/11/2026)

Chỉ nghiên cứu, chưa qua quant-skeptic. Không sửa production, không wire. Thiết kế khoá trước ở `PRELOCK.md` (commit 6e0f65b6f); mọi test dưới đây là test đã khai, không thêm biến thể.
Nguồn số: `out/A_summary.csv`, `out/A_segments.csv`, `out/B_results.csv`, `out/B_gap_by_cu.csv`, `out_C/metrics2_C.csv`, `out_C/C_diff.csv`, `out_C/C_pbo.json` (md5 ở `MD5SUMS`).

## Kết luận (4 dòng)
1. **Luận đề của user ĐÚNG về mặt mô tả**: khoảng cách tâm-giá của D0 phần lớn là SAI SỐ DỰ BÁO EARNINGS NGẦM của chính mô hình. D0 giả định ROE = trung bình 5 năm; giả định này dự báo LNST quý **tệ hơn naive mùa vụ 18–27%** và **lạc quan có hệ thống**. Mã mà D0 đánh giá quá cao earnings thì bị D0 gọi là "rẻ" — và thị trường đúng.
2. **Mô hình dự báo đơn giản (ENS) hơn naive ~10–12% ở quý kế** (cả IS và OOS, CI 99,3% < 1); từ quý thứ 3 trở đi không hơn. Sai số trung vị vẫn ~1,06% vốn chủ/quý, MdAPE ~45% ⇒ earnings quý VN khó dự báo, lợi thế nhỏ.
3. **Giá KHÔNG "hội tụ về tâm" khi earnings lộ** (B3 null cả hai era). Thông tin thị trường có trước về earnings tương lai được E/P bắt tốt hơn gap D0.
4. **Vòng cập nhật**: C2 (hiệu chỉnh thiên lệch, co về ngành) nâng IC36 OOS của D0 +0,022 (CI 99,17% [+0,011; +0,046]), IS ≈ 0, không làm xấu U-hit/cảnh báo đắt — **nhưng vẫn dưới E/P đơn giản (0,230 vs 0,256) và IC phần dư không tăng** ⇒ theo tiêu chí khoá: **chưa đạt "đáng nghiên cứu tiếp"**, cải thiện chủ yếu là kéo D0 về phía E/P.

## A. Năng lực dự báo LNST quý (h = 1; sai số e = (thực − dự báo)/vốn chủ gốc)
| Mô hình | MdAE IS | R vs naive IS [CI99,3] | MdAE OOS | R vs naive OOS [CI99,3] | thiên lệch trung vị OOS | hit hướng OOS |
|---|---|---|---|---|---|---|
| SRW (naive mùa vụ) | 1,20% | 1 | 1,21% | 1 | +0,15% | — |
| TTM4 | 1,09% | 0,922 [0,873; 0,989] | 1,06% | 0,884 [0,843; 0,935] | 0,00% | 70,6% |
| MxR (biên × doanh thu) | 1,09% | 0,916 [0,877; 0,969] | 1,09% | 0,898 [0,862; 0,935] | −0,02% | 67,1% |
| MR (ROE về TB 5 năm, φ 0,65/năm) | 1,09% | 0,924 [0,886; 0,981] | 1,06% | 0,883 [0,836; 0,934] | −0,05% | 70,6% |
| **ENS** = trung vị(SRWD, MxR, MR) | **1,06%** | **0,903 [0,853; 0,952]** | **1,06%** | **0,876 [0,848; 0,906]** | −0,04% | 68,2% |
| SRWD (Foster drift) | 1,44% | 1,211 | 1,47% | 1,215 | 0,00% | 55,2% |
| **D0imp** = roe_tc5·E/4 (earnings ngầm của D0) | 1,52% | **1,271 [1,218; 1,407]** | 1,42% | **1,182 [1,090; 1,277]** | **−0,42%** | 64,2% |
- N: IS 5.758 sự kiện / 24 quý / 6 năm; OOS 10.609 / 27 quý / 7 năm (mẫu chung mọi mô hình). CI = bootstrap khối năm.
- h=2: ENS OOS 0,918 [0,872; 0,958] đạt, IS 0,964 [0,932; 1,016] KHÔNG đạt. h=3,4: không mô hình nào đạt cả hai era ⇒ năng lực dự báo chỉ có ở 1–2 quý.
- D0imp lệch âm ở mọi lớp quy mô/biến động, nặng nhất nhóm biến động ROE cao (OOS −0,96%/quý ≈ −3,8 điểm ROE/năm) và bất động sản (OOS R 1,52). Ngân hàng là ngoại lệ: D0imp lệch DƯƠNG (+0,46%/quý — ROE ngân hàng tăng nhanh hơn trung bình 5 năm).
- ENS hơn naive ở hầu hết ngành; không hơn ở chứng khoán IS (R 1,04) và bất động sản (R ~0,96) — mô tả, chưa có CI theo lớp.

## B. Sai số dự báo giải thích gì về gap = log(tâm D0 / vốn hoá) tại ngày công bố
gap tính bằng giá THÔ × số CP cùng ngày công bố (không dùng mc tháng của panel — tránh lỗi mc V3.1). N: IS 5.848 / OOS 10.973 sự kiện; theo quý rồi bootstrap năm.
| Test | IS IC [CI95] | OOS IC [CI95] | Đọc |
|---|---|---|---|
| B1 gap vs sai số D0imp tích luỹ 4 quý | **−0,453 [−0,512; −0,386]** | **−0,302 [−0,344; −0,264]** | mô hình đánh giá cao earnings ⇒ "rẻ" |
| B1 cùng, kiểm soát E/P, quy mô, chất lượng, momentum | −0,404 [−0,459; −0,348] | −0,361 [−0,396; −0,326] | không phải hiệu ứng E/P |
| B1 \|gap\| vs \|sai số ENS tích luỹ\| | +0,074 [+0,032; +0,116] | +0,059 [+0,031; +0,088] | độ lớn có liên hệ, yếu |
| B2 gap → sai số D0imp 4 quý TỚI | −0,519 | −0,357 [−0,382; −0,331] | gap dự báo D0 sẽ còn sai tiếp |
| B2 gap → sai số ENS 4 quý tới | −0,143 | −0,055 [−0,073; −0,029] | |
| B2 cùng, sau 4 kiểm soát | +0,005 [−0,016; +0,023] | +0,038 [+0,009; +0,071] | gap ≈ không thêm gì về surprise thật |
| B2 null: E/P → sai số ENS 4 quý tới | −0,334 | −0,259 | E/P cao báo trước earnings giảm |
| ΔIC (gap − E/P) cho sai số ENS | +0,191 [+0,163; +0,212] | +0,203 [+0,118; +0,298] | gap KÉM E/P về "thị trường biết trước" |
| B3 gap → lợi suất giữa 2 kỳ công bố (~60 phiên) | −0,007 [−0,039; +0,020] | +0,109 [+0,070; +0,147] | OOS dương nhưng… |
| B3 null E/P → cùng cửa sổ | +0,031 | +0,129 [+0,091; +0,169] | …E/P cao hơn; Δ CI chứa 0 |
| B3 gap → lợi suất quanh công bố kế (±2 phiên) | −0,013 [−0,067; +0,038] | +0,005 [−0,022; +0,034] | **không hội tụ khi earnings lộ** |
| B3 tập trung (IC/phiên quanh công bố − IC/phiên trước đó) | −0,003 [−0,016; +0,009] | −0,001 [−0,007; +0,007] | null |
| B3 SUE → lợi suất ±2 phiên (đối chứng: phản ứng earnings có tồn tại) | +0,038 [+0,024; +0,054] | +0,028 [+0,015; +0,040] | thị trường có phản ứng, nhỏ |
Mô tả (tercile sai số D0imp 4 quý, `B_gap_by_cu.csv`): mã mà D0 đánh giá CAO earnings ~7–9 điểm ROE/năm có gap trung vị +0,27 (IS) / +0,02 (OOS); mã D0 đánh giá THẤP ~5–8 điểm có gap −0,41 / −0,46.
⇒ Chênh "tâm vs giá" của D0 phần lớn là giá đã phản ánh earnings hiện tại mà D0 (bám ROE 5 năm) chậm nhận ra. Đây là vấn đề của mô hình, không phải cơ hội giá.

## C. Vòng cập nhật (code đo V3 `d_metrics2.py` nguyên văn md5 6b36320c…; chân control D0 và E/P tái lập ĐÚNG từng số V3)
| | IC36 IS | IC36 OOS | ΔIC36 vs D0 OOS [CI99,17] | ΔIC36 vs D0 IS [CI99,17] | IC36 phần dư OOS | U-hit IS/OOS | cảnh báo đắt đúng (O_right_rel) IS/OOS |
|---|---|---|---|---|---|---|---|
| D0 (control) | 0,138 | 0,208 | — | — | 0,110 | 60,3% / 70,5% | 71,0% / 68,1% |
| C1 hiệu chỉnh thiên lệch theo mã | 0,120 | 0,210 | +0,002 [−0,016; +0,057] | −0,018 [−0,055; +0,016] | 0,050 | 63,9% / 74,1% | 70,1% / 69,5% |
| **C2 co về ngành** | 0,139 | **0,230** | **+0,022 [+0,011; +0,046]** | +0,001 [−0,030; +0,025] | 0,105 | 58,9% / 72,0% | 70,4% / 68,7% |
| C3 roe_n = dự báo ENS 4 quý | 0,122 | 0,201 | −0,007 [−0,048; +0,060] | −0,015 | 0,022 | 66,5% / 79,4% | 69,7% / 67,0% |
| E/P (null) | 0,130 | **0,256** | C2 − E/P: −0,026 [−0,098; +0,020] | | −0,102 | — | — |
- Tiêu chí khoá: C2 đạt 3/4 vế (ΔOOS CI>0, ΔIS ≥ 0, U-hit/cảnh báo đắt không tệ hơn quá 5pp) và **TRƯỢT vế "IC36 OOS ≥ E/P"** ⇒ "cải thiện D0 nhưng không hơn E/P". C1, C3 trượt.
- IC phần dư (sau E/P, B/P, quy mô) của C2 0,105 ≈ D0 0,110 ⇒ phần cải thiện trùng thông tin E/P, không phải thông tin mới.
- C3 có U-hit cao hơn (79% OOS) nhưng IC phần dư sụp (0,022) và số sự kiện khác (282 vs 224) — không đọc như cải thiện.
- PBO (CSCV, IC36 năm 2014–2023, 4 cấu hình, 252 cách chia) = 0,187 — tham khảo; N năm nhỏ.
- **N độc lập rất mỏng**: OOS 36T = 15 as-of quý / 4 năm ≈ 1,3 cửa sổ 36T không chồng lấn; CI khối năm với 4 khối hẹp giả. Không đủ để wire.

## Hạn chế
- 1 vintage `ticker_financial`: không đo restatement giữa các lần công bố (chỉ kiểm nội bộ: NP_P1(q) = NP_P0(q−1) ở 99,3%).
- Survivorship: 4.053 quý của mã huỷ niêm yết (nguồn VND) không có NP_P* ⇒ vắng ở A/B; sai số D0imp thật có thể còn tệ hơn.
- C dùng mc tháng của panel V3 (mc_old phồng theo tỉ suất cổ tức; V3.1 đang vá). D0 và biến thể chung mc nên Δ cùng thước; mức tuyệt đối cần chạy lại sau V3.1 (`d_update.py` + `d_metrics2.py`, ~1 phút).
- C3 dùng `nanmedian` ENS (cho phép thiếu MxR), A dùng ENS chỉ khi đủ 3 thành phần — khác nhỏ, ghi rõ.
- Không có chi phí/khả năng giao dịch: đây là đo năng lực dự báo và chất lượng mô hình định giá, không phải chiến lược.

## Hàm ý cho mô hình định giá (đề xuất, chưa có quyết định)
- Earnings ngầm của RIM-VN D0 (ROE = TB 5 năm) là MẮT XÍCH YẾU NHẤT: tệ hơn naive. Bất kỳ bản tâm giá nào nên hiển thị kèm "earnings ngầm vs dự báo ENS vs thực tế 4 quý" — một dòng chẩn đoán vì sao tâm lệch giá (display-only).
- Muốn tâm bám earnings tốt hơn: C2 là ứng viên duy nhất qua vế cải thiện; nhưng không vượt E/P ⇒ chưa có cơ sở thay D0. Nếu user muốn đi tiếp: chạy lại sau V3.1, rồi quant-skeptic.
- Không mở tín hiệu giao dịch từ "gap lớn sẽ đóng khi earnings lộ" — B3 null.

## Tái lập
```
cd agents/Taylor/research/dcf_earnings_forecast_20261125d/calc; PY=/home/trido/thanhdt/wc_venv/bin/python
$PY a_events.py && $PY b_forecast.py && $PY c_gap.py && $PY d_update.py
OUT_DIR=$PWD/../out_C ONLY=D0,C1,C2,C3,EP SFX=_C $PY ../in_snapshot/d_metrics2.py && $PY e_cdiff.py
```
Đầu vào snapshot `in_snapshot/vp2.parquet` md5 daaa63ec… (= V3 152e83c11); cache `data/bq_cache` tại 25/11/2026.
