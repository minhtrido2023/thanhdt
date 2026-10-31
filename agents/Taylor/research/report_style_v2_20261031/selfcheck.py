"""Tự kiểm mock v2: chạy 3 mock HAI lần → so text PDF + CSV số liệu; lint markdown thô / repr tuple /
tên nội bộ; font nhúng; HTML email; trần trang. Ghi SELFCHECK.json.
  source /home/trido/thanhdt/WorkingClaude/wc_env.sh && python3 selfcheck.py
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_report_v2 as R  # noqa: E402

MOCKS = {"weekly": ("SpaceX_weekly_26-30_10_v2", 4 + 1), "daily": ("SpaceX_daily_2026-10-30_v2", 1),
         "quarterly": ("SpaceX_quarterly_Q3_2026_v2", 8)}
INTERNAL = r"nav_period|nav_history|\.py\b|bin/|Livermore|Taylor|Mike\b|Bobby|Mafee|DT5G|\bLAG\b|PARK|custom30|SIGNAL_V11|PEAD|skeptic|eod_trading"


def snapshot():
    out = {}
    for m, (stem, _) in MOCKS.items():
        out[m + ".pdf_text"] = hashlib.md5("\f".join(R.pdf_text(f"{HERE}/out/{stem}.pdf")).encode()).hexdigest()
    for f in sorted(glob.glob(f"{HERE}/figs/*.csv") + glob.glob(f"{HERE}/recon/*.csv")):
        out[os.path.relpath(f, HERE)] = hashlib.md5(open(f, "rb").read()).hexdigest()
    return out


def run_all():
    for m in MOCKS:
        r = subprocess.run([sys.executable, f"{HERE}/mock_{m}.py"], cwd=HERE, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f"mock_{m} rc={r.returncode}\n{r.stdout[-800:]}\n{r.stderr[-800:]}")


def main():
    run_all(); a = snapshot()
    run_all(); b = snapshot()
    res = {"rerun_identical": a == b, "rerun_diff": [k for k in a if a.get(k) != b.get(k)], "mocks": {}}
    ok = res["rerun_identical"]
    for m, (stem, cap) in MOCKS.items():
        pdf = f"{HERE}/out/{stem}.pdf"
        lint = R.lint_pdf(pdf)
        text = "\n".join(R.pdf_text(pdf))
        internal = sorted(set(re.findall(INTERNAL, text)))
        html = open(f"{HERE}/out/{stem}_email.html", encoding="utf-8").read()
        imgs = re.findall(r"<img [^>]*>", html)
        bad_img = [i for i in imgs if not re.fullmatch(r'<img src="cid:[a-z0-9]+" alt="[^"<>]*"( style="[^"]*")?/>', i)]
        cids = json.load(open(f"{HERE}/out/{stem}_email_cid.json"))
        missing = [p for p in cids.values() if not os.path.exists(p)]
        meta = json.load(open(f"{HERE}/recon/{m}_meta.json"))
        r = {"pages": lint["pages"], "page_cap": cap, "raw_markdown_hits": lint["raw_markdown_hits"],
             "fonts": lint["fonts"], "non_bvp_fonts": lint["non_bvp_fonts"], "internal_names": internal,
             "email_imgs": len(imgs), "email_bad_img_tags": bad_img, "email_missing_files": missing,
             "html_tuple_repr": "['|" in html, "recon_items": meta["recon_items"], "recon_bad": meta["recon_bad"]}
        r["pass"] = (r["pages"] <= cap and not r["raw_markdown_hits"] and not r["non_bvp_fonts"] and not internal
                     and not bad_img and not missing and not r["html_tuple_repr"] and meta["recon_bad"] == 0)
        ok &= r["pass"]
        res["mocks"][m] = r
    res["pass"] = ok
    json.dump(res, open(f"{HERE}/SELFCHECK.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
