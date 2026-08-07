# 2026-08-07 — Bước merge để sót lệnh nguồn JIT_UNPARK → plan đã user duyệt sẽ BÁN TRÙNG 1.600cp; không tầng tự động nào chặn

**What happened.** Wags (job `Wags_20260807_054509`, dispatch triage question tồn đọng) mở
`plan_SpaceX_2026-08-07.json` / `plan_ZaloPay_2026-08-07.json` — đã `approved_by=user (John)`
lúc 12:36 ICT, giờ chạy `SELL@13:05` — và thấy orders[] chứa **cả lệnh gộp lẫn lệnh nguồn**:

- Lệnh gộp `SELL-<mã>-PARK-nn` mang `merged_from={L1_park_trim_qty, L2_jit_unpark_qty,
  sellable_at_calc}` ⇒ phần L2 (jit_unpark) **đã nằm trong** qty của lệnh gộp.
- 15 lệnh nguồn `SELL-JIT-PARK-<mã>-01` (`play_type=JIT_UNPARK`) **vẫn còn** trong orders[].

Ví dụ SpaceX ACB: gộp 400 (=300 L1 + 100 L2) + `SELL-JIT-PARK-ACB-01` 100 ⇒ **gửi 500cp**
thay vì 400. Tổng bán thừa: **SpaceX 1.200cp** (ACB/BID/CTG/HDB/LPB/SHB/TCB/VCB/VHM/VPB mỗi mã
100, MBB 200) + **ZaloPay 400cp** (BID/MBB/VCB/VHM mỗi mã 100). ZaloPay VHM còn vượt chính
`sellable_at_calc` của nó (300) khi gửi 400.

**Root cause.** Bước gộp (`agents/DollarBill/merge_three_in_one_20260807.py`, chỉ thị user
"gộp 2 nguồn đề xuất bán cùng mã thành 1 lệnh") **thêm** lệnh gộp vào orders[] nhưng **không
xoá** lệnh nguồn L2 đã được cộng vào. Đây là lỗi kinh điển của phép biến đổi kiểu
"append-derived, forget-to-remove-source" trên một mảng.

**Vì sao không ai chặn.** Không tầng nào kiểm bất biến *nội dung* của orders[]: preflight chỉ
đếm số lệnh + trạng thái approve; approval gate và funding gate của bot đều không so lệnh với
nhau. Plan lại đã được user duyệt (nội dung đúng ở thời điểm duyệt về mặt ý định, sai về mặt
dữ liệu) nên approval gate mở đường. Phát hiện được là nhờ **người đọc file**, không phải
automation — đúng dạng điểm mù đã lặp lại nhiều lần trong fleet.

**Escalate + fix.** Wags KHÔNG tự sửa plan (vùng cấm, mandate 2026-07-07): ghi bus event
`error` + notify `plan_approval` và `trading_daily` (12:47), dispatch `DollarBill_20260807_054858`
kèm bằng chứng và cách sửa. DollarBill xác nhận và xoá 15 lệnh sót lúc **12:50:15** — trước
giờ chạy 13:05 khoảng 15 phút. Sau sửa: SpaceX 26→15 lệnh, ZaloPay 13→9 lệnh, `approved_at`
giữ nguyên (thay đổi là GIẢM lệnh). Không lệnh nào bị đặt sai: không có journal/exec
SpaceX/ZaloPay hôm nay tính đến 12:51.

**Fix tooling (Wags, trong phạm vi checker).** Thêm 2 bất biến lệnh vào
`bin/preflight_check.sh`:
- `MERGE_STALE_SRC:<mã>` — có lệnh mang `merged_from` mà **vẫn còn** lệnh khác cùng
  `(side, ticker)` ⇒ bước gộp để sót nguồn. Chữ ký chính xác của sự cố này.
- `SELL_GT_SELLABLE:<mã>(gửi>cap)` — tổng qty BÁN 1 mã vượt `sellable_at_calc` mà chính plan
  ghi ra. Bất biến độc lập, bắt được cả ca ZaloPay VHM.

Selfcheck `bin/preflight_order_invariants_selfcheck.py` (9 assert) **trích khối python thật
đang nằm trong preflight_check.sh** rồi chạy khối đó — không chép lại logic; khối bị đổi/di
chuyển thì selfcheck exit 1 chứ không im lặng pass. Đối chứng `PF_SRC=<HEAD cũ>` ⇒ **FAIL
3/9** đúng 3 assert mô tả điểm mù (chứng minh check mới thật sự thêm năng lực, không phải
assert tự thoả). Preflight thật chạy end-to-end 2 account trên plan đã sửa ⇒ GREEN, 0 báo
động giả.

**Lessons.**
1. Phép biến đổi orders[] kiểu "gộp/derive" phải được kiểm bằng **bất biến trên kết quả**
   (không lệnh nguồn nào sót, không bán quá sellable), không phải bằng niềm tin vào script gộp.
   Script gộp là thứ mới nhất, chưa từng chạy production — chính nó cần bị nghi ngờ nhất.
2. Chữ "user đã duyệt" KHÔNG có nghĩa nội dung đúng. Approval xác nhận **ý định**; bất biến dữ
   liệu vẫn phải do máy kiểm. Sửa plan sau khi duyệt theo hướng GIẢM lệnh thì giữ approval
   được, nhưng phải báo lại topic duyệt plan.
3. Việc triage question tồn đọng có giá trị vượt xa việc đóng question: cả 2 question
   (Taylor 03:27, Winston 02:07) đều đã tự hết hiệu lực khi user duyệt 12:36 — nhưng đọc lại
   artifact thật để xác nhận điều đó là thứ tìm ra bug. Đừng đóng question bằng suy luận
   trạng thái, hãy mở file ra xem.
