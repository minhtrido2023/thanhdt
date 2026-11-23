# BÀN GIAO — topic "DD vòng 3 — DCM DBC SZL VCP HHS" (thread 1574365262965121136)

Từ: Mike (topic cũ 1574208662719828062 "DD dựng lại rev — 4 lô", 23/11/2026 17:05 ICT). Topic cũ DỪNG — đừng poll ở đó.

## Đã xong (cố định, đừng làm lại)
- Dựng lại rev 18 ca (4 lô) XONG, sổ `kb/dd_price_zones.json` = 115 entry, selfcheck 0 lỗi, merge master (bca08acb1, c82f57d02).
  Kết quả: MSB, GAS = CONFIRMED; 16 ca còn lại = REFUTED_OPEN. Plan + bảng lô: `agents/Taylor/research/dd_rebuild_20261123/PLAN.md`.
- Sizing chuẩn V8 = 2–4% NAV/mã (user chốt 23/11).

## USER DUYỆT 23/11 17:03 ICT (2 việc)
1. **Chạy VÒNG 3 cho 5 mã: DCM, DBC, SZL, VCP, HHS** (các ca đã hết 2 vòng skeptic; user cho phép vòng 3).
2. **Sửa skill `due-diligence` (+ prompt rebuild) theo các lỗi định dạng proposal đã gặp** (user "đồng ý").

## VIỆC 1 — vòng 3 (5 job Taylor song song, như lô cũ)
Trạng thái sổ cuối mỗi mã (REFUTED_OPEN; skeptic r3 là vòng cuối của rev vừa dựng):
| Mã | Dir DD | Entry cuối sổ | Hạng mục skeptic r3 còn thiếu (nguồn: LEDGER_PROPOSAL + finding bus dd-rebuild-<MÃ>-20261123) |
|---|---|---|---|
| DCM | agents/Taylor/research/dd_DCM_20261104 | dd_date 2026-11-04 rev3 tâm 26.780 vùng 23.891–29.732, giá 30.400 | quỹ KH&CN trích 100% vs số dư 11% (tâm −1…−2,5k); ND 320/2025 + TT 20/2026 từ nguồn gốc; hạn thuế đất/giấy phép Cà Mau vs chân trời vĩnh viễn; đối chiếu chi từ quỹ với capex LCTT mã 21; tra tin pháp lý sau 05/11 |
| DBC | agents/Taylor/research/dd_DBC_20261118 | dd_date 2026-11-18 rev2 tâm 14.696 vùng 7.284–21.857, giá 16.200 | BĐS dở dang ~1.186 tỷ chưa tách khỏi vốn hoạt động (+5,4…+28,9%, tâm có thể quá THẤP); ưu đãi thuế TNDN chưa kiểm (~−13%); trích lập TSSH (−1,5…−3%); chi tuân thủ môi trường không kiểm chứng |
| SZL | agents/Taylor/research/dd_redo_20261105/SZL | dd_date 2026-10-26 rev3 tâm 25.852 vùng 22.290–29.534; skeptic ước tâm nếu sửa ~24.793 | KTPL 2026 = 20% (BCTC Q3 tr.26) chưa áp (−1.688); NQ76 5,846 không qua P&L (trừ −708 sai); cơ sở 19,85 tr cp thưởng chưa đăng ký; CP trả trước thuê đất Châu Đức/Tân Đức 217 tỷ; ý kiến KT FY2025; tổng mức Long Phước 920 |
| VCP | agents/Taylor/research/dd_VCP_20261112 | dd_date 2026-11-12 rev2 tâm 32.605 vùng 21.037–45.280, giá 37.400 | k=1,0 vs 1,127 (−9,9%); hạn PPA Cửa Đạt (−7,5…−14,2%); bảo lãnh vay Đắk Lô 1–3; NQ ĐHĐCĐ 2026; tiền cấp quyền tài nguyên nước; bản chất pool 1.000 tỷ |
| HHS | agents/Taylor/research/dd_dilution_update_20261110/HHS | dd_date 2026-11-01 rev5 (supersedes #4) tâm 13.969 (cum), vùng 12.422–15.564, giá 9.700 DƯỚI | biên cao tầng HH1–HH4 trong NC-II chưa tách (skeptic: −10…−18%); quỹ KTPL chưa tìm lại; nội dung lấy ý kiến cổ đông 14–25/12 (NQ 10/NQ-HĐQT 20/11). **Giữ BẢN SONG SONG CK holding 0% (headline, theo V4) và 27% (vùng 8.624–13.207, TRONG) — user CHƯA chốt quy ước, KHÔNG tự chọn.** forensic_flags EXCLUDE ⇒ loại khỏi candidate plan |

Cách làm (theo khuôn lô cũ): prompt gốc từng mã ở `agents/Taylor/research/dd_rebuild_20261123/prompts/<MÃ>.txt`
(sinh từ `/tmp/gen_prompts.py` — có thể đã mất; dựng lại theo cùng khuôn). Với vòng 3 phải ĐỔI các điểm sau trong prompt:
 - Bối cảnh = "rev vừa dựng, skeptic r3 vòng cuối KHÔNG CONFIRMED; user DUYỆT vòng 3": đọc skeptic/r3.json + r3_raw.md (missing_items, data_provenance) và LEDGER_PROPOSAL cũ.
 - Chỉ xử lý hạng mục SỬA ĐƯỢC từ nguồn độc lập (BCTC gốc/CBTT/BQ); hạng mục không kiểm chứng ⇒ ghi thẳng + ảnh hưởng ước lượng, đừng nhồi vào base.
 - Dựng REPORT rev mới (không ghi đè), khoá giả định + md5, mục 'Đính chính so với rev trước'.
 - Chạy `bin/dd_skeptic_run.py --dir <dir DD> --report <rev mới>` ĐÚNG 1 VÒNG (vòng 3), không hơn. Sau vòng này hết quyền: nếu vẫn không CONFIRMED → dừng, báo user.
 - KHÔNG ghi `kb/dd_price_zones.json` (5 ca song song) — chỉ ghi `LEDGER_PROPOSAL_<MÃ>.json` theo ĐẶC TẢ MỚI (VIỆC 2 bên dưới).
 - Bus finding `dd-rebuild-v3-<MÃ>-20261123`, post tóm tắt vào topic MỚI (thread 1574365262965121136) — dispatch với `--thread 1574365262965121136`.
Dispatch mẫu (từng mã; chỉ làm SAU khi đã sửa skill/đặc tả proposal ở VIỆC 2 để Taylor đọc bản mới):
`bin/dispatch.sh Taylor "$(cat <prompt>)" --bg --thread 1574365262965121136 --model opus --effort medium --timeout 5400 --wakeup-ack --write-scope "<dir DD>"`
Nhớ: ScheduleWakeup NGAY sau dispatch (poll ~10 phút, lô cũ mất 14–25 phút); `usage_limited` ≠ chết (tự resume thành job MỚI — `grep -l <id gốc> bus/jobs/*`); verify ARTIFACT (skeptic/rN.json mới nhất + md5 report khớp), đừng tin status. Kiểm `bin/usage_watch.py` (<85%) trước khi dispatch.

## VIỆC 2 — sửa skill + prompt (user đã đồng ý; làm TRƯỚC VIỆC 1 dispatch, trong worktree riêng của repo mike → arch-review không cần vì chỉ văn bản skill/prompt, nhưng đưa diff cho user trong topic)
Skill: `~/.claude/skills/due-diligence/SKILL.md` + `SKILL_ext.md` (backup `.bak_<ngày>` trước khi sửa; bản `new/` trong repo `agents/Taylor/research/dd_upgrade_20261122/B5_skill_rewrite/new/due-diligence/` cũng phải đồng bộ). Thêm mục "Đặc tả LEDGER_PROPOSAL (lỗi hay gặp)" gồm — mỗi điểm là một lỗi THẬT đã chặn selfcheck/áp sổ ở lô 1–4:
1. **dd_date/rev/supersedes/expires_on**: đính chính cùng DD ⇒ GIỮ NGUYÊN `dd_date` của entry cuối sổ, `rev` = rev cuối + 1, `supersedes` = `TICKER@dd_date#rev_cuối`, `expires_on` + `expires_basis` = của entry cuối (null làm sập `dd_price_zone_watch`). KHÔNG đặt dd_date = ngày làm rev (HHS, SZL lô 2–3 bị selfcheck chặn: 'rev=5 cần supersedes=…#4', 'expires_on=None').
2. **evidence.quote phải là CHUỖI NGUYÊN VĂN có trong source_file** (chép nguyên dòng, kể cả `**`, `|`), mỗi số trong `fields` (zone_low/center/zone_high/price_ref/center_alt) phải xuất hiện trong chính quote đó; ⚠ quote tự tóm tắt như 'Vùng [7.284; 21.857]' sai (DBC) — dùng `grep -n` lấy dòng thật.
3. **evidence.fields chỉ gồm trường SỐ** (zone_low, center, zone_high, price_ref, center_alt, center_range) — không đưa `price_date` (chuỗi) hay trường dict (`ex_basis_pending`) vào fields (làm selfcheck crash: ValueError/TypeError).
4. **center_alt ⇒ bắt buộc `center_alt_kind`** thuộc enum {expected_weighted, base_scenario, blend, median, zone_midpoint, point} (không dùng tên tự đặt như 'expected_weighted_pre_liquidity') **và** một evidence phủ `center_alt` (BSR, MSB lô 1–3 bị chặn).
5. **center_range = [center, hi] tăng dần, bắt đầu ĐÚNG center** — khung độ nhạy không bắt đầu từ center thì để `center_range: null` và ghi khung vào `notes` (SCL bị chặn: [16558, 22868] vs center 16883).
6. **price_ref cần evidence phủ** (quote chứa đúng số giá) — GAS lô 3 thiếu.
7. **zone nguyên con số của nguồn**: quote chứa 44.760 thì zone_low=44760, không làm tròn 44.800 (GAS).
8. **Nhãn**: vòng cuối REFUTED/INCONCLUSIVE & bản sửa chưa áp ⇒ `REFUTED_OPEN` (không phải FIXED_UNVERIFIED — dispatch cũ ghi sai); CONFIRMED CHỈ qua `bin/dd_ledger_append_confirmed.py` (cần entry bước 1 FIXED_UNVERIFIED trỏ REPORT mới trước, vì tool so md5 source_file của entry CUỐI sổ với report_md5 trong rN.json).
9. Taylor KHÔNG ghi sổ khi chạy song song — chỉ `LEDGER_PROPOSAL_<MÃ>.json` ({entry:{…}} hoặc entry trần đều được; nên thống nhất {entry:…}); trước khi báo xong chạy thử trên BẢN SAO sổ: `python3 bin/dd_price_zones_selfcheck.py --ledger <bản tạm>` = 0 lỗi (script có cờ --ledger; xác nhận bằng --help).
Ngoài ra sửa các file prompt khuôn (`prompts/*.txt` / `/tmp/gen_prompts.py` nếu còn) thêm nhắc 9 điểm trên, và mục 5 'SỔ GIÁ' đổi 'FIXED_UNVERIFIED' → quy tắc nhãn điểm 8.
Mẫu script áp sổ thực tế (nếu còn): `/tmp/apply_rebuild_lot1.py` … `lot4.py` (requote evidence tự động, drop trường không-số, fix dd_date). Lưu bản chuẩn vào repo: `bin/dd_ledger_apply_proposal.py` (CÔNG CỤ MỚI, đề xuất — user chưa duyệt, hỏi trước khi làm) thay vì sửa tay mỗi lô.

## Quy trình áp sổ sau vòng 3 (khi cả 5 xong)
Làm trong worktree riêng (`git worktree add ../wt-<thread> -b session/<thread>`): rsync artifact nhẹ từ cây chính (loại src/ *.pdf *.png *.jpg *.xlsx __pycache__) → worktree, chèn entry (render() của `bin/dd_ledger_append_confirmed.py`; recorded_at=now ICT; ghi `.try` + selfcheck sạch mới `os.replace`), CONFIRMED qua tool 2 bước, commit, XOÁ file untracked giống hệt bản commit ở cây chính (`git diff --name-status --diff-filter=A master <branch>` + cmp) rồi `merge --no-ff` vào master, đọc `git log` + selfcheck sổ. Nhãn không CONFIRMED = REFUTED_OPEN. Báo bảng tổng (tâm cũ→mới, vùng, giá vs vùng) vào topic MỚI.

## Còn chờ user (đừng tự quyết)
- HHS quy ước CK holding 0% vs 27%.
- MSB/CSV: Taylor đề xuất sizing 0% ở giá hiện tại.
- Cờ dữ liệu SCL: BQ `ticker.OShares` ghi 44,84tr từ 06/11 (cum) + `Close` chưa điều chỉnh quyền 09/11 → đề nghị giao Winston (data-ops) kiểm; user chưa duyệt dispatch.
- 11 ca REFUTED_OPEN còn lại (TTA, PNJ, VCB, CST, CSV, LLM, VLB, BSR, POW, QTP, SCL) KHÔNG nằm trong vòng 3.
- KHÔNG gửi email báo cáo DD nào (chỉ khi user báo).
