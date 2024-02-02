class Head:
    def __init__(self,rowlist=[]) -> None:
        self.HeadList = rowlist
        self.text = '\n'.join(self.HeadList)
        self._DataMark = ''
        self._Version = ''
        self._CoordinateSystemType = ''
        self._Dim = ''
        self._XAxisDirection = ''
        self._YAxisDirection = ''
        self._XYUnit = ''
        self._Spheroid = ''
        self._PrimeMeridian = ''
        self._Projection = ''
        self._Parameters = ''
        self._VerticalDatum = ''
        self._TemporalReferenceSystem = ''
        self._ExtentMin = ''
        self._ExtentMax = ''
        self._MapScale = ''
        self._Offset = ''
        self._Date = ''
        self._Separator = ''
        if rowlist:
            self.setHead()

    def setHead(self):
        '''
        获取头信息:
            DataMark:<数据标识>
            Version:<版本号>
            CoordinateSystemType:<坐标系统类型>
            Dim:<坐标维数>
            XAxisDirection:<X坐标轴方向>
            YAxisDirection:<Y坐标轴方向>
            XYUnit:<平面坐标单位>
            Spheroid:<参考椭球>
            PrimeMeridian:<首子午线>
            Projection:<投影类型>
            Parameters:<投影参数>
            VerticalDatum:<高程基准>
            TemporalReferenceSystem:<时间参照系>
            ExtentMin:<最小坐标>
            ExtentMax:<最大坐标>
            MapScale:<比例尺>
            Offset:<坐标偏移量>
            Date:<土地规划批准时间>
            Separator:<属性字段分割符>
        '''
        head = {v.split(':')[0].lower():(v.split(':')[1] if len(v.split(':')) == 2 else '') for v in self.HeadList}
        self._DataMark = head['datamark']
        self._Version = head['version']
        self._CoordinateSystemType = head['coordinatesystemtype']
        self._Dim = head['dim']
        self._XAxisDirection = head['xaxisdirection']
        self._YAxisDirection = head['yaxisdirection']
        self._XYUnit = head['xyunit']
        self._Spheroid = head['spheroid']
        self._PrimeMeridian = head['primemeridian']
        self._Projection = head['projection']
        self._Parameters = head['parameters']
        self._VerticalDatum = head['verticaldatum']
        self._TemporalReferenceSystem = head['temporalreferencesystem']
        self._ExtentMin = head['extentmin']
        self._ExtentMax = head['extentmax']
        self._MapScale = head['mapscale']
        self._Offset = head['offset']
        self._Date = head['date']
        self._Separator = head['separator']
        
    @property
    def DataMark(self):
        return self._DataMark
    
    @DataMark.setter
    def DataMark(self, value):
        if self.HeadList[0] != value:
            self.HeadList[0] = f"DataMark:{value}"
            self.text = '\n'.join(self.HeadList)
            self._DataMark = value
