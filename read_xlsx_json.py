import pandas as pd
import json
df = pd.read_excel('d:/DEV/Human-Agent/import_test.xlsx')
data = {
    'columns': df.columns.tolist(),
    'row': df.head(1).to_dict('records')[0]
}
# convert Timestamps to string for json serialization
for k, v in data['row'].items():
    if isinstance(v, pd.Timestamp):
        data['row'][k] = v.isoformat()

with open('d:/DEV/Human-Agent/excel_info.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
