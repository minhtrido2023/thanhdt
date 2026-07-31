---
kind: script-output
status: DERIVED
source: golive_v23_recommendations_<date>.csv + data/golive_v23_status.json
group: market-state
writer: golive_recommend_v23.py (đọc dt5g_live)
role: ẢNH CHỤP CỦA PHIÊN — status JSON bị GHI ĐÈ mỗi lần chạy; lịch sử đọc ở BQ recommend_v23
---

# golive_v23_recommendations_<date>.csv + data/golive_v23_status.json

**Status: DERIVED**

## Là gì
Khuyến nghị BAL/LAG/CAPIT hàng ngày (CSV + MD, tên CÓ ngày) và **`data/golive_v23_status.json`** —
ảnh chụp trạng thái allocator/CAPIT/breadth của **RIÊNG phiên vừa chạy** (tên file KHÔNG có ngày).

## Ai ghi / cadence
`golive_recommend_v23.py`, đọc `dt5g_live` (đã fix 2026-07-11, trước đó đọc nhầm base).
Chạy trong `bq_freshness_check.sh` [pipeline-2] ~19:00 ICT T2-T6.

## ⚠️ Bẫy #1 — `golive_v23_status.json` là SNAPSHOT BỊ GHI ĐÈ, KHÔNG phải sổ lịch sử
File bị **ghi đè toàn bộ mỗi phiên**. Mọi field trong đó là **điều kiện/kết quả TÍNH LẠI TỪ ĐẦU
cho ngày chạy**, không mang trạng thái tích luỹ nào:
- `capit_signal_today` (tên cũ `capit_fired`, còn giữ làm alias) = gate breadth **của riêng ngày
  chạy**. Breadth rớt dưới `washout_gate` ⇒ cờ về `false` và `basket`/`capit_size`/
  `n_capit_basket` về rỗng/0 **NGAY**, kể cả khi vị thế THẬT vẫn đang giữ.
- Đây là nguyên nhân sự cố visibility 2026-07-29→07-31: mọi kênh báo cáo gate theo cờ này ⇒ im
  lặng hoàn toàn về CAPIT trong khi còn đủ 5 mã (NCT/PVT/SAB/SIP/VNM) ở cả 2 account (verify DNSE
  07-31). Chi tiết: `mike/agents/Taylor/research/capit_state_visibility_gap_20260731.md`.
- **Muốn biết "CÓ ĐANG GIỮ CAPIT không" ⇒ đọc [`capit_episode.md`](capit_episode.md)**
  (`data/capit_episode.json`, và key `capit_episode_open` được bơm vào chính status JSON từ
  2026-07-31), **KHÔNG** đọc `capit_signal_today`. Gate báo cáo đúng =
  `capit_signal_today OR capit_episode_open`.

## ⚠️ Bẫy #2 — cần số của NGÀY KHÁC hôm nay thì KHÔNG có ở đây
Không tồn tại `golive_v23_status_<date>.json`. Nguồn lịch sử chuẩn tắc =
**[`recommend_v23_bq.md`](recommend_v23_bq.md)** (BQ `recommend_v23.status` / `.recommendations`,
partition theo `signal_date`, do [pipeline-3] push mỗi phiên). CSV/MD `_<date>` trong
`deploy_golive_dt5g_v4/out/` vẫn có tên theo ngày nhưng là artifact trên đĩa (có thể bị dọn hoặc
bị chạy-lại ghi đè — coding_guidelines §8), không phải sổ lịch sử được bảo đảm.

## Bẫy #3 — state source
Kiểm tra `state_source` field = `DT5G_macro`, không phải suy đoán.

## ⚠️ Bẫy #4 — cột `weight_pct` trong CSV có **4 mẫu số khác nhau** tuỳ book
Một tên cột, bốn nghĩa. Cột `weight_base` (thêm 2026-07-31) nói rõ 100% là của cái gì:

| book | `weight_base` | 100% = |
|---|---|---|
| BAL | `BAL_book` | vốn book BAL |
| LAG | `LAG_book` | vốn book LAG (giá trị = trọng số tier) |
| CAPIT | `NAV_book_LAG__DA_GOM_capit_size__KHONG_NHAN_LAI` | NAV_book_LAG, **đã nhân `capit_size` sẵn** |
| PARK | `parking_basket` | rổ parking custom30V |

**Sự cố thật 2026-07-21** (finding `Taylor_20260731_154624`): plan SpaceX lấy `weight_pct`=15,0
của dòng CAPIT (= `capit_size`/n = 0,75/5) rồi nhân lên `capit_total_target_vnd` (vốn đã =
NAV_book_LAG × `capit_size`) ⇒ hiệu lực `capit_size²`. Deploy 254,4tr thay vì 348,4tr — thiếu
93,9tr, trong đó **87,1tr do nhân đôi**, chỉ 6,8tr do làm tròn lô (plan tự ghi chú "chênh do
rounding lots" nên không ai để ý). Cùng ngày, cùng CSV, plan ZaloPay chia đúng `/n` ⇒ đây là lỗi
đọc-cột-đa-nghĩa, không phải lỗi số học ngẫu nhiên.

**Lập plan CAPIT thì ĐỪNG tự lắp lại công thức** — đọc thẳng `status["capit_slot_targets"]`
(thêm 2026-07-31), đã tính sẵn **theo từng account**:
`{label: {nav_basis_vnd, nav_basis_source, w_lag_target, capit_size, nav_book_lag_vnd,
capit_total_target_vnd, n_slots, capit_slot_target_vnd, formula}}`, cơ sở NAV = `active_nav`
(đúng con số DollarBill dùng sizing, đã trừ `excluded_tickers`). Thiếu NAV ⇒ field `error`,
KHÔNG bịa số.

Phân biệt với `capit_adv_caps`: đó là **TRẦN** thanh khoản (`bot_execute.py` enforce cứng,
fail-closed); `capit_slot_targets` là **MỤC TIÊU** phân bổ. Lệnh thật = min(mục tiêu, trần) rồi
mới làm tròn lô. `send_plan_report.sh` đối chiếu Σ lệnh CAPIT vs mục tiêu và WARN khi lệch >10%
(WARN-only: lệch lớn có thể đúng — trần %ADV cắt, thiếu cash, mua chia nhiều phiên).

↩ [Nhóm market-state](index.md)
