from pk.土地权属界线认可书 import generate_jxrks_all
import pandas as pd
from pk.Ownership import Ownership

jzx = ''
gdb = 'E:\工作文档\daanchenshi.gdb'
# jzxdf = pd.read_excel(jzx)

Ow = Ownership(gdb)

generate_jzx = Ow.add_jzx_all()
for u in generate_jzx:
    print(u)
    
Ow.JZX.to_excel(r'E:\工作文档\测试导出数据\jzx.xlsx')