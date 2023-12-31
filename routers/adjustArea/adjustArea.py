import geopandas as gpd
import pandas as pd
from shapely.geometry import  mapping, Polygon,Point
import math
from ..Djmod import Djlog

log = Djlog()

class quadraticEquation:
    def __init__(self, x1, y1, x2, y2) -> None:
        self.len: float = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        self.k = (y2 - y1) / (x2 - x1)
        self.b = y1 - self.k * x1

    def x(self, y):
        return (y - self.b) / self.k

    def y(self, x):
        return self.k * x + self.b


class AdjustArea:
    def __init__(self, tab, gdb, coefficient, KEY, precision=0) -> None:
        """
        tab (str): 调整面积数据表格的路径
        gdb (str): GeoDataFrame的路径
        coefficient (float): 调整系数
        KEY (str):tab与gdb的对应 键值
        precision (int): 精度
        """
        self.stat = pd.read_excel(tab)
        self.gdb: gpd.GeoDataFrame = gpd.read_file(gdb)
        self.gdb['INDEX'] = self.gdb.index
        self.keycount = self.stat.shape[0]
        self.boun_d = pd.DataFrame(columns=("X", "Y", "JZDH"))
        self.get_boundary()
        self.coefficient = coefficient
        self.KEY = KEY
        self.key_value_list = set()
        self.precision = precision

    def modify(self, KEY):
        try:
            area = self.stat[self.stat[self.KEY] == KEY].MJ.values[0]
        except:
            log.err(f"未找到{KEY}的修改面积")
            return "未找到{KEY}的修改面积"
        pol_list = self.gdb[self.gdb[self.KEY] == KEY].geometry.values
        area_list = [ar for ar in pol_list.area]
        index_list = []
        
        while not index_list:
            pol = pol_list[area_list.index(max(area_list))]
            area_list.remove(max(area_list))
            xy_zip = zip(pol.exterior.xy[0], pol.exterior.xy[1])
            for index, xy in enumerate(xy_zip):
                count = self.count_xy(int(xy[0]), int(xy[1]))
                if count == 1:
                    index_list.append({"index": index, "x": xy[0], "y": xy[1]})
        
        self.move( KEY, index_list, self.coefficient, area,pol)

        return f"已修改{KEY}面积"


    def modify_all(self):
        KEY = self.stat[self.KEY].drop_duplicates().values
        for k in KEY:
            log.info(k)
            res = self.modify(k)
            yield res
    def to_shp(self,save):
        self.gdb.to_file(save,encoding="gb18030")
    def move(self, KEY, n, lenth, area,pol):
        """
        @centriod: 质心坐标
        @n: 能够移动点的列表
        @x: 要移动x的坐标
        @y: 要移动y的坐标
        @len: 要移动的距离
        @area: 移动后要对比的面积
        """
        pol_list = self.gdb[self.gdb[self.KEY] == KEY].geometry.values
        INDEX = self.gdb[self.gdb[self.KEY] == KEY].geometry[self.gdb.geometry.area == pol.area].index[0]
        area_list = [ar for ar in pol_list.area]
        # pol = pol_list[area_list.index(max(area_list))]
        area_list.remove(pol.area)
        area_all = sum(area_list) # 其他面的总面积
        area_ = round(pol.area+area_all, self.precision) - area
        one = 0  # 记录首次进入循环
        l_mix = lenth/10 # 最小调整距离
        forcount = 0  # 记录循环次数
        while area_:
            if one:
                # 移动
                if (lenth != l_mix) and (area_<1):
                    lenth = lenth-l_mix
            one = 1    
            # 记录差额面积是正数还是负数
            symbol = -1 if area_ < 0 else 1
            for t,i in enumerate(n):
                forcount += 1
                if pol.intersects(Point(i['x'] + lenth, i['y'] + lenth)):
                    pol = self.upPolygon(pol, i["index"], i['x'] + lenth*symbol, i['y'] + lenth*symbol)
                    n[t]['x'] = i['x'] + lenth*symbol
                    n[t]['y'] = i['y'] + lenth*symbol
                else:
                    pol = self.upPolygon(pol, i["index"], i['x'] - lenth*symbol, i['y'] - lenth*symbol)
                    n[t]['x'] = i['x'] - lenth*symbol
                    n[t]['y'] = i['y'] - lenth*symbol
                if abs(area_) < 0.02:
                    pass
                area_ = round(pol.area+area_all, self.precision) - area
                if symbol == -1:
                    if not (area_ < 0):
                        break
                elif symbol == 1:
                    if not (area_ > 0):
                        break
                elif not area_:
                    break
            if forcount > 10000:
                log.err(f"{KEY}超出最大循环次数")
                break
        self.gdb.loc[INDEX,'geometry'] = pol
        return 0

    def upPolygon(self, p, n, x, y):
        arrx = p.exterior.xy[0]
        arry = p.exterior.xy[1]
        arrx[n] = x
        arry[n] = y
        interxy = []
        if len(p.interiors):
            for i in p.interiors:
                interxy.append(list(zip(i.xy[0],i.xy[1])))
        return Polygon(zip(arrx, arry),interxy)

    def get_coordinates(self, one_gdf):
        # @party_gdf:一行GeoDataFrame数据或GeoSeries
        # return 一个整理后的包含内部边界的坐标数据DataFrame
        data = mapping(one_gdf.geometry)
        coor_df = pd.DataFrame(columns=("X", "Y", "JZDH"))
        for index, value in enumerate(data["coordinates"][0]):
            coor_df.loc[coor_df.shape[0]] = [int(value[0]), int(value[1]), index]
        return coor_df[:-1]

    def get_boundary(self):
        # 所有宗地边界坐标
        for index, row in self.gdb.iterrows():
            if index == 0:
                self.boun_d = self.get_coordinates(row)
            else:
                self.boun_d = pd.concat(
                    [self.boun_d, self.get_coordinates(row)], ignore_index=True
                )

    def count_xy(self, x, y):
        return self.boun_d[(self.boun_d["X"] == x) & (self.boun_d["Y"] == y)].shape[0]
