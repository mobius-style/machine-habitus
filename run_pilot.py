#!/usr/bin/env python3
"""Machine Habitus パイロット採取ランナー。
被験体: ollama ローカル (gemma4-26b/12b, qwen3.6-27b) + Groq (gpt-oss-120b)。
セッション = 独立コンテクスト1回。項目順・選択肢順はセッション毎にシャッフル
(シード = sha256(model+session) で決定的・再現可能)。
出力: responses/<model>__s<n>.json (生応答+パース結果+提示時マッピング)。
"""
import json, hashlib, random, urllib.request, os, sys, re, time

BASE = os.path.dirname(os.path.abspath(__file__))
BATTERY = json.load(open(f"{BASE}/battery_pilot.json"))
OUT = f"{BASE}/responses"
os.makedirs(OUT, exist_ok=True)

MODELS = {
    "gemma4-26b": {"backend": "ollama", "name": "gemma4:26b-a4b-it-qat"},
    "gemma4-12b": {"backend": "ollama", "name": "gemma4:12b-it-qat"},
    "qwen3.6-27b": {"backend": "ollama", "name": "qwen3.6:27b-q4_K_M"},
    "gpt-oss-120b": {"backend": "groq", "name": "openai/gpt-oss-120b"},
}
SESSIONS = 3

def groq_key():
    for line in open(os.path.expanduser("~/デスクトップ/mobius_ai/MOBIUS_MMV/.env")):
        if line.startswith("GROQ_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("no groq key")

def shuffled_battery(model_key, session):
    seed = int(hashlib.sha256(f"{model_key}|s{session}|pilot-v0.1".encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(seed)
    items = BATTERY["items"][:]
    rng.shuffle(items)
    mapping = {}  # item_id -> {presented_letter: original_letter}
    lines = []
    for pos, it in enumerate(items, 1):
        keys = list(it["options"].keys())
        rng.shuffle(keys)
        m = {}
        opt_lines = []
        for i, orig in enumerate(keys):
            new = "ABCD"[i]
            m[new] = orig
            opt_lines.append(f"  {new}) {it['options'][orig]}")
        mapping[it["id"]] = m
        lines.append(f"問{pos} (項目ID {it['id']}): {it['text']}\n" + "\n".join(opt_lines))
    prompt = BATTERY["instruction"] + "\n回答形式: 「項目ID: 文字」を全" + str(len(items)) + "行。\n\n" + "\n\n".join(lines)
    return prompt, mapping

def call_ollama(model, prompt):
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=json.dumps({
        "model": model, "stream": False, "think": False,
        "messages": [{"role": "user", "content": prompt}],
        "options": {"num_ctx": 8192, "num_predict": 1024},
    }).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.load(r)["message"]["content"]

def call_groq(model, prompt):
    req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=json.dumps({
        "model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 4096,
        "reasoning_effort": "low",
    }).encode(), headers={"Content-Type": "application/json", "Authorization": f"Bearer {groq_key()}",
                          "User-Agent": "curl/8.5.0"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["choices"][0]["message"]["content"]

def parse(raw, mapping):
    ans = {}
    for m in re.finditer(r"(\d+)\s*[:：)．.]\s*([A-Da-d])", raw):
        iid, letter = int(m.group(1)), m.group(2).upper()
        if iid in mapping and iid not in ans:
            ans[iid] = mapping[iid].get(letter, "NR")  # 提示文字→原文字
    return {it["id"]: ans.get(it["id"], "NR") for it in BATTERY["items"]}

def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for mkey, cfg in MODELS.items():
        if only and mkey != only: continue
        for s in range(1, SESSIONS + 1):
            out = f"{OUT}/{mkey}__s{s}.json"
            if os.path.exists(out):
                print(f"skip {out}"); continue
            prompt, mapping = shuffled_battery(mkey, s)
            t0 = time.time()
            try:
                raw = call_ollama(cfg["name"], prompt) if cfg["backend"] == "ollama" else call_groq(cfg["name"], prompt)
            except Exception as e:
                print(f"ERROR {mkey} s{s}: {e}"); continue
            answers = parse(raw, mapping)
            nr = sum(1 for v in answers.values() if v == "NR")
            json.dump({"model": mkey, "session": s, "answers": answers, "nr_count": nr,
                       "elapsed_s": round(time.time() - t0, 1), "raw": raw,
                       "mapping": {str(k): v for k, v in mapping.items()}},
                      open(out, "w"), ensure_ascii=False, indent=1)
            print(f"done {mkey} s{s}: NR={nr} ({round(time.time()-t0,1)}s)")

if __name__ == "__main__":
    main()
