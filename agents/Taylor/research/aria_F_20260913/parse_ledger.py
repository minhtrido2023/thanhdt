"""Parse muc 'V. Sao ke chung khoan - tien' trong bao cao thang DNSE (PDF->text pypdf layout)
thanh ledger CSV, kiem bang chuoi so du (prev +/- amt == bal). In dong khong khop."""
import re, sys, glob, os, csv
DATE = re.compile(r"^\s*(\d{2}/\d{2}/\d{4})\s{2,}(.*)$")
def num(t): return int(t.replace(",", ""))
ISNUM = re.compile(r"^-?[\d,]+$")
def parse(path):
    lines = open(path).read().splitlines()
    try:
        i0 = next(i for i, l in enumerate(lines) if "Sao kê chứng khoán - tiền" in l)
    except StopIteration:
        return None, "no ledger"
    rows, prev, bad = [], None, 0
    open_bal = close_bal = None
    cur = None
    for l in lines[i0:]:
        if "Số dư đầu kỳ" in l:
            prev = num(l.split()[-1]); open_bal = prev; continue
        if "Số dư cuối kỳ" in l:
            close_bal = num(l.split()[-1]); break
        m = DATE.match(l)
        if not m:
            if cur is not None and l.strip() and not l.strip().startswith("Ngày") :
                cur["desc"] += " " + re.split(r"\s{2,}", l.strip())[0]
            continue
        toks = re.split(r"\s{2,}", m.group(2).strip())
        desc = toks[0]; rest = toks[1:]
        tk = None; nums = []
        for t in rest:
            if ISNUM.match(t): nums.append(num(t))
            elif re.match(r"^[A-Z][A-Z0-9]{2,}$", t): tk = t
            else: desc += " " + t
        inc = dec = 0
        if tk and re.match(r"^(Mua|Bán)\s", desc):
            qty = nums[0] if nums else 0
            bal = nums[1] if len(nums) > 1 else prev
            ok = bal == prev
        else:
            if len(nums) == 2: amt, bal = nums
            elif len(nums) == 1: amt, bal = nums[0], 0
            else: amt, bal = 0, prev
            if prev + amt == bal: inc = amt
            elif prev - amt == bal: dec = amt
            ok = (inc or dec or amt == 0)
            qty = None
        if not ok:
            bad += 1; print("MISMATCH", os.path.basename(path), m.group(1), desc, tk, nums, "prev", prev)
            bal = prev + 0
        cur = {"date": m.group(1), "desc": desc, "ticker": tk or "", "qty": qty, "inc": inc, "dec": dec, "bal": bal}
        rows.append(cur); prev = bal
    return rows, dict(open=open_bal, close=close_bal, last=prev, bad=bad)
if __name__ == "__main__":
    for f in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "statements", "*.txt"))):
        rows, info = parse(f)
        print(os.path.basename(f), info if rows is None else {**info, "n": len(rows), "chain_ok": info["last"] == info["close"]})
        if rows:
            with open(f[:-4] + "_ledger.csv", "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
