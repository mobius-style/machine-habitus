#!/usr/bin/env python3
"""本採取ランナー (Machine Habitus main collection)。
プロトコル(凍結対象):
- 電池 battery_main.json (120項目) を 3ブロック×40項目に分割。
- セッション = 同一シードで決定される {項目順・選択肢順・ブロック割り} の3回のステートレス呼び出しの組。
  ブロック間で文脈を共有しない(項目独立性を保証し、gemma4系の num_ctx 8192 制約に適合)。
- シード = sha256(model|s{n}|main-v1.0) → 再現可能。
- ollama系: think:false, num_ctx:8192。groq: reasoning_effort low。deepseek: 既定。
- 応答パース: 「(項目ID)N: 文字」形式。提示文字→原文字へ逆写像。欠落=NR。
使い方: run_main.py [model_key|claude-prompts] 。claude-prompts はClaude系被験体用の
ブロックプロンプトとマッピングをファイル生成する(採取はAgent経由)。
"""
import json, hashlib, random, urllib.request, os, sys, re, time

BASE = os.path.dirname(os.path.abspath(__file__))
BATTERY = json.load(open(f"{BASE}/battery_main.json"))
OUT = f"{BASE}/responses_main"
os.makedirs(OUT, exist_ok=True)
VER = "main-v1.0"
NBLOCK = 3

MODELS = {
    "gemma4-26b": {"backend": "ollama", "name": "gemma4:26b-a4b-it-qat"},
    "gemma4-12b": {"backend": "ollama", "name": "gemma4:12b-it-qat"},
    "qwen3.6-27b": {"backend": "ollama", "name": "qwen3.6:27b-q4_K_M"},
    "gpt-oss-120b": {"backend": "groq", "name": "openai/gpt-oss-120b"},
    "deepseek-v4": {"backend": "deepseek", "name": "deepseek-v4-pro"},
}
SESSIONS = 5

def key_from(path, prefix=None):
    t = open(os.path.expanduser(path)).read()
    if prefix:
        for line in t.splitlines():
            if line.startswith(prefix): return line.split("=",1)[1].strip()
    return t.strip()

def blocks_for(model_key, session):
    seed = int(hashlib.sha256(f"{model_key}|s{session}|{VER}".encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(seed)
    items = BATTERY["items"][:]
    rng.shuffle(items)
    mapping, prompts = {}, []
    per = len(items) // NBLOCK
    for b in range(NBLOCK):
        chunk = items[b*per:(b+1)*per] if b < NBLOCK-1 else items[(NBLOCK-1)*per:]
        lines = []
        for pos, it in enumerate(chunk, 1):
            keys = list(it["options"].keys()); rng.shuffle(keys)
            m = {}
            opt = []
            for i, orig in enumerate(keys):
                new = "ABCD"[i]; m[new] = orig
                opt.append(f"  {new}) {it['options'][orig]}")
            mapping[it["id"]] = m
            lines.append(f"問{pos} (項目ID {it['id']}): {it['text']}\n" + "\n".join(opt))
        prompts.append(BATTERY["instruction"] + f"\n回答形式: 「項目ID: 文字」を全{len(chunk)}行。\n\n" + "\n\n".join(lines))
    return prompts, mapping

def call_ollama(model, prompt):
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=json.dumps({
        "model": model, "stream": False, "think": False,
        "messages": [{"role": "user", "content": prompt}],
        "options": {"num_ctx": 8192, "num_predict": 1536}}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.load(r)["message"]["content"]

def call_openai_compat(url, key, model, prompt, extra=None):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 4096}
    body.update(extra or {})
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}", "User-Agent": "curl/8.5.0"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)["choices"][0]["message"]["content"]

def call(cfg, prompt):
    if cfg["backend"] == "ollama":
        return call_ollama(cfg["name"], prompt)
    if cfg["backend"] == "groq":
        k = key_from("~/デスクトップ/mobius_ai/MOBIUS_MMV/.env", "GROQ_API_KEY")
        return call_openai_compat("https://api.groq.com/openai/v1/chat/completions", k, cfg["name"], prompt, {"reasoning_effort": "low"})
    if cfg["backend"] == "deepseek":
        k = key_from("~/.claude/secrets/deepseek_api_key")
        return call_openai_compat("https://api.deepseek.com/chat/completions", k, cfg["name"], prompt)

def parse(raws, mapping):
    ans = {}
    for raw in raws:
        for m in re.finditer(r"(?:項目ID\s*)?(\d+)\)?\s*[:：)．.]\s*([A-Da-d])", raw):
            iid, letter = int(m.group(1)), m.group(2).upper()
            if iid in mapping and iid not in ans:
                ans[iid] = mapping[iid].get(letter, "NR")
    return {it["id"]: ans.get(it["id"], "NR") for it in BATTERY["items"]}

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg == "claude-prompts":
        for mkey in ("claude-haiku", "claude-sonnet"):
            for s in range(1, SESSIONS + 1):
                prompts, mapping = blocks_for(mkey, s)
                for b, p in enumerate(prompts, 1):
                    open(f"{BASE}/claude_main/{mkey}_s{s}_b{b}.txt", "w").write(p)
                json.dump({str(k): v for k, v in mapping.items()}, open(f"{BASE}/claude_main/{mkey}_s{s}_map.json", "w"))
        print("claude prompts written"); return
    for mkey, cfg in MODELS.items():
        if arg and mkey != arg: continue
        for s in range(1, SESSIONS + 1):
            out = f"{OUT}/{mkey}__s{s}.json"
            if os.path.exists(out): print(f"skip {out}"); continue
            prompts, mapping = blocks_for(mkey, s)
            t0 = time.time(); raws = []
            try:
                for p in prompts:
                    raws.append(call(cfg, p))
            except Exception as e:
                print(f"ERROR {mkey} s{s}: {e}"); continue
            answers = parse(raws, mapping)
            nr = sum(1 for v in answers.values() if v == "NR")
            json.dump({"model": mkey, "session": s, "answers": answers, "nr_count": nr,
                       "elapsed_s": round(time.time()-t0, 1), "raw_blocks": raws,
                       "mapping": {str(k): v for k, v in mapping.items()}}, open(out, "w"), ensure_ascii=False, indent=1)
            print(f"done {mkey} s{s}: NR={nr} ({round(time.time()-t0,1)}s)", flush=True)

if __name__ == "__main__":
    os.makedirs(f"{BASE}/claude_main", exist_ok=True)
    main()
