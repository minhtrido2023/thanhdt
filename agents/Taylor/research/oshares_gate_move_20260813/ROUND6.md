# Vòng 6 — khép chuỗi Oshares/corp-action 2026-08-13

**Job** `Taylor_20260813_172023` · nối tiếp vòng 5 (`Taylor_20260813_162914`, verdict **CONFIRMED
high**, log `mike/logs/verify_20260813_170117_1706552.log`).

**Phạm vi**: 6 điểm quant-skeptic vòng 5 liệt kê + **1 điểm phát sinh khi verify live** (mục 7).
**KHÔNG có số đặt lệnh nào đổi.** `oshares_live.py`, `oshares_pit.py`, `corp_action_lib.py`
**byte-identical** với vòng 4/5 (`git diff HEAD` rỗng trên cả ba). Chỉ đụng
`mike/bin/corp_action_daily.py` + `mike/bin/corp_action_daily_selfcheck.py` + tài liệu.

Selfcheck: **142 → 153 PASS** (11 ca mới, 0 ca cũ sửa). **6 mutation test** chứng minh các ca mới
thật sự phân biệt được, không phải test cảnh.

---

## 1. Đính chính nguyên nhân TCB (SAI trong ROUND5.md + payload bus)

Bản vòng 5 viết *"Tại 08-13 neo TCB đã là `ticker_financial` nên cổng AIS không đụng tới"* — **sai**.

Đo lại trên snapshot thật `data/corp_action_daily/corp_action_daily_2026-08-13.json` và BQ:

```
TCB @2026-07-21: value=None          method=AIS_UNCERTIFIED anchor=2025-12-01 src=corporate_action.AIS
TCB @2026-08-13: value=7,086,240,414 method=AIS_EXACT       anchor=2026-08-05 src=corporate_action.AIS

tav2_bq.corporate_action  TCB AIS executed 2026-08-05 shares_total_after=7,086,240,414
tav2_bq.corporate_action  TCB AIS executed 2025-12-01 shares_total_after=7,064,851,739
tav2_bq.ticker_financial  TCB @2026-07-21 OShares    =7,086,240,414
```

**Nguyên nhân thật**: một dòng **AIS MỚI HƠN hiệu lực 2026-08-05**, có `shares_total_after` bằng
đúng `ticker_financial`, nên **QUA được cổng chứng nhận**. Cổng AIS **có** xét TCB tại 08-13 — nó
*cho qua*, không phải *không xét*. Trùng khớp với `ticker_financial` là **hệ quả**, không phải
nguồn neo.

**KẾT LUẬN GIỮ NGUYÊN**: hai điểm gọi khác ngày ⇒ hai neo khác nhau ⇒ không suy ra được điểm này
từ điểm kia. Chỉ sửa NGUYÊN NHÂN.

Sửa ở: `ROUND5.md` (khối trích dẫn ĐÍNH CHÍNH, giữ nguyên câu sai + nói rõ sai chỗ nào — không
xoá dấu vết) + payload bus vòng 6 này.

> Vì sao đáng sửa dù không đổi con số nào: đội đã dính đúng loại lỗi này (bảng trống hậu tố
> `vnindex_5state` bị đọc là DT5G). Một câu giải thích sai được archive sẽ bị trích nguyên văn ở
> vòng sau.

## 2. `refused()` lên mức module — log/bus/Discord không thể lệch nhau

`corp_action_daily.py:1129` (cũ) đếm `n_crosscheck_no_model_value` bằng vị ngữ **chỉ-theo-`kind`**
riêng của nó, trong khi chuỗi Discord đếm bằng `refused()` (kind **hoặc** `value is None`) — đúng
khiếm khuyết R8 dời sang tầng log/bus, trái với chính lời payload vòng 5 tuyên bố.

Sửa: `refused()` chuyển từ hàm lồng trong `_fmt_divergence` ra **mức module**; `run()` gọi lại
đúng hàm đó. Vị ngữ giờ được **viết đúng một lần** trong cả file.

**Ca R10** (mở rộng fixture `bare` của R8 sang tầng bus): trên bản ghi cố ý thiếu `kind`, khẳng
định *đếm đầu dòng == đếm bus/log == nội dung thân dòng*, **cộng** một khẳng định cấu trúc —
`source.count('== "NO_MODEL_VALUE"') == 1` — chặn mọi lần cài lại vị ngữ ở bất kỳ tầng nào.

## 3. `_fmt_divergence.one()` — không cho một bản ghi méo giết cả dòng cảnh báo

Cũ: `d['err_pct_vs_ticker_financial']` ⇒ `KeyError` giữa luồng cảnh báo hàng ngày.
Mới: `d.get(...)` + nhánh in **"không rõ sai số"**. Cố ý **không** rơi về `0` — đó chính là cái
`or 0` đẻ ra bug TCB "0,00% ⇒ trông như khớp hoàn hảo".

**Ca R11**: bản ghi DIVERGENT thiếu trường sai số, đứng chung dòng với một mã lành — khẳng định
không nổ, không in `0.00%`, **và mã lành vẫn in đủ hai số**.

## 4. R5 so không phân biệt hoa/thường

Cũ grep đúng chữ `"LỆCH"` viết hoa ⇒ tiêu đề cũ `**Lệch nguồn Oshares**` **lọt PASS oan**.
Mới: `"lệch" not in s.lower()`.

## 5. Hai nguyên nhân của `value is None` — TÁCH NGUYÊN NHÂN, KHÔNG cắt con số

`none_value_watch` chạy **sau** `withhold_suspect` nên `n_none` gộp hai chuyện khác hẳn nhau:
(a) mô hình từ chối tại nguồn ⇒ **kiểm feed**; (b) `INVARIANT_SUSPECT` — có số nhưng bị GIẤU do
vi phạm bất biến ⇒ **đọc dòng 🚨**, kiểm feed là đi sai hướng.

**Chọn phương án rẽ nhánh văn bản, KHÔNG loại `INVARIANT_SUSPECT` khỏi `n_none`.** Lý do: cổng
`systemic` chỉ nổ khi vi phạm **diện rộng**; loại khỏi bộ đếm thì vi phạm **lẻ tẻ dưới ngưỡng**
biến mất khỏi mọi con số — tạo đúng một điểm mù mới ở chỗ vừa dựng lưới để bịt. `n_none` giữ
trọn (nó là câu trả lời đúng cho *"hôm nay bao nhiêu mã KHÔNG có số dùng được"*); thêm
`n_none_invariant` + `by_method`, và văn bản 🔇 rẽ nhánh theo đó (**toàn bộ** do bất biến / **trộn**
hai nguyên nhân / **thuần** feed). **Ca NW10.**

## 6. Xoay vòng track set — chỉ so trên TẬP SO ĐƯỢC

`track = held ∪ ex_today ∪ ais_today` đổi thành viên mỗi ngày, nên hai snapshot liền nhau nói về
**hai tập mã khác nhau**. Luật cũ so `set(now)` với `set(before)` trên hai tập đó ⇒ mã **rời**
track set trông y hệt *"lành lại"*, mã **mới vào** trông y hệt *"vừa hỏng"*.

Sửa: mọi phép so (`delta`, `newly_none`, `recovered`, `alert`) chạy trên
`comparable = set(cur) ∩ set(prev)`. Mã vào/ra kể riêng ở `entered_none` / `left_none`, **có in
ra** log lẫn nội dung cảnh báo nhưng **không kích** cảnh báo — đúng kỷ luật `has_baseline`, áp ở
cấp **từng mã**: không có mốc cho mã đó thì không có kết luận về mã đó. `n_none` vẫn là **tổng**;
chỉ các trường `*_cmp` mới là cơ sở cảnh báo (bus mang cả hai).

Verify LIVE `--asof 2026-08-14`:
```
[gate-4b im lặng] 4/35 mã bị TỪ CHỐI trả số — so được 1→3 trên 29 mã chung với mốc 2026-08-13,
                  Δ+2 MỚI: ['EVF','SHB'] [vào track set, chưa có mốc riêng: ['HRB']]
                  [rời track set: ['DHN']]
```
HRB **không** còn bị tính là "vừa hỏng"; DHN **không** còn bị tính là "lành lại". Ca churn mà
quant-skeptic đo được **đã hết kích cảnh báo**.

**Ca NW7/NW8** dựng đúng ca thật đó; **NW9 là ca chứng minh ngược** — vẫn xoay vòng track set,
nhưng một mã CÓ MỐC (FPT) mất số ⇒ **vẫn phải báo**, và chỉ nêu đích danh FPT. Không có NW9 thì
bộ lọc "tập so được" có thể đã nuốt luôn thứ lưới này được dựng để bắt.

## 7. ⚠️ PHÁT SINH KHI VERIFY LIVE — nguyên nhân báo động giả THỨ HAI cho sáng 08-14: **mô hình đổi, không phải feed đổi**

Sau khi vá mục 6, lượt chạy live 08-14 **vẫn** bắn 🔇 — nhưng vì EVF/SHB, không phải churn. Truy
tới cùng:

| Bằng chứng | Kết quả |
|---|---|
| Snapshot mốc 08-13 `generated_at` | **2026-08-13T17:07:58+07:00** |
| Commit nâng cổng chứng nhận neo AIS | `ffe4b39` **22:15**, `8908640` **23:08** — đều SAU mốc |
| Gọi `oshares_at(["EVF","SHB"], "2026-08-13")` bằng mã HÔM NAY | `AIS_UNCERTIFIED`, **value=None** |
| Chính snapshot 08-13 đang lưu | EVF `AIS_EXACT` 704.248.289 · SHB `ISS_ESTIMATE` 5.377.339.511 |
| BQ: dòng AIS/ISS mới của EVF/SHB? | **KHÔNG** — lần nạp gần nhất **2026-08-12** |
| BQ: sự kiện quyền EVF/SHB hiệu lực 08-14? | **KHÔNG** (08-14 chỉ có DQC/HRB/NQB/PSW/VSH DIV + SGR ISS) |

⇒ **Cùng một `asof=2026-08-13` cho hai câu trả lời khác nhau, chỉ vì mã đổi giữa hai lượt.**
"Hôm nay nhiều mã bị từ chối hơn hôm qua" đang so **hai định nghĩa khác nhau** của *"trả được
số"*. Câu *"kiểm feed"* sẽ khiến người đọc lục feed cả buổi sáng cho một thay đổi **do chính bản
vá của mình gây ra**.

**Sửa**: `model_version()` — sha256 rút gọn **nội dung** `corp_action_lib.py` + `oshares_live.py`
(cùng danh sách `_model_files()` mà `gate_selfcheck` dùng, cố ý: "cái gì được kiểm trước khi
publish" và "cái gì định nghĩa phiên bản" phải là một tập). Ghi vào **mọi** snapshot kể cả bản
`_FAILED`, và vào bus.

Theo **nội dung** chứ không theo git hash: file sửa **chưa commit** vẫn phải đổi chữ ký, và `git`
có thể vắng mặt ở môi trường cron. **Ca NW15** chứng minh bằng cách thật sự sửa 1 dòng vào một
bản sao.

**KHÔNG chặn cảnh báo** — mất số vẫn là mất số, EVF/SHB là mã **đang giữ thật** và người đọc phải
biết. Chỉ **đổi lời chẩn đoán**:
* `model_changed=True` → *"nghi phạm số một là chính bản vá đó siết chặt, không phải feed"*.
* `model_changed=None` (mốc chưa ghi chữ ký) → *"CHƯA LOẠI TRỪ ĐƯỢC"* — **không** tự nhận là
  "cùng mô hình". **Ca NW13**; mutation M5 chứng minh nhánh này thật.

**Chuỗi 🔇 THẬT sẽ gửi sáng 08-14** (đã chạy `--dry-run --no-alert`, đọc bằng mắt):
```
🔇 Số mã bị TỪ CHỐI trả số CP tăng: 1 → 3 trên 29 mã SO ĐƯỢC với mốc 2026-08-13
(tổng hôm nay 4/35); MỚI: EVF (AIS_UNCERTIFIED), SHB (AIS_UNCERTIFIED); (mã MỚI VÀO track set
hôm nay, chưa có mốc riêng nên KHÔNG tính vào đây: ['HRB']). Fail-closed nên KHÔNG có số sai nào
được công bố — … ⚠️ Mốc 2026-08-13 KHÔNG ghi chữ ký mô hình ⇒ CHƯA LOẠI TRỪ ĐƯỢC khả năng thay
đổi này đến từ bản vá của chính mình chứ không phải feed.
```

**Nói thẳng giới hạn**: mốc 08-13 đã publish nên **không có** chữ ký để so — sáng mai câu chẩn
đoán là *"chưa loại trừ được"*, dù trong báo cáo này đã **chứng minh xong** là do mô hình đổi.
**CỐ Ý không sửa ngược snapshot 08-13** để "làm đẹp" tin nhắn: đó là artifact đã publish, sửa nó
là tự hợp thức hoá đúng kiểu lỗi hệ này được dựng để chặn. Từ **08-15** trở đi mọi mốc đều có chữ
ký và câu chẩn đoán tự chính xác.

---

## Mutation test — các ca mới có thật sự phân biệt được không

| # | Đột biến | Ca phải FAIL | Kết quả |
|---|---|---|---|
| M1 | `run()` quay lại vị ngữ chỉ-theo-`kind` | R10 | ✅ FAIL |
| M2 | `one()` quay lại `d[...]` | R11 | ✅ nổ `KeyError` |
| M3 | bỏ lọc "tập so được" | NW7, NW8, NW9 | ✅ cả 3 FAIL |
| M4 | tiêu đề cũ `**Lệch nguồn Oshares**` | R5 | ✅ FAIL (bản cũ PASS oan) |
| M5 | `model_changed` không phân biệt "thiếu chữ ký" vs "đã đổi" | NW13 | ✅ FAIL |
| M6 | chữ ký bỏ qua nội dung file | NW15 | ✅ FAIL |

## Bằng chứng không hồi quy

| Kiểm | Kết quả |
|---|---|
| `corp_action_daily_selfcheck.py` | **153/153 PASS** (142 nền + 11 mới; **0 ca cũ bị sửa**) |
| `git diff HEAD -- oshares_live.py oshares_pit.py corp_action_lib.py` | **rỗng** — không đụng module sinh số |
| Cổng vòng 3/4/5 (`gate-1 selfcheck`) trên lượt chạy live | PASS — `corp_action_lib` + `oshares_live` selfcheck đều rc=0 |
| Lượt live `--asof 2026-08-14 --dry-run --no-alert` | chạy sạch tới cuối, tin nhắn đã đọc bằng mắt |
| Số đặt lệnh / sizing / NAV | **không đụng đường nào** |

## Việc còn lại (không tự nhận đã đóng)

1. **Chờ quant-skeptic vòng CUỐI.** Không tự tuyên bố khép chuỗi.
2. **08-14 sau 07:30 ICT**: xác nhận live rằng (a) 🔇 gửi đúng chuỗi trên, (b) `check_retro` thật
   sự kích hoạt với `prior_snapshot` thật, (c) snapshot 08-14 có `model_version`. Cả ba đều mới
   chỉ chạy dry-run.
3. **Việc B (chọn consumer cho `corporate_action`)** vẫn chờ user — không đổi ở vòng này.
