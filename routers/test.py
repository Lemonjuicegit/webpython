from adjustArea import AdjustArea

tab = r"E:\工作文档\gdb数据\修改\土地分类面积表.xls"
gdb = r"E:\工作文档\gdb数据\修改\01空间数据\权属界线.shp"
aa = AdjustArea(tab,gdb)

aa.get_boundary()

print(aa.boun_d)