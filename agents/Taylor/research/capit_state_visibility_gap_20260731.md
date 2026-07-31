# CAPIT — lỗ hổng hiển thị trạng thái + sự cố ghi đè artifact 07-30

Job `Taylor_20260731_025222` · 2026-07-31 · điều tra vận hành/dữ liệu (không phải R&D mô hình)

Bối cảnh: job trước (`Taylor_20260731_023251`) đọc `data/golive_v23_status.json` ngày 07-30 thấy
`capit_fired=False` và báo "CAPIT hiện KHÔNG fire". User phản hồi: CAPIT ĐÃ fire và giải ngân thật
(07-20/07-21) — "vấn đề là team không có quản lý tốt thông tin".

---

## 1. Vị thế CAPIT THẬT ngay lúc này (DNSE API live, không dùng BQ)

`DNSEBroker.get_positions()` gọi trực tiếp, 2026-07-31 ~03:00 ICT — **CÒN GIỮ ĐỦ 5/5 mã ở cả 2
account, chưa bán mã nào**:

| Ticker | SpaceX | ZaloPay | Mua 07-21 (SpaceX/ZaloPay) |
|---|---|---|---|
| NCT | 500 | 373 | 400 / 373 |
| PVT | 3 500 | 2 071 | 3 000 / 2 070 |
| SAB | 1 100 | 744 | 800 / 744 |
| SIP | 1 700 | 749 | 1 100 / 749 |
| VNM | 900 | 601 | 900 / 601 |

Nguồn rổ: `data/trade_plans/plan_{SpaceX,ZaloPay}_2026-07-21.json` (book=CAPIT) + fill thật trong
`data/execution_logs/dnse_raw_2026-07-21.jsonl` (lọc theo `account_label`).

Hai lưu ý:
- **Rổ CAPIT thật là 5 mã, gồm NCT.** `kb/current_ops.md` ghi "PVT/SIP/VNM/SAB" — thiếu NCT.
- **SpaceX PVT 3 500 > 3 000 và SIP 1 700 > 1 100** ⇒ có phần chồng lấn với custom30V parking.
  Vị thế broker KHÔNG mang nhãn book, nên **không thể tách "bao nhiêu cổ là CAPIT" từ dữ liệu
  broker** — thêm một lý do cần sổ episode riêng (§4).

## 2. Ngữ nghĩa thật của `capit_fired` / `capit_size` / `n_capit_basket` — KHÔNG phải bug

`deploy_golive_dt5g_v4/golive_recommend_v23.py:633`:

```python
capit_fired = bool(pd.notna(breadth_today) and breadth_today >= WASHOUT_GATE and not breadth_stale)
```

Thuần **điều kiện CỦA NGÀY CHẠY**, tính lại từ đầu mỗi phiên, không đọc bất kỳ state nào.
`capit_size`, `basket`, `n_capit_basket`, `capit_adv_caps` đều nằm trong `if capit_fired:`
(dòng 644-673) nên **về 0 / rỗng ngay phiên đầu tiên breadth rớt dưới gate**, bất kể đang giữ gì.

`CAPIT_HOLD = 60` (dòng 275) **chỉ được dùng để in 1 dòng chữ trong MD** (dòng 874, và cũng chỉ
in khi `capit_fired`) — **không có dòng code nào enforce hay đếm ngày giữ**. Không có file/bảng
nào ghi "episode CAPIT #1: entry 07-21, basket X, còn mở".

Timeline thật (BQ `recommend_v23.status`, khớp 100% với các MD/CSV lưu theo ngày trong
`deploy_golive_dt5g_v4/out/`):

| Ngày | breadth | gate | fired | size | n_basket |
|---|---|---|---|---|---|
| 07-17 | 21,8% | 30% | false | 0 | 0 |
| 07-20 | 42,9% | 30% | **true** | 0,75 | 5 |
| 07-21 | 46,2% | 30% | **true** | 0,75 | 5 |
| 07-22 | 49,6% | 31% (pit) | **true** | 0,75 | 4 |
| 07-23 | 38,4% | 31% | **true** | 0,75 | 4 |
| 07-24 | 40,8% | 31% | **true** | 0,75 | 3 |
| 07-27 | 50,8% | 31% | **true** | 0,75 | 3 |
| 07-28 | 37,2% | 31% | **true** | 0,75 | 3 |
| 07-29 | 29,2% | 31% | false | 0 | 0 |
| 07-30 | 10,0% | 31% | false | 0 | 0 |

⇒ `capit_fired=False` ngày 07-30 là **đúng theo ngữ nghĩa của nó**. Kết luận "CAPIT không fire"
rút ra từ đó mới là sai.

**Điểm phụ đáng chú ý**: rổ bị TÍNH LẠI mỗi ngày và co dần (NCT rời sau 07-21, SAB rời sau 07-23)
vì pool pbz được screen lại theo giá mới. CSV mỗi ngày phát lại 1 rổ "như thể triển khai mới",
không có khái niệm "đã giải ngân 07-21 rồi". Việc không mua trùng là do **người** (DollarBill/Mike/
user) nhớ, không do cơ chế nào chặn. Đã kiểm tra plan 07-22→07-30: **không có lệnh CAPIT nào lặp
lại** — lần này không thiệt hại.

## 3. Sự cố THẬT phát hiện thêm: artifact 07-30 trên đĩa bị ghi đè bằng interpreter sai

Đây là phần "quản lý thông tin" hỏng thật sự, không chỉ ngữ nghĩa.

- **19:00-19:03 ICT 07-30** — pipeline `bq_freshness_check.sh` chạy `golive_recommend_v23.py` bằng
  `$PY = ${DNA_PYEXE}` (= `/home/trido/thanhdt/wc_venv/bin/python`, **3.12.13 / pandas 3.0.2**).
  Log (`mike/logs/bq_freshness.log`): `LAG entries: 5 upcoming, 24 entered in last sessions` →
  `push_recommend_v23_to_bq DONE — 2026-07-30 (recs=60, status=1)`. **Bản này ĐÚNG** và đã lên BQ.
- **19:04-19:08 ICT** — có lần chạy lại `golive_recommend_v23.py` bằng **`python3` hệ thống
  (3.10.12 / pandas 2.3.3)**. Bằng chứng: `__pycache__/lag_live_schedule.cpython-310.pyc`,
  `lag_liquidity_filter.cpython-310.pyc`, `custom30.cpython-310.pyc` đều có mtime 19:04-19:08
  (venv là cpython-312, không sinh file `-310`); cùng khoảng đó chỉ có
  `data/golive_v23_status.json` + `out/golive_v23_recommendations_2026-07-30.{csv,md}` +
  `active_nav_*.json` bị ghi.
- pandas 2.3 **không unpickle được** `data/earnings_surprise_data.pkl` (viết bằng pandas 3) →
  `lag_source_error: NotImplementedError (dtype('<M8[ns]'), ...)` → nhánh except → LAG rỗng.
- **Hậu quả**: bản trên ĐĨA cho ngày 07-30 bị thay bằng bản LAG-mù:
  `n_lag_upcoming: 0` (thật: 5), CSV còn **31 dòng** (1 BAL + 30 PARK) thay vì **60** — mất toàn bộ
  29 dòng LAG. BQ giữ bản đúng, đĩa giữ bản hỏng, và **đĩa mới là thứ mọi người đọc**.

Vi phạm: `kb/coding_guidelines.md` §8 (ghi output ad-hoc đè lên tên file canonical) + quy tắc
interpreter pinned `$DNA_PYEXE`.

Cảnh báo `LAG PKL WARN` đã có sẵn (`mike/bin/bq_freshness_check.sh:426`) nhưng nó check **TRƯỚC**
pipeline và **bằng `$DNA_PYEXE`** → về bản chất không thể bắt được lần ghi đè xảy ra SAU đó bằng
interpreter khác.

**Tác động thực tế lên plan 07-31: KHÔNG có.** Kiểm tra độc lập BQ
`recommend_v23.recommendations` ngày 07-30: LAG upcoming sớm nhất là DHD "T+2 phiên tới"
(= 08-01), 4 mã còn lại T+3 (APF/TV3/TV2/MAC) — không mã nào vào lệnh 07-31, đúng như plan Bill
viết. Rủi ro là thật, thiệt hại lần này bằng 0.

## 4. Điểm phụ đã hỏi: `w_lag_target = 0,50` ở NEUTRAL — ĐÚNG, không liên quan

`golive_recommend_v23.py:252-271` — w_LAG là **edge-conditional** từ 2026-07-12, không còn hardcode
0,65: state 3/4/5 chỉ nâng lên 0,65 khi `mean12` (trailing-12M LAG edge-health,
`data/lag_edge_health.csv`, ffill as-of) ≥ `EDGE_THR = 4,0%`.
Đo lại: `mean12` as-of 2026-07-30 = **0,48%** (bản ghi cuối 2026-05-11) < 4% ⇒ **0,50 là đúng
thiết kế**, khớp log `[edge-alloc] mean12 as-of 2026-07-30 = 0.5% vs thr 4% -> w_LAG 0.50`.
Bảng `{NEUTRAL 65}` trong CLAUDE.md/context_pack là **doc cũ chưa cập nhật**, không phải lỗi hệ.
(Việc `lag_edge_health.csv` đứng ở 05-11 đã có kết luận riêng: `kb/projects/lag-edge-health-staleness.md`
— không phải bug, có falsifiable check ~08-25.)

## 5. Đề xuất (CHƯA làm gì — chờ Mike/user quyết)

Không tự sửa code production. Xếp theo mức đáng làm:

1. **Sổ episode CAPIT** (đóng đúng lỗ hổng user chỉ ra). Ghi 1 lần khi gate fire lần đầu, chỉ đóng
   khi exit: `data/capit_episode.json` = `{episode_id, entry_date, basket[], size, accounts{},
   qty_deployed{}, hold_until_session, status: open|closed}`. `golive_recommend_v23.py` đọc file
   này và ghi thêm `capit_episode_open` + `capit_episode_entry_date` +
   `capit_sessions_held` vào status JSON **bên ngoài** nhánh `if capit_fired`. Giải quyết luôn
   việc broker không gắn nhãn book (§1) và việc rổ tự co mỗi ngày (§2).
2. **Đổi gate của mọi kênh báo cáo** từ `capit_fired` sang `capit_fired OR capit_episode_open`:
   `telegram_recommend.py:463`, `mike/bin/bq_freshness_check.sh:571-577` (note CAPIT bơm vào prompt
   DollarBill), EOD report. Hiện tại từ 07-29 **mọi kênh im lặng hoàn toàn về CAPIT** dù đang giữ 5 mã.
3. **Fail-closed interpreter** trong `golive_recommend_v23.py`: từ chối chạy (exit≠0, không ghi đè
   artifact) nếu `pandas.__version__` major ≠ 3 / interpreter ≠ `$DNA_PYEXE`. Chặn đúng lớp sự cố §3
   ở nguồn, rẻ hơn mọi cơ chế cảnh báo sau-sự-việc.
4. **Đổi tên cho đúng nghĩa**: `capit_fired` → `capit_signal_today` (breaking, cần sweep consumer);
   tối thiểu phải ghi rõ ngữ nghĩa vào registry.
5. **Cập nhật `kb/data_registry/market-state/golive_v23_recommendations.md`**: nói rõ
   `data/golive_v23_status.json` = **snapshot ngày chạy, bị ghi đè mỗi phiên, KHÔNG phải sổ vị thế**;
   nguồn LỊCH SỬ chuẩn tắc = BQ `recommend_v23.status` / `recommend_v23.recommendations`
   (partition theo `signal_date`) — dataset này hiện **chưa có entry nào** trong registry.
6. **Sửa `kb/current_ops.md`**: rổ CAPIT là 5 mã (thêm NCT); và nói rõ `capit_fired` trong file
   status không phải chỉ báo "đang giữ CAPIT".
7. Ghi §3 vào `kb/incidents/2026-07/`.
