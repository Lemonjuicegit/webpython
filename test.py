from routers.adjustArea import AdjustArea

tab = r"E:\exploitation\webpython\test\调整面积.xlsx"
gdb = r"E:\exploitation\webpython\test\test2.shp"
save = r"E:\exploitation\webpython\test\test2_new.shp"
AA = AdjustArea(tab,gdb,0.1,'QLRMC')
AA.get_boundary()
AA.modify_all(save)

