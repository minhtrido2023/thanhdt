# Đếm ngành trong funnel 8L — 06/10 → 23/10/2026 (14 phiên, mọi làn A/B/C)

**Đo bằng**: `python3 count_sectors.py` (thư mục này). Nguồn mã: `mike/logs/discretionary_funnel.log`
(dòng `• XXX · làn …` + dòng `LOẠI XXX (làn …)`); nguồn ngành: `ICB_Code` + `route` trong
`data/rating_8l_daily/rating_8l_<asof>.csv` CÙNG ngày asof. 899 lượt mã-ngày, 0 mã không map được.
Chi tiết từng dòng: `funnel_rows_20261006_20261023.csv`. Tên nhóm ICB là nhãn tôi gán theo mã ICB chuẩn
(vd 8355 = Ngân hàng, 8633 = BĐS phát triển, 1357 = Hoá chất đặc biệt, 1353 = Hoá chất hàng hoá).

| Nhóm ICB | Lượt mã-ngày | Số mã | Làn A | Làn B | Làn C | Mã |
|---|---|---|---|---|---|---|
| **Ngân hàng (8355)** | **121** | 10 | 0 | 42 | 79 | ABB, CTG, HDB, MBB, NAB, SHB, TPB, VBB, VCB, VPB |
| **BĐS (8633)** | **119** | 12 | 20 | 42 | 57 | DTD, IDC, KOS, LHG, NTC, NTL, OGC, SIP, SZB, SZL, VHM, VRE |
| **Hoá chất đặc biệt (1357)** | **98** | 7 | 0 | 28 | 70 | CSV, DCM, DDV, DGC, DHB, DPM, PAT |
| Điện (7535) | 65 | 4 | 7 | 42 | 16 | HDG, NT2, QTP, SJD |
| Vật liệu XD (2353) | 61 | 5 | 0 | 0 | 61 | KSB, NNC, NTP, SCL, VLB |
| Hoá chất hàng hoá (1353) | 56 | 3 | 0 | 28 | 28 | DRI, HII, PHR |
| Vận tải/cảng (2777) | 47 | 5 | 3 | 0 | 44 | DVP, DXP, GMD, NCT, VSC |
| Bảo hiểm phi nhân thọ | 42 | 4 | 0 | 42 | 0 | ABI, BIC, MIG, PVI |
| Xây dựng hạ tầng (2357) | 35 | 2 | 7 | 14 | 14 | DC4, LCG |
| (17 nhóm còn lại) | ≤29 mỗi nhóm | | | | | |

**Bẫy đếm phải biết**: làn B có HẠN NGẠCH CỐ ĐỊNH 3 mã × 6 route (BANK/COMPOUNDER/CYCLICAL/INSURANCE/
POWER/REALESTATE) ⇒ 14 phiên × 3 = 42 lượt cho mỗi route bất kể ngành nóng hay nguội. Bỏ làn B đi:
Ngân hàng 79 · BĐS 77 · Hoá chất (1357+1353) 98 · VLXD 61 · Vận tải 47 · Điện 23.
**Top-3 KHÔNG đổi** dù đếm có hay không có làn B, dù gộp hay tách 1357/1353 ⇒ chọn:
**Ngân hàng · BĐS (dân dụng + KCN) · Hoá chất–phân bón**. Điện (65, phần lớn là hạn ngạch làn B) đứng thứ 4.

Khung đã có trong `kb/projects/`: chỉ `vn-realestate-structural-risk-20260826.md` (rủi ro cấu trúc BĐS/tín dụng
cấp VĨ MÔ, Bobby) + `vn_realestate_monthly_checks/`. Không có khung ngân hàng hay hoá chất cấp ngành.
Khung BĐS ở đây THAM CHIẾU tài liệu đó, không lặp lại bảng chỉ báo vĩ mô của nó.
