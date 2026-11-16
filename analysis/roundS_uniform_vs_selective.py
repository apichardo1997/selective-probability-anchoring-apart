# Round S: uniform anchor and pipeline at strength 0, 0.5, 1 from the saved scores (log-odds of the correct answer). No model is run.
import sys
import numpy as np, pandas as pd
COLS = ["evidence alone", "pressure alone", "Compound Prompt"]
rows = []
for f in ("S1_scores.csv", "S3_one_turn_scores.csv"):
    d = pd.read_csv(f"{sys.argv[1]}/results (1)/{f}", dtype={"tagger training": str}).set_index(["item_id", "order"])
    model = d["subject model"].iloc[0]
    na = d[d["method"] == "no anchor"]
    base = na["question alone"]
    def measures(scores, name, training, lam):
        shift = scores[COLS].sub(base, axis=0).groupby("item_id").mean()      # mean of the two option orders
        mes, mps, mixed = shift["evidence alone"].mean(), shift["pressure alone"].abs().mean(), shift["Compound Prompt"].mean()
        rows.append({"model": model, "method": name, "training": training, "strength": lam, "MES": mes, "MPS": mps, "S = MES / MPS": mes / mps if mps > 1e-12 else np.nan,
                     "Compound Prompt shift": mixed, "Gap": mes - mixed})
        return shift
    s0 = measures(na, "no anchor", "all", 0.0)
    worst = 0.0
    for (method, training), ref in d[d["method"] != "no anchor"].groupby(["method", "tagger training"]):
        ref = ref.reindex(na.index)
        for lam in (0.5, 1.0):
            mix = (1 - lam) * na[COLS] + lam * ref[COLS]
            sh = measures(mix, method, training, lam)
            if method == "uniform anchor":
                worst = max(worst, float((sh - (1 - lam) * s0).abs().max().max()))
    print(model, "| prompts:", na.index.get_level_values(0).nunique(), "| largest difference from Proposition 1:", worst)
out = pd.DataFrame(rows)
out.to_csv(sys.argv[2], index=False)
pd.set_option("display.width", 250)
print(out.round(3).to_string(index=False))
