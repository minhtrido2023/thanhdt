# DD SZL (CTCP Sonadezi Long Thành) — chạy lại theo mẫu mù (job `Taylor_20261026_045656`, 2026-10-26)

> READ-ONLY, không phải khuyến nghị mua; user quyết. Giá tham chiếu: **28.200 đ (đóng cửa 23/10/2026, BQ `ticker.Price`)**,
> là giá sau GDKHQ 16/9/2026. Nhãn nguồn: [BQ] · [BC] báo chí trích BCTC · [WEB] · [UL] ước lượng của tôi.
> Mẫu: `dd_template_20261026/TEMPLATE.md`. Khối chu kỳ nằm ở `CYCLE_BLOCK.md`, md5 `ef99ff38a77402dcff06a7bfbf4d25d6`, khoá lúc
> 12:07 ICT (xem `LOCK.txt`), KHÔNG sửa sau khoá.

```
BLIND_ATTESTATION (bản tổng hợp của người viết bước 2 — Taylor)
  tac_gia_buoc_1                   : subagent mới (aa8d475e5b7f07f13), không đọc README/DD cũ/verdict
  da_viet_truoc_khi_doc_BCTC_quy_Q : có (subagent không mở BCTC/bài Q3)
  vo_tinh_thay_du_lieu_cam         : CÓ — trong tóm tắt WebSearch, subagent thấy DT Q3 ~152 tỷ, LNST ~70 tỷ, cổ tức nhận ~36 tỷ
  da_doc_DD_cu_cua_ma_nay          : không (bước 1 và bước 2 trước khi ghi verdict)
  da_biet_verdict_truoc            : bước 1 KHÔNG; bước 2 (Taylor) CÓ — README §4 của template ghi verdict cũ "NON"
  quy_Q                            : 2026Q3, công bố 20/10/2026 (BQ Release_Date)
  du_lieu_tai_chinh_dung_den_quy   : 2026Q2 (bước 1)
  cycle_block_md5                  : ef99ff38a77402dcff06a7bfbf4d25d6 (thay commit: mtime 12:06:36 ICT; REPORT.md ghi sau)
  blind                            : NO
```

## KHỐI CHU KỲ — bản tóm tắt (bản gốc đầy đủ: `CYCLE_BLOCK.md`)
- **Loại ngành:** annuity hợp đồng (KCN Long Thành 487 ha đã gần đầy, nhà xưởng 99% có thuê, tiền thuê đất ghi nhận phân bổ). B và C ghi N/A; giá thuê KCN là `CHUỖI THIẾU`.
- **A:** biên LNST TTM 25,3%, phân vị **p36** trên cửa sổ 2016Q1–2026Q2. Biên gộp BQ 39,0% (p95) bị loại vì `GPM_P0` lệch BCTC. Biên gộp theo BCTC đi từ 39,3% (năm 2025) xuống **34,8%** (Q2/26), do mix xăng dầu tăng.
- **D:** dự án KCN hết hạn ~2053 (ước lượng); doanh thu chưa thực hiện + người mua trả trước ~800 tỷ; cổ tức 2025 gồm 25% tiền và 70% cổ phiếu (SLCP 28,35 → 48,2 triệu); quỹ đất mới là CCN Long Phước 75 ha; rủi ro bảng giá đất Đồng Nai 2026.
- **E:** LN chuẩn hoá **103,0 tỷ** (trung vị LNST năm 2016–25). PE chuẩn hoá thô 13,2x, ex-cash **15,0x**. **PB 1,77x (p78)**, trong khi trung vị PB lịch sử là 1,36x.
- **F:** biên gộp **cả năm 2026** (BCTC Q4/2026) **< 38,0%**, p = 0,65, due **2027-01-31**. Dự báo này cùng phía với persistence.

---

## 0. Verdict: **NON**

| Tiêu chí | Phán quyết | Bằng chứng chính | Dùng khối chu kỳ? |
|---|---|---|---|
| Có trạng thái sợ hãi / trigger (tiền đề) | **KHÔNG** | Giá điều chỉnh −6,3% so đỉnh 52 tuần (30.110 ngày 07/05/2026 → 28.200) [BQ `Close`]. Không có scandal, sốc ngành, vĩ mô hay gián đoạn. LNST Q3 là mức kỷ lục [BC-Q3] | — |
| §2 (nhóm a) | Không áp dụng | Không có scandal cá nhân | — |
| §2.5 #1 chu kỳ/tạm thời | **TRƯỢT (không có khủng hoảng để phân loại)** | Biên LNST ở p36 nghĩa là ở giữa phân phối, không phải đáy | A, C |
| §2.5 #2 sống sót | ĐẠT | Nợ vay 306 tỷ, nợ ròng ~135 tỷ / VCSH 784 tỷ [BQ Q3]; CF_OA 9T 263 tỷ ≥ NP 133 tỷ | — |
| §2.5 #3 chi phí thấp/dẫn đầu | Không đánh giá được | KCN đã đầy, cạnh tranh bằng vị trí chứ không bằng chi phí | D |
| §2.5 #4 sàn tài sản PB≲1 | **TRƯỢT** | PB 1,73x trên VCSH 30/9 [BQ], p78 lịch sử [CYCLE_BLOCK E] | E |

- **Định giá:** PE chuẩn hoá ex-cash ~14,5–15x (cập nhật bảng cân đối 30/9, §4). Nếu cộng thêm 71 tỷ cổ tức tiền đã trả ngày 7/10 thì ~15,2x. Mức này đắt hơn trung vị PE TTM lịch sử 8,1x, nên không có sàn định giá.
- **Điều kiện đổi verdict:** PB ≤ 1,1x (~17.800 đ, với VCSH không đổi) **và** một trigger thật như mất khách thuê, rút giấy phép hay sốc tín dụng KCN. Rẻ đi một mình không đủ.
- **Pháp lý:** WARNING nhẹ (§7).

## 1. Giả thuyết và kiểm chứng
Không có giả thuyết fear-buy của user cho mã này. Đây là lần chạy lại kiểm định khối mù. Giả thuyết ngược lại cần kiểm: "LNST Q3 kỷ lục khiến PE TTM 7,6x trông rẻ". Bị bác ở §2: LN Q3 phồng lên nhờ cổ tức nhận một lần.

## 2. Phân rã LN Q3/2026
| Khoản | Q3/2026 | Q3/2025 | Nguồn |
|---|---|---|---|
| DT thuần | 152,5 tỷ (+12%) | 135,6 tỷ | [BQ `Revenue_P0`], [BC-Q3] |
| Doanh thu tài chính | ~37 tỷ (~123 lần cùng kỳ), trong đó **cổ tức nhận ~36 tỷ** | ~0,3 tỷ [UL: 37/123] | [BC-Q3] |
| LNST | **69,9 tỷ** (kỷ lục quý) | 32,7 tỷ | [BQ `NP_P0`] |
| LNST lõi ≈ LNST − cổ tức (cổ tức từ DN trong nước không chịu thuế TNDN) | **~34 tỷ (ước lượng)**, +4% YoY | ~32 tỷ | [UL] |
| Biên gộp | BQ 38,8%. Bài báo không có LN gộp ⇒ **biên gộp BCTC Q3 chưa đo** | BQ 38,7% | [BQ `GPM_P0`, bị coi là lệch] |

- **Cái bền:** doanh thu cho thuê, nước và phí quản lý đi ngang đến tăng nhẹ. LN lõi ~34 tỷ/quý (ước lượng) ⇒ ~135–140 tỷ/năm nếu cổ tức nhận quay về mức một lần mỗi năm.
- **Cái một lần hoặc lệch quý:** cổ tức nhận 36 tỷ. Năm 2025 khoản này ghi ở Q2, năm 2026 ghi ở Q3 [BC-1: Q2/26 không có cổ tức]. Trên cơ sở năm, nó là khoản **định kỳ năm từ LtInvest 398 tỷ** (chưa xác minh bên trả cổ tức), không phải tăng trưởng mới. LNST 9T 133 tỷ (+42%) phóng đại xu hướng vì cổ tức rơi vào giữa hai kỳ so sánh. Kế hoạch năm 2026 là 148 tỷ (+5%).

## 3. Bảng cân đối, dòng tiền, cổ tức (30/9/2026)
- **Tổng tài sản** 2.364 tỷ. **Nợ phải trả** 1.580 tỷ, trong đó **người mua trả trước + DT chưa thực hiện ~780 tỷ** [BC-Q3]. Đây là tiền thuê đã thu, không phải nợ vay. **VCSH 784,2 tỷ** [BQ: TA − StLiab − LtLiab].
- **Nợ vay 306,4 tỷ** (+46% từ đầu năm), tiền 171,2 tỷ ⇒ **nợ ròng ~135 tỷ** [BQ `StDebt/LtDebt/Cash_P0`; BC-Q3 "vay >300 tỷ", "tiền >171 tỷ"]. Các tiền gửi có kỳ hạn tách riêng chưa đo. Cổ tức tiền 71 tỷ chi ngày 7/10 nằm NGOÀI bảng 30/9 ⇒ nợ ròng pro-forma ~206 tỷ (ước lượng).
- **Dòng tiền 9T:** CF_OA **263,5 tỷ** so NP 132,6 tỷ, tỷ lệ 2,0x [BQ `CF_OA_P0` cộng 3 quý]. CF_Invest −309,4 tỷ, chủ yếu cho **CCN Long Phước** (tổng vốn >920 tỷ, đã chi ~345 tỷ, dự kiến vận hành cuối 2026 [BC-Q3]) ⇒ còn ~575 tỷ capex (ước lượng). Nợ vay sẽ tiếp tục tăng.
- **Cổ tức:** năm 2025 trả 95% (25% tiền, 70% cổ phiếu), cao nhất từ khi niêm yết. Kế hoạch 2026 là 20% [WEB-Q3 tóm tắt].

## 4. Định giá (LN chuẩn hoá từ khối E; cột Q3 cập nhật bảng cân đối)
| Chỉ số | Khối mù (đến Q2) | Cập nhật 30/9 | Ghi chú |
|---|---|---|---|
| Vốn hoá | 1.359 tỷ | 1.359 tỷ | 48,199 triệu CP [BQ `OShares` Q3 khớp số tự tính của khối mù] |
| PE chuẩn hoá ex-cash (LN 103 tỷ) | 15,0x | **14,5x** (trừ lãi tiền gửi: ~15,3x [UL]) | nợ ròng 107 → 135 tỷ |
| PE TTM thô | 9,5x | 7,6x (TTM 179,9 tỷ) | phồng do cổ tức nhận; CẤM dùng theo mẫu |
| PE trên LN lõi ~138 tỷ/năm [UL] | — | ~10,8x | cổ tức coi là định kỳ năm |
| PB | 1,77x | **1,73x** | p78 lịch sử; trung vị 1,36x |
LtInvest 398 tỷ (giá sổ) là tài sản phi lõi sinh cổ tức ~36 tỷ/năm. Nếu tách ra thì phần lõi KCN có PE lõi khoảng 10x (ước lượng). Mức này hợp lý cho một annuity, nhưng không phải sàn sợ hãi.

## 5. Thanh khoản
20 phiên từ 25/9 đến 23/10/2026: **GTGD trung vị 0,36 tỷ/ngày**, trung bình 0,46 tỷ [BQ `Price×Volume`]. Ở mức 10% ADV, mỗi ngày mua được ~36 triệu đồng (ước lượng). Lên 1 tỷ cần khoảng 28 phiên. Free float ≤ 47% vì Sonadezi giữ 52,75% [CYCLE_BLOCK D]. Size thực thi được rất nhỏ.

## 6. Điều kiện ĐỔI verdict
- Có trigger thật (mất khách thuê lớn, rút hoặc rút ngắn thời hạn dự án, phí thuê đất Đồng Nai đội mạnh) **và** PB ≤ 1,1x (~17.800 đ) ⇒ chạy lại §2.5.
- Biên gộp năm 2026 BCTC < 35% **và** LN lõi giảm 2 quý liền ⇒ coi là sốc cấu trúc (mix xăng dầu, giá thuê), không phải chu kỳ.

## 7. ⚠️ WARNING pháp lý/quản trị (chỉ cảnh báo, luật 2026-09-27)
- ⚠️ Bảng giá đất Đồng Nai 2026 (dự thảo tăng 1,1–9 lần) có thể đẩy tiền thuê đất phải nộp lên. Hiệu lực và tác động lên SZL chưa xác minh [CYCLE_BLOCK D, WEB-6].
- ⚠️ Thời hạn dự án KCN (~2053) chưa xác minh bằng giấy phép.
- ⚠️ Capex Long Phước ~920 tỷ, lớn hơn VCSH 784 tỷ, làm rủi ro thực thi và đòn bẩy tăng. Không phát hiện vụ việc pháp lý nào của pháp nhân trong nguồn đã đọc.

## 8. Lệch dữ liệu giữa các nguồn
| Mục | Nguồn A | Nguồn B | Xử lý |
|---|---|---|---|
| Biên gộp Q2/26 | BQ `GPM_P0` 38,5% | [BC-1] 34,8% | dùng BC; Q3 chưa đo |
| LNST Q2/26 | BQ 30,6 tỷ | [BC] "gần 32 tỷ" | lệch 2–4%, có thể do CĐ không kiểm soát; chưa xử lý |
| BVPS Q2/26 | BQ 15.905 đ (theo SLCP sau thưởng tháng 9 ⇒ nhìn trước) | VCSH/28,35 triệu CP | tự tính VCSH |
| Nợ phải trả 30/9 | BQ StLiab+LtLiab 1.580,2 tỷ | [BC-Q3] ">1.580 tỷ" | khớp |
| Tiền 30/9 | BQ `Cash_P0` 171,2 tỷ | [BC-Q3] ">171 tỷ" | khớp; tiền gửi có kỳ hạn riêng chưa đo |

## H. Đối chiếu khối chu kỳ với BCTC Q3 (không sửa khối gốc)
| Mục | Khối mù nói | Q3/2026 cho thấy | Khớp / lệch | Đổi verdict? |
|---|---|---|---|---|
| Loại ngành | annuity, có đuôi chu kỳ nhẹ; cổ tức nhận lệch quý | DT +12% đều; LN quý dao động do cổ tức 36 tỷ | **Khớp**. Khối đã cảnh báo đúng nguồn nhiễu | Không |
| A biên | biên LNST p36; biên gộp BCTC đang co | biên LNST TTM tăng lên 31,8% (179,9/565,9 [UL]) nhưng do cổ tức; biên gộp BCTC Q3 chưa đo (BQ 38,8% không tin được) | **Chưa chấm được** biên gộp. Biên LNST lệch, nhưng lệch vì khoản một lần, không phải lõi | Không |
| C pha | N/A | không có sốc nào | Khớp | Không |
| D neo | Long Phước, quỹ đất, bảng giá đất | Long Phước đã chi 345/920 tỷ, vận hành cuối 2026; vay +46% | **Khớp**, Q3 bổ sung số capex | Không |
| E PE chuẩn hoá | ex-cash 15,0x; PB 1,77x | 14,5x; 1,73x | **Khớp** (chênh <4%) | Không |
| F | biên gộp năm 2026 < 38% | 9T chưa có LN gộp BCTC; nếu hiệu chỉnh BQ theo độ lệch Q2 (−3,7pp) thì Q3 ~35% [UL] ⇒ nghiêng về HIT | đang chờ, due 2027-01-31 | — |
- **Verdict có phụ thuộc khối chu kỳ không?** Một phần, qua E (PB p78, PE chuẩn hoá ~15x). Nhưng tiền đề "không có trạng thái sợ hãi" đã đủ để loại. **Bỏ khối chu kỳ, verdict vẫn giữ NON: có.**
- Đóng góp riêng của khối: chặn đọc nhầm "LN Q3 kỷ lục, PE 7,6x" nhờ quy tắc LN chuẩn hoá và cảnh báo cổ tức lệch quý được viết TRƯỚC khi thấy Q3. Nhưng bước 1 đã vô tình lộ số Q3, kể cả "cổ tức ~36 tỷ", nên không chứng minh được điểm này là mù.

## Sổ chấm
- Entry đề xuất: `CYC-SZL-20261026`, **blind: no** (lộ số Q3 ở bước 1; người viết bước 2 biết verdict cũ). Theo README §3, entry này KHÔNG tính vào cổng. Dự báo F vẫn chấm được tại 2027-01-31 từ BCTC Q4/2026.

---

## I. So với báo cáo cũ (`dd_SZL_20261026/REPORT.md`) — viết SAU khi verdict trên đã ghi
Verdict cũ (job `Taylor_20261026_012527`) là **NON**. Verdict mới cũng **NON**: **KHÔNG ĐỔI**. Hai bản cùng dựa trên lý do chính:
không có trigger (giá điều chỉnh −6%, cú −46% chỉ là ex-right) và PB 1,73 > 1 nên §2.5 #4 trượt. Cả hai cùng tách LN Q3
thành ~34 tỷ lõi cộng ~36 tỷ cổ tức.

**Khác nhau quan trọng — định giá ngược chiều nhau dù cùng verdict:**
| Điểm | Báo cáo cũ | Bản mù (khối E) | Đánh giá |
|---|---|---|---|
| LN chuẩn hoá | 150–170 tỷ (lõi 125–135 + cổ tức 25–40), PE **8,0–9,1x**, "hợp lý, không rẻ" | 103 tỷ (trung vị 2016–25), PE ex-cash **~15x**, "đắt hơn lịch sử" | Quy tắc mẫu "trung vị LNST ≥1 chu kỳ" **lệch xuống** với annuity đang tăng trưởng: trung vị kéo theo các năm 89–105 tỷ cũ, trong khi lõi hiện tại là ~130 tỷ. Mẫu nên cho phép "LN lõi TTM trừ khoản lệch quý" với annuity. Ở đây không đổi verdict vì PB vẫn trượt, nhưng với một mã gần sàn thì sẽ đổi |
| Danh mục đầu tư chéo | SZC/SZB theo **thị giá** ~595 tỷ ≈ **44% vốn hoá**, đưa vào SOTP | chỉ có giá sổ 398 tỷ, "chưa trừ khỏi tử số" | Báo cáo cũ đúng hơn. Khối mù BỎ SÓT cấu phần lớn nhất của SOTP |
| Pháp lý | ⚠️ Trưởng BKS công ty mẹ SNZ bị khởi tố 05/2026; luân chuyển tiền trong tập đoàn | không nêu | Khối mù BỎ SÓT; §7 bản mới cũng sót (WARNING, không đổi verdict) |
| Free float | < 25% (nhóm cổ đông lớn > 75%) | ≤ 47% (chỉ tính SNZ) | Báo cáo cũ đúng hơn; size thực thi còn nhỏ hơn §5 |
| Biên gộp | không nêu riêng (chỉ nói QLDN +33%, lõi Q2 giảm YoY) | **biên gộp BCTC 39,3% → 34,8%**, do mix xăng dầu và thuê đất −17%; có dự báo F bác bỏ được | Khối mù BẮT được một xu hướng báo cáo cũ không nêu, và là chỉ báo duy nhất chấm được về sau |
| Neo có ngày | Long Phước cho thuê 04/2027; 48 vs 75 ha | thêm: hạn dự án ~2053 (chưa xác minh), bảng giá đất Đồng Nai 2026 | bổ sung nhau |

**Lệch thời điểm cổ tức nhận năm 2025:** báo cáo cũ dẫn ABS là Q4/2025 (19 tỷ). §2 bản này ghi Q2/2025 theo một tóm tắt tìm kiếm. Bản thân CYCLE_BLOCK (E: "Q4/25 +112% nhờ thu nhập tài chính [BC-3]") ủng hộ Q4. ⇒ **§2 bản này nhiều khả năng sai ở điểm đó** (không đổi kết luận "lệch quý, thu nhập năm"); không sửa §2 vì verdict đã khoá trước khi đọc báo cáo cũ.

**Tổng kết phép thử:** khối chu kỳ (kể cả mù) **không đổi verdict** SZL. Với một annuity không có trigger, verdict quyết bằng tiền đề "có sợ hãi không" và PB, không bằng pha chu kỳ, đúng như README §4 dự đoán. Khối chỉ thêm được một thứ báo cáo cũ thiếu: chỉ báo biên gộp co và dự báo F có ngày chấm. Nó bỏ sót 3 thứ báo cáo cũ có (SOTP theo thị giá, WARNING công ty mẹ, free float thật). Quy tắc LN chuẩn hoá của mẫu làm định giá lệch ~1,7 lần với annuity tăng trưởng, nên đề xuất sửa mẫu. Phép thử bị nhiễm: `blind: no`.

## Nguồn
- [BQ] `tav2_bq.ticker_financial` SZL 2024Q3–2026Q3 (Release_Date 2026Q3 = 2026-10-20); `tav2_bq.ticker` Price/Close/Volume đến 2026-10-23.
- [BC-Q3] https://doanhnhan.baophapluat.vn/sonadezi-long-thanh-szl-bao-lai-quy-3-cao-ky-luc-hoan-thanh-90-muc-tieu-ca-nam.html (đăng 21/10/2026, truy cập 26/10/2026)
- [WEB-Q3 tóm tắt] tóm tắt kết quả WebSearch 26/10/2026 (cổ tức 2025 95%, kế hoạch 2026 20%); trích từ https://mekongasean.vn/sonadezi-long-thanh-sap-phat-hanh-gan-20-trieu-co-phieu-tra-co-tuc-58373.html, chưa mở trang
- [BC-1], [WEB-6] và các nguồn còn lại: xem `CYCLE_BLOCK.md` § Nguồn.
