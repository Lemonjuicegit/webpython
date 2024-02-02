import geopandas as gpd

class Line:
    def __init__(self,rowlist:str='') -> None:
        self._LineList = rowlist