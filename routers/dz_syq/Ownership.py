import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import MultiPolygon,mapping,LineString
class Ownership:
    def __init__(self,gdbpath):
        self.ZD = gpd.read_file(gdbpath,layer='ZD').fillna('')
        # self.ZD = self.ZD[self.ZD.QLRMC == '双石镇丁家岩村楠竹林村民小组']
        self.JZD = gpd.read_file(gdbpath,layer='JZD').fillna('')
        self.JZD['X'] = np.round(self.JZD.geometry.x*10).astype('int64')
        self.JZD['Y'] = np.round(self.JZD.geometry.y*10).astype('int64')
        # self.JZD = self.JZD[self.JZD.QLRMC == '双石镇丁家岩村楠竹林村民小组']
        # self.get_coordinates(self.ZD)
        self.JZD_All = gpd.read_file(gdbpath,layer='ZD_All')
        # self.JZD_All = self.JZD_All[self.JZD_All.ZDDM == 'JA3711']
        self.zdcount = self.ZD.shape[0]
        self.qlrcount = self.ZD.QLRMC.drop_duplicates().shape[0]
        self.JZX = pd.DataFrame(columns=('ZDDM','QLRMC','LZQLRMC','QSDH','ZJDH','ZZDH','INDEX','BXZ','BCM','BSM','XLXZ','XLCM','XLSM'))
        self.JZD,self.jzd_boundary = self.get_jzd_boundary()
        self.JZD.sort_values(by=['ZDDM','PX'],inplace=True)
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
        self.ZD = self.ZD[self.ZD.ZDDM.isin(zddm)]
        self.JZD = self.JZD[self.JZD.ZDDM.isin(zddm)]
        
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
            temp = [zddm,*(np.round(x_y*10)).astype('int64'),value,V]
            return temp
        
        # coor_df = pd.DataFrame(columns=['ZDDM','X','Y','INDEX','JZDH'])

        for index,value in enumerate(data['coordinates'][0]):
            if not index:
                coor_df = pd.DataFrame([add_index(np.array(x),index,V) for V,x in enumerate(value[:len(value)-1])],columns=['ZDDM','X','Y','INDEX','JZDH'])
            else:
                coor_df = pd.concat([coor_df,pd.DataFrame([add_index(np.array(x),index,V) for V,x in enumerate(value[:len(value)-1])],columns=['ZDDM','X','Y','INDEX','JZDH'])],ignore_index=True)
        return coor_df
    
    def get_coordinates_index(self,coordinates):
        return coordinates.INDEX.drop_duplicates(ignore_index=True)
    
    def get_zddm(self):
        return self.ZD.ZDDM.drop_duplicates(ignore_index=True)
    
    def get_jzd_boundary(self):
        # 这是一个将界址点与边界信息连接的方法
        # @jzd_gdf_:界址点数据
        # @zd_gdf_:宗地数据
        # 界址点和宗地数据必须有ZDDM字段
        _coordinates = pd.DataFrame()
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
            b_jzd,h_xljzd,q_xljzd = self.adjacent_jzdzddm(row)
            if index == 0:

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
                if self.JZX.loc[self.JZX.shape[0]-1,'QSDH'] == jzd_gdf_.at[0,'JZD_NEW']:
                    self.JZX.loc[self.JZX.shape[0]-1,'ZJDH'].remove(jzd_gdf_.tail(1).JZD_NEW.values[0])
                    self.JZX.loc[self.JZX.shape[0]-1,'ZZDH'] = jzd_gdf_.tail(1).JZD_NEW.values[0]
                    self.JZX.loc[self.JZX.shape[0],'ZDDM'] = ZDDM
                    self.JZX.loc[self.JZX.shape[0]-1,'QLRMC'] = QLRMC
                    if XLQLRZDDM := list(set(b_jzd.ZDDM) & set(q_xljzd.ZDDM)):
                        self.JZX.loc[self.JZX.shape[0]-1,'LZQLRMC'] = self.JZD_All[self.JZD_All.ZDDM == XLQLRZDDM[0]].QLRMC.values[0]
                    self.JZX.loc[self.JZX.shape[0]-1,'QSDH'] = jzd_gdf_.tail(1).JZD_NEW.values[0]
                    self.JZX.loc[self.JZX.shape[0]-1,'ZJDH'] = []
                    self.JZX.loc[self.JZX.shape[0]-1,'INDEX'] = jzd_gdf_.at[index,'INDEX']
                self.JZX.loc[self.JZX.shape[0]-1,'ZZDH'] = jzd_gdf_.at[0,'JZD_NEW']
                continue
            
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
    def to_JZXexcel(self,path):
        self.JZX.to_excel(path,index=False)
    
    def add_jzx_all(self):
        zddm_df = self.get_zddm()
        for zddm in zddm_df:
            coordinates_index = self.get_coordinates_index(self.JZD[self.JZD.ZDDM == zddm])
            for index in coordinates_index:
                sel_jzd = self.JZD[(self.JZD.ZDDM == zddm) & (self.JZD.INDEX == index)].reset_index()
                self.add_jzx(sel_jzd)
            yield f"正在生成:{zddm}"
    
    def to_jzxshp(self,savepath):
        JZXDF = self.ZJDH_format()
        JZXDF['ZDDM_INDEX'] = JZXDF.ZDDM.str.cat(JZXDF.INDEX.astype(str))
        jzx = gpd.GeoDataFrame(columns=[*JZXDF.columns,'geometry'],crs=self.ZD.crs) # type: ignore
        zd_node = pd.DataFrame(columns=('QLRMC','ZDDM','INDEX','ZDDM_INDEX','N','X','Y'))
        for index,row in self.ZD.iterrows():
            geojson = mapping(row.geometry)
            n = 0
            for index,value in enumerate(geojson['coordinates'][0]):
                zd_node_row = [{'QLRMC':row.QLRMC,'ZDDM':row.ZDDM,'INDEX':index,'ZDDM_INDEX':row.ZDDM+str(index),'N':n+1,'X':coor[0],'Y':coor[1]} for n,coor in enumerate(value[:len(value)-1])]
                if not zd_node.shape[0]:
                    zd_node = pd.DataFrame(zd_node_row)
                else:
                    zd_node = pd.concat([zd_node,pd.DataFrame(zd_node_row)],ignore_index=True)
        zd_node['int_X'] = np.round(zd_node.X*10).astype('int64')
        zd_node['int_Y'] = np.round(zd_node.Y*10).astype('int64')
        for index,value in JZXDF.iterrows():
            ZD_boundary = zd_node[zd_node.ZDDM_INDEX == value.ZDDM_INDEX].reset_index()
            q_jzd = self.JZD[(self.JZD.ZDDM ==value.ZDDM) & (self.JZD.JZD_NEW == value.QSDH)]
            z_jzd = self.JZD[(self.JZD.ZDDM ==value.ZDDM) & (self.JZD.JZD_NEW == value.ZZDH)]
            q_line_index = ZD_boundary[(ZD_boundary.int_X==q_jzd.X.values[0]) & (ZD_boundary.int_Y==q_jzd.Y.values[0])].index[0]
            z_line_index = ZD_boundary[(ZD_boundary.int_X==z_jzd.X.values[0]) & (ZD_boundary.int_Y==z_jzd.Y.values[0])].index[0]
            xy_list = []
            if q_line_index>=z_line_index:
                max_index = np.max(ZD_boundary.index.values)
                q_line_df = ZD_boundary.iloc[q_line_index:max_index+1]
                h_line_df = ZD_boundary.iloc[0:z_line_index+1]
                xy_list = list(zip(list(q_line_df.X),list(q_line_df.Y))) + list(zip(list(h_line_df.X),list(h_line_df.Y)))
            else:  
                line_df = ZD_boundary[q_line_index:z_line_index+1]
                xy_list = list(zip(list(line_df.X),list(line_df.Y)))
            jzx.loc[index] = [*[v for v in value.values],LineString(xy_list)]
        jzx.to_file(savepath,encoding='gb18030',crs=self.ZD.crs)
    
    def ZJDH_format(self):
        jzxcopy = self.JZX.copy()
        for index,row in jzxcopy.iterrows():
            if len(row.ZJDH) == 0:
                jzxcopy.loc[index,'ZJDH'] = ''
            elif len(row.ZJDH) == 1:
                jzxcopy.loc[index,'ZJDH'] = row.ZJDH[0]
            elif len(row.ZJDH) == 2:
                jzxcopy.loc[index,'ZJDH'] = '、'.join(set(row.ZJDH))
            else:
                jzxcopy.loc[index,'ZJDH'] = f"{row.ZJDH[0]}...{row.ZJDH[-1]}"
        return jzxcopy.fillna('')
    
                
if __name__ == '__main__':
    Ow = Ownership(r'E:\工作文档\SLLJDJZD2.gdb')
    Ow.set_zddm('三教镇郝家坝村邓家岩村民小组')
    Ow.add_jzx_all()
    Ow.ZJDH_format()
    Ow.JZX.to_excel('JZX34324.xlsx')
    
