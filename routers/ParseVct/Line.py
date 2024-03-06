import geopandas as gpd
from shapely import LineString,Polygon


class Line:
    def __init__(self,rowlist='',crs=None) -> None:
        self.gdf = gpd.GeoDataFrame(columns=['BSM','YSDM','TXBXBM','TZLX','count','XDLX','PointCount','geometry'],crs=crs)
        self.polygon = gpd.GeoDataFrame(columns=['BSM','X','Y','geometry'],crs=crs)
        self.text = ''
        n = 0
        index = 0
        while n<len(rowlist):
            self.gdf.loc[index] = [
                rowlist[n],
                rowlist[n+1],
                rowlist[n+2],
                rowlist[n+3],
                rowlist[n+4],
                rowlist[n+5],
                rowlist[n+6],
                LineString([[float(row.split(',')[0]),float(row.split(',')[1])] for row in rowlist[n+7:int(rowlist[n+6])+n+7]])
            ]
            n += int(rowlist[n+6])+8
            index+=1
    
    def to_shp(self,save):
        self.gdf.to_file(save,encoding='gb18030')
        
    def getText(self):
        def TextList(row):
            self.text+=f"{row['BSM']}\n{row['YSDM']}\n{row['TXBXBM']}\n{row['TZLX']}\n{row['count']}\n{row['XDLX']}\n{row['PointCount']}\n"
            self.text+='\n'.join([f"{xy[0]},{xy[1]}" for xy in list(zip(row['geometry'].xy[0],row['geometry'].xy[0]))])
            self.text+='\n0'    
        self.gdf.apply(TextList,axis=1)
        return self.text
    
    def getPolygon(self):
        def _polygon(row):
            xy = [*zip(row['geometry'].xy[0],row['geometry'].xy[1])]
            xy.append((row['geometry'].xy[0][0],row['geometry'].xy[1][0]))
            pol = Polygon(xy)
            self.polygon.loc[self.polygon.shape[0]] = [row['BSM'],pol.centroid.x,pol.centroid.y,pol]
        self.gdf.apply(_polygon,axis=1)
        return self.polygon
        