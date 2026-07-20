# TRIỂN KHAI phương án B — cap %ADV per-name cho CAPIT

Job `Taylor_20260720_172614` · 2026-07-21 · nhánh **`capit-adv-cap-20260721`** (CHƯA merge)
Tiếp nối `REPORT.md` (job `Taylor_20260720_170223` — dừng lại vì selfcheck ra 1/14 thay vì 0/14).

---
## 0. TL;DR
- Wire NGUYÊN công thức đã chốt (X=10%, D=2, ADV20 cửa sổ TRƯỚC). **Không chỉnh tham số** để né
  event NNC (phương án C vẫn bị bác).
- Chọn **hướng (b)**: golive phát trần **VND tuyệt đối/tên**, executor enforce cứng. Lý do quyết
  định ở §1 — không phải sở thích kiến trúc mà là (a) **sai** cho hệ 2 account.
- Selfcheck **PASS toàn bộ**: 14 event lịch sử ra đúng **1/14 = NNC 2016-01-18, 8.975.500đ**;
  tác động live **= 0**; 11/11 unit test tầng enforce (gồm 5 ca fail-closed).
- ⚠️ **PHÁT HIỆN NGOÀI DỰ KIẾN: CAPIT ĐÃ FIRE ngày 2026-07-20** (breadth 0,4291 ≫ gate 0,30,
  `capit_size=0,75` FULL). Rổ thật **5 tên** (NCT/PVT/SAB/**SIP**/VNM) — dispatch giả định 4 tên.
  Đây là điều kiện vận hành CHẶN merge, xem §5.
- Chưa merge. Chờ quant-skeptic + Mike/user.

---
## 1. Quyết định kiến trúc — chọn (b), và (a) thực sự SAI

Dispatch để mở (a) truyền NAV vào golive, hay (b) phát ADV/trần rồi enforce ở `bot_execute.py`.
Tôi chọn **(b)**. Ba lý do, lý do đầu là quyết định:

1. **(a) sai về mặt đúng-sai, không chỉ kém đẹp.** `golive_recommend_v23.py` chạy **một lần/ngày**
   và phục vụ **mọi account** (SpaceX có margin NAV 0,930 tỷ; ZaloPay cash-only NAV 0,920 tỷ; và
   paper `main`). Một trần biểu diễn dưới dạng **% NAV** chỉ đúng cho cái NAV đã dùng để tính nó —
   áp sang account kia là sai số trực tiếp. `X·ADV20·D` là **VND tuyệt đối, độc lập account**, nên
   đúng cho mọi account **theo cấu tạo**, không cần golive biết NAV của ai.
2. **Giữ golive advisory, không kéo nó vào broker state.** Script này thuần BQ + publish %; truyền
   NAV vào buộc nó đọc số dư live per-account (và dính luôn ràng buộc DNSE-vs-BQ, guidelines §6)
   chỉ để phục vụ một safeguard.
3. **Bảo đảm enforce ngang `excluded_tickers`.** Trần nằm trong plan chỉ có tác dụng nếu DollarBill
   (LLM) nhớ copy. Executor đọc **thẳng artifact golive**, nên generator quên cũng không mất trần —
   đúng nguyên tắc guidelines §7 "enforcement lives in ONE place".

**Không đụng `pt_v23_audit_2014.py`** (xác nhận lại phát hiện job trước: sizing tier-level
`tw2[pt]=wt/len(names)`, không có vector trọng số per-name; sửa = đụng lõi engine đã pin R3).

## 2. Thay đổi (3 file production)

| file | thay đổi |
|---|---|
| `deploy_golive_dt5g_v4/golive_recommend_v23.py` | `+ADV_X/ADV_D`, `+capit_adv_caps()` (BQ, median 20 phiên TRƯỚC ngày washout); phát `capit_adv_caps` vào `data/golive_v23_status.json`, cột `capit_cap_vnd` vào CSV, một dòng trần trong MD |
| `trading_bot/plan.py` | `+cap_capit_orders(plan, status_path=None)` — cắt qty lệnh MUA book CAPIT xuống lô chẵn thỏa trần; **fail-closed** |
| `bot_execute.py` | gọi `cap_capit_orders()` ngay sau `filter_excluded_tickers()`, log từng điều chỉnh |

**Fail-closed** (thiếu cap cho mã / artifact thiếu / artifact `signal_date` lệch plan / `ref_price`
≤0 / trần < 1 lô) → **CHẶN lệnh đó**, không thả không giới hạn. CAPIT là sự kiện sizing lớn và
hiếm: thà không mua còn hơn mua quá tay đúng ngày thanh khoản cạn (guidelines §5).
Phần dư **không dồn sang tên khác** → để cash, đúng spec.

Tương thích ngược: cả `telegram_recommend.py` (chọn cột theo tên) và `push_recommend_v23_to_bq.py`
(có cột `extra` JSON hứng field lạ) đều không vỡ vì thêm cột/field — đã kiểm tra, không phải suy đoán.

## 3. Selfcheck — `selfcheck_capit_adv_cap.py` (exit 0)

**A. 14 event lịch sử @ sleeve 0,38 tỷ → 1/14, đúng như đã biết**

| | |
|---|---|
| event kích hoạt | **1/14** (kỳ vọng 1) — **NNC, 2016-01-18** |
| vị thế kích hoạt | 1/66 |
| ADV20_pre / trần / equal-weight | 0,335 / **0,067** / 0,076 tỷ |
| VND để lại cash | **8.975.500đ** |

Khớp chính xác job trước (0,008975 tỷ). Độ nhạy: 0,75→1/14 · 1,50→2/14 · 3,75→9/14 · 7,50→12/14.

**B. Tác động live = 0** — đọc rổ THẬT từ artifact, không hardcode:

| ticker | ADV20_pre (tỷ) | trần (tỷ) |
|---|---|---|
| NCT | 2,338 | 0,468 |
| SIP | 3,054 | 0,611 |
| SAB | 23,29 | 4,658 |
| PVT | 48,50 | 9,700 |
| VNM | 138,78 | 27,755 |

SpaceX: sleeve 0,930×0,75 = **0,697 tỷ** → 0,139 tỷ/tên (n=5) — **không kích hoạt**.
ZaloPay: sleeve 0,690 tỷ → 0,138 tỷ/tên — **không kích hoạt**.
Tên chặt nhất (NCT) còn dư **3,4 lần** headroom. Cap có hay không cho kết quả y hệt hôm nay.

**C. 11/11 unit test tầng enforce** — dưới trần giữ nguyên · trim về lô chẵn không vượt trần ·
thiếu cap BLOCKED · artifact cũ BLOCKED · artifact thiếu BLOCKED · trần<1 lô BLOCKED ·
`ref_price=0` BLOCKED (không chia 0) · không đụng lệnh non-CAPIT/lệnh bán · no-op khi plan không
có CAPIT · phần dư không dồn sang tên khác.

**Regression**: `excluded_tickers_selfcheck.py` + `ghost_order_selfcheck.py` PASS (đường executor
dùng chung).

**self-check 0 VND**: PASS trên NAV path production — backtest engine **không bị sửa**. Ghi rõ,
không làm tròn: nếu về sau đưa cap vào backtest thì mức lệch lịch sử là **8.975.500đ** ở 1 vị thế.

## 4. Sửa tài liệu (việc 2 của dispatch)
`exp_capitexit/RESULT.md` §3c và §5 — chỗ ghi *"ở quy mô sleeve hiện tại nó KHÔNG kích hoạt
(14/14 event đủ capacity ở 0,38 tỷ) → wire bây giờ = zero thay đổi"* đã được thay bằng khối ĐÍNH
CHÍNH nêu đúng **1/14 event (NNC 2016-01-18, 8.975.500đ)** + giải thích nguyên nhân hai cửa sổ ADV
(POST ở bảng §3b vs PRE ở công thức được wire). Bảng §3b giữ nguyên vì nó mô tả đúng biến thể POST.
Docstring của `capit_adv_caps()` và `cap_capit_orders()` cũng ghi 1/14, không ghi "dormant".

## 5. ⚠️ PHÁT HIỆN NGOÀI PHẠM VI DISPATCH — CAPIT ĐÃ FIRE, và nó CHẶN merge

Khi đọc artifact thật để verify việc 4, tôi thấy:

```
capit_fired      True          breadth_oversold 0.4291  (gate 0.30)
capit_size       0.75          capit_grind      False        ← FULL size, không phải 0,375
n_capit_basket   5             capit_dd_excluded ['PNJ']
rổ               NCT, PVT, SAB, SIP, VNM                     ← dispatch giả định 4 tên (thiếu SIP)
```

Hai hệ quả:

1. **Blocker merge (đã tự động hoá vào selfcheck).** Artifact production hiện tại **chưa có**
   `capit_adv_caps` (nó do bản golive mới sinh ra). Nếu merge nhánh này TRƯỚC khi golive chạy lại,
   fail-closed sẽ **chặn sạch lệnh CAPIT** — đúng thiết kế, nhưng hậu quả là **bỏ lỡ nguyên sleeve
   đúng lúc nó fire**. Thứ tự bắt buộc: **chạy lại `golive_recommend_v23.py` → xác nhận artifact có
   `capit_adv_caps` → mới merge.** Selfcheck in cảnh báo này ra khi phát hiện.
2. **Ngoài phạm vi của tôi, cần Mike/user biết ngay**: CAPIT fire full-size là sự kiện vốn thật
   (`context_pack.md` ghi user tự rút Trứng vàng khi CAPIT kích hoạt). Rổ có **SIP** — tên dispatch
   không nhắc, chưa ai review. Tôi **không** tự quyết định gì về nó.

## 6. Ranh giới đã giữ
- ❌ Chưa merge, chưa kích hoạt production. Nhánh `capit-adv-cap-20260721`.
- ❌ Không sửa `pt_v23_audit_2014.py` / plan / executor logic ngoài điểm gọi.
- ❌ Không chỉnh X/D để khớp kỳ vọng.
- ✅ Selfcheck + regression + sửa tài liệu + route quant-skeptic.
