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

- [2026-10-22T11:01:13Z] [livermore-stock-pilot 10-22] XONG job Taylor_20261022_104625: NO-GO sát biên (a đạt AUC 0,629; b hụt ΔAUC +0,024 CI chứa 0); không wire; chờ Mike
- [2026-10-22T14:33:07Z] ĐANG DỞ job Taylor_20261022_143258: vá park_holdings.py đối soát bán tay DRI (tái dùng f0e293c30) | NEXT: đọc commit, worktree wt-park-manual-sell-20261022
- [2026-10-22T14:42:41Z] [park-holdings-manual-sell 10-22] XONG job Taylor_20261022_143258: fix/park-holdings-manual-sell-20261022 @30fe3ba7b chờ arch-review/merge
- [2026-10-22T14:52:45Z] [park-holdings-manual-sell vòng 2 10-22] XONG job Taylor_20261022_145109: @9ccb6b0fe chờ arch-review lần cuối
- [2026-10-22T15:39:25Z] [nav-snapshot-manual-fills 10-22] XONG job Taylor_20261022_153620: fix/nav-snapshot-manual-fills-20261022 chờ arch-review/merge rồi mới bù dòng NAV 21/10 (2 account) + chạy nav_loss_brake_monitor
- [2026-10-24T03:45:09Z] ĐANG DỞ job Taylor_20261024_034455: R&D dcf_rich_outlook_20261024 (DCF RICH sâu có info lợi nhuận/drift?) | NEXT: đọc dcf_valuation.py, data_registry, PIT feasibility
- [2026-10-24T03:53:50Z] [dcf-rich-outlook 10-24] XONG job Taylor_20261024_034455: RICH sâu KHÔNG báo LN xấu; drift xấu chỉ ở ROE<25%/hàng hóa; đề xuất hạ gate→WARNING cho ROE≥25%, chờ quant-skeptic+user
- [2026-10-24T04:09:41Z] ĐANG DỞ job Taylor_20261024_040927: R&D lag_runup_effect_20261024 (run-up trước công bố vs drift LAG) | NEXT: đọc lag_live_schedule.py, registry LAG, dựng event set
- [2026-10-24T04:16:08Z] [lag-runup-effect 10-24] XONG job Taylor_20261024_040927: run-up không làm yếu LAG, NO filter (DSR .56/PBO .83); giả thuyết hàng hóa×YTD>100% cần prereg
- [2026-10-24T04:50:48Z] ĐANG DỞ job Taylor_20261024_045036: dcf_rich_outlook_rerun_20261024 (5 kiểm tra ROE ngưỡng/MDE/LAG surprise/share-change/TR bench) | NEXT: copy panel+code, control
- [2026-10-24T04:56:54Z] [dcf-rich-rerun 10-24] XONG job Taylor_20261024_045036: ROE25% miễn trừ underpowered (MDE10pp); đề xuất B = đòi lý do chỉ MoS<-100% không miễn ROE; chờ user
- [2026-10-25T02:00:28Z] [spend-routing-review 10-25] XONG job Taylor_20261025_020009: no_action (opus 48/135 job, giam so voi 59/110)
