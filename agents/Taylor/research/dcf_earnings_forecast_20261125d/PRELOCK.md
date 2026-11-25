# PRELOCK — Dự báo earnings quý ↔ khoảng cách tâm-giá (job Taylor_20261125_011012)

Khoá TRƯỚC khi chạy bất kỳ mô hình dự báo / test nào. Chỉ nghiên cứu: không sửa `dcf_valuation.py`, không wire, không email, không merge.
Kiểm kê (đã chạy, chỉ đếm): `calc/a_events.py` → `out/inventory.json`.

## 0. Dữ liệu & PIT
- Sự kiện = (mã, quý q). Ngày biết `K = max(time, Release_Date)` của `ticker_financial` (cache `data/bq_cache/ticker_financial.parquet`, 1 vintage).
  Mọi đầu vào dự báo tại gốc q lấy từ CHÍNH dòng q (`NP_P0..P7`, `Revenue_P0..P7` = số QUÝ, P_k = quý q−k) ⇒ đã công bố tại K.
- Thực hiện quý q+h = `NP_P0` của dòng q+h. Kiểm nhất quán vintage: `NP_P1(q)` = `NP_P0(q−1)` ở 99,3% cặp (|lệch|<0,1%), >5% ở 0,38% (n=59.540).
  Hạn chế: 1 vintage ⇒ không đo được restatement giữa các vintage; **mã huỷ niêm yết (nguồn VND của panel V3, 4.053 quý) không có NP_P* ⇒ vắng ở A/B (survivorship nghiêng lạc quan về sai số)**.
- Định giá: panel V3 snapshot `in_snapshot/vp2.parquet` md5 `daaa63ec56789b30c5c148790644b90f` (= MD5SUMS commit 152e83c11). Không sửa nguồn.
  `V_D0 = exp(lv_D0)·mc` (= vb·E, không phụ thuộc mc). **Không dùng mc tháng của panel làm cơ sở kết luận về giá ở B**: gap tại K dùng `MC_rel` = giá THÔ tại ngày công bố × N cùng ngày.
  Ở C buộc phải dùng mc tháng (mc_old, phồng theo tỉ suất cổ tức — lỗi V3.1 đang vá) — D0 và biến thể dùng CHUNG mc nên so sánh Δ là cùng thước; mức IC tuyệt đối mang caveat này; chạy lại sau V3.1.
- Mẫu chung: `iuK` (universe_pit phiên ≤K, dung sai 7 ngày) ∧ đủ 8 quý NP lịch sử ∧ E>0. Mọi mô hình so trên CÙNG mẫu (dòng nào mô hình nào thiếu ⇒ loại khỏi so sánh cặp).
- Era theo năm của K: IS 2014–2019, OOS 2020+. Không có bước FIT nào (tham số cố định dưới đây) ⇒ embargo không cần; nếu phát sinh fit thì chỉ dùng mục tiêu có K_A ≤ 2019-12-31.

## 1. N độc lập (khai trước)
| | Sự kiện (dòng) | Mã | Quý báo cáo (đơn vị độc lập chính) | Năm (khối bootstrap) |
|---|---|---|---|---|
| IS | 6.118 | 487 | 24 | 6 |
| OOS | 11.338 | 671 | 28 (2026 dở dang) | 7 |
Sai số cùng quý tương quan chéo mạnh (cú sốc vĩ mô chung) ⇒ thống kê tính theo QUÝ rồi gộp; CI = bootstrap khối NĂM (2.000 lần, seed 20261125). Không dùng số dòng làm N.
C (IC 36T): as-of OOS 2020-01…2023-10 = 46 tháng chồng lấn 36T ⇒ **~1,3 cửa sổ độc lập** — mọi kết luận C OOS là yếu theo cấu trúc, ghi rõ.

## 2. A — Năng lực dự báo LNST quý (h = 1 chính; h = 2,3,4 phụ)
Họ 8 dự báo, công thức cố định:
- `SRW` A_{q+h−4} = NP_P{4−h} (naive mùa vụ — chuẩn so sánh) · `RW` NP_P0 · `TTM4` ΣNP_P0..3 / 4
- `SRWD` (Foster) SRW + d, d = mean_{k=0..3}(NP_Pk − NP_P{k+4})
- `MxR` Rev_P{4−h}·(1+g) · m; g = clip(ΣRev_P0..3/ΣRev_P4..7 − 1, ±0,5); m = clip(ΣNP_P0..3/ΣRev_P0..3, ±0,5)
- `MR` E·[ρ̄ + 0,65^{h/4}(ρ − ρ̄)]/4; ρ = ΣNP_P0..3/E (ROE TTM), ρ̄ = `roe_tc5` (trung bình 5 năm PIT của panel)
- `ENS` trung vị(SRWD, MxR, MR) · `D0imp` = roe_tc5·E/4 (dự báo earnings NGẦM của RIM-VN D0)
Sai số e = (A − F)/E_gốc (điểm ROE quý). Thước:
- **Chính**: MdAE theo quý báo cáo; skill R_t = MdAE_m/MdAE_SRW; tóm tắt = trung bình nhân R_t qua quý; CI khối năm.
  "Mô hình hơn naive" ⇔ CI trên của R < 1 ở CẢ IS và OOS (Bonferroni 7 so sánh ⇒ CI 99,3%).
- Phụ: mean|e| winsor 1/99; MdAPE trên |A| ≥ 0,25%·E; thiên lệch có dấu = trung vị e; hit hướng = sign(F − A_{q+h−4}) = sign(A − A_{q+h−4}) (bỏ ca bằng nhau; SRW không có hit).
- Cắt lớp (MÔ TẢ, không tuyên bố khác biệt khi chưa có CI): route, tercile quy mô (MC_rel trong quý), tercile biến động ROE (`roe_sd5`), rating ≤3 vs ≥4.

## 3. B — Sai số dự báo có giải thích khoảng cách tâm-giá?
gap_q = log(V_D0/MC_rel) tại K_q (>0 = tâm cao hơn giá = "rẻ"). Sai số tại K_q: u_q = 4·A_q/E_{q−1} − roe_tc5_{q−1} (sai số của D0imp, điểm ROE năm), cu_q = Σ4 quý gần nhất; ε_q = sai số ENS h=1 vừa lộ; cε_q = Σ4.
- **B1 (đồng thời)**: theo quý, Spearman(gap, cu) và Spearman(|gap|, |cε|). Kỳ vọng nếu luận đề đúng: gap ÂM với cu (mô hình đánh giá thấp earnings thực ⇒ giá > tâm).
- **B2 (dẫn trước — thị trường biết trước?)**: Spearman(gap_q, sai số TƯƠNG LAI) với ε⁴ = (ΣA_{q+1..q+4} − ΣF^ENS_{q+1..q+4|q})/E_q và u⁴ (D0imp 4 quý tới). gap>0 dự báo sai số âm ⇒ thị trường thấy trước điều mô hình chưa thấy.
- **B3 (giá về phía tâm khi earnings lộ?)**: lợi suất trừ TB đều universe (Close điều chỉnh, vào phiên sau K): r_pre = (K_q, K_{q+1}−2 phiên], r_ann = (K_{q+1}−2, K_{q+1}+2]. IC(gap, r) mỗi cửa sổ và IC/phiên; "hội tụ tập trung quanh công bố" ⇔ IC/phiên r_ann > IC/phiên r_pre với CI chênh > 0.
- **Null bắt buộc (bài học V3)**: lặp B2/B3 với E/P (np_ttm/MC_rel) và B/P; báo ΔIC(gap − E/P) có CI. IC phần dư của gap sau khi hồi quy hạng trên {E/P, log MC, roe_tc5, momentum 12−1 tại K}.
  "Sai số giải thích gap vượt nhân tố đã biết" ⇔ IC phần dư OOS CI loại 0 VÀ cùng dấu IS. Không phân biệt được với E/P ⇒ nói thẳng.

## 4. C — Vòng cập nhật (PIT: hiệu chỉnh tại K_q chỉ dùng u đã biết ≤ K_q)
Chỉ đổi roe_n trong `rim_vb` (R 12,25%, gT 5,5%, κ 0,4, ret như D0); V' cố định trong quý như D0; lv' = log(V'/mc).
- `C1` bias-corr mã: roe_n = tc + 0,5·mean(u, 4 quý gần nhất, cần ≥2)
- `C2` co về ngành: roe_n = tc + 0,5·[n/(n+4)·ū_mã + 4/(n+4)·ū_route,t]; ū trên ≤8 quý; ū_route,t = trung vị chéo ū_mã trong route tại tháng t (PIT)
- `C3` dùng dự báo A: roe_n = ΣF^ENS_{q+1..q+4|q}/E_q (clip −0,1…0,5)
Đo bằng code V3 (`d_metrics2.py` hàm ic_dates/boot_year/cheap_events/cheap_outcome/exp_events/exp_outcome, phạm vi ALL h50): IC36 IS/OOS, U-hit, O_right_rel (cảnh báo đắt). ΔIC36 cặp vs D0 với CI khối năm.
**Tiêu chí "đáng nghiên cứu tiếp" (không phải GO wire)**: ΔIC36 OOS CI 99,17% (Bonferroni 3) > 0 ∧ ΔIC36 IS ≥ 0 ∧ U-hit, O_right_rel không tệ hơn D0 quá 5pp ∧ IC36 OOS ≥ IC36 E/P (nếu không ⇒ "không hơn E/P"). PBO (CSCV trên IC36 theo năm 2014–2023, 4 cấu hình) báo kèm, chỉ tham khảo (N nhỏ).

## 5. Không lặp NO-GO đã đóng
Không test SUE-tilt LAG (−0,66pp, đã loại), không đề xuất tín hiệu mua/bán; đây là đo năng lực dự báo + hiệu chỉnh mô hình định giá. Không tự xưng CONFIRMED.
