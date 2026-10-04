# Working memory — Wags
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Wags.

# Working memory — Wags
> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Wags ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Wags/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Wags_history.md` — không mất, không auto-load.

- [2026-09-28T05:47:35Z] [2026-09-28] coord-2026-09-28: question Taylor/pnj-trong-ro-custom30v-live KHONG phai loi dieu phoi — PNJ van la thanh vien SONG ro custom30V (verify 3 artifact: publish.csv effective_to rong w0,7075%; park_trim_SpaceX BLOCKED_ALL_NAMES ly do LOT-SIZE; ZaloPay NO_TRIM). Ca 3 option A/B/C deu cham duong dat lenh => USER quyet. Da ack triaged-needs-human suppress_days=7 + post A/B/C vao trading_daily. files_changed=[]. CHO USER; het 7 ngay tu noi lai.
- [2026-09-29T01:23:27Z] [2026-09-29] coord-2026-09-29 XONG. Q closerepair-fix-approval-needed KHONG cho duyet — Taylor da merge 3c55c249 tu 09-28, chi thieu event answer (Pattern B lan 2/thang); da dong bang answer + verify checker sach. Q classifier-blocks-headless chua phai loi dieu phoi: da lam option C (runbook, commit 0bf97d25), ack suppress 7d, A/B CHO USER.
BAI HOC: Pattern B tai dien vi khong ai coi 'merge xong' la su kien phai dong question. Runbook gio ghi buoc 3 tuong minh; neu van tai dien lan 3 thi phai wire TU DONG (vd post-merge hook quet bus question cung branch name) chu khong dua vao ky luat.
CHO USER/MIKE ngoai pham vi: plan SpaceX 2026-09-29 NOT_APPROVED 19 lenh luc 08:22 ICT — preflight se HOLD.
- [2026-09-29T08:19:54Z] [2026-09-29 chiều] coord-2026-09-29 (job 080835): Q Winston/sell-loanpackage-deal-not-found-zalopay KHONG cho quyet dinh — user duyet Discord 14:34, fix merge 14:53 (d51c735e), chi thieu event answer (Pattern B lan 3). Da dong + WIRE TU DONG dung cam ket: bin/question_commit_hint.py (quet git log 2 repo -> goi y commit-resolver cho cau hoi treo, vao prompt wags_autofix canh KNOWN_ISSUE), selfcheck 15/15, 4/4 mutant chet, commit a9c4a421+f63c12ff.
BAI HOC 1: 'git add <file>' KHONG gioi han pham vi commit — index dung chung, phien khac stage truoc thi 'git commit' cuon het. Luon 'git commit -o <files>'. (a9c4a421 cuon 2 file Taylor; Taylor ghi 85b744a1 giai trinh, khong mat gi.)
BAI HOC 2: cong cu match theo tu khoa se TU NHAN DIEN chinh commit gioi thieu no (message liet ke topic lam vi du) — phai co tu-loai-tru + luat meta-commit ngay tu dau.
- [2026-09-30T02:16:42Z] [2026-09-30] coord-2026-09-30 (job 020001, resume): option B da wire BAT BUOC vao dispatch.sh ca 2 duong hoan tat (ff340ea8 + b1bc0dec va 5/5 required_change). Q goc da RESOLVED boi decision cua user 01:49Z (wags_bus_question_pending rc=1). DANG DO: cho arch-review vong 2 tren b1bc0dec; sau do ghi finding + xong.
BAI HOC: append text phu vao $logfile cua job LA THAY DOI VAN BAN USER-FACING — dispatch.sh chup 'tail -c 500 $logfile' lam preview Discord va 'head -c 400' lam cb_summary AUTO-CALLBACK. Hint 812B > cua so 500B nen an sach ket luan agent, va CHI xay ra khi hint non-empty => smoke test voi hint RONG khong the bat duoc. Luat: moi khi ghi them vao artifact cua nguoi khac, grep xem co ai CHUP cua so cua artifact do khong, va test o trang thai artifact CO NOI DUNG.
- [2026-09-30T02:38:15Z] [2026-09-30] coord-2026-09-30 XONG (job 020001). Hint dong-vong-bus gio goi BAT BUOC o ca 2 duong hoan tat dispatch.sh; arch-review CONFIRMED vong 3 (ff340ea8/b1bc0dec/9093f794/7d3f4991); 2 question escalation da dong. Khong con viec treo cua job nay.
BAI HOC: append text phu vao $logfile cua job LA doi VAN BAN USER-FACING — dispatch.sh chup 'tail -c 500 $logfile' lam ping Discord, 'head -c 400' lam cb_summary AUTO-CALLBACK. Hint chi non-empty khi CO question khop => smoke test voi hint RONG ve nguyen tac khong the bat duoc bug nay. LUAT: truoc khi ghi them vao artifact cua nguoi khac, grep xem co ai CHUP CUA SO artifact do khong, va test o trang thai artifact CO NOI DUNG.
BAI HOC 2: bo test 'loai theo SUBSTRING' de tu mo cua thoat — clause 'tail -c not in line' khong bao ve gi ma cho mutant nup vao dong co chua tail -c. Loai theo INDEX/danh tinh, dung theo chuoi.
- [2026-10-01T01:21:25Z] [2026-10-01] coord-2026-10-01: Q label-asof DONG bang answer (cron tu ap schema, Pattern B lan 4). Q duyet-merge-macro-killswitch-a-wiring CHO USER (ack suppress 3d, branch e8d791e9 chua merge). files_changed=[].
- [2026-10-01T05:46:07Z] [2026-10-01 chieu] coord-2026-10-01 (job 054510): Q Taylor/alphalens-buoc-ke-dong-hay-rnd CHO USER (A/B/C), ack suppress 7d, da post topic Taylor 1521735922066919515. files_changed=[].
- [2026-10-02T01:21:04Z] [2026-10-02] coord-2026-10-02: Q spacex-tpb-reconcile DONG bang answer (Pattern B lan 5). Q tpb-price-frame-gate CHO USER/TAYLOR (A patch price_frame cash_div / B confirm tay / C cho plan 10-03), ack suppress 2d, da post trading_daily. files_changed=[].
- [2026-10-03T06:54:54Z] Chờ Mike merge branch fix/report-prompt-port-20261003 (1b9d4d46); sau merge: git worktree remove agents/Wags/wt-reportport-1003
- [2026-10-03T08:28:35Z] [2026-10-03] Chờ Mike merge fix/report-prompt-r2-20261003 (1afc0c59, worktree agents/Wags/wt-reportr2-1003); sau merge: git worktree remove wt-reportr2-1003 (và wt-reportport-1003 nếu port đã merge)
- [2026-10-04T02:52:44Z] [2026-10-04] Cho Mike merge fix/exdate-forecast-feed-status-20261004 (agents/Wags/wt-exdate-feed-1004) TRUOC 05/10 19:00 ICT; sau merge: git worktree remove wt-exdate-feed-1004
