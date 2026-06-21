# Hướng dẫn cấp quyền GHI BigQuery cho server (cho Claude trên server)

> Mục tiêu: làm cho server ghi được BigQuery **giống hệt máy local** (local đang đọc-ghi
> bằng tài khoản user `dtienthanh@gmail.com`). Hiện server **chỉ đọc được**, chưa ghi được.

---

## ✅ TRẠNG THÁI ĐÃ ÁP DỤNG (2026-06-16) — đọc cái này trước

Đã bật ghi BigQuery cho server bằng **Cách B (transplant credential dtienthanh)**, vì:
- **Cách A bất khả thi từ `dtienthanh@gmail.com`**: tài khoản này có quyền ghi DATA nhưng **KHÔNG phải IAM-admin** → `add-iam-policy-binding` báo `setIamPolicy ... denied`, và nó cũng không phải OWNER của dataset `tav2_bq` (owner thật = **`nhh.1501@gmail.com`**). Muốn làm Cách A phải nhờ `nhh.1501` chạy.
- Đã copy credential gcloud của `dtienthanh@gmail.com` từ local sang server, đặt trong **config riêng** `/home/trido/thanhdt/gcloud_dtienthanh` (chmod 700), **không đụng** config gcloud mặc định của server (vẫn là SA read-only).
- Đã wire vào `wc_env.sh`: biến `CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh`.
- **Đã test write-probe (create→read→drop) THÀNH CÔNG** dưới danh tính `dtienthanh@gmail.com`.

**→ Cách dùng quyền ghi trên server (cho Claude server + mọi cron):**
```bash
source /home/trido/thanhdt/WorkingClaude/wc_env.sh   # set CLOUDSDK_CONFIG + PATH gcloud + WORKDIR_8L
# từ đây bq/python client ghi được tav2_bq dưới dtienthanh@gmail.com
```
Không source thì shell dùng config mặc định (SA `bq-reader-8l@`, chỉ đọc).

**Nếu token transplant hết hạn / bị revoke** (mất quyền ghi sau này): làm lại Cách B bằng `gcloud auth login` (mục dưới), hoặc nhờ owner `nhh.1501@gmail.com` chạy Cách A (sạch & bền nhất cho tự động hoá).

Phần bên dưới là tài liệu gốc đầy đủ 3 cách (tham khảo / phương án dự phòng).

---

## 0. Bối cảnh đã xác minh (đừng đoán lại — đã test thực tế 2026-06-16)

| Hạng mục | Local (máy Windows) | Server (`trido@192.168.100.7`) |
|---|---|---|
| Project | `lithe-record-440915-m9` | `lithe-record-440915-m9` |
| Dataset | `tav2_bq` (asia-southeast1) | như local |
| Danh tính `bq` đang dùng | **user `dtienthanh@gmail.com`** (đọc-ghi) | **service account `bq-reader-8l@lithe-record-440915-m9.iam.gserviceaccount.com`** (CHỈ ĐỌC) |
| gcloud SDK | `...\google-cloud-sdk\bin` | `/home/trido/google-cloud-sdk/bin` (đã cài, **chưa** trên PATH của shell non-interactive) |
| Kết quả test ghi | OK | ❌ `Access Denied: Permission bigquery.tables.create denied on dataset tav2_bq` |

**Cách scripts ghi BQ:** đa số dùng **`bq` CLI** (vd `bq load`, `bq query` với `CREATE OR REPLACE TABLE`),
một số ít dùng python client `google.cloud.bigquery`. → Phải cấp quyền cho **cả `bq` CLI** (chính) lẫn ADC (phụ).

**Sự thật kỹ thuật đã test (để khỏi mất công thử lại):**
- `bq` CLI **bắt buộc có "active account" trong gcloud**; KHÔNG tự fallback sang ADC, kể cả khi thêm `--use_google_auth`.
- `gcloud auth login --cred-file=<file>` của bản gcloud này **chỉ nhận service-account / external-account**, **không nhận** file `authorized_user`.
- Trong project trên server có sẵn 2 file credential:
  - `gcp_credentials.json` → loại `authorized_user` = chính token của `dtienthanh@gmail.com` (**có quyền ghi**, đã có refresh_token).
  - `sa-key.json` → key của **chính SA read-only** `bq-reader-8l@...` (KHÔNG giúp ghi được).

---

## Chọn 1 trong 3 cách dưới đây. Khuyến nghị: **Cách A** (nhanh nhất, không cần thao tác trên server).

---

## Cách A — Cấp role GHI cho service account hiện có *(khuyến nghị cho server/tự động hoá)*

Server đang chạy bằng SA `bq-reader-8l@`. Chỉ cần **thêm quyền ghi cho SA đó** thì server ghi được ngay,
**không phải đổi gì trên server**, không dính token user hết hạn.

**Chạy lệnh này TỪ MÁY LOCAL** (nơi `dtienthanh@gmail.com` là owner của project — có quyền sửa IAM):

```bash
# (PATH gcloud local đã có sẵn trong ~/.bashrc)
gcloud projects add-iam-policy-binding lithe-record-440915-m9 \
  --member="serviceAccount:bq-reader-8l@lithe-record-440915-m9.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

# jobUser thường đã có (SA này chạy query đọc được rồi); thêm cho chắc nếu báo thiếu:
gcloud projects add-iam-policy-binding lithe-record-440915-m9 \
  --member="serviceAccount:bq-reader-8l@lithe-record-440915-m9.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"
```

- `roles/bigquery.dataEditor` = tạo/ghi/xoá bảng trong dataset. `roles/bigquery.jobUser` = chạy job query/load.
- Muốn **giới hạn chỉ dataset `tav2_bq`** thay vì cả project: cấp `dataEditor` ở mức dataset (BigQuery Console → dataset `tav2_bq` → Sharing → Permissions → add principal = SA, role = BigQuery Data Editor); vẫn cần `jobUser` ở mức project.
- ⚠️ Lưu ý đặt tên: SA tên "reader" nhưng giờ ghi được → nếu khó chịu về mặt ngữ nghĩa, dùng **Cách A' (tạo SA writer riêng)** ở phần Phụ lục.

**Sau khi cấp xong, KHÔNG cần làm gì trên server.** Sang mục **§ Kiểm tra** để xác nhận.

---

## Cách B — Đăng nhập server bằng chính user `dtienthanh@gmail.com` *(giống local 1:1)*

Cho server danh tính y hệt local. Cần thao tác đăng nhập **một lần** (headless, dán code, không cần trình duyệt trên server).

Chạy **TRÊN SERVER**:

```bash
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"

# 1) Đăng nhập user cho bq CLI (in ra 1 URL — mở URL đó bằng trình duyệt BẤT KỲ máy nào,
#    đăng nhập dtienthanh@gmail.com, copy code dán lại vào terminal):
gcloud auth login dtienthanh@gmail.com --no-launch-browser

# 2) Đặt active account + project:
gcloud config set account dtienthanh@gmail.com
gcloud config set project lithe-record-440915-m9

# 3) (Tuỳ chọn) ADC cho các script dùng python client google.cloud.bigquery:
gcloud auth application-default login --no-launch-browser
```

- Sau bước 1, `bq` chạy dưới `dtienthanh@gmail.com` → ghi được.
- gcloud lưu refresh-token, không phải đăng nhập lại mỗi lần.
- Server vẫn còn config SA cũ; lệnh trên chỉ đổi active account sang user. Muốn quay lại SA:
  `gcloud config set account bq-reader-8l@lithe-record-440915-m9.iam.gserviceaccount.com`.

---

## Cách C — Chỉ cho các script dùng PYTHON client (không phủ `bq` CLI)

Nếu chỉ cần các script gọi `from google.cloud import bigquery` ghi được (KHÔNG đủ cho script gọi `bq` CLI):

```bash
# credential dtienthanh đã có sẵn trong project -> đặt làm ADC mặc định:
mkdir -p ~/.config/gcloud
cp /home/trido/thanhdt/WorkingClaude/gcp_credentials.json \
   ~/.config/gcloud/application_default_credentials.json

# cài thư viện vào venv (nếu chưa có):
/home/trido/thanhdt/wc_venv/bin/pip install google-cloud-bigquery
```

> ⚠️ Cách C **không** làm `bq` CLI ghi được (bq vẫn dùng active account của gcloud, không đọc ADC).
> Đa số job daily dùng `bq` CLI → **phải kèm Cách A hoặc B**. Cách C chỉ là bổ sung cho script python client.

---

## § Kiểm tra (chạy sau khi áp dụng Cách A hoặc B) — TRÊN SERVER

```bash
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
PROJ=lithe-record-440915-m9

# danh tính hiện tại:
gcloud config list --format='value(core.account)'
echo 'SELECT SESSION_USER() AS me' | bq query --use_legacy_sql=false --project_id=$PROJ --format=csv

# WRITE probe: tạo bảng tạm rồi xoá (phải KHÔNG còn "Access Denied"):
echo 'CREATE OR REPLACE TABLE tav2_bq._write_probe AS SELECT 1 AS x' \
  | bq query --use_legacy_sql=false --project_id=$PROJ
echo 'SELECT x FROM tav2_bq._write_probe' \
  | bq query --use_legacy_sql=false --project_id=$PROJ --format=csv
echo 'DROP TABLE IF EXISTS tav2_bq._write_probe' \
  | bq query --use_legacy_sql=false --project_id=$PROJ
```

✅ Thành công khi: `CREATE` không báo `Access Denied`, `SELECT` trả `x=1`, `DROP` chạy gọn.
(Với Cách A, `SESSION_USER()` vẫn là SA `bq-reader-8l@...` — đúng, vì nay SA đã có quyền ghi.
Với Cách B, `SESSION_USER()` = `dtienthanh@gmail.com`.)

---

## § Lưu ý vận hành cho job cron trên server

Shell non-interactive **không** có gcloud trên PATH. Trong mọi wrapper `.sh` / cron phải set:

```bash
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export WORKDIR_8L=/home/trido/thanhdt/WorkingClaude
# python của job: /home/trido/thanhdt/wc_venv/bin/python  (đã cài pandas/numpy/bq-lib...)
```

(File `wc_env.sh` ở thư mục project đã set sẵn các biến này — `source` nó trong wrapper.)

---

## § Bảo mật

- `gcp_credentials.json` và `sa-key.json` là **credential thật** — đừng commit lên git public, đừng share ra ngoài.
- Cách A là ít rủi ro nhất cho tự động hoá (không gắn vào tài khoản Google cá nhân, không token user hết hạn).
- Nếu lỡ lộ: thu hồi key SA trong IAM (Service Accounts → Keys) và/hoặc `gcloud auth revoke dtienthanh@gmail.com`.

---

## Phụ lục — Cách A' : tạo service account WRITER riêng (sạch về ngữ nghĩa)

Chạy từ local (owner). Tạo SA mới chỉ để ghi, rồi đưa key lên server:

```bash
PROJ=lithe-record-440915-m9
gcloud iam service-accounts create bq-writer-8l --project=$PROJ \
  --display-name="BQ writer for 8L server jobs"
gcloud projects add-iam-policy-binding $PROJ \
  --member="serviceAccount:bq-writer-8l@$PROJ.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
gcloud projects add-iam-policy-binding $PROJ \
  --member="serviceAccount:bq-writer-8l@$PROJ.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"
gcloud iam service-accounts keys create bq-writer-key.json \
  --iam-account=bq-writer-8l@$PROJ.iam.gserviceaccount.com
# -> copy bq-writer-key.json lên server, rồi TRÊN SERVER:
#   gcloud auth activate-service-account --key-file=/duong/dan/bq-writer-key.json
#   gcloud config set project lithe-record-440915-m9
```

`activate-service-account` nhận file service-account (đã test: server activate được bằng `gcloud auth activate-service-account --key-file=`), nên cách này chạy **không cần browser**.
