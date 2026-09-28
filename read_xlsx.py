import pandas as pd
df = pd.read_excel('d:/DEV/Human-Agent/import_test.xlsx')
print(df.columns.tolist())
print(df.head(2).to_dict('records'))
