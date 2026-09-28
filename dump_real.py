import pandas as pd
import json

df = pd.read_excel('d:/DEV/Human-Agent/real_import.xlsx')
cols = df.columns.tolist()
with open('d:/DEV/Human-Agent/headers_real.json', 'w', encoding='utf-8') as f:
    json.dump(cols, f, ensure_ascii=False)
