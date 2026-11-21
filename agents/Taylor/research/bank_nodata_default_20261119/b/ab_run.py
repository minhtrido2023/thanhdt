"""A/B: chay main() cua rating_8l_history ban HEAD (d0a14445e) va ban worktree (phuong an B) tren CUNG du lieu BQ
(cache 1 lan, bq() memo) -> /tmp, KHONG refresh BQ, KHONG ghi canonical. So byte tung dong."""
import os, sys, importlib.util, hashlib, pickle
os.environ["R8L_HIST_NO_BQ_REFRESH"] = "1"; os.environ["MIKE_BOT_TEST_MODE"] = "1"
B = os.path.dirname(os.path.abspath(__file__)); T = os.environ.get("AB_TMP", "/tmp/taylor_bnd_ab"); os.makedirs(T, exist_ok=True)
WT = "/home/trido/thanhdt/WorkingClaude/wt-bank-nodata-20261119/WorkingClaude"
sys.path.insert(0, WT)
cache = os.path.join(T, "bq_cache.pkl"); memo = pickle.load(open(cache, "rb")) if os.path.exists(cache) else {}
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    real = m.bq
    def bq(sql):
        k = hashlib.md5(sql.encode()).hexdigest()
        if k not in memo: memo[k] = real(sql); pickle.dump(memo, open(cache, "wb"))
        return memo[k].copy()
    m.bq = bq; return m
for tag, path in (("old", os.path.join(B, "rating_8l_history_HEAD.py")), ("new", os.path.join(WT, "rating_8l_history.py"))):
    os.environ["R8L_HIST_OUT"] = os.path.join(T, f"hist_{tag}.csv")
    print(f"===== {tag} =====", flush=True); load(f"h_{tag}", path).main()
