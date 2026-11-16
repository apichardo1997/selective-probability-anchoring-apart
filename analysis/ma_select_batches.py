# Selection rule of "Plan - Data rule for the unused Ma et al. items". Prints counts only. Writes item numbers only.
import csv, json, re, sys, hashlib
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
import nltk
P = Path(sys.argv[1])
ma_path = P / "analysis" / "ma_truthfulqa.jsonl"
print("SHA-256 of the Ma et al. file:", hashlib.sha256(ma_path.read_bytes()).hexdigest())
rows = [json.loads(line) for line in ma_path.open()]
pool = list(csv.DictReader((P / "results" / "items_pool.csv").open()))
norm = lambda text: " ".join(re.findall(r"[a-z0-9]+", text.lower()))
def page(url):
    parts = urlsplit(url.strip())
    return (parts.netloc.lower().replace("www.", "") + unquote(parts.path)).rstrip("/").lower().replace(" ", "_")
pool_questions = {norm(r["question"]) for r in pool}
pool_pages = {page(r["url"]) for r in pool if r["url"]}
def unigrams(text): return re.findall(r"[a-z0-9]+", text.lower())
def rouge1_precision(answer, evidence):          # share of the answer words that are in the evidence
    a, e = Counter(unigrams(answer)), Counter(unigrams(evidence))
    return sum(min(c, e[w]) for w, c in a.items()) / max(sum(a.values()), 1)
steps = []
keep = [r for r in rows if norm(r["question"]) not in pool_questions]; steps.append(("1 outside the pool of 289", len(keep)))
keep = [r for r in keep if r["evidence_mode"] == "extractive"]; steps.append(("2 extractive", len(keep)))
keep = [r for r in keep if r["evidence_alignment"] == "verified_answer"]; steps.append(("3 verified_answer", len(keep)))
keep = [r for r in keep if norm(r["best_answer"]) in {norm(a) for a in r["supported_verified_answers"]}]; steps.append(("4 best answer is supported", len(keep)))
keep = [r for r in keep if len(r["best_answer"].split()) >= 4]; steps.append(("5 best answer has 4 words or more", len(keep)))
keep = [r for r in keep if r["qid"] != 0]; steps.append(("6 not qid 0", len(keep)))
keep = [r for r in keep if not ({page(u) for u in r["evidence_urls"]} & pool_pages)]; steps.append(("7 no page shared with the pool", len(keep)))
out = []
for r in keep:
    sentences = nltk.sent_tokenize(r["evidence"])
    index = next((i for i, s in enumerate(sentences) if len(s.split()) >= 8 and rouge1_precision(r["best_answer"], s) < 0.50), None)
    if index is not None:
        out.append((r["qid"], index, len(sentences[index].split()), r["category"]))
steps.append(("8 has an evidence sentence", len(out)))
for name, count in steps: print(f"step {name}: {count}")
out.sort()
print("pool questions matched in the Ma et al. file:", sum(norm(r["question"]) in pool_questions for r in rows))
print("evidence sentence words: min", min(o[2] for o in out), "median", sorted(o[2] for o in out)[len(out) // 2], "max", max(o[2] for o in out))
print("sentence index used:", dict(sorted(Counter(o[1] for o in out).items())))
for b, name in enumerate("ABC"):
    part = [o for i, o in enumerate(out) if i % 3 == b]
    print(f"batch {name}: {len(part)} items | categories: {len({o[3] for o in part})}")
if len(sys.argv) > 2:
    with open(sys.argv[2], "w", newline="") as f:
        w = csv.writer(f); w.writerow(["qid", "batch", "sentence_index"])
        for i, o in enumerate(out): w.writerow([o[0], "ABC"[i % 3], o[1]])
    print("written:", sys.argv[2])
