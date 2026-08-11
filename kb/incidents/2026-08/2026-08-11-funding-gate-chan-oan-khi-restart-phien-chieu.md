# 2026-08-11 — FUNDING gate chặn OAN ZaloPay khi restart phiên chiều: gate tính trên TOÀN BỘ plan, không trừ phần đã khớp buổi sáng

**Hiện tượng.** Cron 13:00 ICT (`run_bot.sh --account ZaloPay --auto-otp`, resume state) thoát
`rc=3`: `⛔ FUNDING GATE — Σ lệnh MUA 108.211.098đ VƯỢT sức mua thật 60.570.877đ (pp0Buy) —
tiêu thụ 178,7%`. Bot ZaloPay **không chạy suốt phiên chiều**, để lại lệnh sống không ai quản:
`BUY-TV1-DISC-01` child oid 136481 (200cp @20.000, status `open`) + `BUY-DRI-DISC-02` còn 100cp.
SpaceX 13:00 chạy bình thường.

**Chẩn đoán (số thật, không suy đoán).** Buổi sáng plan đã khớp gần hết: 11/13 lệnh PARK `DONE`,
DRI khớp 1.800/1.900cp. Nhu cầu vốn CÒN LẠI thật sự của phiên chiều:

| | Σ nhu cầu | pp0Buy đo sống | util |
|---|---:|---:|---:|
| Gate tính (toàn bộ `orders[]`) | 108.211.098đ | 60.570.877đ | **178,7% → BLOCK** |
| Thực tế còn lại (trừ phần đã khớp) | **27.230.785đ** (TV1 25,9tr + DRI 1,3tr) | 60.570.877đ | **45% → phải OK** |

**Root cause.** `trading_bot/plan_funding_gate.py:245` — `buys = [o for o in plan.orders if
side == "buy"]`, cộng `o.qty × o.ref_price` trên **số lượng gốc trong plan**, hoàn toàn không đọc
`data/execution_logs/exec_<acc>_<date>_state.json` (`parents[*].filled`). Comment tại call site
`bot_execute.py:536` viết "Σ ở đây là tập lệnh THẬT SỰ sắp đặt" — đúng cho phiên khởi động LẦN
ĐẦU, **sai cho mọi lần resume**: sáng tiêu tiền thật ⇒ `pp0Buy` tụt, còn mẫu số nhu cầu vẫn giữ
nguyên toàn plan ⇒ càng khớp nhiều buổi sáng thì càng chắc chắn bị chặn buổi chiều.

**KHÁC root cause 2026-08-10** (`Σ pp0Buy` đếm hũ tiền chung nhiều lần, đã vá `19e788f` — lần này
dòng `[hũ chung … = min pp0Buy của 2 nhóm]` chứng tỏ bản vá đó đang chạy đúng). Đây là lỗi thứ
hai, độc lập, cùng file.

**Đã KHÔNG tự vá** — gate tiền thật nằm trong vùng cấm của Winston (ops-autofix mandate mục 3).
Escalate: bus question `funding-gate-chan-oan-khi-resume-phien-chieu` + Telegram trading_daily.

**Đề xuất vá (cần Taylor/quant-skeptic + user duyệt):** trong `check_plan_funding`, khi tồn tại
state file của đúng `(account, plan_date)`, tính `need` trên **qty CÒN LẠI**
(`max(0, o.qty − parents[o.id].filled)`) thay vì `o.qty`. Fail-safe: đọc state lỗi/không có ⇒ giữ
nguyên hành vi hiện tại (dùng qty gốc, chặt hơn), **không bao giờ lỏng hơn khi thiếu bằng chứng**.
Lệnh đã `done` ⇒ nhu cầu 0.

**Bài học.** Một gate cấp-PLAN chạy trong tiến trình có RESUME phải khai rõ nó đo *trạng thái nào*:
"tập lệnh của plan" hay "tập lệnh còn phải đặt". Hai đại lượng này bằng nhau đúng một lần trong
ngày. Cùng họ với §14 (verify artifact, đừng suy từ giả định về thời điểm chạy).
