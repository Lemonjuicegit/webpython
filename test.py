import pandas as pd
 
data = {'name': ['John', 'Jane', 'Bob'], 'age': [32, 27, 45]}
df = pd.DataFrame(data)
df = df.set_index('name')
print(df)