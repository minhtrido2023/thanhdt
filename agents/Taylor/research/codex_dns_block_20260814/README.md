# DNS-block 08-13 — KHÔNG phải hạ tầng flaky. Là **chính sách sandbox của codex**, tái hiện được 100%

Job `Taylor_20260814_003518` (Việc 2). Điều tra sơ bộ theo yêu cầu; **không sửa code**.

## Kết luận một dòng

Sự cố 08-13 **không** phải "DNS ra ngoài chết trong cửa sổ 7 phút". Nó là hành vi **tất định** của
sandbox `workspace-write` mà `dispatch.sh` cố ý bật cho provider `codex`: sandbox này **tắt mạng
theo mặc định**. Tái hiện lại được **hôm nay, 2026-08-14**, sau sự cố 1 ngày, bằng A/B một biến.

## Bằng chứng — A/B một biến, chạy thật

| Chân | Lệnh | Kết quả |
|---|---|---|
| **Host** (không sandbox) | `getent hosts openapi.dnse.com.vn` | `103.151.242.24` ✅ |
| **codex `-s workspace-write`** (ĐÚNG argv `dispatch.sh` dùng) | y hệt | `GETENT_FAILED rc=2` — **0ms** ❌ |
| **codex `-s workspace-write` + `-c sandbox_workspace_write.network_access=true`** | y hệt | `103.151.242.24` — 117ms ✅ |

`smtp.gmail.com` phân giải bình thường từ host ⇒ chân SMTP của sự cố #2 cùng một nguyên nhân.

**0ms** là chữ ký của *deny*, không phải *timeout* — resolver bị chặn ngay, không có gì để retry.

`~/.codex/config.toml` **không có** khối `[sandbox_workspace_write]` ⇒ `network_access` nằm ở mặc
định (tắt). Không ai đổi gì trong ngày 08-13; không có gì "hồi phục" lúc 09:21.

## Vì sao "cửa sổ 7 phút" là ảo ảnh quan sát

`logs/` chỉ có **5** log codex, **tất cả** ngày 08-13 09:09→09:21. 3 log đầu chết trước khi chạy
(`No prompt provided via stdin` / prompt rỗng); 2 log còn lại là đúng 2 job trong incident. Tức
**cửa sổ 7 phút đó chính là toàn bộ dân số job codex có chạm mạng** — 2/2 = 100% hỏng, không phải
2 mẫu xui trong một dải rộng.

10 job codex ngày 08-10 (Taylor/Winston, có `provider: codex` trong job record): **0 lỗi mạng** —
nhưng đó là smoke-test, **không chứng minh được là chúng có gọi ra ngoài hay không**. Không tính
là chân đối chứng (§28: vắng mặt trên một kênh ≠ vắng mặt trong thực tế).

## Sự cố ĐÃ được nhìn thấy một nửa từ 08-10, nửa còn lại bị bỏ

Cùng sandbox, cùng lớp lỗi, đã cắn một lần rồi — phần **hệ thống file**:

> `dispatch.sh` §codex: *"workspace-write mặc định chỉ cho ghi workdir + /tmp => KHÔNG ghi nổi
> bus/inbox … Đo thật 2026-08-10: 'Lệnh ghi kết quả lên bus bị chặn: Read-only file system' =>
> job done mà bus TRỐNG, đúng kiểu thất-bại-im-lặng."*

Đã vá bằng `--add-dir "$WC_ROOT"` (user duyệt 08-10, có trình bày đánh đổi). **Phần MẠNG của
đúng sandbox đó chưa ai đụng tới.** Đây là tiền lệ trực tiếp, không phải chuyện mới.

## Phát hiện kèm theo — nghiêm trọng hơn cả DNS

`kb/cli_providers.json`: `codex.allow_agents = ["Taylor","Winston","Wendy","Spyros","Wags"]`.
`claude.notes`: *"Duy nhất được dùng cho surface tiền thật (Mafee/DollarBill)"*.

**Mafee và DollarBill KHÔNG được phép chạy codex** — mà 2 job 08-13 chính là
`Mafee_codex_*` (đặt lệnh TIỀN THẬT) và `DollarBill_codex_*`.

Quét **cả hai tầng lưu trữ** (§17): `bus/jobs/` (724) + `bus/jobs/archive/` (907) = **0** job
record nào có "codex" trong tên, trong khi log `logs/dispatch_<job_id>.log` thì có. Mọi job do
`dispatch.sh` tạo đều có job record. Header log lại đúng argv codex của `dispatch.sh`
(`-C <AGENT_DIR> -s workspace-write --add-dir /home/trido/thanhdt/WorkingClaude`).

⇒ Đọc mạnh nhất: **2 job này chạy vòng qua cổng provider của `dispatch.sh`** (gọi tay `codex exec`
với đúng argv, hoặc qua wrapper), nên `allow_agents` không có cơ hội chặn. **CHƯA xác nhận** —
người biết chắc là Mike/user (ai bấm nút). Ghi ra như giả thuyết có bằng chứng, không phải kết luận.

Nếu đúng: nguyên nhân gốc của sự cố **không phải DNS**. Nó là *một tác vụ tiền thật được định
tuyến sang provider bị cấm cho tác vụ đó*. DNS chỉ là **triệu chứng đã CỨU** ca này — bot fail-safe,
không đặt lệnh mù.

## Trả lời câu hỏi của dispatch: đủ dữ liệu để đề xuất cơ chế phòng ngừa chưa?

**Đủ để KẾT LUẬN, và kết luận là: retry/backoff SAI HƯỚNG — đừng xây.**

Đây không phải lỗi ngẫu nhiên cần thử lại; nó tất định. Retry sẽ đập vào cùng một deny mãi mãi,
và ngày 08-13 nó sẽ ngốn sạch cửa sổ giao dịch để thử lại một thứ không bao giờ thành công. Nguyên
tắc "quan sát tự nhiên trước tự động phục hồi" ở đây cho kết quả còn mạnh hơn dự kiến: **không cần
quan sát thêm, và cũng không cần cơ chế phục hồi nào** — cần một quyết định cấu hình.

Ba lựa chọn, **đều là quyết định CHÍNH SÁCH của user/Mike, tôi KHÔNG tự áp** (§22 tách policy khỏi
technical):

| | Làm gì | Đánh đổi |
|---|---|---|
| **A** | `-c sandbox_workspace_write.network_access=true` trong nhánh codex của `dispatch.sh` | 1 dòng, hết hẳn lớp lỗi này. **Nhưng** codex đã đọc/ghi được `secrets/` + `data/trading_rules.json` (chính `dispatch.sh` ghi rõ 5 chốt chặn của opencode KHÔNG áp cho codex) — thêm mạng ra ngoài = mở bề mặt rò rỉ. Cần user duyệt như lần `--add-dir` 08-10 |
| **B** | Không mở mạng; siết đúng chỗ: đảm bảo tác vụ chạm mạng/tiền thật **không** đi đường codex (đúng `allow_agents` đang khai), và bịt đường vòng qua cổng provider | Trị nguyên nhân gốc thật. Không mở thêm bề mặt nào. Không sửa được ca codex *cần* mạng cho việc R&D hợp lệ |
| **C** | Giữ nguyên | Miễn phí, fail-safe vẫn đúng. Nhưng mỗi lần tái diễn tốn một cửa sổ giao dịch, và **sẽ** tái diễn vì nó tất định |

Khuyến nghị của tôi: **B trước, A sau nếu thật sự cần** — vì sự cố này không phải "codex thiếu
mạng", mà là "việc tiền thật chạy trên codex". Mở mạng cho codex trong khi nó vẫn đọc được
`secrets/` sẽ sửa triệu chứng và làm bề mặt rủi ro rộng ra cùng lúc.

## Cần sửa lại incident file

`kb/incidents/2026-08/2026-08-13-codex-headless-dns-block-tv1-and-smtp.md` hiện ghi root cause là
*"hạ tầng mạng/DNS … bị flaky trong đúng cửa sổ 7 phút"* và *"nếu tái diễn lần 3, đó là bằng chứng
đủ mạnh để đầu tư retry/backoff"*. **Cả hai đều sai** theo số đo ở trên. Để nguyên thì lần sau có
người trích lại nguyên văn — đúng loại lỗi "gán sai nguyên nhân rồi lưu thành tri thức chung" mà
vòng 6 Oshares vừa phải đính chính (ca `vnindex_5state` không hậu tố). Không tự sửa ở đây: file
`kb/` cần Mike duyệt (§13) và tôi đang chạy song song với dispatch khác.

## Tái lập

```bash
getent hosts openapi.dnse.com.vn                     # host: OK
codex exec --skip-git-repo-check -C . -s workspace-write - <<< \
  'Run exactly: getent hosts openapi.dnse.com.vn'    # FAIL rc=2, 0ms
codex exec --skip-git-repo-check -C . -s workspace-write \
  -c sandbox_workspace_write.network_access=true - <<< \
  'Run exactly: getent hosts openapi.dnse.com.vn'    # OK, 117ms
```
