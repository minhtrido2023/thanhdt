# DD — MVC (CTCP Vật liệu và Xây dựng Bình Dương, UPCOM) · bản r5 (nội bộ) · as-of 03/11/2026 · job `Taylor_20261103_100718`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua/bán. User quyết. Email: **CHƯA gửi** (chờ user báo "gửi email"; dry-run OK).
> r5 = ĐỔI NGUYÊN TẮC ĐỊNH GIÁ theo user 03/11 17:06 (skill due-diligence "ĐẦU TƯ DỰ ÁN MỚI", dd-investor-report luật 20): dự án mới ở GIÁ SỔ SÁCH/NPV 0 trong base; mọi khoản giảm trừ base phải có cơ sở dữ liệu độc lập.
> Phần BCTC/ngành/quản trị: `REPORT_r2_20261103.md` §1–§6 vẫn hiệu lực. Bản định giá r3/r4: `REPORT_r4_20261103.md` (lịch sử, KHÔNG còn hiệu lực cho kết luận).
> Đơn vị tỷ đồng; đ/cp = tỷ × 10 (100 tr cp). Giả định tự đặt gắn (ước lượng).

## 0. Mù giá — thứ tự (ICT, `r5/calc/`)
| Bước | |
|---|---|
| `valuation_base.py` (= r3, md5 d3fb9637…) + `model_r5.py` → `model_r5_out.{txt,json}`, `grid_r5.csv`; ngưỡng ĐĂNG KÝ TRƯỚC trong docstring | trước 17:15 |
| `inventory_r5.md` (bảng kiểm kê) | trước 17:15 |
| **KHOÁ** `LOCK_md5_r5.txt` 6 file | 17:15:01 |
| So giá: `compare_r5.py` (02/11 13.700 từ `r3/calc/px_0211.csv`; 03/11 13.300 từ dispatch — BQ chưa sync cùng ngày); `md5sum -c` 6/6 OK | sau khoá |
| Sau khoá, không đổi tham số: `post_lock_mine_wacc.py` (NPV mỏ mới ở chi phí vốn hỗn hợp), `post_lock_combo_r5.py` (tổ hợp mốc) | sau khoá |
Giới hạn: giá 13.700 đã biết từ r1–r4 ⇒ không chứng minh "chưa từng thấy giá"; chứng minh được: không truy vấn giá trong r5 trước khoá, ngưỡng đăng ký trước.

## 1. Kết luận r5
- **Tâm 25.725 đ/cp** (W 25/50/20/5 × đường giá g2031/thực 50:50; r 13%; holding 0; mỏ mới theo giá vốn) · **Base (cơ sở) 24.199** (g2031 22.484 / thực 25.914) · **Stress giá phẳng danh nghĩa 20.316**.
- **Thang (lưới 729 bộ, đăng ký trước):** RẺ CÓ BIÊN AN TOÀN ≤21.824 (P10) · RẺ CÓ ĐIỀU KIỆN 21.824–23.622 · **HỢP LÝ 23.622–28.829** (P25–P75) · nghiêng đắt 28.829–31.565 · **ĐẮT ≥31.565** (P90). P5 20.917, P50 25.924.
- **Sau khoá:** 13.300 (03/11) = 0,52× tâm, 0,55× base, 0,65× stress, P/B 0,86×; 0/729 bộ tham số < giá ⇒ **RẺ CÓ BIÊN AN TOÀN**. Định giá ngược: 100% phẳng + không tích cực 14.266; r 25% → 17.852; 100% xấu (g2031) 10.218; 100% rất xấu 6.516 [`compare_r5_out.txt`].
- Tổ hợp mốc [`post_lock_combo_r5_out.txt`]: 4 mốc tiêu cực 20.894; + holding 30% 18.618; + mỏ mới DCF r13 mọi kịch bản 15.052 (vẫn > giá). 4 mốc tích cực 33.332.
- So r4 (tâm 20.181): +5.544, gần như hoàn toàn do bỏ các khoản giảm trừ không có cơ sở (tái lập: đưa lại tất cả → 20.898, §2).

## 2. Kiểm kê khoản giảm trừ (đầy đủ: `r5/calc/inventory_r5.md`)
| Khoản r3/r4 | Hiệu ứng (đưa lại vào r5) đ/cp | Cơ sở độc lập? | r5 |
|---|---|---|---|
| Mỏ mới NPV mọi kịch bản, đất 431,9 đã chi coi là mất, sàn 30% | −1.351 | KHÔNG | Giá vốn 438,4 |
| ↳ upside kịch bản tốt (IRR 17–21%) | +1.375 (đã gồm trong tâm) | Có một phần (giá Bobby/NNC, chi phí Tân Lập hiệu chỉnh, công suất NQ, trữ lượng QĐ) | W tốt 25% |
| ↳ trễ GP 0/1/2 năm P .30/.40/.30 | −510 (đã gồm) | CÓ: Bobby trễ 2–4 năm; F6 0,30 | Giữ |
| ↳ NPV giá xấu áp lên mỏ mới | −2.299 | KHÔNG (còn quyền dừng ~1.062 chưa chi) | Độ nhạy |
| Cụm công nghiệp 500 tỷ thu hồi 70/50% | −1.571 / −2.618 | KHÔNG | NPV 0, ngoài lưới |
| Mua NNC lên 51% | 0 | Không có giá mua | NPV 0 |
| Holding 15% (30%) | −1.283 (−2.548) | KHÔNG | 0; độ nhạy |
| REL 0,87 | +173 (0,87 làm TĂNG giá trị do hiệu chỉnh biên) | CÓ cho 0,88–0,95 (Bobby Bình Phước cũ 334–360k/m³ ÷ NNC 380) | 0,91 |
| Vách 380→300 2028–30 ("cung mới", FPTS) | −658 | KHÔNG | Trượt 360/340/320; mốc 320 (GPM) giữ |
| Phẳng 10% trong tâm | −758 | KHÔNG cho phần gấp đôi tần suất 5% | Stress riêng |
| SL Tân Lập 1,20 từ 2028 | −386 | KHÔNG | 1,30 |
| MCC/NHC ×0,8, ICD ×0,6 | −115 (+ICD) | KHÔNG | Giá trị ghi sổ BCTC HN V.12 |
| NNC CIP Tam Lập = 0 ở xấu | −96 | KHÔNG | Mọi kịch bản |
| r 13% | 0 ở base mỏ mới | Khung user | Giữ cho dòng tiền hoạt động |
| Hạn GP Tân Lập W 2045/40/35 | ±1,4–1,8k | Chưa xác minh hai chiều | Giữ W |
| BIDV 451,9 > hạn mức 350; vay NH tài trợ dài hạn | không định lượng | CÓ (KT25 6.18, HN Q3 V.20) | Rủi ro hiện thực hoá, không trừ giá trị |
| **Đưa lại tất cả (trừ mỏ mới)** / **+ mỏ mới cách r3/r4** | −2.952 / **−4.827 → 20.898** (≈ r4 20.181; chênh do ramp 0,93, chi phí mỏ mới = Tân Lập, LK sổ sách BCTC) | | |

## 3. Mỏ mới — IRR/NPV từ dữ liệu [`model_r5_out.txt` mục 2; `post_lock_mine_wacc_out.txt`]
Đầu vào: giá = 0,91 × giá NNC kịch bản × đường giá; chi phí tiền mặt 145,2k/m³ (= Tân Lập, giữ biên 2026 200,6k); SGA 15 tỷ/năm; duy trì 3% DT; ramp 0,5/0,8/0,93 (0,93 = Tân Lập 1,3/1,4); 1,0+0,5 tr m³ nguyên khối × 1,42; trữ lượng 14,806 + 3,945; capex 1.500 (438,4 tại 2026; còn lại 60/40 2027–28); capex/trữ lượng thành phẩm 56,3k/m³.
| | IRR (không vay) | NPV r11 / r13 / r15 | NPV @ chi phí vốn hỗn hợp 5,98% |
|---|---|---|---|
| tốt g2031 / thực | 17,1% / 21,1% | 562/338/156 · 994/712/482 | 1.396 / 2.039 |
| cơ sở g2031 / thực | 8,0% / 12,3% | −230/−346/−440 · 105/−55/−185 | **208 / 705** |
| cơ sở phẳng (stress) | 1,5% | −530/−590/−639 | −315 |
| xấu g2031 / thực | −3,1% / 2,2% | −890/−925/−952 · −630/−700/−755 | −742 / −356 |
Lãi vay thực tế ≈4,55%/năm (lãi đã trả 9T 12,255 tỷ, LCTT mã 04, trên dư nợ bình quân 359,3 tỷ — ước lượng; vay dự án dài hạn chưa công bố). Đọc: ở giá cơ sở, IRR dự án 8–12% > chi phí vay; với vay ≤75% NPV dương ⇒ quyết định đầu tư nhất quán với "có lời". Ở r 13% (Ke) NPV cơ sở âm nhẹ — đúng là lý do r 13% không được làm dự án âm mặc định; base vẫn giá vốn.

## 4. Cầu nối base & kiểm sổ [`model_r5_out.txt` mục 1]
| tỷ | g2031 | thực |
|---|---|---|
| Tân Lập | 798,0 | 1.016,3 |
| Mỏ mới (giá vốn 438,4 − trễ kỳ vọng 48,7) | 389,7 | 389,7 |
| BOT 93,7 · gạch/xăng 41,5 · đất ở 150,0 · LK nhỏ+ICD 99,9 · Q4 50,0 | 435,1 | 435,1 |
| Nợ ròng 30/09 | −116,6 | −116,6 |
| **Phần trực tiếp** | 1.506,2 | 1.724,5 |
| Phần NNC (44,07%, vòng chéo) | 742,2 | 866,9 |
| **TỔNG** | **2.248,4 (22.484)** | **2.591,4 (25.914)** |
Kiểm sổ: VCSH HN 30/09 1.546,0 (BVPS 15.460) ⇒ base 1,57×; P/B hợp lý theo ROE ≈18,5% ex-hoàn nhập, r 13%, g 3% ≈1,55× ⇒ khớp. NNC ghi sổ 470,0 (BCTC HN V.12) vs phần NNC 742–867. Tổng MVC > phần NNC và phần trực tiếp > phần NNC ở 8/8 ô (4 kịch bản × 2 đường giá; rất xấu: trực tiếp 717–729 vs NNC 216–235). V_NNC nhất quán: 76.840 (g2031) / 89.749 (thực); tâm 85.124.

## 5. NNC-DD (mục 6 dispatch)
Có cùng lỗi: CIP Tam Lập 1 khu II 83,5 tỷ = 0 ở xấu/rất xấu ⇒ **+952 đ/cp NNC** (khung NNC-DD), +96 đ/cp MVC. Thêm: vách giá 300 (2028–30) → trượt: +2.200 đ/cp NNC (tâm nhất quán 85.124 vs 82.924); vách sản lượng 1,10 chưa rà (cần lý do GP/trữ lượng). Ghi vào `../dd_NNC_20261030/REPORT.md` §ghi chú nội bộ 03/11. KHÔNG dựng lại/gửi PDF NNC — báo Mike để user quyết.

## 6. Thang + điều kiện đổi nhận định
| Vùng | Nhãn | Đổi khi |
|---|---|---|
| ≤21.800 | RẺ CÓ BIÊN AN TOÀN | Xuống: bằng chứng giảm giá trị tài sản — giá Sở XD Q2/27 < −7%, vốn mỏ mới >1.950 tỷ, GP bị từ chối, nợ ròng >600 tỷ trước doanh thu mỏ mới |
| 21.800–23.600 | RẺ CÓ ĐIỀU KIỆN | tâm vào vùng này nếu W tốt 15% (23.477) hoặc chi phí Tân Lập +15% (23.476) |
| 23.600–28.800 | HỢP LÝ | |
| 28.800–31.600 / ≥31.600 | nghiêng đắt / ĐẮT | chỉ biện minh khi 4 mốc tích cực (33.332) |
Mốc: BCTC Q4/26 (≈20–30/01/2027: W −2.248/+3.727) · ĐHĐCĐ 2027 (~04/2027: hạn GP Tân Lập −1.792/+1.426; capex +30% −704) · GP mỏ mới 30/06/2027 (không trễ +510) · giá Sở XD Đồng Nai Q2/27 (≈31/08/2027: PW ∓867).

## Phụ lục E (nội bộ) — việc đổi nguyên tắc
1. Chỉ đạo user 03/11 17:06: đứng vai doanh nghiệp; không ai đầu tư để mất giá trị; base dùng giá trị sổ sách nếu không có cơ sở; tránh tuyệt đối DD cho rằng đầu tư dự án mới làm giảm giá trị. r4 sai ở đúng chỗ này (chương trình mỏ mới −495…−745 tỷ ở base, đất đã chi coi là mất).
2. Áp: dự án mới = giá vốn; khoản không cơ sở độc lập rời base (bảng §2); khoản có cơ sở giữ với xác suất (trễ GP, REL 0,91); upside chỉ khi có IRR từ dữ liệu.
3. Hệ quả: tâm 20.181 → 25.725; nhãn "rẻ có điều kiện" → "rẻ có biên an toàn". Điểm chưa chắc: (a) mức giá cơ sở 2031 (320k) vẫn neo kịch bản NNC-DD; (b) IRR mỏ mới ở r 13% âm nhẹ ở cơ sở — nếu skeptic cho rằng đó là "cơ sở độc lập" thì độ nhạy mỏ mới DCF mọi kịch bản là −1.351 (tâm 24.374), vẫn trong vùng hợp lý; (c) 13.300 ngày 03/11 lấy từ dispatch, chưa đối chiếu BQ (sync 23:45).
4. Chưa chạy fundamental-skeptic trên r5 (khuyến nghị trước khi gửi email: tập trung (a) có khoản giảm trừ base nào còn thiếu cơ sở; (b) có khoản cộng nào thiếu cơ sở — đất ở 150 tỷ kỳ vọng, LK theo sổ sách, ICD vốn góp).

## Tệp
`r5/calc/`: valuation_base.py · model_r5.py · model_r5_out.{txt,json} · grid_r5.csv · inventory_r5.md · LOCK_md5_r5.txt · compare_r5.py/_out · post_lock_mine_wacc.py/_out · post_lock_combo_r5.py/_out · nnc_glide_out.txt.
Báo cáo NĐT (đè): `investor_report/MVC_DD_investor_report_20261103.{md,pdf,html}`, `EMAIL_SUBJECT.txt`, `SELFCHECK.md`, `figs/`. Bản NĐT r4 lưu: `archive_internal/MVC_DD_investor_report_20261103_rev3.md`.
