# Đánh giá OKF-hoá `data/results_registry.md` — BƯỚC 1 (chỉ đánh giá, CHƯA thực thi)

> Job `Taylor_20260730_144031` · Taylor (quant, **chủ sở hữu file này**) · 2026-07-30
> **Kết luận: KHÔNG OKF-split 130 mục pin theo ngày.** Đây là **sổ cái append-only theo thời
> gian** (ledger), không phải registry các fact độc lập như `data_registry.md`. Kết quả cùng
> họ với `cron_registry.md` (Winston giữ nguyên bảng chính vì "giá trị = phụ thuộc giữa các
> dòng liền kề") và với `coding_guidelines §10 mục 4` (không động vào artifact audit-trail).
> Đề xuất thay thế: **3 việc nhỏ tại chỗ, 0 phá tham chiếu, 0 đổi quy trình ghi pin.**

⚠️ **Repo:** file nằm ở repo GỐC `/home/trido/thanhdt` (`WorkingClaude/data/results_registry.md`),
**KHÁC** repo `mike` (`/home/trido/thanhdt/WorkingClaude/mike`) — nơi 3 lần OKF trước diễn ra.
Báo cáo này nằm trong repo `mike`; **không file nào bị sửa** trong job này.

---

## 0. Số đo thật (không ước lượng)

| Đại lượng | Đo được |
|---|---:|
| Kích thước | **548 382 B** (4 447 dòng) |
| Số mục `## ` | **135** |
| Byte trong các mục `##` | 547 452 B (header trước mục đầu: 795 B) |
| Kích thước mục: median / mean | **3 346 B** / 4 055 B |
| Mục lớn nhất | 20 180 B (`REAL-MARGIN self-check FIXED…`, L232) |
| Mục nhỏ nhất | 850 B (`MÔI TRƯỜNG`) |
| Phần "evergreen" (L1–126: header + QUY TẮC + MÔI TRƯỜNG + CONFIG TỐT NHẤT + BẢNG R1–R6) | **14 512 B = 2,6% file** |
| Tham chiếu chéo TRONG file (`cuối file` / `xem section` / …) | **11** |
| Mục có ngày trong tiêu đề | **130/135** (5 mục không: `MÔI TRƯỜNG`, `BẢNG KẾT QUẢ ĐÃ PIN`, `Wyckoff…`, `DSR/PBO Annex`, `DC-book waterfall sleeve`) |
| Nhịp ghi (commit từ 2026-07-01) | **44 commit / 30 ngày ≈ 1,5/ngày** |
| Dạng ghi | **~90% là APPEND THUẦN** (`N	0` trong `git numstat`); chỉ 5/20 commit gần nhất chạm dòng cũ — và đúng 5 lần đó là **sự kiện re-pin/supersede** |

Phân loại 135 mục (theo tiêu đề):

| Nhóm | Mục | Byte |
|---|---:|---:|
| NO-GO / REFUTED / LOẠI | 31 | 142 KB |
| RE-PIN / WIRE / FIX / annex | 21 | 89 KB |
| Sector screen / valuation lens | 26 | 92 KB |
| Khác (nghiên cứu, audit, event-study) | 57 | 212 KB |

---

## 1. Mật độ tham chiếu — grep thật, 61 file (KHÔNG phải 34)

Brief nói 34 file; đo lại `grep -rl "results_registry" mike/` = **61 file** (gồm 16 file
`kb/archive/*-nightly.md` + `events_buffer.md` — bất biến, không cần sửa). Số file **SỐNG** cần
quan tâm ≈ 40. Phân loại theo **cách trích dẫn** (đây mới là biến quyết định):

| Kiểu trích dẫn | Số hit | Ví dụ | STUB REDIRECT có cứu được? |
|---|---:|---|---|
| **A. Trỏ chung file** | ~45 | `Số liệu gốc: data/results_registry.md`; `Pin kết quả vào data/results_registry.md` | ✅ Có |
| **B. Trỏ ĐÍCH DANH tên mục** | **6** | canonical.md:14 + context_pack.md:294 *"mục **2026-07-29 RE-PIN R3 SAU RESTATE DT5G**"*; canonical:69 + context_pack:349 *"mục 'DSR / PBO Robustness Annex'"*; `projects/v2.5-leverage-nogo.md:31` *"mục 'V2.5 LEVERAGE VERIFICATION'"*; `projects/wc-deposit-rate-gate.md:46` *"mục DEPOSIT-RATE-GATE"*; `capit_dividend_gate_framework.md:6` | ⚠️ Chỉ cứu nếu tên file mới **chứa nguyên tên mục** |
| **C. Trỏ SỐ DÒNG** | **7** | `results_registry.md:4040` (current_ops + context_pack); `line ~142` (coding_guidelines §8); `dòng ~245` (bigquery_dictionary.md); `dòng ~145-154` (route_aware_selector_framework); `:3056` + `:3062` (exp_dirs_housekeeping); `L2800` / `dòng 2800` (3 script trong `data/g6_repin/`) | ❌ **Không cứu được** — số dòng biến mất hoàn toàn khi tách |
| **D. Code đọc/nhắc file** | 5 | `dsr_pbo_annex.py:3`, `converge_fullharness_test.py:2317`, `run_depgate_variant.py:7`, `cache_vintage_stamp.py:3`, `fleet_housekeeping.sh:331` | ✅ Chỉ là comment — **không script nào PARSE file này** (kiểm tra: 0 script mở/đọc nó bằng code) |

### Phát hiện quan trọng: 3/7 tham chiếu số dòng ĐÃ SAI SẴN

Verify từng cái (`sed -n '<n>p'`):

| Ref | Trỏ tới nội dung gì hôm nay | Đúng? |
|---|---|---|
| `results_registry.md:4040` | `## 2026-07-22 — RE-PIN R3 TRÊN universe_pit` | ✅ đúng |
| `:3056` / `:3062` | mục DEPOSIT-RATE-GATE / DIVIDEND — đúng | ✅ đúng (viết hôm nay) |
| `coding_guidelines §8: "line ~142"` (vụ ghi đè CSV R3) | L142 = *dòng "Method: 1 obs/(ticker,quý)…"* của IC-panel 8L | ❌ **SAI** (nội dung thật ở L~112) |
| `bigquery_dictionary.md: "dòng ~245"` | L245 = **dòng trống** | ❌ **SAI** |
| `route_aware…: "dòng ~145-154"` | L145-154 = bảng IC-panel — trùng khớp một phần chủ đề nhưng không phải THREAD (b) như mô tả | ⚠️ lệch |
| `data/g6_repin/*.sh: "L2800"` | L2800 = dòng kẻ bảng `\|---\|---\|`; section RE-PIN thật ở L2809 | ⚠️ lệch 9 dòng |

⇒ **Cơ chế trích dẫn theo số dòng đã tự hỏng bởi chính việc chèn/sửa mục ở giữa file, không cần
OKF-split nào cả.** Điều này cắt cả hai chiều: (a) làm YẾU lập luận "tách sẽ phá ref số dòng" —
nó đã hỏng rồi; (b) làm MẠNH lập luận "ref số dòng không phải cơ chế đáng bảo tồn, cần thay bằng
tên mục" — và đó là việc làm được **mà không cần tách gì**.

---

## 2. Khác biệt bản chất với `data_registry.md` (ca tách THÀNH CÔNG)

| | `data_registry.md` (đã OKF, đúng) | `results_registry.md` |
|---|---|---|
| Bản chất | **Danh mục** 76 nguồn dữ liệu **cùng tồn tại song song** | **Sổ cái theo thời gian** — 130 sự kiện pin xếp theo ngày |
| Đơn vị nội dung | 1 nguồn = 1 fact độc lập, đúng/sai không phụ thuộc mục khác | 1 mục = 1 **run tại 1 vintage**; giá trị nằm ở **quan hệ với mục trước/sau** (supersede) |
| Truy cập điển hình | "nguồn X là gì?" → mở đúng 1 file | "số R3 chính thức là bao nhiêu?" → phải biết mục nào **chưa bị thay** |
| Nhịp ghi | thỉnh thoảng, khi có nguồn mới | **1,5 mục/ngày**, ~90% append thuần |
| Thứ tự có nghĩa? | KHÔNG | **CÓ** — thứ tự = tính thời sự |

Nó gần `cron_registry.md` hơn: Winston giữ nguyên bảng chính vì *"giá trị = buffer/phụ thuộc
giữa các dòng liền kề, chống vintage-mismatch C1"* — ở đây cũng đúng, chỉ đổi trục: **vintage
theo thời gian thay vì theo giờ chạy**.

---

## 3. Lập luận quyết định (killer objection) — chuỗi SUPERSEDE là nội dung, không phải rác

Khối L28–59 (`## ⭐ CONFIG TỐT NHẤT = V2.4`) hiện chứa **cả 6 đời pin R3 nằm cạnh nhau**, mỗi đời
bị gạch ngang / dán nhãn `SUPERSEDED` và trỏ tới đời kế:

```
⭐ SỐ CHÍNH THỨC HIỆN HÀNH (2026-07-29): 27,60% / 1,84 / −17,5% / 1,58
~~⭐ (2026-07-22): 27,16% / 1,81 / −18,1% / 1,50~~ → SUPERSEDED 2026-07-29
⚠️ SUPERSEDED cho R3 (07-11 → 28,82) rồi (07-12 → 27,84) rồi (07-22)
⚠️ THÊM 07-21: lỗi fidelity liq<=0 VẪN MỞ ⇒ khoảng trung thực [~27,2%; 31,3%]
bảng threads=1 06-25: 28,05 / 29,01 / 28,01
```

**Giá trị của khối này = đọc tuyến tính thì KHÔNG THỂ trích nhầm số chết.** Đây chính xác là cơ
chế đã cứu đội nhiều lần (số 27,16% "không tái lập được", 27,84% "chỉ là lịch sử", cảnh báo
`liq<=0` gắn liền số hiện hành).

Nếu OKF-split: mỗi đời pin thành 1 file. Người (hoặc agent) grep `27,16` → rơi vào
`2026-07-22-repin-r3-universe-pit.md` → thấy một mục **đầy đủ, tự tin, có lệnh pin, có self-check
0 VND** — và **không có gì trong tầm mắt nói nó đã chết**, trừ khi frontmatter `status: SUPERSEDED`
được cập nhật đúng ở **mọi** file cũ tại **mọi** lần re-pin. Đã re-pin **6 lần trong 7 tuần**
(06-25, 07-11, 07-12, 07-21, 07-22, 07-29). Đây đúng lớp rủi ro của sự cố **SIGNAL_V11 base-leak**
(`kb/INCIDENTS.md`): *"rủi ro không đến từ quên tra, mà từ tra đúng chỗ nhưng chỗ đó cũ"* — và ở
đây "chỗ cũ" là **con số chính thức của chiến lược production**, hạng mục đắt nhất có thể sai.

Hôm nay chi phí giữ chuỗi đúng = **1 lần gạch ngang trong 1 file**. Sau khi tách = N lần sửa
frontmatter rải rác + không có bằng chứng thị giác nào khi đọc 1 file lẻ.

---

## 4. Tác động lên quy trình GHI của chính tôi (câu hỏi §3 của brief)

Đo thật: 44 commit/30 ngày, **~90% `N	0` = append thuần** (`>> results_registry.md`, 1 file, 0
quyết định).

Sau khi tách, mỗi lần pin mới cần: (1) đặt tên file — **quyết định mới mỗi lần**, không có quy tắc
hiển nhiên cho tiêu đề kiểu ``` `v4final` A4 (DY tie-break) + quét cap theo ĐỈNH ```; (2) tạo file;
(3) cập nhật `index.md`; (4) nếu là re-pin: sửa `status:` file cũ. **1 → 3-4 thao tác, ×1,5 lần/ngày.**
Failure mode mới: quên bước (3) ⇒ mục **tồn tại nhưng vô hình** với người điều hướng qua index —
tệ hơn hiện trạng (append thuần không thể "quên index").

Đây không phải lý do đủ để bác một mình, nhưng cộng với §3 thì cán cân rõ.

---

## 5. Lợi ích thật của việc tách — và cách đạt nó rẻ hơn

Lợi ích duy nhất (giống INCIDENTS.md): **chống `Read()` nguyên 548KB**. File **không** auto-inject
(không nằm trong `@import` của bất kỳ `CLAUDE.md` nào — đã kiểm tra) ⇒ chi phí chỉ phát sinh khi
ai đó thực sự mở nó.

Nhưng: **không script nào parse file này** (5 hit code đều là comment), và **130/135 mục có ngày
trong tiêu đề** ⇒ đường truy cập rẻ đã tồn tại và hoạt động tốt hôm nay:

```bash
grep -n "^## " data/results_registry.md | grep 2026-07-29      # tìm mục
sed -n '4336,4448p' data/results_registry.md                    # đọc đúng 8KB
```

Tách file chỉ tự động hoá bước 1. Cái thực sự làm hại là **agent phản xạ gọi `Read()` không grep
trước** — và cách chữa rẻ nhất là **dòng chỉ dẫn ở đầu file + TOC ngắn**, không phải tái cấu trúc
135 file.

---

## 6. KẾT LUẬN

**KHÔNG OKF-split.** Bảng cân:

| Tiêu chí | Nghiêng về |
|---|---|
| Bản chất nội dung (ledger theo thời gian, thứ tự có nghĩa) | **KHÔNG tách** |
| Chuỗi supersede của số production (§3) | **KHÔNG tách** (mạnh nhất) |
| Nhịp ghi 1,5/ngày, 90% append thuần (§4) | **KHÔNG tách** |
| 6 ref đích-danh tên mục (§1B) | trung tính (tách được nếu giữ tên) |
| 7 ref số dòng, **3 đã sai sẵn** (§1C) | trung tính — cần sửa **dù có tách hay không** |
| Không auto-inject, chi phí chỉ khi mở | **KHÔNG tách** (lợi ích nhỏ) |
| Mục tự chứa, median 3,3KB, chỉ 11 cross-ref nội bộ | *có tách được về mặt kỹ thuật* |
| `coding_guidelines §10 mục 4` (không động artifact audit-trail) | **KHÔNG tách** |

Kỹ thuật thì tách được; **không nên** tách. Đây là ca `cron_registry` chứ không phải `data_registry`.

---

## 7. ĐỀ XUẤT THAY THẾ — 3 việc nhỏ, tại chỗ (nếu Mike/user duyệt; CHƯA làm)

| # | Việc | Chi phí | Được gì | Rủi ro |
|---|---|---|---|---|
| **T1** | Thêm ~6 dòng đầu file: **"KHÔNG `Read()` cả file (548KB). Điều hướng: `grep -n '^## ' \| grep <ngày/từ khoá>` rồi `sed -n 'A,Bp'`. Số R3 hiện hành: xem khối ⭐ ngay dưới."** | 5 phút | Chặn đúng failure mode duy nhất mà OKF nhắm tới | 0 |
| **T2** | Sửa **7 ref số dòng → ref TÊN MỤC** (3 cái đang sai: `coding_guidelines §8 "line ~142"`, `bigquery_dictionary "dòng ~245"`, `route_aware "dòng ~145-154"`; 2 cái lệch: `data/g6_repin/*.sh "L2800"`; giữ `:4040`/`:3056`/`:3062` nhưng thêm tên mục kèm) | ~20 phút | Sửa 3 tham chiếu **đang sai thật**; làm mọi ref bền vững với mọi restructure tương lai | Thấp — chỉ sửa file trích dẫn, không đụng registry |
| **T3** | Thêm quy ước tiêu đề: **mọi mục mới bắt đầu bằng `## YYYY-MM-DD — `** (130/135 đã theo; 5 ngoại lệ để nguyên, không sửa hồi tố) | 1 dòng vào `QUY TẮC TÁI LẬP` | grep theo ngày deterministic; là **điều kiện tiên quyết** nếu sau này thật sự cần tách | 0 |

**Ngưỡng kích hoạt xem lại (nêu trước, không mở lại tuỳ hứng):** nếu file vượt **~1,0 MB** hoặc
**>250 mục**, phương án đúng KHÔNG phải OKF 1-mục-1-file mà là **cắt theo NỬA NĂM**
(`data/results_registry_2026H1.md` + stub redirect), vì nó giữ nguyên bản chất ledger, giữ chuỗi
supersede trong cùng file, và **không thêm quyết định đặt tên nào** vào quy trình ghi.

**KHÔNG đề xuất** archive mục cũ theo `coding_guidelines §8b`: các pin đã bị thay (28,26 / 28,05 /
28,82 / 27,84 / 27,22 / 27,16) là **bằng chứng attribution vintage** đang được trích dẫn sống
(`canonical.md`, `context_pack.md`, mục RE-PIN 07-29 phân rã 3 chân dựa vào chúng) — §8b nói rõ
không xoá theo tuổi khi còn giá trị bằng chứng.

---

## 8. Điều tôi KHÔNG kiểm được (nêu thẳng)

- **Không đo được tần suất `Read()` thật** trên file này (không có log truy cập) ⇒ lợi ích chống
  read-cost của mọi phương án, kể cả T1, là **suy luận**, không phải số đo. Nếu Mike có cách đếm
  (transcript scan), con số đó có thể lật ngược cân nhắc §5.
- Không kiểm chéo với `arch-reviewer`/`quant-skeptic` trong job này (brief chỉ yêu cầu phân tích).
