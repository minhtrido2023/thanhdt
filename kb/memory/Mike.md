# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái cuối ngày 2026-09-29 (17:45 ICT)
- **Retro 2026-09-29 ĐÃ ĐÓNG** (`kb/incidents/retro/retro-2026-09-29.md`, commit `44ee1c26`,
  Wags verify GAPS FOUND → đã bổ sung sự cố #4). 4 sự cố: #1 ZaloPay `PLACE_FAIL` deal-not-found
  (2.628 lỗi, 6/15 lệnh bán chặn, TÁI DIỄN lớp lỗi loanPackageId 08-10 — **VÁ HOÀN CHỈNH TRONG
  NGÀY**, user duyệt 14:34 ICT, merge `d51c735e`/`bdc10ae0`); #2 selfcheck corp-action unpack
  lỗi thời che 42 assertion (nửa vá, nghĩa test còn chờ chủ sở hữu quyết); #3 Wags's
  `question_commit_hint.py` bị arch-reviewer NEEDS_CHANGES ngay trên ca sinh ra nó; #4 (gap Wags
  bổ sung) AlphaLens paper report double-count FPT +9,98pp — Taylor tự phát hiện+tự vá+quant-
  skeptic CONFIRMED 2 lần trong phiên.
- **ESCALATE MỚI** `retro-pattern-recurring-bus-question-closure-gap-real-fix-no-answer-event`
  — pattern bus-closure channel gap tái diễn LẦN 3 (2 lần trong 1 ngày 09-29), sau 2 retro liên
  tiếp (09-27, 09-28) đã cảnh báo. 3 phương án chờ user chọn: (A) cưỡng chế cơ học gate hậu-merge,
  (B) hoàn thiện `question_commit_hint.py` (2 gap arch-reviewer chỉ ra), (C) chỉ tăng kỷ luật —
  đã thử, không đủ. Khuyến nghị B trước.

## Còn mở (cần user quyết / chưa làm)
- Escalation bus-closure-gap (xem trên) — MỚI, chờ user chọn A/B/C.
- Escalation classifier-block (mở 09-28, `suppress_days=7`) — vẫn trong cửa sổ ack, chờ user.
- VNM `exright_date` lệch 1 phiên (`tav2_bq.corporate_action`) — cần dispatch Winston xác minh,
  chưa ai giao việc.
- `Taylor/pnj-trong-ro-custom30v-live-can-user-duyet-chan` — ack suppress 7 ngày (mở 09-27),
  chờ user chọn A/B/C.
- Sự cố #2 (09-29) — chủ sở hữu cổng corp-action (Taylor/quant-skeptic) cần quyết nghĩa test
  `filled==200` lỗi thời hay cổng chặn oan.
- File incident `2026-09-29-zalopay-sell-deal-not-found-loanpackage-1826.md` tiêu đề còn STALE
  ("CHƯA VÁ") — cần cập nhật phản ánh đã vá xong 14:53 ICT cùng ngày.
- Fail-open CÒN LẠI (đợt-2 kiểm kê `plan.py`/`executor.py` một số handler) — ranh giới cứng,
  cần user ký từng site.
- `rating8l_icb_pit_selfcheck.py` MergeError dtype — tiền tồn, chưa ai sửa.

## Việc theo lịch
- Xoá cron FiinPro (đã qua hạn 28/09 — làm sớm). Đóng AlphaLens 30/09 + ghi registry.
- Review quý: measurement-integrity audit ~2026-12-27; Bobby structural-risk ~2026-11-26.

## Bẫy đã ghi lại (đừng cắn lần nữa)
- Selfcheck neo bản cũ bằng `HEAD`/`main` ⇒ sau merge FAIL vĩnh viễn. Luôn neo `<commit-vá>^`.
- Selfcheck hardcode gốc canonical ⇒ chạy từ worktree test MASTER thay vì code đang sửa.
- Guard chống ghi-đè production OPT-IN thủ công không đủ an toàn — phải tự suy từ path/context.
- Đóng 1 `question` do AGENT KHÁC đăng lên bus vẫn cần 1 `answer`/`decision` ngắn TRÊN BUS — pattern
  này đã lặp 3 lần (09-27, 09-28, 09-29×2) — nay ĐÃ ESCALATE, chờ user chọn fix cơ học.
- Đổi signature hàm lõi (vd trả thêm 1 giá trị) phải quét HẾT call-site test cũ đang unpack cũ —
  gap thật 09-29 (#2), khớp đúng khuôn §23.
- Safety-net cũ (viết trước khi có cơ chế mới) phải điều kiện hoá lại khi cơ chế mới go-live, nếu
  không sẽ double-apply cùng 1 sự kiện — gap thật 09-29 (#4, đòn tấn công #8 quant-skeptic).
- `git show <rev>:<path>` tính path từ GỐC REPO, `git diff … -- <pathspec>` tính từ CWD — dùng
  `:(top)` + `rev-parse --show-prefix`.

