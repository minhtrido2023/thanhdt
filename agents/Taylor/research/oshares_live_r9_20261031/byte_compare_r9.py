import pickle, sys
a, b = pickle.load(open(sys.argv[1], "rb")), pickle.load(open(sys.argv[2], "rb"))
diff = [k for k in a if a[k] != b.get(k)]
print("n_main", len(a), "n_branch", len(b), "keys_equal", set(a) == set(b), "diff_repr", len(diff), diff[:5])
import collections
print("by_kind", dict(collections.Counter(k[0] for k in a)), "by_asof", dict(collections.Counter(k[1] for k in a if k[0] == "fv")))
