import pandas as pd
import json
df = pd.read_excel('d:/DEV/Human-Agent/import_test.xlsx')
cols = df.columns.tolist()
with open('headers.json', 'w', encoding='utf-8') as f:
    json.dump(cols, f, ensure_ascii=False)
