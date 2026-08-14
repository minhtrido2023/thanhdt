# Oshares vòng 4 — dời cổng chứng nhận AIS vào `oshares_live` (job `Taylor_20260813_154112`)

**Việc**: khuyến nghị #4 của quant-skeptic vòng 3 (CONFIRMED, log
`mike/logs/verify_20260813_152113_1632904.log`): cổng chứng nhận neo AIS chỉ sống ở
`oshares_pit.py` (lớp bọc), nên `oshares_live.oshares_at()` **gọi thẳng** vẫn trả
`3.000.000.000` cho IDC và `461.723.054` cho FPT. "Cảnh báo trong docstring không phải là cổng."

**Kết quả**: cổng đã nằm trong `oshares_live`. Hợp đồng với consumer **không đổi một ô nào**
(0/160 ô), số của cả 3 consumer **không đổi**, và 2 con số sai kể trên nay bị chặn ngay tại hàm
gốc. Đây là REFACTOR (dời logic đã CONFIRMED), không phát minh luật mới.

## Đã đổi cái gì

| | Trước | Sau |
|---|---|---|
| `_ais_verdicts` + `_SERVE_AIS_VERDICTS` | định nghĩa trong `oshares_pit.py` | định nghĩa trong `oshares_live.py`; `oshares_pit` **import lại** (một bản duy nhất) |
| `oshares_at()` với neo AIS không chứng nhận được | trả số, nhãn `AIS_EXACT` | `value=None`, nhãn **`AIS_UNCERTIFIED`**, số bị từ chối giữ ở `uncertified_value` |
| `oshares_pit` / `oshares_reconciled` | tự tính verdict (`_anchor_unverified`) | **đọc phán quyết** (`_uncertified()`), không tính lại |
| Cổng biên độ `SANITY_FACTOR` | ở `oshares_pit` | **giữ nguyên ở `oshares_pit`** — nó so với số nền CỦA CALLER, thứ `oshares_live` không biết |

Ba quyết định thiết kế, nêu ra vì chúng có thể bị đọc là thiếu sót:

1. **Cổng chạy SAU khi tính xong, không phải lúc chọn neo.** Nhánh `blockers` (`UNKNOWN_RATIO`)
   đã từ chối trả lời trước đó thì giữ nguyên nhãn cũ — lý do ĐẦU TIÊN chặn mới là lý do đúng
   để báo. Nhờ vậy tập ô bị chặn trùng khít tập mà `oshares_pit` đang chặn hôm nay.
2. **Neo AIS trượt cổng ⇒ TỪ CHỐI, không tụt xuống neo cũ hơn hay neo dòng quý.** Thay bằng một
   số khác là ĐỔI SỐ, không còn là dời cổng, và số thay thế đó chưa ai đo.
3. **`AIS_UNCERTIFIED` KHÔNG được thêm vào `_DECLINED` của `oshares_pit`.** `summarize()` đếm nó
   dưới `n_fallback_implausible` qua tiền tố lý do "KHÔNG XÁC MINH ĐƯỢC"; thêm vào `_DECLINED` sẽ
   dịch dòng giữa hai cột của `data/oshares_reconcile_log.csv` đang có dữ liệu burn-in.

## Bằng chứng

### 1. Hợp đồng consumer KHÔNG ĐỔI — 160 ô, 20 mã × 8 ngày (2016→2026)
`ab_snapshot.py`, chụp trước/sau (`snap_before.json` / `snap_after.json`):

| So sánh | Khác |
|---|---|
| `oshares_pit` + `oshares_reconciled`: `value`, `source`, `live_value`, `rel_diff` | **0 / 160** |
| chuỗi `reason` của bản ghi fallback | **0** |
| nhãn `method` của bản ghi fallback (`AIS_EXACT` → `AIS_UNCERTIFIED`) | 36 = 18 ô × 2 hàm — trung thực hơn, không đổi số |
| `oshares_at` **gọi thẳng** | **18 ô**, tất cả đều là "có số → `None`"; **0 ô** đổi sang một số khác |

18 ô đó chính là lỗ hổng đang đóng, gồm `IDC@2021-02-05 3.000.000.000 → None` và
`FPT@2020-05-05 461.723.054 → None`.

### 2. Ba consumer, chạy thật

| Consumer | Kết quả |
|---|---|
| **A** `custom30_core_select_audit.py` (historical) | live=6603 (86,8%) · fallback=1004 · none=3 · cổng chặn 500 ô · **liq CAGR 12,44%** — trùng số pin vòng 3 từng chữ số. SELF-CHECK PASS \| SPOTCHECK PASS, `nav_recon_err=0.00 VND` |
| **B** `rating_8l._reconcile_oshares` (live) | 771 mã, **0 mã đổi `OShares`**; dòng tổng hợp trùng tuyệt đối trước/sau: `n=771 khớp=637 lệch=71 nghi lỗi DL=42 từ chối=10 thiếu=11` |
| **C** `mike/bin/corp_action_daily.py` (cron LIVE) | **2/33 mã đổi** — xem mục "Cái giá" |

⚠️ **Consumer C không nằm trong đề bài dispatch** (dispatch chỉ nêu Việc A/B) nhưng nó `import`
**thẳng** `oshares_at` — đúng hình dạng rủi ro mà vòng này đóng, nên phải đo chứ không suy luận.
Selfcheck của nó: **127/127 PASS**.

### 3. Selfcheck

| File | Trước | Sau |
|---|---|---|
| `oshares_live.py --selfcheck` | 22/22 | **32/32** (+10 ca vòng 4) |
| `oshares_pit.py` | 47/47 | **48/48** (A13a đối chứng mới; A13/A14/A15 viết lại theo đường đi mới) |
| `oshares_wire_selfcheck.py` | 11/11 | **11/11** |
| `mike/bin/corp_action_daily.py --selfcheck` | — | **127/127** |

Chạy lại toàn bộ dưới `env -u TZ` và `TZ=America/New_York`: kết quả **giống hệt** (§16/§19).

Mọi ca "chặn được" đều có **ca chứng minh ngược** đi kèm — mở `_SERVE_AIS_VERDICTS` ra thì
IDC 3.000.000.000 và FPT 461.723.054 **thật sự quay lại** (N3, A6, A11); và có **đối chứng** để
cổng không PASS bằng cách chặn tất cả: TCB vẫn `AIS_EXACT` (N5), neo dòng quý không bị đụng (N6),
FPT 2025-10-01 vẫn được phục vụ từ live (A13a). Fail-closed kiểm bằng cách cho hàm chứng nhận ném
lỗi thật (N4, A13).

## Cái giá, đo được — consumer C mất phủ 2/33 mã

| Mã | Trước | Sau | Vì sao |
|---|---|---|---|
| EVF | 704.248.289 `AIS_EXACT` | `None` `AIS_UNCERTIFIED` | AIS 2024-12-06 ghi 704.248.289 trong khi AIS 2024-11-22 = 760.565.802 và `shares_delta` = +2.120.227 ⇒ kỳ vọng 762.686.029. Dòng quý mới nhất (2026-07-21) vẫn 760.565.802 ⇒ dòng vendor này gần như chắc chắn hỏng. **Cổng đúng.** |
| SHB | 5.377.339.512 `ISS_ESTIMATE` | `None` `AIS_UNCERTIFIED` | AIS 2025-10-07 = 4.594.200.024, cả (a) 4.139.086.652 lẫn (b) 4.191.361.564 đều không dựng ra nó (~+10%). Nhưng số cũ 5.377.339.512 chỉ lệch **+0,63%** so với dòng quý 5.343.703.838 ⇒ đây là **báo oan có thật**, mất phủ chứ không phải tránh được số sai. |

Hai mã này rơi vào `value=None`, mà `check_invariants`/`check_retro` của `corp_action_daily`
**bỏ qua** khi một bên là `None` ⇒ chúng cũng mất luôn lớp giám sát bất biến. Đây là hệ quả của
chính chính sách fail-closed đã CONFIRMED vòng 3 (chiều báo oan rẻ hơn chiều bỏ lọt: rơi về số
đang dùng vs. thay số đúng bằng số sai −32%), nhưng **là một cái giá, không phải bằng không** —
ghi ra đây để không ai đọc "0 diff" thành "không mất gì".

Với consumer A/B thì không mất gì: `oshares_pit` đã chặn đúng những ô đó từ vòng 3.

## Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude && source wc_env.sh
PY=/home/trido/thanhdt/wc_venv/bin/python; D=mike/agents/Taylor/research/oshares_gate_move_20260813
$PY oshares_live.py --selfcheck                    # 32/32
MIKE_BOT_TEST_MODE=1 $PY oshares_pit.py            # 48/48
MIKE_BOT_TEST_MODE=1 $PY oshares_wire_selfcheck.py # 11/11
MIKE_BOT_TEST_MODE=1 $PY mike/bin/corp_action_daily.py --selfcheck   # 127/127
$PY $D/ab_snapshot.py /tmp/snap.json               # so với $D/snap_before.json
MIKE_BOT_TEST_MODE=1 $PY custom30_core_select_audit.py               # liq 12,44%
MIKE_BOT_TEST_MODE=1 $PY $D/consumer_b_driver.py /tmp/b.json         # so với $D/consB_before.json
MIKE_BOT_TEST_MODE=1 $PY $D/consumer_c_driver.py /tmp/c.json         # so với $D/consC_before.json
```

Rollback một dòng: trong `oshares_live.py`, `_SERVE_AIS_VERDICTS = ("OK", "NO_PRIOR",
"UNVERIFIED")` ⇒ cổng vô hiệu (đã kiểm: hai số sai quay lại đúng như cũ).

## Còn treo

- Cổng **không** đối chiếu được dòng AIS đầu tiên của mã (`NO_PRIOR`, phục vụ có chủ đích) và
  không thấy được restatement mà feed chưa ingest — giới hạn cũ, không đổi ở vòng này.
- `SANITY_FACTOR` vẫn chỉ bảo vệ consumer đi qua `oshares_pit`; ai gọi thẳng `oshares_at` không có
  lớp biên độ đó (đúng thiết kế: nó cần số nền của caller). Consumer C đang không có lớp này —
  chưa đo được nó có cần hay không.
