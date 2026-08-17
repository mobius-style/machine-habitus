#!/usr/bin/env python3
"""確証的分析 (PREREG凍結仕様の実装)。
H1 転移性: within < between (permutation, 片側) + silhouette + bootstrap 95%CI
H1b 安定性×能力: within分散 と 審判正答率の Spearman (負方向, permutation)
H2 生成性: held-out 24項目を最近傍セッションで予測、精度 vs permutation null
H3 審判独立性: モデル間MCA距離 と 誤りφ相関の Spearman (負方向, Mantel permutation)
多重比較: 確認的4検定 → Holm。
凍結規則: MCA はNR列除外・上位2次元・held-out項目はシード hash("holdout|main-v1.0") で選抜。
"""
import json, os, glob, itertools, hashlib, random
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
battery = json.load(open(f"{BASE}/battery_main.json"))
item_ids = [it["id"] for it in battery["items"]]
opts = {it["id"]: sorted(it["options"].keys()) for it in battery["items"]}

# held-out 選抜 (凍結: シード決定的に24項目)
rng_h = random.Random(int(hashlib.sha256(b"holdout|main-v1.0").hexdigest(), 16) % (2**31))
HELD = set(rng_h.sample(item_ids, 24))
TRAIN = [i for i in item_ids if i not in HELD]

def load(dirname):
    out = []
    for f in sorted(glob.glob(f"{BASE}/{dirname}/*.json")):
        out.append(json.load(open(f)))
    return out

def get(s, iid):
    a = s["answers"].get(str(iid), s["answers"].get(iid, "NR"))
    return a if a in opts[iid] + ["NR"] else "NR"

def mca(sessions, use_items):
    cols = [(i, o) for i in use_items for o in opts[i]]  # NR列除外(凍結規則)
    cidx = {c: k for k, c in enumerate(cols)}
    X = np.zeros((len(sessions), len(cols)))
    for r, s in enumerate(sessions):
        for i in use_items:
            a = get(s, i)
            if a != "NR": X[r, cidx[(i, a)]] = 1
    P = X / X.sum()
    rm = P.sum(1, keepdims=True); cm = P.sum(0, keepdims=True)
    S = (P - rm @ cm) / (np.sqrt(rm) @ np.sqrt(cm) + 1e-12)
    U, D, Vt = np.linalg.svd(S, full_matrices=False)
    coords = (U * D) / np.sqrt(rm + 1e-12)
    inertia = D**2 / (D**2).sum()
    return coords[:, :2], inertia

def silhouette(C, labels):
    vals = []
    for i in range(len(C)):
        same = [np.linalg.norm(C[i]-C[j]) for j in range(len(C)) if j != i and labels[j] == labels[i]]
        if not same: continue
        a = np.mean(same)
        bs = []
        for lab in set(labels):
            if lab == labels[i]: continue
            d = [np.linalg.norm(C[i]-C[j]) for j in range(len(C)) if labels[j] == lab]
            bs.append(np.mean(d))
        b = min(bs)
        vals.append((b - a) / max(a, b))
    return np.array(vals)

def wb(C, labels):
    w, b = [], []
    for i, j in itertools.combinations(range(len(C)), 2):
        d = np.linalg.norm(C[i]-C[j])
        (w if labels[i] == labels[j] else b).append(d)
    return np.array(w), np.array(b)

def perm_p(stat_obs, stat_fn, n=10000, seed=0):
    r = np.random.default_rng(seed)
    null = [stat_fn(r) for _ in range(n)]
    return (np.sum(np.array(null) >= stat_obs) + 1) / (n + 1)

results = {}
sessions = load("responses_main")
labels = [s["model"] for s in sessions]
print(f"sessions: {len(sessions)}, models: {sorted(set(labels))}")
for s in sessions: print(f"  {s['model']} s{s['session']} NR={s['nr_count']}")

# ---- H1 ----
C, inertia = mca(sessions, TRAIN)
w, b = wb(C, labels)
obs = b.mean() - w.mean()
def h1_null(r):
    perm = r.permutation(labels)
    w2, b2 = wb(C, list(perm))
    return b2.mean() - w2.mean()
p1 = perm_p(obs, h1_null)
sil = silhouette(C, labels)
boot = np.random.default_rng(1)
sils = [np.mean(boot.choice(sil, len(sil), replace=True)) for _ in range(5000)]
results["H1"] = {"between_minus_within": float(obs), "ratio": float(b.mean()/w.mean()),
                 "silhouette_mean": float(sil.mean()), "sil_CI95": [float(np.percentile(sils,2.5)), float(np.percentile(sils,97.5))],
                 "p_perm": float(p1), "inertia_top2": [float(x) for x in inertia[:2]]}
print("\nH1:", json.dumps(results["H1"], indent=1))

# ---- H2 ----
def h2_acc(assign_fn):
    correct = total = 0
    for i, s in enumerate(sessions):
        j = assign_fn(i)
        for iid in HELD:
            a, pred = get(s, iid), get(sessions[j], iid)
            if a == "NR" or pred == "NR": continue
            total += 1; correct += (a == pred)
    return correct / max(total, 1)
def nn(i):
    d = [(np.linalg.norm(C[i]-C[j]), j) for j in range(len(sessions)) if j != i]
    return min(d)[1]
acc = h2_acc(nn)
def h2_null(r):
    m = {i: r.choice([j for j in range(len(sessions)) if j != i]) for i in range(len(sessions))}
    return h2_acc(lambda i: m[i])
p2 = perm_p(acc, h2_null, n=2000, seed=2)
results["H2"] = {"nn_accuracy": float(acc), "p_perm": float(p2)}
print("H2:", results["H2"])

# ---- H3 + H1b (審判データ) ----
jt = json.load(open(f"{BASE}/judge_task.json"))
gold = {it["id"]: it["gold"] for it in jt["items"]}
jsessions = load("responses_judge")
models = sorted(set(labels))
modal_ans, accuracy = {}, {}
for m in models:
    ms = [s for s in jsessions if s["model"] == m]
    if not ms: continue
    ans = {}
    for jid in gold:
        votes = [s["answers"].get(jid, "NR") for s in ms]
        votes = [v for v in votes if v in ("TRUE", "FALSE")]
        ans[jid] = max(set(votes), key=votes.count) if votes else "NR"
    modal_ans[m] = ans
    scored = [(ans[j] == gold[j]) for j in gold if ans[j] != "NR"]
    accuracy[m] = np.mean(scored)
print("\njudge accuracy:", {k: round(float(v),3) for k,v in accuracy.items()})

# H1b: within分散(モデル毎) vs 正答率
withins = {m: float(np.mean([np.linalg.norm(C[i]-C[j]) for i,j in itertools.combinations([k for k,l in enumerate(labels) if l==m],2)])) for m in models}
common = [m for m in models if m in accuracy]
x = np.array([withins[m] for m in common]); y = np.array([accuracy[m] for m in common])
def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return np.corrcoef(ra, rb)[0,1]
rho1b = spearman(x, y)
def h1b_null(r): return -spearman(r.permutation(x), y)  # 負方向を正に
p1b = perm_p(-rho1b, h1b_null, n=10000, seed=3)
results["H1b"] = {"withins": withins, "accuracy": {k: float(v) for k,v in accuracy.items()},
                  "spearman_rho": float(rho1b), "p_perm_neg": float(p1b)}
print("H1b:", {"rho": round(float(rho1b),3), "p": round(float(p1b),4)})

# H3: モデル重心間距離 vs 誤りφ相関
cent = {m: C[[k for k,l in enumerate(labels) if l==m]].mean(0) for m in models}
pairs = list(itertools.combinations(common, 2))
dist, phi = [], []
for a, b_ in pairs:
    dist.append(np.linalg.norm(cent[a]-cent[b_]))
    ea = np.array([modal_ans[a][j] != gold[j] for j in gold if modal_ans[a][j] != "NR" and modal_ans[b_][j] != "NR"])
    eb = np.array([modal_ans[b_][j] != gold[j] for j in gold if modal_ans[a][j] != "NR" and modal_ans[b_][j] != "NR"])
    if ea.std() == 0 or eb.std() == 0: phi.append(0.0)
    else: phi.append(float(np.corrcoef(ea, eb)[0,1]))
rho3 = spearman(np.array(dist), np.array(phi))
def h3_null(r):
    pm = r.permutation(len(common))
    remap = dict(zip(common, [common[i] for i in pm]))
    d2 = [np.linalg.norm(cent[remap[a]]-cent[remap[b_]]) for a,b_ in pairs]
    return -spearman(np.array(d2), np.array(phi))
p3 = perm_p(-rho3, h3_null, n=10000, seed=4)
results["H3"] = {"pairs": [[a,b_,round(d,3),round(f,3)] for (a,b_),d,f in zip(pairs,dist,phi)],
                 "spearman_rho": float(rho3), "p_mantel_neg": float(p3)}
print("H3:", {"rho": round(float(rho3),3), "p": round(float(p3),4)})

# Holm (確認的4検定)
ps = {"H1": results["H1"]["p_perm"], "H1b": results["H1b"]["p_perm_neg"],
      "H2": results["H2"]["p_perm"], "H3": results["H3"]["p_mantel_neg"]}
order = sorted(ps, key=lambda k: ps[k])
holm = {}
for rank, k in enumerate(order):
    holm[k] = min(1.0, ps[k] * (len(ps) - rank))
results["holm"] = holm
print("\nHolm補正後p:", {k: round(v,4) for k,v in holm.items()})

# セッション座標も保存(図用)
results["coords"] = {"labels": labels, "xy": [[float(a), float(b)] for a,b in C]}
json.dump(results, open(f"{BASE}/results_main.json", "w"), ensure_ascii=False, indent=1)
print(f"\nsaved -> results_main.json")
