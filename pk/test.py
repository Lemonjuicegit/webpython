from . import groupby
import pandas as pd

data = pd.read_excel(r"E:\工作文档\中山路街道tfh.xlsx")

aa = groupby(data,['TFH'],'count')
