from pathlib import Path
import pandas as pd
import geopandas as gpd
import webview
from Api import Api
from pk.Djmod import Djlog,logErr
from pk.土地权属界线认可书 import generate_jxrks_all
from pk.界址点成果表 import generate_jzdcg_all
from pk.所有权面积分类 import Area_table_all

api = Api()
log = Djlog()
def get_file_path(file_types_list=['*']):
  # 打开文件
  file_types = (f"file (*.{';*.'.join(file_types_list)})",)

  file_path = window.create_file_dialog(webview.OPEN_DIALOG,file_types=file_types)
  return file_path

def get_folder_path():
  # 打开目录
  folder_path = window.create_file_dialog(webview.FOLDER_DIALOG)
  return folder_path


def set_save(savepath):
  api.savepath = savepath

@logErr(log)
def createOwnership(gdb):
  res = api.createOwnership(gdb)
  api.gdb = gdb
  api.jzx = api.Ow.add_jzx_all()
  return res

@logErr(log)
def get_zdcount():
  return api.Ow.zdcount

@logErr(log)
def createLine(end):
  res = next(api.jzx)
  if end == 1:
    api.jzx = api.Ow.add_jzx_all()
    api.Ow.JZX = api.Ow.ZJDH_format()
    return api.Ow.JZX.to_json()
  return res

def set_jzx_excel(jzxpath):
  try:
    return api.set_jzx_excel(jzxpath)
  except BaseException as e:
    return str(e)

@logErr(log)
def to_JZXexcel():
  if not api.Ow:
    return '没有设置数据库'
  if not api.Ow.JZX.shape[0]:
    return '没有界址线数据'
  if not api.savepath:
    api.Ow.to_JZXexcel('JZX.xlsx',index=False)
  else:
    api.Ow.to_JZXexcel(Path(api.savepath) / 'JZX.xlsx',index=False)
  return '界址线数据导出成功'


def set_zdct(zdct):
  api.jpg_zdct = zdct

@logErr(log)
def generate_qjdc(control):
  return api.generate_qjdc(control)

@logErr(log)
def handleGenerate_qjdc(end):
  res = next(api.handleGenerate_qjdc)
  if end == 1:
    api.generate_qjdc()
  return res

def get_qlrcount():
  if not api.Ow:
    return '没有设置数据库'
  return api.Ow.qlrcount

@logErr(log)
def generate_rks(gdb,jzxpath,savepath):
  jzx_df = pd.read_excel(jzxpath)
  jzx_df = jzx_df.fillna('')
  jzd = gpd.read_file(gdb,layer='JZD')
  api.rks =  generate_jxrks_all(api.Ow.ZD,jzd,jzx_df,savepath)
  return '界址线数据读取成功'

@logErr(log)
def jxrks_all(end,gdb='',jzxpath='',savepath=''):
  if not api.Ow.qlrcount:
    return '没有权利人信息'
  res = next(api.rks)
  if end == 1:
    jzx_df = pd.read_excel(jzxpath)
    jzx_df = jzx_df.fillna('')
    jzd = gpd.read_file(gdb,layer='JZD')
    api.rks =  generate_jxrks_all(api.Ow.ZD,jzd,jzx_df,savepath)
  return res

@logErr(log)
def generate_jzdcg(gdb,save_path):
  if not save_path:
    return 0
  jzd = gpd.read_file(gdb,layer='JZD')
  api.jzdcg = generate_jzdcg_all(jzd,api.Ow.ZD,save_path)
  return '界址点数据加载完成'

@logErr(log)
def jzdcg_all(end=0,gdb='',savepath=''):
    if not api.Ow.qlrcount:
      return '没有权利人信息'
    res = next(api.jzdcg)
    if end == 1:
      jzd = gpd.read_file(gdb,layer='JZD')
      api.rks =  generate_jzdcg_all(jzd,api.Ow.ZD,savepath)
    return res

def generate_Area(datapath,df_fda,savepath=''):
  if not savepath:
    return 0
  df = pd.read_excel(datapath)
  api.classifiedArea = Area_table_all(df,df_fda,savepath)
  return df.shape[0]
  
def Area_table(end=0,datapath='',df_fda='',savepath=''):
    res = next(api.Area_table_all)
    if end == 1:
      df = pd.read_excel(datapath)
      api.classifiedArea =  Area_table_all(df,df_fda,savepath)
    return res

def expose(window):
  funlist = [
    get_file_path,
    get_folder_path,
    set_save,
    createOwnership,
    createLine,
    get_zdcount,
    set_jzx_excel,
    to_JZXexcel,
    set_zdct,
    generate_qjdc,
    handleGenerate_qjdc,
    get_qlrcount,
    generate_rks,
    jxrks_all,
    generate_jzdcg,
    jzdcg_all,
    generate_Area,
    Area_table
  ]
  window.expose(*funlist)
  for name in funlist:
    window.evaluate_js(f'pywebview.api.{name}')

# window = webview.create_window('所有权资料生成', 'http://localhost:5173/',resizable=False,width=1200,height=800)
window = webview.create_window('所有权资料生成', './dist/index.html',resizable=False,width=1200,height=800)

webview.start(expose,window)


