import pandas as pd
import json

file_path = 'd:/DEV/Human-Agent/导入文件/AI智能体员工档案中包间.xlsx'
try:
    df = pd.read_excel(file_path)
    cols = df.columns.tolist()
    with open('d:/DEV/Human-Agent/emp_headers.json', 'w', encoding='utf-8') as f:
        json.dump(cols, f, ensure_ascii=False)
except Exception as e:
    with open('d:/DEV/Human-Agent/emp_headers.json', 'w', encoding='utf-8') as f:
        json.dump({"error": str(e)}, f, ensure_ascii=False)
