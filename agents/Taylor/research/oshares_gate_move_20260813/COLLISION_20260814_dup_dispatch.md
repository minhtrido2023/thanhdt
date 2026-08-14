# VA CHẠM DISPATCH — hai job Taylor cùng wire cổng biên độ ×3 vào CÙNG file, cách nhau 52 giây

**Ngày**: 2026-08-14 07:35–07:45 ICT · **Job của tôi**: `Taylor_20260814_003610`
**Job va chạm**: `Taylor_20260814_003518` (Mike dispatch, khởi động trước 52 giây, đang RUNNING)

## Kết luận: TÔI ĐÃ DỪNG VÀ HOÀN NGUYÊN TOÀN BỘ PHẦN CỦA MÌNH. Không có việc nào bị mất của bên kia.

## Chuyện gì xảy ra

Mike dispatch HAI job Taylor chạy song song, cả hai cùng thực thi quyết định C của user
(cổng biên độ `SANITY_FACTOR=3` thành **WARN, không ẩn số** trong `mike/bin/corp_action_daily.py`):

| | `Taylor_20260814_003518` | `Taylor_20260814_003610` (tôi) |
|---|---|---|
| started_at | 00:35:23Z | 00:36:10Z (+52s) |
| prompt | "2 việc nhỏ còn treo từ chuỗi corp-action/TV1, Mike đã quyết cả 2" | "ROUND5 Việc 4 → WARN ×3, phương án C của user" |
| thread Discord | 1521470705563340910 (Trading Daily) | — |
| API đã cài | `sanity_flag()` + `sanity_warns()`, `import oshares_pit as _pit`, dùng `_pit.SANITY_FACTOR` đọc tại LÚC GỌI, áp cho **cả 3 điểm gọi** `oshares_at()` | `magnitude_watch()` + `_fmt_magnitude()` + hằng số riêng `CORP_ACTION_SANITY_FACTOR`, chỉ áp cho điểm publish |

Không job nào biết job kia tồn tại. Cả hai `write_scope` đều RỖNG, không worktree, không lock —
**đúng chế độ hỏng đã được ghi trong `context_pack.md`** ("⚠️ Rủi ro quy trình phát hiện cùng tối
[2026-08-07]: dispatch Mafee + Taylor sửa CÙNG file `plan_funding_gate.py` trong vòng 1 phút không
cách ly"). Lần đó commit của một bên cuốn theo phần việc chưa commit của bên kia; lần này chưa ai
commit nên chưa mất gì.

## Tôi phát hiện bằng cách nào

Tool `Edit` trả cảnh báo *"the file had been modified on disk since you last read it"*. Đối chiếu:
`sed -n '130,155p'` lúc 07:36 KHÔNG có dòng nào về `SANITY_FACTOR`; lúc 07:40 đã có
`import oshares_pit as _pit` + 6 dòng docstring "quyết định Mike 2026-08-14, xem `sanity_flag`".
`stat` cho mtime 07:40:14 trong khi `date` là 07:40:27 — file đang được ghi bởi tiến trình khác
NGAY LÚC ĐÓ. `ls bus/jobs/*.json` xác nhận 3 job Taylor cùng `status=running`.

## Tôi hoàn nguyên thế nào (không đụng việc của bên kia)

KHÔNG dùng `git checkout` (sẽ xoá luôn phần chưa commit của job kia). Gỡ tay đúng 7 hunk của mình:
hằng số, `latest_quarter_row`/`magnitude_watch`/`_fmt_magnitude`, sửa `crosscheck()` về nguyên bản,
dòng `[gate-4c]`, field snapshot, dòng Discord, field bus.

Bằng chứng sau khi gỡ:
* `git diff | grep "📏|MAGNITUDE_SUSPECT|gate-4c|magnitude|latest_quarter_row|CORP_ACTION_SANITY"`
  → rỗng (rc=1). Không còn dấu vết nào của tôi.
* `git diff -U0 | grep "^@@"` → còn đúng 4 hunk, TẤT CẢ thuộc job kia: docstring §NGƯỠNG (+6),
  import `_pit` (+5), khối `sanity_flag`/`sanity_warns` (+88), `check_retro` (1 dòng).
* Mọi dòng `-` trong diff đều là dòng job kia tự thay ở `check_retro` — tôi không xoá dòng nào của ai.
* `ast.parse` OK.

## Thiết kế của tôi — GIỮ LẠI ĐỂ ĐỐI CHIẾU, không phải để wire

Job kia rộng hơn (3 điểm gọi vs 1) nên nếu chọn một bản thì chọn bản đó. Ba điểm bản của tôi có
mà bản kia nên kiểm xem có không — nêu ra như checklist review, KHÔNG phải đòi merge:

1. **Ngưỡng là KNOB RIÊNG hay dùng chung với `oshares_pit`?** Tôi cố ý tách
   (`CORP_ACTION_SANITY_FACTOR`), lập luận: ở `oshares_pit` con số đó là POLICY của một consumer
   (nó GIẤU số live), dùng chung nghĩa là ai sweep cổng chọn mã custom30 cũng lặng lẽ đổi độ nhạy
   cảnh báo hàng ngày. Job kia cố ý dùng chung (`_pit.SANITY_FACTOR`, đọc tại lúc gọi), lập luận
   ngược lại: hai giá trị cho cùng một ngưỡng là chỗ hở "hai phần fleet đọc hai số". **Cả hai đều
   có lý — đây là quyết định CHÍNH SÁCH, nên do người chốt, không phải do job nào chạy sau đè lên.**
2. **Nhãn phải RÕ KHÁC hai cảnh báo cạnh nó.** Đang có 🚨 (bất biến ⇒ số ĐÃ BỊ GIẤU) và ⚠️ (đối
   soát lệch tại ngày dòng quý). Cảnh báo mới nói "số VẪN ĐƯỢC CÔNG BỐ NGUYÊN VẸN" — khác biệt
   quan trọng nhất với 🚨 và phải nằm ngay trong tiêu đề, không phải cuối dòng.
3. **Tách mã ĐANG GIỮ ra trong chuỗi + trong bus** (`magnitude_suspect_held`): 2/34 mã lọt ở
   ROUND5 là VHM và VND — đang giữ thật. Đó mới là nhóm chạm tiền.

Ngoài ra: mã có `value is None` phải bị bỏ qua (gồm nhóm `withhold_suspect` vừa giấu), nếu không
cùng một mã bị đếm ở hai dòng cảnh báo khác nhau.

## Việc trong dispatch của tôi mà KHÔNG ai làm được vì va chạm

Chưa chạy: bộ selfcheck sau patch, ca VHM 2021-10-12 (×1000) thật, ca biên =3,0 chẵn, ca chứng
minh ngược <3×, chạy lại dưới `env -u TZ` + TZ lạ. **Baseline đo được trước khi patch:
`corp_action_daily_selfcheck.py` PASS 153/153** (dispatch ghi "142 ca" — số đã cũ, bộ đã lớn lên;
ai verify vòng sau phải dùng 153 làm mốc, đừng dùng 142).
