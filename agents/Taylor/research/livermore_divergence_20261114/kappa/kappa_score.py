"""Chấm κ lặp lại (G0, kế hoạch §8). Đầu vào: runs/run1.csv, run2.csv, run3.csv — mỗi file 20 dòng
`label,H20_DIR,H20_P_UP,RECOGNIZED` (H20_DIR ∈ UP/DOWN, H20_P_UP ∈ [0,1], RECOGNIZED true/false).
  python kappa_score.py            # chỉ đồng thuận (KHÔNG mở truth) — đủ để quyết G0
  python kappa_score.py --unseal   # thêm hit/Brier mô tả (N=20, KHÔNG dùng để kết luận năng lực)
  python kappa_score.py --selftest # kiểm công thức κ trên dữ liệu tổng hợp
Ngưỡng G0: Fleiss κ(H20_DIR) < 0,4 ⇒ đầu ra là nhiễu lấy mẫu ⇒ bắt buộc ensemble (e) ở mọi pha sau, hoặc dừng."""
import csv, hashlib, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
TRUTH_MD5 = open(f"{HERE}/SEALED_truth.md5").read().split()[0] if os.path.exists(f"{HERE}/SEALED_truth.md5") else None


def fleiss(M):
    """M: n_items × n_cat số rater chọn mỗi loại (tổng mỗi hàng = r)."""
    M = np.asarray(M, float); n, r = M.shape[0], M[0].sum()
    pj = M.sum(0) / (n * r); Pi = ((M ** 2).sum(1) - r) / (r * (r - 1))
    Pbar, Pe = Pi.mean(), (pj ** 2).sum()
    return float("nan") if Pe >= 1 else (Pbar - Pe) / (1 - Pe)


def cohen(a, b):
    a, b = np.asarray(a), np.asarray(b); po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return float("nan") if pe >= 1 else (po - pe) / (1 - pe)


def load(r):
    rows = list(csv.DictReader(open(f"{HERE}/runs/run{r}.csv")))
    d = {x["label"].strip(): x for x in rows}
    assert len(d) == 20 == len(rows), f"run{r}: cần đúng 20 nhãn duy nhất, có {len(d)}/{len(rows)}"
    for x in d.values():
        assert x["H20_DIR"].strip() in ("UP", "DOWN"), x; assert 0 <= float(x["H20_P_UP"]) <= 1, x
    return d


def main(unseal):
    runs = [load(r) for r in (1, 2, 3)]; labels = sorted(runs[0])
    assert all(sorted(R) == labels for R in runs), "3 lần đọc phải cùng tập nhãn"
    D = np.array([[1 if R[l]["H20_DIR"].strip() == "UP" else 0 for l in labels] for R in runs])   # 3 × 20
    P = np.array([[float(R[l]["H20_P_UP"]) for l in labels] for R in runs])
    REC = np.array([[R[l]["RECOGNIZED"].strip().lower() == "true" for l in labels] for R in runs])
    M = np.column_stack([D.sum(0), 3 - D.sum(0)])
    kf = fleiss(M); pair = {f"{i+1}v{j+1}": cohen(D[i], D[j]) for i in range(3) for j in range(i + 1, 3)}
    unanimous = (D.sum(0) % 3 == 0)
    pm = P.mean(0); sdp = P.std(0, ddof=1)
    publish = unanimous & (np.abs(pm - 0.5) >= 0.08)
    out = dict(N_cases=20, runs=3, fleiss_kappa_DIR=round(kf, 4), cohen_pairwise=pair,
               unanimous_frac=float(unanimous.mean()), share_UP_calls=float(D.mean()),
               p_up_mean=float(P.mean()), p_up_sd_overall=float(P.std(ddof=1)), per_case_sd_p_mean=float(sdp.mean()),
               per_case_sd_p_max=float(sdp.max()), sign_consistent_p_vs_dir=float(((P > 0.5) == (D == 1)).mean()),
               ensemble_e_publish=int(publish.sum()), ensemble_e_abstain_rate=float(1 - publish.mean()),
               recognized_any=int(REC.any(0).sum()),
               G0_kappa_lt_0_4=bool(not (kf >= 0.4)),
               G0_note="κ<0,4 (hoặc NaN do mọi call cùng một phía) ⇒ bắt buộc ensemble (e) hoặc dừng; abstain>70% ⇒ vai không dùng được")
    if unseal:
        raw = open(f"{HERE}/SEALED_truth.json", "rb").read()
        if TRUTH_MD5: assert hashlib.md5(raw).hexdigest() == TRUTH_MD5, "SEALED_truth.json đã bị sửa (md5 lệch)"
        T = {t["label"]: t for t in json.loads(raw)}; up = np.array([T[l]["up"] for l in labels])
        maj = (D.sum(0) >= 2).astype(int)
        out["unsealed"] = dict(base_rate_up=float(up.mean()), hit_per_run=[int((D[i] == up).sum()) for i in range(3)],
                               hit_majority=int((maj == up).sum()), brier_per_run=[float(((P[i] - up) ** 2).mean()) for i in range(3)],
                               brier_mean_p=float(((pm - up) ** 2).mean()), always_up_hit=int(up.sum()),
                               mom20_hit=int(sum((T[l]["mom20"] > 0) == bool(T[l]["up"]) for l in labels)),
                               ensemble_hit=f"{int((maj[publish] == up[publish]).sum())}/{int(publish.sum())}",
                               hit_VNINDEX=f"{int(sum(maj[k] == up[k] for k, l in enumerate(labels) if T[l]['kind'] == 'VNINDEX'))}/5",
                               note="N=20: CHỈ mô tả; năng lực đo ở P2 (N≥150)")
    json.dump(out, open(f"{HERE}/kappa_result.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False))


def selftest():
    same = np.array([[3, 0]] * 10 + [[0, 3]] * 10); assert abs(fleiss(same) - 1) < 1e-12
    # ví dụ Fleiss gốc thu nhỏ: hàng nào cũng 2-1 ⇒ Pi = 1/3, pj = .5 ⇒ κ = (1/3-.5)/.5 = -1/3
    mix = np.array([[2, 1]] * 10 + [[1, 2]] * 10); assert abs(fleiss(mix) + 1 / 3) < 1e-12
    assert abs(cohen([1, 1, 0, 0], [1, 1, 0, 0]) - 1) < 1e-12 and abs(cohen([1, 0, 1, 0], [0, 1, 0, 1]) + 1) < 1e-12
    allup = np.array([[3, 0]] * 20); assert np.isnan(fleiss(allup))
    print("selftest PASS")


if __name__ == "__main__":
    if "--selftest" in sys.argv: selftest()
    else: main("--unseal" in sys.argv)
