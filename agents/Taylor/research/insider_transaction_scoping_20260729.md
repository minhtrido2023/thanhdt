# Insider transaction (`tav2_bq.insider_transaction`) — scoping nghiên cứu #9

**Job:** `Taylor_20260729_015830` · **Ngày:** 2026-07-29 · **Tác giả:** Taylor
**Bối cảnh:** hướng #9 "Giao dịch nội bộ" trong `factor_gap_audit_20260718.md` từng xếp
**nhóm B — cần dữ liệu trước** ("thú vị nhất về cấu trúc thị trường"). bq_admin đã thêm bảng
2026-07-27 ⇒ mở khoá được bước đầu tiên.
**Trạng thái:** RESEARCH/THIẾT KẾ. **Chưa wire production, chưa qua quant-skeptic** (đúng phạm vi
dispatch). Artifact: `mike/agents/Taylor/exp_insider/{panel.sql,panel2.sql,ic_analysis.py,
gate_analysis.py,panel.csv,panel2.csv,ic_results.csv}`.

---

## TL;DR — 3 kết luận

1. **Lợi thế cấu trúc "công bố TRƯỚC khi giao dịch" của VN (TT96/2020) — KHÔNG backtest được từ
   bảng này.** Bảng là **snapshot trạng thái**, không phải event-log: khi một sự kiện chuyển
   `Đăng ký → Đã thực hiện xong`, `public_date` **bị ghi đè** từ ngày công bố Ý ĐỊNH sang ngày
   báo cáo KẾT QUẢ. 50.934/52.155 sự kiện đã hoàn tất ⇒ **ngày công bố ý định đã mất vĩnh viễn**.
   Muốn khai thác cửa sổ pre-trade phải **tự snapshot bảng theo ngày TỪ NAY TRỞ ĐI** (dự án dữ
   liệu mới, thu hoạch sớm nhất sau ~12-18 tháng tích luỹ).
2. **Hướng FACTOR: YẾU, không đề xuất theo đuổi.** IC thô cao nhất 0,0191 (t=3,12);
   **sau khi trung tính hoá theo 1/PE + 8L rating chỉ còn 0,0129-0,0139** — nhỏ hơn **một bậc độ
   lớn** so với 1/PE (IC +0,125). Đúng cảnh báo đã ghi trước trong `factor_gap_audit`. Riêng
   **phía MUA chết hẳn OOS** (S9 buy-intensity: IC_OOS −0,004).
3. **Hướng GATE (due-diligence): CÓ NỘI DUNG THẬT, đề xuất theo đuổi.** Bán ròng nội bộ **không
   làm giảm return TRUNG BÌNH** của rổ ứng viên (t=−0,74, không có ý nghĩa) nhưng **làm dày ĐUÔI
   TRÁI rõ rệt**: P(fwd60 < −20%) = 19,7% với cờ "nội bộ bán ≥1% CP lưu hành trong 90 ngày" so
   với 11,3% nền (**lift 1,75×, z=12,9**), sống sót khi phân tầng theo vốn hoá/turnover và **ổn
   định IS↔OOS**. Đây đúng chữ ký của một **cổng rủi ro**, không phải factor return — cùng họ với
   `anomaly_gate` hiện có.

---

## §1 — Data profiling (đã đăng ký registry TRƯỚC khi dùng)

Đã tạo `mike/kb/data_registry/fundamentals/insider_transaction.md` (+ dòng ở `fundamentals/index.md`
+ mục `CHANGELOG.md`), theo `coding_guidelines.md` §9. Tóm tắt các phát hiện quyết định:

### 1.1 Tách 3 nhóm — dùng `event_code`, KHÔNG dùng heuristic person_id

| `event_code` | Nghĩa | Dòng | `trader_person_id` |
|---|---|---:|---|
| `DDIND` | Giao dịch cá nhân (người nội bộ) | 28.828 | 100% CÓ |
| `DDRP` | Giao dịch người liên quan | 6.795 | 100% CÓ |
| `DDINS` | Giao dịch **tổ chức** (SCIC, quỹ ngoại…) | 16.532 | **100% NULL** |

`trader_person_id IS NULL` ⟺ `DDINS` (tương quan 100%) — nhưng `event_code` còn tách được
`DDIND` vs `DDRP`. **Chỉ `DDIND`(+`DDRP`) mới là "true insider"**; `DDINS` là FLOW tổ chức, ý
nghĩa hoàn toàn khác, không trộn vào tín hiệu inside-info (đúng như dispatch cảnh báo).

- **`role_name` KHÔNG phải chức danh** — chứa TÊN NGƯỜI, trùng `trader_name`/`relative_name`
  ("Bùi Minh Tuấn", "Vợ Phạm Anh Tuấn"). **Bảng không có field chức vụ (CT/TGĐ/KTT)** ⇒ không thể
  phân tầng theo cấp bậc (một trong những trục mạnh nhất của literature insider ở DM) nếu không
  có nguồn khác. `relative_name` của `DDRP` nhúng tiền tố quan hệ trong chuỗi — parse được nhưng
  chưa chuẩn hoá.

### 1.2 Điểm chí tử: bảng là SNAPSHOT, `public_date` bị ghi đè

`id` UNIQUE 52.155/52.155; `ingested_at` chỉ có 72 giá trị **trong 81 giây ngày 2026-07-27** ⇒ mới
đúng **1 lần backfill**, không có bằng chứng cron refresh.

| `trade_status` | dòng | trung vị `public_date − start_date` | trung vị `public_date − end_date` | `public_date < start_date` |
|---|---:|---:|---:|---:|
| `Đăng ký` | 1.190 | **−3 ngày** | −28…−31 ngày | 1.120/1.190 |
| `Đã thực hiện xong` | 50.934 | +7…+16 ngày | **+5 ngày** | 63…15 (nhiễu) |

Đọc thẳng: dòng còn ở trạng thái `Đăng ký` mang ngày công bố **ý định** (trước cửa sổ giao dịch
~3 ngày — đúng TT96/2020); dòng đã `Đã thực hiện xong` mang ngày **báo cáo kết quả** (~5 ngày sau
khi cửa sổ đóng). Cùng một `id`, cùng một field ⇒ **giá trị cũ đã bị ghi đè**, không có cột nào
lưu lại ngày đăng ký gốc (`display_date1` = `public_date` ở phần lớn dòng, không cứu được).

**Hệ quả cho câu hỏi trong dispatch ("Registration xuất hiện bao lâu trước Done, bao nhiêu %
Registration không bao giờ thành Done"):**
- Câu 1 trả lời được **chỉ trên cohort đang treo**: đăng ký công bố ~3 ngày trước khi cửa sổ mở,
  cửa sổ dài ~28-31 ngày. Với cohort đã hoàn tất thì chỉ **ước lượng** được (`start_date − 3`),
  không phải sự thật point-in-time ⇒ **không dùng cho backtest**.
- Câu 2: `trade_status='Không thực hiện được'` **chỉ có 2 dòng/11 năm** ⇒ field này vô dụng. Tỷ lệ
  không-thực-hiện thật nằm ở `share_acquire`:

| trong 31.505 dòng Done có `share_register>0` | dòng | % |
|---|---:|---:|
| khớp **0** cổ phiếu (đăng ký rồi không mua/bán gì) | 4.646 | **14,7%** |
| khớp **một phần** | 8.567 | 27,2% |
| khớp đủ/vượt | 18.292 | 58,1% |

(trung vị fill = 1,0; p25 ≈ 0,38-0,44). Thêm: **19.393/50.934 dòng Done có `share_register=0`**
(không mang lượng đăng ký sang) ⇒ chỉ đo được fill-ratio trên ~62% mẫu.

### 1.3 Ba bẫy kế toán khác (đã ghi registry)

1. `share_acquire` là lượng **có dấu**, nhưng **~2.500 dòng Bán KHÔNG âm** ⇒ luôn tự áp dấu theo
   `action_code`.
2. `share_before`/`share_after` **không tin được ở dòng `Đăng ký`** (606/733 dòng Mua-Đăng ký lại
   có `after < before`). Ở dòng Done, `|after − before| = |share_acquire|` chỉ khớp 91% phía Mua.
3. **Cụm ≥5 người cùng MUA một mã trong cùng `public_date` = 327 sự kiện / 2.525 dòng = 15,7% số
   dòng Mua**, trong khi phía Bán chỉ 29 sự kiện / 176 dòng (1,5%). Bất đối xứng này là **dấu vân
   tay ESOP/phát hành ưu đãi**, không phải mua chủ động (ví dụ FPT 2026-06-29: 6 lãnh đạo cùng
   "mua" cùng ngày, `start_date = end_date`).

### 1.4 Độ phủ trên universe đầu tư (`universe_pit`, rebalance cuối tháng)

| Năm | mã/tháng | % mã có ≥1 sự kiện nội bộ 180 ngày | % net-mua | % net-bán |
|---|---:|---:|---:|---:|
| 2015 | 289 | 44,8% | 17,6% | 21,1% |
| 2018 | 379 | 51,9% | 20,7% | 25,0% |
| 2021 | 588 | 55,8% | 14,0% | 35,8% |
| 2024 | 481 | 40,3% | 14,8% | 21,1% |
| 2026 | 434 | 35,5% | 17,5% | 13,9% |

Độ phủ tốt (35-56% universe có tín hiệu) — **không phải vấn đề coverage như #11 analyst revision**.

---

## §2 — Hướng FACTOR: IC panel sơ bộ (KHÔNG đề xuất theo đuổi)

**N trials khai báo TRƯỚC = 6 biến thể × 1 horizon chính (fwd20)**, fwd60 chỉ tham khảo.
Không sweep tham số: cửa sổ 90/180 ngày chọn trước theo lý thuyết (kết quả công bố ~5 ngày sau
`end_date`). Panel: 49.059 quan sát · 132 tháng (2015-06 → 2026-06) · trung bình 366 mã/tháng ·
universe = `universe_pit` in_universe (đúng `_universe-selection-rules.md`, **không** `ticker_prune`).
Ngày "biết được" = `public_date` của dòng Done (an toàn, đã là ngày báo cáo kết quả).

### Kết quả (Spearman IC cắt ngang, trung bình theo tháng)

| Tín hiệu | horizon | IC thô (t) | **IC sau trung tính 1/PE + 8L** (t) | IC_IS 2015-19 | IC_OOS 2020+ |
|---|---|---:|---:|---:|---:|
| S2 net **người** mua−bán, 90d | fwd20 | 0,0191 (3,12) | **0,0129 (2,17)** | 0,0159 | 0,0108 |
| S7 = S2 **đã khử ESOP-bulk** | fwd20 | 0,0197 (3,25) | **0,0139 (2,37)** | 0,0162 | 0,0123 |
| S1 net người, 180d | fwd20 | 0,0139 (2,23) | 0,0091 (1,52) | 0,0069 | 0,0106 |
| S3 net CP / CP lưu hành | fwd20 | 0,0104 (1,73) | 0,0047 (0,77) | 0,0001 | 0,0079 |
| S4 net CP / ADV | fwd20 | 0,0108 (1,86) | 0,0045 (0,76) | −0,0006 | 0,0082 |
| S8 cường độ **BÁN** (âm) | fwd60 | 0,0252 (4,66) | **0,0213 (4,04)** | 0,0028 | 0,0347 |
| S9 cường độ **MUA** (khử ESOP) | fwd60 | 0,0002 (0,04) | **−0,0062 (−1,10)** | −0,0006 | −0,0103 |

**Đọc kết quả:**
- **Trung tính hoá theo 1/PE ăn mất ~30% IC** (0,0191 → 0,0129) — đúng cảnh báo đã pre-register.
  Thêm 8L rating gần như không đổi thêm (rating là gate nhị phân, ít trùng).
- **Ngay cả IC còn lại cũng quá nhỏ để làm factor**: 0,013-0,014 so với 1/PE 0,125 ⇒ nhỏ hơn
  **một bậc độ lớn**. Với chi phí giao dịch VN và turnover của một factor xếp hạng, biên này gần
  như chắc chắn bị ăn hết.
- **Khử ESOP giúp nhưng không cứu được**: S2→S7 chỉ +0,001 IC. Kiểm tra trực tiếp phía mua
  (spread fwd20 demeaned): mua-thuần +0,261% (có ESOP) → +0,298% (đã khử) so với không-tín-hiệu
  +0,064%. Có hướng đúng, độ lớn không đáng kể.
- **Toàn bộ nội dung nằm ở phía BÁN, không phải phía MUA.** Spread theo nhóm (fwd20 demeaned):
  net-bán **−0,184%** (t=−1,52) · không-tín-hiệu +0,077% · net-mua-1-người +0,075% · net-mua-≥2
  **−0,064%** ⇒ **không đơn điệu ở phía mua**. S9 (mua thuần, đã khử ESOP) có **IC_OOS âm**.
- S8 (cường độ bán) có t=4,04 sau trung tính nhưng **IC_IS ≈ 0,003 vs IC_OOS 0,035** — toàn bộ hiệu
  ứng đến từ 2020+. Theo kỷ luật `context_pack` §Quy chuẩn 5 (bài học Wave1/H8a) đây là **cờ đỏ
  non-stationary**, không phải bằng chứng edge bền ở dạng factor.

### Kết luận hướng FACTOR
**KHÔNG đề xuất đi tiếp thành factor xếp hạng.** Không cần backtest production đầy đủ — IC sau
trung tính đã dưới ngưỡng đáng làm, và phía mua (nửa hấp dẫn của giả thuyết) âm OOS. Nếu sau này
có ai muốn mở lại, điều kiện cần là **nguồn chức danh người giao dịch** (tách CT/TGĐ/KTT khỏi
nhân viên) — trục mạnh nhất trong literature mà bảng hiện tại không có.

---

## §3 — Hướng GATE (due-diligence): có nội dung thật

Giả thuyết: bán ròng nội bộ trước một sự kiện xấu = cảnh báo sớm ⇒ đo bằng **đuôi trái**, không
phải bằng trung bình. Biến mục tiêu: `P(fwd60 < −20%)`. Nền toàn mẫu = 11,3%.

### 3.1 Trung bình KHÔNG có tín hiệu, ĐUÔI thì có

| Mẫu | nhóm | mean xs-fwd60 | t | P(fwd60<−20%) | lift | z |
|---|---|---:|---:|---:|---:|---:|
| Toàn universe | có bán ròng 90d | −0,83% | −3,28 | 14,30% | 1,28× | 8,05 |
| **Rổ ứng viên mua** (8L≤3 & 1/PE top-tercile) | có bán ròng 90d | +1,37% vs +1,50% | **−0,17 (KHÔNG ý nghĩa)** | **13,06% vs 8,25%** | **1,58×** | **6,29** |

Trong đúng rổ ta thật sự mua, bán ròng nội bộ **không làm giảm lợi nhuận kỳ vọng** — nhưng
**gần gấp đôi xác suất sập >20% trong 60 phiên**. Đây là lý do phải dùng nó làm **gate/cờ rủi ro**
chứ không phải tilt return.

### 3.2 Kiểm chứng confound — có phải chỉ là proxy của size/vol không? (KHÔNG)

Phân tầng trong từng tháng, `P(fwd60<−20%)`, cờ = có bán ròng 90d:

| Vốn hoá | lift | z | | Turnover | lift | z |
|---|---:|---:|---|---|---:|---:|
| Q1 (nhỏ) | 1,280× | 4,59 | | Q1 (thấp) | 1,187× | 1,66 |
| Q2 | 1,516× | 6,90 | | Q2 | 1,213× | 2,64 |
| Q3 | 1,251× | 3,45 | | Q3 | 1,120× | 1,90 |
| **Q4 (lớn)** | **1,114×** | **1,53 (KHÔNG ý nghĩa)** | | Q4 (cao) | 1,140× | 2,96 |

Hiệu ứng **sống sót** phân tầng ⇒ không phải chỉ là size/vol trá hình. **Nhưng phải nói thẳng:
cờ YẾU NHẤT đúng ở nhóm vốn hoá lớn nhất (Q4, không có ý nghĩa thống kê)** — mà đó lại là nơi
phần lớn sổ BAL/custom30V đang đứng. Giá trị thực tế của cờ sẽ tập trung ở đuôi mid/small-cap
(LAG, CAPIT pool, fear-buy sleeve).

### 3.3 Ổn định IS ↔ OOS (khác hẳn hướng factor)

| Mẫu | kỳ | n cờ | P(cờ) | P(nền) | lift | z |
|---|---|---:|---:|---:|---:|---:|
| Toàn universe | IS 2015-19 | 2.973 | 12,31% | 10,23% | 1,204× | 3,31 |
| Toàn universe | OOS 2020+ | 5.221 | 15,46% | 11,65% | 1,327× | 7,68 |
| Rổ ứng viên | IS 2015-19 | 512 | 13,87% | 8,27% | **1,678×** | 3,99 |
| Rổ ứng viên | OOS 2020+ | 1.151 | 12,77% | 8,27% | **1,544×** | 4,91 |

**Ổn định cả hai kỳ** — đây là khác biệt cốt lõi so với hướng factor (nơi IS≈0 hoặc OOS âm).

### 3.4 Chọn ngưỡng (N trials = 4, ưu tiên plateau chứ không phải điểm cực trị)

| Định nghĩa cờ | % universe bị bắt | P(sập) | nền | lift | z |
|---|---:|---:|---:|---:|---:|
| nsell>nbuy (gốc) | 17,2% | 14,32% | 11,20% | 1,279× | 7,98 |
| nsell≥2 & nsell>nbuy | 7,3% | 15,61% | 11,43% | 1,366× | 7,36 |
| **bán ≥0,5% CP lưu hành/90d** | 6,8% | 18,37% | 11,25% | **1,632×** | 12,11 |
| **bán ≥1,0% CP lưu hành/90d** | 5,4% | 19,68% | 11,28% | **1,745×** | 12,90 |

0,5% và 1,0% cho kết quả gần nhau (1,63× / 1,75×) ⇒ **plateau, không phải đỉnh nhọn** — dấu hiệu
tốt về robustness. **Đề xuất ngưỡng 1,0% CP lưu hành/90 ngày** (bắt 5,4% universe).

### 3.5 Giới hạn phải nói rõ (đánh giá false-positive)

- **Precision thấp theo nghĩa tuyệt đối**: trong số bị gắn cờ, **~80% KHÔNG sập** (19,7% sập).
  ⇒ **KHÔNG được dùng làm hard-exclude tự động.**
- **Recall rất thấp**: cờ chỉ bắt được **~9%** tổng số ca sập >20% (508/5.614). Đây là cờ
  **chính xác-cục bộ**, không phải máy dò khủng hoảng.
- **Tải review**: ở rổ ứng viên (~80 mã/tháng) ngưỡng gốc bắt 16% (~13 mã/tháng — quá nhiều để
  người soi tay); ngưỡng 1% CP lưu hành đưa về ~5% (~4 mã/tháng — vừa sức).
- Yếu nhất ở large-cap (§3.2).
- **Chưa đo được phần gia tăng so với `anomaly_scan`/`forensic_flags` đang có** — hai cơ chế có thể
  bắt trùng cùng một nhóm mã. Đây là việc bắt buộc trước khi wire (xem §5).

---

## §4 — Thiết kế tích hợp (chưa code, theo yêu cầu)

Điểm neo hiện có: `anomaly_gate.py::anomaly_excluded(asof)` là **nguồn sự thật duy nhất** cho gate
due-diligence (đọc `data/anomaly_flags.json` do `anomaly_scan.py` ghi, TTL 30 ngày, cửa sổ **hai
đầu** `cutoff <= last_alert <= asof` chống look-ahead, fail-safe trả set rỗng). Consumers:
`golive_recommend_v23.py` (production) + 3 sổ paper.

**Đề xuất — tách riêng, KHÔNG nhập vào `anomaly_excluded`:**

1. **Writer mới `insider_flags.py`** → `data/insider_flags.json`, cùng shape với `anomaly_flags.json`:
   `{ticker: {last_alert, tier, reasons, sell_pct_osh, n_sellers, window_end}}`.
   - Nguồn: `tav2_bq.insider_transaction`, **chỉ** `event_code IN ('DDIND','DDRP')`,
     `trade_status='Đã thực hiện xong'`, tự áp dấu theo `action_code`.
   - Điều kiện bắn cờ: tổng bán ròng 90 ngày ≥ **1,0% `OShares`**. `last_alert` = `public_date` của
     giao dịch bán đủ điều kiện gần nhất.
   - **TTL = 90 ngày** (không phải 30 như anomaly) — khớp cửa sổ tín hiệu 90d và horizon đo fwd60.
2. **Reader mới `anomaly_gate.py::insider_sell_flagged(asof, ttl_days=90)`** — hàm **RIÊNG**, không
   merge vào `anomaly_excluded`. Lý do: `anomaly_excluded` là **hard exclude** đang chi phối 4 sổ;
   bằng chứng ở §3.5 (80% false-positive) **không đủ** để hard-exclude. Nhập chung sẽ âm thầm đổi
   hành vi loại mã của production.
3. **Tiêu thụ = WATCH, không phải EXCLUDE**: đưa vào **báo cáo due-diligence** của mọi ứng viên mua
   (mandate user 2026-07-21 — mọi candidate đều due-diligence) dưới dạng một dòng bằng chứng
   ("nội bộ bán X% CP lưu hành trong 90 ngày qua, N người bán, lần gần nhất <ngày>"), để người
   duyệt plan cân nhắc, giống cách case PNJ được xử lý.
4. **Fail-safe + freshness**: bảng chưa có cadence refresh xác nhận (§1.2). Nếu
   `MAX(public_date)` cũ hơn ~10 phiên ⇒ log WARN và **không bắn cờ mới** (fail-open — hướng an
   toàn cho một cờ mềm), tuyệt đối không để cờ cũ "đóng băng" tạo cảm giác sạch giả.
5. **Chống look-ahead**: bắt buộc dùng cửa sổ hai đầu như `anomaly_excluded` (`lo <= last_alert
   <= asof`). Với bảng snapshot này còn một rủi ro riêng: nếu bq_admin refresh bằng
   `WRITE_TRUNCATE`, mọi replay lịch sử sẽ dùng bản ghi mới nhất — chấp nhận được cho dòng Done
   (ngày báo cáo kết quả là sự thật đã công bố) nhưng **không** cho dòng `Đăng ký`.

---

## §5 — Đề xuất bước tiếp theo (theo thứ tự, cần user/Mike quyết)

| # | Việc | Chi phí | Điều kiện |
|---|---|---|---|
| 1 | **Hỏi bq_admin cadence refresh** của `insider_transaction` (qua Winston) | rẻ | **Chặn mọi thứ khác** — không refresh thì gate đứng im |
| 2 | Đo **phần gia tăng so với `anomaly_scan`+`forensic_flags`** (overlap ma trận 2×2 trên đuôi trái) | rẻ | Trước khi wire; nếu overlap cao ⇒ không thêm giá trị |
| 3 | Nếu (2) cho thấy thông tin mới ⇒ dựng `insider_flags.py` + `insider_sell_flagged()` theo §4, **WATCH-only**, chạy shadow ≥1 tháng | trung bình | Có quant-skeptic trước khi vào due-diligence chính thức |
| 4 | **Dự án dữ liệu riêng: snapshot `insider_transaction` hàng ngày** (append-only, giữ nguyên `public_date` tại thời điểm quan sát) để 12-18 tháng nữa mới nghiên cứu được cửa sổ pre-trade | rẻ/ngày, chậm thu hoạch | Quyết định riêng của user — đây là cách DUY NHẤT lấy lại lợi thế cấu trúc TT96/2020 |
| 5 | Tìm nguồn **chức danh** người nội bộ (CT/TGĐ/KTT) | chưa rõ | Chỉ cần nếu muốn mở lại hướng factor |

**KHÔNG đề xuất**: backtest production đầy đủ hướng factor (§2 đã đủ để loại).

---

## Tự kiểm (self-check)

- Universe = `universe_pit` in_universe theo từng phiên rebalance (đúng `_universe-selection-rules.md`),
  **không** `ticker_prune`.
- Không look-ahead: mọi tín hiệu lọc `public_date <= ngày rebalance`; forward return tính từ chính
  ngày rebalance bằng `LEAD(Close, 20/60)`; 1/PE và 8L rating lấy as-of (`time <= d`, bản mới nhất).
- `profit_*` (forward-looking) **không** được dùng ở bất kỳ đâu.
- fwd60 chồng lấn (rebalance tháng, horizon 3 tháng) ⇒ t-stat của fwd60 lạc quan; **kết luận
  chính neo vào fwd20 (gần như không chồng lấn) và vào test tỷ lệ đuôi**, nơi mỗi quan sát là một
  cửa sổ độc lập theo mã.
- N trials khai báo trước: 6 (vòng factor) + 4 (vòng gate: 4 biến thể tín hiệu) + 4 (sweep ngưỡng
  gate) = **14**. Chưa tính DSR/PBO vì **chưa có config nào định wire production** — bắt buộc bổ
  sung nếu bước §5.3 được duyệt.

---
---

# PHỤ LỤC A — Đo phần GIA TĂNG so với `anomaly_scan` / `forensic_flags` (bước §5.2)

**Job:** `Taylor_20260729_032713` · **Ngày:** 2026-07-29 · **Tác giả:** Taylor
**Phạm vi:** RESEARCH. Chưa code `insider_flags.py`, chưa qua quant-skeptic (đúng phạm vi dispatch).
**Artifact mới:** `exp_insider/{anom_replay.sql, anom_replay.csv, overlap_analysis.py, overlap_results.txt}`.
**Không chờ bug refresh của bq_admin** — bước này chỉ dùng dữ liệu LỊCH SỬ (backtest overlap), không phải gate sống.

## A.0 — TL;DR

**GO cho §5.3** (dựng `insider_flags.py` WATCH-only, chạy shadow). Trùng lặp **thấp hơn nhiều**
ngưỡng NO-GO (70-80%) mà dispatch đặt ra, và lift trên phần KHÔNG trùng vẫn còn nguyên vẹn:

| Đo trên **rổ ứng viên mua** | overlap | lift phần INS-riêng | z |
|---|---:|---:|---:|
| vs anomaly tier-W (replay TOÀN universe — **ưu ái anomaly**) | **21,7%** | **2,083×** | 5,74 |
| vs anomaly tier-H (ngưỡng lỏng nhất = biên trên độ phủ) | 36,6% | 2,074× | 4,99 |
| vs anomaly ở **phạm vi quét THẬT** (rating≤2) | **7,1%** | 1,984× | 5,96 |
| vs `forensic_flags` (point-in-time) | **0,0%** | — | — |

Hai cờ **gần như độc lập thống kê** (φ = 0,055–0,084) và — quan trọng hơn — **bắn ở hai thời điểm
khác nhau của cùng một câu chuyện**: anomaly bắt sau khi giá đã sập, insider bắt khi giá gần như
chưa động (§A.4). Đây là quan hệ **bổ sung**, không phải thay thế.

## A.1 — Cách tái tạo (đọc code, không đoán)

**Cờ insider (INS)** — copy nguyên văn định nghĩa đã pin ở §3.4 (dòng cuối `gate_analysis.py`):
`sell_sh_90/OShares ≥ 1,0%` **VÀ** `nsell_90 > nbuy_90`, chỉ `event_code IN ('DDIND','DDRP')`,
`trade_status='Đã thực hiện xong'`, tự áp dấu theo `action_code`. Cùng panel/universe/kỳ (`panel2.csv`,
`universe_pit` in_universe, 2015-06 → 2026-07, 134 tháng, 47.886 quan sát có fwd60).

> **Self-check tái lập §3.4**: INS bắt **5,4%** universe (pin 5,4%) · P(sập|INS) = **19,65%**
> (pin 19,68%) · nền **11,26%** (pin 11,28%) · lift **1,746×** (pin 1,745×). ✔ Khớp.

**Cờ anomaly** — `anomaly_flags.json` **không tồn tại trong lịch sử** (`anomaly_scan.py` mới có từ
2026-07-17), nên phải **replay quy tắc** (`anom_replay.sql`), copy nguyên văn ngưỡng từ
`anomaly_scan.py::compute_signals` (FLOOR2/CEIL2/VOLSPIKE/IDIOCRASH, `LIQ_1M_BN=3.0`,
`real_trade val_bn≥0,3`) rồi áp đúng cửa sổ TTL của `anomaly_gate.py::anomaly_excluded`
(`asof−30d ≤ last_alert ≤ asof`, hai đầu, chống look-ahead).

> **Self-check ground-truth** (trùng `anomaly_scan.py::selftest`): PNJ alert đầu tiên
> **2026-07-03** ✔ · DGC **2026-03-17** ✔ · PNJ **2026-03-09** (sàn CÙNG thị trường) **không trip** ✔.

Vì `hold` lịch sử không tái lập được, dùng **hai biến thể kẹp hai đầu sự thật**:
- `anom_w` = nhánh tier-W (ứng viên mua, chưa nắm giữ) áp cho **TOÀN universe** ⇒ **ưu ái anomaly tối đa**
  (thực tế anomaly chỉ quét `hold ∪ watchlist rating≤2`, **43,5%** rổ ứng viên có rating 3 nằm
  NGOÀI tầm quét ⇒ anomaly không bao giờ bắt được).
- `anom_h` = nhánh tier-H (ngưỡng lỏng hơn) ⇒ **biên trên tuyệt đối** của độ phủ anomaly.
- `anom_real` = `anom_w ∧ rating≤2` ⇒ xấp xỉ phạm vi quét THẬT (bỏ nhánh `hold`).

## A.2 — Ma trận 2×2

**Toàn universe** (n = 47.886):

| | anom_w = T | anom_w = F | tổng |
|---|---:|---:|---:|
| **INS = T** | 761 | **1.829** | 2.590 |
| **INS = F** | 7.216 | 38.080 | 45.296 |

⇒ trong số mã bị INS: **29,4% đã có anomaly** (trùng) / **70,6% không có** (tín hiệu MỚI).
Chiều ngược lại: trong số mã bị anomaly, chỉ **9,5%** cũng bị INS. odds-ratio 2,20 · **φ = 0,082**.

**Rổ ứng viên mua** (rating≤3 & 1/PE top-tercile, n = 10.410) — mẫu **thực sự vận hành**:

| | anom_w = T | anom_w = F | tổng |
|---|---:|---:|---:|
| **INS = T** | 107 | **385** | 492 |
| **INS = F** | 1.124 | 8.794 | 9.918 |

⇒ **21,7% trùng / 78,3% MỚI**. Chiều ngược: 8,7% mã anomaly cũng bị INS. φ = 0,068.

Với `anom_h` (lỏng nhất): trùng 36,6% (rổ ứng viên) / 42,5% (toàn universe) — **vẫn dưới xa ngưỡng
NO-GO 70-80%** kể cả ở kịch bản ưu ái anomaly nhất.

Với `anom_real` (phạm vi quét thật, rating≤2): trùng **chỉ 7,1%** (rổ ứng viên) / **2,5%** (toàn universe).

**`forensic_flags` — độ phủ point-in-time = 0.** Cả **11/11** dòng trong `data/forensic_flags.csv`
đều mang `date = 2026-06-20` (một đợt curation thủ công duy nhất) ⇒ trong toàn bộ panel 132 tháng
**không có quan sát nào** có forensic flag hiệu lực. Thêm nữa `build_rating_8l_history.py` áp
forensic → **rating 5 kể từ ngày flag**, mà rổ ứng viên lọc rating≤3 ⇒ mã forensic **cấu trúc không
thể nằm trong rổ** sau ngày bị flag. Kết luận: forensic **không** cạnh tranh với cờ insider; hai cơ
chế đo hai thứ khác nhau (chất lượng kế toán nhiều năm vs giao dịch nội bộ 90 ngày).
*(Kiểm tra TĨNH, không point-in-time, chỉ tham khảo: 5/11 mã forensic từng bị INS bắt — CTF 13 lần,
HHS 11, L40 10, DIG 10, PC1 3; 6 mã còn lại chưa từng.)*

## A.3 — Giá trị RIÊNG còn lại sau khi loại phần trùng

`P(fwd60 < −20%)`, **nền = ô sạch cả hai cờ** (đúng câu hỏi "mã mà anomaly nói là sạch thì cờ
insider có thêm được gì không"):

**Rổ ứng viên mua** — vs `anom_w`:

| Ô | n | P(sập) | lift vs nền sạch | z |
|---|---:|---:|---:|---:|
| **NỀN — không cờ nào** | 8.794 | 7,36% | — | — |
| **INS RIÊNG** (anomaly nói sạch) | **385** | **15,32%** | **2,083×** | **5,74** |
| anomaly RIÊNG (không INS) | 1.124 | 18,42% | 2,503× | 12,45 |
| trùng cả 2 | 107 | **24,30%** | **3,303×** | 6,59 |

Vs `anom_h` (test khắt khe nhất): INS riêng n=312, P=14,42%, lift **2,074×**, z=4,99.
Vs `anom_real` (phạm vi quét thật): INS riêng n=457, P=15,97%, lift **1,984×**, z=5,96.

**Ba điều đáng chú ý:**
1. Lift của phần INS-riêng **không giảm** so với §3.4 — thậm chí **cao hơn** (2,08× vs 1,58× trong
   §3.1) vì loại mã anomaly ra làm cho **nền sạch hơn** (7,36% thay vì 8,61%). Cờ insider không hề
   "sống nhờ" phần trùng với anomaly.
2. **Ô trùng cả 2 cờ là nguy hiểm nhất: 24,3% sập, lift 3,3×.** ⇒ dù kết luận có là gì, việc **ghi
   nhận khi CẢ HAI cùng bắn** đã có giá trị thực tế ngay (đúng gợi ý trong dispatch).
3. **Recall tăng thêm**: trong rổ ứng viên, anomaly bắt 233/939 ca sập (24,8%); INS bắt **thêm 59 ca**
   (+6,3pp) với chi phí **385 cờ mới trên 134 tháng ≈ 2,9 mã/tháng** — vừa sức review tay
   (thấp hơn ước tính ~4/tháng ở §3.5 vì phần trùng anomaly đã bị trừ ra).

**Ổn định IS↔OOS của phần INS-riêng** (vs `anom_w`) — điều kiện then chốt, đều PASS:

| Mẫu | kỳ | n | P(sập) | nền sạch | lift | z |
|---|---|---:|---:|---:|---:|---:|
| Toàn universe | IS 2015-19 | 689 | 12,63% | 9,00% | 1,403× | 3,21 |
| Toàn universe | OOS 2020+ | 1.140 | 16,93% | 9,84% | 1,720× | 7,75 |
| **Rổ ứng viên** | IS 2015-19 | 144 | 14,58% | 7,82% | **1,866×** | 2,89 |
| **Rổ ứng viên** | OOS 2020+ | 241 | 15,77% | 7,16% | **2,201×** | 4,98 |

## A.4 — Vì sao hai cờ gần như độc lập: chúng bắn ở HAI THỜI ĐIỂM khác nhau

Lợi nhuận **quá khứ 2 tháng** tính đến ngày quan sát (rổ ứng viên mua, trung vị):

| Ô | n | trailing 2M (trung vị) | trung bình |
|---|---:|---:|---:|
| không cờ nào | 8.390 | **+0,00%** | +0,97% |
| **INS riêng** | 349 | **−1,45%** | −0,43% |
| **anomaly riêng** | 1.062 | **−7,20%** | −2,42% |
| trùng cả 2 | 95 | **−12,68%** | −6,08% |

Đây là bằng chứng số cho một sự thật vốn nằm sẵn trong định nghĩa quy tắc: FLOOR2/IDIOCRASH **đòi
hỏi giá đã rơi ≥6% mới trip** ⇒ anomaly về bản chất là **máy dò HẬU-sự-kiện** ("cú sập đã bắt đầu").
Cờ insider bắn trên mã **giá gần như chưa động** (−1,45%) nhưng vẫn có xác suất sập 60 phiên tới
gấp đôi. Hai cơ chế **bổ sung** nhau chứ không thay thế — và điều này củng cố quyết định thiết kế ở
§4 mục 2: **giữ hàm RIÊNG, không merge vào `anomaly_excluded`**.

## A.5 — Kết luận: **GO** cho §5.3 (WATCH-only, shadow)

Overlap 21,7% (hoặc **7,1%** theo phạm vi quét thật) — **thấp hơn nhiều** ngưỡng NO-GO 70-80%; lift
trên phần không trùng **2,08×** (z=5,74), ổn định IS↔OOS. ⇒ Khuyến nghị **tiến hành §5.3**: dựng
`insider_flags.py` + `insider_sell_flagged()` theo thiết kế §4, **WATCH-only**, chạy shadow ≥1 tháng.

**Vẫn giữ nguyên mọi điều kiện chặn đã nêu trước đó — không có gì ở phụ lục này nới chúng ra:**
1. **Cadence refresh phải được xác nhận bằng quan sát thật** (bq_admin đang fix bug, 2026-07-29) —
   không refresh thì gate đứng im và tạo cảm giác sạch giả. Fail-safe §4.4 là bắt buộc.
2. **WATCH-only, tuyệt đối không hard-exclude**: ~85% mã bị cờ KHÔNG sập (§3.5); và cờ chỉ bắt
   ~9% tổng số ca sập.
3. **quant-skeptic bắt buộc** trước khi đưa vào due-diligence chính thức; khai báo N trials +
   DSR nếu có bất kỳ tác động nào lên quyết định mua.
4. Yếu nhất ở large-cap (§3.2) ⇒ giá trị tập trung ở LAG / CAPIT pool / fear-buy sleeve.

**Đề xuất bổ sung (rẻ, độc lập với §5.3):** ngay cả khi §5.3 bị hoãn, **ghi nhận trường hợp CẢ HAI
cờ cùng bắn** — ô đó có P(sập) = 24,3% (lift 3,3×), là nhóm rủi ro cao nhất đo được trong toàn
nghiên cứu này.

## A.6 — Tự kiểm (self-check) & giới hạn

- ✔ Tái lập đúng số đã pin ở §3.4 (5,4% / 19,65% / 1,746×) — chênh ~0,03pp do §3.4 lọc thêm
  `mcap`/`turn` khi dropna.
- ✔ Replay anomaly khớp ground-truth PNJ/DGC + negative control (sập cùng thị trường không trip).
- ✔ Assert tổng 4 ô 2×2 = n mẫu (bắt được **một bug thật trong chính script này**: left-join sinh
  NaN làm cột anomaly thành `dtype=object`, khiến `~col` chạy **bitwise-not trên Python bool**
  (`~True = −2`, truthy) thay vì phủ định logic ⇒ ô "INS riêng" phình bằng toàn bộ INS. Đã sửa bằng
  `.astype(bool)` + assert tổng; mọi số trong phụ lục này là **sau khi sửa**).
- ✔ Chống look-ahead: cửa sổ anomaly hai đầu `[asof−30d, asof]`, cờ insider lọc `public_date ≤ ngày
  rebalance`, `profit_*` không dùng ở đâu.
- ⚠ **`anom_*` là TÁI TẠO, không phải `anomaly_flags.json` lịch sử thật** (file đó không tồn tại
  trước 2026-07-17). Nhánh `hold` không tái lập được ⇒ đã kẹp hai đầu (`anom_w` toàn universe =
  ưu ái anomaly tối đa; `anom_real` rating≤2 = xấp xỉ phạm vi thật). **Kết luận GO không đổi dấu ở
  cả hai đầu kẹp** — đây là điểm quan trọng nhất của thiết kế kiểm chứng này.
- ⚠ fwd60 chồng lấn (rebalance tháng, horizon 3 tháng) ⇒ z-stat lạc quan; kết luận neo vào **độ lớn
  overlap** (một phép đếm, không phụ thuộc giả định phân phối) chứ không vào z.
- ⚠ **N trials phụ lục này = 0 tham số mới** — cờ insider lấy nguyên §3.4, cờ anomaly copy nguyên
  văn từ code production. Ba biến thể `anom_w/anom_h/anom_real` là **phân tích độ nhạy**, không phải
  sweep chọn cái đẹp nhất (báo cáo cả ba, và cả ba đều cùng dấu).

---
---

# PHỤ LỤC B — Triển khai §5.3: `insider_flags.py` WATCH-only (shadow)

**Job:** `Taylor_20260729_104614` · **Ngày:** 2026-07-29 · **Tác giả:** Taylor
**Trạng thái:** hạ tầng ĐÃ DỰNG + selfcheck xong, **CHƯA wire vào bất kỳ báo cáo/sổ nào**.
User duyệt tiến hành sau khi Phụ lục A kết luận GO (overlap 7,1–21,7%, lift phần riêng 2,08×).

## B.0 — TL;DR

| | |
|---|---|
| File mới | `mike/agents/Taylor/insider_flags.py` (writer), `mike/agents/Taylor/insider_flags_selfcheck.py` (test) |
| File sửa | `anomaly_gate.py` — thêm hàm RIÊNG `insider_sell_flagged()`, **không đụng** `anomaly_excluded` |
| Output | `data/insider_flags.json` — 17 mã bị bắt tại `asof=2026-07-29` |
| Selfcheck | `--selftest` 8/8 (6 ca thật + 2 negative control) · `insider_flags_selfcheck.py` 15/15 |
| Tiêu thụ | **KHÔNG AI** — cố ý. Chạy shadow để tích luỹ dữ liệu, wire sau (cần quant-skeptic lúc đó) |

## B.1 — Công thức bắn cờ: nói CHÍNH XÁC nó là gì

Đề bài dispatch viết tắt là "tổng bán ròng 90 ngày ≥ 1,0% OShares". Công thức pin ở §3.4 (dòng
`ban >=1% CP luu hanh` trong `exp_insider/gate_analysis.py`) thực chất là **AND của HAI vế**, và
code tái lập đúng bản pin chứ không phải bản viết tắt:

```
sell_sh_90 / OShares >= 0,01        (khối lượng BÁN GỘP, không phải bán trừ mua)
        VÀ  nsell_90 > nbuy_90      (số NGƯỜI bán phân biệt > số người mua phân biệt)
```

Khác biệt có thật: vế 2 loại các mã vừa có người bán lớn vừa có nhiều người mua (thường là
ESOP/phát hành — bẫy #4 trong data registry). Bỏ vế 2 sẽ **không** phải là ngưỡng đã đo lift 1,745×.
Cửa sổ: `asof − 90d < public_date <= asof`, hệt `panel2.sql`. `OShares` lấy as-of
(`ticker_financial`, bản mới nhất `time <= asof`).

Ba bẫy dữ liệu áp đúng registry: chỉ `DDIND`/`DDRP` (bỏ `DDINS` = flow tổ chức), chỉ
`trade_status='Đã thực hiện xong'`, **tự áp dấu** theo `action_code` (~2.500 dòng Bán không có dấu âm).

## B.2 — Thiết kế theo đúng §4 (khác biệt duy nhất được nêu rõ)

- **Shape file**: `{ticker: {last_alert, tier, reasons, sell_pct_osh, n_sellers, window_end}}` — đúng
  §4, cùng convention `anomaly_flags.json`. `tier` luôn `"W"`, `reasons` luôn `INSIDER_SELL_1PCT`
  (giữ chỗ cho biến thể tương lai; hiện chỉ 1 luật nên không tự sinh thêm bậc).
- **Ghi atomic** `tmp` + `os.replace` (guidelines §5).
- **Merge có điều kiện**: bản ghi cũ chỉ bị thay khi cờ mới có `last_alert` MỚI HƠN. Không có luật
  này, cửa sổ 90d trượt qua một giao dịch cũ sẽ tạo **bản ghi lai** (ngày của giao dịch này, số liệu
  của giao dịch kia) — lỗi âm thầm nhất trong nhóm này.
- **TTL 90 ngày do READER áp**, writer không tự xoá cờ cũ (giống anomaly) — file là log tích luỹ.
- **Reader trả `dict`, không phải `set`** (khác `anomaly_excluded`) — CỐ Ý: tiêu thụ là **một dòng
  bằng chứng** trong báo cáo due-diligence, cần cả `sell_pct_osh`/`n_sellers`/`last_alert`; và kiểu
  trả về khác cũng làm khó việc vô tình dùng nó như một danh sách loại mã. Vẫn iterate ra tên mã.
- **Cửa sổ hai đầu** `[asof − ttl, asof]` y hệt `anomaly_excluded` — chặn trên là chống look-ahead
  khi replay ngày quá khứ.
- **Fail-safe freshness (§4.4)**: `MAX(public_date)` cũ hơn 10 phiên ⇒ in WARN, **exit 3, không ghi
  gì** (cờ cũ trong file vẫn hết hạn theo TTL ở reader — cố ý không đóng băng để tránh cảm giác
  "sạch" giả). Đếm phiên bằng ngày T2–T6 (đếm cả ngày lễ ⇒ ước lượng THỪA ⇒ dễ WARN hơn, đúng hướng
  thận trọng; cố ý không tra lịch giao dịch thật để không phụ thuộc thêm một bảng cũng có thể đang cũ).
- **Đọc LIVE BQ**, không qua `bq_cache` (bảng không có trong cache; và guidelines §11 cấm publish
  script đọc qua cache env kế thừa). Chi phí đo thật: **1,41 MB/lần chạy** (dry-run).

## B.3 — Selfcheck (bắt buộc trước khi coi là xong)

**(a) `insider_flags.py --selftest` — PASS 8/8.** Replay `asof=2026-07-24` và đối chiếu với
`exp_insider/panel2.csv` (nghiên cứu gốc, tính bằng SQL độc lập trong BQ):

| Mã | kỳ vọng (panel2) | writer | |
|---|---:|---:|---|
| ITD | 0,15134 | 0,15134 | PASS |
| BIG | 0,07556 | 0,07556 | PASS |
| BMS | 0,02882 | 0,02882 | PASS |
| VCI | 0,01468 | 0,01468 | PASS |
| TOS | 0,01333 | 0,01333 | PASS |
| DIG | 0,01215 | 0,01216 | PASS |

+ negative control FPT/ACB không bị bắt. (Writer quét TOÀN thị trường — 23 mã tại 07-24 — còn
`panel2` chỉ trong `universe_pit`, nên writer ⊇ panel là đúng thiết kế, không phải sai lệch.)

**(b) `insider_flags_selfcheck.py` — PASS 15/15**: idempotent (chạy 2 lần → file byte y hệt, md5
`d7c8f57b…` không đổi, `0 mới / 0 cập nhật`); không để lại `.tmp`; merge giữ bản mới hơn / không
ghi đè bằng bản cũ hơn; **atomic thật** (giả lập `json.dump` chết giữa chừng → file đích còn nguyên
vẹn và vẫn parse được); phục hồi từ file JSON hỏng sẵn; reader: cửa sổ hai đầu, replay 2026-04-01 →
rỗng (không áp cờ tương lai), `asof` 2027 → rỗng (hết TTL), biên trên inclusive, fail-safe thiếu file
→ `{}`.

**(c) Cổng freshness**: chạy `--asof 2026-08-20` (giả lập bảng chết) → WARN + `exit 3`, md5 file
**không đổi**. Đúng hành vi mong muốn.

**(d) Không hồi quy**: `anomaly_excluded('2026-07-29')` vẫn trả đúng 9 mã như trước
(CSV/CTS/DGC/GAS/MBS/PNJ/SHS/VGR/VND). **Giao của hai cờ hôm nay = rỗng** — khớp trực tiếp với kết
luận overlap thấp của Phụ lục A, quan sát trên dữ liệu LIVE chứ không phải replay.

## B.4 — Kết quả chạy thật `asof = 2026-07-29` (17 mã)

DBT 50,9% (8 người bán) · VFR 26,7% · BKG 18,6% · ITD 15,1% · KHS 9,1% · KDM 8,1% · BIG 7,6% ·
SII 5,8% · TNI 5,2% · VNH 4,5% · AGM 4,2% · TNW 3,9% · CCA 3,5% · BMS 2,9% · **TMG 1,6%** ·
VCI 1,5% · DIG 1,2%.

Đáng chú ý: **TMG** — chính là một trong 3 ứng viên LAG phiên 07-24 (IVS/TMG/TRC) mà user cuối cùng
chỉ chọn TRC. Cờ này nếu đã có trong báo cáo due-diligence hôm đó sẽ là **một dòng bằng chứng thật**
cho người duyệt, đúng kịch bản tiêu thụ đã thiết kế. Đây là quan sát 1 ca, **không phải bằng chứng
hiệu lực** — ghi lại để theo dõi trong giai đoạn shadow.

## B.5 — Đề xuất cadence cron (Mike quyết định giờ, tôi KHÔNG tự cài)

**4 câu hỏi bắt buộc** (`kb/cron_registry/_adding-cron-policy.md`):

1. **Đọc gì, vintage nào?** `tav2_bq.insider_transaction` (**BQ LIVE**, không qua cache — bảng không
   tồn tại trong `data/bq_cache/`) + `tav2_bq.ticker_financial.OShares` as-of (BQ live). Ghi
   `data/insider_flags.json`.
2. **Nguồn tươi lúc nào? (ĐO THẬT, 2026-07-29 17:5x ICT)** `MIN/MAX(ingested_at)` =
   **2026-07-27 14:35:45 → 14:36:56 UTC, đúng 1 ngày ingest phân biệt, 52.155 dòng** —
   **CHƯA quan sát được lần refresh nào** ngoài backfill. `MAX(public_date) = 2026-07-24` (~3 phiên
   trước). bq_admin nói cadence dự kiến hàng ngày nhưng đang fix bug. ⇒ **Chưa có mốc "tươi lúc mấy
   giờ" để neo vào**; mốc duy nhất quan sát được là backfill lúc **21:35 ICT**.
3. **Cần T hay T-1?** **T-1 là đủ.** Tín hiệu là cửa sổ 90 ngày với TTL 90 ngày — trễ 1 phiên không
   đổi tập cờ một cách có ý nghĩa. Không có nhu cầu same-day nào.
4. **Ai tiêu thụ, deadline?** **Hiện tại KHÔNG AI** (shadow, đúng chỉ đạo). Consumer tương lai theo
   thiết kế = báo cáo due-diligence cho ứng viên mua → chuỗi kết thúc ở **plan T+1 21:00 ICT**
   (`send_plan_report.sh`), backstop preflight 08:45 sáng hôm sau.

**Đề xuất cụ thể:**

```cron
# insider_flags (WATCH-only shadow) — 18:45 ICT T2-T6
45 11 * * 1-5 /home/trido/thanhdt/wc_venv/bin/python /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/insider_flags.py >> /home/trido/thanhdt/WorkingClaude/mike/logs/insider_flags.log 2>&1
```

- **Vì sao 18:45 ICT**: sau mốc ingest same-day của `ticker_financial` (~17:30, cho `OShares` as-of),
  **trước** `bq_freshness_check` 19:00 → pipeline EOD → plan 21:00, nên khi có consumer thật thì cờ
  đã sẵn sàng cùng ngày. Lệch ≥5 phút với mọi job hiện có; tải không đáng kể (1,41 MB/lần, ~10 giây).
- **Đánh đổi đã biết, nói rõ**: nếu cron của bq_admin thật sự chạy ~21:35 ICT, bản 18:45 sẽ đọc bảng
  **trễ 1 phiên**. Chấp nhận được (câu 3: T-1 đủ) và **tốt hơn** phương án chạy 22:00 — vì 22:00 là
  SAU deadline plan 21:00, tức consumer tương lai vẫn phải dùng bản T-1, mà lại mất luôn tính tươi
  trong ngày. Khi Winston xác nhận được giờ refresh thật, xem lại 1 lần.
- **T2-T6**: nguồn không có gì mới cuối tuần.
- **Không piggyback vào `ops_health_check.sh`** (nơi `anomaly_scan` đang chạy 08:20/12:45): dữ liệu
  này đổi tối đa 1 lần/ngày, chạy 2 lần/ngày trong phiên là lãng phí và sai nhịp.
- **Cảnh báo vận hành cần biết trước**: nếu bug của bq_admin chưa fix, cổng freshness sẽ bắt đầu WARN
  + `exit 3` từ khoảng **2026-08-07** (10 phiên sau 07-24). Đó là hành vi ĐÚNG (không bắn cờ trên
  nguồn chết), nhưng cron sẽ có exit code khác 0 mỗi ngày — đừng nhầm là script hỏng; đó là tín hiệu
  đi hỏi bq_admin.

## B.6 — Giới hạn & việc còn treo

- **CHƯA wire vào due-diligence report** — đúng chỉ đạo. Khi wire, **bắt buộc quant-skeptic** + khai
  N trials/DSR nếu lúc đó nó ảnh hưởng quyết định mua bán.
- **Chưa có backfill lịch sử** của `insider_flags.json`: file bắt đầu từ 2026-07-29. Muốn đo
  false-positive live sau này thì phải hoặc chờ tích luỹ, hoặc replay bằng `--asof` (replay ĐƯỢC, vì
  cờ tính hoàn toàn từ `public_date` của dòng Done — nhưng vẫn dính bẫy snapshot #1: replay dùng bản
  ghi mới nhất của bảng, không phải bản người ta thấy lúc đó).
- **Số mã bị bắt phụ thuộc bảng còn sống**: hôm nay 17 mã toàn thị trường; nếu bảng đứng im, con số
  này sẽ **teo dần** khi cửa sổ 90 ngày trượt qua — đây là lý do cổng freshness tồn tại.
- Vẫn nguyên các giới hạn §3.5 (precision ~20%, recall ~9%, yếu ở large-cap) — **WATCH, không exclude**.
