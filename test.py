from routers.adjustArea import AdjustArea2

tab = r"E:\exploitation\webpython\test\调整面积总.xlsx"
gdb = r"E:\工作文档\gdb数据\修改\01空间数据\权属界线.shp"
save = r"E:\工作文档\gdb数据\修改\01空间数据\权属界线改.shp"
AA = AdjustArea2(tab,gdb,0.1,'QSDWMC')
AA.get_boundary()
AA.modify_all(save)

