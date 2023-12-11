import geopandas as gpd
import pandas as pd
from shapely.geometry import MultiPolygon,mapping,LineString,Polygon
import math
from ..Djmod import Djlog

log = Djlog()
class quadraticEquation:
    def __init__(self,x1,y1,x2,y2) -> None:
        self.len: float = math.sqrt((x1-x2)**2+(y1-y2)**2)
        self.k = (y2-y1)/(x2-x1)
        self.b = y1-self.k*x1
        
    def x(self,y):
        return (y-self.b)/self.k
    
    def y(self,x):
        return self.k*x+self.b

class AdjustArea:
    def __init__(self,tab,gdb,coefficient,KEY,precision=0) -> None:
        """
            tab (str): 调整面积数据表格的路径
            gdb (str): GeoDataFrame的路径
            coefficient (float): 调整系数
            KEY (str):tab与gdb的对应 键值
            precision (int): 精度
        """
        self.stat = pd.read_excel(tab)
        self.gdb:gpd.GeoDataFrame = gpd.read_file(gdb,encoding='gb18030')
        # self.gdb = self.gdb[self.gdb.QLRMC == '统景镇河坝村第18村民小组']
        self.boun_d = pd.DataFrame()
        self.coefficient = coefficient
        self.KEY = KEY
        self.precision = precision
    def modify(self,row):
        area = self.stat[self.stat[self.KEY]==row[self.KEY]].MJ.values[0]
        try:
            xy_zip = zip(row.geometry.exterior.xy[0],row.geometry.exterior.xy[1])
        except NotImplementedError:
            xy_zip = zip(row.geometry.exterior.xy[0],row.geometry.exterior.xy[1])
        index_list = []
        for index,xy in enumerate(xy_zip):
            count = self.count_xy(xy[0],xy[1])
            
            if count == 1:
                index_list.append({'index':index,'x':xy[0],'y':xy[1]})
        eq_area = int(round(row.geometry.area,)) - area
        if eq_area> 0:
            self.move(row[self.KEY],row.geometry.centroid,index_list,self.coefficient,area)

        elif eq_area< 0:
            self.move(row[self.KEY],row.geometry.centroid,index_list,-self.coefficient,area)
    def modify_all(self,save):
        self.gdb.apply(self.modify,axis=1)
        self.gdb.to_file(save,encoding="gb18030")
    def move(self,KEY,centriod,n,lenth,area):
        '''
        @centriod: 质心坐标
        @n: 要移动点的索引
        @x: 要移动x的坐标
        @y: 要移动y的坐标
        @len: 要移动的距离
        @area: 移动后要对比的面积
        '''
        
        pol = self.gdb.geometry[self.gdb[self.KEY] == KEY].values[0]
        area_ = 0
        while round(area_,self.precision) - area:
            for i in n:
                qe = quadraticEquation(centriod.x,centriod.y,i['x'],i['y'])
                position = i['x']-centriod.x
                if position < 0:
                    x = i['x']+lenth
                    y_ = qe.y(x)
                    pol=self.upPolygon(pol,i['index'],x,y_)
                elif position > 0:
                    x = i['x']-lenth
                    y_ = qe.y(x)
                    pol=self.upPolygon(pol,i['index'],x,y_)
                    
                area_ = pol.area
                log.info(round(area_,self.precision) - area)
                if not (round(area_,self.precision) - area):
                    break
        self.gdb.geometry[self.gdb[self.KEY] == KEY] = pol
        return 0
            
    def upPolygon(self,p,n,x,y):
        arrx = p.boundary.xy[0]
        arry = p.boundary.xy[1]
        arrx[n] = x
        arry[n] = y
        return Polygon(zip(arrx,arry))
        
    
    def get_coordinates(self,one_gdf):
        # @party_gdf:一行GeoDataFrame数据或GeoSeries
        # return 一个整理后的包含内部边界的坐标数据DataFrame
        data = mapping(one_gdf.geometry)
        coor_df = pd.DataFrame(columns=('X','Y','JZDH'))
        for index,value in enumerate(data['coordinates'][0]):
            coor_df.loc[coor_df.shape[0]] = [value[0],value[1],index]
        return coor_df[:-1]
    def get_boundary(self):
        # 所有宗地边界坐标
        
        for index,row in self.gdb.iterrows():
            if index == 0:
                self.boun_d = self.get_coordinates(row)
            else:
                self.boun_d = pd.concat([self.boun_d,self.get_coordinates(row)],ignore_index=True)
    
    def count_xy(self,x,y):
        return self.boun_d[(self.boun_d['X'] == x) | (self.boun_d['Y'] == y)].shape[0]
                


