import json,asyncio,math
from pathlib import Path
import pandas as pd
import geopandas as gpd
from multiprocessing import Pool
from fastapi import  Request,APIRouter,WebSocket
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect
from .Djmod import Djlog
from .import ( 
    generate_jxrks_all,
    generate_jzdcg_all,
    Area_table_all,
    zip_list,
    generate_qjdc_,
    generate_qjdcAsync,
    qzb_,
    Ownership
)

from .. import (
    zipDir,
    store,
    use,
    state
)
router = APIRouter()
log = Djlog()

class Args(BaseModel):
    gdb: str = ""
    end: int = 0
    qzb_data:str = "" # 签字表数据表
    choose:dict={}  # 选择要出的签字表
    jzxpath: str = ""
    zdct: str = ""
    control: dict = {}
    Areadatapath: str = ""  # 所有权面积分类excel数据路径
    df_fda: str = ""  # 面积统计表飞地excel数据路径
    precision:int|float = 10 # 界址点匹配精度
    type: str = ""  # websocket发来消息的类型
    state:int = 0
    
async def send_progress(websocket, progress):
    await websocket.send_text(progress)

@router.post("/createOwnership")
async def createOwnership(args: Args, req: Request = None):
    ip = req.client.host
    if (store.uploadPath / ip / f"{args.gdb}.gdb").exists():
        res = use.useApi[ip].createOwnership(store.uploadPath / ip / f"{args.gdb}.gdb",args.precision,Ownership)
        use.useApi[ip].gdb = store.uploadPath / ip / f"{args.gdb}.gdb"
        use.useApi[ip].jzx = use.useApi[ip].Ow.add_jzx_all()
        return res
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
    if args.state == state.GET_READY:
        use.useApi[ip].jzx = use.useApi[ip].Ow.add_jzx_all()
        use.useApi[ip].Ow.JZX = use.useApi[ip].Ow.ZJDH_format()
        return json.dumps(
            {
                "data": json.loads(use.useApi[ip].Ow.JZX.to_json(orient="records")),
                "res": res,
            }
        )
    return res


@router.websocket("/ws/createLine/{client_id}")
async def createLine_socket(websocket: WebSocket,client_id: str):
    await websocket.accept()
    ip = websocket.client.host
    # pool = Pool(10)
    while True:
        try:
            message = json.loads(await websocket.receive_text())
            if message['type'] != 'ping':
                zdcount = use.useApi[ip].Ow.zdcount
                count = 0         
                zddm_df = use.useApi[ip].Ow.get_zddm()
                for zddm in zddm_df:
                    coordinates_index = use.useApi[ip].Ow.get_coordinates_index(use.useApi[ip].Ow.JZD[use.useApi[ip].Ow.JZD.ZDDM == zddm])
                    for index in coordinates_index:
                        sel_jzd = use.useApi[ip].Ow.JZD[(use.useApi[ip].Ow.JZD.ZDDM == zddm) & (use.useApi[ip].Ow.JZD.INDEX == index)].reset_index()
                        await use.useApi[ip].Ow.add_jzx_async(sel_jzd)
                    count += 1
                    await websocket.send_json({'res':f"({count}/{zdcount})|正在生成:{zddm}",'count':math.ceil(count/use.useApi[ip].Ow.zdcount*100),'MessageStatus':state.RES})
                await websocket.send_json( {
                    "data": json.loads(use.useApi[ip].Ow.JZX.to_json(orient="records")),
                    'MessageStatus':state.END
                })
                use.useApi[ip].Ow.JZX = use.useApi[ip].Ow.ZJDH_format()
                await websocket.send_json({'res':'生成界址线完成','count':100,'MessageStatus':state.RES})
            else:
                await websocket.send_json({'res':'ponp','MessageStatus':state.PONP})    
        except asyncio.exceptions.CancelledError:
            log.info('界址线生成连接关闭')  # 连接被关闭时退出循环
        except WebSocketDisconnect as wsd:
            log.err(f'界址线生成连接意外的断开({wsd})')

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
    try:
        res = next(use.useApi[ip].handleGenerate_qjdc)
    except Exception as e:
        log.err(str(e))
    use.useApi[ip].zipFile.append(store.sendPath / ip / f"{res}.docx")
    store.addUseFile(ip, store.sendPath, f"{res}.docx")
    if args.end == 1:
        zip_list(use.useApi[ip].zipFile, store.sendPath / ip / "权籍调查表.zip")
        store.addUseFile(ip, store.sendPath, "权籍调查表.zip")
        use.useApi[ip].zipFile = []
        return 1
    return res

@router.websocket("/ws/generate_qjdc/{client_id}")
async def generate_qjdc_socket(websocket: WebSocket,client_id: str):
    await websocket.accept()
    ip = websocket.client.host

    while True:
        try:
            args = json.loads(await websocket.receive_text())
            if args['type'] != 'ping':
                if use.useApi[ip].Ow is None:
                    await websocket.send_json({'res':'没有加载数据库','count':0,'MessageStatus':state.ERR})
                elif use.useApi[ip].Ow.JZX.shape[0] == 0:
                    await websocket.send_json({'res':'没有生成界址线数据','count':0,'MessageStatus':state.ERR})
                else:
                    zd_data_ = gpd.read_file(use.useApi[ip].gdb,layer='ZD')
                    zd_data_ = zd_data_.fillna('')
                    jzd_data_ = use.useApi[ip].Ow.JZD
                    jzd_data_.sort_values(by=['ZDDM','PX'], inplace=True)
                    qlrcount = use.useApi[ip].Ow.qlrcount
                    count = 0
                    zipFile = []
                    async for res in generate_qjdcAsync(zd_data_,jzd_data_,use.useApi[ip].Ow.JZX, store.sendPath / ip,use.useApi[ip].jpg_zdct,args['control']):
                        count += 1
                        await websocket.send_json({'res':f"({count}/{qlrcount})|{res}",'count':math.ceil(count/qlrcount*100),'MessageStatus':state.RES})
                        zipFile.append(store.sendPath / ip / f"{res}.docx")
                    zip_list(zipFile, store.sendPath / ip / "权籍调查表.zip")
                    store.addUseFile(ip, store.sendPath, "权籍调查表.zip")
                    await websocket.send_json({'res':'生成权籍调查表完成','count':100,'MessageStatus':state.END})
            else:
                await websocket.send_json({'res':'ponp','MessageStatus':state.PONP})
        except asyncio.exceptions.CancelledError:
            log.info('权籍表生成连接关闭')  # 连接被关闭时退出循环
        except WebSocketDisconnect as wsd:
            log.err(f'权籍表生成连接意外的断开({wsd})')

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
        zip_list(use.useApi[ip].zipFile, store.sendPath / ip / "界址点成果表.zip")
        store.addUseFile(ip, store.sendPath, "界址点成果表.zip")
        use.useApi[ip].zipFile = []
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
    shpfile = list(Path(store.sendPath / ip).glob("JZXshp.*"))
    zipFile = [store.sendPath / ip / i.name for i in shpfile]
    zip_list(zipFile,store.sendPath / ip / 'JZX矢量.zip')
    store.addUseFile(ip,store.sendPath, 'JZX矢量.zip')
    return "导出界址线矢量成功"

@router.post("/qzb_one")
async def qzb_one(args: Args, req: Request = None):
    ip: str = req.client.host
    tempdf = store.useFile[store.useFile.filename == args.qzb_data].path
    if len(tempdf) > 0:
        qzb_file = store.useFile[store.useFile.filename == args.qzb_data].path.values[0]
    else:
        log.err(f"qzb_one:{tempdf}")
        return 0
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
        use.useApi[ip].zipFile = []
    return res

@router.get("/hzdh_repeat")
async def hzdh_repeat(req: Request = None):
    ip = req.client.host
    use.useApi[ip].Ow.hzdh_repeat(store.sendPath / ip /'hzdh_repeat.xlsx')
    store.addUseFile(ip, store.sendPath, "hzdh_repeat.xlsx")
    return '检查完成'