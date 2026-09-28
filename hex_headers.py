import pandas as pd

df = pd.read_excel('d:/DEV/Human-Agent/real_import.xlsx')
for c in df.columns.tolist():
    print(f"Col: {c.encode('utf-8').hex()} -> {c}")
