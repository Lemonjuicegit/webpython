import math
import sqlite3
import geopandas as gpd
import pandas as pd
from shapely import wkt
from shapely.geometry import  mapping,LineString,Point
class dbExtractsThePhoto:
    def __init__(self, db):
        self.db_path = db
        with sqlite3.connect(db) as con:
            DKJBXX = pd.read_sql("SELECT * FROM DKJBXX",con=con)
            self.DKJBXX = gpd.GeoDataFrame(DKJBXX, geometry=DKJBXX.DKFW.apply(lambda x: wkt.loads(x)),crs="EPSG:4523")
            FJ = pd.read_sql("SELECT * FROM FJ",con=con)
            self.FJ = gpd.GeoDataFrame(FJ, geometry=FJ.apply(lambda row: Point(row.Longitude,row.Latitude),axis=1),crs="EPSG:4490")
            self.FJ = self.FJ.to_crs({'init': 'EPSG:4523'})
            self.imgdf = pd.DataFrame(columns=('DKBSM','FJMC','FJHXZ','PSJD','JYM','URL','X','Y'))
            self.sx = []
    def eq(self,pol,x,y,FW):
        angle_rad = math.radians(-FW-90)
        # 计算直线的斜率
        k = math.tan(angle_rad)
        b = y-k*x

        def find_points(d):
            if d:
                x1 = x +1000/math.sqrt(1+k**2)
            else:
                x1 = x -1000/math.sqrt(1+k**2)
            
            y1=k*x1+b
            return x1,y1
            
        if 0<FW<=180:
            x1,y1=find_points(1)
            line = LineString([(x,y),(x1,y1)])
            self.sx.append(line)
            if line.intersects(pol):
                return True

        elif 180<FW<360:
            x1,y1=find_points(0)
            line = LineString([(x,y),(x1,y1)])
            self.sx.append(line)
            if line.intersects(pol):
                return True
        elif FW==0 or FW==360:
            line = LineString([(x,y),(x,y+1000)])
            self.sx.append(line)
            if line.intersects(pol):
                return True
        return False
    def img(self,save):
        def one_img(row,pol):
            
            eq = self.eq(pol,row.geometry.x,row.geometry.y,row.PSJD)
            if eq:
                self.imgdf.loc[self.imgdf.shape[0]] = [row.DKBSM,row.FJMC,row.FJHXZ,row.PSJD,row.JYM,row.URL,row.geometry.x,row.geometry.y]
            
        def extract(row):
            imgdf = self.FJ[self.FJ.DKBSM	== row.BSM]
            imgdf.apply(lambda img_row: one_img(img_row,row.geometry),axis=1)
        self.DKJBXX.apply(extract,axis=1)
        imgshp = gpd.GeoDataFrame(self.imgdf, geometry=self.imgdf.apply(lambda row: Point(row.X,row.Y),axis=1),crs="EPSG:4523")
        # sx = gpd.GeoSeries(self.sx,crs='EPSG:4523')
        # sx.to_file(save)
        imgshp.to_file(save)
    
    def to_fj(self,save):
        fj = self.FJ.drop('FJ', axis=1)
        fj['X'] = fj.geometry.x
        fj['Y'] = fj.geometry.y
        fj.to_file(save)
    

      
