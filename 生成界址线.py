from pk.Ownership import Ownership
import pandas as pd
import geopandas as gpd
import numpy as np
from pk.Djmod import Djlog,logErr
from shapely.geometry import MultiLineString,mapping,Point,LineString
Ow = Ownership(r'E:\工作文档\SLLJDJZD2.gdb')
boundary = Ow.jzd_boundary.copy()
boundary['ZDDM_INDEX'] = boundary.ZDDM.str.cat(boundary.INDEX.astype(str))
log = Djlog()
add_jzx_all = Ow.add_jzx_all()
for i in add_jzx_all:
    pass
    
JZXDF = Ow.ZJDH_format()
JZXDF['ZDDM_INDEX'] = JZXDF.ZDDM.str.cat(JZXDF.INDEX.astype(str))

zd_node = pd.DataFrame(columns=('QLRMC','ZDDM','INDEX','ZDDM_INDEX','N','X','Y'))
for index,row in Ow.ZD.iterrows():
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

@logErr(log)
def linedef():
    jzx = gpd.GeoDataFrame(columns=[*JZXDF.columns,'geometry'],crs=Ow.ZD.crs)
    line = []
    for index,value in JZXDF.iterrows():
        ZD_boundary = zd_node[zd_node.ZDDM_INDEX == value.ZDDM_INDEX].reset_index()
        q_jzd = Ow.JZD[(Ow.JZD.ZDDM ==value.ZDDM) & (Ow.JZD.JZD_NEW == value.QSDH)]
        z_jzd = Ow.JZD[(Ow.JZD.ZDDM ==value.ZDDM) & (Ow.JZD.JZD_NEW == value.ZZDH)]
        q_line_index = ZD_boundary[(ZD_boundary.int_X==q_jzd.X.values[0]) & (ZD_boundary.int_Y==q_jzd.Y.values[0])].index[0]
        z_line_index = ZD_boundary[(ZD_boundary.int_X==z_jzd.X.values[0]) & (ZD_boundary.int_Y==z_jzd.Y.values[0])].index[0]
        xy_list = []
        if q_line_index>z_line_index:
            max_index = np.max(ZD_boundary.index.values)
            q_line_df = ZD_boundary.iloc[q_line_index:max_index+1]
            h_line_df = ZD_boundary.iloc[0:z_line_index+1]
            xy_list = list(zip(list(q_line_df.X),list(q_line_df.Y))) + list(zip(list(h_line_df.X),list(h_line_df.Y)))
        elif q_line_index == z_line_index:
            xy_list = list(zip(list(ZD_boundary.X),list(ZD_boundary.Y)))
        else:  
            line_df = ZD_boundary[q_line_index:z_line_index+1]
            xy_list = list(zip(list(line_df.X),list(line_df.Y)))
        # jzx = pd.concat([jzx,gpd.GeoDataFrame({**value,'geometry':LineString(xy_list)},crs=Ow.ZD.crs)],ignore_index=True)
        if xy_list:
            jzx.loc[index] = [*[v for v in value.values],LineString(xy_list)]
            
    jzx.to_file('jzx.shp',encoding='gb18030')

linedef()