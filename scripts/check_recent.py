import os
import glob
import time

for p in glob.glob('data/**/*.json', recursive=True) + glob.glob('scripts/**/*.py', recursive=True):
    mtime = os.path.getmtime(p)
    if time.time() - mtime < 1800:
        t_str = time.strftime("%H:%M:%S", time.localtime(mtime))
        print(f"{t_str} : {p}")
