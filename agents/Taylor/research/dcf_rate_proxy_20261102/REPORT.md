# REPORT — lãi suất và discount rate DCF VN: chọn proxy · job Taylor_20261102_012810 · 02/11/2026
R&D thuần. Không sửa `dcf_valuation.py`, không merge; `domestic_v2` (r = 12,25% hằng, g_T cap 5,5%) giữ mặc định.
PREREG `43f941991` (commit trước mọi số). Số: `out/*.csv`, log `out/run_main.txt`, `out/run_extra.txt`. Hình: `out/rstar_vs_proxies.png`.

## Kết luận trước
- **(A) Lãi huy động Big-4: đúng chiều nhưng TRỄ và biên độ nhỏ — không đủ nhạy làm proxy.** Big-4 1M (số thật, 2019+) đúng chiều ở cả 3 giai đoạn. Nhưng năm 2026 nó chỉ tăng +0,5pp (12/2025→09/2026), trong khi r\* thị trường tăng +2,8pp và EY VNINDEX +1,9pp. Năm 2022 nó chỉ bật lên ở 10/2022: liên NH 3M đã tăng từ 07/2022, P/E đã rơi từ 05/2022. Liên NH dẫn Big-4 1M một tháng (Δ1M, độ trễ 1: tương quan 0,55, CI [0,23; 0,68]). Chuỗi Big-4 **12M** (`deposit_rate_vn`) là 26 mốc neo **hồi tố** một lần ngày 19/06/2026, nên không kiểm được như một chuỗi PIT. Chuỗi trông "đẹp" nhất (Δr\*/Δproxy ổn định 1,5–1,9) chính là chuỗi dựng sau khi đã biết kết quả.
- **(B) Proxy hợp lý hơn: TPCP 10Y. Đó là chuỗi DUY NHẤT đạt luật khai trước, nhưng chỉ đạt sát nút.** Nó đúng chiều 3/3 với cả r\* lẫn EY, đủ nhạy 2/3 giai đoạn, PIT từ 2014. Năm 2026 nó chỉ +0,45pp (0,38 SD), và tương quan Δ3M với r\* chỉ 0,05, CI [−0,46; 0,62]. Liên NH 3M nhạy nhất ở 2022/2023 (+6,6 / −5,3pp) nhưng sai chiều ở 2026 vì mốc 12/2025 dính đợt căng thanh khoản cuối năm; đổi mốc sang TB 3 tháng (ngoài PREREG) thì đúng 3/3. Lãi tái cấp vốn không đổi từ 06/2023 nên mù hoàn toàn với 2026. Khoảng huy động NHNN >12–24M sai chiều năm 2023 (tăng tiếp tới 09/2023). **Không có trong dữ liệu**: lãi cho vay bình quân theo tháng, chuỗi huy động NH tư nhân lịch sử.
- **(C) Không nên gắn r vào lãi suất. Giữ r hằng 12,25%.** Có ba lý do.
  1. r giống nhau cho mọi mã trong cùng tháng, nên thứ hạng MoS không đổi (tương quan hạng = 1,0 ở mọi tháng, mọi kịch bản). Lãi suất chỉ dời MỨC FV, không đổi việc chọn mã.
  2. Về mức, cho r theo TPCP 10Y làm tín hiệu "%RẺ thị trường" tệ đi. Ở đỉnh 03/2022, %RẺ tăng 44,9 → 58,2%, tức báo "rẻ" đúng lúc đỉnh, vì lãi suất khi đó còn thấp. Tương quan với lợi suất 12 tháng tới giảm 0,26 → 0,16 (hiệu −0,10, CI [−0,79; +0,39]).
  3. Nếu cho g_T đi theo, kết quả trùng r hằng (r − g_T hằng). **Nếu đã gắn lãi suất thì thành phần đúng là rf (ERP và g_T giữ hằng), nhưng dữ liệu không ủng hộ việc gắn.**
- **Cơ chế:** ở VN, lãi suất và giá biến động CÙNG THÁNG (TPCP 10Y: Δ1M vs Δlog P/E −0,29, CI [−0,48; −0,10]; đỉnh tương quan ở độ trễ 0). Cho r theo lãi suất thì FV rơi cùng lúc với giá, nên MoS bị "trung hoà" và mất tính ngược chu kỳ. r hằng để giá tự kéo MoS đi, và đó mới là biên an toàn.
- **Nên hiển thị thêm (không đổi FV): r\* thị trường.** Hôm nay **15,1%**, so với 12,25% hằng. Mức này ngang đáy 11/2022 (15,6%) và cao hơn 12/2025 (12,3%). Đây là thước đo trực tiếp "thị trường đang chiết khấu nặng tới đâu", không cần proxy lãi suất hành chính.

## r\* — lãi suất ngầm định thị trường (PIT, panel universe_pit, số CP live)
r\* tháng t = r sao cho median log(P/FV) = 0 trên rổ, với FV đúng công thức production (s = 0,5, g_T 5,5%). Chạy trên 155 tháng, 12/2013→10/2026. Sai số nghiệm tối đa 7,8e−6 (SELFCHECK). Đổi g_T sang 4,5% thì r\* dịch xuống khoảng 0,9pp, còn Δ thì trùng (±0,05pp), nên mọi kết luận về thay đổi không phụ thuộc g_T.
| Mốc | r\* | EY VNI (%) | P/E VNI | TPCP 10Y | Liên NH 3M (TE TB tháng) | Big-4 1M | Big-4 12M\* |
|---|---|---|---|---|---|---|---|
| 12/2021 | 12,1 | 5,8 | 17,3 | 2,09 | 1,90 | 3,0 | 5,5 |
| 12/2022 | 15,9 | 9,3 | 10,8 | 5,12 | 8,54 | 4,9 | 7,5 |
| 12/2023 | 12,2 | 7,4 | 13,4 | 2,42 | 3,22 | 2,4 | 5,0 |
| 12/2025 | 12,3 | 6,4 | 15,5 | 4,13 | 7,45 | 1,6 | 5,2 |
| 10/2026 | 15,1 | 8,4 | 12,0 | 4,58 | 7,05 | 2,1 (09/2026) | 6,8 |
\* hồi tố, không PIT. Nguồn: `out/episode_levels.csv`, `out/monthly_series.csv`.

## Bảng proxy × 3 giai đoạn (Δ pp; trong ngoặc là Δ/SD(Δ12T); ✓/✗ = cùng dấu với Δr\* / ΔEY) — `out/episodes.csv`
| Proxy | PIT từ | 2022 tăng (12/21→12/22) | 2023 giảm (12/22→12/23) | 2026 tăng (12/25→10/26) | Đạt luật? |
|---|---|---|---|---|---|
| **r\* (mục tiêu)** | — | +3,84 (1,75) | −3,76 (−1,71) | +2,79 (1,27) | — |
| **EY VNINDEX (độc lập)** | — | +3,53 (2,56) | −1,86 (−1,35) | +1,92 (1,39) | — |
| **TPCP 10Y** (TE) | 2007 | +3,03 (2,54) ✓✓ | −2,70 (−2,26) ✓✓ | +0,45 (0,38) ✓✓ | **ĐẠT** (duy nhất) |
| Liên NH 3M (TE, TB tháng) | 2012 | +6,63 (3,06) ✓✓ | −5,31 (−2,45) ✓✓ | −0,39 (−0,18) ✗✗ | không (chiều 2026) |
| Liên NH 3M (FiinPro, 1 phiên) | 2014 | +5,81 (2,53) ✓✓ | −6,16 (−2,68) ✓✓ | −1,22 (tới 09/26) ✗✗ | không |
| Liên NH 1M / 1W / ON | 2014 | +1,8 / +2,7 / +3,7 ✓ | −2,2 / −1,4 / −3,9 ✓ | −1,3 / −3,6 / −0,7 ✗ | không |
| Big-4 huy động 1M | 2019-02 | +1,90 (1,62) ✓✓ | −2,50 (−2,13) ✓✓ | +0,50 (0,43, tới 09/26) ✓✓ | không (PIT chỉ từ 2019) |
| Big-4 huy động 12M | hồi tố | +2,00 (1,94) ✓✓ | −2,50 (−2,43) ✓✓ | +1,60 (1,56) ✓✓ | không (không PIT) |
| NHNN huy động >12–24M, đầu thấp / cao | 2011 | +0,7 / +0,9 ✓ | **+1,2 / +0,7** ✗ | +1,1 / +1,2 ✓ | không (trễ ~9 tháng) |
| Lãi tái cấp vốn | 2006 | +2,00 ✓✓ | −1,50 ✓✓ | 0,00 (không đổi) | không |
| CCTG Big-4 6M | 1 mốc 09/2026 | — | — | — | không đo được |
| Lãi cho vay tháng / huy động NH tư nhân | **KHÔNG CÓ** | | | | |

Tỉ số Δr\*/Δproxy theo giai đoạn: TPCP 10Y 1,27 / 1,39 / **6,22**; liên NH 3M (TE) 0,58 / 0,71 / **−7,13**. Không proxy PIT nào có hệ số truyền dẫn ổn định qua 3 giai đoạn.
Độ bền mốc (NGOÀI PREREG, `out/episodes_avg3_ngoai_prereg.csv`, mốc = TB 3 tháng): liên NH 1M/3M (cả hai nguồn) chuyển sang đúng chiều 3/3. Kết quả liên NH ở 2026 vì vậy **phụ thuộc mốc**, chưa phải bằng chứng ngược chiều.

## Dẫn trước / trễ (Δ1M, 2014–2026, CI khối 12 tháng) — `out/leadlag.csv`, `out/leadlag_ci.csv`
- **Với thị trường (Δlog P/E, ΔEY):** mọi proxy thị trường đạt đỉnh tương quan ở **độ trễ 0**: TPCP 10Y −0,29 [−0,48; −0,10], liên NH 3M FiinPro −0,33 [−0,44; −0,16], TE −0,27 [−0,42; −0,10], Big-4 1M −0,35 [−0,58; −0,02]. Các chuỗi hành chính (Big-4 12M, NHNN >12M, tái cấp vốn) ở độ trễ 0 có tương quan quanh 0. Không có proxy nào dẫn trước giá đủ để dùng.
- **Với r\*:** liên NH 3M đạt đỉnh ở độ trễ −1 (0,26–0,31, CI loại 0), tức **thị trường dẫn liên NH một tháng**, không phải ngược lại. Δr\* theo tháng nhiễu vì FV đổi theo kỳ BCTC, nên ưu tiên đọc dòng P/E/EY.
- **Liên NH dẫn huy động: ĐÚNG.** Liên NH 3M (TE) → Big-4 1M: độ trễ 1, 0,55 [0,23; 0,68]. TPCP 10Y → Big-4 1M: độ trễ 1, 0,56 [0,25; 0,73]. Liên NH → NHNN >12M: đỉnh ở độ trễ 6 (0,31–0,37). Huy động là phần cuối của chuỗi truyền dẫn: liên NH/TPCP → (1 tháng) Big-4 ngắn hạn → (~6 tháng) huy động dài hạn.

## (iv) PIT / ngày dùng được
| Chuỗi | Dùng được từ | Ghi chú |
|---|---|---|
| TPCP 10Y, liên NH 3M (TE) | phiên kế tiếp | BQ `tav2_bq.macro_indicator`, vintage 30/10–01/11/2026; **chưa có entry trong `kb/data_registry/`** (UNVERIFIED, chưa đối chiếu nguồn thứ hai) |
| Liên NH 4 tenor (FiinPro) | T+1 | MỘT phiên cuối tháng; hết nguồn sau 09/2026 |
| Big-4 1M (FiinPro) | trong tháng (mốc ngày 15) | 2019-02→2026-09; không có nguồn nối tiếp |
| NHNN huy động >12–24M | ~đầu tháng sau | trong kịch bản đã trễ 1 tháng |
| Big-4 12M `deposit_rate_vn` | — | hồi tố trước 06/2026 |
| Tái cấp vốn | ngày hiệu lực | |

## Ba kịch bản DCF — `out/scen_*.csv`
(b) r_t = proxy_t + ERP_b, với ERP_b chọn để TB r 2014–2026 = 12,25% (trung tính về mức). TPCP 10Y: ERP_b 7,72, r trong khoảng 9,8–16,6%. sbv_lo chạy để minh hoạ, **không đạt luật**: ERP_b 6,06, r 10,9–13,6%. (c) như (b), cộng thêm g_T đi theo 1:1.
| Kịch bản | r hôm nay | FV trung vị vs (a) | %RẺ 10/2026 | Lật RẺ→ĐẮT / ĐẮT→RẺ | %RẺ 03/2022 (đỉnh) | 11/2022 (đáy) | 12/2023 | Spearman(%RẺ, lợi suất VNI 12T tới) | Hiệu vs (a) [CI95] |
|---|---|---|---|---|---|---|---|---|---|
| (a) r hằng 12,25% | 12,25 | — | 66,0% | — | 44,9% | 66,8% | 49,7% | 0,26 [−0,10; 0,67] | — |
| (b) TPCP 10Y | 12,30 | −0,8% | 65,3% | 1 / 0 | 58,2% | 65,3% | 62,7% | 0,16 [−0,30; 0,52] | −0,10 [−0,79; +0,39] |
| (c) TPCP 10Y, g_T theo | 12,30 | −0,1% | 66,0% | 0 / 0 | 46,4% | 65,8% | 51,0% | 0,26 | −0,00 [−0,04; +0,03] |
| (b) sbv_lo (minh hoạ) | 12,16 | +1,4% | 66,7% | 0 / 1 | 49,0% | 67,9% | 44,4% | 0,40 [0,14; 0,64] | +0,14 [−0,17; +0,33] |
| (c) sbv_lo, g_T theo | 12,16 | +0,1% | 66,0% | 0 / 0 | 46,0% | 66,8% | 49,0% | 0,27 | +0,01 [−0,01; +0,02] |
Tiêu chí PREREG: hiệu > 0 và CI không chứa 0. **Không kịch bản nào đạt, nên không phân biệt được.** Tương quan hạng MoS so với (a): 1,0 ở mọi tháng.
Hôm nay FV gần như không đổi là do **cách hiệu chuẩn ERP**, không phải do proxy. TPCP 10Y hôm nay (4,58) ≈ TB 2014–2026 (4,53). Nếu hiệu chuẩn ERP theo cửa sổ 2019+ (ngoài PREREG, `out/erp_window_ngoai_prereg.csv`) thì r hôm nay là 13,48%. Tức câu "r hôm nay bao nhiêu" do lựa chọn cửa sổ quyết định.

**Độ nhạy FV hôm nay theo r** (ngoài PREREG, `out/sens_today_ngoai_prereg.csv`, n = 147):
| Δr | g_T giữ 5,5% | g_T đi theo |
|---|---|---|
| −1pp | FV +17,9%, %RẺ 70,7% | +1,3% |
| +1pp | FV −13,3%, %RẺ 57,8% | −1,3% |
| +2pp | FV −23,5%, %RẺ 53,7% | −2,5% |
| +2,89pp (r = r\* hôm nay) | FV −30,9%, %RẺ 49,7% | −3,6% |
Nếu có ngày phải gắn r theo lãi suất thì chỉ gắn **rf**, giữ ERP và g_T hằng. Cho g_T đi theo thì độ nhạy biến mất (đúng như kết quả cũ `dcf_discount_rate_rf_slow_20261013`). Gắn ERP thì vô nghĩa vì đã có rf.

## Đề xuất (không wire)
1. Giữ r hằng 12,25%. Không thay rf bằng Big-4 huy động hay bất kỳ proxy nào ở trên.
2. Nếu user muốn thấy rủi ro lãi suất trong báo cáo, **hiển thị thêm** hai dòng, không đổi FV hay cờ RẺ/ĐẮT:
   - (i) r\* thị trường, kèm vị trí so với lịch sử (hôm nay 15,1%, đỉnh 2022 là 15,9%);
   - (ii) TPCP 10Y kèm Δ12 tháng.
3. Điều kiện dữ liệu trước khi dùng TPCP 10Y / liên NH 3M ở bất kỳ đâu:
   - thêm entry `kb/data_registry/macro/` cho `tav2_bq.macro_indicator` (writer, cron, vintage);
   - đối chiếu ≥3 mốc với nguồn thứ hai (HNX/VBMA cho TPCP, `dttktt.sbv.gov.vn` cho liên NH), lệch ≤0,2pp.
   - Nếu cần một chuỗi huy động thị trường thật (NH tư nhân), phải mua/chụp nguồn: hiện chỉ có CCTG tier2 từ 10/2026.

## Hạn chế (đọc trước khi trích số)
1. **N = 3 giai đoạn**, nên không tuyên bố ý nghĩa thống kê. Các CI theo tháng dựa trên khoảng 150 tháng tự tương quan (khối 12). Test dự báo dùng cửa sổ 12 tháng chồng nhau: 142 tháng tương đương khoảng 12 quan sát độc lập.
2. r\* dựng từ chính DCF, mang theo các vấn đề mức đã biết (`dcf_level_rerun_20261102`: hố giữa nhóm phát hành và nhóm ổn định). EY là thước đo độc lập, và nó cho cùng chiều 3/3.
3. Kịch bản (b) hiệu chuẩn ERP trên TB toàn kỳ, nên mức có hindsight (đúng như PREREG khai). Phần biến thiên theo thời gian thì PIT.
4. Kết quả liên NH ở 2026 nhạy với mốc (mốc điểm vs TB 3 tháng). FiinPro liên NH là một phiên cuối tháng.
5. TPCP 10Y và liên NH TE chưa được đối chiếu nguồn thứ hai. Dữ liệu là vintage fetch 30/10–01/11/2026.
6. Big-4 1M dừng ở 09/2026. Big-4 12M hồi tố. Không có chuỗi cho vay theo tháng, không có chuỗi huy động NH tư nhân lịch sử.
7. Số ô thử: 11 proxy × 3 giai đoạn × 2 mục tiêu (luật chọn), 5 kịch bản DCF. Không chọn theo lợi suất nên không tính DSR.

## Tái lập
`source wc_env.sh`, rồi chạy `/home/trido/thanhdt/wc_venv/bin/python analysis.py`, tiếp theo `extra.py`, `selfcheck_tz.sh`.
Dữ liệu `data/te_macro.csv` và `data/vnindex_pe.csv` lấy bằng `bq query` (lệnh ở SELFCHECK.md). Panel lấy từ `../dcf_level_rerun_20261102/data/panel_live.parquet`.
