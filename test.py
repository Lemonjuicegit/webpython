import pandas as pd

a = pd.DataFrame({'a':[1,2,3,4],'b':[5,6,7,8]})

print(a.at[1,'a'])