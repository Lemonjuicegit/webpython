import re
from .tool import reElementSplit,reElement
from .Comment import Comment
from .Head import Head
from .FeatureCode import FeatureCode
from .TableStructure import TableStructure
from .Point import Point
from .Line import Line
from .Polygon import Polygon
from .Annotation import Annotation
from .Topology import Topology
from .Attribute import Attribute
from .Style import Style


class Vct:
    def __init__(self,filePath) -> None:
        self.filePath = filePath
        with open(self.filePath,'r') as f:
            self.vct_str = f.read()
        self.Comment = Comment(reElementSplit(self.vct_str,'Comment'))
        self.Head = Head(reElementSplit(self.vct_str,'Head'))
        self.FeatureCode = FeatureCode(reElementSplit(self.vct_str,'FeatureCode'))
        self.TableStructure = TableStructure(reElementSplit(self.vct_str,'TableStructure'))
        self.Point = Point(reElementSplit(self.vct_str,'Point'))
        self.Line = Line(reElementSplit(self.vct_str,'Line'))
        self.Polygon = Polygon(reElementSplit(self.vct_str,'Polygon'))
        self.Annotation = Annotation(reElementSplit(self.vct_str,'Annotation'))
        self.Topology = Topology(reElementSplit(self.vct_str,'Topology'))
        self.Attribute = Attribute(reElementSplit(self.vct_str,'Attribute'))
        self.Style = Style(reElementSplit(self.vct_str,'Style'))
     
                 
if __name__ == "__main__":
    vct = Vct(r'E:\工作文档\(500104)2023年度国土变更调查数据库更新成果\更新数据包\标准格式数据\2001H2023500104GX.vct')