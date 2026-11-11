# PRELOCK — dd_fcfe3y_decay_20261111 (job Taylor_20261111_051016)

Khoá TRƯỚC mọi lần tính IC/PIC của job này. Đã làm trước khoá: dựng `out/ext.parquet` (thành phần
dòng tiền, không nhãn) + kiểm đơn vị (không nhãn). Đã BIẾT trước khoá (từ dd_fwd_prelock): PIC V_dài
IS/OOS theo N, PIC theo năm và DT5G (`ic_by_year.csv`). Không có số IC nào của thành phần/biến thể
dưới đây được tính trước khoá.

## Dữ liệu & khuôn đo (giữ nguyên dd_fwd_prelock)
- Panel `dd_blend_20261111/out/panel.parquet` md5 1de5145f42281f9b3bf5e940064e473c + `out/ext.parquet`.
- Mẫu gốc M0 = rating≤3 ∧ MC0 hữu hạn ∧ V_dài>0 ∧ V_ngắn(v0)>0 (đúng mask0 của dd_fwd_prelock).
- Nhãn y = log TR_N, N ∈ {12,24,36,60}. Quý có <20 dòng bị bỏ. Rank IC theo quý → trung bình quý.
- PIC(x) = hệ số chuẩn hoá của x trong hồi quy hạng 2 biến (x, V_ngắn v0) mỗi quý (= PIC_l cũ).
- CI: bootstrap cụm MÃ B=1000 (seed 20261111+N) và bootstrap KHỐI NĂM (rút năm có hoàn lại trong
  từng split, B=1000) thay cho cụm quý đơn (nhãn N>3 tháng chồng lấp giữa các quý cùng năm).
- Kiểm soát: baseline phải tái lập PIC_l IS/OOS của dd_fwd_prelock tới 1e-9 (assert).

## Q1 — thật hay artifact (mô tả + kiểm định, KHÔNG chọn gì)
(a) PIC V_dài trên các split: IS16–18/OOS19+; IS16–19/OOS20+ (gốc); IS16–21/OOS22+; cửa sổ trượt
    4 năm as-of (2016–19 … 2022–25 khi đủ quý). Thêm: hồi quy PIC theo quý lên (i) xu hướng tuyến
    tính theo năm, (ii) bước nhảy 2020; so SSE + CI khối-năm của độ dốc / bước.
(b) Hiệu Δ = PIC(IS) − PIC(OOS) gốc: CI cụm mã (cùng mẫu bootstrap cho cả hai vế) và CI khối năm.
    "Sụt thật" ⇔ Δ>0 với CI cụm mã loại 0 ở ≥3/4 N VÀ CI khối năm loại 0 ở ≥2/4 N.
    "Artifact" ⇔ Δ CI chứa 0 ở ≥3/4 N theo CẢ hai cách cụm. Còn lại ⇒ CHƯA KẾT LUẬN.
(c) OOS bỏ 2022; OOS bỏ 2020–21.
(d) Tập mã đồng nhất: mã có ≥1 quý trong IS và ≥1 quý trong OOS của M0; và bản chặt ≥8 quý mỗi bên.

## Q2 — cơ chế (mô tả; mỗi thành phần: IC, PIC kiểm soát V_ngắn; IS vs OOS; CI cụm mã)
Ký hiệu: CFO3 = CF_OA_3Y/3, CPX3 = −CF_Invest_3Y/3, FCFE3 = CFO3 − CPX3 (= cơ sở engine), MC0 thước đo.
Do r, g_T hằng số chéo-mã trong frame domestic_v2 ⇒ log(V_dài/MC0) = log(FCFE3/MC0) + log k(g_exp).
 (i) FCFE3/MC0 · (ii) CFO3/MC0 · (iii) CPX3/MC0, CPX3/CFO3, CPX3/doanh thu TTM, CPX3/tổng tài sản
 (iv) ΔNWC 1 năm = Δ(Tồn kho + Phải thu − Nợ ngắn hạn)/tài sản; accrual = (NI_TTM − CFO_TTM)/tài sản
 (v) mix ngành: tỉ trọng nhóm capex-nặng (BDS, XD_VLXD, tienIch, taiNguyen_chuKy) theo năm; IC trung
     hoà ngành (hạng trong nhóm); IC theo nhóm IS vs OOS (mô tả, N nhỏ)
 (vi) g_exp một mình; PIC của log k(g_exp) kiểm soát FCFE3/MC0; tương quan g_exp với tăng trưởng LN quá khứ
 (vii) độ cũ trường 3Y (m_since_fy 0–9 tháng): PIC theo nhóm tuổi; FCFE 12 quý cuốn (cfo12q+cfi12q) làm đối chứng
 Tham chiếu (không phải trial): E/P = NI_TTM/MC0.
"Mất thông tin" = PIC IS CI loại 0 nhưng OOS CI chứa 0 hoặc giảm ≥ 0,07.

## Q3 — biến thể khai trước: 8 trials (cùng g_exp, g_T, r, DCF 2 giai đoạn của engine)
DA = EBITDA_P0 − EBITM_P0 × doanh thu TTM (khấu hao TTM proxy); FA = doanh thu TTM / FAssetTurn_P0.
Cổng chung: CF_OA_3Y>0 ∧ cơ sở>0 (như engine); DA thiếu/≤0 ⇒ biến thể dùng DA không định nghĩa.
 C1 FCFE5 = (CF_OA_5Y + CF_Invest_5Y)/5                       (trung bình 5 năm)
 C2 CFO3 − DA                                                (capex bảo trì = khấu hao)
 C3 CFO3 − DA − g_exp·FA                                     (bảo trì + capex tăng trưởng theo g)
 C4 CFO3 − min(CPX3, DA)                                     (capex vượt bảo trì = đầu tư NPV-0, không trừ)
 C5 NI3 + DA − CPX3, NI3 = TB LNST 3 năm (annual_np[:3])     (FCFE trung tính vốn lưu động)
 C6 CF_OA_5Y/5 − DA                                          (CFO 5 năm − bảo trì)
 C7 nhóm capex-nặng dùng C2, nhóm khác dùng baseline        (kết hợp theo ngành)
 C8 (cfo12q + cfi12q)/12 × 4                                 (FCFE 12 quý cuốn, hết độ cũ ≤9 tháng)
Không làm được (khai): thu nhập tài chính / khoản một-lần — cache không có cột.

## Tiêu chí "PHỤC HỒI" (khoá)
So trên GIAO hỗ trợ (M0 ∩ biến thể>0), cùng dòng với baseline. ΔPIC = PIC(Cx) − PIC(baseline).
 (i) OOS 2020+: ΔPIC > 0 và CI cụm mã của ΔPIC loại 0 ở ≥3/4 N;
 (ii) IS 2016–19: PIC(Cx) ≥ PIC(baseline) − 0,03 (điểm) ở MỌI N;
 (iii) ΔPIC OOS điểm > 0 khi bỏ 2020–21 VÀ khi bỏ 2022, ở mọi N đánh giá được (≥6 quý; cần ≥2 N);
 (iv) PBO (CSCV, 8 khối năm 2016–23, 9 cấu hình = 8 biến thể + baseline, chỉ số = PIC theo năm) < 0,5
      ở N24 VÀ N36.
Đạt (i)–(iv) ⇒ "phục hồi". Nhiều biến thể đạt ⇒ khuyến nghị biến thể có PIC IS trung bình 4 N cao
nhất trong nhóm đạt. Không biến thể nào đạt ⇒ "chưa có cách sửa có cơ sở" + đề xuất theo dõi.
Mô tả kèm (không dùng để chấm): PIC trên hỗ trợ riêng, độ phủ.

## Đếm trials
Lựa chọn: 8 (Q3). Q1/Q2 là mô tả/kiểm định cơ chế, không chọn. Cộng dồn chuỗi DD: 417 + 8 = 425.
Tái lập: chạy `calc/analyze.py` 2 lần, md5 output trùng. Tính lại độc lập (scipy) vài ô.
