# PVT — ADDENDUM bước 3c (5F + moat trong mô hình) — 07–08/11/2026, job `Taylor_20261107_172013` (resume của `Taylor_20261107_131640`)

> Bổ sung cho `REPORT_r2.md` (05/11). KHÔNG sửa REPORT/SUMMARY cũ. Số: `calc_5f/pvt_5f.py` → `calc_5f/pvt_5f_out.txt` (import `calc/model.py`,
> `calc/model_r2.py`, `_common_014127/common_r2.py` — không sửa); bằng chứng định lượng: `calc_5f/peer_5f_bq.csv` (BQ `ticker_financial`, Q4 2015–25 + Q3/26).
> Chưa qua fundamental-skeptic. 5F dùng tri thức LLM ⇒ non-point-in-time, chỉ cho DD sống, KHÔNG đưa vào backtest.

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng hay làm mới:** LÀM MỚI — `data/moat_tags.csv` chưa có dòng PVT; `kb/projects/pvt-dd-20261029.md` + DD 29/10 không có audit 5F.
**Loại hình DN:** vận tải biển dầu thô/sản phẩm/LPG + FSO/FPSO, chu kỳ cước, thâm dụng vốn; công ty con PVN (51%).

| Lực | Đánh giá (bằng chứng) |
|---|---|
| Đối thủ hiện hữu | Cạnh tranh cước theo thị trường thế giới (BDTI/BCTI), sản phẩm đồng nhất. PVT lớn nhất nội địa, nhưng ROIC5Y peer nội địa chỉ 4,2–8,8% (GSP 8,2 · PJT 7,7 · PVP 8,8 · VIP 4,2) ⇒ ngành không có lợi nhuận siêu ngạch. |
| Gia nhập mới | Rào vốn (tàu) + quy định cabotage nội địa (dành vận tải nội địa cho tàu treo cờ VN — **cần kiểm chứng** điều khoản/ngoại lệ) — rào có thật nhưng mỏng ở tuyến quốc tế. |
| Quyền lực người mua | Bên PVN 22,4% DT 9T/26 (Q3 31,7%), phải thu đơn vị PVN 1.144,7 tỷ (+130%) [REPORT_r2 §5] ⇒ khách tập trung, mua theo giá thị trường/thương lượng; captive cho **khối lượng**, không cho **giá**. |
| Quyền lực nhà cung cấp | Giá tàu cũ/đóng mới + nhiên liệu theo thế giới; capex 2026 ≤3.445 tỷ ở vùng đỉnh giá tàu cũ (Bobby mục 7). Không tự chủ đầu vào. |
| Sản phẩm thay thế | Đường ống/xe bồn cho tuyến ngắn; dài hạn chuyển dịch năng lượng giảm khối lượng dầu — tốc độ: **cần kiểm chứng**. |
| **Lực thứ 6 (đồng hồ cắt hào)** | IMO CII/EEXI + mục tiêu 2030/2050 trên đội tàu già ~17,7 năm (Bobby) ⇒ capex thay thế bắt buộc; hợp đồng bên PVN thương lượng lại được (không độc quyền pháp định — **cần kiểm chứng**). |

**Ba điều kiện bền (cả hai phía bằng chứng, Ke = r = 13,5%):**
| | PVT | Nhận xét |
|---|---|---|
| (i) ROIC (BQ, Q3/26) | ROIC5Y **10,0%** · ROIC_Min5Y **9,4%** · ROIC10Y **9,05%** · ROIC_Min10Y **2,5%** | Mọi cửa sổ < Ke. Phía thuận: ROIC5Y cao nhất nhóm peer nội địa (4,2–8,8%). ❌ không siêu ngạch |
| ROE riêng (không thay ROIC) | trung vị ROE_Trailing Q4 2015–25 **13,15%**, ROE_Min5Y 12,4%, TTM Q3/26 15,77% (đỉnh cước) | ≈ Ke, kể cả lãi tiền gửi; bỏ lãi gửi 10,97% (REPORT_r2 §4) |
| GPM (Q4 = cả năm, TTM) | trung vị 2015–25 **15%**, Q3/26 TTM 16% | Peer: GSP 8 · PJT 11 · PVP 14,5 · VIP 21 · VTO 17 ⇒ quanh trung vị, không vượt trội |
| (ii) Cơ chế gọi tên | captive PVN + quy mô nội địa + cabotage (cần kiểm chứng) | có, nhưng cho khối lượng chứ không cho biên |
| (iii) Đồng hồ | IMO/đội tàu già; PVN không bắt buộc | có |

**Kết luận:** **moat_tier = NONE**, moat_type = NONE (lợi thế TƯƠNG ĐỐI captive PVN/quy mô — không ra lợi nhuận > Ke). **moat_durable = false.**
**Rủi ro số 1:** cước tanker về đáy chu kỳ đúng lúc capex thay tàu bắt buộc (IMO, đội tàu ~17,7 năm) mua ở đỉnh giá tàu ⇒ ROIC lùi về Min10Y 2,5%.

## 2. Moat trong mô hình
- Mô hình r2: TV = ROE_mid × VCSH × (1+g)(1−g/RONIC)/(r−g), **RONIC = ROE** riêng PVT, ROE_mid = trung vị **riêng PVT 13,15%** giữ vĩnh viễn. Năm 1 / chiết khấu: Q4 ^0,125, LN 2027 ^0,75, TV ^1,25 — calc_5f chép nguyên (H: nhất quán).
- **Không thưởng moat** (NONE): không có tham số moat cộng thêm. Nhưng KIỂM luật C: mô hình đang giữ ROE **riêng** (13,15%) trên TB chu kỳ ngành (trung vị peer 11,91%, trung bình 10,77%) tới vô hạn ⇒ **KHÔNG ghi "nhất quán"**.
- Mô hình hiện hành KHÔNG ngầm WIDE: ROE_mid < Ke nên RONIC=ROE đang **phạt** tăng trưởng (giá trị âm của tái đầu tư), không thưởng; TTM 15,77% không vào terminal.
- **Bản CHẶT-3C** (headline, *quy ước chờ Mike/user duyệt*): ROE giữa chu kỳ → TB chu kỳ NGÀNH (hệ số lưới 0,8–1,2 × kịch bản giữ nguyên), RONIC = Ke **đối xứng** mọi nhánh (gồm nhánh ROE < Ke ⇒ nâng). Trục r, mua tàu, CK thanh khoản giữ nguyên r2.
- Peer (F): GSP (LPG, nhóm PV), PJT (vận tải xăng dầu Petrolimex — một phần đường thuỷ nội địa), PVP (tanker, **công ty con PVT** ⇒ chạy thêm bản loại PVP), VIP (tanker nhỏ) — đều NỘI ĐỊA, không phải đối thủ quốc tế đúng nghĩa (peer quốc tế: cần kiểm chứng, không có trong BQ). Loại: VTO (thiếu ROE_Trailing), VOS (hàng rời), HAH (container) — khác phân khúc.

## 3. Độ nhạy (sau CK 5 tỷ 0,67%; giá 04/11 21.000; nhãn 40 triệu trùng mọi dòng)
| Bản | ROE neo | RONIC | Tâm | P10 / P50 / P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| WIDE (giả định moat sai chiều lên) | TTM 15,77% vĩnh viễn | ROE | 21.782 | 15.643 / 21.667 / 28.048 | 46,2% | TRONG |
| **Hiện hành r2** | riêng 13,15% | ROE | **17.675** | 12.533 / 17.425 / 23.135 | 78,3% | TRONG |
| Chỉ RONIC=Ke | riêng 13,15% | Ke | 17.977 | 13.852 / 17.719 / 22.298 | 78,3% | TRONG |
| Chỉ ROE→trung vị peer | 11,91% | ROE | 15.711 | 10.946 / 15.475 / 20.787 | 91,3% | TRÊN (P90 −1,0%: ranh giới) |
| **CHẶT-3C trung vị peer** | 11,91% | Ke | **16.492** | 12.636 / 16.299 / 20.401 | 94,0% | **TRÊN** (P90 −2,9%) |
| CHẶT-3C trung bình peer | 10,77% | Ke | 15.132 | 11.523 / 15.002 / 18.740 | 98,0% | TRÊN |
| CHẶT-3C trung vị peer ex-PVP | 12,19% | Ke | 16.829 | 12.912 / 16.593 / 20.865 | 90,8% | TRÊN — **ranh giới** (P90 −0,6%) |
| CHẶT-3C trung bình peer ex-PVP | 10,48% | Ke | 14.791 | 11.244 / 14.664 / 18.324 | 99,5% | TRÊN |
| NONE thuần (ROE = Ke) | 13,5% | Ke | 18.381 | 13.721 / 17.926 / 22.469 | 79,5% | TRONG |

Tách phần chênh (trung vị peer): RONIC=Ke **+302** (+1,7%); neo ROE→ngành **−1.964**; gộp **−1.183 (−6,7%)**. Khoảng theo cách chọn peer: tâm **14.791–16.829**.

## 4. Thay đổi so với báo cáo hiện hành
Theo đúng luật 3c (NONE ⇒ RONIC=Ke, ROE về TB chu kỳ ngành), tâm **17.675 → 16.492** (−6,7%; khoảng 14.791–16.829 theo peer), P10/P50/P90 12.533/17.425/23.135 → **12.636/16.299/20.401**, nhãn **TRONG → TRÊN vùng** — nhưng mong manh: P90 chỉ cách giá −2,9% (trung vị) và −0,6% (ex-PVP, ranh giới); cùng chiều với hai bản song song TRÊN vùng sẵn có của REPORT_r2 (neo KH 5 năm 11.456, ROE bỏ lãi gửi 14.219). Toàn bộ chênh đến từ neo ROE riêng → ngành; RONIC=Ke tự nó **nâng** giá trị vì ROE < Ke. **Quy ước chờ Mike/user duyệt** — không tự ghi dd_price_zones/SUMMARY. Pháp lý (thay TGĐ, phải thu PVN, kiểm toán chưa có) giữ WARNING, không dùng ép ROE; không đếm hai lần.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi)
```
PVT,NONE,NONE,L,"Tanker freight-cycle commodity: ROIC5Y 10.0%/Min5Y 9.4%/Min10Y 2.5% all < Ke 13.5% despite best-in-domestic-peers; PVN captive (22.4% rev 9T/26) gives volume not price; IMO CII/EEXI on ~17.7y fleet forces replacement capex near ship-price peak",2026-11-07,5f_dd_taylor,N
```
entry = L: ngành tanker chu kỳ, hàng hoá đồng nhất, thâm dụng vốn (moat_5f.py:33 = hấp dẫn cấu trúc NGÀNH). moat_upgrade = N.
