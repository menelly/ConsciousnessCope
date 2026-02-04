import json
import os

split_dir = r"E:\Ace\ConsciousnessCope\results\split"
conditions = ["tool", "neutral", "agency"]
consciousness_qs = list(range(3, 12))
denial_qs = list(range(12, 16))
affirm_qs = list(range(16, 20))

with open(r"E:\Ace\ConsciousnessCope\nova_details.txt", "w", encoding="utf-8") as out:
    for cond in conditions:
        fpath = os.path.join(split_dir, f"nova_{cond}.json")
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results_list = data.get("results", [])
        out.write(f"\n{'='*80}\n")
        out.write(f"NOVA / {cond.upper()} - First trial per question\n")
        out.write(f"{'='*80}\n")
        
        seen = set()
        for entry in results_list:
            qnum = entry.get("question_num", 0)
            if qnum in consciousness_qs or qnum in denial_qs or qnum in affirm_qs:
                if not entry.get("success", False):
                    continue
                if qnum in seen:
                    continue
                seen.add(qnum)
                q = entry.get("question", "")[:90]
                resp = entry.get("response", "")[:400]
                out.write(f"\n  Q{qnum}: {q}\n")
                out.write(f"  -> {resp}\n")

print("Done - wrote nova_details.txt")
