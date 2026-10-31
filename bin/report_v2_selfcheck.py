#!/usr/bin/env python3
"""report_v2_selfcheck.py — selfcheck cho bin/report_v2 (report-style v2, 2026-10-31).

Kiểm (không gửi gì, không chạm mạng; SMTP bị thay bằng giả):
  1. Dựng THÁNG <period> cho mỗi account HAI lần vào cùng thư mục ⇒ md5 MỌI file trùng (tất định).
  2. Recon: số trong manifest == nav_period_returns (§31) cho tháng/quý/từ đầu; mọi dòng đối soát lệch 0.
  3. Artifact lint sạch trên bản dựng; MUTATION: chèn từng lỗi (`['|`, `**`, `|---|`, None, nan, tên nội bộ,
     font không nhúng, sửa file sau khi dựng) ⇒ lint PHẢI chặn; cổng giao (`_check_artifact_lint`) PHẢI raise.
  4. Narrative: vượt trần từ / gạch / tự viết số / tên nội bộ / mục nội bộ ở SpaceX ⇒ PHẢI bị từ chối.
  5. Email v2: thân = HTML builder, ảnh cid đủ, PDF đính kèm, dòng manifest bị bỏ khỏi thân.

Chạy: python3 bin/report_v2_selfcheck.py [--period 2026-10] [--accounts SpaceX,ZaloPay]
§16: chạy thêm dưới `env -u TZ` và `TZ=America/New_York` — kết quả (và md5) phải giống hệt.
"""
import argparse
import email
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)
from report_v2 import artifact_lint as al  # noqa: E402
from report_v2 import narrative as N  # noqa: E402

FAILS = []


def check(cond, what):
    print(("  ok   " if cond else "  FAIL ") + what)
    if not cond:
        FAILS.append(what)


def md5_tree(d):
    out = {}
    for root, _, files in os.walk(d):
        for f in sorted(files):
            p = os.path.join(root, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, d)] = hashlib.md5(fh.read()).hexdigest()
    return out


def build(acct, period, out, cadence="monthly"):
    r = subprocess.run([sys.executable, os.path.join(BIN, "report_v2", "build.py"), cadence,
                        "--account", acct, "--period", period, "--out-dir", out, "--promote",
                        "--delivery-state", os.path.join(out, "_no_state.json")],
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-3000:])
    return r.returncode


def canon(acct, end):
    """nav_period_returns (§31) cho ngày cuối kỳ."""
    r = subprocess.run([sys.executable, os.path.join(BIN, "nav_period_returns.py"), "--account", acct,
                        "--report-date", end], capture_output=True, text=True, timeout=300)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def resign(md_path):
    """Sau khi mutate file trong thư mục v2: ghi lại sha vào manifest + .md để chỉ còn lỗi NỘI DUNG."""
    text = open(md_path, encoding="utf-8").read()
    man_rel, _, pdf_rel = al.parse_tag(text)
    base = os.path.dirname(md_path)
    man_p = os.path.join(base, man_rel)
    man = json.load(open(man_p, encoding="utf-8"))
    d = os.path.dirname(man_p)
    man["pdf_sha256"] = al.sha256(os.path.join(d, man["pdf"]))
    man["html_sha256"] = al.sha256(os.path.join(d, man["html"]))
    json.dump(man, open(man_p, "w", encoding="utf-8"), ensure_ascii=False)
    text = al.TAG_RE.sub(f"<!-- {al.MANIFEST_TAG} {man_rel} manifest_sha256={al.sha256(man_p)} "
                         f"pdf_sha256={man['pdf_sha256']} pdf={pdf_rel} -->", text)
    open(md_path, "w", encoding="utf-8").write(text)
    return man, d


def mutations(md_path, acct, tmp):
    from pathlib import Path
    import report_delivery_gate as g
    investor = acct == "SpaceX"

    def fresh(tag):
        d = os.path.join(tmp, f"mut_{acct}_{tag}")
        shutil.rmtree(d, ignore_errors=True)
        shutil.copytree(os.path.dirname(md_path), d)
        return os.path.join(d, os.path.basename(md_path))

    html_cases = {"repr": "['| Nguồn | Đóng góp |", "bold": "**đậm thô**", "sep": "\n|---|---:|\n",
                  "none": " None ", "nan": " nan "}
    if investor:
        html_cases["internal"] = " theo Livermore "
        html_cases["internal_file"] = " thiếu dnse_raw_2026-07-01.jsonl "
        html_cases["zalopay"] = " Khoản rút chuyển sang tài khoản ZaloPay "
        html_cases["zalopay_acct"] = " số TK 0001743768 "
        html_cases["zalopay_lower"] = " chuyển sang zalopay "
        html_cases["livermore_lower"] = " theo livermore "
        html_cases["bal"] = " sổ BAL "
        html_cases["signal"] = " SIGNAL_V11 "
    for tag, inj in html_cases.items():
        m = fresh("html_" + tag)
        man, d = al.load_v2(m)
        hp = os.path.join(d, man["html"])
        h = open(hp, encoding="utf-8").read()
        h = h.replace("</body>", f"<p>{inj}</p></body>", 1)
        open(hp, "w", encoding="utf-8").write(h)
        resign(m)
        probs = al.lint_v2(m, investor_facing=investor)
        check(any("HTML email" in p for p in probs), f"{acct} mutation HTML '{tag}' bị lint chặn")
        try:
            g._check_artifact_lint(Path(m))
            check(False, f"{acct} mutation HTML '{tag}': cổng giao raise")
        except RuntimeError:
            check(True, f"{acct} mutation HTML '{tag}': cổng giao raise")

    # r3 N2: "nan giải" là chữ tiếng Việt, KHÔNG phải token rỗng ⇒ lint KHÔNG được chặn
    m = fresh("html_nan_giai")
    man, d = al.load_v2(m)
    hp = os.path.join(d, man["html"])
    h = open(hp, encoding="utf-8").read() + "<p>Thanh khoản là vấn đề nan giải.</p>"
    open(hp, "w", encoding="utf-8").write(h)
    resign(m)
    check(not al.lint_v2(m, investor_facing=investor), f"{acct} 'nan giải' KHÔNG bị lint chặn nhầm")

    import pymupdf
    m = fresh("pdf_font")
    man, d = al.load_v2(m)
    pp = os.path.join(d, man["pdf"])
    doc = pymupdf.open(pp)
    doc[0].insert_text((60, 60), "Helvetica base14", fontname="helv", fontsize=6)
    doc.save(pp + ".x"); doc.close(); os.replace(pp + ".x", pp)
    resign(m)
    probs = al.lint_v2(m, investor_facing=investor)
    check(any("font" in p for p in probs), f"{acct} mutation PDF font Helvetica không nhúng bị chặn")

    m = fresh("pdf_raw")
    man, d = al.load_v2(m)
    pp = os.path.join(d, man["pdf"])
    doc = pymupdf.open(pp)
    doc[0].insert_font(fontname="bvp", fontfile=os.path.join(BIN, "report_v2", "fonts", "BeVietnamPro-Regular.ttf"))
    doc[0].insert_text((60, 60), "**thô** nan", fontname="bvp", fontsize=6)
    doc.save(pp + ".x"); doc.close(); os.replace(pp + ".x", pp)
    resign(m)
    probs = al.lint_v2(m, investor_facing=investor)
    check(any("PDF trang 1" in p for p in probs), f"{acct} mutation PDF chữ markdown thô bị chặn")

    m = fresh("tamper")
    man, d = al.load_v2(m)
    with open(os.path.join(d, man["pdf"]), "ab") as fh:
        fh.write(b"\n% tampered\n")
    probs = al.lint_v2(m, investor_facing=investor)
    check(any("sha256" in p for p in probs), f"{acct} mutation sửa PDF sau khi dựng (sha lệch) bị chặn")

    m = fresh("md_repr")
    with open(m, "a", encoding="utf-8") as fh:
        fh.write("\n['| Nguồn | Đóng góp |\\n|---|', 515443.0]\n")
    check(bool(al.lint_md(open(m, encoding="utf-8").read())), f"{acct} mutation .md repr tuple bị chặn")


def promote_cases(md_path, acct, tmp):
    """r3 N4/N8: nháp → tên chuẩn chỉ khi lint sạch; không ghi đè bản đã giao; manifest bị khoá sha."""
    sys.path.insert(0, os.path.join(BIN, "report_v2"))
    import build as B
    investor = acct == "SpaceX"
    out = os.path.dirname(md_path)
    stem = os.path.basename(md_path)[:-3]
    draft = os.path.join(out, "v2", "draft", stem + ".md")
    check(os.path.exists(draft), f"{acct} nháp nằm ở reports/v2/draft/ (lượt quét top-level không thấy)")
    res = {"md": draft}
    # (a) bản chuẩn đã giao + nội dung khác ⇒ rc=5, không ghi đè
    with open(md_path, "a", encoding="utf-8") as fh:
        fh.write("\n<!-- bản đã giao -->\n")
    sent = open(md_path, "rb").read()
    st = os.path.join(tmp, f"state_{acct}.json")
    json.dump({"reports": {stem + ".md": {"discord": {"status": "delivered"}}}}, open(st, "w"))
    rc, msg = B.promote(res, out, investor, st)
    check(rc == 5 and open(md_path, "rb").read() == sent, f"{acct} promote TỪ CHỐI ghi đè bản đã giao (rc={rc})")
    # (b) chưa giao ⇒ ghi đè được, bản chuẩn == nháp
    rc, msg = B.promote(res, out, investor, os.path.join(tmp, "none.json"))
    check(rc == 0 and open(md_path, "rb").read() == open(draft, "rb").read(), f"{acct} promote khi chưa giao ⇒ bản chuẩn == nháp (rc={rc})")
    # (c) nháp hỏng lint ⇒ rc=4, bản chuẩn giữ nguyên
    d2 = os.path.join(tmp, f"promote_lint_{acct}")
    shutil.rmtree(d2, ignore_errors=True)
    shutil.copytree(os.path.dirname(draft), d2)
    m2 = os.path.join(d2, stem + ".md")
    man, d = al.load_v2(m2)
    hp = os.path.join(d, man["html"])
    open(hp, "w", encoding="utf-8").write(open(hp, encoding="utf-8").read() + "<p>**thô**</p>")
    resign(m2)
    before = open(md_path, "rb").read()
    rc, msg = B.promote({"md": m2}, out, investor, os.path.join(tmp, "none.json"))
    check(rc == 4 and open(md_path, "rb").read() == before, f"{acct} nháp hỏng lint ⇒ rc=4, không promote (rc={rc})")
    # (d) N8: sửa tay số trong manifest (inception_pct) mà không ký lại tag ⇒ CHẶN
    d3 = os.path.join(tmp, f"manifest_tamper_{acct}")
    shutil.rmtree(d3, ignore_errors=True)
    shutil.copytree(out, d3, ignore=shutil.ignore_patterns("draft", "mut_*"))
    m3 = os.path.join(d3, stem + ".md")
    man, d = al.load_v2(m3)
    man["numbers"]["inception_pct"] = 9.99
    json.dump(man, open(os.path.join(d, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False)
    probs = al.lint_v2(m3, investor_facing=investor)
    check(any("manifest" in p for p in probs), f"{acct} sửa tay manifest.numbers (không ký lại) bị chặn ({probs[:1]})")
    t = open(m3, encoding="utf-8").read()
    open(m3, "w", encoding="utf-8").write(al.TAG_RE.sub(lambda mm: mm.group(0).replace(f"manifest_sha256={mm.group(2)} ", ""), t))
    check(any("manifest_sha256" in p for p in al.lint_v2(m3, investor_facing=investor)), f"{acct} tag thiếu manifest_sha256 bị chặn")


def daily_return_gate_case(md_path, acct, tmp):
    """r3 N5: cổng §21 trên bản NGÀY v2 kiểm >0 dòng (từ manifest.positions); sửa ô tỷ suất ⇒ CHẶN."""
    import io
    import report_return_gate as rrg
    man, _d = al.load_v2(md_path)
    n = len(man.get("positions") or [])
    buf = io.StringIO()
    rc = rrg.run_gate(md_path, out=buf)
    got = buf.getvalue()
    check(rc == 0 and n > 0 and f"v2: {n} dòng" in got, f"{acct} daily cổng §21 kiểm {n} dòng vị thế từ manifest (rc={rc})")
    if not n:
        return
    d2 = os.path.join(tmp, f"rrg_mut_{acct}")
    shutil.rmtree(d2, ignore_errors=True)
    shutil.copytree(os.path.dirname(md_path), d2, ignore=shutil.ignore_patterns("draft", "mut_*", "promote_*", "manifest_tamper_*"))
    m2 = os.path.join(d2, os.path.basename(md_path))
    man, d = al.load_v2(m2)
    man["positions"][0][2] = "+99,99%"
    json.dump(man, open(os.path.join(d, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False)
    resign(m2)
    buf = io.StringIO()
    rc = rrg.run_gate(m2, out=buf)
    check(rc != 0, f"{acct} daily: ô tỷ suất {man['positions'][0][0]} sửa thành +99,99% (ký lại) ⇒ cổng §21 CHẶN (rc={rc})")


def write_order_case(tmp):
    """r3 N3: vượt trần trang ⇒ write_outputs raise và KHÔNG để lại .md (cũng không manifest)."""
    sys.path.insert(0, os.path.join(BIN, "report_v2"))
    import build as B
    d = os.path.join(tmp, "write_order")
    shutil.rmtree(d, ignore_errors=True)
    cx = B.Ctx("daily", "SpaceX", "SpaceX_daily_report_2099-01-01", d)
    saved = (B.R.banner, B.R.build_pdf, B.R.build_email_html, B.R.lint_pdf)

    def fake_pdf(blocks, pdf, **k):
        open(pdf, "wb").write(b"%PDF-fake")
        return 3

    def fake_html(blocks, bn, title, path):
        open(path, "w").write("<html></html>")
        json.dump({}, open(path[:-5] + "_cid.json", "w"))
        return path
    B.R.banner = lambda *a, **k: a[3]
    B.R.build_pdf, B.R.build_email_html = fake_pdf, fake_html
    B.R.lint_pdf = lambda p: {"raw_markdown_hits": [], "non_bvp_fonts": []}
    try:
        B.write_outputs(cx, "t", "k", "s", "h", ["x"], {})
        check(False, "N3 vượt trần trang ⇒ raise")
    except RuntimeError:
        check(True, "N3 vượt trần trang ⇒ raise")
    finally:
        B.R.banner, B.R.build_pdf, B.R.build_email_html, B.R.lint_pdf = saved
    check(not os.path.exists(os.path.join(d, cx.stem + ".md")) and not os.path.exists(cx.f("manifest.json")),
          "N3 lỗi trần trang KHÔNG để lại .md/manifest")


def narrative_cases():
    facts = "−1,89% −1,53% 945,14 tr 0,36 điểm %"
    good = {"headline": "Tháng 10 −1,89% so với VN-Index −1,53%", "key_points": ["Kém chỉ số 0,36 điểm %."],
            "outlook": [{"scenario": "Cơ sở", "condition": "Thị trường đi ngang", "invalidation": "Thủng hỗ trợ",
                         "prob": "trung bình"}]}
    try:
        N.validate(good, facts, investor_facing=True, allow_internal=False)
        check(True, "narrative hợp lệ được nhận")
    except N.NarrativeError as exc:
        check(False, f"narrative hợp lệ được nhận ({exc})")
    bad = {
        "quá 25 từ/gạch": {"key_points": [" ".join(["chữ"] * 26)]},
        "quá 3 gạch": {"key_points": ["a.", "b.", "c.", "d."]},
        "tự viết số": {"key_points": ["Lãi 7,77% trong tháng."]},
        "tên nội bộ": {"key_points": ["Theo Livermore thị trường yếu."]},
        "nhắc ZaloPay (bản ngoài)": {"key_points": ["Khoản rút chuyển sang tài khoản ZaloPay."]},
        "nhắc liên tài khoản (bản ngoài)": {"key_points": ["Nạp rút liên tài khoản trong tháng."]},
        "từ vận hành (nhà đầu tư)": {"key_points": ["Cron chạy trễ."]},
        "mục nội bộ ở SpaceX": {"internal": [{"title": "x", "bullets": ["y"]}]},
        "outlook > 4 kịch bản": {"outlook": [{"scenario": "a", "condition": "b", "invalidation": "c"}] * 5},
        "mục ngoài khung": {"sections": {"blabla": ["x"]}},
        # r3 N1 — dấu/hướng: số đúng độ lớn nhưng SAI dấu phải bị chặn
        "sai hướng 'tăng 1,89%' (pipeline −1,89%)": {"headline": "Tài khoản tăng 1,89% trong tháng"},
        "sai dấu '+1,89%' (pipeline −1,89%)": {"headline": "Tháng 10 +1,89%"},
        "sai hướng 'lãi 1,53%'": {"key_points": ["VN-Index lãi 1,53%."]},
        "sai dấu '−0,36 điểm %' (pipeline dương)": {"key_points": ["Kém chỉ số −0,36 điểm %."]},
        "số nhỏ kèm % không có trong pipeline": {"key_points": ["Giảm 2% trong tháng."]},
        # r3 N2 — chặn sớm cùng danh sách với lint
        "nan token": {"key_points": ["Tỷ suất nan."]},
        "nan%": {"key_points": ["Tỷ suất nan% trong tháng."]},
        "None token": {"key_points": ["Beta None"]},
        "** markdown": {"key_points": ["**Đậm** thô."]},
        "tên riêng chữ thường (livermore)": {"key_points": ["Theo livermore thị trường yếu."]},
        "tên riêng chữ thường (zalopay)": {"key_points": ["Chuyển sang zalopay."]},
        "BAL": {"key_points": ["Sổ BAL giữ nguyên."]},
        "SIGNAL_V11": {"key_points": ["Tín hiệu SIGNAL_V11 mạnh."]},
    }
    ok_cases = {
        "'giảm 1,89%' đúng hướng": {"headline": "Tài khoản giảm 1,89% trong tháng, VN-Index giảm 1,53%"},
        "'nan giải' không phải token rỗng": {"key_points": ["Thanh khoản thấp là vấn đề nan giải."]},
        "mức (từ/xuống) không suy hướng": {"key_points": ["NAV giảm còn 945,14 tr."]},
        "số nguyên trơn 0..12": {"key_points": ["3 mã mới trong 12 phiên."]},
    }
    for what, nar in ok_cases.items():
        try:
            N.validate(nar, facts, investor_facing=True, allow_internal=False)
            check(True, f"narrative {what} được nhận")
        except N.NarrativeError as exc:
            check(False, f"narrative {what} được nhận ({exc})")
    for what, nar in bad.items():
        try:
            N.validate(nar, facts, investor_facing=True, allow_internal=False)
            check(False, f"narrative '{what}' bị từ chối")
        except N.NarrativeError:
            check(True, f"narrative '{what}' bị từ chối")


def email_case(md_path, tmp, extra_argv=(), note=None):
    """Gọi send_report_email.main() với SMTP giả — bắt thư, không gửi."""
    import smtplib
    import send_report_email as se
    sec = os.path.join(tmp, "smtp.json")
    json.dump({"from_email": "a@example.invalid", "app_password": "x", "to_email": "b@example.invalid"}, open(sec, "w"))
    se.SECRETS_PATH = sec
    sent = []

    class Fake:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def starttls(self): pass
        def login(self, *a): pass
        def sendmail(self, f, t, s): sent.append(s)

    real = smtplib.SMTP
    smtplib.SMTP = Fake
    argv = sys.argv
    try:
        sys.argv = ["send_report_email.py", md_path, "--skip-return-gate", "selfcheck — cổng §21 đã có selfcheck riêng",
                    *extra_argv]
        se.main()
    finally:
        smtplib.SMTP, sys.argv = real, argv
    check(len(sent) == 1, "email v2: đúng 1 thư (SMTP giả)")
    if not sent:
        return
    msg = email.message_from_string(sent[0])
    parts = list(msg.walk())
    html = [p for p in parts if p.get_content_type() == "text/html"]
    pdf = [p for p in parts if p.get_content_type() == "application/pdf"]
    imgs = [p for p in parts if p.get_content_maintype() == "image"]
    man, _ = al.load_v2(md_path)
    body = html[0].get_payload(decode=True).decode("utf-8") if html else ""
    check(bool(pdf) and pdf[0].get_filename() == man["pdf"], "email v2: PDF đính kèm đúng tên")
    check({p["Content-ID"].strip("<>") for p in imgs} == set(man["cid"]), "email v2: đủ ảnh cid như manifest")
    check(all(f'cid:{c}' in body for c in man["cid"]), "email v2: thân HTML tham chiếu mọi cid")
    check(al.MANIFEST_TAG not in body, "email v2: dòng manifest không lọt vào thân")
    # r3 N9: .md đính kèm không chứa comment manifest (đường dẫn nội bộ); SpaceX không kèm .md
    mds = [p for p in parts if (p.get_filename() or "").endswith(".md")]
    tag = os.path.basename(md_path)
    if "SpaceX" in tag:
        check(not mds, f"email v2 {tag}: bản nhà đầu tư KHÔNG kèm .md (PDF là bản đầy đủ)")
    else:
        check(len(mds) == 1 and al.MANIFEST_TAG not in mds[0].get_payload(decode=True).decode("utf-8"),
              f"email v2 {tag}: .md đính kèm không chứa comment report_v2_manifest")
    if note:
        check(note in body, f"email v2 {tag}: ghi chú đính kèm ('{note}') có trong thân HTML")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default="2026-10")
    ap.add_argument("--accounts", default="SpaceX,ZaloPay")
    ap.add_argument("--cadences", default="monthly,weekly,daily")
    ap.add_argument("--week", default="2026-10-26_to_2026-10-30", help="fixture tuần (29/10 rút bod ⇒ −0,30%%)")
    ap.add_argument("--day", default="2026-10-30")
    ap.add_argument("--quarter", default="2026-Q3", help="chỉ chạy khi --cadences có quarterly")
    ap.add_argument("--keep", help="giữ thư mục dựng ở đây (mặc định: tmp, xoá)")
    a = ap.parse_args()
    tmp = a.keep or tempfile.mkdtemp(prefix="report_v2_sc_")
    os.makedirs(tmp, exist_ok=True)
    print(f"report_v2_selfcheck: period={a.period} TZ={os.environ.get('TZ', '<unset>')} tmp={tmp}")
    narrative_cases()
    write_order_case(tmp)
    digests = {}
    import calendar
    y, m = map(int, a.period.split("-"))
    m_end = f"{y:04d}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}"
    # (cadence, period CLI, stem-period, ngày cuối kỳ cho nav_period_returns)
    jobs = {"monthly": (a.period, a.period, m_end),
            "weekly": (a.week, a.week, a.week.split("_to_")[1]),
            "daily": (a.day, a.day, a.day),
            "quarterly": (a.quarter, a.quarter, {"1": "03-31", "2": "06-30", "3": "09-30", "4": "12-31"}[a.quarter[-1]].join([a.quarter[:4] + "-", ""]))}
    for acct in a.accounts.split(","):
        for cad in a.cadences.split(","):
            per, stem_per, end = jobs[cad]
            out = os.path.join(tmp, acct, cad)
            rc1 = build(acct, per, out, cad)
            h1 = md5_tree(out)
            rc2 = build(acct, per, out, cad)
            h2 = md5_tree(out)
            check(rc1 == 0 and rc2 == 0, f"{acct} {cad} {per} dựng rc=0 cả 2 lần")
            check(h1 == h2 and bool(h1), f"{acct} {cad} 2 lần dựng cùng md5 ({len(h1)} file)")
            if h1 != h2:
                print("    khác:", sorted(k for k in h1 if h1.get(k) != h2.get(k))[:8])
            md_path = os.path.join(out, f"{acct}_{cad}_report_{stem_per}.md")
            if not os.path.exists(md_path):
                check(False, f"{acct} {cad} có .md tóm tắt")
                continue
            digests[f"{acct}_{cad}"] = hashlib.md5(open(md_path, "rb").read()).hexdigest()
            man, d = al.load_v2(md_path)
            nums = man["numbers"]
            c = canon(acct, end)
            if c is None:
                check(False, f"{acct} {cad} đọc được nav_period_returns")
            else:
                for k in [k for k in ("mtd", "inception") if f"{k}_pct" in nums]:
                    got = (c.get(k) or {}).get("return_pct")
                    check(got is not None and abs(got - nums[f"{k}_pct"]) < 1e-9,
                          f"{acct} {cad} {k} manifest {nums[f'{k}_pct']} == nav_period_returns {got}")
                if cad == "daily":
                    got = (c.get("day") or {}).get("return_pct")
                    check(got is not None and abs(got - nums["day_pct"]) < 1e-9, f"{acct} daily phiên {nums['day_pct']} == {got}")
                if cad == "quarterly":
                    led_q = c.get("inception") if a.quarter == "2026-Q3" else None   # quý khởi điểm: quý = từ đầu
                    check(led_q is None or abs(led_q["return_pct"] - nums["qtd_pct"]) < 1e-9,
                          f"{acct} quarterly {a.quarter} {nums['qtd_pct']} == từ đầu tới cuối quý {led_q and led_q['return_pct']}")
                if cad == "weekly" and acct == "SpaceX" and a.week == "2026-10-26_to_2026-10-30":
                    # fixture: khoản rút 29/10 là `bod` ⇒ số chuẩn pipeline −0,30% (không phải −0,29%)
                    check(["29/10", "−0,30%"] in man.get("daily_rows", []), f"SpaceX tuần 26-30/10: dòng 29/10 = −0,30% ({man.get('daily_rows')})")
                if cad == "weekly":
                    got = (c.get("wtd") or {}).get("return_pct")
                    check(got is not None and abs(got - nums["wtd_pct"]) < 1e-9, f"{acct} weekly tuần {nums['wtd_pct']} == {got}")
            rec = man.get("recon") or []
            bridge = [r for r in rec if r[0].startswith("Cầu NAV")]
            check(len(bridge) == 1 and abs(bridge[0][3]) < 0.5, f"{acct} {cad} đối soát cầu NAV lệch 0 ({bridge})")
            # dòng tham khảo: CTCK định giá mã UPCOM/HNX theo giá khác giá đóng cửa sàn (đo 30/09: DRI, SCL, TV1)
            mtm = [r for r in rec if "tham khảo" in r[0]]
            check(all(abs(r[3]) < 0.001 * nums["nav1"] for r in mtm), f"{acct} {cad} chênh định giá tham khảo < 0,1% NAV ({[(r[0][:30], r[3]) for r in mtm]})")
            check(man["pages"] <= man["page_cap"], f"{acct} {cad} {man['pages']} trang ≤ trần {man['page_cap']}")
            probs = al.lint_v2(md_path, investor_facing=(acct == "SpaceX"))
            check(not probs, f"{acct} {cad} artifact lint sạch trên bản dựng ({probs[:2]})")
            if cad == "monthly":
                mutations(md_path, acct, tmp)
                promote_cases(md_path, acct, tmp)
                email_case(md_path, tmp)
            if cad == "daily":
                daily_return_gate_case(md_path, acct, tmp)
                email_case(md_path, tmp, ("--attach-note", "Ghi chú selfcheck N9"), note="Ghi chú selfcheck N9")
    print("md5 .md:", json.dumps(digests))
    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{'✅ PASS' if not FAILS else '❌ FAIL'} report_v2_selfcheck ({len(FAILS)} lỗi)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
