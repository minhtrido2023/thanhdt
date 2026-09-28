#!/usr/bin/env python3
"""Kho ledger BẤT BIẾN cho mọi số đã pin — khoá bằng md5, GHI-MỘT-LẦN.

VÌ SAO TỒN TẠI (sự cố 2026-09-28, user phát hiện):
User gửi lại `data/v23_golive_audit_2014_now.csv` mà anh giữ từ ~2026-06-11 (md5
`84295bee…`) để đối chiếu. Trên đĩa hôm nay CÙNG TÊN ĐÓ là một file KHÁC HẲN
(md5 `65e7bb04…`, cửa sổ →2026-06-25). **Hai bản khác nhau, một cái tên, không ai
biết cái nào là "số đã công bố".** Nguyên nhân gốc: `data/*.csv` nằm trong
`.gitignore` (dòng 57) ⇒ 822 file audit / 2,1GB **không có version control** và tên
canonical **ghi đè được**. Registry rule 2 ("CSV LÀ ARTIFACT ĐÔNG CỨNG") tồn tại từ
2026-06-19 nhưng CHƯA BAO GIỜ có cơ chế cưỡng chế — nó là văn xuôi.

Đo thật lúc mở kho (2026-09-28): trong 31 tham chiếu md5 của `results_registry.md`,
**2 mất dấu hoàn toàn** và **5 chỉ còn sống bên trong một worktree TẠM** — xoá
worktree là mất số pin.

HỢP ĐỒNG:
  · Bố cục: data/pinned_ledgers/<pin_date>__<label>__<md5[:8]>.csv.gz
  · Manifest: data/pinned_ledgers/PINS.jsonl (append-only, 1 dòng JSON / pin)
  · GHI-MỘT-LẦN: md5 đã có trong manifest ⇒ TỪ CHỐI (rc=2), in đường dẫn bản cũ.
    Không có đường "ghi đè" nào — kể cả `--force`. Muốn sửa metadata thì
    `annotate`, muốn thay số thì pin một ledger MỚI (md5 mới).
  · Ghi nguyên tử: tmp + fsync + os.replace (coding_guidelines §5) — kill giữa
    chừng không để lại .gz nửa vời cho lần sau tin nhầm.

LỆNH:
  pin_ledger.py add <ledger.csv> --label L --command "…" --audit-end YYYY-MM-DD
                                 [--note "…"] [--decided-by user|agent]
  pin_ledger.py verify [--md5 M | --all]      # tính lại md5 mọi bản đã lưu
  pin_ledger.py resolve <md5|md5[:8]>         # in đường dẫn bản lưu
  pin_ledger.py extract <md5|md5[:8]> --out P # bung ra CSV để audit
  pin_ledger.py list [--json]
  pin_ledger.py --selfcheck [--mutations]

KHÔNG làm: không xoá, không nén lại, không dọn rác. Retention = giữ vĩnh viễn
(B6). Thiếu dung lượng thì nén thêm, KHÔNG xoá — một ledger đã pin mất đi là một
con số neo kỳ vọng không còn tái lập được.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import sys
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from wc_paths import find_wc_root  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")

STORE_DIRNAME = os.path.join("data", "pinned_ledgers")
MANIFEST_NAME = "PINS.jsonl"

# Các METRIC rút tự động từ ledger. Tên khoá = đúng tên trong cột `key` của file.
_METRIC_KEYS = (
    "cagr",
    "sharpe_252",
    "sharpe_spy",
    "sortino_252",
    "max_dd",
    "calmar",
    "final_nav_vnd",
    "init_nav_vnd",
    "years",
    "cash_flow_identity_max_err_vnd_BAL",
    "cash_flow_identity_max_err_vnd_LAG",
    "final_nav_identity_err_vnd_BAL",
    "final_nav_identity_err_vnd_LAG",
    "allocator_replay_err_vnd",
)


def store_root(wc_root: str) -> str:
    return os.path.join(wc_root, STORE_DIRNAME)


def manifest_path(wc_root: str) -> str:
    return os.path.join(store_root(wc_root), MANIFEST_NAME)


def md5_of_file(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_of_gz_member(path: str) -> str:
    """md5 của NỘI DUNG GỐC bên trong .gz (không phải md5 của chính file .gz).

    Phải so bằng nội dung gốc: gzip nhúng mtime + tên nên hai lần nén cùng một
    CSV cho hai file .gz khác byte. So md5 của .gz là so nhầm thứ.
    """
    h = hashlib.md5()
    with gzip.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest(wc_root: str) -> list:
    p = manifest_path(wc_root)
    if not os.path.exists(p):
        return []
    out = []
    with open(p, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as exc:
                # §29: nêu đúng dòng hỏng, không đoán "file corrupt".
                raise SystemExit(
                    f"PINS.jsonl dòng {i} không parse được JSON: {exc}\n"
                    f"  file: {p}\n"
                    f"  Sửa TAY dòng đó; script KHÔNG tự đoán/bỏ qua."
                ) from exc
    return out


def _atomic_write_bytes(path: str, data: bytes) -> None:
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_pin_", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _atomic_append_line(path: str, line: str) -> None:
    """Append 1 dòng + fsync. Append của POSIX là nguyên tử với ghi < PIPE_BUF,
    nhưng ta vẫn fsync để dòng manifest không biến mất sau khi .gz đã nằm trên đĩa
    (thứ tự: GHI .gz TRƯỚC, manifest SAU — mất manifest còn dò lại được từ tên file;
    mất .gz mà manifest nói có thì tệ hơn nhiều)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line if line.endswith("\n") else line + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def parse_ledger_metrics(path: str) -> dict:
    """Rút METRIC + META tối thiểu từ ledger CSV. KHÔNG tính lại gì — chỉ đọc."""
    metrics = {}
    meta = {}
    counts = {}
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        rdr = csv.reader(fh)
        for row in rdr:
            if not row:
                continue
            rt = row[0]
            counts[rt] = counts.get(rt, 0) + 1
            if rt == "METRIC" and len(row) >= 3:
                if row[1] in _METRIC_KEYS:
                    try:
                        metrics[row[1]] = float(row[2])
                    except (TypeError, ValueError):
                        metrics[row[1]] = row[2]
            elif rt == "META" and len(row) >= 3:
                if row[1] in ("period", "system", "baseline_label", "cash_identity"):
                    meta[row[1]] = row[2]
    counts.pop("record_type", None)
    return {"metrics": metrics, "meta": meta, "row_counts": counts}


def selfcheck_ok(metrics: dict) -> bool:
    """Self-check 0 VND theo quy ước registry rule 5.

    Ngưỡng 1e-3 VND: identity thực tế trả ~1e-5 (sai số float64 trên số cỡ 1e11),
    KHÔNG phải 0.0 tuyệt đối. Đặt 0.0 cứng sẽ loại mọi ledger thật.
    Thiếu khoá ⇒ KHÔNG coi là pass (fail-closed) — ledger không khai identity thì
    ta không có bằng chứng gì để nói nó cân sổ.
    """
    need = (
        "cash_flow_identity_max_err_vnd_BAL",
        "cash_flow_identity_max_err_vnd_LAG",
        "final_nav_identity_err_vnd_BAL",
        "final_nav_identity_err_vnd_LAG",
    )
    for k in need:
        v = metrics.get(k)
        if v is None or not isinstance(v, float):
            return False
        if abs(v) > 1e-3:
            return False
    return True


def safe_label(label: str) -> str:
    keep = []
    for ch in label:
        keep.append(ch if (ch.isalnum() or ch in "-_.") else "-")
    out = "".join(keep).strip("-")
    if not out:
        raise SystemExit("--label rỗng sau khi chuẩn hoá; đặt nhãn có chữ/số.")
    return out[:80]


def cmd_add(args, wc_root: str) -> int:
    src = os.path.abspath(args.ledger)
    if not os.path.exists(src):
        raise SystemExit(f"Không thấy ledger: {src}")
    digest = md5_of_file(src)
    man = read_manifest(wc_root)

    for rec in man:
        if rec.get("md5") == digest:
            print(
                f"TỪ CHỐI (rc=2) — md5 {digest} ĐÃ nằm trong kho, kho là GHI-MỘT-LẦN.\n"
                f"  bản đã lưu : {rec.get('stored')}\n"
                f"  nhãn cũ    : {rec.get('label')}  (pin {rec.get('pin_date')})\n"
                f"  Nội dung y hệt ⇒ không cần pin lại. Muốn đổi metadata: dùng `annotate`."
            )
            return 2

    info = parse_ledger_metrics(src)
    pin_date = args.pin_date or datetime.now(ICT).strftime("%Y-%m-%d")
    fname = f"{pin_date}__{safe_label(args.label)}__{digest[:8]}.csv.gz"
    dest = os.path.join(store_root(wc_root), fname)
    if os.path.exists(dest):
        # Không thể xảy ra nếu manifest đúng; nếu xảy ra = manifest và đĩa lệch nhau.
        raise SystemExit(
            f"Đường dẫn đã tồn tại nhưng KHÔNG có trong manifest: {dest}\n"
            f"  ⇒ manifest và đĩa lệch nhau. Chạy `verify --all` rồi sửa TAY; "
            f"script KHÔNG tự ghi đè."
        )

    with open(src, "rb") as fh:
        raw = fh.read()
    buf = io.BytesIO()
    # mtime=0 ⇒ nén cùng nội dung cho ra cùng byte (tái lập được), không nhúng giờ chạy.
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9, mtime=0) as gz:
        gz.write(raw)
    _atomic_write_bytes(dest, buf.getvalue())

    back = md5_of_gz_member(dest)
    if back != digest:
        os.unlink(dest)
        raise SystemExit(
            f"Đọc lại bản nén KHÔNG khớp md5 gốc ({back} != {digest}) — đã xoá bản hỏng, "
            f"KHÔNG ghi manifest."
        )

    rec = {
        "md5": digest,
        "md5_gz": md5_of_file(dest),
        "label": args.label,
        "pin_date": pin_date,
        "audit_end": args.audit_end,
        "command": args.command,
        "stored": os.path.relpath(dest, wc_root),
        "source_name": os.path.basename(src),
        "bytes_raw": len(raw),
        "bytes_gz": os.path.getsize(dest),
        "row_counts": info["row_counts"],
        "metrics": info["metrics"],
        "meta": info["meta"],
        "selfcheck_0vnd": selfcheck_ok(info["metrics"]),
        "decided_by": args.decided_by,
        "note": args.note or "",
        "pinned_at_ict": datetime.now(ICT).isoformat(timespec="seconds"),
    }
    _atomic_append_line(manifest_path(wc_root), json.dumps(rec, ensure_ascii=False))

    m = info["metrics"]
    print(f"✅ PIN {digest}")
    print(f"   lưu tại  : {rec['stored']}  ({len(raw):,}B → {rec['bytes_gz']:,}B)")
    print(f"   nhãn     : {args.label}   AUDIT_END={args.audit_end}")
    if "cagr" in m:
        print(
            f"   CAGR {m['cagr']*100:.2f}%  Sharpe252 {m.get('sharpe_252', float('nan')):.3f}  "
            f"MaxDD {m.get('max_dd', float('nan'))*100:.2f}%  Calmar {m.get('calmar', float('nan')):.3f}"
        )
    print(f"   self-check 0 VND: {'PASS' if rec['selfcheck_0vnd'] else '⚠️ KHÔNG XÁC NHẬN ĐƯỢC'}")
    if not rec["selfcheck_0vnd"]:
        print("   ⚠️ Ledger vẫn được lưu, nhưng manifest ghi selfcheck_0vnd=false — "
              "cổng pin_artifact_gate sẽ TỪ CHỐI dùng nó làm số pin.")
    return 0


def _find(man: list, key: str) -> list:
    key = key.lower()
    return [r for r in man if r.get("md5", "").startswith(key)]


def cmd_resolve(args, wc_root: str) -> int:
    hits = _find(read_manifest(wc_root), args.md5)
    if not hits:
        print(f"KHÔNG tìm thấy md5 bắt đầu bằng {args.md5!r} trong kho.")
        return 1
    if len(hits) > 1:
        print(f"MƠ HỒ — {len(hits)} bản khớp tiền tố {args.md5!r}; đưa md5 dài hơn:")
        for r in hits:
            print("  ", r["md5"], r["stored"])
        return 1
    print(os.path.join(wc_root, hits[0]["stored"]))
    return 0


def cmd_extract(args, wc_root: str) -> int:
    hits = _find(read_manifest(wc_root), args.md5)
    if len(hits) != 1:
        print(f"Cần đúng 1 bản khớp, tìm được {len(hits)}.")
        return 1
    p = os.path.join(wc_root, hits[0]["stored"])
    with gzip.open(p, "rb") as fh:
        data = fh.read()
    got = hashlib.md5(data).hexdigest()
    if got != hits[0]["md5"]:
        print(f"⚠️ BẢN LƯU HỎNG: md5 đọc ra {got} != manifest {hits[0]['md5']} — KHÔNG ghi ra.")
        return 3
    _atomic_write_bytes(os.path.abspath(args.out), data)
    print(f"✅ bung ra {args.out}  (md5 {got} khớp manifest)")
    return 0


def cmd_verify(args, wc_root: str) -> int:
    man = read_manifest(wc_root)
    targets = man if args.all or not args.md5 else _find(man, args.md5)
    if not targets:
        print("Không có bản nào để kiểm.")
        return 1
    bad = 0
    for r in targets:
        p = os.path.join(wc_root, r["stored"])
        if not os.path.exists(p):
            print(f"❌ MẤT FILE  {r['md5'][:12]}  {r['stored']}")
            bad += 1
            continue
        got = md5_of_gz_member(p)
        if got != r["md5"]:
            print(f"❌ LỆCH nội dung  {r['md5'][:12]} → giải nén ra {got[:12]}  {r['stored']}")
            bad += 1
            continue
        # Phải kiểm CẢ md5 của chính file .gz. Lý do (selfcheck bắt được 2026-09-28):
        # gzip đọc xong member hợp lệ là DỪNG — nối thêm rác vào cuối file vẫn giải
        # nén ra đúng nội dung ⇒ chỉ so md5 nội dung là BỎ LỌT file đã bị sửa.
        want_gz = r.get("md5_gz")
        if want_gz is None:
            print(f"⚠️ {r['md5'][:12]}  {r['label']}  (bản cũ không có md5_gz — chỉ kiểm được nội dung)")
            continue
        got_gz = md5_of_file(p)
        if got_gz != want_gz:
            print(f"❌ FILE BỊ SỬA  {r['md5'][:12]}  md5_gz {want_gz[:12]} → {got_gz[:12]}  {r['stored']}")
            bad += 1
        else:
            print(f"✅ {r['md5'][:12]}  {r['label']}")
    print(f"--- {len(targets) - bad}/{len(targets)} bản còn nguyên vẹn")
    return 1 if bad else 0


def cmd_list(args, wc_root: str) -> int:
    man = read_manifest(wc_root)
    if args.json:
        print(json.dumps(man, ensure_ascii=False, indent=1))
        return 0
    if not man:
        print("Kho rỗng.")
        return 0
    print(f"{'md5':10} {'pin_date':11} {'CAGR':>7} {'Sharpe':>7} {'MaxDD':>8}  label")
    for r in man:
        m = r.get("metrics", {})
        c = f"{m['cagr']*100:.2f}%" if isinstance(m.get("cagr"), float) else "-"
        s = f"{m['sharpe_252']:.3f}" if isinstance(m.get("sharpe_252"), float) else "-"
        d = f"{m['max_dd']*100:.2f}%" if isinstance(m.get("max_dd"), float) else "-"
        print(f"{r['md5'][:10]} {r.get('pin_date',''):11} {c:>7} {s:>7} {d:>8}  {r.get('label','')}")
    return 0


def cmd_annotate(args, wc_root: str) -> int:
    """Thêm ghi chú cho một pin — KHÔNG sửa dòng cũ, append dòng `annotation`.
    Manifest append-only: lịch sử không được viết lại."""
    hits = _find(read_manifest(wc_root), args.md5)
    if len(hits) != 1:
        print(f"Cần đúng 1 bản khớp, tìm được {len(hits)}.")
        return 1
    rec = {
        "record": "annotation",
        "md5": hits[0]["md5"],
        "note": args.note,
        "at_ict": datetime.now(ICT).isoformat(timespec="seconds"),
    }
    _atomic_append_line(manifest_path(wc_root), json.dumps(rec, ensure_ascii=False))
    print(f"✅ ghi chú thêm cho {hits[0]['md5'][:12]}")
    return 0


# ----------------------------------------------------------------- selfcheck
_SAMPLE = """record_type,key,value,ymd
META,system,V2.3A test,
META,period,2014-01-02 -> 2026-06-19,
META,cash_identity,"deposit interest = 0, no margin",
TX,,,2014-01-02
DAILY,,,2014-01-02
METRIC,cagr,0.2336876855359784,
METRIC,sharpe_252,1.8780657727616887,
METRIC,max_dd,-0.14642652702283832,
METRIC,calmar,1.595938183383465,
METRIC,final_nav_vnd,684515711483.0369,
METRIC,cash_flow_identity_max_err_vnd_BAL,6.103515625e-05,
METRIC,cash_flow_identity_max_err_vnd_LAG,6.4849853515625e-05,
METRIC,final_nav_identity_err_vnd_BAL,0.0,
METRIC,final_nav_identity_err_vnd_LAG,0.0,
"""


def _run_selfcheck(mutations: bool) -> int:
    import shutil

    n = 0
    fails = []

    def check(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)

    sandbox = tempfile.mkdtemp(prefix="pinledger_sc_")
    try:
        wc = os.path.join(sandbox, "WorkingClaude")
        os.makedirs(os.path.join(wc, "data"), exist_ok=True)
        open(os.path.join(wc, "wc_env.sh"), "w").close()
        led = os.path.join(sandbox, "led.csv")
        with open(led, "w", encoding="utf-8") as fh:
            fh.write(_SAMPLE)
        digest = md5_of_file(led)

        class A:
            pass

        a = A()
        a.ledger = led
        a.label = "r3-pin0-test"
        a.command = "CMD"
        a.audit_end = "2026-06-19"
        a.note = ""
        a.decided_by = "agent"
        a.pin_date = "2026-09-28"

        rc = cmd_add(a, wc)
        check("add_rc0_lan_dau", rc == 0)
        man = read_manifest(wc)
        check("manifest_co_1_dong", len(man) == 1)
        check("md5_ghi_dung", man and man[0]["md5"] == digest)
        check("selfcheck_0vnd_true", man and man[0]["selfcheck_0vnd"] is True)
        check("metric_cagr_rut_dung", man and abs(man[0]["metrics"]["cagr"] - 0.2336876855359784) < 1e-15)
        check("meta_period_rut_dung", man and man[0]["meta"]["period"].endswith("2026-06-19"))
        check("row_counts_dung", man and man[0]["row_counts"].get("METRIC") == 9
              and man[0]["row_counts"].get("TX") == 1)
        stored = os.path.join(wc, man[0]["stored"])
        check("file_gz_ton_tai", os.path.exists(stored))
        check("gz_giai_nen_ra_dung_md5", md5_of_gz_member(stored) == digest)
        check("manifest_luu_ca_md5_gz", man and man[0].get("md5_gz") == md5_of_file(stored))
        check("ten_file_mang_md5_8", os.path.basename(stored).endswith(f"__{digest[:8]}.csv.gz"))
        check("ten_file_mang_pin_date", os.path.basename(stored).startswith("2026-09-28__"))

        # GHI-MỘT-LẦN: pin lại đúng nội dung đó phải bị từ chối rc=2
        rc2 = cmd_add(a, wc)
        check("add_lan_2_tu_choi_rc2", rc2 == 2)
        check("manifest_van_1_dong_sau_tu_choi", len(read_manifest(wc)) == 1)

        # Cùng nội dung nhưng TÊN KHÁC ⇒ vẫn phải từ chối (khoá theo md5, không theo tên)
        led2 = os.path.join(sandbox, "led_ten_khac.csv")
        shutil.copy(led, led2)
        a.ledger = led2
        a.label = "nhan-khac"
        check("trung_noi_dung_khac_ten_van_tu_choi", cmd_add(a, wc) == 2)

        # Nội dung KHÁC ⇒ pin được, thành bản thứ 2
        led3 = os.path.join(sandbox, "led3.csv")
        with open(led3, "w", encoding="utf-8") as fh:
            fh.write(_SAMPLE.replace("0.2336876855359784", "0.2524000000000000"))
        a.ledger = led3
        a.label = "dep1m-21s"
        check("noi_dung_khac_pin_duoc", cmd_add(a, wc) == 0)
        check("manifest_2_dong", len(read_manifest(wc)) == 2)

        # verify --all sạch
        va = A()
        va.all = True
        va.md5 = None
        check("verify_all_sach", cmd_verify(va, wc) == 0)

        # resolve + extract
        ra = A()
        ra.md5 = digest[:8]
        check("resolve_rc0", cmd_resolve(ra, wc) == 0)
        ea = A()
        ea.md5 = digest[:8]
        ea.out = os.path.join(sandbox, "out.csv")
        check("extract_rc0", cmd_extract(ea, wc) == 0)
        check("extract_byte_identical", md5_of_file(ea.out) == digest)

        # md5 mơ hồ / không có
        ra.md5 = "ffffffff"
        check("resolve_khong_co_rc1", cmd_resolve(ra, wc) == 1)

        # selfcheck_ok fail-closed khi thiếu khoá
        check("selfcheck_thieu_khoa_la_false", selfcheck_ok({"cagr": 0.2}) is False)
        check("selfcheck_lech_lon_la_false",
              selfcheck_ok({"cash_flow_identity_max_err_vnd_BAL": 1.0,
                            "cash_flow_identity_max_err_vnd_LAG": 0.0,
                            "final_nav_identity_err_vnd_BAL": 0.0,
                            "final_nav_identity_err_vnd_LAG": 0.0}) is False)
        check("selfcheck_sai_so_float_van_pass",
              selfcheck_ok({"cash_flow_identity_max_err_vnd_BAL": 6.1e-05,
                            "cash_flow_identity_max_err_vnd_LAG": 6.5e-05,
                            "final_nav_identity_err_vnd_BAL": 0.0,
                            "final_nav_identity_err_vnd_LAG": 0.0}) is True)

        # BẢN LƯU BỊ SỬA ⇒ verify phải bắt
        with open(stored, "ab") as fh:
            fh.write(b"\x00")
        check("verify_bat_duoc_ban_hong_noi_them_rac", cmd_verify(va, wc) == 1)
        # và cả khi nội dung giải nén ĐỔI THẬT
        with gzip.GzipFile(stored, "wb", compresslevel=9, mtime=0) as gz:
            gz.write(b"noi dung khac han")
        check("verify_bat_duoc_noi_dung_doi", cmd_verify(va, wc) == 1)

        # manifest hỏng ⇒ SystemExit có tên dòng, KHÔNG im lặng bỏ qua
        _atomic_append_line(manifest_path(wc), "{khong-phai-json")
        try:
            read_manifest(wc)
            check("manifest_hong_phai_bao_loi", False)
        except SystemExit as exc:
            check("manifest_hong_phai_bao_loi", "dòng 3" in str(exc))

        if mutations:
            killed = 0
            total = 0

            def mut(name, fn):
                nonlocal killed, total
                total += 1
                if fn():
                    killed += 1
                else:
                    fails.append(f"MUTATION SỐNG SÓT: {name}")

            # M1 ghi-một-lần bị gỡ ⇒ manifest sẽ có 2 dòng cùng md5
            def m1():
                man2 = read_manifest_safe(wc)
                seen = [r["md5"] for r in man2 if "md5" in r]
                return len(seen) == len(set(seen))
            mut("M1_khong_co_md5_trung_trong_manifest", m1)

            # M2 nếu khoá theo TÊN thay vì md5 thì bản led2 (tên khác) đã lọt
            def m2():
                man2 = read_manifest_safe(wc)
                return not any(r.get("label") == "nhan-khac" for r in man2)
            mut("M2_khoa_theo_md5_khong_theo_ten", m2)

            # M3 md5 lưu phải là md5 NỘI DUNG GỐC, không phải md5 của file .gz
            def m3():
                p = os.path.join(wc, read_manifest_safe(wc)[1]["stored"])
                return md5_of_file(p) != read_manifest_safe(wc)[1]["md5"]
            mut("M3_md5_la_cua_noi_dung_khong_phai_cua_gz", m3)

            # M4 nén phải tái lập được byte (mtime=0), không nhúng giờ chạy
            def m4():
                b1 = io.BytesIO()
                with gzip.GzipFile(fileobj=b1, mode="wb", compresslevel=9, mtime=0) as g:
                    g.write(b"abc")
                b2 = io.BytesIO()
                with gzip.GzipFile(fileobj=b2, mode="wb", compresslevel=9, mtime=0) as g:
                    g.write(b"abc")
                return b1.getvalue() == b2.getvalue()
            mut("M4_nen_tai_lap_duoc_byte", m4)

            # M5 không còn file .part sót lại (ghi nguyên tử)
            def m5():
                return not any(f.startswith(".tmp_pin_")
                               for f in os.listdir(store_root(wc)))
            mut("M5_khong_con_file_tam", m5)

            print(f"mutation: {killed}/{total} bị giết")
            n += total

    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    if fails:
        print(f"❌ FAIL {len(fails)}/{n}")
        for f in fails:
            print("   -", f)
        return 1
    print(f"✅ pin_ledger selfcheck: {n} assertion PASS")
    return 0


def read_manifest_safe(wc_root: str) -> list:
    """Như read_manifest nhưng bỏ dòng hỏng — CHỈ dùng trong selfcheck sau khi đã
    cố tình chèn dòng rác để test nhánh báo lỗi."""
    p = manifest_path(wc_root)
    out = []
    if not os.path.exists(p):
        return out
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--mutations", action="store_true")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("add")
    p.add_argument("ledger")
    p.add_argument("--label", required=True)
    p.add_argument("--command", required=True, help="LỆNH CHẠY ĐẦY ĐỦ đã sinh ra ledger này")
    p.add_argument("--audit-end", required=True)
    p.add_argument("--note", default="")
    p.add_argument("--decided-by", default="agent", choices=["user", "agent"])
    p.add_argument("--pin-date", default=None)

    p = sub.add_parser("verify")
    p.add_argument("--md5", default=None)
    p.add_argument("--all", action="store_true")

    p = sub.add_parser("resolve")
    p.add_argument("md5")

    p = sub.add_parser("extract")
    p.add_argument("md5")
    p.add_argument("--out", required=True)

    p = sub.add_parser("list")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("annotate")
    p.add_argument("md5")
    p.add_argument("--note", required=True)

    args = ap.parse_args(argv)
    if args.selfcheck:
        return _run_selfcheck(args.mutations)
    if not args.cmd:
        ap.print_help()
        return 1

    wc_root = os.environ.get("PIN_STORE_WC_ROOT") or find_wc_root(__file__)
    return {
        "add": cmd_add,
        "verify": cmd_verify,
        "resolve": cmd_resolve,
        "extract": cmd_extract,
        "list": cmd_list,
        "annotate": cmd_annotate,
    }[args.cmd](args, wc_root)


if __name__ == "__main__":
    sys.exit(main())
