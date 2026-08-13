# Oshares vòng 5 — vá lỗi HIỂN THỊ + đo đủ 3 điểm gọi (job `Taylor_20260813_162914`)

**Việc**: 2 vấn đề quant-skeptic vòng 4 tìm ra (CONFIRMED nhưng kèm điều kiện, log
`mike/logs/verify_20260813_161316_1668591.log`) + 2 hạng mục kèm theo. **KHÔNG đổi một con số đặt
lệnh nào** — đây là lỗi hiển thị, lỗi đo, và một lưới giám sát mới.

Kết quả ngắn gọn: **cả hai vấn đề đều THẬT, và cả hai đều LỚN HƠN ước lượng của vòng 4.**

---

## Việc 1 · Đo đủ CẢ BA điểm gọi `oshares_at` — quant-skeptic ĐÚNG

`consumer_c_driver.py` bản trước chỉ đo `oshares_at(track, asof)` (dòng ~1008). `corp_action_daily.py`
gọi hàm này ở **ba** chỗ, mỗi chỗ hỏi một câu khác nhau nên một chỗ không nói thay được hai chỗ kia:

| # | Chỗ gọi | Hỏi tại NGÀY NÀO | Vai trò |
|---|---|---|---|
| 1 | `run()` ~1008 | `asof` | số **CÔNG BỐ** ra snapshot |
| 2 | `check_retro()` ~837 | `prev_asof` | tính lại **quá khứ** bằng feed hôm nay |
| 3 | `crosscheck()` ~872 | **ngày dòng quý CỦA TỪNG MÃ** (khác nhau mỗi mã, lùi tới ~3 tháng) | đối soát chéo với `ticker_financial` |

Driver nay chụp cả ba, **hai chân trong MỘT tiến trình trên CÙNG một `cache`** (chạy hai lượt
riêng thì khác biệt quan sát được sẽ lẫn giữa "cổng làm đổi" và "feed đổi giữa hai lượt").

### Số công bố lại — bật/tắt cổng chứng nhận neo AIS, `asof=2026-08-13`, track 33 mã / 29 mã đang giữ

| Điểm gọi | n | Mã ĐỔI | Đang giữ THẬT |
|---|---:|---|---|
| `publish` @2026-08-13 | 33 | **2** — EVF, SHB | cả 2 |
| `check_retro` @2026-08-12 ⚠️ | 33 | **2** — EVF, SHB | cả 2 |
| `crosscheck` @ngày dòng quý từng mã | 32 | **3** — EVF, SHB, **TCB** | cả 3 |

⇒ **"3/33 mã: EVF, SHB, TCB — 2 tại điểm publish, 3 tại điểm đối soát chéo"**, đúng như
quant-skeptic nói. Báo cáo vòng 4 ghi "2/33" là **đo thiếu**, không phải sai số học.

TCB lọt lưới vì `crosscheck` hỏi tại **2026-07-21** (ngày dòng quý), còn `publish` hỏi tại
**2026-08-13**. Tại 08-13 neo của TCB đã là `ticker_financial` nên cổng AIS không đụng tới; tại
07-21 neo là AIS 2025-12-01 và cổng chặn. Một điểm đo không thể suy ra điểm kia.

⚠️ `check_retro` **CHƯA kích hoạt trong lượt chạy thật hôm nay** — mới có đúng một snapshot đã
publish nên `prior_snapshot()` trả `None`. Số ở trên đo bằng phiên giao dịch liền trước
(`retro_synthetic=true` trong JSON) để biết trước nó sẽ làm gì từ lượt **08-14**. Ghi rõ ra chứ
không trình bày như số của lượt hôm nay.

Bằng chứng: `consC_3points.json` (`diff_gate_off_to_on` tách theo từng điểm).

---

## Việc 2 · Lỗi hiển thị Discord — THẬT, và ảnh hưởng **4 mã đang giữ**, không phải 1

### Bug

`corp_action_daily.py` dòng ~1182 render mọi bản ghi của `crosscheck()` bằng MỘT khuôn, trong khi
`crosscheck()` trả **hai loại khác hẳn nhau về nghĩa**:

* `DIVERGENT` — hai nguồn cùng trả số, hai số khác nhau.
* `NO_MODEL_VALUE` — mô hình **TỪ CHỐI** trả số (fail-closed). `oshares_live` là `None`, và
  **không có** trường sai số vì không có sai số nào để tính.

Khuôn cũ viết `(d['oshares_live'] or 0)` với `err_pct` mặc định `0`. `or 0` ở đây không phải một
mặc định lành tính: **nó biến một lời TỪ CHỐI TRẢ LỜI thành một con số, và con số đó tình cờ làm
sai số bằng đúng 0** — hướng sai lệch tệ nhất có thể, vì nó *trấn an* người đọc thay vì cảnh báo.

### Chứng minh trên dữ liệu SỐNG, không phải số học trên giấy

`probe_render_before_after.py` chạy `crosscheck()` thật (BQ, track set thật 2026-08-13) rồi render
bản ghi thu được bằng **đúng biểu thức f-string cũ chép nguyên văn từ commit `8908640`**:

```
KHUÔN CŨ  ⚠️ **Lệch nguồn Oshares** (5 mã, script KHÔNG tự chọn số):
          EVF@2026-07-21 corp-action 0 vs bq_admin   760,565,802 (0.00%);
          SHB@2026-07-30 corp-action 0 vs bq_admin 5,343,703,838 (0.00%);
          TCB@2026-07-21 corp-action 0 vs bq_admin 7,086,240,414 (0.00%);
          VPB@2026-07-20 corp-action 0 vs bq_admin 7,933,923,601 (0.00%);
          VRE@2026-07-29 corp-action 2,328,818,410 vs bq_admin 2,272,318,410 (2.49%)
```

**4 mã — EVF, SHB, TCB, VPB — TẤT CẢ đều đang giữ THẬT**, và cả 4 sẽ hiện ra như "khớp hoàn hảo"
trong báo cáo Discord sáng 08-14. Vòng 4 ước lượng 1 mã (TCB); con số thật là 4. VPB còn nằm ngoài
phạm vi vòng 4 hoàn toàn — nó `UNKNOWN_RATIO`, tức lỗi hiển thị này **có từ trước cổng chứng nhận
AIS**, đúng như quant-skeptic mô tả.

### Bản vá

`_fmt_divergence()` — hàm module-level (tách ra khỏi `run()` để **kiểm được CHUỖI**, xem dưới):

```
KHUÔN MỚI ⚠️ **Đối soát nguồn Oshares** (1 mã LỆCH + 4 mã KHÔNG đối soát được, script KHÔNG tự chọn số):
          EVF@2026-07-21 mô hình TỪ CHỐI trả số (AIS_UNCERTIFIED) — KHÔNG đối soát được với bq_admin 760,565,802;
          … TCB@2026-07-21 mô hình TỪ CHỐI trả số (AIS_UNCERTIFIED) — KHÔNG đối soát được với bq_admin 7,086,240,414;
          VRE@2026-07-29 corp-action 2,328,818,410 vs bq_admin 2,272,318,410 (2.49%)
```

Ba điểm thiết kế:
1. **Hai loại ĐẾM RIÊNG ở đầu dòng.** "5 mã lệch" và "1 lệch + 4 không đối soát được" là hai tình
   trạng khác nhau của hệ thống.
2. **MỘT vị ngữ `refused()` dùng cho CẢ đầu dòng lẫn thân dòng.** Bản nháp đếm theo `kind` nhưng
   render theo `oshares_live is None`; một bản ghi thiếu `kind` liền được đếm là "1 mã LỆCH" trong
   khi thân dòng nói "TỪ CHỐI". Ca R8 của selfcheck chốt việc này lại.
3. Cùng cách tách đã áp cho **payload bus**: `n_crosscheck_divergent` /
   `n_crosscheck_no_model_value` tách đôi, thay vì một con số gộp.

### Selfcheck — kiểm CHUỖI, không kiểm field

Vì sao phải nói rõ: ca **X4** đã có sẵn từ vòng trước, kiểm `d[0]["oshares_live"] is None` và
**PASS** — trong khi dòng Discord vẫn in "corp-action 0 … (0.00%)". Một `None` đúng trong dict
không chứng minh gì về chuỗi render; giữa hai cái có một `or 0`. Bug sống đúng trong khoảng hở đó
qua nhiều vòng review.

`t_render_divergence()` — **9 ca (R1-R9)**, tất cả assert lên **chuỗi thật**:

| Ca | Nội dung |
|---|---|
| R1 | `NO_MODEL_VALUE` ⇒ chuỗi nói TỪ CHỐI + nêu nhãn phương pháp + vẫn nêu số bq_admin |
| **R2** | **CA CHỨNG MINH NGƯỢC = chính bug đã ship**: chuỗi KHÔNG được chứa `corp-action 0` lẫn `0.00%` |
| R3 | `DIVERGENT` vẫn in đủ hai số + sai số đúng mẫu số (không hồi quy phần đang chạy) |
| R4 | hai loại đếm riêng ở đầu dòng |
| R5 | chỉ có `NO_MODEL_VALUE` ⇒ đầu dòng KHÔNG được nói "LỆCH" |
| R6 | rỗng ⇒ `None`, không đẻ dòng trống |
| R7 | quá `limit` ⇒ nói rõ còn bao nhiêu mã nữa (không im lặng cắt cụt) |
| R8 | thiếu `kind` + `oshares_live=None` ⇒ vẫn TỪ CHỐI, **và đầu dòng đếm khớp thân dòng** |
| **R9** | **ĐẦU-CUỐI**: bản ghi do chính `crosscheck()` sinh ra → render → chuỗi TỪ CHỐI (hai đầu khớp hình dạng dict, không phải fixture tự bịa) |

Thêm: `--no-alert` nay **IN RA** tin nhắn sẽ gửi (`[dry] tin nhắn SẼ gửi:`). Không in thì cách duy
nhất để kiểm chuỗi thật là để nó ping người thật — và đó chính là lý do lỗi này sống lâu.

---

## Việc 3 · Lưới giám sát diễn biến fail-closed (`none_value_watch`)

quant-skeptic gọi tình trạng cũ là "im lặng vĩnh viễn không giám sát", và đúng: fail-closed cấp mã
(`value is None`) an toàn theo thiết kế, nhưng nếu không ai theo dõi con số đó thì một feed hỏng
dần chỉ biểu hiện thành "im lặng ngày càng nhiều" — không cổng nào đỏ, không ai biết.

`none_value_watch(cur, prev_snap)` so số mã bị từ chối với **snapshot đã publish gần nhất**, publish
kết quả ra field `none_value_watch` của snapshot (để lượt sau có mốc và người đọc lại file thấy
được xu hướng), và đẩy vào bus (`n_none_value` / `none_value_alert`).

Bốn quyết định, mỗi cái có một ca selfcheck (`t_none_value_watch`, NW1-NW6):

| | Hành vi | Vì sao |
|---|---|---|
| NW1 | đứng yên ⇒ **KHÔNG** báo | báo DIỄN BIẾN, không báo hiện trạng đã biết |
| NW2 | tăng ⇒ BÁO, nêu đích danh mã MỚI + nhãn phương pháp | "3→5" một mình không hành động được |
| NW3 | **giảm ⇒ KHÔNG báo** (ca chứng minh ngược) | feed lành lại không phải sự cố; vẫn ghi `recovered` |
| NW4 | **tổng đứng yên nhưng ĐỔI MÃ ⇒ VẪN BÁO** | đếm tổng một mình sẽ nuốt mất ca này |
| NW5 | chưa có mốc ⇒ **CHƯA ĐÁNH GIÁ ĐƯỢC**, không báo, `delta=None` | cùng kỷ luật với `invariant_evaluated` — không mốc thì không kết luận |
| NW6 | gộp theo nhãn phương pháp | đọc được nguyên nhân, không chỉ con số |

Trạng thái thật hôm nay: `4/33 mã bị TỪ CHỐI trả số — CHƯA ĐÁNH GIÁ ĐƯỢC diễn biến (chưa có mốc)`,
mã DHN, EVF, SHB, VPB. **Mốc đầu tiên có từ lượt 08-14.**

⚠️ Chú ý dễ đọc nhầm: tập 4 mã này (`publish` @asof) **KHÁC** tập 4 mã `NO_MODEL_VALUE` của
`crosscheck` (EVF, SHB, TCB, VPB) — hai điểm hỏi hai ngày khác nhau. Lại đúng lý do Việc 1 tồn tại.

---

## Việc 4 · `SANITY_FACTOR` có cần cho người gọi THẲNG `oshares_at` không?

### TRẢ LỜI: **CÓ.** Đo được, không phải lập luận.

`probe_sanity_direct_call.py` — lưới **RỘNG HƠN** custom30: **1.070 mã** (mọi mã có ≥1 dòng AIS
`executed`) × **48 mốc quý** 2014→2026 = **51.360 ô**, đi qua ĐÚNG đường gọi thẳng `oshares_at`.

Định nghĩa "ô lọt" = `oshares_at` **TRẢ SỐ** (cổng chứng nhận đã cho qua) nhưng số đó lệch quá
`SANITY_FACTOR` lần so với dòng quý gần nhất ≤ ngày đó — tức tập "chỉ cổng biên độ bắt được".

| | |
|---|---:|
| ô được `oshares_at` phục vụ | 37.327 |
| **ô LỌT cổng chứng nhận, cổng biên độ ×3 SẼ chặn** | **279 (0,75%) / 34 mã** |
| theo nhãn | `AIS_EXACT` 252 · `ISS_ESTIMATE` 27 |
| hướng | 218 ô live QUÁ NHỎ · 61 ô live QUÁ LỚN |
| ô từ 2024 trở lại | 67, trên 10 mã |
| ô gần nhất | 2026-03-31 |

Quét theo ngưỡng (⚠️ **tập nền lọc ở ×3 nên các dòng ngưỡng <3 là CẬN DƯỚI, không phải số đúng**):

| ngưỡng × | ô lọt | mã |
|---:|---:|---:|
| 3,0 | 279 | 34 |
| 5,0 | 190 | 17 |
| 10,0 | 68 | 8 |
| **13,0** | **40** | **7** |
| 30,0 | 37 | 4 |
| 1000,0 | 12 | 1 |

Ở ngưỡng 13× ra **40 ô** — cùng bậc độ lớn với "~27 ô" mà docstring `oshares_live` ghi. Hai con số
**không mâu thuẫn**: 27 đo trên lưới custom30 (hẹp hơn nhiều), 40 trên 1.070 mã. Con số cần dùng để
trả lời câu hỏi này là **279 ở ngưỡng production ×3**.

### Ca thật, và nó chạm mã ĐANG GIỮ

**2 trong 34 mã lọt đang được giữ THẬT: VHM và VND.**

VHM: dòng AIS **2021-10-12** mang `shares_total_after = 4.354.367` trong khi số thật là
**4.354.367.488** — sai **×1000**, gần như chắc chắn là lỗi đơn vị của vendor. `oshares_at` phục vụ
nó ở nhãn tin cậy cao nhất **`AIS_EXACT`** suốt **13 ô quý** (2021-12-31 → 2024-12-31), tới khi một
AIS sau đó thay chỗ.

Hôm nay không ảnh hưởng (neo của VHM đã là `ticker_financial` 2026-07-30, giá trị publish
8.214.824.008 hợp lý). Nhưng **cơ chế thì đang sống**: vendor công bố một dòng AIS sai hôm nay thì
`corp_action_daily` publish thẳng, cổng chứng nhận không chặn.

### `corp_action_daily` có lớp bù không? CÓ MỘT PHẦN — và lỗ hổng đo được

Chạy `check_invariants` + `withhold_suspect` thật trên đúng con số VHM:

| Tình huống | Kết quả |
|---|---|
| (a) CÓ mốc hôm trước mang số đúng, hôm nay nhảy ×1/1000 | `UNEXPLAINED_DROP` ⇒ **value=None, `INVARIANT_SUSPECT`** ✅ bắt được |
| (b) **KHÔNG có mốc** (snapshot đầu tiên / mã mới vào track set) | **0 vi phạm ⇒ CÔNG BỐ NGUYÊN SỐ SAI** ❌ |
| (c) **mốc ĐÃ mang số sai** (từ ngày thứ hai) | **0 vi phạm ⇒ số sai sống tiếp, im lặng** ❌ |

Lớp bất biến chỉ bắt **CHUYỂN TIẾP**. Nó mù với "sai ngay từ ô đầu tiên" và với "sai rồi tự nhất
quán với chính nó". Cổng biên độ đóng đúng hai lỗ đó vì nó so với một nguồn ĐỘC LẬP
(`ticker_financial`) chứ không so với chính mình hôm qua.

**Và (b) đúng là trạng thái của hệ THÁNG NÀY** — hôm nay `prev_snap` là `None`, gate-3 in
`CHƯA ĐÁNH GIÁ ĐƯỢC (chưa có mốc)`.

### Khuyến nghị — KHÔNG tự wire

Cổng biên độ cho `corp_action_daily` là **đổi số công bố**, không phải sửa hiển thị ⇒ ngoài phạm vi
job này (dispatch nói rõ "KHÔNG đổi số đặt lệnh gì"). Đề xuất cho vòng sau, kèm ghi chú thực thi:

* Số nền cần có sẵn rồi: `crosscheck()` đã lấy đúng dòng quý ≤ `asof` cho từng mã — không cần truy
  vấn thêm.
* Nhưng **`SANITY_FACTOR` ở `oshares_pit` là POLICY của consumer**, và mỗi consumer có ngưỡng riêng
  hợp lý. Đưa nguyên si ×3 sang `corp_action_daily` là một **quyết định chính sách** (nó sẽ giấu số
  của 34 mã ở các ô lịch sử), cần user duyệt chứ không phải quant-skeptic một mình — theo
  `coding_guidelines` §22 (tách quyết định CHÍNH SÁCH khỏi quyết định KỸ THUẬT).
* Lựa chọn rẻ hơn và không đổi số nào: **báo** (WARN) khi `|live/quarterly|` vượt ×3 thay vì giấu
  số — thông tin thuần, đúng tinh thần `crosscheck()` "KHÔNG chọn bên nào đúng".

---

## Kiểm chứng

| Bộ | Kết quả |
|---|---|
| `corp_action_daily_selfcheck.py` | **142/142 PASS** (127 cũ + 15 mới: R1-R9, NW1-NW6) |
| lại dưới `TZ=America/New_York`, `TZ=UTC`, `env -u TZ` (§16) | **142/142 PASS** cả 3 |
| `oshares_live.py --selfcheck` | 32/32 PASS (không đụng) |
| `oshares_pit.py --selfcheck` | 48/48 PASS (không đụng) |
| `corp_action_daily.py --dry-run --no-alert` trên dữ liệu thật | chạy sạch; tin nhắn thật đã đọc bằng mắt, TCB in đúng |

**Không hồi quy phần đã CONFIRMED**: 127 ca cũ giữ nguyên, không sửa ca nào. `oshares_live.py` và
`oshares_pit.py` không đổi một dòng — cổng chứng nhận vòng 4 nguyên vẹn.

## File

| File | Đổi gì |
|---|---|
| `mike/bin/corp_action_daily.py` | `_fmt_divergence()` + `none_value_watch()` mới; wire vào `run()`; tách đếm 2 loại ở log/bus; `--no-alert` in tin nhắn |
| `mike/bin/corp_action_daily_selfcheck.py` | +15 ca (`t_render_divergence`, `t_none_value_watch`) |
| `research/…/consumer_c_driver.py` | đo đủ 3 điểm, A/B 1 tiến trình / 1 cache |
| `research/…/probe_render_before_after.py` | **mới** — chuỗi cũ vs mới trên dữ liệu sống |
| `research/…/probe_sanity_direct_call.py` | **mới** — 51.360 ô, đo lọt cổng biên độ |
| `research/…/consC_3points.json`, `sanity_direct_call.json` | dữ liệu đo |

## Còn treo sau vòng này

1. **Cổng biên độ cho `corp_action_daily`** — chưa wire, cần user duyệt (quyết định chính sách).
2. **`check_retro` chưa chạy thật lần nào** — kích hoạt từ lượt 08-14; số ở Việc 1 là `synthetic`.
3. **`none_value_watch` chưa có mốc** — mốc đầu tiên từ lượt 08-14. Ngày đầu nó **phải** in
   "CHƯA ĐÁNH GIÁ ĐƯỢC"; nếu in ra một phán quyết thì đó là bug.
