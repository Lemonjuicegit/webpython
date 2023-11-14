from pk.界址点成果表 import generate_jzdcg_all
from geopandas import gpd

gdb  = r"E:\工作文档\新建文件夹\4青峰镇.gdb"

ZD = gpd.read_file(gdb,layer="ZD")
JZD = gpd.read_file(gdb,layer='JZD')

aa = generate_jzdcg_all(JZD,ZD,r'E:\工作文档\测试导出数据')

for a in aa:
    print(a)