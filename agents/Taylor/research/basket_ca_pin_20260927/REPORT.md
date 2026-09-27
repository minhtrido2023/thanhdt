# VIỆC 3 — PIN `BASKET_CA_SNAPSHOT` cho `basket_price_basis_selfcheck.py`

job `Taylor_20260927_131720` · 2026-09-27 21:2x ICT · branch `fix/basket-ca-snapshot-pin-2709`
(worktree `mike/agents/Taylor/wt-casnap-2709`, trên `2b2f6a28`) — **CHƯA MERGE**.

## Kết quả một dòng

Ghim xong, **6/6 lần chạy đầy đủ liên tiếp byte-identical** (`md5 83c449b3ec97a7cf1f05e437c4503f9d`
cho cả 6 log). **Nhưng phần chẩn đoán trong đề bài không đứng được**: đo độc lập cho thấy bảng
corp-action KHÔNG hề đổi hôm nay, nên cái pin này **không giải thích** lần T1 FAIL chưa rõ nguyên
nhân — và trên đường đi lại lộ ra **một lỗi khác, thật, fail-OPEN**, đúng lớp lỗi ấy nhưng ở
`forensic_flags.csv`.

## 1. Việc đã làm

`basket_price_basis_selfcheck.py` — thêm `_ca_snapshot_candidates()` + `_pin_corp_action_vintage()`,
gọi ở đầu `main()`:

- Mặc định ghim `data/snapshots/corp_action_share_20260927.parquet` (vintage 11:53 ICT 2026-09-27,
  cùng vintage mà lệnh pin `research/oshares_weight_exdate_20260927/run_publish_leg_v3.sh` đã chạy
  trên — cố ý KHÔNG sinh vintage 09-27 thứ hai, để một ngày chỉ có một nguồn sự thật).
- In dấu vết kiểm được từ ngoài: `vintage: 14912 dòng ISS+AIS, 1434 mã, digest=7409599216578255470`.
- **FAIL-CLOSED** nếu không tìm thấy vintage ở đâu cả — không âm thầm rơi về LIVE BQ.
- Hai lối thoát tường minh: `BASKET_CA_SNAPSHOT=<path>` (env thắng) · `BASKET_CA_SNAPSHOT=` rỗng
  (khai rõ "tôi muốn đọc live").
- **Fallback cây canonical** (thêm ngoài đề bài, có lý do đo được): vintage là `*.parquet`, bị
  `.gitignore:73` chặn ⇒ **không worktree nào có nó**. Nếu chỉ tìm theo `WORKDIR` thì cổng
  fail-closed ở đúng lúc cần nhất — lúc review một branch trong worktree — tức tái lập y hệt cái
  bẫy Mike vừa vá cho `WORKDIR`/T5 vài giờ trước, chỉ dịch từ CODE sang DỮ LIỆU. Cây canonical suy
  ra bằng `git rev-parse --git-common-dir`, **không hardcode đường dẫn**.

## 2. Tất định — 6/6 byte-identical

```
run1..run6 EXIT=0   md5 83c449b3ec97a7cf1f05e437c4503f9d  (cả 6 log giống nhau từng byte)
mỗi run: vintage 14912 dòng / 1434 mã / digest 7409599216578255470   ← KHÔNG đổi
         [oshares-step] 1736 dòng (cửa sổ RECENT) · 1875 dòng (cửa sổ OLD)   ← KHÔNG đổi
```

Chạy trên **LIVE BQ** (log: `BQ_LOCAL_CACHE = (live BQ)`) — tức là bản thử KHẮT KHE hơn chạy trên
cache đóng băng, không dễ hơn.

**Giới hạn phải nói rõ**: 6 lần đó nằm trong CÙNG một buổi tối (21:01→21:16 ICT). Panel giá đọc từ
`tav2_bq.ticker`, mà bảng đó sync 23:45 ICT ⇒ **tất định QUA MỐC 23:45 thì chưa chứng minh**. Đo
thật cho thấy điều này không phải lo xa: đổi cache dữ liệu làm các con số IN RA của T2 đổi thật —
`data/bq_cache` cho `recent p50 0.892, Δ -8.47pp` còn `bq_cache_asof20260729_postrestate` cho
`p50 0.926, Δ -15.25pp`. Verdict của 6 check vẫn PASS ở cả hai (chúng là bất biến cấu trúc: "phải
bằng 0" / "phải khác 0"), nhưng ai dùng dòng in ra làm số tham chiếu thì phải ghim cả cache.

## 3. Điều KHÔNG đúng trong chẩn đoán gốc — đo độc lập

Đề bài quy lần T1 FAIL chưa giải thích được cho việc corp-action đổi giữa các lần chạy
(Mike đo `1706/1843` rồi `1736/1875`). Tôi đo lại, và nó **không khớp**:

| Đo | Kết quả |
|---|---|
| LIVE BQ ngay bây giờ (`COUNT(*)` ISS+AIS, `event_status != not_executed`) | **14.912 dòng**, `MAX(public_date) = 2026-09-25` |
| Snapshot lấy 11:53 ICT cùng ngày | **14.912 dòng** |

⇒ bảng **không đổi một dòng nào** trong ~9,5 giờ hôm nay. Thêm nữa, `1736/1875` là số dòng **SAU
khi lọc về member-union của lượt chạy** (`custom_basket.py:275-283`), nên cặp `1706/1843` → `1736/1875`
là bằng chứng về **member-union**, không phải về bảng corp-action. Và cả 3 cấu hình dữ liệu tôi chạy
(live BQ · `data/bq_cache` · `bq_cache_asof20260729_postrestate`) đều cho **đúng 1736/1875**.

**Kết luận đúng mực**: pin vẫn đáng làm vì lý do CẤU TRÚC — bảng bị UPSERT IN-PLACE
(`kb/data_registry/price-volume/corporate_action_bq.md` Bẫy 2b: `public_date` bị ghi đè khi sự kiện
lật trạng thái), nên một kết quả pin hôm nay không tái lập được sau vài tháng nếu đọc live. Nhưng
pin này **KHÔNG đóng được** lần T1 FAIL kia, và **không nên** ghi vào KB là đã đóng.

## 4. Lỗi THẬT tìm thấy trên đường đi — fail-OPEN ở `forensic_flags.csv` (cần user/Mike quyết)

Chạy selfcheck từ worktree, log in ra:

```
[forensic exclude] none ([Errno 2] No such file or directory:
  .../wt-casnap-2709/WorkingClaude/data/forensic_flags.csv)
```

so với canonical:

```
[forensic exclude] custom30 universe drops from flag date:
  {'KSF','VVS','PC1','HHS','L40','KLB','DIG','BFC' — đều 2026-06-20}
```

- `data/forensic_flags.csv` bị `.gitignore:57` (`*.csv`) chặn và **không được git theo dõi** ⇒
  **không worktree nào có nó**.
- `custom_basket.py:642-644` bắt exception rồi in `none (...)` và **đi tiếp** — fail-OPEN. Hành vi
  này được `lag_forensic_filter.py:67` khai là CÓ CHỦ Ý ("thiếu file → giữ nguyên danh sách").
- Hệ quả: **mọi lần chạy selfcheck này từ worktree đều âm thầm bỏ 8 mã forensic-exclude**
  (KSF, VVS, PC1, HHS, L40, KLB, DIG, BFC) — **3 trong số đó nằm trong danh sách BANNED vĩnh viễn**
  (KSF, VVS, PC1). Universe khác ⇒ T2/T3 ra số khác canonical, mà log chỉ nói "none" chứ không nói
  "tôi đang chạy thiếu 8 mã".
- Đây **đúng lớp lỗi** mà pin của tôi vừa vá cho `*.parquet`, chỉ khác là nó fail-OPEN thay vì
  fail-CLOSED. Tôi **KHÔNG tự sửa**: `custom_basket.py` là module production mà lệnh pin R3 chạy
  qua, đổi cách nó resolve universe là thay đổi cấp wire, cần người duyệt.

## 5. Selfcheck 2 chiều cho chính bản vá

`pin_resolution_selfcheck.py` — phạm vi theo §23 (chỉ 2 hàm được thêm; phần T1-T5 không đổi một
dòng và đã có 6 lần chạy đầy đủ làm bằng chứng riêng):

| | Nội dung |
|---|---|
| P1 | ghim mặc định trong cây của chính file + ĐẶT được env + in số dòng/digest; cây không-phải-git vẫn chạy |
| P2 | fail-closed thật (env trỏ file lạ · cây không có vintage ở đâu cả) |
| P3 | env trỏ file thật THẮNG pin · env RỖNG = khai muốn live, và không âm thầm đặt lại |
| P4 | chạy từ **worktree thật** (không có vintage tại chỗ) → resolve sang cây canonical, có nhãn riêng |

Mutation **4/4 bị giết**: M1 bỏ fallback (= bản tiền-vá) ⇒ P4 đỏ · M2 `exists()` luôn True ⇒ P2 đỏ ·
M3 log nói ghim nhưng không đặt env ⇒ P1 đỏ · M4 coi env rỗng như chưa set ⇒ P3b đỏ.

PASS dưới `$DNA_PYEXE` (3.12.13) ở **4 môi trường giờ**: `Asia/Ho_Chi_Minh`, `America/New_York`,
`UTC`, và `env -u TZ`.

## 6. ĐỀ XUẤT wire (đề xuất thôi — KHÔNG tự wire)

Điều chỉnh lại tiền đề của đề bài: **`run_selfchecks.sh` đã tự nhặt file này lên rồi** (nó
auto-discover `find -iname "*selfcheck*.py"`, dòng 60). `is_live()` khớp `import simulate_holistic_nav`
⇒ xếp tier **live** ⇒ hiện **bị SKIP ở lượt mặc định**, chỉ chạy khi `--live` với trần **300s**.
Không cần thêm dòng nào để nó "được chạy"; cần đúng 2 chỉnh:

1. **Lượt MẶC ĐỊNH (offline): cho chạy `--scan-only`.** Đo thật 3 lần: **0,69-0,74s**, không chạm
   BQ, tất định by-construction (chỉ AST+regex trên file). Đây là cổng CƠ HỌC chống trộn
   số-lượng-thô × giá-đã-điều-chỉnh — hiện nó có **0 coverage hằng ngày**. Cùng khuôn ngoại lệ
   `report_return_gate_selfcheck.py` đang dùng:
   ```bash
   *basket_price_basis_selfcheck.py)
     if [ "$RUN_LIVE" -eq 1 ]; then t=600; else SC_ARGS=(--scan-only); t=60; fi ;;
   ```
2. **Lượt `--live`: nâng trần 300s → 600s.** Đo thật: một lần chạy đầy đủ ~150-190s khi máy rảnh,
   nhưng 2-3 lượt chạy song song đã đẩy lên ~300s. Trần 300s hiện tại là rc=124 chờ sẵn, đúng lớp
   "timeout mismatch" mà chính file runner đã ghi 3 lần.

**Điều kiện tôi tự đặt cho mình trước khi ai wire lượt `--live`**: sửa fail-OPEN ở mục 4 trước.
Nếu không, cron sẽ chạy nó ở canonical (có `forensic_flags.csv`, đúng) còn người review chạy ở
worktree (thiếu, sai) — hai bên ra số khác nhau và không ai biết vì sao. Lượt `--scan-only` ở đề
xuất 1 **không** vướng chuyện này (T5 không đọc `data/`) nên có thể wire độc lập, ngay.

## 7. Tệp
```
research/basket_ca_pin_20260927/
  REPORT.md                     ← file này
  pin_resolution_selfcheck.py   ← selfcheck 2 chiều + 4 mutation
  determinism.txt               ← run1..run6 EXIT=0 + 2 run worktree
  pinned_run1..6.log            ← 6 lần chạy đầy đủ, byte-identical
  wt_run_liveBQ.log             ← chạy từ worktree (lộ fail-OPEN forensic_flags)
  wt_run_pinnedcache.log        ← chạy từ worktree + cache asof20260729_postrestate
```

**`_pf_bpb_pinned_run16.py`** = ĐÚNG bản đã chạy 6 lần determinism (bản TRƯỚC khi thêm fallback cây
canonical; đặt ở gốc canonical nên `WORKDIR` = canonical, nơi vintage CÓ SẴN ⇒ nhánh fallback không
tham gia, 6 log vẫn là bằng chứng hợp lệ cho đường canonical). Giữ lại làm vật chứng, đã dọn khỏi
gốc `WorkingClaude/` để không thành file lạc canonical (§10).
