import pandas as pd
df = pd.read_excel('d:/DEV/Human-Agent/导入文件/AI排班信息导入.xlsx')
for c in df.columns:
    print(c.encode('utf-8').hex())
