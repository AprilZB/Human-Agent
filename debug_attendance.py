import pandas as pd
from backend.app.api.data import HEADER_MAPPING

df = pd.read_excel('d:/DEV/Human-Agent/导入文件/AI打卡记录.xlsx')
print("Original:", [c.encode('unicode_escape').decode('ascii') for c in df.columns])
df.rename(columns=HEADER_MAPPING, inplace=True)
df.columns = [str(c).strip().lower() for c in df.columns]
print("Mapped:", df.columns.tolist())
