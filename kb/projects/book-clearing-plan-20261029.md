# Clearing giữa các sổ (PARK ↔ LAG/BAL) — kế hoạch thiết kế (user yêu cầu 29/10/2026 00:32 ICT)

**Trạng thái: THIẾT KẾ, CHƯA CODE.** Chạm đường tiền (sổ lô → quyết định bán) nên cần user duyệt + quant/arch-review trước khi wire.

## Vấn đề
Broker (DNSE) không có "sổ"; sổ PARK/LAG/BAL chỉ là NHÃN trong sổ lô FIFO (`park_holdings.LotBook`, dựng lại từ journal `FILL.book`). Khi LAG mua mã X trong lúc PARK đang giữ X và định bán, hệ thống hiện mua đủ và bán đủ → trả 2 chiều phí + thuế + cắn spread hai lần cho cùng số cổ phiếu.
Ca thật 26-29/10 (SpaceX VPB): PARK 286cp (160@07-02, 126@08-11) trong khi LAG mua 1.500cp (26/10, KHÔNG trừ phần đang có); plan 29/10 lại bán PARK 200cp (L1 park_trim, target park 0). Chi phí vòng tròn trên phần chồng 286cp ≈ 0,097% mua + 0,097% bán + 0,1% thuế = **0,294% ≈ 20k VND** (nhỏ; giá trị chính là sổ sạch + không cắn spread 2 lần, lớn hơn khi PARK bật lại).

## Nguyên tắc
Clearing = **chuyển nhãn lô trong sổ (BOOK_TRANSFER)**, KHÔNG phát lệnh, không phí, không thuế; tổng qty mỗi mã không đổi nên reconcile broker vẫn khớp. Phần còn lại (thiếu/dư) mới mua/bán thật — đúng chỉ đạo user.

## Thiết kế
1. **Sổ lô** (`park_holdings.py`): sự kiện journal mới `BOOK_TRANSFER` (ticker, qty, from_book, to_book, ref_price, id idempotent). `LotBook.transfer()` trừ lô from_book theo cùng thứ tự FIFO với `sell()`, thêm lô to_book MỚI cuối sổ: `entry_date` = ngày hiệu lực chuyển (đồng hồ T+25/T+45 của LAG/BAL bắt đầu từ lúc vào sổ LAG, KHÔNG thừa kế ngày PARK cũ — tránh bị auto-exit bán ngay như lỗi 28/10), `cost_price` = giá tham chiếu (P&L sổ nguồn chốt sổ tại giá ref; giá vốn thật broker không đổi).
2. **Planner** `bin/clear_books.py` (chạy cuối chuỗi plan, SAU `auto_exit_inject`/`merge_park_orders`, TRƯỚC `send_plan_report` 21:00): với mỗi mã ghép (a) lệnh BÁN book A + lệnh MUA book B trong CÙNG plan, (b) lượng PARK đang cần xả (park_trim target / L2 jit) + lệnh MUA LAG/BAL cùng mã. `m = min(buy, phần-PARK-xả, sellable T+2)`; ghi `plan["book_transfers"]` + giảm qty lệnh mua/bán đi m (giữ bội lô 100; số lẻ chuyển nhãn vẫn được vì không đặt lệnh). Hiển thị rõ cho user trong báo cáo duyệt plan ("chuyển PARK→LAG 286cp VPB, tiết kiệm ~Xđ").
3. **Thực thi**: bước riêng `apply_book_transfers.py` chạy trước `bot_execute` (KHÔNG sửa `executor.py` lõi), idempotent theo id (§5), kiểm broker qty ≥ transfer, ghi journal `BOOK_TRANSFER`. Không thực hiện được ⇒ **fail-safe-pause mã đó + báo bus**, không đoán.
4. **Điều kiện chặn**: mã excluded/unverified/BANNED; lô quyền mua đang khoá; PARK chưa sellable (T+2); chuyển chỉ khi lệnh MUA đích đã qua đủ cổng của book đích (8L≤3, DD ack, forensic, ADV); không chuyển chéo account; LAG→PARK (khi park bật, LAG thoát mã nằm trong rổ park) làm đối xứng, giai đoạn 2.
5. **Cùng sổ**: LAG thoát lô cũ T+25 cùng ngày LAG vào lô mới cùng mã = "roll" (giai đoạn 2, cần quant-skeptic vì lệch spec pinned R3).
6. **Phải sửa theo**: `merge_park_orders` (bất biến Σ sell ≤ sellable), `preflight_check`/`preflight_order_invariants`, `auto_exit_inject` (đọc lô sau chuyển), `portfolio_status` (hiển thị), §23 quét selfcheck rộng; thêm selfcheck + mutant: ca VPB SpaceX, nhiều đêm, idempotent chạy lại, thiếu sellable, lô quyền.

## Ca cụ thể phiên 29/10 (quyết định user)
Lệnh MUA LAG 1.500cp đã khớp từ 26/10 nên **cơ hội tiết kiệm đã mất** (muộn). Chuyển 286cp PARK→LAG lúc này chỉ để LAG VPB = 1.786cp, vượt sizing 1.500 → vẫn phải bán 286cp. Hai lựa chọn:
- **A (khuyến nghị)**: giữ plan: bán PARK 200cp ngày 29/10 (+86 sau), LAG về đúng 1.500cp sizing. Chi phí ~20k, không đụng gì, không cần cơ chế chưa tồn tại.
- B: bỏ lệnh bán PARK, giữ 286cp thành LAG ⇒ LAG VPB +19% so sizing (~6,7tr). Tiết kiệm ~20k nhưng sai spec và đêm nay chưa có cơ chế chuyển nhãn.
ZaloPay VPB: PARK 30cp dưới ngưỡng trim (không bán) → không có gì để clearing; lệnh bán LAG 282cp là lô T+25 quá hạn theo luật, không liên quan PARK.

## Lộ trình đề xuất
G1 (Taylor, Opus high, worktree): ledger `BOOK_TRANSFER` + `clear_books.py` ở chế độ **SHADOW** (chỉ báo "lẽ ra chuyển Xcp, tiết kiệm Yđ" vào báo cáo plan, không đổi lệnh) chạy ≥ vài phiên; G2: quant-skeptic + arch-review; G3: user duyệt bật thật (cạnh `apply_book_transfers.py`); G4: giai đoạn 2 (LAG→PARK, roll).
