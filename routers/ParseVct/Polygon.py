import geopandas as gpd
from shapely import LineString,Polygon
class Polygon:
    '''
    BSM标识码:
    YSDM要素代码
    TXBXBM图形表现编码:
        建议使用《市(地)级土地利用总体规划制图规范》、《县级土地利用总体规划制图规范》、《乡(镇)级土地利用总体规划制图规范》
        中要素的表达图式，但在制图规范中并没有提供相应的编码，用户可自行编码，但要提交一个编码对照表；或直接使用预定义的保留编码“Unknown”。
    TZLX面的特征类型:
        1表示由直接坐标表示的面对象，100表示由间接坐标表示的面对象。土地利用规划面状数据采用间接坐标表示的面对象。
    标识点X坐标,标识点Y坐标:
        土地利用规划面状数据采用间接坐标交换。
    JJZBMGCLX间接坐标面构成类型:
        21表示引用线对象构成的面，22表示引用面对象构成的面。
    count对象的个数
    DXBSH对象标识号:
        对象标识号8个一行，以逗号“，”分开，总数目为对象的项数。以0表示不相连的对象间的分隔标识，分隔标识计入对象的项数中。
        要注意线对象标识号的正负号，负号表示该线对象反向
    '''
    def __init__(self,line,crs=None,rowlist:str='') -> None:
        self._PolygonList = rowlist
        self.gdf = gpd.GeoDataFrame(columns=['BSM','YSDM','TXBXBM','TZLX','X','Y','JJZBMGCLX','count','DXBSH','geometry'],crs=crs)
        n = 0
        while n<len(self._PolygonList):
            try:
                if len(rowlist[n+7].split(',')) == 1:
                    line
                    xy = [*zip(row['geometry'].xy[0],row['geometry'].xy[1])]
                    xy.append((row['geometry'].xy[0][0],row['geometry'].xy[1][0]))
                    pol = Polygon()
                self.gdf.loc[self.gdf.shape[0]] = [
                    rowlist[n],
                    rowlist[n+1],
                    rowlist[n+2],
                    rowlist[n+3],
                    rowlist[n+4].split(',')[0],
                    rowlist[n+4].split(',')[1],
                    rowlist[n+5],
                    rowlist[n+6],
                    rowlist[n+7],
                    line[line.BSM == rowlist[n+7]].geometry.values[0]
                ]
                n+=9
            except:
                pass