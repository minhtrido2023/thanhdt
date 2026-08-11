# 2026-08-11 — `dd_check` ghi dạng CHUỖI trong plan làm `step()` ném lỗi mỗi lần có FILL (22 POLL_FAIL ZaloPay + 27 SpaceX)

**Triệu chứng.** `ops_health_check.sh` 12:45 báo `{'POLL_FAIL': 22}` cho ZaloPay
(`exec_ZaloPay_2026-08-11_journal.csv`), note lặp lại y hệt:
`'str' object has no attribute 'get'`. SpaceX cùng ngày: 27 POLL_FAIL. Lịch sử: 08-11 là ngày
đầu tiên có hiện tượng ở quy mô này (07-24: 1, 07-27: 3, 07-28: 1 — nhiễu lẻ tẻ, note khác).

**Số khớp 1:1 là manh mối quyết định.** ZaloPay POLL_FAIL 22 = FILL 22; SpaceX 27 = 27. Tức
mỗi lần ghi được 1 FILL là ngay sau đó ném exception — lỗi nằm trong `_sync_fills()`, ngay
SAU dòng `self._journal("FILL", ...)`, chứ không phải trong `poll_orders()`.

**Root cause (tái lập được, không suy đoán).** `trading_bot/executor.py:659`:

```python
_dd = o.dd_check
if o.side == "buy" and _dd and _dd.get("has_red_flag") is True:
```

giả định `dd_check` là **dict**. Plan 2026-08-11 của CẢ HAI account ghi nó là **chuỗi văn xuôi**:
`"PASS — dd_check_for_order 2026-08-11, 0 red flag"` (2 mã TV1/DRI còn có `dcf_check` = `"CHEAP"`,
cũng chuỗi — `_dcf.get("status")` ở dòng 647 sẽ nổ y hệt nếu 2 mã đó khớp trước).

Tái lập bằng chính plan production:

```
$ python3 -c "from trading_bot.plan import load_plan; o=load_plan('2026-08-11','ZaloPay').orders[2]; o.dd_check.get('has_red_flag')"
AttributeError: 'str' object has no attribute 'get'      # khớp từng chữ với note trong journal
```

**Đây là lệch SCHEMA DỮ LIỆU, không phải regression code.** Kiểu `dd_check` theo ngày:
08-03→08-06 `none` · **08-07 `dict` · 08-10 `dict`** · **08-11 `str`** (cả 2 account). Code
`dd_check` vào từ commit `c504204` và chạy đúng 2 phiên trước đó. Người/luồng sinh plan
(DollarBill) lần này ghi văn xuôi thay vì object — không có gì kiểm kiểu ở ranh giới nạp plan,
nên plan sai schema đi thẳng vào executor.

**Ảnh hưởng thật (đã đo, KHÔNG mất tiền).** Exception bị `except` của `step()` bắt và xử
fail-safe ĐÚNG: `ghost_tickers = mọi mã trong plan` ⇒ chu kỳ đó không đặt lệnh mới. Hệ quả:
- mỗi chu kỳ có fill thì `_sync_fills` **bỏ dở vòng lặp** — các order đứng sau trong danh sách
  không được cập nhật `filled/done` chu kỳ đó (tự lành ở chu kỳ sau);
- `_lever_package_audit` **không chạy** ở những chu kỳ đó (guard đòn bẩy câm — chiều an toàn,
  vì placement đã bị chặn);
- throughput đặt lệnh chậm lại ~1 chu kỳ/lần fill.
Kết quả phiên sáng ZaloPay vẫn ổn: 11/13 order DONE, TV1+DRI còn `WAIT_QUOTA` (throttle
participation bình thường, không liên quan lỗi này).

**KHÔNG tự sửa — chạm vùng cấm.** Cả hai điểm vá khả dĩ đều nằm ngoài quyền Winston:
`trading_bot/plan.py::load_plan()` (ép kiểu/validate ở ranh giới nạp plan) và
`trading_bot/executor.py` (làm cứng 2 chỗ đọc `_dcf`/`_dd`). Đã escalate bus `question` +
Trading Daily.

**Đề xuất (chờ Taylor/Wags/user quyết):**
1. `load_plan()` — cùng chỗ và cùng tinh thần với `filter_excluded_tickers()` (§7) và
   `hard_no_chase_ceiling_vnd` (§24): field nào executor đọc như dict thì ở đây phải là dict,
   không phải thì **coi như `None` + ghi cảnh báo** (không được ném, không được để chuỗi lọt).
   Đây là ranh giới đúng: `load_plan()` đã im lặng lọc mất field lạ (§24) — thêm chuyện im lặng
   nuốt field SAI KIỂU thì không, phải ồn ào.
2. Ràng buộc phía sinh plan: `dd_check`/`dcf_check` là object có schema, prompt DollarBill nêu rõ.
3. Không dùng `getattr(_dd, "get", None)` rải rác trong executor làm cách vá chính — đó là vá
   triệu chứng ở 2 chỗ hôm nay và chỗ thứ 3 lần sau.

*Job `Winston_20260811_054509` (ops-autofix ZaloPay 12:45).*
