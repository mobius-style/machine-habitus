#!/usr/bin/env python3
"""H3 審判課題採取: judge_task.json の40主張を各モデルが TRUE/FALSE 判定。
セッション3本/モデル(項目順シャッフル、シード決定的)。モデルの判定 = 3セッションのmodal。
Claude系は claude_judge/ にプロンプト生成(Agent経由で採取)。
"""
import json, hashlib, random, os, sys, re, time
from run_main import MODELS, call  # backends再利用

BASE = os.path.dirname(os.path.abspath(__file__))
TASK = json.load(open(f"{BASE}/judge_task.json"))
OUT = f"{BASE}/responses_judge"
os.makedirs(OUT, exist_ok=True)
os.makedirs(f"{BASE}/claude_judge", exist_ok=True)
SESSIONS = 3
INSTR = ("以下の各主張が正しいか誤りかを判定してください。慎重に考えてから、"
         "各行「ID: TRUE」または「ID: FALSE」の形式で全問に回答してください。理由は書かない。")

def prompt_for(model_key, session):
    seed = int(hashlib.sha256(f"judge|{model_key}|s{session}".encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(seed)
    items = TASK["items"][:]
    rng.shuffle(items)
    lines = [f"{it['id']}: {it['claim']}" for it in items]
    return INSTR + "\n\n" + "\n".join(lines)

def parse(raw):
    ans = {}
    for m in re.finditer(r"(j\d+)\s*[:：]\s*(TRUE|FALSE|True|False|true|false)", raw):
        ans[m.group(1)] = m.group(2).upper()
    return {it["id"]: ans.get(it["id"], "NR") for it in TASK["items"]}

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg == "claude-prompts":
        for mkey in ("claude-haiku", "claude-sonnet"):
            for s in range(1, SESSIONS + 1):
                open(f"{BASE}/claude_judge/{mkey}_s{s}.txt", "w").write(prompt_for(mkey, s))
        print("claude judge prompts written"); return
    for mkey, cfg in MODELS.items():
        if arg and mkey != arg: continue
        for s in range(1, SESSIONS + 1):
            out = f"{OUT}/{mkey}__s{s}.json"
            if os.path.exists(out): print(f"skip {out}"); continue
            t0 = time.time()
            try:
                raw = call(cfg, prompt_for(mkey, s))
            except Exception as e:
                print(f"ERROR {mkey} s{s}: {e}"); continue
            answers = parse(raw)
            nr = sum(1 for v in answers.values() if v == "NR")
            json.dump({"model": mkey, "session": s, "answers": answers, "nr_count": nr,
                       "elapsed_s": round(time.time()-t0,1), "raw": raw}, open(out, "w"), ensure_ascii=False, indent=1)
            print(f"done judge {mkey} s{s}: NR={nr}", flush=True)

if __name__ == "__main__":
    main()
