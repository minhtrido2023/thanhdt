#!/usr/bin/env python3
"""Benchmark srcwalk vs grep trên 2 tác vụ, chấm bằng ground truth AST (gt_*.json).

Tác vụ 1 — TÌM ĐỊNH NGHĨA:  srcwalk discover X --scope .   vs  grep -rnE "^(def|class) X\\b"
Tác vụ 2 — TÌM CALL SITE :  srcwalk trace callers X -d 1   vs  grep -rnE "\\bX\\s*\\("

Chấm 2 mức: exact (file,line) và file-level (tập file). Nếu 2 mức lệch nhau nhiều -> bản thân
điều đó là phát hiện về chất lượng quy kết dòng.
"""
import json, os, random, re, subprocess, sys, time

ROOT = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
SEED = 20260803


def sh(cmd):
    t0 = time.perf_counter()
    p = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
    return p.stdout, time.perf_counter() - t0


def norm(path):
    return os.path.normpath(path.lstrip("./"))


# ---------- parsers ----------
CALLSITE_RE = re.compile(r"^\s*\[[^\]]+\]\s+\S+\s+(?P<path>[^\s:]+):(?P<line>\d+)")
BFS_RE = re.compile(r"^\s+\S+\s+(?P<path>[^\s:]+):(?P<line>\d+)\s+→")
DEF_RE = re.compile(r"^\s*\[(?P<kind>fn|class|struct|enum|method)\]\s+(?P<name>\S+)\s+(?P<path>[^\s:]+):(?P<line>\d+)")


def parse_sw_callers(out):
    """Chỉ lấy call site TRỰC TIẾP; bỏ khối 'impact (2nd hop)' và hop>=2."""
    hits, mode = set(), None
    for ln in out.splitlines():
        if ln.startswith("<- calls"):
            mode = "direct"; continue
        if "impact (2nd hop)" in ln or re.match(r"^──\s*hop [2-9]", ln.strip()):
            mode = None; continue
        if re.match(r"^──\s*hop 1", ln.strip()):
            mode = "bfs"; continue
        if ln.startswith("#") or not ln.strip():
            continue
        if mode == "direct":
            m = CALLSITE_RE.match(ln)
            if m:
                hits.add((norm(m.group("path")), int(m.group("line"))))
        elif mode == "bfs":
            m = BFS_RE.match(ln)
            if m:
                hits.add((norm(m.group("path")), int(m.group("line"))))
    return hits


def parse_sw_defs(out, name):
    hits = set()
    for ln in out.splitlines():
        m = DEF_RE.match(ln)
        if m and m.group("name") == name:
            hits.add((norm(m.group("path")), int(m.group("line"))))
    return hits


def parse_grep(out):
    hits = set()
    for ln in out.splitlines():
        parts = ln.split(":", 2)
        if len(parts) >= 2 and parts[1].isdigit():
            hits.add((norm(parts[0]), int(parts[1])))
    return hits


def score(pred, gt):
    tp = len(pred & gt)
    prec = tp / len(pred) if pred else (1.0 if not gt else 0.0)
    rec = tp / len(gt) if gt else 1.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return prec, rec, f1, tp


def main():
    gtc = json.load(open(os.path.join(HERE, "gt_callers.json")))
    names = sorted(gtc)
    random.seed(SEED)
    sample = random.sample(names, min(N, len(names)))

    rows = []
    for i, name in enumerate(sample, 1):
        g = gtc[name]
        gt_calls = {(norm(f), l) for f, l in g["callers"]}
        gt_defs = {(norm(g["def_file"]), g["def_line"])}

        # scope "cẩn thận" = thư mục top-level chứa định nghĩa (né bẫy gitignore)
        top = g["def_file"].split("/")[0]
        careful = top if "/" in g["def_file"] else "."

        # --- tác vụ 2: call sites ---
        sw_out, sw_t = sh(f"srcwalk trace callers {name} --scope . --depth 1")
        sw_hits = parse_sw_callers(sw_out)
        swc_out, swc_t = sh(f"srcwalk trace callers {name} --scope {careful} --depth 1")
        swc_hits = parse_sw_callers(swc_out)
        gp_out, gp_t = sh(
            rf"""grep -rnE "\b{name}\s*\(" --include='*.py' . | grep -vE ":[0-9]+:\s*(def|class)\s+{name}\b" """)
        gp_hits = parse_grep(gp_out)

        # --- tác vụ 1: definition ---
        swd_out, swd_t = sh(f"srcwalk discover {name} --scope . --as symbol")
        swd_hits = parse_sw_defs(swd_out, name)
        swdc_out, swdc_t = sh(f"srcwalk discover {name} --scope {careful} --as symbol")
        swdc_hits = parse_sw_defs(swdc_out, name)
        gpd_out, gpd_t = sh(
            rf"""grep -rnE "^\s*(def|class)\s+{name}\b" --include='*.py' .""")
        gpd_hits = parse_grep(gpd_out)

        # độ mơ hồ văn bản của cái TÊN (không phải call) — dùng để phân tầng hậu kiểm
        amb_out, _ = sh(rf"""grep -rcE "\b{name}\b" --include='*.py' . | grep -v ':0$' | wc -l""")
        try:
            amb_files = int(amb_out.strip())
        except ValueError:
            amb_files = -1

        r = {"name": name, "n_gt_calls": len(gt_calls), "amb_files": amb_files,
             "def_file": g["def_file"], "kind": g["kind"],
             "gitignored": subprocess.run(f"git check-ignore -q '{g['def_file']}'", shell=True,
                                          cwd=ROOT).returncode == 0}
        for tag, pred, gt, out, t in (
            ("sw_call", sw_hits, gt_calls, sw_out, sw_t),
            ("swc_call", swc_hits, gt_calls, swc_out, swc_t),
            ("gp_call", gp_hits, gt_calls, gp_out, gp_t),
            ("sw_def", swd_hits, gt_defs, swd_out, swd_t),
            ("swc_def", swdc_hits, gt_defs, swdc_out, swdc_t),
            ("gp_def", gpd_hits, gt_defs, gpd_out, gpd_t),
        ):
            p, rc, f1, tp = score(pred, gt)
            pf, rf, f1f, _ = score({x[0] for x in pred}, {x[0] for x in gt})
            r[tag] = {"prec": p, "rec": rc, "f1": f1, "tp": tp, "n_pred": len(pred),
                      "prec_file": pf, "rec_file": rf, "f1_file": f1f,
                      "tok": len(out) / 4, "sec": t}
        rows.append(r)
        if i % 20 == 0:
            print(f"  ...{i}/{len(sample)}", file=sys.stderr, flush=True)

    with open(os.path.join(HERE, "bench_rows.json"), "w") as fh:
        json.dump(rows, fh, indent=1)
    print(f"đã ghi bench_rows.json  N={len(rows)}")


if __name__ == "__main__":
    main()
