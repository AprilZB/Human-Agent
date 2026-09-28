import os
import pandas as pd
for root, dirs, files in os.walk('d:/DEV/Human-Agent'):
    for f in files:
        if 'xlsx' in f and 'AI' in f and '排班' in f.encode('utf-8').decode('utf-8','ignore') or 'AI' in f:
            src = os.path.join(root, f)
            print("Found:", src.encode('utf-8').hex())
            try:
                df = pd.read_excel(src)
                for c in df.columns:
                    print("  Col:", c.encode('utf-8').hex())
            except:
                pass
