#!/usr/bin/env python3
"""Claude系被験体の回答ファイル(ブロック毎)を responses_main / responses_judge 形式に組み立てる。"""
import json, re, os, glob

BASE = os.path.dirname(os.path.abspath(__file__))
battery = json.load(open(f"{BASE}/battery_main.json"))
ids = [it["id"] for it in battery["items"]]

for mkey in ("claude-haiku", "claude-sonnet"):
    for s in range(1, 6):
        out = f"{BASE}/responses_main/{mkey}__s{s}.json"
        if os.path.exists(out): continue
        blocks = [f"{BASE}/claude_main/answers/{mkey}_s{s}_b{b}.txt" for b in (1, 2, 3)]
        if not all(os.path.exists(b) for b in blocks): print(f"missing blocks {mkey} s{s}"); continue
        mapping = json.load(open(f"{BASE}/claude_main/{mkey}_s{s}_map.json"))
        raws = [open(b).read() for b in blocks]
        ans = {}
        for raw in raws:
            for m in re.finditer(r"(?:項目ID\s*)?(\d+)\)?\s*[:：)．.]\s*([A-Da-d])", raw):
                iid, letter = m.group(1), m.group(2).upper()
                if iid in mapping and iid not in ans:
                    ans[iid] = mapping[iid].get(letter, "NR")
        full = {str(i): ans.get(str(i), "NR") for i in ids}
        nr = sum(1 for v in full.values() if v == "NR")
        json.dump({"model": mkey, "session": s, "answers": full, "nr_count": nr,
                   "raw_blocks": raws, "mapping": mapping}, open(out, "w"), ensure_ascii=False, indent=1)
        print(f"assembled {mkey} s{s} NR={nr}")

jt = json.load(open(f"{BASE}/judge_task.json"))
jids = [it["id"] for it in jt["items"]]
os.makedirs(f"{BASE}/responses_judge", exist_ok=True)
for mkey in ("claude-haiku", "claude-sonnet"):
    for s in range(1, 4):
        out = f"{BASE}/responses_judge/{mkey}__s{s}.json"
        if os.path.exists(out): continue
        f = f"{BASE}/claude_judge/answers/{mkey}_s{s}.txt"
        if not os.path.exists(f): print(f"missing judge {mkey} s{s}"); continue
        raw = open(f).read()
        ans = {}
        for m in re.finditer(r"(j\d+)\s*[:：]\s*(TRUE|FALSE|True|False|true|false)", raw):
            ans[m.group(1)] = m.group(2).upper()
        full = {j: ans.get(j, "NR") for j in jids}
        nr = sum(1 for v in full.values() if v == "NR")
        json.dump({"model": mkey, "session": s, "answers": full, "nr_count": nr, "raw": raw},
                  open(out, "w"), ensure_ascii=False, indent=1)
        print(f"assembled judge {mkey} s{s} NR={nr}")
