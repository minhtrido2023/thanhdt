#!/usr/bin/env python3
"""append_event_selfcheck.py — khoá hồi quy cho BIÊN GIỚI GHI BUS (bin/append_event.sh).

Vì sao tồn tại: append_event.sh là đường ghi bus DUY NHẤT của fleet (~42 call site) và
28/42 call site bọc `2>/dev/null || true`, nên mọi thay đổi hành vi ở đây đều có thể biến
"ghi event hỏng" thành "vứt hẳn event" mà không ai thấy. Ba chốt fail-loud thêm ngày
2026-08-13 (chống payload bị shell word-split) ĐÃ ĐƯỢC arch-review chấm NEEDS_CHANGES đúng
vì KHÔNG có selfcheck nào được commit cùng — file này trả nốt required_change #3 đó, và
khoá luôn required_change #2 (siết hình dạng trace_id) áp ngày 2026-08-16.

Chạy THẬT script production trên 1 cây bus sandbox (tmpdir + symlink bin/mike_json.py +
kb/version.txt), không mock — cùng khuôn extract-and-test với ops_health_check_selfcheck.py.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "bin", "append_event.sh")

_fails = []


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))
        _fails.append(name)


def mksandbox():
    """Cây bus giả: append_event.sh tính ROOT từ vị trí CHÍNH NÓ nên phải copy script vào
    sandbox, kèm mike_json.py + kb/version.txt thật."""
    d = tempfile.mkdtemp(prefix="append_event_selfcheck_")
    os.makedirs(os.path.join(d, "bin"), exist_ok=True)
    os.makedirs(os.path.join(d, "kb"), exist_ok=True)
    shutil.copy2(SCRIPT, os.path.join(d, "bin", "append_event.sh"))
    shutil.copy2(os.path.join(ROOT, "bin", "mike_json.py"),
                 os.path.join(d, "bin", "mike_json.py"))
    # json_payload_diag.py: phụ thuộc MỚI của append_event.sh (2026-09-25). Không copy thì sandbox
    # đo một script KHÁC với production — và chính cái thiếu này đã làm mọi ca payload JSON
    # HỢP LỆ bị từ chối (weekly-ops-audit 2026-09-26).
    shutil.copy2(os.path.join(ROOT, "bin", "json_payload_diag.py"),
                 os.path.join(d, "bin", "json_payload_diag.py"))
    # finding_measured_by.py: helper của cổng cảnh báo measured_by (2026-10-13). Cùng lý do —
    # thiếu nó thì sandbox đo nhánh fail-open chứ không đo đường production.
    shutil.copy2(os.path.join(ROOT, "bin", "finding_measured_by.py"),
                 os.path.join(d, "bin", "finding_measured_by.py"))
    with open(os.path.join(d, "kb", "version.txt"), "w", encoding="utf-8") as f:
        f.write("1\n")
    return d


def run(sandbox, args, env_extra=None, cwd=None):
    env = dict(os.environ)
    env.pop("JOB_ID", None)          # nếu không, fallback $JOB_ID che mất ca "không trace_id"
    env.update(env_extra or {})
    # errors="surrogateescape": ca byte-hỏng truyền argv chứa byte không hợp lệ, và
    # append_event.sh in lại dòng event ra stdout ⇒ subprocess giải mã STRICT sẽ nổ
    # UnicodeDecodeError ngay trong communicate(), TRƯỚC khi tới bất kỳ assertion nào —
    # tức harness chết vì lý do không liên quan tới thứ đang đo. Không nới lỏng gì:
    # assertion đọc lại BYTE của file bus, không đọc stdout này.
    p = subprocess.run([os.path.join(sandbox, "bin", "append_event.sh")] + args,
                       capture_output=True, text=True, errors="surrogateescape",
                       env=env, cwd=cwd)
    return p.returncode, p.stdout, p.stderr


def rejected(sandbox):
    # bus/, KHÔNG phải bus/inbox/ (đổi 2026-08-16): reader nào cũng glob inbox/*.jsonl mà
    # không lọc tên ⇒ đặt trong inbox thì consolidate.sh nuốt bản ghi cách ly (cursor nhảy,
    # bằng chứng mất) và render `?/? — : null` vào KB. Đã đo, không phải suy đoán.
    path = os.path.join(sandbox, "bus", "_rejected.jsonl")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def events(sandbox, agent):
    path = os.path.join(sandbox, "bus", "inbox", f"{agent}.jsonl")
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


# ── 1. Đường HỢP LỆ: 4 dạng payload/trace_id phải ghi được, không được siết oan.
def case_valid_paths():
    d = mksandbox()
    try:
        ok = [
            (["W", "finding", "t-json", '{"a":1}'], "payload JSON object, không trace_id"),
            (["W", "status", "t-list", '[1,2]'], "payload JSON array"),
            (["W", "status", "t-str", "chuoi thuong khong phai JSON"], "payload chuỗi thường"),
            (["W", "heartbeat", "t-trace", '{"a":1}', "Wags_20260816_090511"],
             "trace_id đúng hình dạng <Agent>_<YYYYMMDD>_<HHMMSS>"),
        ]
        for args, label in ok:
            rc, out, err = run(d, args)
            check(f"hợp lệ: {label} ⇒ exit 0", rc == 0, f"rc={rc} err={err.strip()[:200]}")
        evs = events(d, "W")
        check("hợp lệ: ghi đủ 4 event", len(evs) == 4, f"chỉ có {len(evs)}")
        check("hợp lệ: payload JSON được giữ nguyên KIỂU (dict, không phải chuỗi)",
              isinstance(evs[0].get("payload"), dict), repr(evs[0].get("payload"))[:200])
        check("hợp lệ: trace_id đúng dạng được ghi nguyên vẹn",
              evs[3].get("trace_id") == "Wags_20260816_090511", repr(evs[3].get("trace_id")))
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── 2. $# > 5: chữ ký kinh điển của payload bị shell word-split (13 event/6 agent, 2026-07/08).
def case_too_many_args():
    d = mksandbox()
    try:
        rc, out, err = run(d, ["W", "finding", "t", '{"a":1}', "Wags_20260816_090511", "thua"])
        check("word-split: >5 tham số ⇒ exit != 0", rc != 0, f"rc={rc}")
        check("word-split: >5 tham số ⇒ nói rõ nghi word-split", "word-split" in err, err[:200])
        check("word-split: >5 tham số ⇒ KHÔNG ghi event nào (không để lại rác)",
              events(d, "W") == [], events(d, "W"))
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── 3. JSON cụt: payload mở đầu bằng { hoặc [ mà không parse được = bị cắt, KHÔNG phải chuỗi.
def case_truncated_json_payload():
    d = mksandbox()
    try:
        rc, out, err = run(d, ["W", "question", "t", '{"question":"abc'])
        check("JSON cụt: exit != 0", rc != 0, f"rc={rc}")
        check("JSON cụt: KHÔNG rơi về fallback 'ghi như chuỗi'", events(d, "W") == [],
              events(d, "W"))
        # Chuỗi thường KHÔNG mở đầu bằng {/[ vẫn phải đi lọt — nếu không, siết quá tay.
        rc2, _, _ = run(d, ["W", "status", "t2", "khong phai json ma co { o giua"])
        check("JSON cụt CONTROL: chuỗi thường có '{' ở GIỮA vẫn ghi được", rc2 == 0, f"rc={rc2}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── 3b. JSON hỏng nhưng KHÔNG cụt: thông điệp phải nói ĐÚNG nguyên nhân, không đoán "cắt cụt".
#    Ca thật: Taylor 2026-08-28T01:48:25Z — payload đủ, đóng đúng, thừa 1 dấu '}' giữa chừng
#    ⇒ "Extra data". Thông điệp cũ khẳng định "nhiều khả năng bị cắt cụt" và checker §5b chép
#    nguyên văn vào dispatch ops-autofix, dẫn người xử lý đi sai hướng.
def case_json_error_message_names_real_cause():
    d = mksandbox()
    try:
        extra = '{"a":{"b":1}},"c":"2"}'          # thừa '}' — KHÔNG cụt
        rc, out, err = run(d, ["W", "finding", "t3", extra])
        check("JSON thừa ngoặc: exit != 0", rc != 0, f"rc={rc}")
        check("JSON thừa ngoặc: thông điệp in lỗi parser thật ('Extra data')",
              "Extra data" in err, err)
        check("JSON thừa ngoặc: KHÔNG khẳng định 'cắt cụt' cho ca không hề cụt",
              "nhiều khả năng bị cắt cụt" not in err, err)
        check("JSON thừa ngoặc: vẫn được cách ly nguyên văn",
              any(r["argv"][3] == extra for r in rejected(d)), rejected(d))

        cut = '{"question":"abc'                   # cụt thật
        rc2, _, err2 = run(d, ["W", "question", "t4", cut])
        check("JSON cụt: exit != 0", rc2 != 0, f"rc={rc2}")
        check("JSON cụt: thông điệp in lỗi parser thật (Unterminated/Expecting)",
              ("Unterminated" in err2 or "Expecting" in err2), err2)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── 4. trace_id SAI HÌNH DẠNG (arch-review coord-2026-08-13 required_change #2).
#    Bản whitelist-ký-tự cũ để LỌT 7/8 giá trị rác trong chính danh sách sự cố của nó.
def case_trace_id_shape():
    d = mksandbox()
    try:
        # Đúng các giá trị rác THẬT đã nằm trên bus (không phải ca tổng hợp cho dễ đậu).
        for bad in ("nguoi", "du", "capacity", "khoan", "lai", "con", "hom", "thêm",
                    "734cbac0977a5183f305ac1a66c5d99d1ff78aef"):
            rc, out, err = run(d, ["W", "finding", "t", '{"a":1}', bad])
            check(f"trace_id rác {bad!r} ⇒ bị chặn (exit != 0)", rc != 0, f"rc={rc}")
        rc, out, err = run(d, ["W", "finding", "t", '{"a":1}',
                               "mot chuoi dai co khoang trang"])
        check("trace_id có khoảng trắng ⇒ bị chặn, thông điệp nói word-split",
              rc != 0 and "word-split" in err, f"rc={rc} err={err[:200]}")
        check("trace_id rác ⇒ KHÔNG ghi event nào", events(d, "W") == [], events(d, "W"))
        # CONTROL 2 chiều: các dạng HỢP LỆ khác nhau không được chặn oan.
        for good in ("Wags_20260816_090511", "arch-reviewer_20260816_090511",
                     "quant.skeptic_20260101_000000"):
            rc, out, err = run(d, ["W", "finding", "t", '{"a":1}', good])
            check(f"trace_id hợp lệ {good!r} ⇒ KHÔNG bị chặn oan", rc == 0,
                  f"rc={rc} err={err[:200]}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── 5. $JOB_ID fallback: agent chạy trong dispatch chỉ truyền 4 arg vẫn phải được trace.
def case_job_id_fallback():
    d = mksandbox()
    try:
        rc, _, err = run(d, ["W", "finding", "t", '{"a":1}'],
                         {"JOB_ID": "Wags_20260816_090511"})
        evs = events(d, "W")
        check("JOB_ID fallback: 4 arg trong dispatch vẫn có trace_id",
              rc == 0 and evs and evs[0].get("trace_id") == "Wags_20260816_090511",
              f"rc={rc} evs={evs}")
        # JOB_ID rác cũng phải bị chặn — nếu không, đường fallback thành lỗ hổng vòng qua chốt.
        d2 = mksandbox()
        try:
            rc2, _, err2 = run(d2, ["W", "finding", "t", '{"a":1}'], {"JOB_ID": "capacity"})
            check("JOB_ID fallback: JOB_ID rác cũng bị chặn (không vòng qua chốt)",
                  rc2 != 0, f"rc={rc2}")
        finally:
            shutil.rmtree(d2, ignore_errors=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── 6. Ca THẬT đã cắn: verify_finding.sh propagate trace_id nhiễm độc từ bus append-only.
#    Chốt shape ở append_event.sh là FATAL ⇒ caller sạch phải TỰ LÀM SẠCH trước khi gọi,
#    nếu không một verdict hợp lệ bị giết sau khi đã đốt nguyên 1 lượt reviewer headless.
def case_verify_finding_sanitizes_inherited_trace_id():
    # HAI call site propagate trace_id từ bus append-only. Cả hai phải làm sạch — và chúng
    # hỏng theo hai kiểu KHÁC nhau: verify_finding.sh chạy dưới `set -e` không guard ⇒ ABORT
    # cả run_and_record; wags_autofix.sh bọc `|| true` ⇒ verdict arch-review BIẾN MẤT IM LẶNG
    # rồi pipeline đẻ `wags-arch-review-inconclusive` giả.
    for fname, var, call_marker in (
            ("verify_finding.sh", "finding_trace_id", 'verification "VERIFY:'),
            ("wags_autofix.sh", "trace_id", 'verification "ARCH-REVIEW:')):
        src = open(os.path.join(ROOT, "bin", fname), encoding="utf-8").read()
        _i, _j = src.find(f'{var}=""'), src.find(call_marker)
        check(f"{fname}: có làm sạch trace_id kế thừa trước khi gọi append_event.sh",
              _i >= 0 and "SAI HÌNH DẠNG" in src, "không tìm thấy khối sanitize")
        check(f"{fname}: khối sanitize nằm TRƯỚC lời gọi append_event.sh ghi verdict",
              _i >= 0 and _j >= 0 and _i < _j,
              f"sanitize@{_i} vs call@{_j} — thiếu khối hoặc nằm sau lời gọi ⇒ vô tác dụng")
    # Replay bằng CHÍNH biểu thức shell của call site: trace_id rác ⇒ bị hạ về rỗng.
    probe = (
        'finding_trace_id="thêm"\n'
        "if [ -n \"$finding_trace_id\" ] && ! printf '%s' \"$finding_trace_id\" "
        "| grep -qE '^[A-Za-z0-9_.:-]+_[0-9]{8}_[0-9]{6}$'; then finding_trace_id=\"\"; fi\n"
        'printf "[%s]" "$finding_trace_id"\n')
    p = subprocess.run(["bash", "-c", probe], capture_output=True, text=True)
    check("verify_finding.sh: replay biểu thức thật ⇒ trace_id nhiễm độc bị hạ về rỗng",
          p.stdout.strip() == "[]", repr(p.stdout))


# ── 7. CÁCH LY: 28/42 call site gọi kèm `2>/dev/null || true` ⇒ fail-loud bị vứt sạch.
# Bằng chứng phải sống sót ngay cả khi KHÔNG AI đọc stderr (arch-review coord-2026-08-13 #4).
def case_quarantine_survives_discarded_stderr():
    d = mksandbox()
    # stderr bị vứt hoàn toàn — đúng cách 28 call site đang gọi
    rc, _, _ = run(d, ["W", "status", "chu-de", '{"a":1}', "nguoi"], cwd=d)
    check("cách ly: arg bị chặn vẫn exit != 0", rc != 0, f"rc={rc}")
    recs = rejected(d)
    check("cách ly: có ĐÚNG 1 bản ghi trong bus/_rejected.jsonl", len(recs) == 1, recs)
    # Hàng đợi cách ly PHẢI đứng ngoài glob bus/inbox/*.jsonl — nếu ai đó dời nó về lại
    # inbox/, consolidate.sh sẽ ăn bản ghi và chính bằng chứng biến mất (đo 2026-08-16).
    check("cách ly: KHÔNG có file nào lọt vào bus/inbox/ (glob của mọi reader)",
          not os.path.exists(os.path.join(d, "bus", "inbox", "_rejected.jsonl")),
          sorted(os.listdir(os.path.join(d, "bus", "inbox")))
          if os.path.isdir(os.path.join(d, "bus", "inbox")) else "<no inbox>")
    if recs:
        r = recs[0]
        check("cách ly: argv gốc được giữ NGUYÊN VĂN (đủ 5, không phải từ của thông điệp lỗi)",
              r.get("argv") == ["W", "status", "chu-de", '{"a":1}', "nguoi"], r.get("argv"))
        check("cách ly: ghi lại LÝ DO bị chặn", "trace_id" in r.get("reason", ""),
              r.get("reason", "")[:120])
        check("cách ly: có mốc thời gian UTC", str(r.get("ts", "")).endswith("Z"), r.get("ts"))
    check("cách ly: event hỏng KHÔNG lọt vào inbox thật", events(d, "W") == [], events(d, "W"))

    # >5 arg cũng phải được cách ly, và phải giữ ĐỦ cả arg thừa
    run(d, ["W", "status", "t2", '{"a":1}', "W_20260101_000000", "thua"], cwd=d)
    recs = rejected(d)
    check("cách ly: ca >5 tham số cũng được lưu", len(recs) == 2, len(recs))
    if len(recs) == 2:
        check("cách ly: giữ đủ cả tham số THỪA (bằng chứng word-split)",
              recs[1].get("argv", [])[-1] == "thua", recs[1].get("argv"))

    # HỒI QUY `-c`: `python3 -c CODE a b` ⇒ sys.argv[0] == '-c'. Bản đầu dùng sys.argv[0]
    # làm đường dẫn ⇒ ghi vào file tên `-c` ở cwd, hàng đợi rỗng vĩnh viễn, `|| true` nuốt hết.
    check("cách ly: KHÔNG tạo file rác tên '-c' ở cwd (hồi quy sys.argv[0])",
          not os.path.exists(os.path.join(d, "-c")), "có file -c trong sandbox")

    # ĐỐI CHỨNG: đường hợp lệ tuyệt đối không được sinh bản ghi cách ly
    rc, _, _ = run(d, ["W", "status", "ok", '{"a":1}', "W_20260101_000000"], cwd=d)
    check("cách ly ĐỐI CHỨNG: call hợp lệ ⇒ exit 0", rc == 0, f"rc={rc}")
    check("cách ly ĐỐI CHỨNG: call hợp lệ KHÔNG thêm bản ghi cách ly", len(rejected(d)) == 2,
          len(rejected(d)))
    shutil.rmtree(d, ignore_errors=True)


def case_byte_hong_khong_dau_doc_duoc_bus():
    """Khoá hồi quy cho mike_json.py::_utf8_safe (arch-review round 2, coord-2026-08-16).

    bus/inbox/*.jsonl là APPEND-ONLY: một dòng byte hỏng nằm đó VĨNH VIỄN, và load_jsonl —
    reader dùng chung của MỌI consumer (ops_health_check §5, wags_autofix bước 1.5,
    consolidate, trace) — ném UnicodeDecodeError cho cả file, tức câm luôn kênh escalation.
    Byte hỏng vào được vì caller cắt chuỗi bằng `cut -c`/`head -c` dưới LANG="C" (đếm BYTE)
    giữa một ký tự tiếng Việt 3 byte; Python đọc argv bằng surrogateescape nên nó đi lọt tới
    tận json.dumps và ghi ra rc=0. Chốt thật nằm ở CHOKEPOINT cmd_event, nên phải test qua
    chính append_event.sh chứ không gọi hàm trực tiếp.

    Ca này RED trên c528aa7e^ (tái lập: UnicodeDecodeError @142-143) và GREEN từ c528aa7e.
    """
    d = mksandbox()
    # b"k\xe1\xba" = 'k' + 2/3 byte đầu của một ký tự tiếng Việt bị cắt cụt — đúng thứ
    # `cut -c1-300` sinh ra. surrogateescape biến nó thành '\udce1\udcba' trong argv.
    topic = "chu-de-" + b"k\xe1\xba".decode("utf-8", errors="surrogateescape")
    payload = json.dumps({"err_tail": "loi " + b"th\xe1\xbb".decode("utf-8",
                                                                   errors="surrogateescape")},
                         ensure_ascii=False)
    rc, _, err = run(d, ["W", "status", topic, payload, "W_20260101_000000"], cwd=d)
    check("byte hỏng: append_event.sh vẫn exit 0 (không chặn — chốt là làm SẠCH, không từ chối)",
          rc == 0, f"rc={rc} err={err[-200:]}")

    bus = os.path.join(d, "bus", "inbox", "W.jsonl")
    raw = open(bus, "rb").read() if os.path.exists(bus) else b""
    try:
        raw.decode("utf-8")
        utf8_ok = True
    except UnicodeDecodeError as e:
        utf8_ok = False
        err = str(e)
    check("byte hỏng: dòng ghi ra bus là UTF-8 HỢP LỆ (đọc strict được)", utf8_ok,
          err if not utf8_ok else "")

    # Đọc lại bằng CHÍNH load_jsonl production — nếu nó chết thì mọi consumer cũng chết.
    probe = (f"import sys; sys.path.insert(0, {os.path.join(ROOT, 'bin')!r}); "
             f"import mike_json; print(len(mike_json.load_jsonl([{bus!r}])))")
    p = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True)
    check("byte hỏng: load_jsonl production đọc lại được (rc=0, không UnicodeDecodeError)",
          p.returncode == 0 and p.stdout.strip() == "1",
          f"rc={p.returncode} out={p.stdout.strip()} err={p.stderr.strip()[-250:]}")

    # ĐỐI CHỨNG: tiếng Việt/emoji HỢP LỆ phải giữ NGUYÊN XI, không bị _utf8_safe làm hỏng.
    d2 = mksandbox()
    good = "kết thúc bất thường 🔴 — hết hạn"
    rc2, _, _ = run(d2, ["W", "status", good, json.dumps({"n": [1, 2, {"k": "ế"}]},
                                                         ensure_ascii=False),
                         "W_20260101_000000"], cwd=d2)
    ev = json.loads(open(os.path.join(d2, "bus", "inbox", "W.jsonl"),
                         encoding="utf-8").readline())
    check("ĐỐI CHỨNG: dữ liệu hợp lệ (tiếng Việt + emoji + payload lồng) giữ NGUYÊN XI",
          rc2 == 0 and ev.get("topic") == good and ev.get("payload", {}).get("n", [])[2]
          == {"k": "ế"}, f"rc={rc2} topic={ev.get('topic')!r} payload={ev.get('payload')!r}")
    shutil.rmtree(d, ignore_errors=True)
    shutil.rmtree(d2, ignore_errors=True)


def case_quarantine_ghi_duoc_arg_byte_hong():
    """Arch-review round 3, killer objection: hàng đợi PHÁP Y tự chết đúng ở lớp lỗi nó bắt.

    `_quarantine()` ghi bằng open(encoding="utf-8") STRICT + json.dumps(ensure_ascii=False),
    trong khi arg vào qua surrogateescape ⇒ UnicodeEncodeError "surrogates not allowed" ngay
    tại f.write, bị `2>/dev/null || true` nuốt sạch. Kết quả: bus/_rejected.jsonl 0 BYTE,
    stderr vẫn khẳng định "arg bị chặn đã lưu vào ...", và §5b (người đọc) im lặng tuyệt đối
    vì không có bản ghi nào — BÁO YÊN GIẢ. 28/42 call site vứt stderr nên không còn dấu vết.

    Đây đúng ca hàng đợi TỒN TẠI để bắt (payload bị cắt giữa ký tự dưới LANG=C), nên nó phải
    là ca được test kỹ nhất, không phải ca duy nhất không được test.
    RED trên bản ensure_ascii=False (đã tái lập: file 0 byte).
    """
    d = mksandbox()
    # payload mở đầu bằng '{' nhưng cắt cụt giữa ký tự tiếng Việt 3 byte ⇒ die() gọi
    # _quarantine với ĐÚNG loại arg gây lỗi.
    bad = '{"a":"loi ' + b"th\xe1\xbb".decode("utf-8", errors="surrogateescape")
    rc, _, _ = run(d, ["W", "status", "chu-de", bad, "W_20260101_000000"],
                   env_extra={"LANG": "C", "LC_ALL": "C"}, cwd=d)
    check("payload cắt cụt vẫn bị CHẶN (rc=1) — chốt cũ không được nới", rc == 1, f"rc={rc}")

    qf = os.path.join(d, "bus", "_rejected.jsonl")
    size = os.path.getsize(qf) if os.path.exists(qf) else 0
    check("arg byte-hỏng PHẢI thật sự vào được hàng đợi cách ly (file khác 0 byte)",
          size > 0, f"size={size} — stderr hứa đã lưu nhưng file rỗng = báo yên giả")

    recs = [l for l in open(qf, encoding="utf-8").read().splitlines() if l.strip()] \
        if size else []
    check("đúng 1 bản ghi, và đọc lại được bằng json.loads (không surrogate lọt ra file)",
          len(recs) == 1 and isinstance(json.loads(recs[0]), dict) if recs else False,
          f"n={len(recs)}")
    check("bản ghi giữ được arg gốc để làm pháp y (argv có mặt, argc đúng)",
          bool(recs) and json.loads(recs[0]).get("argc") == 5
          and len(json.loads(recs[0]).get("argv") or []) == 5,
          recs[0][:200] if recs else "")
    shutil.rmtree(d, ignore_errors=True)

# ── 10. Cổng `measured_by` cho finding: CHỈ CẢNH BÁO ─────────────────────────────────────
# Yêu cầu cứng (user duyệt 2026-10-13): không đổi exit code, không chặn/sửa event gốc trong
# MỌI trường hợp; chỉ finding; cảnh báo không đệ quy, không vào bus/inbox/.
WARN_MARK = "thiếu \"measured_by\""
NUM_PAYLOAD = '{"selfcheck":"27 PASS / 0 FAIL","note":"đo lại"}'


def warn_path(sandbox):
    return os.path.join(sandbox, "bus", "_measured_by_warn.jsonl")


def warns(sandbox):
    path = warn_path(sandbox)
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def raw_lines(sandbox, agent):
    path = os.path.join(sandbox, "bus", "inbox", f"{agent}.jsonl")
    if not os.path.exists(path):
        return []
    with open(path, "rb") as f:
        return f.read().split(b"\n")[:-1]


_VOLATILE = re.compile(rb'"(event_id|ts)": "[^"]*"')


def expected_line(sandbox, args):
    """Dòng event mà bản TRƯỚC cổng sẽ ghi: đúng output của `mike_json.py event` (đường dựng
    event không đổi), chuẩn hoá 2 trường tất yếu khác nhau mỗi lần gọi (event_id, ts)."""
    a = list(args) + [""] * (5 - len(args))
    p = subprocess.run([sys.executable, os.path.join(sandbox, "bin", "mike_json.py"), "event",
                        a[0], a[1], a[2], a[3], "1", a[4]], capture_output=True)
    return _VOLATILE.sub(rb'"\1": "X"', p.stdout.rstrip(b"\n"))


def case_measured_by_warn_only():
    d = mksandbox()
    try:
        # (a) có số + CÓ measured_by ⇒ im
        for mb in ('"git diff --numstat a b"', '["cmd1","out.txt"]', '{"selfcheck":"x.log"}'):
            args = ["A", "finding", "co-khai", '{"n_fail":27,"measured_by":%s}' % mb]
            rc, out, err = run(d, args)
            check(f"measured_by={mb[:14]}…: rc=0, im lặng", rc == 0 and WARN_MARK not in err,
                  f"rc={rc} err={err[:160]}")
        check("có khai ⇒ KHÔNG tạo file cảnh báo", warns(d) == [], repr(warns(d))[:200])
        check("có khai ⇒ ghi đủ 3 event", len(events(d, "A")) == 3)

        # (b) có số + THIẾU ⇒ cảnh báo, event gốc y nguyên
        args = ["B", "finding", "thieu-khai", NUM_PAYLOAD, "Wags_20261013_012440"]
        rc, out, err = run(d, args)
        check("thiếu khai: rc=0 (không chặn)", rc == 0, f"rc={rc}")
        check("thiếu khai: stdout y như bản cũ", out == "appended finding/thieu-khai for B\n", repr(out))
        check("thiếu khai: stderr có đúng 1 dòng cảnh báo",
              err.count(WARN_MARK) == 1 and err.count("\n") == 1, repr(err)[:300])
        check("thiếu khai: cảnh báo nói rõ KHÔNG chặn + nêu topic + số mẫu",
              "KHÔNG chặn" in err and "thieu-khai" in err and "27" in err, repr(err)[:300])
        check("thiếu khai: cảnh báo dặn event ĐÃ ghi / ĐỪNG gửi lại / khai ở CẤP CAO NHẤT / Lần sau",
              all(k in err for k in ("event ĐÃ ghi", "ĐỪNG gửi lại", "CẤP CAO NHẤT", "Lần sau")),
              repr(err)[:300])
        lines = raw_lines(d, "B")
        check("thiếu khai: inbox có ĐÚNG 1 dòng (cảnh báo không sinh event ⇒ không đệ quy)",
              len(lines) == 1, f"{len(lines)} dòng")
        check("thiếu khai: dòng event ĐÚNG TỪNG BYTE như mike_json dựng (trừ event_id/ts)",
              lines and _VOLATILE.sub(rb'"\1": "X"', lines[0]) == expected_line(d, args),
              repr(lines[:1])[:300])
        ev = events(d, "B")[0]
        check("thiếu khai: payload không bị thêm/sửa trường nào",
              ev["payload"] == json.loads(NUM_PAYLOAD) and ev["event_type"] == "finding")
        w = warns(d)
        check("thiếu khai: đúng 1 bản ghi ở bus/_measured_by_warn.jsonl", len(w) == 1, repr(w)[:200])
        if w:
            check("bản ghi cảnh báo trỏ đúng event (event_id, agent, topic, trace_id)",
                  w[0].get("event_id") == ev["event_id"] and w[0].get("agent_id") == "B"
                  and w[0].get("topic") == "thieu-khai"
                  and w[0].get("trace_id") == "Wags_20261013_012440", repr(w[0])[:300])
            check("bản ghi cảnh báo có số mẫu + rule_version + loại cảnh báo",
                  w[0].get("sample_numbers") == ["27", "0"] and w[0].get("rule_version") == 1
                  and w[0].get("warn") == "finding_missing_measured_by",
                  repr(w[0])[:300])
            ts = w[0].get("ts", "")
            now = datetime.datetime.now(datetime.timezone.utc)
            try:
                dt = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=datetime.timezone.utc)
                skew = abs((now - dt).total_seconds())
            except ValueError:
                skew = None
            check("bản ghi cảnh báo: ts là UTC thật (lệch <120s, bất kể TZ)",
                  skew is not None and skew < 120, f"ts={ts!r} skew={skew}")
        check("bus/inbox/ chỉ chứa file của agent (cảnh báo KHÔNG nằm trong inbox)",
              sorted(os.listdir(os.path.join(d, "bus", "inbox"))) == ["A.jsonl", "B.jsonl"],
              repr(os.listdir(os.path.join(d, "bus", "inbox"))))
        check("không sinh question/hàng đợi cách ly nào", rejected(d) == []
              and not any(e.get("event_type") == "question" for a in "AB" for e in events(d, a)))

        # lần cảnh báo thứ 2 phải NỐI vào file, không ghi đè
        rc, out, err = run(d, ["B", "finding", "thieu-khai-2", '{"n_fail": 3}'])
        check("thiếu khai lần 2: rc=0, file cảnh báo có 2 bản ghi (nối, không ghi đè)",
              rc == 0 and [x.get("topic") for x in warns(d)] == ["thieu-khai", "thieu-khai-2"],
              repr(warns(d))[:200])

        # (c) finding KHÔNG số ⇒ im
        n0 = len(warns(d))
        for pl in ('{"status":"done","branch":"fix/x-20261013","commit":"a1b2c3d4","ok":true}',
                   '{"note":"merge luc 2026-10-13T01:24:40Z, job Wags_20261013_012440, §23 r2 v3.4b"}',
                   '{"note":"xem bin/a.py:120 va kb/x.md ngay 12/10 luc 08:23"}'):
            rc, out, err = run(d, ["C", "finding", "khong-so", pl])
            check(f"finding không số ⇒ rc=0, im: {pl[:38]}…", rc == 0 and WARN_MARK not in err,
                  f"rc={rc} err={err[:200]}")
        check("finding không số ⇒ không thêm bản ghi cảnh báo", len(warns(d)) == n0)

        # (d) loại event KHÁC ⇒ đường cũ, không chạy cổng
        for et in ("status", "question", "answer", "decision", "error", "heartbeat",
                   "verification", "findings", "Finding", "FINDING"):
            rc, out, err = run(d, ["D", et, "loai-khac", NUM_PAYLOAD])
            check(f"event_type={et}: rc=0, im", rc == 0 and err == "", f"rc={rc} err={err[:200]}")
        check("loại khác ⇒ không thêm bản ghi cảnh báo", len(warns(d)) == n0)
        check("loại khác ⇒ ghi đủ 10 event", len(events(d, "D")) == 10)

        # Loại khác KHÔNG được chạy helper (không thêm tiến trình nào): thay helper bằng bản
        # ghi dấu — finding phải để lại dấu (chứng minh bản dò hoạt động), loại khác thì không.
        marker = os.path.join(d, "helper_ran")
        real_helper = os.path.join(d, "bin", "finding_measured_by.py")
        shutil.copy2(real_helper, real_helper + ".real")
        with open(real_helper, "w", encoding="utf-8") as f:
            f.write(f"open({marker!r}, 'a').write('x')\n")
        for et in ("status", "heartbeat", "question", "answer", "decision", "error",
                   "verification", "VERIFY", "findings", "Finding", "FINDING", "finding2"):
            run(d, ["D2", et, "khong-chay-helper", NUM_PAYLOAD])
        check("loại khác ⇒ helper KHÔNG được gọi", not os.path.exists(marker))
        run(d, ["D2", "finding", "co-chay-helper", NUM_PAYLOAD])
        check("finding ⇒ helper ĐƯỢC gọi đúng 1 lần (bản dò có hiệu lực)",
              os.path.exists(marker) and open(marker).read() == "x")
        shutil.move(real_helper + ".real", real_helper)

        # (e) payload lạ: chuỗi thường / mảng ⇒ không xét, hành vi cũ
        for pl in ("chuoi thuong co so 27 va 11", "[27, 11]", "27", '"11 fail"'):
            rc, out, err = run(d, ["E", "finding", "payload-la", pl])
            check(f"payload lạ {pl[:16]!r}: rc=0, im", rc == 0 and WARN_MARK not in err,
                  f"rc={rc} err={err[:200]}")
        check("payload lạ ⇒ ghi đủ 4 event, không cảnh báo",
              len(events(d, "E")) == 4 and len(warns(d)) == n0)
        # JSON hỏng vẫn bị chốt CŨ từ chối như trước (cổng mới không nới, không đổi rc)
        rc, out, err = run(d, ["E", "finding", "json-hong", '{"n": 27'])
        check("finding JSON hỏng ⇒ vẫn rc=1 như trước, không cảnh báo measured_by",
              rc == 1 and WARN_MARK not in err and len(events(d, "E")) == 4, f"rc={rc}")

        # (f) tắt khẩn
        rc, out, err = run(d, ["F", "finding", "tat", NUM_PAYLOAD], {"AE_MEASURED_BY_CHECK": "0"})
        check("AE_MEASURED_BY_CHECK=0 ⇒ rc=0, im, event vẫn ghi",
              rc == 0 and err == "" and len(events(d, "F")) == 1 and len(warns(d)) == n0,
              f"rc={rc} err={err[:200]}")
        # chỉ ĐÚNG chuỗi "0" mới tắt (ghi rõ trong append_event.sh) — giá trị khác vẫn bật
        for val in ("2", "false", ""):
            rc, out, err = run(d, ["F", "finding", "van-bat", NUM_PAYLOAD],
                               {"AE_MEASURED_BY_CHECK": val})
            check(f"AE_MEASURED_BY_CHECK={val!r} ⇒ VẪN cảnh báo", rc == 0 and WARN_MARK in err,
                  f"rc={rc} err={err[:120]}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def case_measured_by_fail_open():
    """Phần kiểm tự hỏng theo MỌI kiểu ⇒ rc=0, stdout y cũ, event gốc đúng từng byte."""
    args = ["G", "finding", "fail-open", NUM_PAYLOAD]

    def assert_intact(label, d, rc, out, max_s=None, dt=None):
        lines = raw_lines(d, "G")
        check(f"fail-open [{label}]: rc=0", rc == 0, f"rc={rc}")
        check(f"fail-open [{label}]: stdout y như bản cũ", out == "appended finding/fail-open for G\n",
              repr(out))
        check(f"fail-open [{label}]: event gốc ghi đúng từng byte",
              len(lines) == 1 and _VOLATILE.sub(rb'"\1": "X"', lines[0]) == expected_line(d, args),
              repr(lines)[:300])
        if max_s is not None:
            check(f"fail-open [{label}]: không treo (≤{max_s}s)", dt <= max_s, f"{dt:.1f}s")

    helper_bodies = {
        "helper nổ exception": "raise RuntimeError('boom')\n",
        "helper exit 3": "import sys\nsys.exit(3)\n",
        "helper lỗi cú pháp": "def (:\n",
        "helper tự kill -9": "import os, signal\nos.kill(os.getpid(), signal.SIGKILL)\n",
    }
    for label, body in helper_bodies.items():
        d = mksandbox()
        try:
            with open(os.path.join(d, "bin", "finding_measured_by.py"), "w", encoding="utf-8") as f:
                f.write(body)
            rc, out, err = run(d, args)
            assert_intact(label, d, rc, out)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    d = mksandbox()
    try:
        # Có file mà KHÔNG ĐỌC ĐƯỢC (-r, không phải -f) ⇒ im như vắng mặt. Bỏ qua nếu chạy bằng
        # quyền đọc-được-mọi-file (root): chmod 000 không còn nghĩa.
        hp = os.path.join(d, "bin", "finding_measured_by.py")
        os.chmod(hp, 0)
        if os.access(hp, os.R_OK):
            print("  SKIP  helper KHÔNG ĐỌC ĐƯỢC (process vẫn đọc được file chmod 000)")
        else:
            rc, out, err = run(d, args)
            assert_intact("helper KHÔNG ĐỌC ĐƯỢC", d, rc, out)
            check("fail-open [helper KHÔNG ĐỌC ĐƯỢC]: stderr RỖNG", err == "", repr(err)[:200])
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = mksandbox()
    try:
        os.remove(os.path.join(d, "bin", "finding_measured_by.py"))
        rc, out, err = run(d, args)
        assert_intact("helper VẮNG", d, rc, out)
        check("fail-open [helper VẮNG]: stderr RỖNG (đổi tên helper = công tắc tắt sạch toàn fleet)",
              err == "", repr(err)[:200])
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = mksandbox()
    try:
        with open(os.path.join(d, "bin", "finding_measured_by.py"), "w", encoding="utf-8") as f:
            f.write("import time\ntime.sleep(60)\n")
        t0 = time.time()
        rc, out, err = run(d, args)
        assert_intact("helper treo 60s", d, rc, out, max_s=8, dt=time.time() - t0)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = mksandbox()
    try:
        # Helper dò khoá: flock inbox của agent phải ĐÃ NHẢ lúc phần kiểm chạy (không giữ khoá
        # lâu hơn bản cũ). Helper thử khoá non-blocking chính file inbox rồi ghi kết quả.
        marker = os.path.join(d, "lock_probe")
        with open(os.path.join(d, "bin", "finding_measured_by.py"), "w", encoding="utf-8") as f:
            f.write("import fcntl, os\n"
                    f"inbox = {os.path.join(d, 'bus', 'inbox', 'G.jsonl')!r}\n"
                    "try:\n    os.fstat(9); fd9 = 'fd9-open'\n"
                    "except OSError:\n    fd9 = 'fd9-closed'\n"
                    "n = len(open(inbox, 'rb').read().splitlines()) if os.path.exists(inbox) else 0\n"
                    "fh = open(inbox, 'a')\n"
                    "try:\n    fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB); r = 'free'\n"
                    "except OSError:\n    r = 'held'\n"
                    f"open({marker!r}, 'w').write(r + ' ' + fd9 + ' lines=' + str(n))\n")
        rc, out, err = run(d, args)
        assert_intact("helper dò khoá", d, rc, out)
        got = open(marker).read() if os.path.exists(marker) else "(helper không chạy)"
        check("khoá inbox ĐÃ nhả trước khi phần kiểm chạy", got.startswith("free "), got)
        check("helper KHÔNG thừa hưởng fd 9 của inbox", " fd9-closed " in got, got)
        check("THỨ TỰ: lúc phần kiểm chạy, event gốc ĐÃ nằm trên bus", got.endswith(" lines=1"), got)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = mksandbox()
    try:
        # THỨ TỰ + ĐỒNG BỘ: helper ngủ 1,5s. Dòng "appended" phải ra TRƯỚC khi helper xong
        # (cổng đứng SAU echo) và script phải CHỜ helper (không bỏ mồ côi chạy nền). Đo hiệu
        # t_exit − t_line nên không phụ thuộc tải máy.
        with open(os.path.join(d, "bin", "finding_measured_by.py"), "w", encoding="utf-8") as f:
            f.write("import time\ntime.sleep(1.5)\n")
        env = dict(os.environ)
        env.pop("JOB_ID", None)
        p = subprocess.Popen([os.path.join(d, "bin", "append_event.sh")] + args, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        line = p.stdout.readline()
        t_line = time.time()
        p.wait()
        gap = time.time() - t_line
        check("THỨ TỰ: 'appended' in ra TRƯỚC khi phần kiểm xong, script CHỜ phần kiểm (gap≥1s)",
              line == "appended finding/fail-open for G\n" and p.returncode == 0 and gap >= 1.0,
              f"line={line!r} rc={p.returncode} gap={gap:.2f}s")
        p.stdout.close()
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = mksandbox()
    try:
        # stderr của caller là PIPE ĐẦY không ai đọc: helper kẹt ở write ⇒ timeout cắt, trần +2s.
        r_fd, w_fd = os.pipe()
        os.set_blocking(w_fd, False)
        try:
            while True:
                os.write(w_fd, b"x" * 4096)
        except BlockingIOError:
            pass
        os.set_blocking(w_fd, True)
        env = dict(os.environ)
        env.pop("JOB_ID", None)
        t0 = time.time()
        try:
            # timeout cứng phía harness: nếu cổng hỏng mà treo thật thì selfcheck FAIL chứ không treo theo.
            p = subprocess.run([os.path.join(d, "bin", "append_event.sh")] + args, env=env,
                               stdout=subprocess.PIPE, stderr=w_fd, text=True, timeout=30)
            dt = time.time() - t0
            assert_intact("stderr là pipe đầy", d, p.returncode, p.stdout, max_s=8, dt=dt)
        except subprocess.TimeoutExpired:
            check("fail-open [stderr là pipe đầy]: không treo (harness timeout 30s)", False,
                  "append_event.sh treo >30s")
        finally:
            os.close(r_fd)
            os.close(w_fd)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = mksandbox()
    try:
        os.makedirs(warn_path(d))            # file cảnh báo KHÔNG ghi được (là thư mục)
        rc, out, err = run(d, args)
        assert_intact("file cảnh báo không ghi được", d, rc, out)
        check("fail-open [file cảnh báo không ghi được]: stderr VẪN cảnh báo", WARN_MARK in err,
              repr(err)[:200])
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = mksandbox()
    try:
        # stderr ĐÓNG hẳn (caller `2>&-`): helper không in được ⇒ vẫn phải êm, bản ghi vẫn có.
        env = dict(os.environ)
        env.pop("JOB_ID", None)
        p = subprocess.run(["bash", "-c", 'exec "$0" "$@" 2>&-',
                            os.path.join(d, "bin", "append_event.sh")] + args,
                           capture_output=True, text=True, env=env)
        assert_intact("stderr đóng", d, p.returncode, p.stdout)
        check("fail-open [stderr đóng]: bản ghi cảnh báo vẫn được ghi", len(warns(d)) == 1)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = mksandbox()
    try:
        # payload chứa byte hỏng (surrogateescape) + có số: đường cũ ghi được thì nay vẫn phải ghi.
        bad = os.fsdecode(b'{"n": 27, "s": "h\xe1\xbb ng \xff"}')
        rc, out, err = run(d, ["G", "finding", "fail-open", bad])
        check("fail-open [payload byte hỏng]: rc=0, ghi đúng 1 event",
              rc == 0 and len(raw_lines(d, "G")) == 1, f"rc={rc} err={err[:200]}")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = mksandbox()
    try:
        # payload lớn (~100KB, sát trần 128KB/arg của execve): không treo, không cắt.
        big = json.dumps({"n_rows": 12663, "blob": "x1 " * 33000})
        t0 = time.time()
        rc, out, err = run(d, ["G", "finding", "fail-open", big])
        dt = time.time() - t0
        evs = events(d, "G")
        check("fail-open [payload ~100KB]: rc=0, payload nguyên vẹn, cảnh báo, ≤10s",
              rc == 0 and len(evs) == 1 and evs[0]["payload"] == json.loads(big)
              and WARN_MARK in err and dt <= 10, f"rc={rc} dt={dt:.1f}s")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def case_measured_by_rule_table():
    """Luật cơ học, từng mệnh đề của docstring finding_measured_by.py."""
    sys.path.insert(0, os.path.join(ROOT, "bin"))
    sys.dont_write_bytecode = True       # không để lại bin/__pycache__ ngoài sandbox
    import finding_measured_by as fmb

    def v(payload, etype="finding"):
        return fmb.verdict({"event_type": etype, "payload": payload})

    has_num = [
        ({"rate": 7.5}, "giá trị JSON float"),
        ({"n": 0}, "giá trị JSON int 0"),
        ({"a": {"b": [{"c": 11}]}}, "số lồng sâu"),
        ({"note": "6M 7,4->7,5: Vietcombank 7,5% cao nhat"}, "ca thật 10-12 cctg 7,4->7,5"),
        ({"broad_scan_s23": "11 file fail o ca hai nhanh"}, "ca thật 10-12 broad_scan 11"),
        ({"monitor": "1658 -> 1527 (-131; go ~-460 dong, them ~+330)"}, "ca thật 10-12 ~-460/+330"),
        ({"diff": "+480/-611"}, "diffstat +a/-b"),
        ({"selfcheck": "228/0 x 3 TZ"}, "tỉ số PASS/FAIL"),
        ({"cagr": "23,37%"}, "phần trăm kiểu VN"),
        ({"x": ["ok", "93 PASS"]}, "số trong list chuỗi"),
        ({"measured_by": "", "n": 3}, "measured_by rỗng"),
        ({"measured_by": "   ", "n": 3}, "measured_by toàn khoảng trắng"),
        ({"measured_by": [], "n": 3}, "measured_by list rỗng"),
        ({"measured_by": {}, "n": 3}, "measured_by dict rỗng"),
        ({"measured_by": None, "n": 3}, "measured_by null"),
        ({"measured_by": True, "n": 3}, "measured_by không phải chuỗi/list/dict"),
        ({"meta": {"measured_by": "cmd"}, "n": 3}, "measured_by KHÔNG ở cấp cao nhất"),
        ({"Measured_By": "cmd", "n": 3}, "sai hoa/thường tên khoá"),
    ]
    for payload, label in has_num:
        check(f"luật: CẢNH BÁO — {label}", bool(v(payload)), repr(v(payload)))
    silent = [
        ({"ok": True, "merged": False}, "bool không phải số"),
        ({"commit": "a1b2c3d4", "md5": "4707bcbe9f0a11223344556677889900"}, "mã hex"),
        ({"ts": "2026-10-12T01:09:31Z", "d": "2026-10-12", "when": "12/10/2026 luc 08:23"}, "ngày/giờ"),
        ({"job": "Taylor_20261012_124854"}, "job id"),
        ({"file": "bin/a.py:120", "f2": "x_selfcheck.py:33", "p": "kb/retro-2026-10-12.md"}, "đường dẫn/file"),
        ({"note": "vong r2, T5, v3.4b, §23, #5, K11, 10-12, 06-15..06-30, a1,2b L:120 3x v3.4 a1,2"},
         "mã tham chiếu dính chữ/gạch/dấu"),
        ({"p": "xem logs/2026/10/run va data/x/7/out"}, "số là thành phần đường dẫn"),
        ({"f": "snapshot 20261013.json va 2026.md"}, "tên file thuần số"),
        ({"t": "2026-10-12 01:09:31 va 2026-10-12T01:09Z"}, "ngày ISO + giờ rời"),
        ({"branch": "fix/x-20261013", "wt": "agents/Wags/wt-measuredby-1013"}, "tên nhánh/worktree"),
        ({"1_numbers_unchanged": "ok", "v2": "xong"}, "số chỉ nằm trong TÊN KHOÁ"),
        ({"note": ""}, "chuỗi rỗng"),
        ({}, "payload rỗng"),
        ({"n": 27, "measured_by": "git diff --numstat a b"}, "đã khai (chuỗi)"),
        ({"n": 27, "measured_by": ["out.txt"]}, "đã khai (list)"),
        ({"n": 27, "measured_by": {"n": "x.log"}}, "đã khai (dict)"),
    ]
    for payload, label in silent:
        check(f"luật: IM — {label}", v(payload) is None, repr(v(payload)))
    for et in ("status", "question", "answer", "decision", "error", "heartbeat", "findings", ""):
        check(f"luật: IM — event_type={et!r} dù có số", v({"n": 27}, et) is None)
    # Token CHÍNH XÁC, mỗi dòng một dạng — gồm cả các "hệ quả chấp nhận" ghi trong docstring.
    exact = [
        ("-25,2%", ["-25,2%"]), ("23.37", ["23.37"]), ("10%", ["10%"]), ("N=200", ["200"]),
        ("~460", ["460"]), ("(27)", ["27"]), ("7,4->7,5", ["7,4", "7,5"]),
        ("+480/-611", ["+480", "-611"]), ("25/25", ["25", "25"]), ("13/13", ["13", "13"]),
        ("32/12", ["32", "12"]), ("23,37%/năm", ["23,37%"]), ("10%/năm", ["10%"]), ("3,5%/năm,", ["3,5%"]), ("23,37%/năm.", ["23,37%"]), ("(10%/năm)", ["10%"]), ("(3,5%/năm).", ["3,5%"]), ("3%/năm;", ["3%"]), ("3%/năm:", ["3%"]), ("3%/năm!", ["3%"]), ("3%/năm?", ["3%"]), ("[3%/năm]", ["3%"]),
        ("0,1%/chiều", ["0,1%"]), ("3.pyramid", ["3"]),
        # âm tính giả đã biết
        ("0.2-0.5", []), ("1,234.5-2,000", []), ("2.5x", []), ("1.5tỷ", []), ("3.4b", []),
        ("1.2e6", []), ("9/9", []), ("25/12", []), ("P/E=12.5", []), ("(pass=27/fail=0)", []),
        ("+480/-611dòng", []), ("DATA/2026/10", []), ("−25,2%", ["25,2%"]),
        # dương tính giả đã biết
        ("HTTP 401", ["401"]), ("12.10.2026", ["12.10.2026"]), ("2026/10/12", ["2026"]),
    ] + [(f"7{ext} 20261013{ext}", []) for ext in (
        ".py", ".sh", ".json", ".jsonl", ".md", ".csv", ".txt", ".log", ".html", ".sql",
        ".yaml", ".yml", ".toml")]
    for text, want in exact:
        got = fmb.number_tokens({"x": text}, 20)
        check(f"luật: token {text!r} ⇒ {want}", got == want, repr(got))
    check("luật: IM — số chỉ nằm trong tên khoá THUẦN SỐ", v({"27": "ok", "k 11": "x"}) is None)
    check("luật: IM — số chỉ nằm trong topic",
          fmb.verdict({"event_type": "finding", "topic": "x 27 fail", "payload": {"a": "b"}}) is None)
    for key in ("measured_by ", " measured_by", "measuredBy", "measured-by", "MEASURED_BY"):
        check(f"luật: CẢNH BÁO — khoá {key!r} không phải `measured_by`", bool(v({key: "cmd", "n": 3})))
    check("luật: IM — measured_by là list khác rỗng dù phần tử rỗng (chỉ kiểm RỖNG, không kiểm nội dung)",
          v({"measured_by": [""], "n": 3}) is None and v({"measured_by": {"a": ""}, "n": 3}) is None)
    for payload in ("11 fail", [27], 27, None):
        check(f"luật: IM — payload không phải object ({type(payload).__name__})", v(payload) is None)
    check("luật: event không phải dict ⇒ IM (không nổ)", fmb.verdict([1, 2]) is None)
    check("luật: số mẫu bị chặn ở 5 token",
          fmb.number_tokens({"s": " ".join(str(i) for i in range(10, 40))}) == ["10", "11", "12", "13", "14"])
    # Helper gọi TRỰC TIẾP: tự nó phải rc=0 trong mọi ca (không dựa vào `|| true` của shell).
    helper = os.path.join(ROOT, "bin", "finding_measured_by.py")
    ev = json.dumps({"event_type": "finding", "topic": "chủ-đề " + "x" * 300, "agent_id": "H",
                     "event_id": "e1", "payload": {"n": 27}})
    tmp = tempfile.mkdtemp(prefix="fmb_direct_")
    try:
        wf = os.path.join(tmp, "w.jsonl")
        for label, stdin, argv, want_warn in (
                ("stdin rác", "khong phai json", [wf], False),
                ("stdin rỗng", "", [wf], False),
                ("event hợp lệ + file", ev, [wf], True),
                ("event hợp lệ, KHÔNG có đường dẫn file", ev, [], True),
                ("event hợp lệ, thư mục cha không tồn tại", ev, [os.path.join(tmp, "nope", "w")], True)):
            p = subprocess.run([sys.executable, helper] + argv, input=stdin, capture_output=True,
                               text=True)
            check(f"helper trực tiếp [{label}]: rc=0", p.returncode == 0, f"rc={p.returncode}")
            check(f"helper trực tiếp [{label}]: cảnh báo={want_warn}, không traceback",
                  (WARN_MARK in p.stderr) == want_warn and "Traceback" not in p.stderr,
                  repr(p.stderr)[:200])
        with open(wf, encoding="utf-8") as f:
            recs = [json.loads(l) for l in f if l.strip()]
        check("helper trực tiếp: đúng 1 bản ghi, topic có dấu đọc lại được và bị cắt ở 200 ký tự",
              len(recs) == 1 and recs[0]["topic"] == ("chủ-đề " + "x" * 300)[:200],
              repr(recs)[:200])
        with open(wf, "rb") as f:
            check("helper trực tiếp: file cảnh báo thuần ASCII", f.read().isascii())
        # stderr HỎNG (/dev/full): rc vẫn phải 0, bản ghi vẫn có
        wf2 = os.path.join(tmp, "w2.jsonl")
        with open("/dev/full", "w") as full:
            p = subprocess.run([sys.executable, helper, wf2], input=ev, stderr=full,
                               stdout=subprocess.DEVNULL, text=True)
        check("helper trực tiếp [stderr /dev/full]: rc=0 và bản ghi vẫn được ghi",
              p.returncode == 0 and os.path.isfile(wf2), f"rc={p.returncode}")
        # locale C ép buộc: topic có dấu vẫn đọc lại đúng (helper tự giải mã UTF-8 từ byte)
        wf3 = os.path.join(tmp, "w3.jsonl")
        envc = dict(os.environ, LC_ALL="C", PYTHONCOERCECLOCALE="0", PYTHONUTF8="0")
        envc.pop("PYTHONIOENCODING", None)
        # ensure_ascii=False: byte UTF-8 THẬT trên stdin (json.dumps mặc định escape hết ⇒ ca rỗng)
        raw = json.dumps(json.loads(ev), ensure_ascii=False).encode("utf-8")
        p = subprocess.run([sys.executable, helper, wf3], input=raw, capture_output=True, env=envc)
        check("helper trực tiếp [LC_ALL=C]: đầu vào thử có byte ngoài ASCII", not raw.isascii())
        r3 = [json.loads(l) for l in open(wf3, encoding="utf-8")] if os.path.isfile(wf3) else []
        check("helper trực tiếp [LC_ALL=C]: rc=0, topic có dấu đọc lại đúng",
              p.returncode == 0 and len(r3) == 1 and r3[0]["topic"].startswith("chủ-đề "),
              f"rc={p.returncode} {r3!r}"[:200])
        # topic nhiều dòng không được bẻ cảnh báo thành 2 dòng; agent_id/số mẫu bị cắt
        ev2 = json.dumps({"event_type": "finding", "topic": "tieu-de\nFATAL: dong gia",
                          "agent_id": "H" * 200, "event_id": "e2",
                          "payload": {"x": "so " + "9" * 40}})
        wf4 = os.path.join(tmp, "w4.jsonl")
        p = subprocess.run([sys.executable, helper, wf4], input=ev2, capture_output=True, text=True)
        r4 = [json.loads(l) for l in open(wf4, encoding="utf-8")] if os.path.isfile(wf4) else [{}]
        check("helper trực tiếp: topic nhiều dòng ⇒ stderr vẫn ĐÚNG 1 dòng",
              p.stderr.count("\n") == 1 and "\nFATAL" not in p.stderr, repr(p.stderr)[:200])
        check("helper trực tiếp: agent_id cắt 80, số mẫu cắt 24 (cả file lẫn stderr)",
              r4[0].get("agent_id") == "H" * 80 and r4[0].get("sample_numbers") == ["9" * 24]
              and "9" * 25 not in p.stderr, repr(r4)[:200])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    check("luật: thứ tự số mẫu = thứ tự xuất hiện",
          fmb.number_tokens({"a": 3, "b": "x 44 y", "c": 5.5}) == ["3", "44", "5.5"])


def main():
    for fn in (case_valid_paths, case_too_many_args, case_truncated_json_payload,
               case_json_error_message_names_real_cause,
               case_trace_id_shape, case_job_id_fallback,
               case_verify_finding_sanitizes_inherited_trace_id,
               case_quarantine_survives_discarded_stderr,
               case_byte_hong_khong_dau_doc_duoc_bus,
               case_quarantine_ghi_duoc_arg_byte_hong,
               case_measured_by_warn_only, case_measured_by_fail_open,
               case_measured_by_rule_table):
        print(f"\n{fn.__name__}")
        fn()
    print()
    if _fails:
        print(f"FAIL: {len(_fails)} assertion hỏng")
        for n in _fails:
            print(f"  - {n}")
        sys.exit(1)
    print("OK: toàn bộ assertion PASS")


if __name__ == "__main__":
    main()
