import os
import sys
import pandas as pd
import json

folder = 'd:/DEV/Human-Agent/导入文件/'
files = [f for f in os.listdir(folder) if f.endswith('.xlsx')]

all_headers = {}
for file in files:
    try:
        df = pd.read_excel(os.path.join(folder, file))
        all_headers[file] = [str(c).encode('unicode_escape').decode('ascii') for c in df.columns]
    except:
        pass

print(json.dumps(all_headers, indent=2))
