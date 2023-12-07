from pathlib import Path
import geopandas as gpd
import pandas as pd
from . import Djmod


class Stacking:
    def __init__(self, shp,priority:str,isorderly: bool=True,layer=''):
        '''
        shp:shp文件路径
        Priority:优先级
        layer:图层名
        '''
        self.priority = priority
        self.isorderly = isorderly
        if Path(shp).name.split('.')[-1] not in ['shp','gdb']:
            raise Djmod.Myerr('请设置shp或gdb')
        if Path(shp).name.split('.')[-1] =='shp':
            self.gdf = gpd.read_file(shp)
        else:
            if layer != '':
                self.gdf = gpd.read_file(shp,layer=layer)
            else:
                raise Djmod.Myerr('请设置图层')
        if priority not in self.gdf.columns:
            raise Djmod.Myerr(f'{Path(shp).name}中不存在({priority})字段')
    def overlap_noorderly(self,row):
        '''
        无序
        '''
        ovdf = self.gdf[self.gdf.geometry.overlaps(row.geometry,align=False)]
        if ovdf[self.priority].shape[0]:
            bhlist = list(ovdf[self.priority])
            bhlist.append(row[self.priority])
            bhmax = max(bhlist)
            self.gdf.loc[self.gdf[self.gdf[self.priority] == bhmax].index[0],'YXJ'] = 1
            
    def overlap_orderly(self)->pd.DataFrame:
        pr_list = self.gdf.priority.drop_duplicates().values
        con:pd.DataFrame = self.gdf.copy()
        for pr in pr_list:
            ovdf = con[con.priority == pr].copy()
            con = con.overlay(ovdf,how='difference')
            con = pd.concat([con,ovdf])
        return con
    def all_(self,save):
        if self.isorderly:
            con = self.overlap_orderly()
        else:
            self.gdf.apply(self.overlap_noorderly,axis=1)
            left = self.gdf[self.gdf.YXJ == 1].copy()
            con = self.gdf.overlay(left,how='difference')
            con = pd.concat([con,left])
        con.to_file(save,encoding='gb18030')
