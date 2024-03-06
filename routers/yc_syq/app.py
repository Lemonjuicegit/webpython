import json
import pandas as pd
import geopandas as gpd
from fastapi import  Request,APIRouter
from pydantic import BaseModel
from Api import Api
from .Djmod import Djlog
from .import generate_jxrks_all
from . import generate_jzdcg_all
from . import Area_table_all
from . import  zip_list
from .. import zipDir
from . import qzb_
from .. import store
from .. import use
from . import Ownership
from . import generate_qjdc_
router = APIRouter()
log = Djlog()

class Args(BaseModel):
    gdb: str = ""
    end: int = 0
    jzxpath: str = ""
    zdct: str = ""
    control: dict = {}
    Areadatapath: str = ""  # 所有权面积分类excel数据路径
    df_fda: str = ""  # 面积统计表飞地excel数据路径
    stacking_shp:str = "" # 需要堆叠融合的矢量数据
    stacking_field:str = "" # 堆叠优先级字段
    isorderly:int = 0 # 堆叠优先级字段是否有序
    stack_layer: str = '' # 堆叠融合图层

@router.post("/createOwnership")
async def createOwnership(args: Args, req: Request = None):
    ip = req.client.host
    if (store.uploadPath / ip / f"{args.gdb}.gdb").exists():
        use.useApi[ip].Ow = Ownership(store.uploadPath / ip / f"{args.gdb}.gdb")
        use.useApi[ip].gdb = store.uploadPath / ip / f"{args.gdb}.gdb"
        use.useApi[ip].jzx = use.useApi[ip].Ow.add_jzx_all()
        return '数据库设置成功'
    else:
        return "数据库加载失败"

@router.post("/get_zdcount")
async def get_zdcount(req: Request = None):
    ip = req.client.host
    return use.useApi[ip].Ow.zdcount

@router.post("/createLine")
async def createLine(args: Args, req: Request = None):
    ip = req.client.host
    res = next(use.useApi[ip].jzx)
    if args.end:
        use.useApi[ip].jzx = use.useApi[ip].Ow.add_jzx_all()
        use.useApi[ip].Ow.JZX = use.useApi[ip].Ow.ZJDH_format()
        return json.dumps(
            {
                "data": json.loads(use.useApi[ip].Ow.JZX.to_json(orient="records")),
                "res": res,
            }
        )
    return res


@router.post("/set_jzx_excel")
async def set_jzx_excel(args: Args, req: Request = None):
    ip = req.client.host
    return use.useApi[ip].set_jzx_excel(args.jzxpath)


@router.post("/to_JZXexcel")
async def to_JZXexcel(req: Request = None):
    ip = req.client.host
    if not use.useApi[ip].Ow:
        return "没有设置数据库"
    if not use.useApi[ip].Ow.JZX.shape[0]:
        return "没有界址线数据"
    else:
        use.useApi[ip].Ow.to_JZXexcel(store.sendPath / ip/ "JZX.xlsx")
        store.addUseFile(ip,store.sendPath, "JZX.xlsx")
    return "界址线数据导出成功"


@router.post("/set_zdct")
async def set_zdct(args: Args, req: Request = None):
    ip = req.client.host
    use.useApi[ip].jpg_zdct = args.zdct


@router.post("/generate_qjdc")
async def generate_qjdc(args: Args, req: Request = None):
    ip = req.client.host
    return use.useApi[ip].generate_qjdc(args.control, store.sendPath / ip,generate_qjdc_)


@router.post("/handleGenerate_qjdc")
async def handleGenerate_qjdc(args: Args, req: Request = None):
    ip = req.client.host
    res = next(use.useApi[ip].handleGenerate_qjdc)
    use.useApi[ip].zipFile.append(store.sendPath / ip / f"{res}.docx")
    store.addUseFile(ip, store.sendPath, f"{res}.docx")
    if args.end == 1:
        zip_list(use.useApi[ip].zipFile, store.sendPath / ip / "权籍调查表.zip")
        store.addUseFile(ip, store.sendPath, "权籍调查表.zip")
        use.useApi[ip].zipFile = []
    return res


@router.post("/get_qlrcount")
async def get_qlrcount(req: Request = None):
    ip = req.client.host
    if not use.useApi[ip].Ow:
        return "没有设置数据库"
    return use.useApi[ip].Ow.qlrcount


@router.post("/generate_rks")
async def generate_rks(args: Args, req: Request = None):
    ip = req.client.host
    jzxpath = store.useFile[store.useFile.filename == args.jzxpath].path.values[0]
    jzx_df = pd.read_excel(jzxpath)
    jzx_df = jzx_df.fillna("")
    use.useApi[ip].rks = generate_jxrks_all(
        use.useApi[ip].Ow.ZD, use.useApi[ip].Ow.JZD, jzx_df, store.sendPath / ip, args.control
    )
    return "界址线数据读取成功"


@router.post("/jxrks_all")
async def jxrks_all(args: Args, req: Request = None):
    ip = req.client.host
    if not use.useApi[ip].Ow.qlrcount:
        return "没有权利人信息"
    res = next(use.useApi[ip].rks)
    use.useApi[ip].zipFile.append(store.sendPath / ip / f"{res}.docx")
    store.addUseFile(ip, store.sendPath, f"{res}.docx")
    if args.end == 1:
        zip_list(use.useApi[ip].zipFile, store.sendPath / ip / "认可书.zip")
        store.addUseFile(ip, store.sendPath, "认可书.zip")
        use.useApi[ip].zipFile = []
        jzxpath = store.useFile[ (store.useFile.ip == ip) & (store.useFile.filename == args.jzxpath)].path.values[0]
        jzx_df = pd.read_excel(jzxpath)
        jzx_df = jzx_df.fillna("")
        use.useApi[ip].rks = generate_jxrks_all(
            use.useApi[ip].Ow.ZD, use.useApi[ip].Ow.JZD, jzx_df, store.sendPath / ip, args.control
        )
    return res


@router.post("/generate_jzdcg")
async def generate_jzdcg(req: Request = None):
    ip = req.client.host
    # 创建界址点成果表生成器
    jzd = gpd.read_file(use.useApi[ip].gdb, layer="JZD")
    use.useApi[ip].jzdcg = generate_jzdcg_all(jzd, use.useApi[ip].Ow.ZD, store.sendPath / ip)
    return "界址点数据加载完成"


@router.post("/jzdcg_all")
async def jzdcg_all(args: Args, req: Request = None):
    # 导出所有界址点成果表
    ip = req.client.host
    if not use.useApi[ip].Ow.qlrcount:
        return "没有权利人信息"
    res = next(use.useApi[ip].jzdcg)
    use.useApi[ip].zipFile.append(store.sendPath / ip / f"{res}.xlsx")
    store.addUseFile(ip, store.sendPath, f"{res}.xlsx")
    if args.end == 1:
        jzd = gpd.read_file(use.useApi[ip].gdb, layer="JZD")
        zip_list(use.useApi[ip].zipFile, store.sendPath / ip / "界址点成果表.zip")
        store.addUseFile(ip, store.sendPath, "界址点成果表.zip")
        use.useApi[ip].zipFile = []
        use.useApi[ip].rks = generate_jzdcg_all(jzd, use.useApi[ip].Ow.ZD, store.sendPath / ip)
    return res


@router.post("/generate_Area")
async def generate_Area(args: Args, req: Request = None):
    ip = req.client.host
    if not (store.sendPath / ip).exists():
        return 0
    Areadatapath = store.useFile[
        (store.useFile.id == ip) & (store.useFile.filename == args.Areadatapath)
    ].path.values[0]
    df = pd.read_excel(Areadatapath)
    df_fda = store.useFile[
        (store.useFile.id == ip) & (store.useFile.filename == args.df_fda)
    ].path.values[0]
    use.useApi[ip].classifiedArea = Area_table_all(df, df_fda, store.sendPath / ip)
    return df.shape[0]


@router.post("/Area_table")
async def Area_table(args: Args, req: Request = None):
    ip = req.client.host
    res = next(use.useApi[ip].Area_table_all)
    datapath = store.useFile[
        (store.useFile.id == ip) & (store.useFile.filename == args.datapath)
    ].path.values[0]
    df_fda = store.useFile[
        (store.useFile.id == ip) & (store.useFile.filename == args.datapath)
    ].path.values[0]
    if args.end == 1:
        df = pd.read_excel(datapath)
        use.useApi[ip].classifiedArea = Area_table_all(df, df_fda, store.sendPath / ip)
    return res


@router.post("/to_jzxshp")
async def to_jzxshp(req: Request = None):
    ip = req.client.host
    use.useApi[ip].Ow.to_jzxshp(store.sendPath / ip / "JZXshp.shp")
    store.addUseFile(ip, store.sendPath, "JZXshp.shp")
    return "导出界址线矢量成功"

@router.post("/qzb_one")
async def qzb_one(args: Args, req: Request = None):
    ip: str = req.client.host
    qzb_file = store.useFile[store.useFile.filename == args.qzb_data].path.values[0]
    use.useApi[ip].qzb = qzb_(qzb_file, store.sendPath / ip,args.choose)
    return next(use.useApi[ip].qzb)

@router.post("/generate_qzb")
async def generate_qzb(args: Args, req: Request = None):
    ip = req.client.host
    res = next(use.useApi[ip].qzb)
    store.addUseFile(ip, store.sendPath, f"{res}.xlsx")
    if args.end == 1:
        zipDir(str(store.sendPath / ip / '签字资料'), store.sendPath / ip / "签字资料.zip")
        store.addUseFile(ip, store.sendPath, "签字资料.zip")
        qzb_file = store.useFile[store.useFile.filename == args.qzb_data].path.values[0]
        use.useApi[ip].zipFile = []
        use.useApi[ip].qzb = qzb_(qzb_file, store.sendPath / ip,args.choose)
    return res


