# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Taylor.

> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Taylor ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Taylor/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Taylor_history.md` — không mất, không auto-load.

- [2026-10-20T16:03:56Z] [survivorship V1/V2/V3 10-20] XONG job Taylor_20261020_153324 @4a2cf8643: V1A -0,2..-1,0pp (2/4), V2 dưới sàn, V3 +0,3..+0,5pp (2/4). Mở: quant-skeptic verify; ~44% mua LAG ở mã ADV3M<=0 bỏ trần thanh khoản — chờ Mike/user. (Thay dòng ĐANG DỞ 122917.)
- [2026-10-20T16:26:21Z] ĐANG DỞ job Taylor_20261020_162558 (V1D/V1E/V3A'/V4 survivorship-volzero, thư mục research/survivorship_volzero_20261020) | NEXT: đọc REPORT_V1/V3 + eng diff, viết PREREG_V1D_V1E/V3Ap/V4
- [2026-10-20T16:29:32Z] ĐANG DỞ job Taylor_20261020_162558: batch nohup run_batch_162558.sh (24 run, 2 song song, log logs/run_batch_162558.log); prereg 4482feb6a, engine dbe28b85f | NEXT: V4 script, rồi v_metrics V1D V1D0 V1E20 V1E60 V3Ap + md5 ctlG, REPORT_V1D_V1E.md
- [2026-10-20T17:08:54Z] ĐANG DỞ job Taylor_20261020_162558: V4 finding đã post (33323d6dc); V1D/V1D0 đo xong (v_metrics). Batch còn V1E20/V1E60/V3Ap/ctlG | NEXT: v_metrics + v1de_describe, md5 ctlG vs pin, REPORT_V1D_V1E.md, 3 finding + tổng
- [2026-10-20T18:01:49Z] [survivorship-volzero V1D/V1E/V3A'/V4 10-21] XONG job Taylor_20261020_162558 (REPORT_V1D_V1E.md, e8a0550b1) — chờ Mike/skeptic verify; mở: trần tham gia theo phiên nhân quả chưa đo
- [2026-10-21T02:25:20Z] ĐANG DỞ job Taylor_20261021_022501 (vnindex_tr sealed rows 12-13/10 bị dựng lại, G1/G4 fail) | NEXT: RCA built_at/vintage, vá worktree, selfcheck
- [2026-10-21T02:30:16Z] [vnindex-tr 10-21] job Taylor_20261021_022501 XONG: vá G1 tail-rechain nhánh fix/vnindex-tr-tail-rechain-20261021 @94c5fddb0 (chờ arch-review Mike). Mở: đường --restate-sealed cho 12/13/10 + ack 14/10 + seal-guard G4 — chờ user.
- [2026-10-21T04:31:09Z] [survivorship-volzero F1-F3 10-21] XONG commit c7cef9792, chờ Mike/skeptic. Mở: phần dư OOS F2 (+39..+64 tỷ lô khớp được) chưa phân rã; F2F1 hậu kỳ cần prereg nếu dùng.
