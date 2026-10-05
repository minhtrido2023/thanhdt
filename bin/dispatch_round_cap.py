#!/usr/bin/env python3
"""dispatch_round_cap.py — CẦU CHÌ VÒNG POLISH bằng CODE (dispatch.sh exit 7).

VẤN ĐỀ. Luật "cầu chì vòng 3" (kb/mike_model_routing.md § "Hai chế độ theo ĐỘ KHÓ + cầu chì",
skill dispatch-routing §3) là văn xuôi + lời nhắc stderr (dispatch_loop_hint.py) ⇒ vẫn bị vượt:
chuỗi feat/broker-primary-20261003 đi r1→r4 trong 10-03/10-04 (Taylor_20261003_162814,
_20261004_024239, _103554, _120510). Bus question
Mike/retro-pattern-recurring-polish-chain-review-rounds-cost — user duyệt phương án 1 (2026-10-05).

ĐỊNH NGHĨA CHUỖI = dispatch_loop_hint.py (import, không định nghĩa lại): token nhánh
`fix|feat|wire|session/<tên>` hoặc `wt-<tên>` trong prompt; "vòng trước" = job trong bus/jobs
≤24h có token đó (field `chain_tokens` từ prompt ĐẦY ĐỦ, record cũ thì `prompt_summary`), bỏ job
cancelled / [RESUME / [FALLBACK, gộp dispatch cách nhau <5 phút thành 1 vòng. THÊM MỘT ràng buộc
so với lời nhắc: chỉ đếm job tới CÙNG agent (--to). Lý do đo thật: retro tự động hằng ngày
(DISPATCH_FROM=user, gửi Mike/Wags) có NHẮC tên nhánh trong prompt — không ràng buộc agent thì
retro vừa bị tính thành vòng của chuỗi Taylor vừa có thể bị CHẶN khi nhánh đó đang nóng.

LUẬT. Đã có ≥ DISPATCH_ROUND_CAP_PRIOR (mặc định 3) vòng trước ⇒ đây là vòng ≥4 ⇒ CHẶN CỨNG
(exit 7). Prompt bắt đầu bằng [RESUME / [FALLBACK (tự sinh, tiếp nối job ĐÃ được nhận) ⇒ miễn.

OVERRIDE — CHỈ phiên tương tác của Mike hoặc user dùng, KHÔNG BAO GIỜ agent headless:
  DISPATCH_ROUND_CAP_OVERRIDE=1 bin/dispatch.sh ...   (lý do tuỳ chọn: DISPATCH_ROUND_CAP_REASON)
Chốt cơ học: caller đang chạy BÊN TRONG một job dispatch (env JOB_ID kế thừa khác rỗng — dispatch.sh
export JOB_ID cho mọi agent headless) ⇒ override BỊ TỪ CHỐI, vẫn chặn. dispatch.sh unset biến
override ngay sau khi gọi script này ⇒ không rò xuống agent con. Mỗi lần override/chặn ghi 1 dòng
TSV vào logs/dispatch_round_cap.log (retro đo: số vòng override/ngày) + field `round_cap` trên job.

FAIL-OPEN CÓ ĐIỀU KIỆN. Không đọc được thư mục job / lỗi bất ngờ ⇒ IN CẢNH BÁO, exit 0 (chặn nhầm
1 dispatch thật tệ hơn bỏ lọt 1 vòng — và lời nhắc của dispatch_loop_hint vẫn còn). Prompt không
có token nhánh ⇒ không phải chuỗi polish ⇒ cho qua im lặng (ca thường của mọi dispatch cron).
Nhưng ĐÃ nhận ra chuỗi và đếm ≥ ngưỡng ⇒ chặn cứng, không ngoại lệ nào khác ngoài override.

GIAO KÈO stdout (dispatch.sh đọc): đúng 1 dòng `<chain_tokens>\t<round_cap_note>` (có thể rỗng).
Thông báo cho người đi stderr.

  echo "<prompt>" | dispatch_round_cap.py check --to <agent> [--from <caller>]
  dispatch_round_cap.py replay --days 30 [--jobs-dir D ...]   # đo lại trên dữ liệu thật
Selfcheck: python3 bin/dispatch_round_cap_selfcheck.py
"""
import argparse
import datetime
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dispatch_loop_hint as H  # noqa: E402  — MỘT định nghĩa chuỗi duy nhất

ROOT = H.ROOT
BLOCK_RC = 7
_ICT = datetime.timezone(datetime.timedelta(hours=7))
_AUTO_PREFIX = ("[RESUME", "[FALLBACK")


def cap_prior():
    try:
        return max(1, int(os.environ.get("DISPATCH_ROUND_CAP_PRIOR", "3")))
    except ValueError:
        return 3


def _ict(t):
    return datetime.datetime.fromtimestamp(t, _ICT).strftime("%d/%m %H:%M ICT")


def evaluate(prompt, now=None, jobs_dir=None, cap=None, mtime_prefilter=True, agent=None):
    """→ (verdict, tokens, worst_token, rounds, round_no). verdict ∈ exempt|nochain|ok|block.
    Ném OSError khi không đọc được thư mục job (caller fail-open)."""
    cap = cap or cap_prior()
    tokens = H.branch_tokens(prompt)
    if prompt.lstrip().startswith(_AUTO_PREFIX):
        return "exempt", tokens, None, [], 0
    if not tokens:
        return "nochain", tokens, None, [], 0
    pj = H.prior_jobs(tokens, now=now, jobs_dir=jobs_dir, mtime_prefilter=mtime_prefilter,
                      agent=agent or None)
    worst, rounds = None, []
    for t in tokens:
        r = H.dedup_rounds(pj[t])
        if worst is None or len(r) > len(rounds):
            worst, rounds = t, r
    # Dispatch hiện tại cách vòng cuối <DEDUP_S ⇒ là BẢN ĐÚP của vòng đó (cùng luật gộp), không
    # phải vòng mới — re-dispatch ngay sau 1 lần gõ hỏng không bị tính thêm vòng.
    now = now or time.time()
    round_no = len(rounds) if rounds and now - rounds[-1][-1][0] < H.DEDUP_S else len(rounds) + 1
    return ("block" if round_no > cap else "ok"), tokens, worst, rounds, round_no


def _audit(event, to, frm, token, rounds, reason=""):
    path = os.environ.get("MIKE_DISPATCH_ROUND_CAP_LOG") or os.path.join(ROOT, "logs", "dispatch_round_cap.log")
    jobs = ",".join(r[0][1] for r in rounds)
    line = "\t".join([datetime.datetime.now(_ICT).isoformat(timespec="seconds"), event, f"to={to}",
                      f"from={frm}", f"chain={token}", f"prior_rounds={len(rounds)}", f"jobs={jobs}",
                      f"reason={reason}"])
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as fh:
            fh.write(line.replace("\n", " ") + "\n")
        return True
    except OSError as e:
        print(f"WARN round-cap: KHÔNG ghi được audit {path}: {e}", file=sys.stderr)
        return False


def cmd_check(a):
    prompt = sys.stdin.read()
    frm = a.frm or os.environ.get("DISPATCH_FROM") or "Mike"
    try:
        verdict, tokens, tok, rounds, rno = evaluate(prompt, jobs_dir=a.jobs_dir, agent=a.to)
    except Exception as e:  # fail-open: không đọc được records ⇒ KHÔNG chặn, nhưng nói to
        print(f"WARN round-cap: không đếm được vòng ({type(e).__name__}: {e}) — FAIL-OPEN, "
              f"dispatch vẫn chạy. Cầu chì vòng KHÔNG được kiểm cho lần này.", file=sys.stderr)
        try:
            toks = ",".join(H.branch_tokens(prompt))
        except Exception:
            toks = ""
        print(f"{toks}\tfailopen")
        _audit("failopen", a.to, frm, "", [], reason=f"{type(e).__name__}: {e}")
        return 0
    toks = ",".join(tokens)
    if verdict != "block":
        print(f"{toks}\t")
        return 0
    ov = os.environ.get("DISPATCH_ROUND_CAP_OVERRIDE", "")
    reason = os.environ.get("DISPATCH_ROUND_CAP_REASON", "")
    inherited_job = os.environ.get("JOB_ID", "")
    n = len(rounds)
    if ov == "1" and not inherited_job:
        print(f"NOTE round-cap: OVERRIDE vòng {rno} trên '{tok}' ({n} vòng trước) — đã ghi audit.",
              file=sys.stderr)
        _audit("override", a.to, frm, tok, rounds, reason)
        print(f"{toks}\toverride:{tok}:{rno}")
        return 0
    print(f"ERROR: dispatch bị CHẶN — cầu chì vòng polish: chuỗi '{tok}' đã có {n} vòng trong 24h,",
          file=sys.stderr)
    print(f"   đây sẽ là vòng {rno} (ngưỡng: chặn từ vòng {cap_prior() + 1}). Các vòng trước:", file=sys.stderr)
    for r in rounds:
        extra = f" (+{len(r) - 1} bản đúp <5')" if len(r) > 1 else ""
        print(f"     - {r[0][1]}  {_ict(r[0][0])}{extra}", file=sys.stderr)
    print("   Cách xử lý (kb/mike_model_routing.md § cầu chì, skill dispatch-routing §3):", file=sys.stderr)
    print("   (1) DỪNG vá cuốn chiếu; chuyển CHẾ ĐỘ B — Opus high review TOÀN BỘ nhánh rồi sửa MỘT lượt —", file=sys.stderr)
    print("       nhưng vòng này vẫn cần USER DUYỆT; hoặc (2) user đã duyệt ⇒ phiên tương tác chạy lại với", file=sys.stderr)
    print("       DISPATCH_ROUND_CAP_OVERRIDE=1 [DISPATCH_ROUND_CAP_REASON=\"user duyệt <giờ>\"] bin/dispatch.sh ...", file=sys.stderr)
    if ov == "1" and inherited_job:
        print(f"   OVERRIDE BỊ TỪ CHỐI: caller đang chạy trong job dispatch '{inherited_job}' (headless) —",
              file=sys.stderr)
        print("   chỉ phiên tương tác của Mike/user được override. Escalate bằng event `question`.", file=sys.stderr)
        _audit("override_refused", a.to, frm, tok, rounds, f"inherited JOB_ID={inherited_job}")
    else:
        _audit("block", a.to, frm, tok, rounds)
    print(f"{toks}\tblock:{tok}:{rno}")
    return BLOCK_RC


def _load_all(dirs):
    rows = []
    for d in dirs:
        for f in glob.glob(os.path.join(d, "*.json")):
            try:
                rows.append(json.load(open(f)))
            except Exception:
                continue
    return rows


def cmd_replay(a):
    """Mô phỏng: mỗi dispatch trong `--days` ngày, đếm vòng trên các job TRƯỚC nó (cùng định nghĩa)."""
    import shutil
    import tempfile
    dirs = a.jobs_dir_list or [os.path.join(ROOT, "bus", "jobs"), os.path.join(ROOT, "bus", "jobs", "archive")]
    rows = _load_all(dirs)
    now = time.time()
    # Gộp vào 1 thư mục tạm để prior_jobs đọc đúng 1 nguồn (archive + hot).
    tmp = tempfile.mkdtemp(prefix="roundcap_replay_")
    try:
        for d in rows:
            jid = d.get("job_id")
            if jid:
                with open(os.path.join(tmp, f"{jid}.json"), "w") as fh:
                    json.dump(d, fh)
        cand = [d for d in rows if d.get("job_id") and now - H.dispatch_time(d) <= a.days * 86400]
        cand.sort(key=H.dispatch_time)
        hits, n_chain = [], 0
        for d in cand:
            prompt = d.get("prompt_summary", "") or ""
            if d.get("chain_tokens"):   # nối SAU để tiền tố [RESUME/[FALLBACK vẫn ở đầu
                prompt = prompt + " " + " ".join(str(d["chain_tokens"]).split(","))
            t = H.dispatch_time(d)
            v, toks, tok, rounds, rno = evaluate(prompt, now=t - 1, jobs_dir=tmp, mtime_prefilter=False,
                                               agent=d.get("to"))
            if toks and v != "exempt":
                n_chain += 1
            if v == "block":
                hits.append((d, tok, rounds, rno))
        if a.verbose:
            for d in cand:
                pr = d.get("prompt_summary", "") or ""
                toks = H.branch_tokens(pr + " " + " ".join(str(d.get("chain_tokens") or "").split(",")))
                if toks:
                    print(f"CHAIN {d['job_id']}  from={d.get('from')}  {toks}  | {pr[:70]}")
        print(f"replay {a.days} ngày: {len(cand)} dispatch, {n_chain} có token chuỗi, "
              f"{len(hits)} sẽ bị CHẶN (ngưỡng {cap_prior()} vòng trước)")
        for d, tok, rounds, rno in hits:
            print(f"BLOCK {d['job_id']}  from={d.get('from')}  chain={tok}  vòng={rno}  "
                  f"trước={','.join(r[0][1] for r in rounds)}")
            print(f"      {(d.get('prompt_summary') or '')[:110]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--to", default="")
    c.add_argument("--from", dest="frm", default="")
    c.add_argument("--jobs-dir", default=None)
    r = sub.add_parser("replay")
    r.add_argument("--days", type=int, default=30)
    r.add_argument("--jobs-dir", dest="jobs_dir_list", action="append")
    r.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    if a.cmd == "check":
        try:
            return cmd_check(a)
        except Exception as e:  # lưới cuối: lỗi ngoài evaluate cũng fail-open
            print(f"WARN round-cap: lỗi bất ngờ ({type(e).__name__}: {e}) — FAIL-OPEN.", file=sys.stderr)
            print("\tfailopen")
            return 0
    return cmd_replay(a)


if __name__ == "__main__":
    sys.exit(main())
