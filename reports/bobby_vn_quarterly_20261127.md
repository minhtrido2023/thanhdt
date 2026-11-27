# Review quý macro, 27/11/2026 (Bobby, chỉ đọc)

**Kết luận:** chưa có ngưỡng nào buộc escalate cho user ngay. Có ba thứ nên báo user ở mức trung bình (mục A5): lượng bán Hà Nội đã qua ngưỡng 1 quý, HDB xấu đi mạnh, và cron kiểm tra tháng 11 chết im lặng. Phân loại giữ nguyên, tôi chỉ nâng xác suất kịch bản đóng băng cục bộ.

Tôi không sửa file nào, không ghi bus, không cập nhật registry. Không dùng forward-return. Phần FTSE không dùng giá hay lợi suất sau 21/09, và tôi không mở `agents/Taylor/research/ftse_recheck_20261127/`.

## PHẦN A — Chỉ báo dẫn, rủi ro cấu trúc BĐS

### A1. Bảng chỉ báo dẫn

| Chỉ báo (ngưỡng cảnh báo / nguy hiểm) | Mốc trước | Số mới nhất (kỳ, nguồn) | Chạm? |
|---|---|---|---|
| Tín dụng BĐS / tổng (>28% / >30%) | 25,5% (30/6) | 25,39% (31/8, NHNN qua báo). Số 30/9: không có | Không |
| Vi phạm TPDN 12 tháng (>2% / >5%) | 0,24% (T8) | Tỷ lệ mới hơn T8: không có. 10 tháng: 8 lô chậm trả, 5.182 tỷ ([24hmoney](https://24hmoney.vn/news/8-lo-trai-phieu-cham-tra-trong-nam-2026-mot-doanh-nghiep-om-khoan-2-210-ty-dong-c4a2857669.html)) | Không |
| Giao dịch BĐS cả nước (−50% YoY 2 quý liền) | Q3 = 92% Q2 | Q3: **−32,7% YoY** ([VietNamNet 17/11](https://vietnamnet.vn/en/vietnam-to-propose-property-market-measures-as-transactions-plunge-32-7-2574618.html)). Tôi tự kiểm: 92.004 vs 136.681 ([Báo Đấu thầu](https://baodauthau.vn/ton-kho-bat-dong-san-tang-quy-iii2026-ghi-nhan-khoang-92004-giao-dich-thanh-cong-post209850.html), [Saigon Times](https://thesaigontimes.vn/giao-dich-chung-cu-nha-rieng-le-giam-trong-qui-3/)) | Không |
| Lượng bán căn hộ sơ cấp CBRE (−30% YoY 2 quý liền) | HN Q2 ~5.800 căn, Q1 +33% YoY | **HN Q3 ~3.900 căn, −66% YoY**, −33% QoQ ([DN&PL 16/10, dẫn CBRE](https://doanhnhan.baophapluat.vn/nguon-cung-can-ho-ha-noi-quy-iii-2026-giam-40-thanh-khoan-di-xuong.html)). Một nguồn không ghi tên CBRE ghi −48%. HCM: không có số. HN Q2 YoY: không có số | **1 quý đã qua ngưỡng** (HN). Chưa xác định được "2 quý liền" |
| Tài sản nhận gán nợ / TSĐB chờ xử lý (đặt mốc đầu từ BCTC Q3) | — | **Không có số.** Không có bản tổng hợp; BQ không có cột này | Mốc đầu CHƯA lập |
| Liên NH qua đêm (>6% đột biến / kéo dài) | 5,79% (30/10) | **6,07% phiên 06/11**, về 4,8% ngày 12/11 ([TBTCVN 14/11](https://thoibaotaichinhvietnam.vn/thi-truong-tien-te-tuan-9-13-11-usd-bat-tang-kich-hoat-hai-cong-cu-giua-nhip-hut-rong-hon-25000-ty-dong-206938.html)) | **Chạm mức cảnh báo** (1 phiên, đã tan). Không kéo dài |
| NPL NHNN, nội bảng trừ 5 NH kiểm soát đặc biệt (>3% / >5%) | 1,51% (30/6, đang giảm) | **1,58% (T7) → 1,66% (T8)** ([Báo Đấu thầu 09/11](https://baodauthau.vn/chu-trong-kiem-soat-truoc-ap-luc-no-xau-lan-rong-post212126.html)). Số 30/9: không có | Không, nhưng **đảo chiều tăng** |
| NPL gộp 27 NH niêm yết (>3% / >5%) | 2,01% (Q2, TCBS) | **2,12%** (30/9, 28-29 NH). Cuối 2025 là 1,87-1,88%. Nợ xấu +26,8% YTD. SSI 13 NH: 2,09% ([24hmoney](https://24hmoney.vn/news/no-xau-ngan-hang-quy-3-tang-ap-luc-chat-luong-tai-san-don-ve-cuoi-nam-c4a2857960.html), [vietbao 08/11](https://vietbao.vn/no-xau-ngan-hang-tang-tro-lai-chat-luong-tai-san-tao-khoang-cach-giua-cac-nha-bang-614997.html)) | Không |
| Bao phủ ngành (lead table không có ngưỡng) | ~83% (Q2) | 74% (SHS) · 77% (SSI) · ~80% (FiinRatings, thấp nhất 5 năm). Riêng nhóm NH TMCP 55% (SSI) | — (chạm mốc <75% của entry 13/10, theo 1 nguồn) |
| VND (mất giá >3%/tháng) | VCB bán 26.170 (02/10) | VCB bán **26.010** (27/11), 26.020 (28/10) (`data/vcb_fx_rate.csv`) | Không |
| Dự trữ ngoại hối (<60 tỷ USD) | 87,6 tỷ (18/6, NHNN) | 82,8 tỷ (07/2026, theo IMF qua trang tổng hợp, 1 nguồn chưa kiểm). NHNN mua USD giao ngay từ 11/11 | Không |
| Rollover TPDN BĐS (>100K tỷ thất bại/quý) | Đáo hạn Q4 ~77K tỷ | Đáo hạn 12 tháng sau Q3: 252K tỷ (12 tháng trước: 157K) ([24hmoney](https://24hmoney.vn/news/loat-dau-moc-cua-thi-truong-trai-phieu-sau-9-thang-c4a2849459.html)) | Không (Q4 về cấu trúc không thể chạm) |
| CPI / lạm phát cơ bản | T9: 5,08% / 4,45% | **T10: 5,09% / 4,04%** (NSO; `te_cpi_yoy_snapshot.csv`). T11 chưa công bố (~06/12) | Đẩy chi phí, lệch trục. Không có relapse mới |

Điểm không thể quay lại (point of no return): 0/4.

### A2. Bảy ngưỡng "tăng ngầm" chi phí vốn

| # | Mốc | Hiện tại | Chạm? |
|---|---|---|---|
| 1 Spread CCTG Big-4 − tiết kiệm 12M online | 12M 0,6 · 6M 0,7 | 12M 7,4−6,8 = **0,6** · 6M 7,5−6,8 = **0,7** (CSV CCTG 02/11, deposit 16/11) | Không |
| 2 Top-5 tư nhân 12M / số NH ≥7% | ~7,2% · 10 NH | **~6,98% · 4 NH** (MBV, PGBank, Sacombank, VIB) ([vietbao 03/11](https://vietbao.vn/lai-suat-huy-dong-ngan-hang-nao-cao-nhat-thang-112026-614379.html)) | Không (giảm) |
| 3 Liên NH 3M, bình quân tháng >7,5% | ~6,9-6,98% | 6,60% (05/11) → **7,45% (12/11)**. Bình quân tháng 11: không đủ số | Không. 7,45% sát ngưỡng |
| 4 Tín dụng YTD − huy động YTD ≥2pp | +1,11pp (28/9) | Số toàn hệ thống cùng phạm vi sau 28/9: **không có**. Chỉ có số khu vực 2: −0,95pp, khác phạm vi, không dùng | Không có số |
| 5 Tiền gửi lớn ≥10% kéo dài 2 tháng | Đồng hồ chỉ tính từ xác nhận đầu tiên ≥13/10 | PVcomBank 10% (từ 2.000 tỷ, tại quầy), xác nhận **03/11** ([vietbao](https://vietbao.vn/lai-suat-huy-dong-ngan-hang-nao-cao-nhat-thang-112026-614379.html)) | **Đồng hồ đang chạy.** Chạm nếu vẫn ≥10% tới khoảng 03/01/2027 |
| 6 CCTG nhóm sau Big-4, bậc 100tr ≥9,5% hoặc +0,3pp | VPB 9,2% | VPB **9,0%**, TCB 8,0 → **7,6%**, MB 7,1% (tier2 CSV 02/11) | Không (giảm) |
| 7 Trái phiếu cấp 2 Big-4, biên ≥2,75pp | CTG +2,25 | Không tìm thấy đợt mới tháng 11 | Không |

0/7 chạm. Kill-switch A: effective 7,4% dưới ngưỡng 7,5%, CLEAR.

Lãi vay mua nhà Savills ~13%: chưa có số mới để đọc kèm theo luật 14/10. Đây vẫn là 1 nguồn, chưa kiểm.

### A3. Audit exposure BĐS của ngân hàng, Q3/2026

| NH | %BĐS kinh doanh (Q2 → Q3) | NPL Q3 | Bao phủ (Q2 → Q3) | Nguồn |
|---|---|---|---|---|
| TCB | 26,7% → **25,12%** (dư nợ giảm 7.927 tỷ QoQ) | 1,36% (từ 1,08%). Nhóm 2 tăng gấp đôi, nhóm 3 +252% | 126-128% → **107%** | [vietbao 31/10 (VietTimes)](https://vietbao.vn/12-ngan-hang-tu-nhan-cho-vay-kinh-doanh-bat-dong-san-115-trieu-ty-dong-ai-dan-dau-613978.html), 24hmoney |
| HDB | Không có số (dư nợ KD BĐS 86.155 tỷ, +22,7% YTD) | **3,4%** (đầu năm 2,43%). Nợ xấu +85% YTD, nhóm 2 +48% | 50% → **46%** | [vietbao 01/11, BCTC hợp nhất](https://vietbao.vn/hdbank-cho-nhom-cong-ty-lien-quan-lanh-dao-ngan-hang-vay-hon-10000-ty-614059.html) |
| MBB | 13,64% → **13,95%**, vẫn tăng (cuối 2025: 11,18%) | ~1,67%, nợ xấu +53% | 93,6% → **~85%** | VietTimes, 24hmoney |
| ACB | Không có số (Q2 ~6%) | 1,04% riêng lẻ / 1,18-1,19% nếu tính theo CIC | 104% riêng lẻ / 91% theo CIC | [VNBA](https://vnba.org.vn/vi/acb-dat-hon-16-600-ty-dong-loi-nhuan-truoc-thue-sau-9-thang--fitch-ratings-nang-xep-hang-len-bb-24042.htm?print=print), 24hmoney |

Lưu ý về HDB:
- Số NPL Q2 trong bảng audit 26/08 là 2,12%, có thể khác phạm vi với số 2,43% đầu năm và 3,4% hiện nay. Tôi chưa đối chiếu được BCTC gốc.
- Thêm một cảnh báo (WARNING): báo chí nêu khoản cho vay nhóm công ty liên quan lãnh đạo khoảng 10.181-10.183 tỷ. Hai con số trong bài lệch nhau.

Thứ tự dễ tổn thương nay là **HDB #1 > TCB > MBB > ACB**. Trước đây TCB đứng #1; nay TCB đang giảm tỷ trọng BĐS, còn HDB là NH duy nhất trong bảng có NPL trên 3% và bao phủ dưới 50%.

### A4. Phân loại và kịch bản

**Phân loại giữ nguyên:** trục 1 STRUCTURAL_ACCUMULATION, trục 2 không xử lý được bằng một can thiệp, giai đoạn GIỮA (đã dời từ 14/10), độ tin cậy AMBIGUOUS. So với 26/08: giai đoạn đã đổi (sớm-giữa → giữa, từ 14/10), độ tin cậy không đổi.

Hình thái đang chuyển từ "tích tụ" sang "chững / đóng băng cục bộ". Kịch bản B có 3 điều kiện định lượng, nay đạt 1/3:

| Điều kiện của kịch bản B | Trạng thái |
|---|---|
| Giao dịch cả nước −30-50% YoY | Đạt (−32,7%, 1 quý) |
| NPL >2,5% | Chưa (2,12%) |
| Chi phí vốn vượt ngưỡng | Chưa (0/7) |

**Lực đỡ ngược chiều:**
- Chính sách vẫn nới: CV 9608 yêu cầu giảm lãi suất, TT 50 nâng trần LDR lên 95% từ 01/12, swap 182 ngày, NHNN mua USD.
- FX vững.
- Vi phạm TPDN thấp (0,24%).
- Lạm phát cơ bản giảm (4,04%).
- GDP Q3 tăng 9,95%.

**Kịch bản 6-12 tháng (JUDGMENT, không phải thống kê):**

| Kịch bản | 14/10 | Nay |
|---|---|---|
| A — tích tụ tiếp, có quản lý | 50-55% | **45-50%** |
| B — đóng băng thanh khoản BĐS cục bộ | 20-25% | **25-30%** |
| C — stress hệ thống | 5-10% | 5-10% |
| D — hạ cánh mềm sớm | 15-20% | **10-15%** |

Khung dài hạn 3-7 năm của 26/08 giữ nguyên. Playbook không đổi: không đổi V2.4/DT5G/margin.

### A5. Escalate

**Không có tín hiệu buộc escalate ngay.** Các mục nên báo user, mức độ trung bình:
1. **Lượng bán sơ cấp CBRE Hà Nội Q3 −48…−66% YoY.** Nếu Q2 cũng ≤−30% YoY thì ngưỡng 14/10 đã chạm ngay bây giờ. Cần ai đó lấy số CBRE HN Q2/2025 và Q2/2026, cùng số HCM Q3.
2. **HDB** (NH Tier-1 trong book): NPL 3,4%, bao phủ 46%, kèm cảnh báo cho vay bên liên quan. Đây là số trong chu kỳ quý nên không phải trigger "ngoài chu kỳ". Chỉ là cảnh báo (WARNING), làm PRIOR cho discretionary / due diligence, không phải lệnh bán.
3. **Vận hành:** kiểm tra tháng 11 **không chạy**. Không có file `vn_realestate_monthly_checks/2026-11.md`. Dòng cuối `logs/vn_realestate_monthly_check.log`: `LỖI: claude -p --agent macro-strategist thoát mã 1. Lỗi thật: (stderr rỗng)`. Tôi chỉ báo, không sửa.
4. ON 6,07% (06/11) chạm mức cảnh báo, nhưng đã tan trong 1 tuần. Đây là mẫu đầu tháng / cuối tháng lặp lại (01/06, 31/07, 30/10, 06/11), là triệu chứng thiếu vốn cấu trúc. Tôi đề xuất ghi nhận, chưa phải hành động.

## PHẦN B — Quét `kb/structural_break_watch.json`

| Sự kiện | Trạng thái | Ngày hiệu lực thật, nguồn | Đề xuất |
|---|---|---|---|
| ftse_msci_upgrade | triggered (giữ) | FTSE 21/09/2026. Đợt 2 (30% luỹ kế) có hiệu lực 22/03/2027, giao dịch cơ cấu 19/03. MSCI: không đổi (06/2026 chưa vào danh sách theo dõi; review kế tiếp ~06/2027) | Giữ kết luận "không đổi tham số". Xem đọc BLIND bên dưới |
| krx_microstructure | watching → **sắp kích hoạt** | **Chuyển toàn bộ cổ phiếu niêm yết HNX sang HOSE:** phiên cuối trên HNX 23/12, ngừng giao dịch 24-25/12, giao dịch trên HOSE từ **28/12/2026**. Căn cứ: TT 139/2025/TT-BTC ([VietnamPlus 30/09](https://www.vietnamplus.vn/2312-ngay-giao-dich-cuoi-cung-cua-cac-co-phieu-tai-hnx-post1139250.vnp), [TheLeader](https://theleader.vn/chuyen-toan-bo-co-phieu-niem-yet-tren-san-hnx-se-sang-san-hose-d47892.html)). Khoảng 299 mã; biên độ ±10% → ±7% (phương án biên độ sau chuyển chưa công bố); phân loại Prime/Standard Board công bố 28/12. Giao dịch xuyên trưa và nới biên độ: chưa có ngày ([24hmoney 07/10](https://24hmoney.vn/news/chung-khoan-sap-giao-dich-xuyen-trua-noi-bien-do-va-tien-gan-t-0-c1a2841286.html)) | Ghi `effective_date` 2026-12-28. Chỉ chuyển `triggered` sau khi xác minh phiên đầu tiên chạy thật. Tầng cần re-validate: thêm logic trần/sàn theo biên độ và trường sàn giao dịch trong universe_pit / fill model / chase-cap cho nhóm mã HNX cũ |
| settlement_cycle | watching | Không có ngày T+1/T+0. CCP dự kiến 2026-2027 | Giữ |
| margin_regulation | watching | Không thấy văn bản mới. Dư nợ margin kỷ lục ~457,5K tỷ (Q3) là biến trạng thái, không phải sự kiện quy định | Giữ |
| foreign_ownership_room | watching | **Luật CK sửa đổi thông qua 13/11/2026, hiệu lực 01/03/2027** ([TTTCTT 13/11](https://thitruongtaichinhtiente.vn/quoc-hoi-thong-qua-luat-sua-doi-bo-sung-mot-so-dieu-cua-luat-chung-khoan-87022.html)). Bản tóm tắt KHÔNG nhắc room ngoại; dự thảo trước đó từng đề xuất "không hạn chế" | Giữ. **Dispatch legal-vn đọc toàn văn** |
| new_products | watching | Luật trên thêm cơ chế thử nghiệm có kiểm soát (sandbox, hiệu lực 01/03/2027). Bán khống / T+0: chưa triển khai | Giữ |

Sự kiện mới đề xuất thêm vào registry: không cần mục riêng. HNX→HOSE xếp vào `krx_microstructure`, hoặc tách mục `exchange_consolidation` nếu muốn theo dõi riêng Prime Board. `next_review` nên đặt khoảng đầu 02/2027, sau mùa BCTC Q4.

**Đọc BLIND FTSE (định tính, không dùng giá):** giữ nguyên đọc 13/10, tức "đổi DẦN, chưa phải đổi chế độ".
- Tiêu chí lên "đổi chế độ thật": MSCI đưa vào danh sách theo dõi (chưa), nới room ngoại (luật đã qua nhưng nội dung room chưa xác minh, sớm nhất 01/03/2027).
- Hai tiêu chí còn lại (tỷ trọng 27 mã >60%, khối ngoại >15% GTGD) là đo lường, thuộc việc của Taylor; tôi không xem.
- Dữ kiện không phải giá: khối ngoại bán ròng HOSE tháng thứ 3 liên tiếp (T10 ~22-24K tỷ, từ REGIME READ #3) là sell-on-news, không phải dòng vốn thụ động vào.
- Mốc có khả năng thấy tín hiệu vẫn là sau 19/03/2027 và hai đợt 06/2027, 09/2027.
- Theo mặc định của protocol: không đổi tham số.

## Những gì tôi không xác minh được
- Tín dụng BĐS / tổng tại 30/9. NPL NHNN tại 30/9.
- Tỷ lệ vi phạm TPDN sau T8.
- Lượng bán CBRE HN Q2 YoY và HCM Q3. Cũng chưa rõ CBRE HN Q3 là −66% hay −48%.
- **Tài sản nhận gán nợ:** không có tổng hợp, mốc đầu chưa lập. Muốn lập phải đọc thuyết minh BCTC từng NH.
- %BĐS kinh doanh của HDB và ACB tại Q3. Phạm vi NPL của HDB (hợp nhất hay riêng lẻ, có gồm HD Saison không).
- Liên NH 3M bình quân tháng 11, và mọi số liên NH sau 12/11.
- Chênh tín dụng − huy động toàn hệ thống sau 28/9.
- Dự trữ ngoại hối (con số IMF 82,8 tỷ chỉ qua 1 trang tổng hợp).
- Lãi vay mua nhà ~13% (Savills, 1 nguồn).
- Nội dung room ngoại trong Luật CK sửa đổi. Biên độ giá sau chuyển sàn.
- Số NH ≥7% cuối tháng 11 (khuyến mãi VPB/TCB hết hạn 11/11 và 30/11).
- **Dữ liệu nội bộ:** CSV CCTG không có dòng mới sau 02/11, deposit không có dòng sau 16/11. File log mà crontab trỏ tới (`mike/logs/refresh_deposit_cctg_weekly.log`) không tồn tại. Tôi chưa xác định được cron tuần có chạy hay không. Nếu không có dòng mới, CCTG sẽ stale vào khoảng 17/12.
- Dự thảo nghị quyết của Bộ Xây dựng siết tín dụng người mua nhà thứ hai: chưa rõ trạng thái và ngày.

**Nguồn chính:** đã dẫn trong từng bảng. Thêm: [CafeF 02/10 (PVcomBank trái phiếu 10,5%, không phải tiền gửi)](https://cafef.vn/ngan-hang-huy-dong-von-voi-lai-suat-len-toi-105-nam-188261001235428064.chn), [TTTCTT 17/11 (TCBS: ON Q3 bình quân 3,9%)](https://thitruongtaichinhtiente.vn/print/87117.html), [VOV 15/10](https://vov.vn/kinh-te/thi-truong-bat-dong-san-quy-iii2026-gia-ha-nhiet-luong-giao-dich-giam-tren-50-post1341209.vov) (tít "giảm trên 50%" thực ra là 48% số môi giới khảo sát, so với quý trước; không dùng).
