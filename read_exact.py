import pandas as pd
import json

filename = "d:/DEV/Human-Agent/导入文件/AI智能体中包含生产订单信息表格.xlsx"
df = pd.read_excel(filename)
cols = df.columns.tolist()
with open('headers2.json', 'w', encoding='utf-8') as f:
    json.dump(cols, f, ensure_ascii=False)
