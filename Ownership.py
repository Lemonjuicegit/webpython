import geopandas as gpd
import pandas as pd
import numpy as np
from decimal import Decimal, getcontext
from shapely.geometry import Polygon, MultiPolygon,mapping
from Djmod import Djlog
log = Djlog()

class Ownership:
    def __init__(self,gdbpath):
        self.ZD = gpd.read_file(gdbpath,layer='ZD')
        self.JZD = gpd.read_file(gdbpath,layer='JZD')

        # self.JZD['X'] = np.ceil(self.JZD.geometry.x*1000).astype('int64')
        # self.JZD['Y'] = np.ceil(self.JZD.geometry.y*1000).astype('int64')
        self.JZD['X'] = np.round(self.JZD.geometry.x*10).astype('int64')
        self.JZD['Y'] = np.round(self.JZD.geometry.y*10).astype('int64')
        self.JZD['XY'] = self.JZD['X'] + self.JZD['Y']
        # self.a = self.JZD[(self.JZD.ZDDM == '500118002015JA10033') & (self.JZD.JZD_NEW == 'J1')]
        # self.get_coordinates(self.ZD)
        self.JZD_All = gpd.read_file(gdbpath,layer='ZD_All')
        self.JZX = pd.DataFrame(columns=('ZDDM','QLRMC','LZQLRMC','QSDH','ZJDH','ZZDH','INDEX','BXZ','BCM'))
        self.JZD,self.jzd_boundary = self.get_jzd_boundary()
    
    def adjacent_jzdzddm(self,jzd):
        # 相邻界址点
        x = jzd.X
        y = jzd.Y
        b_xljzd = self.jzd_boundary[(self.jzd_boundary.X == x) & (self.jzd_boundary.Y == y) & ~(self.jzd_boundary.ZDDM== jzd.ZDDM)]
        b_jzd = self.jzd_boundary[(self.jzd_boundary.ZDDM == jzd.ZDDM) & (self.jzd_boundary.INDEX == jzd.INDEX)]
        JZDH = jzd.JZDH
        if not JZDH:
            h_boundary_x = b_jzd.iloc[-1].X
            h_boundary_y = b_jzd.iloc[-1].Y
            q_boundary_x = b_jzd.iloc[JZDH+1].X
            q_boundary_y = b_jzd.iloc[JZDH+1].Y
            h_xljzd = self.jzd_boundary[(self.jzd_boundary.X == h_boundary_x) & (self.jzd_boundary.Y == h_boundary_y) & ~(self.jzd_boundary.ZDDM == jzd.ZDDM)] # 后面相邻界址点
            q_xljzd = self.jzd_boundary[(self.jzd_boundary.X == q_boundary_x) & (self.jzd_boundary.Y == q_boundary_y) & ~(self.jzd_boundary.ZDDM == jzd.ZDDM)] # 前面相邻界址点
        elif JZDH == b_jzd.iloc[-1].JZDH:
            h_boundary_x = b_jzd.iloc[JZDH-1].X
            h_boundary_y = b_jzd.iloc[JZDH-1].Y
            q_boundary_x = b_jzd.iloc[0].X
            q_boundary_y = b_jzd.iloc[0].Y
            h_xljzd = self.jzd_boundary[(self.jzd_boundary.X == h_boundary_x) & (self.jzd_boundary.Y == h_boundary_y) & ~(self.jzd_boundary.ZDDM == jzd.ZDDM)] # 后面相邻界址点
            q_xljzd = self.jzd_boundary[(self.jzd_boundary.X == q_boundary_x) & (self.jzd_boundary.Y == q_boundary_y) & ~(self.jzd_boundary.ZDDM == jzd.ZDDM)] # 前面相邻界址点
        else:
            h_boundary_x = b_jzd.iloc[JZDH-1].X
            h_boundary_y = b_jzd.iloc[JZDH-1].Y
            q_boundary_x = b_jzd.iloc[JZDH+1].X
            q_boundary_y = b_jzd.iloc[JZDH+1].Y
            h_xljzd = self.jzd_boundary[(self.jzd_boundary.X == h_boundary_x) & (self.jzd_boundary.Y == h_boundary_y) & ~(self.jzd_boundary.ZDDM == jzd.ZDDM)] # 后面相邻界址点
            q_xljzd = self.jzd_boundary[(self.jzd_boundary.X == q_boundary_x) & (self.jzd_boundary.Y == q_boundary_y) & ~(self.jzd_boundary.ZDDM == jzd.ZDDM)] # 前面相邻界址点 
        return b_xljzd,h_xljzd,q_xljzd
 
    def set_zddm(self,zddm):
        self.ZD = self.ZD[self.ZD.ZDDM == zddm]
        self.JZD = self.JZD[self.JZD.ZDDM == zddm]
        
    def get_coordinates(self,one_gdf):
        # @party_gdf:一行GeoDataFrame数据或GeoSeries
        # return 一个整理后的包含内部边界的坐标数据DataFrame
        if not (isinstance(one_gdf, pd.DataFrame) or isinstance(one_gdf, pd.Series)):
            raise TypeError(f'传入的是:{type(one_gdf.geometry.values[0])},需要的是{type(MultiPolygon())}|{type(gpd.GeoDataFrame())}|{type(pd.Series())}')
        if isinstance(one_gdf, pd.Series):
            if isinstance(one_gdf.geometry, MultiPolygon):
                data = mapping(one_gdf.geometry)
                zddm = one_gdf.ZDDM
            else:
                raise TypeError(f'传入的是:{type(one_gdf.geometry)},需要的是{type(MultiPolygon())}')
        if isinstance(one_gdf, pd.DataFrame):
            if one_gdf.shape[0] > 1:
                raise ValueError(f'只接收一行数据,但传入了{one_gdf.shape[0]}行数据')
            if isinstance(one_gdf.geometry.values[0], MultiPolygon):
                data = mapping(one_gdf.geometry.values[0])
                zddm = one_gdf.ZDDM.values[0]
            else:
                raise TypeError(f'传入的是:{type(one_gdf.geometry.values[0])},需要的是{type(MultiPolygon())}')
        def add_index(x_y,value,V):
            # if V == 87:
            #     pass
            x = (np.round(x_y,1)*10).astype('int64')[0]
            y = (np.round(x_y,1)*10).astype('int64')[1]
            temp = [zddm,x,y,x+y,value,V]
            return temp
        
        coor_df = None
        for index,value in enumerate(data['coordinates'][0]):
            if not index:
                coor_df = pd.DataFrame([add_index(np.array(x),index,V) for V,x in enumerate(value[:len(value)-1])],columns=['ZDDM','X','Y','XY','INDEX','JZDH'])
            else:
                coor_df = pd.concat([coor_df,pd.DataFrame([add_index(np.array(x),index,V) for V,x in enumerate(value[:len(value)-1])],columns=['ZDDM','X','Y','XY','INDEX','JZDH'])],ignore_index=True)
        return coor_df
    
    def get_coordinates_index(self,coordinates):
        return coordinates.INDEX.drop_duplicates(ignore_index=True)
    
    def get_zddm(self):
        return self.ZD.ZDDM.drop_duplicates(ignore_index=True)
    
    def get_jzd_boundary(self):
        # 这是一个蒋界址点与边界信息连接的方法
        # @jzd_gdf_:界址点数据
        # @zd_gdf_:宗地数据
        # 界址点和宗地数据必须有ZDDM字段
        for index,row in self.JZD_All.iterrows():
            if index == 0:
                _coordinates = self.get_coordinates(row)
            else:
                _coordinates = pd.concat([_coordinates,self.get_coordinates(row)],ignore_index=True)
        self.JZD[~self.JZD.X.isin(_coordinates.X) | ~self.JZD.Y.isin(_coordinates.Y)].to_excel('没匹配上的界址点.xlsx')
        
        return pd.merge(self.JZD,_coordinates,on=['ZDDM','X','Y'], how='inner'),_coordinates
        
    def add_jzx(self,jzd_gdf_):
        # @jzd_gdf_
        for index,row in jzd_gdf_.iterrows():
            QLRMC = self.ZD[self.ZD.ZDDM.isin(jzd_gdf_.ZDDM)].QLRMC.values[0]
            ZDDM = jzd_gdf_.ZDDM.values[0]
            if index == 0:
                b_jzd,h_xljzd,q_xljzd = self.adjacent_jzdzddm(row)
                # h_xljzd = self.jzd_boundary[self.jzd_boundary.X.isin(jzd_gdf_.tail(1).X) & self.jzd_boundary.Y.isin(jzd_gdf_.tail(1).Y) & ~self.jzd_boundary.ZDDM.isin(jzd_gdf_.ZDDM)] # 后面相邻界址点
                # q_xljzd = self.jzd_boundary[(self.jzd_boundary.X == jzd_gdf_.iloc[1].X) & (self.jzd_boundary.Y == jzd_gdf_.iloc[1].Y) & ~self.jzd_boundary.ZDDM.isin(jzd_gdf_.ZDDM)]   # 前面相邻界址点
                # b_jzd = self.jzd_boundary[(self.jzd_boundary.X == row.X) & (self.jzd_boundary.Y == row.Y) & ~self.jzd_boundary.ZDDM.isin(jzd_gdf_.ZDDM)]   # 本界址点相邻界址点
                self.JZX.loc[self.JZX.shape[0],'ZDDM'] = ZDDM
                self.JZX.loc[self.JZX.shape[0]-1,'QLRMC'] = QLRMC
                if XLQLRZDDM := list(set(b_jzd.ZDDM) & set(q_xljzd.ZDDM)):
                    self.JZX.loc[self.JZX.shape[0]-1,'LZQLRMC'] = self.JZD_All[self.JZD_All.ZDDM == XLQLRZDDM[0]].QLRMC.values[0]
                self.JZX.loc[self.JZX.shape[0]-1,'QSDH'] = jzd_gdf_.JZD_NEW.values[0]
                self.JZX.loc[self.JZX.shape[0]-1,'ZJDH'] = []
                self.JZX.loc[self.JZX.shape[0]-1,'INDEX'] = jzd_gdf_.at[index,'INDEX']
                continue
            if index == jzd_gdf_.shape[0]-1:
                # 终点界址点
                b_jzd,h_xljzd,q_xljzd = self.adjacent_jzdzddm(row)
                if list(set(h_xljzd.ZDDM) & set(q_xljzd.ZDDM)) or (b_jzd.shape[0] == 0):

                    self.JZX.loc[self.JZX.shape[0]-1,'ZJDH'].append(row.JZD_NEW)
                else:
                    self.JZX.loc[self.JZX.shape[0],'ZDDM'] = ZDDM
                    self.JZX.loc[self.JZX.shape[0]-1,'QLRMC'] = QLRMC
                    if XLQLRZDDM := list(set(b_jzd.ZDDM) & set(q_xljzd.ZDDM)):
                        self.JZX.loc[self.JZX.shape[0]-1,'LZQLRMC'] = self.JZD_All[self.JZD_All.ZDDM == XLQLRZDDM[0]].QLRMC.values[0]
                    self.JZX.loc[self.JZX.shape[0]-1,'QSDH'] = row.JZD_NEW
                    self.JZX.loc[self.JZX.shape[0]-1,'ZJDH'] = []
                    self.JZX.loc[self.JZX.shape[0]-2,'ZZDH'] = row.JZD_NEW
                    self.JZX.loc[self.JZX.shape[0]-1,'INDEX'] = jzd_gdf_.at[index,'INDEX']
                
                self.JZX.loc[self.JZX.shape[0]-1,'ZZDH'] = jzd_gdf_.at[0,'JZD_NEW']
                continue
            b_jzd,h_xljzd,q_xljzd = self.adjacent_jzdzddm(row)
            if list(set(h_xljzd.ZDDM) & set(q_xljzd.ZDDM))  or (b_jzd.shape[0] == 0):
                self.JZX.loc[self.JZX.shape[0]-1,'ZJDH'].append(row.JZD_NEW)
            else:
                self.JZX.loc[self.JZX.shape[0],'ZDDM'] = ZDDM
                self.JZX.loc[self.JZX.shape[0]-1,'QLRMC'] = QLRMC
                if XLQLRZDDM := list(set(b_jzd.ZDDM) & set(q_xljzd.ZDDM)):
                    self.JZX.loc[self.JZX.shape[0]-1,'LZQLRMC'] = self.JZD_All[self.JZD_All.ZDDM == XLQLRZDDM[0]].QLRMC.values[0]
                self.JZX.loc[self.JZX.shape[0]-1,'QSDH'] = row.JZD_NEW
                self.JZX.loc[self.JZX.shape[0]-1,'ZJDH'] = []
                self.JZX.loc[self.JZX.shape[0]-2,'ZZDH'] = row.JZD_NEW
                self.JZX.loc[self.JZX.shape[0]-1,'INDEX'] = jzd_gdf_.at[index,'INDEX']
    
    def add_jzx_all(self):
        zddm_df = self.get_zddm()
        for zddm in zddm_df:
            coordinates_index = self.get_coordinates_index(self.JZD[self.JZD.ZDDM == zddm])
            for index in coordinates_index:
                log.info(f"{zddm}-{index}")
                print(f"{zddm}-{index}")
                sel_jzd = self.JZD[(self.JZD.ZDDM == zddm) & (self.JZD.INDEX == index)].reset_index()
                self.add_jzx(sel_jzd)
                
if __name__ == '__main__':
    Ow = Ownership(r'E:\工作文档\SLLJDJZD2.gdb')
    Ow.add_jzx_all()
    Ow.set_zddm('')
    # for index,row in Ow.JZX.iterrows():
    #     if len(row.ZJDH) == 0:
    #         Ow.JZX.loc[index,'ZJDH'] = ''
    #     elif len(row.ZJDH) == 1:
    #         Ow.JZX.loc[index,'ZJDH'] = row.ZJDH[0]
    #     elif len(row.ZJDH) == 2:
    #         Ow.JZX.loc[index,'ZJDH'] = '、'.join(row.ZJDH)
    #     else:
    #         Ow.JZX.loc[index,'ZJDH'] = f"{row.ZJDH[0]}....{row.ZJDH[-1]}"
    Ow.JZX.to_excel('JZX34324.xlsx')
    