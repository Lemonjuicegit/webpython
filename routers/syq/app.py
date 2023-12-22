from fastapi import APIRouter

import uvicorn, json, shutil
import pandas as pd
import geopandas as gpd
from fastapi import FastAPI, Request, UploadFile
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pathlib import Path
from Api import Api
from pk.Djmod import Djlog
from pk.土地权属界线认可书 import generate_jxrks_all
from pk.界址点成果表 import generate_jzdcg_all
from pk.所有权面积分类 import Area_table_all
from .Djmod import zip_list

router = APIRouter()

app = FastAPI()
useApi: dict[str, Api] = {}
log = Djlog()

uploadPath = Path(r"E:\exploitation\webpython\upload")
sendPath = Path(r"E:\exploitation\webpython\send")

# rewrite = '/api'
rewrite = ''

class Args(BaseModel):
    gdb: str = ""
    end: int = 0
    jzxpath: str = ""
    zdct: str = ""
    control: dict = {}
    Areadatapath: str = ""  # 所有权面积分类excel数据路径
    df_fda: str = ""  # 面积统计表飞地excel数据路径

class useFile:
    value = pd.DataFrame(columns=["ip","directory", "filename", "path", "type", "name"])  # coulmns: directory,filename,path,type,name
    zipFile = []


def addUseFile(ip, directory: Path, filename: str):
    useFile.value.loc[useFile.value.shape[0]] = [
        ip,
        str(directory),
        filename,
        str(directory / filename),
        filename.split(".")[1],
        filename.split(".")[0],
    ]


@router.get(f"{rewrite}/disconnect")
async def use_disconnect(req: Request = None):
    ip = req.client.host
    if (uploadPath / ip).exists():
        shutil.rmtree(uploadPath /ip)
    if (sendPath / ip).exists():
        shutil.rmtree(sendPath / ip)
    useFile.value = useFile.value[useFile.value.ip != ip]
    log.info(f"{ip}断开")


@router.post(f"{rewrite}/createOwnership")
async def createOwnership(args: Args, req: Request = None):
    ip = req.client.host
    if (uploadPath / ip / f"{args.gdb}.gdb").exists():
        res = useApi[ip].createOwnership(uploadPath / ip / f"{args.gdb}.gdb")
        useApi[ip].gdb = uploadPath / ip / f"{args.gdb}.gdb"
        useApi[ip].jzx = useApi[ip].Ow.add_jzx_all()
        return res
    else:
        return "数据库加载失败"


@router.post(f"{rewrite}/get_zdcount")
async def get_zdcount(req: Request = None):
    ip = req.client.host
    return useApi[ip].Ow.zdcount


@router.post(f"{rewrite}/createLine")
async def createLine(args: Args, req: Request = None):
    ip = req.client.host
    res = next(useApi[ip].jzx)
    if args.end:
        useApi[ip].jzx = useApi[ip].Ow.add_jzx_all()
        useApi[ip].Ow.JZX = useApi[ip].Ow.ZJDH_format()
        return json.dumps(
            {
                "data": json.loads(useApi[ip].Ow.JZX.to_json(orient="records")),
                "res": res,
            }
        )
    return res


@router.post(f"{rewrite}/set_jzx_excel")
async def set_jzx_excel(args: Args, req: Request = None):
    ip = req.client.host
    return useApi[ip].set_jzx_excel(args.jzxpath)


@router.post(f"{rewrite}/to_JZXexcel")
async def to_JZXexcel(req: Request = None):
    ip = req.client.host
    if not useApi[ip].Ow:
        return "没有设置数据库"
    if not useApi[ip].Ow.JZX.shape[0]:
        return "没有界址线数据"
    else:
        useApi[ip].Ow.to_JZXexcel(sendPath / ip/ "JZX.xlsx")
        addUseFile(ip, sendPath / ip, "JZX.xlsx")
    return "界址线数据导出成功"


@router.post(f"{rewrite}/set_zdct")
async def set_zdct(args: Args, req: Request = None):
    ip = req.client.host
    useApi[ip].jpg_zdct = args.zdct


@router.post(f"{rewrite}/generate_qjdc")
async def generate_qjdc(args: Args, req: Request = None):
    ip = req.client.host
    return useApi[ip].generate_qjdc(args.control, sendPath / ip)


@router.post(f"{rewrite}/handleGenerate_qjdc")
async def handleGenerate_qjdc(args: Args, req: Request = None):
    ip = req.client.host
    res = next(useApi[ip].handleGenerate_qjdc)
    useFile.zipFile.append(sendPath / ip / f"{res}.docx")
    addUseFile(ip, sendPath / ip, f"{res}.docx")
    if args.end == 1:
        zip_list(useFile.zipFile, sendPath / ip / "权籍调查表.zip")
        addUseFile(ip, sendPath / ip, "权籍调查表.zip")
        useFile.zipFile = []
        return useApi[ip].generate_qjdc(args.control, sendPath / ip)
    return res


@router.post(f"{rewrite}/get_qlrcount")
async def get_qlrcount(req: Request = None):
    ip = req.client.host
    if not useApi[ip].Ow:
        return "没有设置数据库"
    return useApi[ip].Ow.qlrcount


@router.post(f"{rewrite}/generate_rks")
async def generate_rks(args: Args, req: Request = None):
    ip = req.client.host
    jzx_df = pd.read_excel(args.jzxpath)
    jzx_df = jzx_df.fillna("")
    useApi[ip].rks = generate_jxrks_all(
        useApi[ip].Ow.ZD, useApi[ip].Ow.JZD, jzx_df, useApi[ip].savepath, args.control
    )
    return "界址线数据读取成功"


@router.post(f"{rewrite}/jxrks_all")
async def jxrks_all(args: Args, req: Request = None):
    ip = req.client.host
    if not useApi[ip].Ow.qlrcount:
        return "没有权利人信息"
    res = next(useApi[ip].rks)
    if args.end == 1:
        jzxpath = useFile.value[
            (useFile.value.id == ip) & (useFile.value.filename == args.jzxpath)
        ].path.values[0]
        jzx_df = pd.read_excel(jzxpath)
        jzx_df = jzx_df.fillna("")
        useApi[ip].rks = generate_jxrks_all(
            useApi[ip].Ow.ZD, useApi[ip].Ow.JZD, jzx_df, sendPath / ip, args.control
        )
    return res


@router.post(f"{rewrite}/generate_jzdcg")
async def generate_jzdcg(req: Request = None):
    ip = req.client.host
    # 创建界址点成果表生成器
    jzd = gpd.read_file(useApi[ip].gdb, layer="JZD")
    useApi[ip].jzdcg = generate_jzdcg_all(jzd, useApi[ip].Ow.ZD, sendPath / ip)
    return "界址点数据加载完成"


@router.post(f"{rewrite}/jzdcg_all")
async def jzdcg_all(args: Args, req: Request = None):
    # 导出所有界址点成果表
    ip = req.client.host
    if not useApi[ip].Ow.qlrcount:
        return "没有权利人信息"
    res = next(useApi[ip].jzdcg)
    useFile.zipFile.append(sendPath / ip / f"{res}.xlsx")
    addUseFile(ip, sendPath / ip, f"{res}.xlsx")
    if args.end == 1:
        jzd = gpd.read_file(useApi[ip].gdb, layer="JZD")
        zip_list(useFile.zipFile, sendPath / ip / "界址点成果表.zip")
        addUseFile(ip, sendPath / ip, "界址点成果表.zip")
        useFile.zipFile = []
        useApi[ip].rks = generate_jzdcg_all(jzd, useApi[ip].Ow.ZD, sendPath / ip)
    return res


@router.post(f"{rewrite}/generate_Area")
async def generate_Area(args: Args, req: Request = None):
    ip = req.client.host
    if not (sendPath / ip).exists():
        return 0
    Areadatapath = useFile.value[
        (useFile.value.id == ip) & (useFile.value.filename == args.Areadatapath)
    ].path.values[0]
    df = pd.read_excel(Areadatapath)
    df_fda = useFile.value[
        (useFile.value.id == ip) & (useFile.value.filename == args.df_fda)
    ].path.values[0]
    useApi[ip].classifiedArea = Area_table_all(df, df_fda, sendPath / ip)
    return df.shape[0]


@router.post(f"{rewrite}/Area_table")
async def Area_table(args: Args, req: Request = None):
    ip = req.client.host
    res = next(useApi[ip].Area_table_all)
    datapath = useFile.value[
        (useFile.value.id == ip) & (useFile.value.filename == args.datapath)
    ].path.values[0]
    df_fda = useFile.value[
        (useFile.value.id == ip) & (useFile.value.filename == args.datapath)
    ].path.values[0]
    if args.end == 1:
        df = pd.read_excel(datapath)
        useApi[ip].classifiedArea = Area_table_all(df, df_fda, sendPath / ip)
    return res


@router.post(f"{rewrite}/to_jzxshp")
async def to_jzxshp(req: Request = None):
    ip = req.client.host
    useApi[ip].Ow.to_jzxshp(sendPath / ip / "JZXshp.shp")
    addUseFile(ip, sendPath / ip, "JZXshp.shp")
    return "导出界址线矢量成功"



if __name__ == "__main__":
    @router.post(f"{rewrite}/test")
    def test(req: Request):
        ip = req.client.host
        print(ip)
        return "test"
    uvicorn.run(app, host="192.168.2.194", port=8000)
