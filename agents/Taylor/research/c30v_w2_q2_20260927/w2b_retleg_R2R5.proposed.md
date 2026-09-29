# ĐỀ XUẤT (không merge) — R2/R5 của `basket_return_leg_oshares_selfcheck.py`

Job `Taylor_20260927_155645` (W2b, quant-skeptic recommended_rerun #4). **Chỉ đề xuất** — không sửa
`custom_basket.py`, không sửa selfcheck canonical.

## Chẩn đoán: KHÔNG có baseline nào để "refresh"

Dispatch giả định R2/R5 neo vào một **baseline lưu sẵn** có thể regen sang `exdate`. Đọc code thì
không phải: baseline là **một module dựng từ git ref**, không phải file số.

```
basket_return_leg_oshares_selfcheck.py:82   ref = os.environ.get("BASKET_RETLEG_PREREF", "HEAD")
                                      :83   src = git show f"{ref}:./custom_basket.py"
                                      :86   if "BASKET_RETURN_OSHARES" in src: SystemExit(...)
```

Module tiền-sửa ấy **không có** knob `BASKET_OSHARES_STEP` (`custom_basket.py:148,216` — knob ra đời
cùng bản vá exdate) ⇒ nó CHỈ biết bước OShares theo QUÝ. Vì vậy "regen baseline sang exdate mode" là
việc **không thể thực hiện**: không có cách nào bắt một module tiền-exdate sinh ra weight exdate.

## Bằng chứng cơ học (không phải suy luận) — 3 log cùng `TZ-ICT__dnapy`, cùng WORKDIR canonical

`research/postmerge_haukiem_20260927/selfchecks/`:

| log | `BASKET_OSHARES_STEP` | kết quả |
|---|---|---|
| `…__PREREF2c_STEPQUARTER__…` | `quarter` | **PASS TOÀN BỘ** (R5 `max|Δlevel| = 0.000000e+00` / 415 phiên) |
| `…__PREREF2c_EXDATE__…` | `exdate` (mặc định) | **FAIL 2** — R2 md5(weight), R5 `max|Δlevel| = 9.223644e+01` |
| `…__PREREF__…` | `exdate` (mặc định) | **FAIL 2** — cùng cặp md5, cùng `9.223644e+01` |

Một biến env, hai kết quả, mọi thứ khác giữ nguyên ⇒ nguyên nhân là **chế độ bước OShares**, không
phải chân return-leg mà R2/R5 tưởng đang đo. (Đúng §29: kết luận này trích từ log vừa đọc, không
đoán.)

## Vì sao 2 assertion đó FAIL "đúng theo thiết kế"

R2/R5 được viết để chứng minh **một** điều: knob `BASKET_RETURN_OSHARES` KHÔNG làm đổi đường tiền
weight. Chúng làm điều đó bằng cách so với module tiền-sửa. Sau khi bản vá **exdate** (một thay đổi
ĐỘC LẬP, chạm đúng đường weight) được merge và thành mặc định, phép so đó gộp **HAI** thay đổi vào
một assertion ⇒ nó fail vì thay đổi thứ hai, và không còn nói gì về thay đổi thứ nhất.

## Đề xuất — 1 dòng, trong SELFCHECK, không chạm `custom_basket.py`

Trong `run()` (`basket_return_leg_oshares_selfcheck.py:99`), nơi đã pin `BASKET_RETURN_OSHARES`,
pin thêm chế độ bước OShares về `quarter` cho CẢ 3 chân (mới / legacy / tiền-sửa) của R2+R5:

```python
prev_step = os.environ.get("BASKET_OSHARES_STEP")
os.environ["BASKET_OSHARES_STEP"] = "quarter"   # R2/R5 do MOT bien: BASKET_RETURN_OSHARES.
#   Module tien-sua (load_pre_edit) khong co knob nay va chi biet buoc theo QUY; de mac dinh
#   `exdate` thi R2/R5 gop 2 thay doi doc lap vao 1 assertion va fail vi thay doi SAI.
```
…restore trong `finally` y như dòng 104-106.

**Cộng thêm (khuyến nghị mạnh, biến nợ đỏ thành sức phân giải)** — một assertion kiểu R3
positive-control để chế độ `exdate` KHÔNG còn im lặng:

```python
# R6. exdate PHAI doi weight (neu khong, ban va exdate la no-op)
os.environ["BASKET_OSHARES_STEP"] = "exdate"
h_ex, _ = publish_weight_md5(cur, *build(...))
check("R6 exdate weight KHAC quarter (ban va exdate co tac dung thuc)", h_ex != h_new,
      f"{h_ex} vs {h_new}")
```

## Xác nhận đã làm / chưa làm

- ĐÃ xác nhận nguyên nhân bằng 3 log thật ở trên (không chạy lại — 3 log đó đủ phân giải).
- **CHƯA** áp patch: đây là code canonical, dispatch W2b là PAPER-ONLY. Cần Mike/user duyệt.
- Rủi ro của patch: R2/R5 sau patch **không còn** phủ đường `exdate` — đó đúng là lý do phải thêm R6
  cùng lượt, không tách ra sau.
