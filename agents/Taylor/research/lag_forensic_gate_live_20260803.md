# Vá lỗ hổng BANNED/forensic ở đường live LAG — `lag_filter_forensic_banned()`

**Job** `Taylor_20260803_035250` · 2026-08-03 · Taylor (quant)
**Nguồn**: job `Taylor_20260803_015850` §7 (`research/lag_quality_gate_20260803.md`) → **user duyệt**.
**Loại thay đổi**: cổng an toàn/quản trị ở TẦNG TÍN HIỆU của book LAG. **Không** phải tham số tối ưu
lợi nhuận ⇒ DSR/PBO không áp dụng (không có cấu hình nào được chọn từ một họ biến thể).

---

## 1. Lỗ hổng được vá (nhắc lại, có bằng chứng)

Engine backtest ĐÃ có gate forensic từ 2026-06-20 (`pt_v23_audit_2014.py:1035`,
`LAG_FORENSIC_GATE=1` mặc định ON). Đường LIVE **không có gì**: `grep -n "forensic|BANNED|banned"`
trong `golive_recommend_v23.py` + `lag_live_schedule.py` → **0 kết quả** (trước thay đổi này).
`anomaly_excluded()` chỉ áp cho pool CAPIT (`golive_recommend_v23.py:702`, trong nhánh
`if capit_size > 0.005`); `due_diligence.py` cố ý thuần thông tin, không chặn.

Hệ quả đo được: **VVS** (BANNED vĩnh viễn trong `mike/kb/KNOWLEDGE.md` **và** cờ forensic
`exclude`) đi qua toàn bộ gate LAG tự động và **có mặt trong file khuyến nghị**. Ngày 07-30 nó chỉ
bị chặn **bằng tay** (plan note: *"VVS=BANNED"*) ⇒ lớp phòng thủ khi đó là **trí nhớ của người/LLM
lập plan**, không phải cơ chế.

---

## 2. Thiết kế — và một điểm CỐ Ý KHÁC engine (đọc kỹ)

`lag_forensic_filter.lag_filter_forensic_banned(cand, asof, workdir=…)`, gọi ngay sau
`lag_filter_low_rating()` trong `golive_recommend_v23.py`.

| Nguồn | Ngữ nghĩa | Fail-safe |
|---|---|---|
| `BANNED` (hằng số, 15 mã) | cấm **vĩnh viễn**, không có ngày hiệu lực ⇒ áp mọi lúc | hằng số trong code ⇒ **không thể hỏng**, fail-closed tuyệt đối |
| `data/forensic_flags.csv` severity=`exclude` | áp khi `flag_date <= asof` | đọc hỏng → giữ nguyên danh sách + trả `error string` (**fail-open**), `BANNED` vẫn áp |
| severity=`watch` | KHÔNG loại | — |
| `asof` = NaT/không hợp lệ | coi như mọi cờ đã hiệu lực | **fail-closed** |

### ⚠️ Mốc date-aware = `asof`, KHÔNG phải `Release_Date` — sửa sau khi chạy thật
Bản đầu tiên tôi viết đúng theo ngữ nghĩa engine (`Release_Date >= flag_date`). **Chạy thử trên rổ
thật đã bác bỏ nó**: BFC có cờ `exclude` ngày 2026-06-20 nhưng event gần nhất release **2026-05-04**
⇒ theo tiêu chí `Release_Date`, **BFC KHÔNG bị chặn** — đúng cái ca mà báo cáo §7 nêu là lỗ hổng.

Lý do engine dùng `Release_Date` là đúng **cho engine**: trong replay lịch sử, thời điểm ra quyết
định ≈ `Release_Date`, nên so với ngày cờ ở đó chính là "không hindsight". Ở đường LIVE thời điểm ra
quyết định là **hôm nay** — một event công bố 05-04 của mã bị gắn cờ 06-20 mà **hôm nay** mới xét
mua thì phải chặn, vì hôm nay ta ĐÃ biết. Dùng `asof` giữ nguyên tính chất "không hồi tố" (replay
một ngày trước ngày cờ vẫn không thấy cờ — có test) mà không để lọt event cũ. Hai mốc trùng nhau
trong mọi ca event mới; chỉ khác ở event cũ, và ở đó `asof` mới đúng.

Ghi nhận thẳng: **đây là sai sót trong bản viết đầu, được bắt bởi việc CHẠY THẬT chứ không phải đọc
lại code** (đúng bài học `coding_guidelines` §15/§19).

---

## 3. Self-check — `lag_forensic_filter_selfcheck.py`, **26 PASS / 0 FAIL**

Chạy lại dưới **3 biến thể môi trường** (`$DNA_PYEXE`, `env -u TZ`, `TZ=UTC`) — **26/26 PASS cả ba**
(kỷ luật §16/§19: self-check thừa hưởng `TZ` đúng của tác giả thì pass ở đâu cũng vô nghĩa; ở đây
mọi mốc thời gian đều truyền tường minh, không đọc đồng hồ máy).

Nhóm test đáng chú ý:
- **2 test cơ học chống trôi lệch danh sách BANNED** (danh sách bị nhân bản 3 nơi): so khớp với
  `mike/bin/build_universe_pit_quality.py::BANNED` (danh sách Python, so chính xác) **và** với dòng
  "Cổ phiếu BANNED vĩnh viễn" trong `mike/kb/KNOWLEDGE.md` (nguồn chuẩn tắc). Đây là lý do file
  self-check tồn tại thay vì một dòng ghi chú "nhớ đồng bộ tay".
- **Ca BFC thật**: event cũ hơn ngày cờ, xét ở `asof` sau cờ → vẫn bị chặn.
- **Không hồi tố**: replay `asof=2026-06-19` (trước cờ) → giữ; `asof=2026-06-20` (đúng ngày) → chặn.
- **Fail-safe**: CSV thiếu → forensic fail-open + error string, nhưng **BANNED vẫn chặn**.
- **Guard nối dây**: `golive_recommend_v23.py` có thật sự import + gọi `(cand, LATEST, …)`.
- **Bất biến với cửa sổ pin**: mọi cờ `exclude` đều có ngày > `AUDIT_END=2026-06-19`.

---

## 4. Verify TRỰC TIẾP trên đường live hôm nay — A/B 1 biến

Chạy **2 lần đường live thật** (`$DNA_PYEXE deploy_golive_dt5g_v4/golive_recommend_v23.py`,
`TZ=Asia/Ho_Chi_Minh`, BQ **live** — script tự `os.environ.pop("BQ_LOCAL_CACHE")`), khác nhau đúng
**1 dòng**: bản A dùng bản sao `sed` vô hiệu hoá lời gọi gate (`golive_recommend_v23_NOGATE_PROBE.py`,
đã xoá sau khi chạy), bản B là code production.

| | A (không gate) | B (có gate) |
|---|---|---|
| `[lag-live]` events / qualify | 1492 / **184** | 1492 / **184** |
| `lag_liq_excluded` | **19 mã** | **19 mã — Y HỆT** |
| `lag_rating_excluded` | **57 mã** | **57 mã — Y HỆT** (gồm **KLB, L40, HSG**) |
| `lag_forensic_excluded` | `[]` | **BFC (forensic, cờ 2026-06-20), VVS (banned)** |
| `n_lag_recent` | 24 | 23 |
| khuyến nghị (CSV) | **64 dòng** | **63 dòng** |
| chênh lệch danh mục | — | **chỉ mất đúng `('LAG','VVS')`** |
| `weight_pct` / `status` / `play_type` khác nhau | — | **0 dòng** |

⇒ Gate làm **đúng một việc và chỉ một việc**: loại VVS khỏi khuyến nghị + loại BFC khỏi rổ ứng viên.
**Nhóm đã bị 8L rating chặn từ trước (KLB/L40/HSG) không đổi hành vi** — vẫn bị chặn ở đúng tầng cũ,
gate mới không đụng tới. Không có mã nào khác đổi trọng số/trạng thái.

Câu diễn giải trong `status.json` (bản B):
`"FORENSIC_EXCLUDE — cờ 2026-06-20 ≤ asof 2026-07-31, data/forensic_flags.csv severity=exclude"`
(`asof` = `LATEST` = phiên dữ liệu mới nhất, 2026-07-31 — đúng, hôm nay T2 03-08 BQ mới tới 07-31).

**Vệ sinh production**: `data/golive_v23_status.json` và `out/golive_v23_recommendations_2026-08-03.*`
đã được **sao lưu trước khi chạy và khôi phục/xoá sau khi chạy** (diff JSON sau khôi phục = **0**);
bản sao probe đã xoá. Cây làm việc trả về đúng trạng thái trước khi verify.

---

## 5. Không đụng số pin (verify lại, không tin ghi chú cũ)

Mọi dòng `severity=exclude` trong `data/forensic_flags.csv` đều có `date = 2026-06-20` > `AUDIT_END
= 2026-06-19` ⇒ trong cửa sổ backtest pin, gate drop **0 event**. Ngoài ra gate này **chỉ nằm ở
đường live**, engine backtest không đọc module mới. Có test cơ học khoá bất biến này
(`min(flag_date) > 2026-06-19`) để lần sau thêm cờ mới lùi ngày thì self-check kêu ngay.

Số pin R3 hiện hành (re-pin cùng ngày, việc riêng): **28,86% / 1,90 / −17,8% / 1,62 / 1.178,01B**.

---

## 6. Việc còn MỞ (nêu rõ, không tự làm)

1. **Chưa có lưới ở TẦNG LỆNH.** LAG hiện có `filter_lag_rating_orders` (P1) chặn theo rating trên
   từng order của plan, nhưng **không có** lưới tương ứng cho BANNED/forensic. Một plan viết tay/LLM
   vẫn có thể đặt lệnh mua mã BANNED mà không gì chặn. Đây đúng lý do P1 tồn tại — nên làm tương tự,
   nhưng nằm ngoài phạm vi user đã duyệt hôm nay.
2. **Danh sách BANNED bị nhân bản 3 nơi** (`lag_forensic_filter.py`, `build_universe_pit_quality.py`,
   `converge_union_test.py`) + nguồn chuẩn tắc là văn xuôi trong `KNOWLEDGE.md`. Self-check khoá 2/3
   bản sao; hợp nhất về một file dữ liệu là việc vệ sinh riêng.
3. `data/forensic_flags.csv` **không có trong `mike/kb/data_registry/`** — nên thêm một entry
   (CANONICAL, ai ghi, cadence) theo `coding_guidelines` §9.

---

## 7. Kỷ luật đã theo

- Đọc code thật trước (§1): 3 tiền đề của báo cáo gốc được verify lại từng dòng.
- `git status` sạch trên engine/production trước khi đo (§14); backtest engine **không bị sửa**.
- N/A: N_trials, DSR/PBO — không chọn cấu hình nào (§13).
- Self-check chạy thật, đa môi trường (§19), và **chính lần chạy thật đã bắt lỗi thiết kế** (§2).
- Chưa commit khi viết báo cáo này — **chờ quant-skeptic CONFIRMED mới merge** (§15, user yêu cầu).

**Artifact**: `mike/agents/Taylor/research/lag_forensic_20260803/` — `run_A_nogate.log`,
`run_B_gate.log`, `status_A_nogate.json`, `status_B_gate.json`, `recs_A_nogate.csv`,
`recs_B_gate.csv`, `report_A_nogate.md`, `report_B_gate.md`, `backup/golive_v23_status.json.bak`.
Code: `lag_forensic_filter.py`, `lag_forensic_filter_selfcheck.py`,
`deploy_golive_dt5g_v4/golive_recommend_v23.py` (+4 khối nhỏ: import, khởi tạo biến, lời gọi,
`status.json` + block báo cáo).
