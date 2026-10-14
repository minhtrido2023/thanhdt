# ARCH-REVIEW — `feat/fund-history-lock-20261014` @ `3642e43a1` (base `04ddef5f6`)

Chép từ báo cáo arch-reviewer (Mike gọi 2026-10-14 ~10:15 ICT, một lần toàn nhánh). Harness mutant của
reviewer: `/tmp/arch_fl/mut/mut.py` (bản chép trong thư mục này nếu còn: `mut.py`, `demo/`).

## VERDICT: NEEDS_CHANGES — 1 CHẶN (B1), phần còn lại NÊN SỬA / GHI CHÚ; 15/41 mutant mới sống

Đúng, GIỮ NGUYÊN: hai sửa dữ liệu dựng lại độc lập khớp ≤ 1 đ (SpaceX 07-02 NAV đúng = 990.304.454–455;
chèn 08-06 = 950.871.323 / 937.070.077); kho bất biến (khoá file, ghi nguyên tử + fsync, manifest trước
file sau, seal dưới TZ lạ chốt đúng "hôm qua ICT", md5 141f8bb3…); `apply` ràng md5 + idempotent trên
bản sao (giữ CRLF); khi KHÔNG truyền cờ mới thì `daily_nav_snapshot.py` cho đầu ra GIỐNG TỪNG BYTE master
(4 ngày ước tính); 5 selfcheck khép kín dưới strace (không mở file nào dưới data/); chính sách điểm 4
cài đúng (biên `<0,05` bậc 1 · `0,05..0,5` bậc 2 · `>0,5` bậc 3; lấy số lớn nhất của lệch NAV% và lệch
tỉ suất); bảng D đúng (không số chính nào đổi); 78/78 mutant của tác giả tái lập.

## Chẩn đoán SpaceX 07-02 (sửa diễn đạt)
400 VGC = 4 lệnh THẬT khác nhau (110581, 110721, 126401, 126631; cùng loanPackageId 1841) — KHÔNG có lô
bị cộng hai lần. Lỗi thật: bản ghi số dư 09:46:35 lấy TRƯỚC khi lệnh 126631 bị khoá tiền (DNSE trừ
`totalCash` ngay lúc ĐẶT lệnh, không đợi khớp; lệnh tạo 09:46:35,295). Chữ "đếm trùng" trong file đính
chính là diễn đạt sai; SỐ TIỀN sửa đúng. VHM 77.100 CÓ nguồn thứ hai: `marketPrice` broker sáng 08-07 =
77.100 (feed broker trễ 1 phiên).

## Bảng lỗi
| # | Mức | File:dòng | Tái hiện | Việc phải làm |
|---|---|---|---|---|
| B1 | **CHẶN merge** | `daily_nav_snapshot.py:1222-1234`, `:1496-1530`, `:286-287`; help `:1099-1103`; test `nav_ledger_vault_selfcheck.py:744-752` | `--from-raw --date 2026-08-06 --raw-price-override VHM=77100 --raw-price-override ACB=30000` ⇒ rc=0, NAV 962.646.323 (đúng 950.871.323). Nhánh `stale_market_price` (:286-287) chấp nhận mọi giá thay khi marketPrice broker = giá phiên trước (ngày 08-06 cả danh mục như vậy); còn các lối `early_credit`, `corp_action_recovered`, `cash_div_confirmed`, thiếu marketPrice; ghi chú in sai nhãn "dùng BQ Price 30,000"; V8 chỉ kiểm CHUỖI VĂN BẢN trong code; 7/8 mutant Sa–Sh sống; nav_source ghi MÃ=GIÁ nhưng không ghi bằng chứng (bằng chứng chỉ nằm trong nav_snapshot JSON, bị ghi đè khi chạy lại) | Hoặc kiểm tường minh \|giá thay − marketPrice\|/marketPrice ≤ 5% (BẮT BUỘC có marketPrice) TRƯỚC `classify_raw_price_gap`, không nhánh thoát, sai ⇒ rc=2, kèm test HÀNH VI chạy main() trên fixture dnse_raw; HOẶC gỡ hẳn cờ (chèn 08-06 qua file đính chính, không cần cờ). Sửa help + README |
| B2 | NÊN SỬA trước thao tác thật | `nav_unit_ledger.py:347-349`, `fund_restatement.py:607-611` | `WC_ROOT=<sandbox A>` + `--nav-dir <sandbox B>` ⇒ `apply` ghi không cần `--real-data`; `--seal` vào thư mục "thật" chạy chế độ thường (không manifest, không cổng; dòng 08-24 chốt không ai nhận) | So thêm realpath canonical cố định `/home/trido/thanhdt/WorkingClaude/data/execution_logs` hoặc coi mọi thư mục có `dnse_raw_*.jsonl` là dữ liệu thật |
| B3 | HỎI USER | `corrections/cash_identity_acks_PROPOSED.json` | bản đề xuất đổi `window.from` + `evidence` nhưng giữ `confirmed_by: user 12/10` (registry: dòng bị chụp lại ⇒ lời xác nhận cũ hết hiệu lực) | user xác nhận lại khoá mới, hoặc giữ bản ghi cũ + thêm bản ghi mới `confirmed_by: Mike (đổi khoá …)` (§20) |
| B4 | NÊN SỬA | README bước "Chạy ban ngày…"; `fund_restatement.py:668-677` | khung giờ ghi nav_history thật = 19:00–21:45 (`nav_sync_retry` mỗi 15'), 19:10 (EOD), 19:50 (+2 retry); README ghi "19:05–19:15, 20:15, 23:30" SAI. Không có khoá chung với `_write_nav_history` ⇒ snapshot có thể ghi đè mất bản đính chính | chỉ áp trong 09:00–18:30 ICT; đọc lại md5 ngay trước `os.replace`; tốt hơn: dùng chung khoá file |
| B5 | HỎI USER (cron/gate mới, §11) | `nav_unit_ledger.py` docstring; `nav_period_returns` | sổ đã chốt không ai đọc: `nav_period_returns.py` đọc nav_history; nav_history bị sửa sau chốt ⇒ số công bố đổi theo, KHÔNG cảnh báo | thêm kiểm lệch chỉ-đọc (`nav_unit_ledger.py --ledger-dir data/execution_logs`) vào chuỗi tối hoặc `report_delivery_gate` |
| B6 | NÊN SỬA | `nav_unit_ledger.py:536-540`, `:671-678` | lời nhận `--accept-preclose` cho "NAV 1010 lúc 10:00" tự áp cho đính chính thành "NAV 1005 lúc 11:00" (demo `/tmp/arch_fl/demo`) | lưu lời nhận dạng {ngày: {lý do, balance_ts, nav}}; chỉ mang sang khi balance_ts và nav không đổi |
| B7 | NÊN SỬA | `fund_restatement.py:80-82`, `:365-368`, `:385-453`, docstring `:6-8` | 4 lớp âm tính giả của `impact`: (i) so "dữ liệu cũ tính lại" với "mới tính lại", KHÔNG so với số ĐÃ IN (biến động tháng 8 ZaloPay in 25,58% trong khi dữ liệu cũ tính ra 21,35%); (ii) `HEADLINE_KEYS` thiếu QTD/YTD dù §6 bắt báo cáo tháng in (cắn từ báo cáo tháng 11); (iii) đổi cột tiền/cổ phiếu/nợ mà giữ NAV ⇒ coi "không ảnh hưởng"; (iv) bỏ qua `*.bak_sent_*` (chính là bản đã gửi) và báo cáo ngày trước 08-17 chỉ có trên Discord. Tìm số bằng chuỗi chỉ bắt NAV nguyên số dòng cũ (báo cáo tuần 07-03 in "993.598.747" và "~−405 triệu" — dạng làm tròn trượt, ca này vẫn bị cờ nhờ khối số theo ngày) | thêm qtd/ytd; quét cả `*.bak_sent_*`; đổi cột ≠ nav ⇒ hàng đợi người xem; sửa docstring thành "đo tác động của THAY ĐỔI này, không đo sai số của số đã in"; tìm cả NAV mới của dòng chèn |
| B8 | NÊN SỬA (test) | selfcheck | 15 mutant sống (dưới) | thêm test cho N2, N21, G25, G26, G7, G10 (+ nhóm Sa–Sh nếu giữ cờ) |
| B9 | GHI CHÚ | dòng 07-02 sau sửa; `nav_unit_ledger.py:515` | `balance_ts` quy ước 14:45:00 trùng đúng biên đóng cửa (so sánh chặt `<`) ⇒ lọt cổng "chụp trước đóng cửa" không cần nhận tường minh | ghi quy ước vào `nav_history.md`; hoặc dùng 09:46:56 + `--accept-preclose 2026-07-02` |
| B10 | GHI CHÚ | `correction_SpaceX_AB.json` `reason` | — | sửa: lỗi = "số dư chụp TRƯỚC khi lệnh 126631 bị khoá tiền", không phải "đếm trùng" |
| B11 | GHI CHÚ | file đính chính 08-06 `evidence` | — | thêm nguồn thứ hai: marketPrice broker sáng 08-07 = 77.100 |
| B12 | GHI CHÚ | `read_manifest`; `seal(write=False)` không giữ khoá | — | manifest bị cắt dòng cuối ⇒ kẹt vĩnh viễn, chưa có runbook; lệnh chỉ-đọc chạy song song lần chốt có thể báo nhầm "chết giữa chừng" |
| B13 | GHI CHÚ | — | — | không có mốc ngoài (git/bus) cho md5 manifest ⇒ hoàn tác đồng thời file + đuôi manifest không phát hiện được; đề xuất post md5 mỗi lần chốt lên bus hoặc commit vào repo mike |
| B14 | GHI CHÚ | `cmd_apply` | — | không sao lưu byte, không lệnh lui; lui = một đính chính ngược (nhật ký chỉ-thêm) |
| B15 | GHI CHÚ | fixture `bin/fixtures/nav_unit_ledger_asof_20261013` | — | che `account_no` (account_inception.json) |
| B16 | GHI CHÚ | `agents/Taylor/research/fund_history_lock_20261014/` | thư mục untracked | `apply` ràng md5 file đính chính ⇒ commit hoặc lưu trữ trước khi chạy thật |
| B17 | GHI CHÚ (ngoài phạm vi, có từ trước) | NAV | `cashDividendReceiving` (SpaceX 9,775tr / ZaloPay 6,4535tr, không đổi suốt tháng 8) không nằm trong NAV ⇒ NAV thấp hơn ~1%, sẽ nhảy lên khi cổ tức được trả | xem riêng |

## Mutant sống (15/41 mới; chạy với WC_ROOT rỗng, gỡ TZ)
N2 `nav_unit_ledger.py restate()` bỏ khoá file · N21 `:567` không kiểm thiếu phiên ngay sau dòng đã chốt
cuối (code đúng, thiếu test) · G7 `fund_restatement.py:465` hàng đợi user trùng mục bậc 3 · G10 `:343`
báo cáo tháng đặt tên theo 1 ngày ⇒ kỳ còn 1 ngày · G11 `:632` "đã áp" không kiểm md5 (gần tương đương) ·
G19 `:220` `delete` không cần `expect` (vẫn bị chặn nhưng bằng `KeyError` — chẩn đoán sai §29) · G25
`:407-409` số chính xuất hiện/biến mất giữa hai phía ⇒ bậc 0 thay vì vô cực · G26 `:662` nhận nhầm bản
ghi nhật ký của đính chính khác là "đang dở" ⇒ mất bản ghi nhật ký · Sa Sb Sc Sd Se Sf Sh = khối giá thay
`daily_nav_snapshot.py main()` (lách cổng, mất bằng chứng, không chặn mã không giữ, `nav_source` rỗng, giá
bị ghi đè, lỗi chỉ in rồi chạy tiếp, giá thay bị bỏ qua). Chết: Sg và 26 mutant còn lại.

## Chuỗi thao tác dữ liệu thật 0-9 của tác giả — đúng thứ tự, cần bổ sung
1. sửa khung giờ cấm (B4) · 2. chạy từ cây canonical, gỡ `WC_ROOT` (B2) · 3. bước "trình user" phải thêm:
đổi khoá lời xác nhận (B3) + biến động ZaloPay tháng 8 25,58 → 18,27 · 4. commit thư mục `corrections/` trước
(B16) · 5. bước kiểm sau: so diff với bản sao lưu (đúng 2 dòng) + chạy `cash_identity` cho CẢ ZaloPay · 6.
ĐỢI ≥ 1 chu kỳ 19:10 sau `apply`, kiểm dòng 07-02/08-06 còn nguyên, rồi mới chốt (chốt gần như không đảo
ngược — sau đó chỉ còn đường đính chính) · 7. ghi rõ đường lui (trước chốt = khôi phục bản sao lưu + thêm
đính chính ngược vào nhật ký; sau chốt = chỉ đường đính chính) · 8. lên lịch "dòng ghi chú ở báo cáo kế tiếp"
cho các mục bậc 2.

## Phân loại
Mike/agent sửa được (nhỏ, có file:dòng): B1 (cần test hành vi), B2, B4, B6, B7, B8, B9, B10, B11, B14, B15,
B16. Phải hỏi user: B3 (đổi khoá lời xác nhận user đã ký), B5 (cron/gate mới đọc sổ chốt), quyết định đính
chính biến động tháng 8 ZaloPay (bậc 3 so với số in) và ghi chú SpaceX (12,37→12,80; 17,3→17,4), thời điểm
chốt sổ thật.

## Chưa kiểm được
Thời gian giả quanh nửa đêm ICT (không có faketime; chỉ qua mã + một lượt chạy thật lúc ngày máy NY ≠ ICT);
không tái lập được 12,37 / 25,58 đã in (kể cả từ bản sao lưu trước 09-13: ra 12,04/24,78 hoặc 9,21/25,24 ⇒
độ lệch có từ trước nhánh này — phương pháp tính lúc in chưa rõ); sao kê DNSE tháng 7.
