from pathlib import Path
import geopandas as gpd
import pandas as pd
shp = r'E:\exploitation\地块压盖处理\test.shp'
gdf = gpd.read_file(shp)
gdf['nfbh'] = gdf.NF.astype('int64')*1000 + gdf.BH
def overlap(row):
    ovdf = gdf[gdf.geometry.overlaps(row.geometry,align=False)]
    if ovdf.nfbh.shape[0]:
        bhlist = list(ovdf.nfbh)
        bhlist.append(row.nfbh)
        bhmax = max(bhlist)
        gdf.loc[gdf[gdf.nfbh == bhmax].index[0],'YXJ'] = 1
gdf.apply(overlap,axis=1)
left = gdf[gdf.YXJ == 1].copy()
con = gdf.overlay(left,how='difference')
con = pd.concat([con,left])

class Stacking:
    def __init__(self, shp,layer=''):
        if Path(shp).name.split('.')[-1] not in ['shp','gdb']:
            raise Exception('请设置shp或gdb')
        if Path(shp).name.split('.')[-1] =='shp':
            self.gdf = gpd.read_file(shp)
        else:
            if layer != '':
                self.gdf = gpd.read_file(shp,layer=layer)
            else:
                raise Exception('请设置图层')
    def overlap(self,row):
        ovdf = gdf[gdf.geometry.overlaps(row.geometry,align=False)]
        if ovdf.nfbh.shape[0]:
            bhlist = list(ovdf.nfbh)
            bhlist.append(row.nfbh)
            bhmax = max(bhlist)
            gdf.loc[gdf[gdf.nfbh == bhmax].index[0],'YXJ'] = 1
    def all_(self):
        self.gdf.apply(overlap,axis=1)
        left = gdf[gdf.YXJ == 1].copy()
        con = gdf.overlay(left,how='difference')
        con = pd.concat([con,left])

# 设置保存的位置和文件名

保存 = r'E:\exploitation\地块压盖处理'
文件名 = '处理.shp'

con.to_file(f"{保存}\\{文件名}",encoding='gb18030')