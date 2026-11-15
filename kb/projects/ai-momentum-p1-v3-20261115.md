# AI-momentum P1-V3 — nới ngưỡng sự kiện ×2 (PREREG v3)

Job `Taylor_20261115_162439` · nhánh `research/ai-momentum-p1-20261115` (worktree `agents/Taylor/wt-ai-momentum-p1`) · **chưa merge, chưa cron, chưa chạy forward.**
User chốt 15/11 23:24 ICT (`decided_by: user`): phương án A. Thư mục: `agents/Taylor/research/ai_momentum_20261115/`.

## Làm gì
- `PREREG_v3.md` (+`PREREG_v3.md5`, khoá md5 cả `prereg_v3.json` và `events_v3.csv`): mom20≥0,15; idio20≥0,10; volr≥1,2; liq≥1 tỷ; giữ Close≥HI_3M_T1, universe_pit rv1, rating_8l≤4 as-of, cooldown 90 ngày+khác quý, hàng đợi 10/tuần. v3 thay v2 trước mọi lần chạy forward.
- `ai_momentum_daily.py`: tham số đọc từ `prereg_v3.json` (một nơi); fail-closed nếu md5 lệch; mọi dòng JSONL (kể cả `skipped_capacity`) mang `prereg_version`+`prereg_md5`; scorer chỉ đếm dòng đúng md5; thêm `T1_ticker_sensitivity` (bootstrap cụm theo mã + chênh trên sự kiện đầu mỗi mã) — mô tả, ngoài họ BH.
- Hoán vị khối tháng GIỮ; hoán vị trong-năm/trong-tháng CẤM (luật 12/11). Ngưỡng kinh tế T1≥5pp, T2≥8pp giữ nguyên. Không đề xuất đổi tham số nào khác.

## Số liệu (đo trong phiên)
- `build_events.py . qual_days_loose.csv events_v3.csv`: R4 **N=560 sự kiện, 321 mã, 26 tháng, 21,5/tháng** (6 tháng gần May–Oct: 12,3/tháng). 168/321 mã có >1 sự kiện (tối đa 4). Phân bố rating R4: 1:34, 2:69, 3:198, 4:259. ex20 TB +2,97% / trung vị −0,12%, P(ex20>0)=48,6%.
- **Hàng đợi 10/tuần (nhân quả theo ngày): cắt 86/560 = 15,4%**; tuần TB 5,3 sự kiện, tuần cao nhất **32**, 12/106 tuần vượt 10 ⇒ cắt dồn vào cụm (ngày 2025-07-28 có 13 ⇒ 3 bị bỏ).
- Power (`power_sim_directional_v3.out`, phân phối ex20 thật, NSIM=150 ⇒ ±~0,04): T1 Δ8pp/Δ12pp — p_dir=0,4: N_dir=80 → 0,73/0,99; N_dir=150 → 0,95/1,00. p_dir=0,3: 0,78/1,00; 0,96/1,00.
- Tháng tới N_dir=80 / 150 (chưa cộng ~3 tháng ex60; trong ngoặc = có cắt hàng đợi): nhịp TB 21,5, p_dir 0,4: **9,3 (11,0) / 17,4 (20,6)**; p_dir 0,3: 12,4 (14,7) / 23,3 (27,5). Nhịp 6 tháng gần 12,3, p_dir 0,4: **16,3 (19,2) / 30,5 (36,0)**; p_dir 0,3: 21,7 (25,6) / 40,7 (48,0). FINAL N_scored=250: 11,6 (13,7) tháng ở nhịp TB; 20,3 (24,0) ở nhịp gần.
- Look định nghĩa theo N_dir (L1=80, L2=150), FINAL = N_scored≥250 hoặc 24 tháng — **không đổi so với v2**, khoá lại trong v3 §3.
- Dry-run đối chiếu SQL (nguồn `ai_momentum_daily.py`, ngưỡng v3) vs `events_v3.csv` R4: **8/8 ngày khớp 100%** (`dryrun_v3_compare.out`: gồm ngày 13 sự kiện → 10 processed + 3 skipped, 2 ngày đúng 10, ngày 0 sự kiện, ngày gần nhất 2026-11-12).
- Selfcheck: **29 test, 33 mutant (33 killed), ALL PASS** dưới `env -u TZ`, `TZ=UTC`, `TZ=America/New_York` (`selfcheck_v3_*.txt`). Mutant mới: đổi từng ngưỡng sang giá trị v2, lệch cap, mất `prereg_version/md5`, bỏ khoá md5, scorer đếm dòng prereg khác, bỏ/lot sensitivity.

## Cảnh báo còn tồn
1. **N_dir vẫn có thể thấp**: p_dir=0,3–0,4 mới đo trên mẫu 10 (thô). Ở nhịp 6 tháng gần, L1 xong ~16–26 tháng (+3 ex60) — sát trần 24 tháng; **L2 không tới được** trong 24 tháng. Chỉ khi nhịp về TB dài hạn mới có kết luận. Đo p_dir thật sau 40 sự kiện xử lý.
2. **Phụ thuộc theo mã**: 168 mã lặp. p khối-tháng không bắt phụ thuộc trong-mã; sensitivity chỉ mô tả — nếu CI cụm-mã chứa 0 thì phải báo "không bền vững".
3. **Cụm theo thời gian**: cắt hàng đợi 15,4% dồn vào tuần bùng nổ (cùng thời điểm thị trường); sự kiện bị cắt không được chấm ⇒ nguy cơ lệch chọn nhẹ (chọn theo liq trong ngày).
4. **liq≥1 tỷ gồm mã kém thanh khoản** ⇒ **chỉ PAPER, không đề xuất thực thi/sizing**. Mã BANNED (vd HVN) vẫn vào sự kiện với `dd_flag`.
5. ~~M2 fail-open~~ → ĐÃ NỐI (P1-M2-WIRE, xem mục M2 bên dưới). M2 vẫn fail-open theo thiết kế: provider/model có thể bị gỡ lần nữa (đã xảy ra: `deepseek-v4-flash-free`) ⇒ theo dõi `m2_status=FAIL` hằng ngày; FAIL kéo dài = T3 mất mẫu. Model free của Zen: không SLA.
6. Hồi tố: v3 chọn theo outcome P0? Không — ngưỡng do user chốt dựa trên bảng N hợp lệ (chưa xem outcome forward); nhưng events_v3 hồi tố đã thấy ex20 ≈ 0 (trung vị −0,12%): không dùng để suy edge.

## Bước kế (không phải của tôi)
Mike: arch-review + quant-skeptic, rồi merge; cài cron chỉ sau khi Wags xong M2 và user duyệt.

## M2 — đã nối (P1-M2-WIRE, 2026-11-15)
- Nhánh vẫn `research/ai-momentum-p1-20261115`, đã `merge --no-ff wags/m2-wrapper-20261115` (không xung đột; không sửa `second_opinion.sh`). `m2_adapter()` gọi `bin/second_opinion.sh --raw-prompt-file P --out R --text-out T --timeout 240` (bin tìm theo root của chính worktree). Chi tiết thay đổi prompt: `PREREG_v3_1.md` (+dòng no-tool, +khung JSON; không đổi md5 khoá v3).
- Blind chạy trước, không nhận JSON M1; challenge nhận gói + JSON M1. Lỗi (exit 10/11/12/2, timeout, parse, schema, event_id) ⇒ `m2_status=FAIL`, fail-open (T1/T2 chấm, loại khỏi T3). Raw text M2 lưu trong ledger (`m2_raw`).
- **Chạy thật retro 2 sự kiện** (HID_2026-09-17, DXP_2026-10-12; `retro_run_v31/`, ledger retro riêng): lần 1 FAIL 2/2 vì deepseek bịa tên trường/enum (không có khung định dạng) + `validate()` ném KeyError với kiểu `boolean`; sửa; lần 2: **m2_status OK 2/2**. Thời gian cả sự kiện (M1 + blind + challenge + M1 phản biện): 138,8s và 109,1s (tổng 247,9s). Chi phí M1 (gồm phản biện): $0,0508 và $0,0382 (M2 free). Mô tả thô, N=2 vô nghĩa thống kê: blind vs M1 — driver khớp 1/2, view20 khớp 1/2; challenge nêu missed 8/3, disagree 3/2; không sự kiện nào đổi view sau phản biện (flip 0/2).
- Selfcheck: `selfcheck_ai_momentum.py` **36 test / 44 mutant (44 killed) ALL PASS** dưới `env -u TZ`, `TZ=UTC`, `TZ=America/New_York` (`selfcheck_v31_*.txt`); `bin/second_opinion_selfcheck.sh` PASS 17 check ×3 TZ trên nhánh hợp nhất.
- ⚠️ Cảnh báo M2: (a) model free có thể bị gỡ/đổi bất cứ lúc nào (Wags §1) ⇒ cron nên báo khi `m2_status=FAIL` liên tiếp; (b) wrapper retry nội bộ, một sự kiện FAIL có thể mất tới ~timeout×retry; (c) deepseek còn bịa nếu prompt đổi ⇒ giữ khung định dạng; (d) M2 không có WebSearch (opencode deny), M1 retro cấm WebSearch ⇒ cả hai chỉ dựa trên gói.
