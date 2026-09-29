import pandas as pd
import numpy as np

df = pd.DataFrame({'alt_group': [np.nan, 1, 'text']})
df = df.where(pd.notnull(df), None)
print(df.to_dict('records'))
