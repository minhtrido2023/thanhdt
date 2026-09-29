# DEVIATIONS — dividend_yield_floor_20260818

Sai lệch so với `PREREG.md` (commit `beabb4f8`, khoá TRƯỚC mọi query outcome). Mỗi mục có
marker `# DEVIATION Dn` ngay tại dòng code gây ra nó.

---

## D1 — `trailing_div(t) > 0` chỉ áp cho chân SỰ KIỆN, không áp cho toàn mẫu
`analyze.py:235`

PREREG §4.1 mục 4 viết điều kiện này vào "MỌI ngày-cổ-phiếu vào mẫu". Áp đúng chữ thì **nhóm
chứng NON-PAYER rỗng theo định nghĩa** (non-payer có `div0 = 0`), và §6 không chạy được. Điều
kiện được giữ nguyên ở chân sự kiện (Test A crossing, Test B proximity — cả hai đều cần
`trailing_div > 0` để `yield`/`prox` tồn tại), bỏ ở pool ứng viên chứng.

**Ảnh hưởng**: không có, với chân sự kiện. Không có nó thì §6 vô nghĩa.

---

## D2 — Test "giá bất khả thi" §4.2 áp trên `Close`, không trên `Price`
`analyze.py:245`

PREREG §4.2 viết: loại dòng có `P_raw(t) ∉ [Low(t), High(t)]`. Nhưng `ticker.Low/High` là giá
**đã hồi tố** (sống trong hệ quy chiếu `Close`), còn `Price` là giá thô. Đo trên chính panel này:

| Đại lượng | Giá trị |
|---|---|
| median `Price/Close` | 1,284 (p90 = 3,03) |
| `Close ∈ [Low, High]` | 99,9997% số dòng |
| `Price ∈ [Low, High]` | **24,7%** số dòng |
| Số crossing hợp lệ nếu đọc đúng chữ | 1.469 → **65** |

Đọc đúng chữ thì test vứt 96% mẫu vì **lệch hệ quy chiếu**, không phải vì dữ liệu hỏng. Test
được áp trong đúng hệ quy chiếu mà `Low/High` sống. Ý định của §4.2 — "loại dòng có bằng chứng
tự chứa rằng giá không thể có thật" — được giữ nguyên.

**Bù lại**: chữ ký thật của bẫy registry (`Price` đứng yên trong khi `Close` đã đổi) được tính
riêng thành cờ `stale_px` (0,48% số dòng) và báo cáo như một chân sensitivity
(`ex_stale_px`) — **cố ý KHÔNG** biến thành bộ lọc thứ ba, vì thêm filter sau khi nhìn dữ liệu
là thêm tham số tự do. Kết quả `ex_stale_px` trùng khít primary (Test B: +3,456 → +3,456).

---

## D3 — `ticker.ICB_Code` là mã ICB 4 chữ số, không phải nhãn thô CT/NH/BH/CK
`analyze.py:263, 369, 489, 528`

PREREG §6/§7.4 (và `bigquery_schema.md`) mô tả `ICB_Code` là nhóm ngành thô CT/NH/BH/CK. Thực
tế cột chứa **mã ICB subsector 4 chữ số** (76 giá trị phân biệt trong panel; 8355 = Ngân hàng,
2357 = Xây dựng nặng…).

- Ngân hàng (§7.4) nhận diện bằng `icb == 8355`.
- "Cùng ICB_Code" khi ghép cặp (§6) dùng **ICB industry** = `code // 1000` — đúng mức thô mà §6
  yêu cầu. Ghép theo subsector 4 chữ số sẽ **chặt hơn hẳn** mức đã prereg.

---

## D4 — Thêm placebo GHÉP CẶP bên cạnh placebo gốc
`analyze.py:414, 533`

PREREG §8 yêu cầu "chạy đúng pipeline trên ngày giả `t − 250` phiên". Bản cài đặt đầu
(`placebo()`) chỉ kéo outcome của chính mã sự kiện lùi 250 phiên — nó **không chạy lại bước
ghép cặp**, nên không trả lời được câu hỏi mà placebo sinh ra để trả lời: *khoảng cách
sự kiện − chứng có đặc thù cho việc đang đứng ở sàn, hay chỉ là khoảng cách thường trực giữa
một mã trả cổ tức ổn định và một mã không trả, vào bất kỳ ngày nào?*

`placebo_matched()` chạy TOÀN BỘ pipeline (kể cả re-match) trên ngày giả. Đây đúng là bài học
Sprint 2 (`corp_action_program_20260815`): null của một pipeline **không mặc định bằng 0** cho
tới khi đo. Giữ **cùng với**, không thay thế, bản gốc.

**Đây là deviation quan trọng nhất về mặt kết luận** — xem FINDINGS.md §4.

---

## D5 — Chân falsification thêm ngoài prereg (khai báo là THÊM, không phải thay)
`analyze.py` — `far_from_floor`, `pretrend_matched`

Hai chân này **không có trong PREREG** và không được dùng để đổi tiêu chí §9. Chúng chỉ để
người đọc tự phản biện, và được báo cáo dù kết quả bất lợi:

- `far_from_floor` (`prox > 1,3` — giá ở XA phía trên sàn, cơ chế yield floor lẽ ra không áp
  dụng): nếu ΔMDD vẫn dương lớn ở đây thì "sàn cổ tức" chỉ là tên gọi khác của "mã cổ tức ổn
  định thì ít drawdown hơn".
- `pretrend_matched`: episode Test B chạm sàn **bằng cách rơi**, nên xu hướng giá 60 phiên
  trước là confound mà ghép cặp đã prereg (ICB + rvol) KHÔNG đóng. Chân này ghép thêm theo
  `pret60` dải ±10pp.

---

## Không phải deviation — ghi để khỏi hiểu nhầm

- `analyze.py` không chạy lại `build.py`. Panel là artifact của attempt 1 cùng job-family
  (`build_summary.json` ghi `"resumed": "stages 1-5 reused from disk"`). Panel được sinh
  TRƯỚC khi bất kỳ outcome nào bị nhìn.
- `scipy` không có trên host ⇒ Spearman trong `selfcheck.py` tính tay (Pearson trên hạng).
  Cùng định nghĩa, không phải xấp xỉ.
