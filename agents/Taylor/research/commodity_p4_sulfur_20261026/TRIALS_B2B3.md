# Danh sách trial B2/B3 — khai TRƯỚC khi chạy b2_nowcast.py (job Taylor_20261026_160657, 2026-10-26 ~23:30 ICT)
Biến: c_yoy = log(giá TB quý Q / Q−4), giá TB = trung bình ngày làm việc (T2–T6), quý cần ≥40 quan sát.
Đích = BCTC bản công bố ĐẦU (Release_Date sớm nhất mỗi ticker-quarter): rev_yoy=log(DT0/DT4), gpm_d=GPM0−GPM4, np_d=(LN0−LN4)/DT4 (clip ±0,5).
PIT: chỉ giữ cặp khi qend+2 ngày < Release_Date. N độc lập = SỐ QUÝ (gộp trung vị nhóm theo quý), không phải số cặp mã-quý.
Công cụ: Spearman theo quý; CI90 moving-block bootstrap (block 4 quý, 5000 lần, seed 20261026); p = circular-shift permutation (2000).

## Nhóm
- P4 (dấu kỳ vọng +): DGC, PAT.
- S (lưu huỳnh trực tiếp, đầu vào H2SO4; dấu kỳ vọng gpm/np −, rev +): DDV, LAS, CSV.
- Mô tả (KHÔNG suy luận, KHÔNG tính trial): BFC, DPM, DCM, SFG, VAF, NFC — chỉ in IC từng mã.

## Trial nowcast (KQKD), 8
N1 P4→rev_yoy · N2 P4→gpm_d · N3 P4→np_d (nhóm P4)
N4 S→rev_yoy · N5 S→gpm_d · N6 S→np_d (nhóm S)
N7 DGC np_d ~ c_yoy(P4) + c_yoy(S) (OLS 2 biến, hệ số S kỳ vọng −)
N8 spread P4 − 9×phosphate_rock_cny (TE, từ 2022-08) → DGC np_d (N rất nhỏ, ~12 quý)

## Trial giao dịch (tích luỹ vào 13 trial của commodity_cycle_te), 4
G1 P4 c_yoy → ann (DGC,PAT; vượt trội EW universe_pit, phiên trước→phiên sau công bố)
G2 P4 c_yoy → post60
G3 S c_yoy (×−1) → ann (DDV,LAS,CSV)
G4 S c_yoy (×−1) → post60
Cổng: Bonferroni × (13+4)=17 ở α 0,05 VÀ dấu đúng VÀ IS(≤2022)/OOS(2023+) cùng dấu. Không mở thêm biến thể sau khi chạy.
