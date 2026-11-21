import os
import glob
import re

for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['.git', 'node_modules', '.gemini', '__pycache__']):
        continue
    for f in files:
        if f.endswith(('.json', '.csv', '.py', '.ts', '.tsx', '.js')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    matches = re.findall(r'Shahdara.*?28\.67\d+', content, re.DOTALL)
                    for m in matches[:3]:
                        print(f"{path}: {m[:60]}")
            except Exception:
                pass
