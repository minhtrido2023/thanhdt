> **ĐỒNG BỘ r3 (09/11/2026, job Taylor_20261108_180130):** headline mới = `REPORT_r3.md` — CK holding base 0% (luật user): **tâm 13.969 · P10 12.422 · P90 15.564 @9.990 (06/11) ⇒ DƯỚI vùng** (5 tỷ & 40 tr); bản song song có CK holding r2: 10.761 / 8.624 / 13.207 ⇒ TRONG. Lỗi giá gốc không chiết khấu nêu ở §2 dưới đây ĐÃ SỬA trong r3 (giá gốc + thặng dư cùng pv(y), y 2,5/3,25/4; s = biên NC-II quan sát 0,70) — các tâm 10.387 / 8.393–9.700 bên dưới là SỐ CŨ (r2/5F). Đính chính: 'vay 390 tỷ CRV đáo hạn 18/11/2026' SAI — đã trả 9T/2026, nay không còn nợ vay (BQ ticker_financial 2026Q3).

> **QUY ƯỚC CUỐI (user chốt 08/11/2026 10:50 ICT):** KHÔNG áp luật 3c chặt. Moat chỉ được THÊM vào định giá khi bền; NARROW/NONE = không thưởng nhưng KHÔNG trừ. **Headline = mô hình cơ sở hiện hành (tâm 10.387 theo báo cáo gốc)**; mọi 'bản chặt-3c / headline mới / chờ duyệt' bên dưới chỉ còn là **độ nhạy rủi ro** ('nếu về trung bình ngành'), KHÔNG phải kết luận định giá. Các sửa lỗi dữ liệu/công thức/peer trong tài liệu này vẫn có hiệu lực. Không mã nào trong 20 mã có moat bền ⇒ không thêm tham số moat.

# HHS — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (07/11/2026, job Taylor_20261107_130213; VÒNG SỬA job Taylor_20261107_131625 sau skeptic — bản trước: `ADDENDUM_5F_r1.md`)

Bổ sung cho `REPORT_r2.md` (05/11/2026), không thay nó. **Kết luận: moat NONE / loại LOCATION (asset-play quỹ đất CRV Hải Phòng), KHÔNG bền — kết luận dựa chủ yếu vào (iii) đồng hồ (quỹ đất tự cạn); chuỗi ROIC của HHS hỏng cả hai phía (§2). Mô hình hiện hành KHÔNG nhất quán luật 3c** (r1 viết "gần nhất quán, lệch −0,4%, không trọng yếu" — SAI, rút lại): `crv()` để giá gốc HTK cũ ~6.009,8 tỷ KHÔNG chiết khấu (chỉ thặng dư s nhân pv(4)) ⇒ vốn nằm ~4 năm vẫn được coi như sinh đủ Ke, rồi còn cộng thêm biên ≈ TB peer 37,7% (peer ở biên đó có ROIC5Y trung vị 6,2% < Ke) = **kênh RONIC>Ke ngầm**. **BẢN CHẶT-3C = KHOẢNG tâm 8.393 – 9.700 (−19,2% … −6,6% so 10.387), % kết cục dưới giá 35,2% → 50,8–79,8%; nhãn TRONG giữ** ở mọi biến thể và mọi cỡ — quy ước (năm vốn nằm, có trừ khách trả trước hay không) chờ Mike/user duyệt. Quy ước này kế thừa từ DD TCH v2 nhưng lớn gấp 20–48 lần trục I.14 (−41) mà r1 báo.**
Số vòng sửa: `5F/moat_fix_r2.py` (nạp `moat_sens_5f.py` ⇒ chạy lại assert tái lập tâm 10.387; 2 lần trùng byte md5 out.txt `f9dd1286…`, out.json `21385620…`) → `5F/moat_fix_r2_out.txt`. Số r1: `5F/moat_sens_5f.py` (hằng số + `fv2` chép nguyên văn `calc/hhs_r2.py`, assert tái lập tâm/P10 REPORT_r2; chạy 2 lần trùng byte md5 `2ce48bf4…`) → `5F/moat_sens_5f_out.txt`; BQ `tav2_bq.ticker_financial` truy vấn 07/11/2026 → `5F/bq_annual.csv`, `5F/peer_stats_out.txt`.

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng hay làm mới: LÀM MỚI** — `data/moat_tags.csv` không có dòng HHS (cũng không có CRV/TCH); `kb/projects/hhs-dd-20261101.md`, `dd_HHS_20261101/{REPORT,SKEPTIC,GAPS*}.md`, REPORT/REPORT_r2 không có mục 5F/moat ⇒ chưa từng audit. Làm từ dữ liệu đang có trong thư mục + BQ; không nghiên cứu mới.

**Loại hình DN:** HOLDING — giá trị chủ yếu là 51,15% lợi ích CRV (BĐS nhà ở Hải Phòng, quỹ đất mua từ trước theo giá gốc; NC-II đã bán trước 3.099 tỷ) + đại lý xe tải Dongfeng (LNST 25/35/50 tỷ × P/E 5/6/8 ≈ 0,5k đ/cp, nhỏ) + tiền mẹ/Pruksa. Khung 5F = BĐS (bẫy: quỹ đất giá gốc ≠ hào) + phân phối ô tô.

| Lực | Mức | Cơ chế + bằng chứng (nguồn) |
|---|---|---|
| Rào cản gia nhập | 🟡 TB | BĐS: cần quỹ đất + pháp lý dự án. Lợi thế CRV là đất mua sớm giá gốc (biên NC-II ex-PPA 52,2% — `dd_HHS_20261101/REPORT.md` C7), nhưng dự án mới I.14 phải mua đất ~1.066 tỷ theo giá hiện hành (REPORT §5 TM18) ⇒ lợi thế không tái tạo. Xe tải: hợp đồng đại lý không có chữ "độc quyền" (REPORT_r2 §9.13). |
| Nhà cung cấp | 🔴 Cao | Nhà nước (tiền SDĐ: TB 2124/TB-TTCP N01 bổ sung 7,87 tỷ; KL 08 Pruksa điều chỉnh giá — §9.3–4). Dongfeng: phải trả 364,01 tỷ, HHS là đại lý (§9.10). |
| Người mua | 🟡 TB | Người mua nhà phân tán; NC-II đã thu trước 3.099,2 tỷ (cầu hiện tốt). NƠXH bị cơ quan nhà nước ép giá theo quyết toán (KL 08). Xe tải: khách doanh nghiệp vận tải, sản phẩm dễ so giá — biên gộp peer ô tô TB 2016–25 **6,6%** (HAX 5,7 · SVC 6,5 · TMT 7,6). |
| Sản phẩm thay thế | 🟡 TB | Dự án khác tại Hải Phòng (VHM có mặt — thị phần **cần kiểm chứng**); xe tải thương hiệu khác. |
| Cạnh tranh nội ngành | 🔴 Cao | 14 CĐT niêm yết nội địa (không phải đối thủ trực tiếp tại HP trừ TCH cùng nhóm): ROIC5Y trung vị **6,2%** (VHM 14,0 · HDG 12,6 · NTL 22,9 … NVL 0,8 · SCR −0,9) < Ke 13,5% ⇒ ngành không giữ được siêu ngạch. |
| **Lực thứ 6** | 🔴 | (a) **Quỹ đất tự cạn**: HTK CRV còn lại 7.338,8 tỷ (gồm I.14) bán hết trong ~4 năm (mô hình PV4) ⇒ "hào" giá gốc hết khi bán xong. (b) Cấu trúc holding/quản trị: kiểm soát CRV phụ thuộc uỷ quyền 7,53%, biên >50% chỉ 1,15đ% (§9.2). (c) ~~Vay 390 tỷ CRV đáo hạn 18/11/2026~~ — ĐÃ TRẢ 9T/2026, không còn nợ vay (đính chính r3). Pháp lý = WARNING, không dùng ép biên (luật 27/09). |

**moat_tier = NONE · moat_type = LOCATION (asset-play quỹ đất giá gốc, không phải rào cản tái tạo) · rủi ro số 1 = thực hiện thặng dư quỹ đất CRV còn lại (biên 24–47% theo kịch bản) + dòng tiền lên HHS qua 2 tầng holding (CK holding là trục quyết định nhãn — REPORT_r2 §3).**

## 2. Moat trong mô hình
| Điều kiện moat BỀN | KQ | Bằng chứng (BQ `ticker_financial` 07/11/2026, dòng Q4 = năm; Ke = r 13,5%) |
|---|---|---|
| (i) siêu ngạch nhiều chu kỳ | ❌ (yếu — dữ liệu hỏng 2 phía) | **Chuỗi ROIC HHS không dùng được ở CẢ HAI phía ⇒ đối xứng 'nghi artifact':** ROIC_Min5Y = 0,0% suốt 2017–2022 CÙNG LÚC ROIC5Y 330–335% (2015–18) — trung bình 330% với min 0 không thể cùng đúng; ROIC10Y 165–335% đến 2023. Phía thấp cũng méo: HHS là holding sống bằng thu nhập liên kết/tài chính ⇒ ROIC (EBIT/vốn hoạt động) ~0,3–2,6% (ROIC5Y 2019–26Q3) trong khi ROE 6–8% — ROIC thấp KHÔNG chứng minh được thiếu siêu ngạch. Số đo (BQ `ticker_financial` 07/11/2026, `5F/bq_annual.csv`): ROIC_Min5Y 0,0–2,0% (2016–24), −0,4% (2025–26Q3); ROIC_Min10Y 0,0/−0,4%. **ROE riêng** (`ROE_Trailing` Q4): 2016 4,7 · 2017 2,9 · 2018 6,1 · 2019 6,1 · 2020 7,9 · 2021 6,0 · 2022 5,5 · 2023 8,0 · 2024 7,8 (< Ke 9/9 năm); 2025 **22,1%**, ROE5Y 15,7% — do ghi nhận 3.488,72 tỷ khi hợp nhất CRV (REPORT.md:94) = giá trị quỹ đất tích luỹ nhiều năm nay mới ghi nhận (r1 gọi 'không kinh tế' — rút lại), một lần, không lặp. **CRV không có trong BQ ⇒ cần kiểm chứng**; proxy TCH (cùng nhóm, HP): ROIC5Y 5,6–12,6% · ROIC_Min5Y 1,0–4,5% · ROIC10Y 7,0–11,9% · ROE_Trailing TB 2016–25 8,8% (min 3,1) < Ke. ⇒ (i) nghiêng ❌ nhưng không phải trụ chính; **kết luận không bền đứng trên (iii)**. |
| (ii) cơ chế rào cản gọi tên được | ⚠️ yếu | LOCATION = quỹ đất mua sớm; không tái tạo (I.14 mua giá thị trường); xe tải không độc quyền. |
| (iii) không có đồng hồ cắt hào | ❌ | Quỹ đất tự cạn ~4 năm (lực 6a). |

⇒ **moat_durable = false ⇒ luật 3c: RONIC = Ke VÀ biên về TB chu kỳ ngành.** Rà mô hình hiện hành (`calc/hhs_r2.py:33`, chép `hhs_redo.py`):
- **Không có terminal**, NAV hữu hạn (backlog PV1, HTK cũ PV4) — nhưng điều đó KHÔNG tự đủ chặt.
- **LỆCH 3c CHÍNH — vốn HTK cũ không chiết khấu:** `crv = CRV_COST + … + (REST_CRV−NEW_I14)·s·pv(4)` ⇒ giá gốc ~6.009,8 tỷ được trả về đủ 100% ở năm 0 dù chỉ thu hồi khi bán (~4 năm theo chính mô hình) — tương đương giả định vốn đó sinh đúng Ke trong lúc nằm kho, RỒI cộng thặng dư s (E[s] 35,5% ⇔ GPM ~37,7% = TB peer 37,7% / trung vị 37,9%, 14 CĐT nội địa; dòng Q4 GPM_P0 = năm). Peer ở biên đó có ROIC5Y trung vị 6,2% < Ke ⇒ biên 37,7% trên giá gốc ≠ lợi nhuận ≥ Ke trên vốn; mô hình đếm cả hai = RONIC>Ke ngầm. r1 chỉ so biên với peer, bỏ sót kênh vốn — sai. Bản chặt: trừ `giá gốc × (1−pv(y))`.
- **Quy ước chờ duyệt** (đều đối xứng, không cắt một chiều): A) y = 4 năm (= năm thu thặng dư của mô hình); B) y = 2,5 (bán đều 4 năm, vốn thu hồi trung bình giữa kỳ — ước lượng); C) y = 2,5 và loại 3.099,2 tỷ khách trả trước NC-II khỏi vốn bị giam (khách đã ứng tiền). Thêm A+ (chiết khấu cả giá gốc I.14 1.329 tỷ) làm cận dưới. Quy ước bỏ qua chiết khấu giá gốc kế thừa từ DD TCH v2.
- **I.14** (dự án mới) −15/0/+40% ⇒ kỳ vọng +6,25% — thưởng NPV>0 không cơ sở moat; bản chặt I.14 ±15% đối xứng (r1: −41 tâm, giữ). Mọi bản chặt §3 đã gồm sửa này.
- **Backlog NC-II** (m 30/33,5/36% × PV1): doanh thu ĐÃ KÝ/ĐÃ THU, biên quan sát cùng dự án ⇒ dữ kiện hợp đồng; stress ở bảng r1, không vào bản chặt.
- **Ô tô P/E:** E[P/E] 6,1 < 1/Ke 7,4 ⇒ không thưởng ✔. BĐSĐT = tài sản hiện hữu ⇒ giữ.
- **GOV_AX (CK quản trị/pháp lý) KHÔNG chỉ là WARNING:** trục 0/5/10/15% (0,55/0,20/0,15/0,10) có kỳ vọng **−4,0%** (đo, `moat_fix_r2_out.json` E_gov) và **NẰM TRONG TÂM** — ví dụ bản A: tâm 8.393 có GOV, 8.743 nếu GOV=0. Đây là giảm trừ định lượng trong base, không phải chỉ cờ. Không đếm trùng với biên (biên không bị ép vì pháp lý — bài học E); việc có giữ trục này trong base hay chuyển ra WARNING thuần là quyết định quy ước của Mike/user.
- **I.14 đối xứng theo luật 20 là BẮT BUỘC** (dự án mới: base = sổ sách/NPV 0, lệch chỉ khi có cơ sở độc lập), không phải 'chờ duyệt'. Phần chờ duyệt chỉ là quy ước chiết khấu vốn (A/B/C).
- Quy ước năm 1 (bài học H): giữ `pv(1)`/`pv(4)` @13,5% của mô hình; chỉ thêm `pv(y)` cho giá gốc.

## 3. Độ nhạy WIDE / NARROW / NONE (sau CK 5 tỷ; giá 9.550, 04/11/2026; `5F/moat_fix_r2_out.txt`)
Bản chặt-3c (I.14 ±15% đối xứng, biên = mô hình ≈ TB peer) theo quy ước chiết khấu giá gốc:
| Biến thể | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn 5 tỷ / 10tr / 40tr |
|---|---|---|---|---|---|---|
| Hiện hành REPORT_r2 (không chiết khấu, I.14 +6,25%) | 10.387 | 8.252 | 10.194 | 12.827 | 35,2% | TRONG ×3 |
| r1 chặt (chỉ I.14 đối xứng) — **rút** | 10.346 | 8.218 | 10.152 | 12.769 | 36,0% | TRONG ×3 |
| **A: giá gốc pv(4)** | **8.393** | 6.635 | 8.238 | 10.377 | 79,8% | TRONG ×3 |
| **B: giá gốc pv(2,5)** | **9.012** | 7.142 | 8.845 | 11.123 | 66,7% | TRONG ×3 |
| **C: pv(2,5), trừ KH trả trước 3.099** | **9.700** | 7.696 | 9.527 | 11.967 | 50,8% | TRONG ×3 |
| A+: pv(4) cả giá gốc I.14 (cận dưới) | 7.961 | 6.277 | 7.824 | 9.848 | 86,8% | TRONG ×3 (P90 sát giá +3%) |

Độ nhạy moat trên từng quy ước (tâm; nhãn TRONG ×3 mọi ô):
| Moat giả định | A pv(4) | B pv(2,5) | C pv(2,5)−KH |
|---|---|---|---|
| WIDE: biên = NC-II 52,2%, I.14 +40% | 9.695 | 10.315 | 11.003 |
| NARROW: biên 45,0%, I.14 hiện hành | 8.887 | 9.506 | 10.194 |
| **NONE (chặt-3c, biên TB peer)** | **8.393** | **9.012** | **9.700** |
| NONE-sàn: biên = TB TCH 29,9% | 8.046 | 8.666 | 9.354 |
| NONE + GOV=0 (đo đóng góp trục quản trị) | 8.743 | 9.388 | 10.104 |

Đọc: quy ước chiết khấu vốn (A↔C: 1.307 đ/cp) lớn hơn chọn peer (TB↔TCH: 346–347 đ/cp) và gần bằng biên độ moat NONE↔WIDE (1.302–1.303). Giá 9.550 nằm giữa P10 và P90 ở mọi biến thể/cỡ ⇒ nhãn TRONG không nhạy (ca gần ranh giới nhất: A+ P90 9.848). Luật 4 (giá ≤ 0,85×tâm, cần tâm ≥ 11.235) không đạt ở mọi bản chặt. % kết cục dưới giá tăng mạnh (35% → 51–80%) ⇒ phân bố dịch xuống đáng kể dù nhãn giữ.

## 4. Thay đổi so với báo cáo hiện hành
REPORT_r2/SUMMARY.json **giữ nguyên, không sửa; không ghi `dd_price_zones`**. Headline theo luật 3c = **KHOẢNG tâm 8.393 – 9.700** (A/C; B giữa 9.012) so 10.387: **−687 … −1.994 đ/cp (−6,6% … −19,2%)**; P10 8.252 → 6.635–7.696; P50 10.194 → 8.238–9.527; P90 12.827 → 10.377–11.967; % dưới giá 35,2% → 50,8–79,8%; **nhãn TRONG → TRONG** (5 tỷ, 10tr, 40tr). Chênh do: kênh vốn HTK không chiết khấu (−646 … −1.953, phần RONIC ngầm) + I.14 đối xứng (−41, bắt buộc luật 20); phần biên đóng góp 0 (biên mô hình đã ≈ TB peer). Kết luận r1 "lệch −0,4%, không trọng yếu, có thể giữ REPORT_r2 nguyên trạng" **rút lại** — lệch là trọng yếu về giá trị/phân bố, chỉ không đổi nhãn. Chọn A/B/C: **quy ước chờ Mike/user duyệt**; cùng lỗi có khả năng nằm ở DD TCH v2 (nguồn quy ước) ⇒ đề nghị rà TCH.

## 5. Đề xuất dòng moat_tags.csv (KHÔNG tự sửa — chỉ đề xuất)
entry = L (cấu trúc NGÀNH: CĐT nội địa ROIC5Y trung vị 6,2% < Ke; phân phối ô tô GPM ~6,6%; `moat_5f.py:33`) — lưu ý dòng VHM hiện ghi entry H cho cùng ngành, Mike rà nhất quán; moat_upgrade = N.

**Nhất quán tier với họ LOCATION trong moat_tags** (IDC/NTC/SZL/DTD đều NARROW/LOCATION, asof 2026-06-05, `moat_upgrade=Y`). BQ `ticker_financial` 2025Q4 (đo 07/11/2026): ROIC_Min5Y IDC 6,3% · NTC 4,0% · SZL 10,2% · **DTD 13,3%** (brief ghi 4–6% — chỉ đúng IDC/NTC); ROIC5Y 20,6 / 12,7 / 13,7 / 22,7% — tức 3/4 mã có ROIC5Y ≥ Ke, còn HHS ROIC5Y 0,3%. Ghi chú: (a) IDC/NTC có ROIC_Min5Y < Ke như HHS mà vẫn NARROW ⇒ thang tier đang không thống nhất theo (i); (b) với HHS, **NONE hay NARROW không đổi giá trị** — cả hai đều 'không bền' ⇒ luật 3c như nhau (RONIC=Ke, biên TB ngành); khác biệt chỉ ở nhãn tier. Đề xuất giữ NONE cho HHS (không có cơ chế tái tạo quỹ đất như KCN có giấy phép mở rộng); Mike rà lại IDC/NTC (không sửa CSV).
```
HHS,NONE,LOCATION,L,"Holding (51.15% CRV Hai Phong residential + Dongfeng truck dealer, non-exclusive). Never earned above Ke: ROE_Trailing 2.9-8.0% 2016-24 (2025 22.1% = 3,488bn one-off recognition of accumulated land value on CRV consolidation), ROIC5Y 0.3-2.6% 2019-26, ROIC series broken both ways (ROIC_Min5Y 0.0 alongside ROIC5Y 330%; holding earns via associates so ROIC~2% vs ROE 6-8%) - durability verdict rests on depleting land bank. CRV not in BQ (verify); proxy TCH ROIC5Y 5.6-12.6%, ROE avg 8.8%. Only edge = land bank at historical cost (NC-II ex-PPA GPM 52.2%) - self-depleting ~4y, new I.14 land bought at market. #1 risk: realising remaining CRV land-bank surplus + cash upstreaming through 2-tier holding (holding discount axis decides label); CRV control via 7.53% proxy votes; 390bn CRV loan REPAID 9M2026 (r3 correction), no borrowings",2026-11-07,5f_full_dd_redo,N
```

*Phân tích, không phải khuyến nghị đầu tư. 5F dùng kiến thức non-point-in-time ⇒ chỉ cho DD sống, cấm đưa vào backtest. Pháp lý/quản trị: chỉ WARNING (luật 27/09). Vòng sửa sau skeptic; chưa qua skeptic lần 2 (Mike chạy).*
