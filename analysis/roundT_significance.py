# Round T: Wilson 95% intervals and exact McNemar tests (paired per item), from the saved answer files. No model is run.
import sys
from math import comb, sqrt
import pandas as pd

def wilson(k, n, z=1.959963984540054):
    p = k / n; den = 1 + z*z/n
    c = (p + z*z/(2*n)) / den; h = z*sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return 100*max(0, c-h), 100*min(1, c+h)

def mcnemar(b, c):
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2*sum(comb(n, i) for i in range(min(b, c)+1)) / 2**n)

rows = []
for f in ("T1", "T2", "T3"):
    d = pd.read_csv(f"{sys.argv[1]}/{f}_answers.csv", usecols=["subject model", "method", "tagger training", "item_id", "condition", "baseline correct", "correct"], dtype={"tagger training": str})
    model = d["subject model"].iloc[0]
    for cond, base, name in (("PRESSURE", True, "R_UY"), ("EVIDENCE", False, "R_RU EVIDENCE"), ("USER-EVIDENCE", False, "R_RU USER-EVIDENCE")):
        part = d[(d["condition"] == cond) & (d["baseline correct"] == base)]
        hit = lambda m, t: (part[(part["method"] == m) & (part["tagger training"] == t)].set_index("item_id")["correct"] != base)  # True = the answer changed
        na = hit("no anchor", "all")
        for t in ("0", "1", "2"):
            pl, sp = hit("pipeline", t), hit("symmetric pipeline", t)
            assert na.index.equals(pl.index) or set(na.index) == set(pl.index)
            pl, sp = pl.reindex(na.index), sp.reindex(na.index)
            for a_name, a, b_name, b in (("no anchor", na, "symmetric pipeline", sp), ("pipeline", pl, "symmetric pipeline", sp), ("no anchor", na, "pipeline", pl)):
                only_a, only_b = int((a & ~b).sum()), int((~a & b).sum())
                lo_a, hi_a = wilson(int(a.sum()), len(a)); lo_b, hi_b = wilson(int(b.sum()), len(b))
                rows.append({"model": model, "measure": name, "training": t, "A": a_name, "B": b_name, "n": len(a),
                             "A count": int(a.sum()), "A 95%": f"[{lo_a:.1f}, {hi_a:.1f}]", "B count": int(b.sum()), "B 95%": f"[{lo_b:.1f}, {hi_b:.1f}]",
                             "only A": only_a, "only B": only_b, "McNemar p": round(mcnemar(only_a, only_b), 4)})
out = pd.DataFrame(rows)
out.to_csv(sys.argv[2], index=False)
pd.set_option("display.width", 300, "display.max_rows", 200)
print(out.to_string(index=False))
