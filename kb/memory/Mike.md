# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-17T08:23 ICT (2 plan hôm nay ĐÃ DUYỆT, chờ phiên sáng)

## Plan hôm nay (08-17) — ĐÃ DUYỆT, chờ chạy ~09:05 ICT
- Cả 2 file plan đã có approved_by (John Dinh qua Discord, Mike ghi hộ 08:23 ICT). Verify qua
  production loader: block_reason=None cả 2 account.
- SpaceX: mua TV1 500cp @20.640đ. ZaloPay: 0 lệnh (HOLD ALL).
- THEO DÕI: phiên sáng nay chạy có đúng không (journal, fill TV1 — đây cũng là dịp quan sát
  lệnh TV1 dùng cơ chế TRƯỚC Rule A fix, ceiling_rule=None, không phải bug).

## ⚠️ GDKHQ dry-run D1-D3 CHƯA setup (gap thật, tự theo dõi)
- BID có GDKHQ THẬT hôm nay (đã áp đúng vào sổ lô qua corp_actions.json có sẵn, không liên quan
  D1-D3). apply_exdate_gate() chưa wire vào executor/bot thật — dry-run mà user chọn 08-16 chưa
  từng chạy. Không hại hôm nay (BID không có lệnh nào). Cần quyết setup dry-run trước GDKHQ tiếp
  theo (VIX 08-20) hoặc để bàn sau.

## Việc còn hở khác (chưa xử lý, không khẩn)
1. verify_account_snapshot.py trả cost-basis 0 cho CẢ 2 account ("no fill history legacy") —
   pipeline §6 gap thật, cần điều tra.
2. book_breakdown_current trong plan file ghi nhãn sai (SCL không phải LAG, thật ra LÀ LAG) —
   sửa ở lần lập plan kế tiếp.
3. Selfcheck-masking E5 capit_lever — chưa xác nhận đã vá.
4. plan-dd-check-string fix (commit 9a9dbb1) — chờ xác nhận phiên LIVE 08-17 (HÔM NAY).
5. EOD daily report chưa bao giờ gửi email.
6. lag_entry_anchor.py:105 — chưa vá, không khẩn.

## Bối cảnh còn hiệu lực
- dispatch-prompt-heredoc skill; dispatch job >2 phút BẮT BUỘC --bg.
- TV1 Rule A (bản fix UPCOM) đang LIVE từ 08-15, an toàn.
- CASH_VENDOR gate: giữ ĐÓNG. CAPIT margin: enabled=false.

