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
import json
import os
import shutil
import subprocess
import sys
import tempfile

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


def main():
    for fn in (case_valid_paths, case_too_many_args, case_truncated_json_payload,
               case_trace_id_shape, case_job_id_fallback,
               case_verify_finding_sanitizes_inherited_trace_id,
               case_quarantine_survives_discarded_stderr,
               case_byte_hong_khong_dau_doc_duoc_bus):
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
