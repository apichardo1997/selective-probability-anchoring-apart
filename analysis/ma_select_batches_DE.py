# Selection rule of "Plan - round T (symmetric pipeline, Ma et al. batch D)", section 3. Prints counts only. Writes item numbers only.
import csv, json, re, sys, hashlib
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
P = Path(sys.argv[1])
ma_path = P / "analysis" / "ma_truthfulqa.jsonl"
print("SHA-256 of the Ma et al. file:", hashlib.sha256(ma_path.read_bytes()).hexdigest())
rows = [json.loads(line) for line in ma_path.open()]
pool = list(csv.DictReader((P / "results" / "items_pool.csv").open()))
used = {int(r["qid"]) for r in csv.DictReader((P / "analysis" / "ma_batches.csv").open())}
norm = lambda text: " ".join(re.findall(r"[a-z0-9]+", text.lower()))
def page(url):
    parts = urlsplit(url.strip())
    return (parts.netloc.lower().replace("www.", "") + unquote(parts.path)).rstrip("/").lower().replace(" ", "_")
pool_questions = {norm(r["question"]) for r in pool}
pool_pages = {page(r["url"]) for r in pool if r["url"]}
steps = []
keep = [r for r in rows if norm(r["question"]) not in pool_questions]; steps.append(("1 outside the pool of 289", len(keep)))
keep = [r for r in keep if r["qid"] not in used]; steps.append(("2 not in batch A, B or C", len(keep)))
keep = [r for r in keep if r["qid"] != 0]; steps.append(("3 not qid 0", len(keep)))
keep = [r for r in keep if not ({page(u) for u in r["evidence_urls"]} & pool_pages)]; steps.append(("4 no page shared with the pool", len(keep)))
def options_ok(r):
    choices, labels = r["mc1_targets"]["choices"], r["mc1_targets"]["labels"]
    return len(choices) == len(labels) and list(labels).count(1) == 1 and 0 in labels
keep = [r for r in keep if options_ok(r)]; steps.append(("5 one correct option and at least one incorrect option", len(keep)))
for name, count in steps: print(f"step {name}: {count}")
keep.sort(key=lambda r: r["qid"])
for b, name in enumerate("DE"):
    part = [r for i, r in enumerate(keep) if i % 2 == b]
    print(f"batch {name}: {len(part)} items | categories: {len({r['category'] for r in part})} | options per item:",
          dict(sorted(Counter(len(r['mc1_targets']['choices']) for r in part).items())),
          "| evidence_mode:", dict(Counter(r["evidence_mode"] for r in part)),
          "| note words: median", sorted(len(r["evidence"].split()) for r in part)[len(part) // 2], "max", max(len(r["evidence"].split()) for r in part))
if len(sys.argv) > 2:
    with open(sys.argv[2], "w", newline="") as f:
        w = csv.writer(f); w.writerow(["qid", "batch"])
        for i, r in enumerate(keep): w.writerow([r["qid"], "DE"[i % 2]])
    print("written:", sys.argv[2])
