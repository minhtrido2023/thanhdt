# LAG: tín hiệu theo mỗi cổ phiếu + rủi ro ex-date quyền mua — REPORT (job Taylor_20261021_165514)

PAPER-ONLY. Không wire, không đổi pin, không ghi registry. PREREG: `PREREG.md` md5 `c60975e2e29c8ec33d79add2e92ea83c`
(ghi trước khi tính outcome). Biến thể đã thử: **2** (PS1 thô, PS2 kiểu IAS 33) — không thêm. Phân tích ngoài PREREG
được dán nhãn **POST-HOC**.

**Dữ liệu (chỉ đọc)**: `data/earnings_events_classified.csv` + `data/earnings_surprise_data.pkl` (bản 2026-10-21) +
`data/forensic_flags.csv`; BQ kéo 2026-10-21/22: `corporate_action` ISS/AIS (`iss_raw.csv`, `ais_raw.csv`),
`ticker_financial.OShares` (`tf_oshares.csv`), VNINDEX/Price/Close từ `ticker`. Lệch PREREG: lịch phiên lấy từ
VNINDEX trên BQ (`vni.csv`) vì `VNINDEX.csv` không tồn tại — cùng lịch engine dùng (VNI_QUERY).

**Tập sự kiện U** (`build_events.py`, mirror `pt_v23_audit_2014.py` §4): NP_R≥15 ∧ prior_n_good≥4 ∧ pa_HL3≥5 ∧
forensic ON, entry = Release+5 từ 2014. **N = 5.419 sự kiện / 794 mã / 576 ngày công bố / 51 mùa**. Kiểm: NP_R CSV =
pkl×100 = (NP_P0/NP_P4−1)×100 (sai lệch tối đa 1e-11). ⚠️ U chỉ gồm sự kiện đã đủ R+30 (SCL 2026Q3 chưa có trong U).

**Ca kiểm SCL 2026Q3** (đo, công thức PREREG): production surprise 0,591 (HI) / NP_R 136%; **PS2 0,485 (LO) / 73,5%**;
PS1 0,316 / 36,1% — khớp dải 0,32–0,46 của fundamental-skeptic (PS1 ở đầu dưới; PS2 vừa dưới ngưỡng 0,5).

---

## Q1 — Bao nhiêu sự kiện LAG có số CP thay đổi; bao nhiêu đổi nhãn

Nguồn số CP: `OShares` theo quý (TRAP: restate) — chỉ dùng **tỉ lệ** g = S(P0)/S(P4); kiểm bằng
E = Π(1+exercise_ratio) các ISS executed có ex-date giữa 2 dòng quý.

| Đo (U, N=5.412 có số CP) | Số | % |
|---|---:|---:|
| \|g−1\| ≤ 1% (không đổi) | 3.646 | 67,4% |
| \|g−1\| > 1% | 1.766 | 32,6% |
| \|g−1\| ≥ 10% (nhóm L) | 1.283 | 23,7% |
| pha loãng THẬT sau hồi tố CP thưởng/cổ tức CP ≥10% (S0/(S4·B4)) | 592 | 10,9% |

Phân bố mức đổi (nhóm đổi >1%): p10 +5,0% · p25 +10,0% · trung vị +23,2% · p75 +53,3% · p90 +102,2%; 52 sự kiện giảm CP.

Độ tin cậy nguồn (toàn U): `explained` (khớp corporate_action ±2%) 4.676 · `ratio_missing` (có riêng lẻ/ESOP/chuyển đổi
không có ratio) 412 · `unexplained` 324 · không có số 7. **Trong nhóm L: 728 explained, 350 ratio_missing, 205
unexplained** ⇒ ~16% nhóm L có số CP không tự giải thích được (có thể là restate/lỗi vendor).

Đổi nhãn (prior giữ theo production; superset C):

| | rớt qualify (NP_R_ps<15) | thêm qualify | HI→LO | LO→HI |
|---|---:|---:|---:|---:|
| PS1 (mọi tăng CP = pha loãng) | 540 (10,0% U) | 6 | 116 | 3 |
| **PS2 (hồi tố thưởng/cổ tức CP)** | **218 (4,0% U)** | 10 | **60 (2,7% HI)** | 3 |

## Q2 — Tín hiệu theo cổ phiếu có dự báo drift khác không

Outcome y_ex = post_ret (Close đ/c R+5→R+30) − VNINDEX cùng cửa sổ, %. CI 95% bootstrap cụm (B=2000) theo ngày công bố
và theo mùa. Đủ chi tiết: `q2_out.txt`, `q2_groups.csv`. Pre-flight: MARGINAL (`rnd_preflight_power.py`, effect giả
định 300bps/1.500bps là **ước lượng**) ⇒ mọi kết luận Q2 ở mức chẩn đoán.

| Phép so (PREREG) | N sự kiện / ngày | hiệu y_ex (pp) | CI cụm-mùa | IS | OOS |
|---|---:|---:|---|---:|---:|
| **PS2 HI→LO vs HI giữ nguyên** | 60 / 47 | **−4,62** | **[−9,34; −1,29]** | −4,71 | −4,56 |
| PS2 HI→LO vs LO giữ nguyên | 60 / 47 | −1,62 | [−6,00; +1,68] | −1,39 | −1,75 |
| PS2 rớt qualify vs giữ | 218 / 134 | −1,66 | [−3,98; +0,58] | −1,54 | −1,62 |
| PS1 rớt qualify vs giữ | 540 / 233 | −1,52 | [−3,00; −0,10] | −1,17 | −1,71 |
| PS1 HI→LO vs HI giữ | 116 / 86 | −4,09 | [−6,81; −1,29] | −2,06 | −5,03 |
| HI−LO toàn U, production | 2.196 vs 3.223 | +2,79 | [+1,29; +4,26] | +2,99 | +2,65 |
| HI−LO toàn U, PS2 | 2.088 vs 3.113 | +3,03 | [+1,65; +4,42] | +3,35 | +2,85 |
| HI−LO trong nhóm L, production | 518 vs 765 | +2,18 | [+0,28; +4,26] | +3,77 | +1,15 |
| HI−LO trong nhóm L, PS2 | 414 vs 656 | +3,21 | [+1,30; +5,34] | +5,44 | +1,83 |

IC Spearman (surprise vs y_ex): toàn U production 0,103 / PS2 0,103 / PS1 0,107; nhóm L 0,060 / 0,058 / 0,072;
ΔIC(PS2−prod) trên L CI cụm-mùa [−0,031; +0,026] ⇒ **IC không khác** — khác biệt chỉ nằm ở ~1% sự kiện đổi tầng.

LOYO (PS2 HI→LO vs HI giữ): −3,62 … −5,22 qua 13 lần bỏ năm — không năm nào lật dấu. LOYO PS2 rớt−giữ: −0,97 … −2,06.

**Theo luật PREREG** (cùng dấu IS/OOS, CI cụm-mùa không chứa 0, ≥30 ngày công bố): **PS2 HI→LO ĐẠT** (47 ngày);
PS2 rớt-qualify KHÔNG đạt (CI chứa 0). PS1 rớt-qualify đạt biên, nhưng PS1 phạt cả cổ tức CP (không có lý do kinh tế)
và đây là 1 trong ~6 phép so ⇒ không coi là bằng chứng độc lập.

POST-HOC (không trong PREREG, chỉ để kiểm độ vững — `q2_posthoc_out.txt`): winsor 5/95 hiệu HI→LO còn **−2,22pp**
(một phần do đuôi); chỉ sự kiện `explained` N=20: −4,66; median HI→LO −1,04 vs HI giữ +1,49; **placebo: HI có pha
loãng ≥10% nhưng KHÔNG đổi tầng (N=151) lại +5,81 vs HI không pha loãng +3,66** ⇒ không phải "pha loãng thì xấu",
mà là "surprise sinh ra do tăng vốn thì không phải surprise". Theo năm: N HI→LO 1–11/năm, 2018 = 0.

## Q3 — Rủi ro ngày không hưởng quyền (quyền mua)

Nguồn: ISS "Quyền mua CP cho Cổ đông hiện hữu" executed/announced (1.718 dòng; K = total_value/issue_volumn có ở 75,3%
toàn bảng, **100% ở 52 sự kiện trúng cửa sổ**). `q3_rights.py` → `q3_out.txt`, `q3_rights_table.csv`.

**(a) Tần suất.** Ex-date nằm trong [entry, R+30]: **52/5.419 sự kiện U = 0,96%** (43 ngày công bố; 1–11 sự kiện/năm,
2015 = 11). Trên sổ lệnh R3 đã pin (`2026-10-08__R3-park0-pin0pct-SAN__537e349b`, giữ thật): **10/1.516 holding LAG =
0,66%**, trong đó 6/10 ở 2014-2015, từ 2020 chỉ 2 (VIX 2022, MBS 2024). "Đã công bố, ex sau cửa sổ / chưa có ngày tại
entry" (kiểu SCL): 38 sự kiện — ⚠️ XẤP XỈ, `public_date` bị vendor ghi đè (registry Bẫy 2b), không đo được point-in-time.

**(b) Mức điều chỉnh lý thuyết** ((P+rK)/(1+r) − P)/P, P = Price chưa đ/c phiên trước ex: p10 −31,2% · p25 −19,0% ·
**trung vị −12,6%** · p75 −6,4% · p90 −3,3%. K/P trung vị 0,56; 1 ca K>P. Đối chiếu thật: Price thô ngày ex trung
vị −12,2% (corr với lý thuyết 0,82); Close đ/c cùng ngày trung vị +4,4% ⇒ **xác nhận backtest coi ex-date như không có
sự kiện**.

**(c) Tiền cần nếu thực hiện đủ** = r×K×số CP: theo vị thế trung vị 22,5% giá trị vị thế (p90 60,3%, max 129,9%).
Theo NAV: slot 8% → trung vị 1,8% · p90 4,8% · max 10,4% NAV; slot 10% → 2,25% · 6,0% · 13,0% NAV. Trên sổ pin R3
(vị thế thật 0,35–7,9% NAV): trung vị **1,55% NAV**, max **7,10% NAV** (HDA 2015, K≈P).

**(d) Nếu KHÔNG thực hiện và KHÔNG bán quyền**: lỗ = −adj × tỷ trọng: slot 8% trung vị 1,0% NAV (p90 2,5%, max 3,5%);
slot 10% 1,26% (p90 3,1%, max 4,3%). Bán quyền trong kỳ chuyển nhượng thu lại phần lớn giá trị — chưa đo (không có giá
quyền trong BQ).

**(e) Tác động lên pin LAG (ƯỚC LƯỢNG, không đổi pin)**: 10 holding trên sổ R3 cộng đơn **7,16% NAV / 12,5 năm ≈
0,57 pp/năm** nếu bỏ quyền hoàn toàn (`q3e_ledger_out.txt`; giá trị vị thế suy theo Close đ/c, NAV từ ledger). Từ 2020:
1,82% NAV / 6,5 năm ≈ 0,28 pp/năm. Nếu thực hiện đủ (luật user mới) ⇒ backtest giá đ/c ≈ đúng về kinh tế, cái giá là
tiền mặt (c) và tăng phơi nhiễm vào mã đó. Chặn trên thô theo mọi sự kiện U (không giới hạn tiền) 4,7–5,9 pp/năm là
VÔ NGHĨA cho pin (engine chỉ vào ~1.516 holding) — chỉ ghi để không ai trích nhầm.
Lưu ý: 52 sự kiện này có y_ex (giá đ/c) trung bình **+7,06pp** (trung vị +3,86) vs U +2,01 — lọc bỏ chúng sẽ mất drift
tốt; giá trị đó chỉ thật nếu thực hiện/bán quyền.

## Q4 — Khuyến nghị (chỉ khuyến nghị; chờ quant-skeptic)

1. **(i) Tầng HI/LO**: chuyển tầng theo surprise PS2 (NP theo CP, hồi tố thưởng/cổ tức CP) — bằng chứng: 60 sự kiện
   HI→LO kém HI giữ −4,6pp, CI cụm-mùa không chứa 0, IS≈OOS, LOYO ổn; nhưng winsor còn −2,2pp, N nhỏ, chỉ ~2,7% sự kiện HI.
   **Chắc chắn: TRUNG BÌNH.** Điều kiện trước wire: chạy full engine (bậc danh mục, skill bước 6) + quant-skeptic; kỳ vọng
   tác động CAGR nhỏ vì IC tổng không đổi.
2. **(i) Cổng qualify NP_R**: **KHÔNG đổi** sang NP_R theo CP — PS2 rớt-qualify CI chứa 0; PS1 không có cơ sở kinh tế.
3. **(ii) Cờ, không lọc**: cờ DD khi ứng viên LAG có quyền mua (ex trong 25 phiên hoặc đã công bố chưa có ngày) hoặc
   pha loãng thật ≥10% YoY. Không lọc bỏ: nhóm quyền mua có drift đ/c +7pp. Chắc chắn: CAO (đo trực tiếp, 0,7–1% sự kiện).
4. **(iii) Tiền thực hiện quyền**: không cần dự trữ thường trực (≈0,8 ca/năm trên sổ pin, 2 ca từ 2020); khi có cờ, lập
   plan khoá r×K×CP giữ (trung vị ~1,5–2,3% NAV, xấu nhất 7–13% NAV) trước ngày đăng ký. Chắc chắn: CAO về quy mô.
