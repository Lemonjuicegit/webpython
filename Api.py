import pandas as pd
import geopandas as gpd
from pk import Sign
from pk.areaClassification import exportArea
from pk.Ownership import Ownership
from pk.不动产权籍调查表 import generate_qjdc
class Api:
  def __init__(self) -> None:
    self.result = None
    self.temmp = None
    self.exportAreaLen = 0
    self.Ow = None
    self.gdb = None
    self.jzx = None     # 直接生成的界址线生成器
    self.jzx_df = None  # 认可书要使用的界址线信息
    self.handleGenerate_qjdc = None
    self.savepath = None
    self.jpg_zdct = None
    self.rks = None  # 认可书生成器
    self.jzdcg = None  # 界址点成果表生成器
    self.classifiedArea = None # 面积分类表生成器
    self.classifiedAreaCount = 0

  def getSign_date(self,xlsx_teb):
    self.result = Sign.get_date(xlsx_teb)
    
  def exportArea(self,datapath,df_fda):
    return exportArea(datapath,df_fda)
  
  def createOwnership(self,gdb):
    self.Ow = Ownership(gdb)
    field_zd = set(self.Ow.ZD.columns)
    field_zd = {'QLRMC','ZDDM','BDCDYH','TFH','飞地坐落','ZDMJ','TDZL','FRDB','LXDH','ZJHM','SZD','SZX','SZB','SZN','FDQK'} - field_zd

    if field_zd:
      self.Ow = None
      return f'宗地字段不正确:{field_zd}'
    else:
      return '数据库设置成功'
  def set_jzx_excel(self,path):
    self.jzx_df = pd.read_excel(path)
    return '界址线设置成功'
    
  def generate_qjdc(self,control):
    zd_data_ = gpd.read_file(self.gdb,layer='ZD')
    zd_data_ = zd_data_.fillna('')
    jzd_data_ = self.Ow.JZD.fillna('')
    jzd_data_.sort_values(by=['ZDDM','PX'], inplace=True)
    self.handleGenerate_qjdc = generate_qjdc(zd_data_,jzd_data_,self.Ow.JZX,self.savepath,self.jpg_zdct,control)
    return self.Ow.qlrcount
