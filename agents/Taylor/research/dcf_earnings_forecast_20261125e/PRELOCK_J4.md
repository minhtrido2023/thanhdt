# PRELOCK J4: chu kỳ ngành bằng chuỗi PIT tốt hơn World Bank (job Taylor_20261125_021625, 25/11/2026)

Khoá TRƯỚC mọi dòng code mô hình chu kỳ. Chưa có số nào của J4 được tính khi viết file này.
Có 2 thứ đã nhìn trước khi khoá: (i) chẩn đoán mc ảo, chỉ đếm dòng, không tính IC; (ii) độ phủ cột `gpm`/`cashcycle`/`capex_ttm`/`roe` của panel V3.1 (98% / 91% / 75% / 96%).
Kế thừa nguyên văn từ `../dcf_earnings_forecast_20261125d/PRELOCK.md` + `PRELOCK_J3_CYCLE.md`, trừ chỗ ghi đè dưới đây:
- hàm `rim_vb` và tham số R = 12,25%, gT = 5,5%, κ = 0,4, H = 10;
- era IS 2014–2019 / OOS 2020–2023, đo bằng `d_metrics2.py` V3.1;
- universe = `in_universe`, IC Spearman theo ngày as-of, lợi suất 36 tháng.

## 0. Nguồn chuỗi: vì sao hướng (1) không có ứng viên mới
- Đã tra lại `mike/kb/data_registry/`. Kết luận loại ở PRELOCK_J3 §0 vẫn đúng:
  - TE (`commodity_prices`): từ 2016-10, `fetched_at` backfill 1 lần.
  - sunsirs: từ 2018, không PIT.
  - BDI: từ 2026-05.
  - heo: ~2026.
  - xút: dữ liệu tổng hợp (synthetic).
  - thép HRC: không có chuỗi PIT phủ IS.
- ⇒ **Hướng (1) KHÔNG có chuỗi giá ngành PIT nào phủ IS 2014–2019 ngoài WB CMO**, mà WB đã thua ở J3. J4 không thử lại WB.
- ⇒ J4 chỉ dùng hướng (2) + (3): **chỉ báo nội sinh theo ngành từ BCTC PIT, tính bằng cross-section ngành**.
  - PIT theo cấu trúc: mỗi dòng panel tháng t chỉ mang số BCTC có `known ≤ t`. Đây là assert của `b_panel.py` V3, J4 kiểm lại.
  - Lag công bố = `known` (ngày công bố thật, hoặc cuối quý + K của PRELOCK J2, theo `E_src`), không thêm giả định mới.
- Ngành: ICB 4 chữ số (`in/icb_pit_20251231.csv`, chép từ fixture `commodity_cycle_prereg_20261025`).
  - Kiểm BQ: chỉ 13/1306 mã từng đổi `ICB_Code` kể từ 2010 ⇒ coi như tĩnh.
  - Rủi ro hindsight nhẹ: đây là phân ngành HIỆN TẠI, nên lệch về mô hình kinh doanh, không lệch về kết quả. Khai làm hạn chế.
- Không dùng (thiếu trong `ticker_financial`): doanh thu trả trước / đơn hàng, khấu hao. "capex/khấu hao" thay bằng capex/doanh thu.

## 1. Vá mc ảo V3.1 (bắt buộc, chạy TRƯỚC mọi mô hình)
- **Lỗi:** V3.1 cho N bước sang `N_next` khi có cả hai điều kiện:
  - hệ số Close/Price đổi > 0,3% so với ngày công bố;
  - kỳ BCTC kế xác nhận N đổi > 1%.
  Nhưng cổ tức TIỀN cũng làm hệ số đổi. Hệ quả: N bước sớm, từ ngày GDKHQ cổ tức tiền thay vì ngày GDKHQ cổ phiếu thưởng/phát hành.
  Ca đã thấy: ACG 2022-03 (Δlr 0,048 so với log tỉ lệ N 0,438), ABI 2025-07/08, TCB 2024-05 (0,031 so với 0,693).
- **Luật V3.2:** chỉ cho N bước khi điều kiện V3.1 đúng **VÀ** `Δlr ≥ 0,5·log(N_next/N)` với `log(N_next/N) > 0,01`. Tức sự kiện giá phải có cỡ tương đương thay đổi số cổ phiếu.
  - Ngược lại giữ N tại ngày công bố. Với quyền mua có Δlr nhỏ hơn nửa tỉ lệ, mc bị thấp tạm thời cho tới kỳ BCTC kế. Đây là hướng thận trọng, có khai.
- Mọi cột `lv_*` của mô hình tuyệt đối dịch đúng `log(mc_V31/mc_V32)`. ep/bp/sp/ev tính lại.
- Báo cáo: số dòng đổi (in_universe 2014+), 3 ca trên trước/sau, D0/EP IC36 trước/sau vá.

## 2. Chỉ báo pha chu kỳ (chỉ cross-section ngành, LOẠI CHÍNH MÃ)
Tại mỗi dòng (mã i, tháng t): lấy trung vị trên các mã CÙNG ICB 4 chữ số, trừ i, có số PIT tại t (mọi mã có dòng panel, không chỉ in_universe).
Cần ≥ 5 mã ngang hàng (trừ i), thiếu thì NaN. NaN ⇒ mô hình rơi về null P1 cho dòng đó.
Không dùng ROE của chính mã để xác định pha. Đây là điểm skeptic J3 đã bác (đại số persistence).
| Mã | Chỉ báo của mỗi mã ngang hàng j (PIT tại t) | Ý nghĩa |
|---|---|---|
| S1 | roe_ttm_j − roe_tc5_j | ROE ngành so với chuẩn 5 năm |
| S2 | gpm_j − trung vị gpm_j của 20 quý trước (≥ 8 quý) | biên gộp ngành so với chuẩn |
| S3 | −(cashcycle_j − trung vị 20 quý trước) (≥ 8 quý) | vòng quay tồn kho + phải thu: chu kỳ tiền rút ngắn ⇒ pha tốt |
| S4 | capex_ttm_j/rev_ttm_j − trung vị 20 quý trước (≥ 8 quý) | capex ngành tăng (đỉnh đầu tư) |
Lịch sử 20 quý của j chỉ gồm các quý có `known ≤ t`, vì dựng theo thứ tự `known`.

## 3. Mô hình (tâm RIM, thay roe_n; mọi hệ số fit trên IS)
Ký hiệu: tc = roe_tc5 (D0); g = roe_ttm − tc; Sk = chỉ báo ngành k, chuẩn hoá theo hạng phần trăm ∈ [−0,5; 0,5] trong cross-section tháng t.
- **D0:** roe_n = tc.
- **EP:** E/P (chỉ dùng hạng).
- **P1, null persistence một hệ số (tiêu chí (iii)):** roe_n = tc + φ·g.
- **M1, phân rã ngành/riêng:** roe_n = tc + φ_I·gI + φ_S·(g − gI), với gI = S1 (phần ngành của chênh ROE).
- **M2..M4, persistence theo pha:** roe_n = tc + (φ0 + φ1·Sk)·g, lần lượt k = 2, 3, 4.
- **M5:** roe_n = tc + (φ0 + φ1·S1)·g.

Tổng **5 biến thể chu kỳ** (M1–M5) + 1 null P1.
- **Fit (IS):** OLS gộp trên dòng (ticker, quarter) với `known` 2014-01..2019-12, bản ghi đầu tiên mỗi quý.
  - Mục tiêu: y = trung bình(roe_ttm tại +4 quý, +8 quý) − tc.
  - Chỉ nhận mục tiêu khi cả 2 quý tương lai có `known < 2020-01-01`, để không rò OOS.
  - Winsor g, y ở [−0,3; 0,3]. Không hằng số.
  - Cắt φ (và φ0 + φ1·S) vào [0; 1]. roe_n cắt [−0,1; 0,5] như D0.
- Mã FIN (route BANK, SECURITIES, INSURANCE) vẫn nằm trong ALL như J3, không fit riêng.

## 4. Tiêu chí (khoá)
- **Quyết định = OOS 2020–2023, phạm vi ALL, IC36.** IS chỉ để fit và chọn.
- **GO cho biến thể Mk:** phải đạt cả ba điều kiện:
  - ΔIC36(Mk − P1) OOS > 0 và ≥ 3/4 năm > 0;
  - ΔIC36(Mk − D0) OOS > 0 và ≥ 3/4 năm > 0;
  - ΔIC36(Mk − EP) OOS > 0 và ≥ 3/4 năm > 0.
- **Thêm hai điều kiện:**
  - IS ΔIC36(Mk − P1) ≥ 0, để không khác dấu giữa 2 era;
  - DSR(Mk − P1, chuỗi năm 2014–2023, N thử = 7 của J3 + 6 của J4 = 13) ≥ 0,95.
    PBO {P1, M1..M5} báo kèm; PBO ≥ 0,5 ⇒ không được chọn biến thể IS tốt nhất.
- **"KHÔNG CÓ GÌ MỚI" (dispatch):** không Mk nào hơn P1 ở OOS IC36 với ≥ 3/4 năm cùng dấu dương ⇒ **NO-GO, dừng, KHÔNG thử thêm biến thể**.
  Tiêu chí này độc lập với điều kiện EP và DSR. Hơn P1 nhưng trượt EP hoặc DSR vẫn là NO-GO cho wire; báo là "mô tả".
- **Phụ (không quyết định):**
  - IC36 trong CYC (COMM + CYC_HI của J3) và REST, để mô tả;
  - R² OOS của roe_n dự báo y (roe tương lai) so với P1, trên quý có `known` 2020+;
  - P1 so với D0 / EP: báo để biết null persistence tự nó đứng ở đâu.
- **N hiệu dụng:**
  - IS 6 năm, OOS 4 năm, tức ~1,3 cửa sổ 36 tháng độc lập.
  - Chu kỳ ngành lớn trong mẫu: ~2–3 (2011–12, 2018–19 và 2022–23; COVID 2020).
  - Không đọc CI khối-năm như xác suất. Sign-count năm là thước chính.

## 5. Kỷ luật chạy
- Thứ tự commit: PRELOCK → panel V3.2 (vá mc) + bus → mô hình + đo → REPORT + selfcheck.
- Selfcheck chạy dưới cả `env -u TZ` và `TZ=Asia/Ho_Chi_Minh`, md5 phải giống. Gồm:
  - tính lại ΔIC36(M* − P1) OOS bằng vòng lặp riêng;
  - tính lại φ của P1 bằng `numpy.linalg.lstsq` riêng;
  - kiểm LOO (chỉ báo của i không chứa i);
  - kiểm PIT (`known ≤ time` trên mọi dòng dùng để dựng S).
- Interpreter: `/home/trido/thanhdt/wc_venv/bin/python`. threads = 1.
- Không wire, không merge, không email.
