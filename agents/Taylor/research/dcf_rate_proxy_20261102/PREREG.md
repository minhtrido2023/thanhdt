# PREREG — proxy lãi suất cho discount rate DCF VN · job Taylor_20261102_012810 · 02/11/2026
Viết và commit TRƯỚC khi chạy bất kỳ số đo nào dưới đây. R&D thuần: không sửa `dcf_valuation.py`, không merge, `domestic_v2` giữ mặc định.

## Kiểm kê nguồn (đã làm trước PREREG — chỉ liệt kê, chưa đo quan hệ)
| Mã | Chuỗi | Nguồn | Phủ | PIT? |
|---|---|---|---|---|
| dep12 | Big-4 huy động 12M | `deposit_rate_vn.py` DEPOSIT_EVENTS | 2011→ | **KHÔNG** — 26 mốc neo hồi tố 1 lần 2026-06-19 từ hình dạng lending-rate TE (registry caveat b) |
| dep1m | Big-4 huy động 1M cá nhân | FiinPro snapshot `idle_cash_proxy_20260927/` | 2019-02→2026-09 | có (biểu niêm yết, mốc ngày 15) |
| sbv_hi / sbv_lo | NHNN: khoảng lãi suất huy động phổ biến kỳ hạn >12–24M, đầu cao/thấp | FiinPro snapshot | 2011-01→2026-08 (khuyết 10 tháng, ffill) | có, công bố tháng (trễ ~1 tháng) |
| refi | Lãi tái cấp vốn NHNN | `sbv_macro_overlay.SBV_REFI_EVENTS` | 2006→ | có (quyết định công khai ngày hiệu lực) |
| ib_on/1w/1m/3m | Liên NH BQ, **một phiên cuối tháng** | FiinPro snapshot | 2014-01→2026-09 | có (T+1) |
| te_ib3m | Liên NH 3M ngày → TB tháng | BQ `tav2_bq.macro_indicator` (Trading Economics), vintage fetch 30/10–01/11/2026 | 2012→2026-10 | thị trường, gần PIT; nguồn **chưa có trong data_registry** (UNVERIFIED) |
| gb10 | TPCP 10Y lợi suất ngày → TB tháng | BQ `macro_indicator` `vn_bond_10y` (TE) | 2007-03→2026-10 | như trên, UNVERIFIED |
| cctg6m | CCTG Big-4 6M | `cctg_rate_vn.py` | 1 mốc 2026-09 (+tier2 10/2026) | — chỉ mô tả, không đo |
| — | Lãi suất cho vay bình quân THEO THÁNG | **KHÔNG CÓ** (chỉ năm, WB/TE, tới 2023, `data/macro_daily.csv`) | | |
| — | Huy động NH tư nhân cao nhất (chuỗi lịch sử) | **KHÔNG CÓ** (chỉ CCTG tier2 từ 10/2026; `sbv_hi` là đầu cao của khoảng toàn hệ thống — proxy gián tiếp) | | |

## Biến mục tiêu (thị trường)
- **r\*** tháng t (cuối tháng 2013-12→2026-10, panel `dcf_level_rerun_20261102/data/panel_live.parquet`: universe_pit, OShares live PIT, base_valid, Price>0): r sao cho median log(P/FV) = 0, FV = đúng công thức production (`level.fv`, s=0,5, g_T = min(g_T thô, 5,5%)). Giải bằng chia đôi trên [5%, 40%]. Kiểm độ bền: r\* với g_T 4,5%.
- **EY** = 1/VNINDEX_PE (BQ `ticker.VNINDEX_PE`, đã backfill; TB tháng của phiên). Thước đo độc lập, không qua DCF.
- **ΔlogVNI**: log Close VNINDEX cuối tháng.

## Giai đoạn (lịch, theo câu hỏi user — không chọn theo giá)
E1 2022 (tăng): 2021-12 → 2022-12 · E2 2023 (giảm): 2022-12 → 2023-12 · E3 2026 (tăng): 2025-12 → 2026-10 (hoặc tháng cuối có dữ liệu).
Δ = giá trị cuối − đầu. **N = 3 giai đoạn độc lập** ⇒ không tuyên bố ý nghĩa thống kê.

## Đo cho mỗi proxy
(i) Δ trong E1/E2/E3 (pp) và Δ chuẩn hoá = Δ / SD(Δ12 tháng của chính proxy, 2014-01→2026-10).
(ii) Lead-lag: tương quan chéo Δ1M proxy vs Δ1M r\*, Δ1M log PE, Δ1M logVNI, độ trễ k = −6..+6 (k>0 ⇒ proxy DẪN), mẫu 2014-02→2026-10; CI 95% bootstrap khối 12 tháng (2.000 lần, seed 20261102) cho k=0 và k tốt nhất. Thêm: Δ1M ib_1m/ib_3m/te_ib3m vs Δ1M sbv_lo/dep1m (giả thuyết liên NH dẫn huy động).
(iii) Mỗi giai đoạn: dấu Δproxy so với dấu Δr\*, dấu ΔEY, dấu −ΔlogPE; tỉ số Δr\*/Δproxy.
(iv) Bảng PIT/công bố (ngày dùng được).

## Luật chọn "proxy tốt nhất" (khai trước)
Đạt cả: (a) cùng dấu với Δr\* VÀ ΔEY ở **3/3** giai đoạn; (b) |Δ chuẩn hoá| ≥ 0,5 ở ≥ 2/3 giai đoạn; (c) PIT thật từ ≤ 2014 (dep12 bị loại ở (c); dep1m chỉ 2019+ ⇒ chỉ được xếp "hạng phụ").
Trong số đạt, chọn tương quan Δ3M (không chồng, cuối quý) proxy vs Δ3M r\* lớn nhất 2014-2026. Không proxy nào đạt ⇒ **"không đủ bằng chứng, giữ r hằng"**.

## Ba kịch bản DCF (trên panel trên)
(a) r = 12,25% hằng, g_T cap 5,5% (production).
(b) r_t = proxy_t + ERP_b; ERP_b hằng chọn để TB r_t 2014-01→2026-10 = 12,25% (trung tính về mức, chỉ còn biến thiên theo thời gian); g_T cap 5,5% (theo CPI+GDP — g thô ≥ 8,77% nên cap luôn ràng buộc), KHÔNG cap theo rf; chặn r − g_T ≥ 1pp.
(c) như (b) nhưng g_T_t = 5,5% + (proxy_t − TB proxy) (r − g_T hằng).
Proxy cho (b)/(c): proxy tốt nhất theo luật trên; nếu không có thì chạy minh hoạ với gb10 và sbv_lo, gắn nhãn "minh hoạ, không đạt luật".
Đo: (1) tháng cuối: FV trung vị vs (a), %RẺ (MoS>0), số mã lật RẺ↔ĐẮT; (2) chuỗi %RẺ thị trường theo tháng — giá trị tại 2022-03 (đỉnh), 2022-11 (đáy), 2023-12, 2026-10; (3) Spearman(%RẺ_t, log lợi suất VNINDEX 12 tháng tới) 2014-01→2025-10, CI khối 12 tháng; báo hiệu (b)−(a), (c)−(a); (4) tương quan hạng MoS cắt ngang giữa kịch bản (min theo tháng).
Tiêu chí "cải thiện": (b) hoặc (c) có Spearman ở (3) cao hơn (a) VÀ CI của hiệu không chứa 0; ngược lại báo "không phân biệt được".

## Self-check
SELFCHECK.md: (1) r\* tại 12,25% ⇒ FV khớp `level.fv` 0 lệch; (2) kịch bản (a) tháng cuối khớp V0 của `dcf_level_rerun/out/level_live_impact_20261030.csv` (%RẺ 66,0%); (3) chạy lại toàn bộ dưới `env -u TZ` và `TZ=America/New_York`, md5 out/*.csv trùng.
