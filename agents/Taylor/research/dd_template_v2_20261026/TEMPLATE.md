# MẪU DD CHUẨN — sleeve discretionary (fear-buy / special-situation) · v2 2026-10-26

> Mẫu do job `Taylor_20261026_045054` dựng, user duyệt ý tưởng 26/10/2026 11:50 ICT. Khung tiêu chí vẫn là
> `agents/Taylor/research/calculated_fear_state_backstop.md` §2 (nhóm a) và §2.5 (nhóm b/c/d). Mẫu này KHÔNG đổi
> tiêu chí. Nó chỉ chuẩn hoá thứ tự làm việc và thêm **KHỐI CHU KỲ** viết mù.
> Đây là công cụ kỷ luật và so sánh, KHÔNG phải tín hiệu. Chưa có bằng chứng triển vọng ngành thêm alpha (README §2).

---

## V2 — BỔ SUNG SAU PHÉP THỬ MÙ NHIỄM 26/10 (GHI ĐÈ v1 NẾU MÂU THUẪN)
1. **Bước 1 giao cho agent chưa từng làm mã đó và chưa đọc DD/KB/working memory về mã đó.** CẤM mở `mike/kb/projects/*`, `mike/kb/memory/*`, `agents/Taylor/research/dd_*`, bus finding về mã. Nếu mã đã có case cũ trong KB, vẫn cấm; ghi `da_doc_DD_cu_cua_ma_nay: không`.
2. **Bước 1 CẤM WebSearch/WebFetch về kết quả kinh doanh quý Q, khuyến nghị/giá mục tiêu của CTCK, hay tin sau ngày chốt dữ liệu của mã.** WebSearch về ngành/chính sách chỉ được dùng với từ khoá không chứa tên mã + "quý 3"/"Q3"/"khuyến nghị"/"giá mục tiêu"; nếu tóm tắt lộ số Q hoặc khuyến nghị thì ghi `blind: no`.
3. **Bước 1 PHẢI đọc bảng cân đối + thuyết minh BCTC quý Q−1 (hoặc BCTC năm kiểm toán) GỐC**, không chỉ BQ: `Cash_P0` của BQ thiếu tiền gửi giữ đến đáo hạn (DDV: thiếu 1.208 tỷ; NNC: 322 tỷ; NT2: 12 so 5.374 tỷ), và BQ lưu số CHƯA điều chỉnh soát xét ở quý đó (số đã restate nằm ở cột `NP_P1` của dòng quý sau).
4. **Mục D thêm dòng bắt buộc:** cổ đông chi phối là ai, họ có nhu cầu vốn / xung đột lợi ích với cổ tức không (ví dụ công ty mẹ đang đầu tư dự án lớn, không chia cổ tức).
5. **Mục E:** ngoài trung vị nhiều năm, ghi thêm lợi nhuận lõi TTM đã trừ khoản lệch quý (cổ tức nhận, bù trừ một lần). Với mã tăng trưởng, trung vị nhiều năm lệch xuống (SZL: ~1,7 lần), nên ghi cả hai và nêu chênh lệch.
6. **Mục F:** chấm bằng BCTC năm kiểm toán hoặc BCTC quý gốc, không `SUM(NP_P0)` của BQ.
7. **Gỡ phụ lục 5 mã khỏi README** (đã làm trong v2).

---

## THỨ TỰ LÀM VIỆC — BẮT BUỘC, không đảo

| Bước | Việc | ĐƯỢC đọc | CẤM đọc |
|---|---|---|---|
| **0** | Header + xác định pháp nhân, ngành, nhóm trigger dự kiến | Tên công ty, mã, ICB, BCTN gần nhất (phần mô tả kinh doanh, KHÔNG đọc phần kết quả năm), CBTT pháp lý | — |
| **1** | **KHỐI CHU KỲ (mục A–F)** → lưu thành file riêng `CYCLE_BLOCK.md` → khoá bằng md5 + git commit | Feed hàng hoá/vĩ mô; `ticker_financial` các quý **≤ Q−1** (Q = quý mới nhất đã công bố); BCTC kiểm toán năm **trước** Q; tin chính sách/hạ tầng/giấy phép | BCTC quý Q; bài báo, note CTCK hay tin bình luận về KQKD quý Q; `data/discretionary_funnel_latest.json` (có `g_qoq`, `drop_pct`); DD cũ của chính mã đó; verdict của bất kỳ ai |
| **2** | BCTC quý Q, phân rã LN, bảng cân đối, dòng tiền, định giá | Mọi thứ | Sửa `CYCLE_BLOCK.md` (muốn đổi thì ghi ở mục **H**) |
| **3** | Verdict theo §2 / §2.5 | Mọi thứ | — |
| **4** | Mục **H** đối chiếu khối chu kỳ với BCTC; ghi dự báo F vào sổ chấm | — | — |

**Bước 1 làm bởi ai:** nếu người viết ĐÃ đọc BCTC quý Q hoặc DD cũ của mã (ví dụ chạy lại 5 mã 26/10) thì bước 1
phải giao cho một phiên/agent mới chưa đọc chúng. Người viết tự khai ở dòng dưới; khai "không" vẫn được nộp, nhưng
sổ chấm ghi `blind: no` và entry đó **không tính** vào cổng đánh giá (README §3).

```
BLIND_ATTESTATION
  da_viet_truoc_khi_doc_BCTC_quy_Q : có / không
  da_doc_DD_cu_cua_ma_nay          : có / không
  da_biet_verdict_truoc            : có / không
  quy_Q (mới nhất đã công bố)      : 20xxQn       ngày công bố: yyyy-mm-dd
  du_lieu_tai_chinh_dung_den_quy   : 20xxQ(n-1)
  cycle_block_md5                  : <md5sum CYCLE_BLOCK.md>
  cycle_block_commit               : <git hash, commit TRƯỚC mọi file bước 2>
  thoi_diem_khoa (ICT)             : yyyy-mm-ddTHH:MM+07:00
```
Kiểm được bằng cơ học: commit của `CYCLE_BLOCK.md` phải có timestamp sớm hơn commit đầu tiên chứa file BCTC Q
(`src/*`) và `REPORT.md`. Lệch ⇒ ghi `blind: no`.

---

# DD <MÃ> (<tên công ty>) — sleeve discretionary (job `<job_id>`, yyyy-mm-dd)

> READ-ONLY, không phải khuyến nghị mua — user quyết. Giá tham chiếu **<giá> đ (đóng cửa <ngày>, BQ `ticker`)**.
> Nhãn nguồn: **[BQ]** · **[BCTC]** bản gốc · **[BC]** báo chí trích BCTC · **[CTCK]** · **[FEED]** file trong
> `data/` (ghi tên) · **[UL]** ước lượng của tôi (ghi công thức). Số không đo được gắn **(ước lượng)** ngay cạnh.

## KHỐI CHU KỲ (copy nguyên văn từ `CYCLE_BLOCK.md` đã khoá — tối đa ~1 trang)

**Loại ngành:** chu kỳ hàng hoá / chu kỳ cầu đầu tư / phân bổ theo chính sách / annuity hợp đồng / không chu kỳ.
Nếu "annuity" hoặc "không chu kỳ": vẫn điền A, D, E, F. Ghi B và C là `N/A — <lý do 1 dòng>`.

**A. Biên hiện tại so với lịch sử CHÍNH mã** (dữ liệu đến Q−1)
- Chỉ số: biên gộp TTM (4 quý trượt) và biên LNST TTM. Chuỗi phải phủ **≥ 1 chu kỳ đáy→đỉnh** (thường ≥ 8 năm).
  Ghi rõ cửa sổ: `20xxQ1–20xxQn, N quý, số chu kỳ thấy được = k`.
- Kết quả: biên gộp TTM = x%, phân vị **p** trong lịch sử chính mã · biên LNST TTM = y%, phân vị **p**.
  Nếu có đổi mô hình (mỏ mới, nhà máy mới, hết khấu hao) thì cắt chuỗi tại điểm đổi và ghi lý do.
- Nguồn: `tav2_bq.ticker_financial` (`Revenue_P0`, `NP_P0`, `GPM_P0`). ⚠️ `GPM_P0` từng KHÔNG khớp biên gộp
  quý của BCTC (DDV Q3/26: BQ 0,10 vs BCTC 3,7%; SAS: 0,682 vs 65%) ⇒ kiểm `GPM_P0` với ≥ 1 quý BCTC kiểm toán
  trước khi tính phân vị; lệch thì dùng biên LNST (`NP/Revenue`) và ghi lệch.
- Với k ≤ 3 chu kỳ thì phân vị là **mô tả**, không phải thống kê. Không viết p-value.

**B. Giá đầu ra và đầu vào chính so với 5–10 năm**
| Biến | Vai trò (ra/vào, % giá vốn nếu biết) | Giá trị gần nhất | Trung vị 5 năm | Phân vị 10 năm | Nguồn |
|---|---|---|---|---|---|
| | | | | | |
- Feed có sẵn (CANONICAL theo `kb/data_registry/feeds/`): WB CMO tháng từ 2006-04 — `data/dap_monthly.csv`,
  `urea_`, `brent_`, `iron_ore_`, `rubber_`, `maize_`, `soybean_meal_`, `sugar_`, `caustic_soda_monthly.csv`;
  `data/rubber_weekly.csv`; `data/hog_price_vn.csv`; `data/bdi_daily_real.csv`; `data/oni_index.csv` (ENSO,
  proxy thủy văn cho điện); `data/vcb_fx_rate.csv`. Lãi suất/tín dụng: `kb/data_registry/macro/`.
- **Không có feed** (phải tự lấy nguồn ngoài, ghi URL + ngày truy cập; nhãn [WEB]): lưu huỳnh, NH3, đá xây dựng,
  HRC/thép VN, than, khí, Qc/Qm điện, lượt khách sân bay, giá thuê KCN. Biến chi phối mà không có chuỗi ≥ 5 năm
  ⇒ ghi `CHUỖI THIẾU`, và mục C chỉ được kết luận "giữa / không xác định", không được kết luận "đáy" hay "đỉnh".

**C. Pha chu kỳ: ĐÁY / GIỮA-LÊN / ĐỈNH / GIỮA-XUỐNG / KHÔNG XÁC ĐỊNH**
- Kết luận + **2 bằng chứng ủng hộ + 1 bằng chứng chống** (bắt buộc có bằng chứng chống).
- Mặc định cơ học, chỉ được lệch nếu nêu lý do: phân vị A **và** B (biến đầu ra hoặc spread) ≥ 80 ⇒ ĐỈNH;
  cả hai ≤ 20 ⇒ ĐÁY.
- Ghi rõ cơ chế của cú sốc: **cầu/giá bán** sập, hay **chi phí đầu vào** tăng khi giá bán vẫn cao. Hai loại đáy
  này khác nhau; so PB đáy chỉ có nghĩa giữa các đáy CÙNG loại.
- Cung: công suất mới của ngành/đối thủ trong 12–24 tháng, tồn kho ngành (nếu có số).

**D. Neo chính sách và rủi ro cấu trúc** — mỗi dòng PHẢI có NGÀY
| Neo/rủi ro | Loại (giấy phép / hợp đồng / hạ tầng / phân bổ / thuế-phí) | Ngày hiệu lực hoặc hết hạn | Chu kỳ hay cấu trúc? | Nguồn |
|---|---|---|---|---|
- Câu hỏi phải trả lời: dòng tiền lõi có **thời hạn** không (giấy phép mỏ, PPA, hợp đồng mặt bằng)? Nếu có ⇒ mục E
  định giá theo dòng tiền có thời hạn, không dùng PE vĩnh viễn.
- Rủi ro "mất vị trí/giấy phép" thuộc danh sách LOẠI của §2.5, kể cả khi số tài chính đang đẹp.

**E. PE/PB trên LN chuẩn hoá** (dữ liệu đến Q−1, bảng cân đối dùng quý Q−1 hoặc BCTC năm kiểm toán)
- LN chuẩn hoá = **trung vị LNST năm qua ≥ 1 chu kỳ** (cùng cửa sổ A), HOẶC biên giữa chu kỳ × doanh thu ở công
  suất hiện tại. Chọn một cách, ghi lý do. Loại khoản một lần đã biết (bù hợp đồng, hoàn nhập, cổ tức nhận lệch quý).
  **CẤM** dùng quý đơn lẻ ×4 hoặc TTM thô.
- PE_chuẩn hoá ex-cash = (vốn hoá − net cash) / (LN chuẩn hoá − lãi tiền gửi sau thuế).
  ⚠️ `Cash_P0` của BQ có thể **thiếu tiền gửi có kỳ hạn/giữ đến đáo hạn** (NT2: 12 tỷ vs BCTC 5.374 tỷ; DDV: thiếu
  1.207,8 tỷ) ⇒ net cash lấy từ BCTC; nếu dùng BQ thì ghi rõ. `Debt_Eq_P0` = tổng nợ phải trả/VCSH, KHÔNG phải nợ vay.
- PB trên tài sản hữu hình. So với PB tại các đáy CÙNG loại cú sốc (mục C) của chính mã.

**F. DỰ BÁO CÓ THỂ BÁC BỎ** (một dự báo chính về NGÀNH/BIÊN, không phải giá cổ phiếu)
```
FORECAST
  indicator   : <chỉ báo, đo được cơ học, vd "biên gộp TTM <MÃ> theo BCTC">
  source      : <file/bảng/cột hoặc tài liệu cụ thể sẽ dùng để chấm>
  baseline    : <giá trị tại as-of, dữ liệu đến Q−1>
  call        : <lớn hơn / nhỏ hơn> <ngưỡng>       (hoặc: sự kiện X xảy ra / không xảy ra trước ngày)
  horizon     : quý 20xxQm (2–3 quý sau Q)
  due_date    : <ngày công bố BCTC dự kiến của quý m + 10 ngày>
  p           : <xác suất chủ quan 0..1>
  persistence : <kết quả nếu chỉ báo GIỮ NGUYÊN phía hiện tại — dùng làm baseline chấm>
  void_if     : <điều kiện huỷ: đổi chuẩn mực kế toán, M&A, đình chỉ giao dịch...>
```
Một dự báo tốt có thể sai rõ ràng. "Biên sẽ biến động" không phải dự báo.

---

## 0. Verdict (viết SAU bước 2): QUALIFY / AMBIGUOUS / NON

| Tiêu chí (§2 hoặc §2.5) | Phán quyết | Bằng chứng chính | Có dùng khối chu kỳ? (mục nào) |
|---|---|---|---|
| | | | |

Định giá theo kịch bản (một dòng), điều kiện đổi verdict (một dòng), pháp lý (một dòng).

## 1. Giả thuyết của user / của tôi và kiểm chứng
## 2. Phân rã LN quý Q — cái gì bền, cái gì một lần
## 3. Bảng cân đối, dòng tiền (CF_OA vs NP), cổ tức
## 4. Định giá — trên LN chuẩn hoá (dùng lại E, cập nhật bảng cân đối quý Q ở cột riêng)
## 5. Thanh khoản và size tối đa thực thi được (ADV 20 phiên, trung vị, free float)
## 6. Điều kiện ĐỔI verdict (giá và chỉ báo cụ thể)
## 7. ⚠️ WARNING pháp lý/quản trị (chỉ cảnh báo; luật 2026-09-27)
## 8. Lệch dữ liệu giữa các nguồn (bảng Nguồn A / Nguồn B / Xử lý)

## H. Đối chiếu khối chu kỳ sau khi đọc BCTC (viết ở bước 4, KHÔNG sửa khối gốc)
| Mục | Khối mù nói | BCTC quý Q cho thấy | Khớp / lệch | Nếu lệch: đổi gì trong verdict? |
|---|---|---|---|---|
| A biên | | | | |
| C pha | | | | |
| E PE chuẩn hoá | | | | |
- Verdict có phụ thuộc mục nào của khối chu kỳ không? Nếu bỏ khối chu kỳ, verdict có giữ nguyên không? (ghi có/không)

## Sổ chấm
- Entry đã gửi Mike để ghi vào sổ đề xuất (README §3): `CYC-<MÃ>-<yyyymmdd>`, `blind: yes/no`.

## Nguồn
