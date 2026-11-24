# PRE-REGISTRATION — CK holding VN v5 (job Taylor_20261124_073243)

Viết TRƯỚC lần chạy calc v5 đầu tiên. Chưa có số v5 nào. Đã biết: toàn bộ số v4 + ước lượng skeptic v4
(MSN thêm MSR ⇒ mốc 11/2026 ≈18–23%). Đã đọc dữ liệu đầu vào để viết quy tắc (BCTN MSN 2024/2025, KBS, quét
`sweep_v5.py` → `inputs/sweep_v5.csv`, tải MSR qua stage `v5add`) — KHÔNG chạy calc. Không sửa file này sau khi chạy.
Code diễn giải khác chữ file này ⇒ ghi mục "Khác PREREG" trong report, không im lặng.

## A. Sửa (theo dispatch 1–7; quy tắc chung, không vá riêng theo kết quả)
S1. **Tỷ lệ sở hữu theo nguồn gốc có ngày (`inputs/stakes_override_v5.csv`)**: thay cặp (mẹ, con) trong stakes_all bằng các
  dòng override; một cặp có thể có nhiều dòng theo thời gian. PIT: dùng dòng mới nhất có `valid_from` ≤ D;
  `valid_from` trống = stake_date + 90 ngày (đúng quy tắc v4). Chế độ `fixed` (độ nhạy look-ahead): dòng cuối.
  - MSN (BLOCKING): MCH 67,4% (31/12/2024) → 66,2% (31/12/2025); TCB 19,8 → 19,7%; MML 94,3 → 91,2% (tỷ lệ lợi ích
    kinh tế trong bảng công ty con BCTC hợp nhất MSN); MSR 87,46% CP phổ thông (KBS, Tầm nhìn Masan), áp từ
    31/12/2024 vì BCTC MSN ghi lợi ích kinh tế MHT 94,9% không đổi 2024→2025; VSN bỏ (liên kết của MML ⇒ trong MV MML).
    Chuỗi: MSN→ZENITH 100%→Tầm nhìn Masan 100%→MSR; MSN→SHERPA 100%→Masan Agri 100% / WinEco 100%→MML.
  - Độ nhạy MSR (bắt buộc theo dispatch): s_MSR ∈ {0 (chặt: KBS 30/10/2026 + 90 ngày nằm ngoài cửa sổ), 25%, 43,7%,
    87,46% (chính), 94,9% (lợi ích kinh tế gồm CP ưu đãi)}. Kèm biến thể "MSN như v4" để tách tác động.
  - Quét hệ thống (mục 2, `sweep_v5.csv`): sửa ca có bằng chứng — VSC→VGR 74% → 54,35% (bán 20% 07/2025; hiệu lực
    từ ngày công bố BCTC Q3/2025 của VSC 28/10/2025 để tỷ lệ và VCSH mẹ đổi cùng lúc); PAN→FMC 50,12% → 37,75% trực
    tiếp (12,37% qua ABT đã nằm trong MV ABT). Ca khác (ngoài N, trùng thương hiệu giả) liệt kê trong report.
S2. **Lãi pha loãng của mẹ (mục 3)**: với mỗi sự kiện F1 áp mặc định "mẹ không tham gia" (s_b → s_a = s_b·f, tv > 0),
  khi BCTC mẹ đang dùng có cuối quý < ex: E_p += s_a·E_con_sau − s_b·E_con_trước, E_con_sau = VCSH con tại D (gồm tiền
  thu nếu đã cộng/đã phản ánh), E_con_trước = E_con_sau − tv. Không áp khi mẹ tham gia (s theo KBS/override) hoặc khi
  VCSH con không có tiền thu (BCTC con quá cũ, S3). Biến thể tắt để báo tác động (OGC, LHC, VSC).
S3. **PROCEEDS_ADD bỏ khi BCTC con cũ > 4 quý** so với quý của ngày ex (mục 4). Biến thể bật lại để báo tác động (SNZ).
S4. **Quy tắc ambiguous (mục 5)**: GIỮ quy tắc code v4 (mọi dòng PP/Rights/PUBL âm ⇒ cả (mã, ex) mơ hồ) và KHAI trong
  "Khác PREREG"; biến thể đúng chữ PREREG_v4 (chỉ khi cùng method có cả dòng âm lẫn dương) báo tác động (VIC/GEG/HPA).
S5. Report: khôi phục hạn chế MSR/MML tới khi sửa xong (mục 6) — ghi đã sửa ở v5 và phần còn lại; bỏ câu
  "4 mốc khớp số skeptic". GIC (mục 7): ghi rõ chuyển sang KBS 66,34% từ ngày niêm yết 22/06 < ngày KBS 30/06; báo bản
  chặt (update+90) cạnh bản chính.

## B. KHÔNG đổi
Ứng viên dải (a)–(d), R1/R2, con mỏng, độ phủ ≥60% ở ≥3 tháng, stale, VCSH mẹ, F1–F5 của PREREG_v4, tiêu chí §C v3/v4
(gồm §C2 đúng chữ + báo kèm hull (a)∪(d)), bootstrap khối (seed 20261124, B=5000), T_eff trên tháng n ≥ 11.

## C. Ánh xạ ra đề xuất HHS (khai trước; chỉ là đề xuất)
Base 0% (nhãn "đầu lạc quan"); "trung tâm" = đầu trên khoảng F5; "hiện tại" = trung vị cắt ngang tháng cuối (20/11/2026,
n ≥ 11); "phân tán một holding" = q75 liên-holding N (đặc tả chính); đầu âm chỉ giữ nếu HHS thuộc R1/R2.
Báo hull (a)∪(d) và hull §C2 đúng chữ: độ rộng, 0% ở phân vị nào. Số không ủng hộ mốc skeptic thì nói thẳng.
