---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-09 (lô dd_lagcand_20261109). KHÔNG biết mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về doanh nghiệp khí cụ thể.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành khí đốt VN (thu gom–xử lý–vận chuyển khí khô bể Cửu Long/Nam Côn Sơn/PM3, cấp khí cho điện–đạm–công nghiệp, LNG nhập khẩu + dự án điện LNG, LPG nhập khẩu/phân phối). Gồm pipeline cầu, đa proxy giá (Brent/MFO/JKM/LNG hợp đồng/LPG CP), cấu trúc cạnh tranh/rào cản, phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED theo 2 tầm, FORECAST khoá trước 20/60/120 ngày + sự kiện, checklist DD.
as_of: 2026-11-09 (BQ commodity tới 2026-11-06; snapshot vĩ mô dd_lagcand_20261109 có áp độ trễ công bố; tin web ≤ 2026-11-01)
---

# SECTOR READ: Khí đốt / phân phối khí & LPG Việt Nam, as-of 09/11/2026 (Bobby, real-time BLIND)

Bản đọc này không phải episode VNINDEX và không vào N_effective. Nhãn: **[DK]** dữ kiện có nguồn + ngày; **[UĐ]** ước đoán /
suy luận của Bobby; **[NỀN]** hiểu biết nền chưa kiểm lại trong lượt này. File chị em dùng để đối chiếu bối cảnh (cùng cú
sốc Hormuz): `sector_read_phan_dam_ure_20261104.md` (giá khí cấp đạm, kịch bản K1/K2/K3), `sector_read_oil_gas_shipping_20261029.md`
(cước VLGC/LPG, Brent/Urals), `sector_read_power_consulting_20261028.md` (tiến độ PDP8, thiếu điện 2027-2030).

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Repo đã đọc:** 3 file chị em ở trên (mục phân loại / FORECAST / pipeline PDP8), `market-state/index.md`, snapshot
  `agents/Taylor/research/dd_lagcand_20261109/macro_snapshot_20261109.md` (chỉ file đó trong thư mục; KHÔNG mở file nào khác
  trong `dd_lagcand_20261109/` hay `agents/Taylor/*`).
- **BQ (tự truy vấn 09/11):** `tav2_bq.commodity_prices`, luôn chỉ rõ `source`, loại T7/CN:
  - `trading_economics` daily: `brent`, `liquefied_natural_gas_japan_korea` (JKM-proxy), `eu_natural_gas` (TTF), `propane` (Mont Belvieu, USD/gal).
  - `sunsirs` daily: `lpg` (LPG nội địa TQ, CNY/t), `fuel_oil` (FO nội địa TQ, CNY/t — proxy HƯỚNG cho MFO).
  - `worldbank_cmo` monthly: `lng_japan` (giá LNG nhập khẩu Nhật bình quân ≈ hợp đồng gắn dầu), `brent`, `natural_gas`.
  - Không dùng view `commodity_latest`.
- **Không có trong BQ (ghi "không có số", không suy):** giá khí khô bán cho điện/đạm/công nghiệp VN, MFO Singapore, Saudi CP
  (lấy từ báo), sản lượng khí VN theo tháng, giá LNG nhập khẩu thực của VN, cước đường ống.
- **Rò rỉ không chủ ý (ghi trung thực, KHÔNG dùng cho phân loại/forecast/bảng số):** bản tóm tắt công cụ tìm kiếm đã trích
  (a) kết quả kinh doanh 9T/2026 của một DN phát điện khí (doanh thu/LNTT, khoản thu hồi chênh lệch tỷ giá–giá khí);
  (b) tiêu đề một bài phân tích cổ phiếu nói lợi nhuận của nhà vận hành khí trung nguồn "thăng hoa nhờ giá dầu" và nhắc
  "câu chuyện thoái vốn nhà nước"; (c) một số dự báo sản lượng khí 2026 từ tài liệu CTCK (7,2 tỷ m³); (d) số liệu vận hành của
  một nhà phân phối khí thấp áp Đông Nam Bộ (sản lượng T1/2026 +19% YoY, giảm giá 3-5% Q4/2025). Với (a)-(c): bỏ hẳn.
  Với (d): chỉ dùng như **chỉ báo định tính** "cầu khí công nghiệp chuyển đổi từ than/dầu đang tăng", không dùng con số.
  Cơ chế "giá bán gắn dầu, giá mua miệng giếng mỏ cũ gần như cố định" cũng xuất hiện trong (b); tôi coi nó là **[NỀN]** (hiểu
  biết ngành phổ biến) và đưa vào mục DD để KIỂM, không dùng làm dữ kiện.
- **Không mở:** báo cáo CTCK (ACBS 2H.2026, VDSC/researchpool, DSC, VCBS, HSC, vietstock downloadedoc, elibook), không tra giá
  cổ phiếu, BCTC hay KQKD quý của DN nào. Một số URL ở mục Nguồn có tên DN trong đường dẫn — người đọc blind sau nên bỏ qua mục Nguồn.

## 1. Chuỗi giá và đa proxy [DK, BQ trừ khi ghi khác]
| Chuỗi | Hiện tại | Mốc so sánh | Ghi chú |
|---|---|---|---|
| Brent TE (USD/bbl) | **TB5 = 100,99** (02-06/11: 105,76 / 103,10 / 100,61 / 97,17 / 98,32). TB T10 107,33, max 116,72 | TB T11/2025 63,49 ⇒ **+59% YoY**. TB T1-T2/2026 64,6-69,4; T3 98,1; T6-T7 84-85; T9 100,8 | Rơi ~16% từ đỉnh 28/10 (115,95) trong 7 phiên — thị trường định giá khả năng thoả thuận Hormuz (file urê: kế hoạch mở eo do Qatar trung gian, 02/11). Chưa có văn bản thoả thuận |
| FO nội địa TQ (sunsirs, CNY/t) | T11 **8.005** | T11/2025 5.380 ⇒ **+49% YoY** | Proxy độc lập về HƯỚNG cho MFO Singapore (biến tham chiếu trong công thức giá khí khô VN [NỀN]). Đồng thuận Brent về hướng; **chưa** giảm theo Brent đầu T11 |
| LNG giao ngay Đông Bắc Á (TE `liquefied_natural_gas_japan_korea`, USD/MMBtu) | **TB5 = 31,63** (02-06/11) | T11/2025 11,25 ⇒ **×2,8**. T3/2026 18,3; T8 22,0; T10 28,3 | **Không** giảm theo Brent đầu T11. Mùa đông Bắc bán cầu + công suất Ras Laffan bị hư hại (~17%, AXS Marine T3) + Qatar gia hạn bất khả kháng tới đầu T11 (Enterprise AM 29/09) |
| LNG nhập khẩu Nhật bình quân (WB `lng_japan`, gần với LNG hợp đồng gắn dầu) | **16,59** (T10) | T10/2025 11,10 ⇒ **+49%** | **Phân kỳ lớn:** giá hợp đồng gắn dầu ≈ 1/2 giá giao ngay. Người mua LNG giao ngay/ngắn hạn (VN chủ yếu mua tender giao ngay từ T3/2026 — lngprime T3) chịu giá gấp đôi người có hợp đồng dài hạn |
| TTF (EUR/MWh) | TB T11 **90,2** | T11/2025 30,8 ⇒ ×2,9 | Châu Âu–châu Á tranh hàng ⇒ đỡ JKM |
| LPG nội địa TQ (sunsirs, CNY/t) | **TB5 = 7.947,5** | T11/2025 4.513 ⇒ **+76% YoY**. T1-T2/2026 ~4.400 | Đứng ~7.800-8.050 suốt 2 tuần, chưa giảm theo Brent |
| Propane Mỹ (TE, USD/gal) | TB5 1,152 (30/10-06/11); 06/11 1,10 | T11/2025 0,65 ⇒ +72% | Đã giảm 13% từ đỉnh 1,27 (30/10) |
| **Saudi CP LPG** (báo VN) | **T11/2026 = 750 USD/t** (+45 so với T10): propane 720 / butane 780 (Thanh Niên 31/10) | T11/2025 467,5 ⇒ **+60%**. T2/2026 542,5 | Giá bán lẻ VN T11: bình 12kg 609.000đ (một thương hiệu, +10.000) đến 637.500đ (miền Tây, +15.000) (SGGP, Tuổi Trẻ 01/11). Hai đợt T10+T11 cộng dồn +30.000đ/bình (Dân Trí 31/10) |
| USD/VND (snapshot) | 25.582,5 (06/11) | **−2,77% 12T** (VND tăng giá) | Làm nhẹ một phần giá nhập khẩu USD khi quy VND |

**Đọc đa proxy [UĐ]:**
1. **Đồng thuận về hướng:** cả 7 chuỗi năng lượng đều cao hơn năm trước 49% đến ×2,9. Đây là một cú sốc **chung**, không
   riêng mặt hàng nào.
2. **Phân kỳ quan trọng nhất:** Brent đã giảm ~16% từ đỉnh trong 7 phiên vì kỳ vọng thoả thuận, còn **JKM, LPG TQ và FO TQ
   gần như đứng yên**. Khí/LPG bình thường hoá **chậm hơn** dầu (file urê mục 5c, file DAP), vì (a) mùa đông, (b) công suất
   hoá lỏng Qatar bị hư hại là vật lý chứ không chỉ là rủi ro vận chuyển, (c) hàng tồn kho phải tái lập.
3. **Phân kỳ hợp đồng vs giao ngay** (16,6 vs 31,6) là biến số lớn nhất cho phần LNG của VN: ai mua giao ngay, ai chịu, ai
   được chuyển ngang chi phí (mục 3, mục 6).
4. **Về MỨC:** khí khô nội địa bán theo công thức gắn dầu (MFO/Brent) [NỀN] nên mức giá bán biên của phần nội địa ~ theo
   Brent (+59% YoY), còn phần LNG theo JKM/hợp đồng (+49% đến ×2,8). Không có số giá bán thật trong BQ — **không suy mức**.

**Bẫy dữ liệu:** (1) WB `brent` T9 = 116,8 trong khi TB daily TE T9 = 100,8 (bẫy 1 file feeds, đã ghi ở file urê) ⇒ dùng Brent TE.
(2) TE `propane` là Mont Belvieu (Mỹ), **không phải** Saudi CP — chỉ dùng cho hướng. (3) `sunsirs lpg` là LPG nội địa TQ,
**không phải** CFR Đông Nam Á.

## 2. Pipeline cầu VN

### 2.1 Khí khô cho điện (khối cầu lớn nhất) [DK]
- **Sản lượng điện toàn hệ thống 10T/2026: 297,4 tỷ kWh, +9,8% YoY; riêng T10 +14,3%** (Nhân Dân, ~đầu T11/2026).
- **Tua-bin khí 10T: 23,28 tỷ kWh = 7,8%** (than 49,7%, thuỷ điện 24,7%). H1: 8% (than 54,5%, thuỷ 21%) (Tạp chí Công
  Thương, ~T7/2026). Tính ra T7-T10 khí ~9,6 tỷ kWh ≈ 7,6% [UĐ, phép trừ] ⇒ **tỷ trọng khí không tăng** dù cầu điện tăng
  gần 10% và dù NT3&4 (LNG) đã vào. Khí là nguồn **bị điều độ theo giá** (đắt hơn than/thuỷ điện), không phải nguồn nền.
- **LNG điện đầu tiên:** NT3&4 (Đồng Nai) **vận hành thương mại 05/01/2026**; **Qc 65% trong 10 năm**; PPA ký T10/2024; hợp đồng
  cấp LNG 25 năm (VnEconomy, Báo Đấu thầu, T1/2026). Một báo nêu kế hoạch 2026 khoảng 6 tỷ kWh [DK từ báo, không kiểm].
- **Cấp khí cho điện 2026** (họp 21/08, PetroTimes 28/08/2026): khả năng cấp **~6,4 tỷ Sm³ = ~3,3 nội địa + ~3,1 LNG**; tiêu thụ
  khí nội địa ước **~2,9 tỷ Sm³**; LNG cho điện theo KH BCT ~0,9 tỷ Sm³; **kho LNG Thị Vải (1 tr t/năm) chạy < 40% công suất**;
  **bán khí nội địa những năm gần đây chỉ hơn 80% khả năng khai thác**; cước vận chuyển đường ống **nhiều năm chưa được phê
  duyệt chính thức, nhiều khu vực chạy giá tạm tính**. 2027: dự báo cung khí cho điện **vượt** cầu khí cho điện.
  ⇒ **[UĐ] Ràng buộc hiện tại ở phía CẦU-ĐIỀU-ĐỘ, không phải phía cung.** Có khí (và có công suất tái hoá) nhưng hệ thống
  không huy động hết vì giá. Đây là ADMIN_GATED (NSMO/EVN quyết huy động; Qc quyết phần sàn).
- **Cầu tiềm năng dài hạn (PDP8 điều chỉnh, QĐ 768/QĐ-TTg 15/04/2025):** 2030 điện khí nội địa **10.861-14.930 MW**, điện LNG
  **22.524 MW** (MOIT). Thực tế trượt:
  - **18 dự án điện LNG (>20 GW): chỉ 1 đúng tiến độ (Hiệp Phước, COD Q4/2028); 16/18 đã có nhà đầu tư nhưng chỉ 2 đã khởi
    công**; BNEF hạ dự báo NK LNG 2030 từ 4,9 xuống **~3 tr t** (Bloomberg qua BBW, 06/10/2026).
  - LNG Quảng Trạch II (1.612,8 MW) **khởi công 20/10/2026**, COD ~2030 (trễ ~1 năm) (Tạp chí Công Thương; file tư vấn điện).
  - Cục Điện lực/BCT (15/09 và 07/10/2026, qua file tư vấn điện): trên công suất nguồn PDP8 sau hơn 3 năm **~5% đã vận hành,
    ~9% đã khởi công, ~45% chưa có chủ trương đầu tư**; BCT dự kiến đề xuất **điều chỉnh PDP8 thêm lần nữa**; thiếu công suất
    **4.256 MW (2027) → 13.964 MW (2030)**.
  - ⇒ [UĐ] Áp lực chính trị **thúc** điện khí (thiếu điện thật), nhưng tốc độ thực hiện bị chặn bởi PPA/Qc/thu xếp vốn/giá LNG.
- **Cơ chế:** NĐ 100/2025 sửa NĐ 56/2025 (hiệu lực 08/05/2025): **chuyển ngang giá nhiên liệu vào giá điện** + **Qc dài hạn tối
  thiểu 65%** cho điện khí (LNG). BCT đang soạn dự thảo **nâng Qc lên 75% trong 15 năm**; EVN phản đối vì Qc 65% đã gây
  "over-contract" (VnEconomy, 24hMoney, Đại biểu Nhân dân — dự thảo, **chưa ban hành** tới as-of).
- **Giá điện bán lẻ:** **giảm 2% từ 01/11/2026**, còn 2.159,9 đ/kWh (QĐ 1305/QĐ-EVN 30/10/2026); NĐ 278/2026 đổi ngưỡng (tăng
  <2% không điều chỉnh, 2-<5% phải có ý kiến BCT) (Tạp chí Công Thương, Thời báo Tài chính, ~31/10/2026). EVN lãi ~52.000 tỷ năm
  2025, đã xoá lỗ luỹ kế (VCCI). ⇒ [UĐ] Rủi ro **thanh toán** của chuỗi khí–điện năm 2026-27 THẤP hơn 2023-24 (khi EVN lỗ và nợ
  đọng chuỗi khí–điện), nhưng **dư địa chuyển giá nhiên liệu cao vào giá điện bị chính trị kìm** — vừa giảm giá điện lúc dầu
  khí đang ở đỉnh là tín hiệu nhà nước ưu tiên giá điện thấp.

### 2.2 Khí cho đạm [DK]
- Khí cấp cho nhà máy đạm Đông Nam Bộ: **325 tr Sm³ (T1-T7/2026), cả năm ~590 tr Sm³**; ổn định về lượng và giá trung–dài hạn
  (PetroTimes 28/08/2026). Biên urê–khí: xem file urê (biên proxy ~219-225 USD/t, phân loại CYCLICAL 0,50).
- Khối này nhỏ (~10% khí khô) và ổn định [UĐ].

### 2.3 Khí công nghiệp (thấp áp, CNG, LNG xe bồn) [DK + UĐ]
- Mùa khô: điện được ưu tiên khí ⇒ **lo ngại thiếu khí cục bộ ở KCN Đông Nam Bộ** (KTSG 12/02/2026). Cầu tăng từ chuyển đổi
  than/dầu sang khí, khách hàng ~3/4 là DN FDI (Nhật/Hàn/Âu) (cùng nguồn; xem rò rỉ (d)).
- Rủi ro [UĐ]: cầu khí công nghiệp gắn **FDI sản xuất** (snapshot: SXCN +15,0% YoY T10, PMI 52,3, FDI YTD +13% — đều đang
  tốt) và **giá tương đối khí vs FO/than**. Khi LNG chiếm tỷ trọng lớn hơn trong nguồn cấp, giá bán công nghiệp đắt lên ⇒
  một phần cầu chuyển đổi có thể chậm lại.

### 2.4 LPG [DK + NỀN]
- VN **nhập khẩu ròng LPG** [NỀN: phần lớn cầu; nguồn trong nước từ nhà máy xử lý khí + 2 nhà máy lọc dầu]. Nguồn NK truyền
  thống: Saudi, Kuwait, Qatar/UAE (qua Hormuz) [NỀN + VOV, năm chưa xác minh]. Từ T3/2026 nhà nhập khẩu lớn **chuyển sang
  Mỹ (~45 nghìn t/chuyến), Úc (~38 nghìn t)** (Thời báo Tài chính, Tuổi Trẻ T3-T4/2026); NK LPG T6-T7/2026 ~140 nghìn t (một
  nhà nhập khẩu, Lao Động).
- Cầu LPG: dân dụng (bình 12kg) + thương mại + công nghiệp + một phần hoá dầu. Cầu dân dụng **ít co giãn** [NỀN]; công nghiệp
  co giãn theo giá thay thế. Giá bán lẻ **chuyển ngang CP hằng tháng** (thị trường, không bình ổn như xăng dầu [NỀN]).
- Cước VLGC giao ngay từng lên ~150.000 USD/ngày (T8, file vận tải dầu khí) ⇒ chi phí nhập từ Mỹ (tuyến dài) cao.

### 2.5 Cung khí nội địa — suy giảm tự nhiên và mỏ mới [DK]
- Các bể Cửu Long, Nam Côn Sơn, PM3-CAA khai thác lâu năm, sản lượng giảm từ đỉnh **10-11 tỷ m³/năm (2018-19) xuống ~8-9 tỷ
  m³** [DK thứ cấp, nguồn tổng hợp tìm kiếm — mức cần kiểm]. 2021-2025 PVN đưa **35,21 tỷ m³** khí về bờ (~7 tỷ/năm) (tóm tắt tìm kiếm).
- **Sư Tử Trắng 2B: first gas 29/06/2026** (sớm 1 ngày), ~30,7 triệu ft³/ngày ban đầu; giếng tiếp theo T9 và T11/2026; bổ sung
  khoảng **1,2 tỷ m³/năm** (VCCI/Báo Quốc tế T6-T7/2026). Đáng kể nhưng chỉ **làm chậm** đà giảm.
- **Lô B – Ô Môn: first gas lùi từ Q4/2026 (CT 05/CT-TTg 2024) sang ~T8/2027 / Q3/2027** (SGGP, Tạp chí Công Thương; năm
  2026 rải ống từ giữa T4). Đây là nguồn cung **mới lớn nhất** (~5 tỷ m³/năm khi đầy đủ [NỀN]), gắn chuỗi điện Ô Môn I/III/IV
  (Ô Môn IV vượt KH khối lượng tới T7/2026).
- **Cá Voi Xanh:** không có FID; đối tác nước ngoài không ưu tiên; mốc 2028 cũng khó (tin 2024-2025, **không có cập nhật 2026**).
- Nam Du–U Minh, Thiên Nga–Hải Âu, Khánh Mỹ–Đầm Rơi: file urê nêu "bổ sung ~11 tỷ m³ giai đoạn cuối 2026-2028" (Báo Đầu tư) —
  lượt này **không** kiểm lại được tiến độ ⇒ coi là kế hoạch, chưa phải dữ kiện.

## 3. Cấu trúc cạnh tranh / rào cản [NỀN + DK]
| Khâu | Cấu trúc | Rào cản | Ai quyết biên |
|---|---|---|---|
| Thượng nguồn (mỏ) | PSC: tập đoàn nhà nước + đối tác ngoại | Rất cao (vốn, giấy phép) | Giá miệng giếng theo hợp đồng mỏ: mỏ cũ thấp/ổn định, mỏ mới (Lô B, STT 2B) cao hơn và có thể gắn dầu [NỀN, cần DD] |
| **Trung nguồn: thu gom–xử lý–đường ống** | **Gần độc quyền tự nhiên** của một nhà vận hành nhà nước (đường ống Bạch Hổ, NCS1/NCS2, PM3-CAA; nhà máy xử lý khí) | Tuyệt đối (hạ tầng duy nhất, quy hoạch) | **Hành chính:** cước vận chuyển do BCT duyệt (**nhiều năm chạy cước tạm tính**, PetroTimes 28/08/2026) + công thức giá bán gắn MFO/Brent có sàn [NỀN]. Biên = f(Brent, sản lượng) |
| Tái hoá LNG | Thị Vải (1 tr t, nhà nước; nâng tái hoá 288 t/giờ ≈ 9,5 tr Sm³/ngày, Vietstock T4/2026); Cái Mép (tư nhân) [NỀN]; Thị Vải giai đoạn mở rộng + các kho đi kèm dự án điện LNG [NỀN] | Cao (cảng, quy hoạch) nhưng **đang mở cho tư nhân/FDI theo dự án** | Phí tái hoá + điều khoản chuyển ngang; công suất dư (<40%) ⇒ biên cố định/t cao |
| Phân phối khí công nghiệp (thấp áp/CNG/LNG xe bồn) | Vài nhà phân phối gắn hạ tầng ống khu vực + nhiều DN CNG/LNG xe bồn | Trung bình–cao (ống thấp áp khu vực là độc quyền địa phương; CNG/LNG xe bồn cạnh tranh hơn) | Thương mại, nhưng **giá đầu vào** do trung nguồn quyết |
| Điện khí (khách hàng chính) | EVN + NĐT độc lập; bán qua thị trường điện + PPA | — | NSMO điều độ theo giá; Qc; trần khung giá phát điện BCT |
| LPG nhập khẩu–bán buôn–bán lẻ | **Phân mảnh ở bán lẻ** (nhiều thương hiệu, đại lý); tập trung hơn ở **kho đầu mối/nhập khẩu lạnh** (vài DN có kho lạnh lớn) [NỀN] | Thấp ở bán lẻ (nạn chiết nạp trái phép, tranh vỏ bình); cao ở kho lạnh/cầu cảng | Thị trường: CP + premium + cước + chi phí; biên/kg tương đối ổn định, **lãi/lỗ tồn kho** khi CP đổi chiều |

**Đọc [UĐ]:**
- Phần biên **cao và bền** của ngành nằm ở trung nguồn khí nội địa (độc quyền + giá bán gắn dầu + chi phí mua mỏ cũ thấp).
  Phần đó **co lại theo thời gian** vì (i) mỏ cũ cạn, (ii) khí mới (Lô B, STT 2B) đắt hơn, (iii) LNG thay thế là hàng **chuyển
  ngang chi phí** với biên/đơn vị thấp hơn nhiều. Đây là trục STRUCTURAL của ngành — chuyển dịch "pool lợi nhuận" từ "khí
  nội địa gắn dầu" sang "phí hạ tầng + LNG pass-through".
- LPG là ngành **phân phối thương mại**: lợi nhuận phụ thuộc lượng × biên/kg; giá CP cao làm doanh thu phình nhưng không
  nhất thiết làm lãi tăng; rủi ro chính là lỗ tồn kho khi CP giảm mạnh (kịch bản thoả thuận Hormuz).

## 4. PHÂN LOẠI

### 4.1 Hai trục Bobby cho cú sốc hiện tại
- **Trục 1 (nguyên nhân gốc):** cú sốc giá năng lượng 2026 là **cú sốc cung ngoại sinh** (Hormuz bị phong toả/tranh chấp từ
  đầu T3/2026; LNG Qatar gần như đứng 6 tháng — Euronews 08/09/2026; Qatar bất khả kháng tới đầu T11). **Không** phải mất cân
  đối vĩ mô VN. Bên trong VN: CPI YoY 5,09% (+1,84pp 12T), một phần là truyền dẫn năng lượng [UĐ]; VND **tăng** giá 2,8% 12T —
  không có dấu hiệu khủng hoảng thanh toán quốc tế.
- **Trục 2 (khoanh được?):** **KHÔNG khoanh được bởi VN** (`EXTERNAL_CYCLE`). VN chỉ chỉnh được tham số: huy động khí cho
  điện, Qc, cước ống, giá điện bán lẻ, nguồn NK LPG/LNG.

### 4.2 Nhãn chi phối lợi nhuận NGÀNH (xác suất = nhãn nào CHI PHỐI; không loại trừ nhau)
**Tầm 2-4 quý (tới ~Q3/2027):**
| Nhãn | P | Lý lẽ |
|---|---|---|
| **CYCLICAL** | **0,50** | Mặt bằng giá bán (Brent +59%, CP +60%, JKM ×2,8) do cú sốc Hormuz quyết định; cả 2 nhánh (thoả thuận / kéo dài) đều đưa giá **xuống** trong 2027, chỉ khác tốc độ (file vận tải, file urê). Khí/LPG giảm chậm hơn dầu |
| **ADMIN_GATED** | **0,35** | LƯỢNG khí bán ra do điều độ + Qc quyết (khí chỉ 7,8% sản lượng điện dù cầu +9,8%; bán khí nội địa chỉ >80% khả năng; Thị Vải <40%); cước ống tạm tính chờ duyệt (rủi ro truy thu/điều chỉnh hồi tố hai chiều); giá điện vừa **giảm** 2% ⇒ trần chuyển giá; dự thảo Qc 75% |
| **STRUCTURAL** | **0,15** | Suy giảm mỏ cũ và dịch chuyển sang LNG đang diễn ra nhưng quá chậm để chi phối 2-4 quý; STT 2B (+1,2 tỷ m³) còn bù được một phần |

**Tầm 2027-2030:**
| Nhãn | P | Lý lẽ |
|---|---|---|
| **STRUCTURAL** | **0,45** | Pool lợi nhuận khí nội địa gắn dầu co lại; LNG (pass-through, biên mỏng) thành nguồn chính; Lô B (2027+) là nguồn mới đắt hơn mỏ cũ; thiếu điện 2027-2030 tạo cầu thật nhưng ở dạng LNG |
| **ADMIN_GATED** | **0,40** | Tốc độ hiện thực hoá cầu LNG-điện phụ thuộc gần như hoàn toàn vào văn bản: Qc/thời hạn, chuyển ngang giá, PPA, điều chỉnh PDP8 lần nữa; 1/18 dự án đúng hạn cho thấy nút thắt là hành chính–tài chính, không phải cầu |
| **CYCLICAL** | **0,15** | Chu kỳ dầu/LNG toàn cầu vẫn dao động biên, nhưng cung LNG toàn cầu tăng mạnh 2026-2028 (Qatar mở rộng ~T11/2026 theo tiêu đề oilandgas360; Mỹ) [NỀN] ⇒ nền giá LNG 2028+ thấp hơn nay |

**Độ tin cậy: ambiguous (~60/40)** cho tầm 2-4 quý: CYCLICAL rõ về hướng, nhưng ADMIN_GATED có thể chi phối nếu Qc/cước ống/
huy động thay đổi đột ngột. Tầm 2027-2030: clean về hướng STRUCTURAL+ADMIN, không chắc về tốc độ.

### 4.3 Vị trí chu kỳ giá [UĐ]
Dầu: **đã qua đỉnh cấp tính** (Brent T10 TB 107 → TB5 101, đáy 97 ngày 05/11), còn ở **mức cao lịch sử** và rủi ro K3.
Khí/LPG: **còn ở đỉnh** (JKM 31,6 đứng yên, CP T11 vừa tăng). Ngành khí VN ở **cuối đỉnh lợi nhuận đơn vị** về giá, với độ trễ
1-3 tháng của công thức gắn MFO bình quân [NỀN] ⇒ giá bán bình quân Q4/2026 vẫn neo ở mức T9-T10 cao.

## 5. FORECAST KHOÁ TRƯỚC (lập 2026-11-09; chấm theo quan sát cuối cùng ≤ ngày chấm)
**Proxy chấm chính:** BQ `tav2_bq.commodity_prices`, loại T7/CN, **TB 5 quan sát cuối ≤ ngày chấm**:
- `source='trading_economics'`, `cadence='daily'`, `metric_key='brent'` — **gốc 100,99** (02-06/11).
- `source='trading_economics'`, `cadence='daily'`, `metric_key='liquefied_natural_gas_japan_korea'` — **gốc 31,63** (02-06/11).
- `source='sunsirs'`, `cadence='daily'`, `metric_key='lpg'` — **gốc 7.947,5** (02-06/11).
**Proxy phụ (báo VN):** Saudi CP hằng tháng (gốc **T11/2026 = 750 USD/t**).

Kịch bản (đồng bộ file urê 04/11, chỉnh nhẹ theo Brent rơi tiếp 04-06/11) [UĐ]:
- **K1 — Hormuz còn tranh chấp/hạn chế tới hết Q1/2027 (p ≈ 0,47):** Brent 90-112; JKM 26-36 qua đông; CP 680-800.
- **K2 — thoả thuận thật trước giữa T1/2027 (p ≈ 0,38):** Brent 72-88; JKM rơi chậm hơn (20-28 tới Q1); CP 560-680.
- **K3 — leo thang (p ≈ 0,15):** Brent 115-140; JKM > 35; CP > 820.

| ID | Mốc chấm | Chuỗi (gốc) | Dự báo |
|---|---|---|---|
| F1 | **2026-11-30** (+21 ngày) | TB5 Brent TE (100,99) | Trung vị **97**, 80% **84-112**. **P(<100,99) = 0,60**; P(<90) = 0,25; P(>110) = 0,12 |
| F2 | **2027-01-08** (+60 ngày) | TB5 Brent TE | Trung vị **92**, 80% **74-115**. **P(<100,99) = 0,64**; P(<85) = 0,35; P(>115) = 0,10 |
| F3 | **2027-03-09** (+120 ngày) | TB5 Brent TE | Trung vị **88**, 80% **70-118**. **P(<100,99) = 0,67**; P(<80) = 0,33; P(>115) = 0,11 |
| F4 | 2026-11-30 | TB5 JKM-proxy TE (31,63) | Trung vị **31,0**, 80% **26-35**. **P(<31,63) = 0,57** |
| F5 | 2027-01-08 | TB5 JKM-proxy TE | Trung vị **29**, 80% **20-37**. **P(<31,63) = 0,62**; P(<25) = 0,28 |
| F6 | 2027-03-09 | TB5 JKM-proxy TE | Trung vị **23**, 80% **15-34**. **P(<31,63) = 0,78**; P(<20) = 0,33 |
| F7 | 2026-11-30 | TB5 sunsirs LPG (7.947,5) | Trung vị **7.850**, 80% **7.300-8.300**. **P(<7.947,5) = 0,56** |
| F8 | 2027-01-08 | TB5 sunsirs LPG | Trung vị **7.550**, 80% **6.500-8.400**. **P(<7.947,5) = 0,63** |
| F9 | 2027-03-09 | TB5 sunsirs LPG | Trung vị **6.900**, 80% **5.600-8.300**. **P(<7.947,5) = 0,73** |
| F10 | công bố ~cuối T11 | Saudi CP **T12/2026** so với 750 | **P(CP T12 < 750) = 0,50**; P(≤ 700) = 0,22 (mùa đông đỡ CP; Brent giảm kéo xuống — hai lực ngang nhau) |
| F11 | công bố ~cuối T2/2027 | Saudi CP **T3/2027** so với 750 | **P(< 750) = 0,70**; P(≤ 650) = 0,40 |
| **Tỷ lệ phân kỳ** | 2027-01-08 | (TB5 JKM / TB5 Brent) so với gốc 31,63/100,99 = **0,313** | **P(tỷ lệ > 0,313) = 0,55** — kiểm giả thuyết "khí bình thường hoá chậm hơn dầu" |

**Câu sự kiện (chấm bằng văn bản/tin chính thức công bố đầu tiên ≤ ngày chấm):**
| ID | Mốc | Sự kiện | P |
|---|---|---|---|
| E1 | 2027-03-31 | Văn bản **nâng Qc điện khí/LNG lên ≥ 70%** (sửa NĐ 56/100) được **ban hành** | **0,40** |
| E2 | 2027-03-31 | EVN **tăng** giá bán lẻ điện bình quân (bất kỳ mức nào) | **0,20** (vừa giảm 2% ngày 01/11; NĐ 278 nâng ngưỡng thủ tục) |
| E3 | 2027-02-28 | Tỷ trọng **tua-bin khí cả năm 2026** (EVN/NSMO báo cáo năm) nằm trong **7,0-8,5%** | **0,75**; P(> 8,0%) = 0,30 |
| E4 | 2027-09-30 | **Lô B: first gas** được công bố | **0,45**; (tới 2027-12-31: 0,70) |
| E5 | 2027-03-31 | Thoả thuận Hormuz chính thức + tàu LNG Qatar đi qua eo ổn định 4 tuần liên tiếp (theo Bloomberg/Lloyd's/Kpler qua báo) | **0,35** |
| E6 | 2027-06-30 | Thêm ≥ 1 dự án điện LNG mới (ngoài NT3&4, QT II) **khởi công** chính thức | **0,55** |

Cách chấm: Mike/Bobby truy vấn BQ (ghi rõ `source`) tại 3 mốc, tra tin cho F10-F11/E1-E6, ghi Brier ngay dưới bảng này.
Đây là thước đo **hướng giá đầu vào/đầu ra của ngành**, không phải lợi nhuận của DN nào.

## 6. Chỉ báo dẫn dắt (theo dõi)
| # | Chỉ báo (tần suất) | Nguồn | Tín hiệu lên ⇔ xuống |
|---|---|---|---|
| 1 | Hormuz: lượt tàu LNG/LPG qua eo, bất khả kháng Qatar, tiến độ trung gian (tuần) | Bloomberg/Lloyd's/Euronews/Kpler qua báo | Thoả thuận + LNG qua eo ổn định (giá xuống) ⇔ tấn công hạ tầng (K3) |
| 2 | Brent / FO TQ (proxy MFO) / JKM / LNG hợp đồng WB (ngày/tháng) | BQ (`brent`, `fuel_oil`, `liquefied_natural_gas_japan_korea`, `lng_japan`) | Theo dõi **phân kỳ JKM−hợp đồng** và **JKM/Brent** |
| 3 | Saudi CP + giá bình 12kg (tháng, cuối tháng) | Báo VN (Thanh Niên/Tuổi Trẻ/Dân Trí) | CP ≥ 800 ⇔ CP ≤ 650 (lãi/lỗ tồn kho LPG) |
| 4 | Huy động tua-bin khí, tỷ trọng % sản lượng (tháng) | EVN/NSMO bản tin | > 9% (khí được huy động nhiều hơn — mùa khô 2027) ⇔ < 7% |
| 5 | Văn bản: Qc 75%, cước ống chính thức, khung giá phát điện khí 2027, điều chỉnh PDP8 lần 2, giá điện bán lẻ (sự kiện) | Chinhphu.vn, MOIT, EVN | Ban hành Qc 75% + cước chính thức ⇔ cắt mục tiêu LNG trong PDP8 sửa |
| 6 | Mỏ: giếng STT 2B (ST-10P, ST-4PST), rải ống Lô B, Ô Môn IV (tháng) | PVN/PetroTimes | Đúng hạn ⇔ lùi thêm |
| 7 | Snapshot vĩ mô: SXCN, PMI, FDI (tháng) | `macro_indicator` | Cầu khí công nghiệp; PMI < 50 hai tháng liền là cờ |

## 7. DD cần kiểm gì (BCTC/hồ sơ một DN khí — trung nguồn, phân phối khí, hay LPG — phải chứng minh được)
1. **Cơ cấu sản lượng theo khách hàng** (điện / đạm / công nghiệp thấp áp / CNG / LNG xe bồn / LPG) và **theo nguồn** (khí nội
   địa từng mỏ vs LNG). Xu hướng 8-12 quý. Lượng bán so với khả năng cấp (có bị điều độ cắt không).
2. **Công thức giá bán** từng nhóm khách: % MFO/Brent, **sàn**, trần, độ trễ bình quân, phí vận chuyển; với LNG: chuyển ngang
   bao nhiêu % chi phí, phí tái hoá. **Ai chịu chênh lệch giao ngay vs hợp đồng** (31,6 vs 16,6 USD/MMBtu).
3. **Giá mua miệng giếng** theo mỏ (mỏ cũ cố định/thấp vs STT 2B/Lô B gắn dầu/cao) ⇒ biên đơn vị tách theo mỏ; lịch hết hợp đồng
   mua khí mỏ cũ; **đường cong suy giảm** từng mỏ.
4. **Cước vận chuyển đường ống:** chính thức hay tạm tính; khoản nào đang ghi nhận theo cước tạm tính; **rủi ro truy thu/hoàn
   trả hồi tố** khi BCT duyệt chính thức; dự phòng.
5. **Take-or-pay hai đầu:** cam kết mua với chủ mỏ / nhà cung cấp LNG vs cam kết bao tiêu của khách (Qc điện, hợp đồng đạm).
   Khoản phạt/khí trả trước nếu điều độ không lấy đủ.
6. **Phải thu chuỗi khí–điện:** tuổi nợ từ nhà máy điện/EVN, lãi chậm trả, dự phòng; so với năm 2023-24 (nợ đọng chuỗi).
7. **LNG:** tồn kho LNG tại kho và giá vốn; tỷ trọng mua giao ngay vs hợp đồng; nguồn gốc lô hàng (Trung Đông vs khác); công
   suất sử dụng kho tái hoá; khấu hao kho trên sản lượng thấp.
8. **LPG:** số ngày tồn kho, **lãi/lỗ tồn kho** theo biến động CP (tách khỏi biên thương mại); biên/kg theo kênh (bán buôn,
   bán lẻ, công nghiệp); tỷ trọng nguồn Trung Đông vs Mỹ/Úc và chi phí cước; nợ phải trả tiền cược vỏ bình; thị phần.
9. **Khoản một lần:** thu hồi chênh lệch tỷ giá/giá nhiên liệu giai đoạn trước, hoàn nhập dự phòng, lãi bán tài sản — **tách
   khỏi** lợi nhuận lặp lại.
10. **Capex và dự án:** đường ống Lô B–Ô Môn, mở rộng kho LNG, ống thấp áp mới; nguồn vốn; IRR công bố giả định cước/giá
    bao nhiêu; rủi ro dự án trễ (Lô B đã lùi 3 quý).
11. **Tỷ giá:** mua/bán gắn USD nhưng thanh toán VND; vị thế ngoại tệ ròng; nợ vay USD.
12. **Lãi tiền gửi trong LNTT** (nếu DN dư tiền lớn): phần này gắn lãi suất huy động, không gắn ngành.
13. **Chính sách:** thuế (VAT, thuế BVMT LPG [NỀN]), khung giá, chỉ đạo ưu tiên khí cho điện mùa khô (cắt khí công nghiệp?),
    chính sách chuyển ngang giá nhiên liệu vào giá điện có áp dụng hồi tố hay không.

## 8. Điều gì làm tôi sai
1. **Thoả thuận Hormuz nhanh và hàng Qatar xả mạnh** ⇒ JKM/CP rơi nhanh như Brent (F4-F11 lệch về phía "giảm nhiều hơn").
   Cờ: tàu LNG qua eo ≥ 2/ngày trong 2 tuần.
2. **K3 leo thang** (đánh vào Ras Laffan / hạ tầng Gulf) ⇒ toàn bộ forecast giá lệch lên.
3. **Điều độ đảo chiều:** mùa khô 2027 thuỷ văn kém + thiếu điện ⇒ khí được huy động mạnh bất chấp giá (tỷ trọng > 9%); khi đó
   ADMIN_GATED đổi dấu thành **hỗ trợ lượng**.
4. **Công thức giá khí sai:** nếu giá bán khí nội địa có **trần** hoặc ít nhạy Brent hơn tôi nghĩ, biên trung nguồn nhạy dầu
   **thấp** hơn; nếu giá mua mỏ cũ cũng gắn dầu, biên **không** phình theo Brent. Đây là biến DD số 1.
5. **Mức suy giảm mỏ** (10-11 → 8-9 tỷ m³) là số thứ cấp từ tóm tắt tìm kiếm — có thể lệch phạm vi (khai thác vs đưa về bờ vs bán).
6. **PDP8 sửa lần nữa cắt mạnh LNG** (như bản thẩm định 02/2025 từng hạ LNG 2030 còn 8.824 MW — Mekong ASEAN 20/02/2025, sau đó
   QĐ 768 vẫn giữ 22.524 MW) ⇒ STRUCTURAL tầm 2027-2030 thiên về "cầu LNG thấp hơn", không phải "dịch chuyển sang LNG".

**Đây không phải khuyến nghị mua/bán bất kỳ mã nào.** Không có ngưỡng escalate nào được đề xuất từ bản đọc này.

## Nguồn (ngày công bố)
- BQ `tav2_bq.commodity_prices` (truy vấn 09/11/2026): TE daily `brent`, `liquefied_natural_gas_japan_korea`, `eu_natural_gas`,
  `propane`; sunsirs daily `lpg`, `fuel_oil`; WB monthly `lng_japan`, `brent`, `natural_gas`.
- Snapshot vĩ mô `agents/Taylor/research/dd_lagcand_20261109/macro_snapshot_20261109.md` (CPI, SXCN, PMI, FDI, USD/VND).
- PetroTimes, "PETROVIETNAM chủ động nguồn khí cho Điện – Đạm khu vực Đông Nam Bộ", 28/08/2026: https://petrovietnam.petrotimes.vn/petrovietnam-chu-dong-nguon-khi-cho-dien-dam-khu-vuc-dong-nam-bo-745039.html
- Nhân Dân, EVN 10 tháng 2026 (sản lượng, cơ cấu huy động), ~đầu T11/2026: https://nhandan.vn/post-999892.html ; Tạp chí Công Thương H1/2026: https://tapchicongthuong.vn/evn-dam-bao-cung-ung-dien-an-toan--on-dinh-trong-6-thang-dau-nam-2026-532173.htm
- VnEconomy, NT3&4 vận hành thương mại, T1/2026: https://vneconomy.vn/nha-may-dien-lng-dau-tien-van-hanh-thuong-mai-mo-duong-cho-chuyen-dich-nang-luong.htm
- VnEconomy, đề xuất nâng bao tiêu LNG lên 75%: https://vneconomy.vn/de-xuat-nang-bao-tieu-dien-khi-lng-len-75-tien-do-ky-ket-hop-dong-mua-ban-dien-duoc-day-nhanh.htm ; Tạp chí Công Thương NĐ 100/2025: https://tapchicongthuong.vn/chinh-phu-ban-hanh-quy-dinh-moi-ve-co-che-phat-trien-cac-du-an-dien-khi-140268.htm
- BBW (Bloomberg), "Kế hoạch mở rộng điện khí LNG chậm tiến độ nghiêm trọng", 06/10/2026: https://bbw.vn/ke-hoach-mo-rong-dien-khi-lng-cua-viet-nam-cham-tien-do-nghiem-trong-60769.html
- Tạp chí Công Thương, khởi công LNG Quảng Trạch II (20/10/2026): https://tapchicongthuong.vn/khoi-cong-nha-may-nhiet-dien-lng-quang-trach-ii-559538.htm
- MOIT, PDP8 điều chỉnh QĐ 768/QĐ-TTg (15/04/2025): https://moit.gov.vn/tin-tuc/phat-trien-nang-luong/chinh-thuc-phe-duyet-quy-hoach-dien-viii-dieu-chinh.html ; Mekong ASEAN 20/02/2025 (bản thẩm định): https://mekongasean.vn/cong-suat-dien-hat-nhan-se-dat-khoang-6400-mw-vao-giai-doan-2030-2035-38459.html
- Tạp chí Công Thương, giá bán lẻ điện giảm 2% từ 01/11/2026: https://tapchicongthuong.vn/gia-ban-le-dien-binh-quan-giam-2--tu-ngay-1-11-2026-562569.htm ; NĐ 278/2026: https://tapchicongthuong.vn/chinh-phu-sua-quy-dinh-ve-dieu-chinh-gia-ban-le-dien-binh-quan-532790.htm ; VCCI (EVN lãi 2025): https://www.vcci.com.vn/tin-tuc/khi-evn-lanh-manh-tai-chinh-dn-phat-dien-toan-thi-truong-huong-loi
- SGGP, Lô B first gas T8/2027: https://www.sggp.org.vn/chuoi-du-an-khi-lo-b-du-kien-co-dong-khi-dau-tien-vao-thang-8-2027-post831467.html ; Tạp chí Công Thương Q3/2027: https://tapchicongthuong.vn/don-dong-khi-lo-b-dau-tien-vao-du-an-nhiet-dien-o-mon-i-trong-quy-iii-2027-391428.htm
- VCCI / Báo Quốc tế, Sư Tử Trắng 2B first gas 29/06/2026: https://vcci.com.vn/tin-tuc/chinh-thuc-don-nhan-dong-khi-dau-tien-vuot-xa-du-kien-tu-mo-su-tu-trang-giai-doan-2b
- Báo Đấu thầu, Cá Voi Xanh khó về đích 2028 (cũ): https://baodauthau.vn/du-an-mo-khi-ca-voi-xanh-kho-ve-dich-nam-2028-post161512.html
- Thanh Niên, giá gas T11 (CP 750), 31/10/2026: https://thanhnien.vn/gia-gas-thang-11-tang-manh-binh-50-kg-tang-hon-42000-dong-185261031175418983.htm ; Tuổi Trẻ 01/11/2026: https://tuoitre.vn/gia-gas-thang-11-tiep-da-tang-100261101090211908.htm ; SGGP: https://dttc.sggp.org.vn/gia-gas-tang-10000-dong-mot-binh-12kg-post138948.html ; Dân Trí 31/10/2026: https://dantri.com.vn/kinh-doanh/gia-gas-thang-11-tang-tiep-len-hon-600000-dongbinh-12kg-20261031202841336.htm
- LPG đa dạng nguồn (Mỹ/Úc), T3-T4/2026: https://thoibaotaichinhvietnam.vn/petrovietnampv-gas-thong-nhat-phuong-an-dam-bao-nguon-cung-lpg-voi-khach-hang-den-thang-52026-truoc-mat-nhap-ngay-gan-38000-tan-lpg-tu-australia-194182.html ; https://news.tuoitre.vn/vietnam-imports-more-lpg-lng-from-us-australia-as-gas-prices-hold-high-103260430093534994.htm ; Lao Động: https://news.laodong.vn/thong-tin-doanh-nghiep/pv-gas-nhap-khau-gan-120000-tan-lng-lpg-giua-cao-diem-nhu-cau-nang-luong-1720551.ldo
- LNG nhập khẩu 2026 / Thị Vải: Tuổi Trẻ (lô đầu 10/03/2026): https://tuoitre.vn/plo/chuyen-tau-lng-nhap-khau-dau-tien-trong-nam-2026-cua-pv-gas-cap-cang-kho-lng-thi-vai-109899007.htm ; Vietstock T4/2026 (tái hoá 288 t/h): https://vietstock.vn/2026/04/pv-gas-nhap-khau-bo-sung-gan-60000-tan-lng-chu-dong-dam-bao-nguon-khi-cho-mua-kho-34-1426486.htm ; CafeF T6/2026: https://cafef.vn/tau-lng-khong-lo-tu-canada-cap-cang-thi-vai-dua-73000-tan-nhien-lieu-ve-viet-nam-188260611230202497.chn
- Hormuz/LNG Qatar: Euronews 08/09/2026: https://www.euronews.com/business/2026/09/08/six-months-into-hormuz-blockade-qatar-and-uae-test-ways-to-keep-lng-moving ; Enterprise AM 29/09/2026: https://enterpriseam.com/logistics/2026/09/29/more-qatari-lng-is-getting-through-hormuz-but-qatarenergy-isnt-ready-to-promise-deliveries/ ; EnergyConnects T9/2026: https://www.energyconnects.com/news/gas-lng/2026/september/qatar-boosts-lng-traffic-via-hormuz-as-global-shortage-bites/ ; AXS Marine T3/2026: https://public.axsmarine.com/blog/lng-shock-from-supply-disruption-to-system-strain
- KTSG, lo ngại thiếu khí sản xuất ĐNB, 12/02/2026 (rò rỉ (d), chỉ dùng định tính): https://tuoitre.vn/saigontimes/lo-ngai-thieu-khi-cho-san-xuat-pv-gas-d-khang-dinh-bao-dam-nguon-cung/
