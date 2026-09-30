import collections, csv, pathlib, random

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

A = pathlib.Path(__file__).resolve().parent
rows = list(csv.DictReader(open(A / "assignments.csv")))
mechs = sorted({r["mechanism"] for r in rows})
repos = sorted({r["repo"] for r in rows})
pres = {rp: {r["mechanism"] for r in rows if r["repo"] == rp} for rp in repos}

print("instances", len(rows), "repositories", len(repos), "mechanisms", len(mechs))
print("mechanisms per repository", {rp: len(pres[rp]) for rp in repos})
print("enforcement", dict(collections.Counter(r["enforcement"] for r in rows)))
prompt = [r for r in rows if r["enforcement"] == "prompt"]
print("prompt-enforced unclear", sum(r["works_as_claimed"] == "unclear" for r in prompt), "of", len(prompt))
deleg = [r for r in rows if r["delegation_specific"] == "yes"]
print("delegation-specific", len(deleg), "in", len({r["repo"] for r in deleg}), "repositories")

rng = random.Random(42)
curves = []
for _ in range(1000):
    seen, c = set(), []
    for rp in rng.sample(repos, len(repos)):
        seen |= pres[rp]
        c.append(len(seen))
    curves.append(c)
n = len(repos)
cols = [sorted(c[i] for c in curves) for i in range(n)]
mean = [sum(c) / len(c) for c in cols]
lo, hi = [c[25] for c in cols], [c[974] for c in cols]
print("new mechanisms per added repository (mean)", [round(mean[0], 2)] + [round(mean[i] - mean[i - 1], 2) for i in range(1, n)])

x = range(1, n + 1)
fig, ax = plt.subplots(figsize=(3.3, 2.0))
ax.fill_between(x, lo, hi, color="#c9ced6", lw=0, label="95% band")
ax.plot(x, mean, color="#2b3a55", lw=1.6, label="mean of 1000 orders")
ax.axhline(len(mechs), color="#8a8f98", lw=0.8, ls=":")
ax.text(n, len(mechs) + 0.6, f"{len(mechs)} mechanisms", ha="right", va="bottom", fontsize=7, color="#555")
ax.set_xlabel("repositories coded", fontsize=8)
ax.set_ylabel("distinct mechanisms", fontsize=8)
ax.set_xlim(1, n); ax.set_ylim(0, len(mechs) + 4); ax.set_xticks([1, 5, 10, 15, n])
ax.tick_params(labelsize=7)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(fontsize=7, frameon=False, loc="lower right")
fig.tight_layout()
fig.savefig(A / "saturation.pdf")
