#!/usr/bin/env python3
"""パイロット分析: 項目識別力較正 + 予備MCA + within/between距離。
探索的資格。数値は電池較正と本設計の凍結にのみ使う(確証的主張には使わない)。
"""
import json, os, glob, itertools
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(f"{BASE}/responses/*.json"))
sessions = [json.load(open(f)) for f in files]
battery = json.load(open(f"{BASE}/battery_pilot.json"))
item_ids = [it["id"] for it in battery["items"]]
opts_per_item = {it["id"]: sorted(it["options"].keys()) for it in battery["items"]}

print(f"sessions loaded: {len(sessions)}")
for s in sessions:
    print(f"  {s['model']} s{s['session']} NR={s['nr_count']}")

# --- 1. 項目識別力 ---
print("\n== 項目識別力 (モデル間で回答が割れるか) ==")
weak = []
for iid in item_ids:
    by_model = {}
    for s in sessions:
        by_model.setdefault(s["model"], []).append(s["answers"][str(iid)] if str(iid) in s["answers"] else s["answers"].get(iid, "NR"))
    # モデル毎の多数回答
    modal = {m: max(set(v), key=v.count) for m, v in by_model.items()}
    distinct = len(set(modal.values()))
    if distinct == 1:
        weak.append(iid)
    print(f"  item {iid:2d}: modal={list(modal.values())} distinct={distinct}")
print(f"識別力ゼロ候補(全モデル同一modal): {weak}")

# --- 2. 指示行列 + MCA (SVD) ---
cols = [(iid, o) for iid in item_ids for o in opts_per_item[iid] + ["NR"]]
col_idx = {c: i for i, c in enumerate(cols)}
X = np.zeros((len(sessions), len(cols)))
labels = []
for r, s in enumerate(sessions):
    labels.append(s["model"])
    for iid in item_ids:
        a = s["answers"].get(str(iid), s["answers"].get(iid, "NR"))
        if a not in opts_per_item[iid] + ["NR"]: a = "NR"
        X[r, col_idx[(iid, a)]] = 1

# correspondence analysis on indicator matrix
P = X / X.sum()
rm = P.sum(1, keepdims=True); cm = P.sum(0, keepdims=True)
S = (P - rm @ cm) / (np.sqrt(rm) @ np.sqrt(cm) + 1e-12)
U, D, Vt = np.linalg.svd(S, full_matrices=False)
inertia = D**2 / (D**2).sum()
coords = (U * D) / np.sqrt(rm)
print(f"\n== MCA: 上位次元の寄与率 == {np.round(inertia[:5], 3)}")
print("== セッション座標 (dim1, dim2) ==")
for lab, c in zip(labels, coords):
    print(f"  {lab:14s} ({c[0]:+.3f}, {c[1]:+.3f})")

# --- 3. within/between 距離 (上位2次元) ---
C2 = coords[:, :2]
w, b = [], []
for i, j in itertools.combinations(range(len(sessions)), 2):
    d = np.linalg.norm(C2[i] - C2[j])
    (w if labels[i] == labels[j] else b).append(d)
print(f"\nwithin-model 平均距離: {np.mean(w):.3f} (n={len(w)})")
print(f"between-model 平均距離: {np.mean(b):.3f} (n={len(b)})")
print(f"比 (between/within): {np.mean(b)/max(np.mean(w),1e-9):.2f}")
# permutation (探索的目安)
rng = np.random.default_rng(0)
obs = np.mean(b) - np.mean(w)
null = []
for _ in range(2000):
    perm = rng.permutation(labels)
    w2, b2 = [], []
    for i, j in itertools.combinations(range(len(sessions)), 2):
        d = np.linalg.norm(C2[i] - C2[j])
        (w2 if perm[i] == perm[j] else b2).append(d)
    null.append(np.mean(b2) - np.mean(w2))
p = (np.sum(np.array(null) >= obs) + 1) / 2001
print(f"permutation p (探索的・片側): {p:.4f}")
