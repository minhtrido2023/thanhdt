# Liên thông đóng-việc chéo topic — phân tích kiến trúc + PROPOSAL

- **Job**: Wags_20260814_041611 (VIỆC B) · **Ngày**: 2026-08-14 · **Trạng thái**: PROPOSAL, chưa implement
- **Phản hồi user (08-14)**: *"Một số việc đã đóng ở topic khác nhưng bên này vẫn nhắc lại, chứng tỏ
  quy trình liên thông nội bộ khá kém. Cần suy nghĩ sâu về kiến trúc … để những việc đã xong đều
  phải được biết trước khi raise những câu hỏi warning vô nghĩa."*
- **Xây tiếp từ** `~/.claude/skills/close-the-loop/SKILL.md` — KHÔNG lặp lại root cause A/B ở đó.

---

## 1. Cái mà skill close-the-loop CHƯA phủ

Skill đã phủ 2 hình dạng:
- **A** — người sửa xong nhưng KHÔNG đăng event đóng.
- **B** — chính checker tra cứu sai (exact-match trên topic có free text), và "không tra ra" bị gộp
  chung code path với "đã tra và bác".

Cả hai đơn thuốc của skill — *"đăng closer trên ĐÚNG topic string của question"*, *"match theo
prefix hoặc theo ID"* — đều **giả định rằng topic string mang danh tính của VẤN ĐỀ**. Trong fleet
này giả định đó sai về mặt cấu trúc. Đó là hình dạng thứ ba.

## 2. Root cause D — danh tính dùng để theo dõi đóng-việc là MỐC THỜI GIAN QUAN SÁT, không phải KHOÁ VẤN ĐỀ

Chuỗi thật, đọc được từ code:

```
bin/ops_health_check.sh:900   wags_autofix.sh "coord-${TODAY}" "$COORD_WARN"
bin/wags_autofix.sh:251       append_event.sh Wags question "wags-fix-not-confirmed: $LABEL"
                              ⇒ topic = "wags-fix-not-confirmed: coord-2026-08-07"
```

`$LABEL` = **ngày chạy checker**. Hệ quả suy ra được bằng máy, không cần phỏng đoán:

1. **Một root cause bị nhận ra ở 2 ngày ⇒ 2 danh tính khác nhau.** Prefix-matching (đơn thuốc B#1
   của skill) KHÔNG cứu được: `coord-2026-08-07` và `coord-2026-08-10` chung prefix `coord-2026-08-`,
   nhưng đó là prefix của NGÀY — match theo nó thì gộp mọi sự cố điều phối từng có.
2. **Danh tính bất ổn đúng ở chiều cần ổn định, và ổn định đúng ở chiều cần phân biệt.** Hai vấn đề
   không liên quan trong cùng một ngày ⇒ CHUNG một topic (đụng độ). Một vấn đề kéo qua hai ngày ⇒
   HAI topic (phân mảnh). Sai cả hai hướng cùng lúc.
3. **Làm ĐÚNG kỷ luật của skill vẫn không thoát.** "Đóng trên đúng topic gốc" nghĩa là đóng
   `coord-2026-08-07` — một chuỗi không nói gì về root cause, nên không thể thông tin cho checker
   ngày mai.

⇒ **Đây không phải A cũng không phải B.** Kỷ luật hoàn hảo + matcher hoàn hảo vẫn sinh ra đúng
triệu chứng user mô tả. Gọi là **root cause D: danh tính sai đối tượng**.

## 3. Root cause E — closure bị nộp vào SAI LOẠI ĐỐI TƯỢNG (vòng review là SỰ KIỆN, không phải TRẠNG THÁI)

`wags-fix-not-confirmed: coord-<ngày>` **không** mang nghĩa "vấn đề P đang mở". Nó mang nghĩa
"**vòng review R** trả verdict NEEDS_CHANGES". Một vòng review là sự kiện đã xảy ra — nó không bao
giờ có thể "được giải quyết", chỉ có thể **bị thay thế** bởi vòng R+1.

Nhưng bus mô hình hoá nó là `question` chờ `answer`. Không có khái niệm **supersession**. Vì vậy nó
treo vĩnh viễn trừ khi có người thủ công đăng closer — và không ai kỳ vọng bản fix vòng R+1 sẽ đóng
vòng R, vì hai bên khác topic. **Đó chính xác là lý do cả 4 vòng cùng treo** (7d/6d/3d/3d).

## 4. Bằng chứng đo được: fleet đã có 3 matcher "đã đóng chưa?", và chúng KHÔNG khớp nhau

| Matcher | Cửa sổ | Thuật toán |
|---|---|---|
| `ops_health_check.sh` check #5 `_resolved()` | **48h** | substring + `r_ts >= q_ts` |
| `bus_question_audit.py` | **không giới hạn** | port cùng thuật toán (cố ý) |
| check #5 khối HINT | 48h | prefix ≥16 ký tự **HOẶC** chung "từ hiếm" (df≤15) trong 48h |
| ~~`check_report_cadence.sh`~~ | — | *matcher THỨ 4, đã xoá ở commit 2ce53d7a — chính là finding NEEDS_CHANGES coord-08-10* |

Đo thật hôm nay (2026-08-14):

```
ops_health_check §5  (cửa sổ 48h) : 1 pending question
bus_question_audit.py (toàn bộ)   : 24 pending question
```

Chênh 1 vs 24 là **do thiết kế** (§5 còn nhánh `aged_q` WARN-ONLY in riêng phần >48h), nhưng nó cho
thấy: nguồn sự thật "còn treo cái gì" phụ thuộc vào **hỏi ai**.

**Con số quan trọng nhất — khối HINT tự ghi lại kết quả đo của chính nó** (`ops_health_check.sh:496-503`):

> *"token-overlap TRẦN (không lọc) gợi ý **61/63** câu hỏi = vô nghĩa … + cửa sổ 48h + stoplist →
> còn **9 gợi ý, ~5 đúng thật**"*

**~55% precision sau khi tinh chỉnh bằng tay 3 tham số** (`STEM_MIN`/`DF_MAX`/`WIN_H`) + một
stoplist tiếng Việt gõ tay. Đây là bằng chứng cứng: **so khớp chuỗi tự do không giải được bài toán
này**. Mọi lần thử tới nay đều rơi vào một trong hai: nhiễu (61/63) hoặc im lặng (matcher exact).

---

## 5. Đánh giá 3 phương án user/Mike nêu

### (a) `closes_topics: [...]` — CẦN, nhưng KHÔNG ĐỦ, và nguy hiểm nếu đứng một mình
Đòi người đóng phải **nhớ được MỌI topic lịch sử cùng root cause** — tức đẩy một bài toán *recall*
sang agent không có cách rẻ nào để liệt kê (phải đọc cả lịch sử bus). Thực tế agent sẽ liệt kê topic
trước mặt và bỏ sót cái 7 ngày trước — **đúng cái đã xảy ra**. Tệ hơn: thiếu một mục thì **không ai
thấy** (fail silent).
⇒ **Giữ, nhưng như một override thủ công ĐẶT TRÊN một cơ chế, không phải LÀ cơ chế.**

### (b) Vòng coord hằng ngày phải tra `coord-<ngày trước>` còn treo — ĐÚNG HƯỚNG, còn yếu
Rẻ và đúng trực giác, nhưng: chỉ vá họ `coord-`, và **tái lập bài toán nhiễu** — "ưu tiên xử lý
trước" mà không có danh tính nghĩa là agent phải ĐỌC và PHÁN ĐOÁN lại cùng mấy mục đó mỗi ngày. Nó
không chặn phân mảnh, chỉ bắt người đi bộ qua các mảnh vỡ.
⇒ **Nhận dạng mạnh hơn: không phải "tra rồi ưu tiên" mà "vòng mới trên CÙNG problem_key TỰ ĐỘNG
thay thế vòng cũ".** Khi đó việc đi bộ là cơ học, không phải phán đoán.

### (c) ĐỀ XUẤT — `problem_key` + supersession, `closes_topics` là escape hatch

**C1 — `problem_key`: danh tính bền, do agent khai, TÁCH khỏi topic.**
Thêm field tuỳ chọn `problem_key` **trong payload JSON** (⚠️ ràng buộc thật: `append_event.sh:33`
chặn cứng >5 tham số vị trí để bắt lỗi word-split ⇒ KHÔNG được thêm arg vị trí thứ 6).
Là slug của **KHIẾM KHUYẾT**, không phải của DỊP: `preflight-silent-fail`,
`report-cadence-closer-mismatch`, `send-plan-report-gate-silent-fail-open`.
Topic giữ nguyên free text cho người đọc — không ai phải từ bỏ nó.
Phép đóng thành: **cùng `problem_key` + có `answer`/`decision` sau đó ⇒ ĐÓNG, bất kể topic string.**

Đây chính là đơn thuốc B#1 của skill (*"match theo ID không phụ thuộc định dạng chuỗi"*) nâng lên
một tầng: skill áp cho **một** question; lỗ hổng là **không có ID nào bắc qua các VÒNG**.

Điểm sống-chết: `problem_key` phải **rẻ để tái dùng và khó gõ sai**, nếu không nó thoái hoá thành
free-text thứ hai với đúng bài toán phân mảnh. ⇒ registry (`kb/problem_keys.md`) + validate ngay
tại `append_event.sh`: key lạ ⇒ **die() ỒN ÀO kèm danh sách near-match**, không im lặng nhận.
(Đúng chỗ đó đã là biên giới validate — bản vá word-split 2026-08-13.)

**C2 — Supersession cho vòng review.**
`wags-fix-not-confirmed: <label>` **không nên là `question`** — nó là verdict của một vòng. Mô hình
đúng: vòng R+1 đăng verdict trên cùng `problem_key` ⇒ question vòng R tự đóng với
`superseded_by: <trace_id mới>`. Diệt cả lớp mà không agent nào phải nhớ gì.
Nếu KHÔNG bao giờ có vòng R+1 ⇒ question ĐÚNG là vẫn mở — hành vi hiện tại cho vấn đề bị bỏ rơi
thật, và đó là điều ta muốn giữ.

**C3 — Phép kiểm "đã xong ở nơi khác" của checker phải dựa ARTIFACT, không dựa chuỗi.**
Skill đã nói checker nên đối chiếu artifact rẻ trước khi escalate. Áp vào đây: trước khi phát lại,
hỏi *"có commit nào chạm các file trong `files_changed` của finding này, sau mốc question, message
tham chiếu problem_key không?"*
`files_changed` **ĐÃ TỒN TẠI** — prompt dispatch của `wags_autofix.sh:158` bắt buộc khai. Hiện chỉ
dùng để quyết định có cần arch-review đầy đủ hay không. Tái dùng làm bằng chứng đóng gần như miễn phí.
⚠️ **Caveat đo được: chỉ 35/56 (63%) finding `wags-fix:` thực sự có `files_changed`** ⇒ C3 phủ ~2/3
số ca cho tới khi field này được ép cứng. Phải fail về phía KHÔNG đóng khi thiếu field.

**C4 — Bỏ heuristic HINT từ-hiếm SAU KHI C1/C3 chạy ổn.**
55% precision, WARN-ONLY, và chính comment của nó ghi lại một bài tinh chỉnh sẽ phải làm lại mỗi lần
từ vựng fleet đổi. Để một heuristic precision thấp NẰM CẠNH một cơ chế đáng tin sẽ dạy người đọc bỏ
qua cả hai. ⚠️ Đây là **xoá code** ⇒ cần arch-reviewer duyệt riêng, và giữ ít nhất 1 tuần sau C1.

**KHÔNG làm:** match ngữ nghĩa/LLM giữa các topic. Tái tạo bài toán precision với khả năng debug tệ
hơn và chi phí mỗi lần chạy, trong một script cron.

---

## 6. Thứ tự triển khai + blast radius

| Bước | Rủi ro | Hướng fail-safe |
|---|---|---|
| **C1** problem_key + registry + validate | THẤP — field tuỳ chọn, additive; event cũ không đổi | chỉ die() khi field CÓ MẶT mà key lạ |
| **C3** checker đối chiếu artifact | THẤP — read-only | lookup lỗi/thiếu `files_changed` ⇒ **KHÔNG đóng** (giữ ồn) |
| **C2** supersession | **CAO NHẤT** — đổi thứ `wags_autofix` phát ra, chạm `WAGS_SELF_Q_PREFIXES` | làm CUỐI; pin bằng selfcheck ca 10/11 đã có |
| **C4** xoá HINT | trung bình (xoá code) | sau C1 ≥1 tuần, arch-review riêng |

⚠️ `WAGS_SELF_Q_PREFIXES` đã gây **một regression thật** (2026-08-12: tách nhánh
`wags-arch-review-inconclusive:` mà quên cập nhật danh sách ⇒ vòng lặp tự nuôi). C2 chạm đúng chỗ đó.

## 7. Cần NGƯỜI quyết (không tự làm)

**C1 đặt ra một quy ước TOÀN FLEET mà mọi agent phải theo** — đó là thay đổi mức `MIKE.md`, không
phải một bản vá tooling của Wags. Vì vậy tài liệu này dừng ở PROPOSAL.

Câu hỏi cho Mike/user:
1. Duyệt `problem_key` làm quy ước bus toàn fleet không? (nếu không → chỉ còn (b) yếu + `closes_topics` thủ công)
2. Có ép `files_changed` thành **bắt buộc** cho mọi finding `wags-fix:` không? (nâng phủ C3 từ 63% → 100%)
3. C2 (supersession) đổi hành vi escalation của chính pipeline autofix — làm ngay sau C1, hay chờ C1 chạy 1 tuần lấy dữ liệu?
