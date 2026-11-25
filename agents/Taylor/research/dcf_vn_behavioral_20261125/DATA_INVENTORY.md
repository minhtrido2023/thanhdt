# Kiểm kê dữ liệu cho đặc trưng hành vi (job Taylor_20261125_104308, đo 25/11/2026)

Nguồn số: `calc/p1_features.py`, `calc/p4_cases.py` → `out/feat_build.json`, `out/inventory_cover.csv`, `out/feat_corr.csv`;
truy vấn `data/bq_cache/ticker/*.parquet` (DuckDB) trong phiên này; `kb/data_registry/feeds/*.md`. "Độ phủ" = tỉ lệ dòng
in-universe (panel V3.1 `out_F/vp2.parquet`) có giá trị.

## 1. Bảng có / không

| Đặc trưng hành vi | Có? | Nguồn — cột | PIT? | Độ phủ / độ sâu | Ghi chú |
|---|---|---|---|---|---|
| Đỉnh/đáy 52 tuần (`hi52`) | **Có** | `ticker.Close` (cache 2013-01-02→2026-11-23, 1.309 mã) + `px_pre2013_d.csv` (2006→2013, 130→631 mã/năm) + VNDirect mã vắng BQ (640 mã) | Có (chỉ dùng giá ≤ ngày) | 96,1% (2013) → 99,9% (2023) | Tính trên Close điều chỉnh; trước 2013 KHÔNG có High/Low (file chỉ Close/Price/Volume) ⇒ đỉnh theo giá đóng cửa |
| Giá vốn đám đông / overhang (`cgo`) | **Có, xấp xỉ** | `Volume` ngày ÷ `N` (số CP PIT của panel V3.1) | Có | 88,3% (2013) → 99,5% (2023) | Mẫu số là TỔNG số CP, không phải free-float (kho không có free-float PIT) ⇒ vòng quay bị thấp ở mã sở hữu cô đặc (VNM cgo 1,3–1,45 năm 2015–2017 — giá vốn "ì"); 4,4% dòng-ngày dùng N lấp ngược; `Volume` của vendor chưa kiểm đã điều chỉnh chia tách hay chưa |
| Đà 12-1, đảo chiều 1 tháng | **Có** | `Close` | Có | 88,3–99,5% / 100% | — |
| Số phiên trần/sàn | **Xấp xỉ** | `Price` thô ngày: đếm phiên |Δ| ≥ 6,5% trong 60 phiên (`n_up60`, `n_dn60`) | Có | 100% | **Kho KHÔNG có cột sàn niêm yết theo thời gian** cho mã BQ (chỉ file VNDirect của mã vắng BQ có `floor`; `new_listings_history.csv` có `exchange` hiện tại) ⇒ không phân biệt được chạm biên ±7 / ±10 / ±15; không có dư mua/dư bán trần |
| MAX (lợi suất ngày lớn nhất 21 phiên) | **Có** | `Close` | Có | 100% | Bị biên độ chặn ⇒ ở VN MAX ≈ đếm phiên trần (tương quan hạng với `n_up60` 0,62) |
| Vòng quay / chú ý (`to60`) | **Có, xấp xỉ** | `Volume`/`N` | Có | 100% | Cùng giới hạn free-float |
| Thanh khoản | **Có** | `Trading_Value_1M_P50` (`tv` trong panel), `universe_pit` | Có | cổng PIT sẵn | — |
| Khối ngoại mua/bán ròng theo MÃ | **Có nhưng CHƯA wire** | API VNDirect `/v4/foreigns` (`buyVal/sellVal/netVal/buyVol/sellVol/netVol`) | Có (theo ngày) | **Chỉ từ 2018-08-30** (gọi thử 25/11: dòng đầu của VNM = 2018-08-30, 2.056 dòng) | Không phủ IS 2014–2019 ⇒ chỉ dùng được cho OOS / theo dõi về sau; API bên thứ ba không hợp đồng |
| Room ngoại | **Có nhưng CHƯA wire** | cùng API: `totalRoom`, `currentRoom` | Có | từ 2018-08-30 | như trên |
| Khối ngoại cấp CHỈ SỐ | **Có** | `mike/data/fiinprox_foreign_flow_index_daily_20260914.csv` (2009-06→2018-08), `mike/data/fiinprox_vnindex_investor_flow_daily_20260914.csv` (2014-01→2026-09) | Có | 2.313 và 3.165 phiên (theo registry) | Chuỗi thị trường ⇒ N theo thời gian nhỏ; nguồn FiinPro-X trial đã hết hạn 2026-09-28, không cập nhật tiếp |
| Dòng tiền cá nhân (ròng, cấp chỉ số) | **Có** | file investor-flow ở trên, cột `local_individual_net_bn` | Có | đủ 5 nhóm từ 2016-04 (registry: UNVERIFIED cho 3 nhóm trong nước) | Chỉ giá trị RÒNG, cấp VNINDEX; **không có theo mã, không có tỉ trọng giao dịch cá nhân** ⇒ con số "cá nhân > 90%" KHÔNG đo được từ kho |
| Dư nợ margin (thị trường / theo mã) | **Không** | — | — | — | Không có feed; `data/margin_cycle_detector.csv` là chu kỳ BIÊN LỢI NHUẬN, không phải margin; `marginability_cache.json` chỉ là trạng thái hiện tại theo tài khoản |
| Danh mục cho vay margin / tỉ lệ ký quỹ lịch sử | **Không** | — | — | — | — |
| VNINDEX, P/E thị trường | **Có** | `VNINDEX.csv`, `ticker.VNINDEX_PE` | Có | `VNINDEX_PE` trống 30–31% dòng 2013–2015, 22% năm 2016, 0% từ 2017 | Bẫy đã ghi ở registry (`vnindex_pe_mirror_col.md`) |
| Breadth | **Có** | `tav2_mike.universe_pit` / `data/breadth_*.csv` | Có | — | Chuỗi thị trường |
| Trạng thái thị trường | **Có** | `vnindex_5state_dt5g_live` (`dt5g` trong panel) | Có | — | Chỉ để phân rã, không làm đặc trưng cắt ngang |
| Ngày công bố KQKD | **Có** | `ticker_financial.Release_Date` → `known` trong panel | Có | — | Nhánh VNDirect dùng độ trễ giả định 45/90 ngày (độ nhạy 90/120 đã làm ở V3.1) |
| Lãi suất huy động | **Có** | `deposit_rate_vn`, `idle_rate_proxy.py` | Có | — | Chuỗi thị trường |
| Giá số tròn / bước giá | **Có** | `Price` thô | Có | 100% | Chưa dựng; bước giá HOSE đổi theo thời kỳ ⇒ cần bảng quy định |
| Mã huỷ niêm yết | **Một phần** | VNDirect finfo: 640 mã vắng BQ có giá (từ 2013-01) | Có | trước 2013: KHÔNG | Trước 2013 panel chỉ có mã BQ còn sống ⇒ thiên lệch sống sót |
| `ticker_1m` | Không dùng | ảnh chụp ~1 tháng | — | — | Không có lịch sử ⇒ vô dụng cho nghiên cứu |
| `ticker_prune`, `profit_*` | **Cấm** | — | — | — | TRAP / nhìn trước |

## 2. Tương quan hạng giữa các đặc trưng (in-universe, 2014+; `out/feat_corr.csv`)
`hi52`–`cgo` 0,67 · `hi52`–`mom` 0,45 · `hi52`–`rev1` 0,47 · `cgo`–`mom` 0,49 · `lv_ENS2`–`ep` 0,53 ·
`lv_ENS2`–`lv_L2_ENS2` 0,54 · `lv_L2_ENS2`–`mom` −0,43 · `lv_ENS2`–`hi52` −0,17 · `max21`–`n_up60` 0,62.
⇒ Ba đặc trưng "neo" (hi52, cgo, đà) là MỘT cụm; số tham số hữu hiệu ít hơn số đếm. Lớp 2 (rẻ so lịch sử của chính mã)
ngược chiều với đà: mã "rẻ lớp 2" thường là mã vừa rớt giá.

## 3. Khoảng trống quyết định thiết kế
1. **Không có sàn niêm yết PIT** ⇒ đặc trưng trần/sàn chỉ là xấp xỉ; muốn làm đúng cần Winston dựng bảng mã–sàn–ngày chuyển sàn.
2. **Không có free-float PIT** ⇒ giá vốn đám đông lệch ở mã sở hữu cô đặc (nhà nước, ngoại nắm giữ lớn).
3. **Khối ngoại / room theo mã chỉ từ 2018-08** ⇒ không kiểm được trong IS; nếu thêm thì bằng chứng chỉ là OOS + theo dõi về sau.
4. **Không có margin** ⇒ chuỗi "margin-call" không đo trực tiếp được; proxy khả dĩ duy nhất: chuỗi phiên sàn liên tiếp + khối lượng (chưa dựng).
5. **Thời gian độc lập ít**: in-universe bắt đầu 2013; pilot h = 12: IS 5 năm as-of, OOS 6 năm; h = 24: 4 và 5 năm.
6. Panel có `lv_ENS2` cho 2009–2012 (3.014 → 6.373 dòng/năm) nhưng `in_universe` = 0 trước 2013 và không có mã đã huỷ ⇒ dùng làm
   mẫu giữ lại được, nhưng chịu thiên lệch sống sót và phải tự dựng cổng thanh khoản.
