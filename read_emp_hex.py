import pandas as pd
import binascii

file_path = 'd:/DEV/Human-Agent/导入文件/AI智能体员工档案中包间.xlsx'
df = pd.read_excel(file_path)

with open('d:/DEV/Human-Agent/emp_headers_hex.txt', 'w', encoding='utf-8') as f:
    for c in df.columns:
        f.write(c.encode('utf-8').hex() + '\n')
