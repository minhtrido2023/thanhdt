# Provenance — artifact job `Winston_20260918_052425` (treasury size inference)

Thư mục này là **artifact của Winston**, được Taylor `git add` trong job
`Taylor_20260918_110145` (N3) để **chốt bytes lại làm bằng chứng**, không phải để sửa.

## Vì sao phải chốt
`final3.py` (và `final.py`/`final2.py`) **ghi đè output của chính nó** — không có tên file
versioned: `final3.py` → `final_inferred.csv` / `resolved.csv` / `still_unsized.csv`. Chạy lại là
mất bản cũ. Quan sát được trên filesystem lúc chốt: `final3.py` mtime **2026-09-18 12:32** nhưng
`resolved.csv` + `final_inferred.csv` mtime **17:31** và `inferred.csv` + `still_unsized.csv`
**17:33** ⇒ đã có ít nhất một lần chạy lại SAU khi script được sửa lần cuối. **Ai chạy thì không
xác định được từ filesystem** (thư mục chưa vào git nên không có history) — không đoán, và đó
chính là lý do chốt bytes ngay.

## Cái ĐÃ kiểm chứng được về bytes này
- `inputs/{resolved,final_inferred}.csv` trong `agents/Taylor/research/treasury_table_20260918/`
  là snapshot **byte-identical** (md5 khớp) với 2 file cùng tên ở đây ⇒ loader của Taylor đọc
  đúng bộ bytes đang được commit này.
- `agents/Taylor/.../patch/resolved_patched.csv` (chạy `final3.py` đã vá `SHARE_CODES`) cũng
  **md5 khớp** `resolved.csv` ở đây ⇒ bản vá là no-op trên batch này.
- Đếm lại trực tiếp từ `final_inferred.csv` (577 dòng): 131 `is_unsized=False`
  (118 chỉ có `shares_delta` + 13 ca CONTROL có cả `shares_delta` lẫn `inferred`) và
  446 `is_unsized=True` (413 không có `inferred` + 33 có).

## Đính chính một con số của `report.md` ở đây (KHÔNG sửa report gốc)
`report.md` viết "**410** thật sự KHÔNG có dữ liệu" (= 446 − 33 − 3). Con số đúng là **413**:
3 sự kiện "thu hồi miễn phí / dòng anh em" (CTD 2018-02-06, HVG 2020-01-13, KHW 2018-02-22) **đã
nằm trong 131 sized rồi** — chính `final_inferred.csv` ghi `is_unsized=False` cho cả 3, vì dedup
`MAX(shares_delta)` lấy được số từ dòng anh em. Chúng KHÔNG nằm trong 446, nên trừ lần thứ hai là
đếm trùng. Bảng `tav2_mike.treasury_share_events` dùng **413 UNSIZED**.
(`report.md` dòng 97 tự viết "413 ca không suy được (gồm 410 + 3 …)" — tức chính nó đã chạm tới
413; chỉ headline dòng 7-8 và bảng §3 dùng 410.)

## ⚠️ Bẫy nặng hơn, phát hiện lúc chốt: `still_unsized.csv` KHÔNG phải 413 ca của report

**BỐN script cùng ghi vào MỘT tên file** `still_unsized.csv`: `infer_size.py:124`,
`final.py:66`, `final2.py:68`, `final3.py:79`. Bytes hiện tại là output của **`infer_size.py` —
thế hệ ĐẦU TIÊN**, không phải `final3.py`. Bằng chứng cơ học (bộ từ vựng `tier`, không phải suy đoán
từ mtime):

| file | n dòng | tier xuất hiện |
|---|---:|---|
| `still_unsized.csv` (hiện tại) | **342** | NO_MOVE 182, MULTI_EVENT 80, SIGN_MISMATCH 45, NO_DATA 26, **IMPLAUSIBLE 9** |
| `final_inferred.csv` (`is_unsized` ∧ không `inferred`) | **413** | CA_CONFOUNDED 143, NO_MOVE 134, MULTI_EVENT 94, NO_DATA 26, ISSUANCE_MATCH 8, SIGN_MISMATCH 6, **OVER_CAP 2** |

`IMPLAUSIBLE` chỉ tồn tại trong `infer_size.py`/`final.py`/`final2.py`; `OVER_CAP` và
`ISSUANCE_MATCH` chỉ tồn tại trong `final3.py`. File hiện tại có `IMPLAUSIBLE` và **không có**
`CA_CONFOUNDED` ⇒ nó ra từ `infer_size.py`, trước cả `final.py`.

**Và nó là file mtime MỚI NHẤT trong thư mục** (17:33, cùng `inferred.csv` — đúng cặp output của
`infer_size.py`; `resolved.csv`/`final_inferred.csv` của `final3.py` là 17:31). ⇒ Ai chọn file
theo "mới nhất" sẽ lấy đúng kết quả của thuật toán CŨ. Dòng "`still_unsized.csv` (413)" trong
`report.md` §Artifact vì thế không đúng với bytes đang có.

**Hệ quả cho bảng:** không dùng `still_unsized.csv`. Nguồn chuẩn tắc của 413 ca UNSIZED là
`final_inferred.csv` lọc `is_unsized=True ∧ inferred` rỗng — đúng cái
`build_treasury_share_events.py::load_winston_reasons()` đang đọc (đối chiếu khớp: 413 dòng,
7 `unsized_reason` đúng như bảng trên).
