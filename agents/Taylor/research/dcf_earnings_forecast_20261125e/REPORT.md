# J4: chu kỳ ngành bằng chuỗi PIT nội sinh từ BCTC (hướng C, job Taylor_20261125_021625, 25/11/2026)

Chỉ nghiên cứu. Chưa qua quant-skeptic. Không wire, không merge, không email.
- Thiết kế khoá ở `PRELOCK_J4.md`, commit `c6c53f113`, trước mọi mô hình.
- Commit theo bước: PRELOCK `c6c53f113` → panel V3.2 `a04e6e9f9` → fit 2a `055e5a037` → kết quả + REPORT (commit này).

## Kết luận (đọc trước)
1. **Không có chuỗi giá ngành PIT nào phủ IS 2014–2019 ngoài World Bank.** Kết luận J3 §0 đứng nguyên sau khi tra lại `data_registry`.
   ⇒ J4 chỉ dùng chỉ báo nội sinh từ BCTC, tính bằng trung vị NGÀNH (ICB4), **loại chính mã** (LOO), ≥ 5 mã ngang hàng, PIT theo `known`.
   Bốn chỉ báo: S1 ROE, S2 biên gộp, S3 chu kỳ tiền, S4 capex/doanh thu.
2. **Không biến thể nào đạt GO.** Cả 5 biến thể đều thua E/P ở OOS, khoảng −0,036 đến −0,039 IC36, chỉ 1/4 năm hơn. Không biến thể nào hơn D0 ở ≥ 3/4 năm. DSR tối đa 0,765 < 0,95.
3. **Tiêu chí "không có gì mới" KHÔNG bị kích hoạt về mặt kỹ thuật**, nhưng độ lớn gần bằng 0:
   - **M4** (độ bền của chênh ROE giảm khi capex ngành cao hơn chuẩn; φ1 = −0,196) hơn null P1:
     - OOS +0,0019 IC36, 3/4 năm;
     - IS +0,0023, 5/6 năm;
     - PBO {P1, M1..M5} = 0,024.
   - **M2** (biên gộp ngành) hơn P1 +0,0001, 3/4 năm, tức là nhiễu.
   - Lấy thước so sánh: P1 so với D0 đã là +0,0095; E/P so với P1 là +0,038.
     Phần M4 thêm vào cỡ 1% IC36 (0,2205 so với 0,2186), không có ý nghĩa thực dụng.
   ⇒ Đề xuất đọc: **NO-GO cho mô hình hoá, coi như "không có gì mới đủ dùng"**. Mike/user quyết A → B theo kế hoạch. Không thử thêm biến thể (đúng PRELOCK).
4. **Null persistence P1 tự nó** (roe_n = tc + 0,466·g, φ fit IS) đứng ở đâu:
   - OOS so với D0: +0,0095 IC36, nhưng chỉ 2/4 năm.
   - Dự báo ROE tương lai tốt hơn hẳn: R² OOS 0,305 so với 0,217 của D0.
   - Nhưng P1 **xoá phần thông tin riêng** của D0: IC36 phần dư 5 biến OOS là −0,002, so với +0,089 của D0.
   ⇒ "Dự báo ROE tốt hơn" không chuyển thành "xếp hạng lợi suất tốt hơn". D0 hơn E/P/B/P ở chỗ nào thì đó lại là chỗ nó KHÔNG ngoại suy ROE hiện tại.
5. **Vá mc ảo V3.2** (bắt buộc từ skeptic J3):
   - **Luật mới:** N chỉ bước khi `Δlog(Close/Price) ≥ 0,5·log(N_next/N)`, tức khi có sự kiện cổ phiếu thật, không phải cổ tức tiền.
   - **Phạm vi:** đổi 609 / 56.549 dòng in_universe 2014+ (1,08%). Skeptic đo ~0,6%. Luật V3.2 thận trọng hơn vì giữ N cũ cả ở các ca quyền mua.
   - **Ba ca skeptic chỉ ra (mc, tỷ VND):**
     - ACG 2022-03: 13.978 → 9.018;
     - ABI 2025-07: 2.838 → 2.027;
     - TCB 2024-05: 331.116 → 165.558 (mc_old 170.697).
   - **Ảnh hưởng tới số đo:** ALL OOS D0 0,210 → 0,209; E/P 0,258 → 0,2566. Không đổi kết luận nào của J3.

## Bảng chính (ALL, IC36; `out_ALL/J4_diff.csv`, `J4_verdict.json`)
| Biến thể | IC36 IS / OOS | Δ so với P1 IS (năm +) | Δ so với P1 OOS (năm +) | Δ so với D0 OOS (năm +) | Δ so với EP OOS (năm +) | DSR so với P1 |
|---|---|---|---|---|---|---|
| D0 | 0,1373 / 0,2090 | | | | | |
| EP | 0,1285 / 0,2566 | | | | | |
| P1 (null) | 0,1382 / 0,2186 | — | — | +0,0095 (2/4) | −0,0381 (1/4) | — |
| M1 phân rã ngành/riêng | 0,1386 / 0,2184 | +0,0004 (4/6) | −0,0002 (1/4) | +0,0094 (2/4) | −0,0383 (1/4) | 0,099 |
| M2 pha GPM ngành | 0,1389 / 0,2187 | +0,0007 (5/6) | +0,0001 (3/4) | +0,0096 (2/4) | −0,0380 (1/4) | 0,261 |
| M3 pha chu kỳ tiền ngành | 0,1387 / 0,2187 | +0,0004 (4/6) | +0,0001 (2/4) | +0,0097 (2/4) | −0,0380 (1/4) | 0,176 |
| **M4 pha capex ngành** | 0,1405 / 0,2205 | +0,0023 (5/6) | **+0,0019 (3/4)** | +0,0115 (2/4) | −0,0362 (1/4) | **0,765** |
| M5 pha ROE ngành | 0,1383 / 0,2179 | +0,0000 (2/6) | −0,0006 (0/4) | +0,0089 (2/4) | −0,0387 (1/4) | 0,013 |
- M4 OOS theo năm so với P1: 2020 +0,0047 · 2021 +0,0003 · 2022 +0,0034 · 2023 −0,0015.
- M4 so với D0 OOS theo năm: +0,010 · −0,005 · −0,003 · +0,054. Phần thắng D0 gần như chỉ đến từ 2023.
- Hệ số fit IS (`out_ALL/fit.json`, 4.254 dòng / 466 mã), dạng [φ0, φ1]:
  - P1: 0,466.
  - M1 [φ_ngành, φ_riêng]: [0,400; 0,460]. Phần chênh ROE do ngành bền gần bằng phần riêng, nên phân rã không thêm gì.
  - M2 [0,442; −0,022] · M3 [0,447; −0,154] · M4 [0,449; −0,196] · M5 [0,456; −0,074].
- Phụ (`out_{CYC,REST}`): trong CYC (COMM + CYC_HI), M2 so với P1 có IS +0,0067 (6/6) và OOS +0,0017 (3/4).
  M4 trong CYC: OOS +0,0005 (2/4). Trong REST: +0,0021 (3/4). Cùng cỡ 0,002, không tập trung ở mã chu kỳ.
- R² OOS dự báo ROE tương lai TB(+4 quý, +8 quý), trên 8.131 dòng:
  - D0 0,217 · P1 0,305;
  - M1 0,306 · M2 0,307 · M3 0,310 · M4 0,304 · M5 0,309.
  ⇒ Chỉ báo ngành không cải thiện dự báo ROE so với persistence một hệ số.

## Sự cố trong lúc chạy (phải đọc khi review)
- **Lần chạy đầu sai.** Selfcheck LOO báo FAIL: 252/300 dòng S1 không khớp.
  - Nguyên nhân: `groupby(...).indices` gọi trên frame đã lọc `icb.notna()` trả vị trí TƯƠNG ĐỐI, nên S1..S4 bị gán lệch dòng.
  - Sửa: dùng `.groups` (nhãn = vị trí sau `reset_index`). Sau khi sửa, kiểm LOO 0/300 lệch.
- Kết quả của lần chạy lỗi được giữ lại: `out_ALL/J4_verdict_BUGGY_loo_index.json`, `J4_diff_BUGGY_loo_index.csv`.
  - Lần đó cho NO_NEW = true: M4 so với P1 OOS +0,0003, 2/4 năm.
  - Sau khi sửa: NO_NEW = false, do M4 và M2 đạt 3/4 năm.
- **Bản sửa là sửa lỗi cơ học** (kiểm chứng bằng phép LOO tường minh), không phải biến thể mới. Nhưng nó đổi trạng thái của tiêu chí dừng sau khi đã thấy số. Skeptic nên soi điểm này.
- **Lựa chọn nhỏ chưa ghi trong PRELOCK** (đã chốt trong code trước lần chạy đầu):
  - mẫu fit chỉ lấy dòng `in_universe`;
  - S1 trong M1 dùng mức (cắt ±0,3), M2–M5 dùng hạng phần trăm;
  - capex dùng `|capex_ttm|`.

## Selfcheck (`calc/d_selfcheck_j4.py` → `out_ALL/selfcheck_{noTZ,ICT}.txt`)
12/12 PASS. md5 `406b9f5b9b64a6a44448865b0858ead1` giống nhau dưới `env -u TZ PYTHONHASHSEED=0` và `TZ=Asia/Ho_Chi_Minh PYTHONHASHSEED=12345`. Các kiểm tra:
- IC36 OOS của P1 / M4 / EP tính lại bằng vòng lặp tháng quý + scipy: 0,2186 / 0,2205 / 0,2566 (15 mốc).
- ΔIC36 M4 − P1 = +0,0019. Dung sai 0,002 cỡ bằng chính Δ, nên phép kiểm này chỉ xác nhận dấu và độ lớn thô, không xác nhận chữ số thứ 4.
- φ P1 tính lại bằng `lstsq` trên mẫu dựng lại theo đường khác: 0,4663, cùng 4.254 dòng.
- LOO S1: 0/300 lệch. PIT: 0 dòng `known > time`.
- Ba ca mc V3.2: |log(mc32/mc_old)| < 0,1.

## Hạn chế
- **N hiệu dụng:** OOS 4 năm (~1,3 cửa sổ 36 tháng độc lập), IS 6 năm, ~2–3 chu kỳ ngành lớn. Sign-count 3/4 năm có xác suất ngẫu nhiên 5/16 ≈ 0,31 dưới H0.
- ICB là phân ngành hiện tại, coi như tĩnh (13/1306 mã đổi): hindsight nhẹ về mô hình kinh doanh. ~16–20% dòng in_universe không đủ 5 mã ngang hàng, nên rơi về P1.
- 1 vintage `ticker_financial`. Mã huỷ niêm yết vắng ở đường BQ. Không có dữ liệu đơn hàng / doanh thu trả trước / khấu hao.
- `lv_*` của các mô hình tương đối (REL/MULT…) chỉ được dịch xấp xỉ theo mc mới. J4 không dùng chúng.

## Hàm ý (đề xuất, chưa quyết)
- Không wire M1–M5. Không đổi tâm D0 sang persistence P1: P1 dự báo ROE tốt hơn, nhưng làm mất thông tin xếp hạng riêng.
- Panel V3.2 (vá mc) nên thay V3.1 cho mọi lần chạy lại nhánh DCF-VN. Đây là sửa dữ liệu, độc lập với kết quả chu kỳ.
- Về chu kỳ, hướng C đã cạn với dữ liệu PIT hiện có. Muốn đi tiếp phải có chuỗi giá/tồn kho ngành PIT thật, phủ ≥ 2014, mà fleet hiện chưa có. Đó là việc của Winston (thu thập dữ liệu), không phải R&D mô hình.
