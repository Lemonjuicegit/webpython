import uvicorn, json, shutil
import pandas as pd
import geopandas as gpd
from fastapi import FastAPI, Request, UploadFile,File
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pathlib import Path
from Api import Api
from pk.Djmod import Djlog
from pk.土地权属界线认可书 import generate_jxrks_all
from pk.界址点成果表 import generate_jzdcg_all
from pk.所有权面积分类 import Area_table_all
from pk import Myerr, zip_list, unzip,Stacking
from routers import adjustArea
from routers import store

app = FastAPI()
useApi: dict[str, Api] = {}
log = Djlog()
# app.mount("/index", StaticFiles(directory="static", html=True), name="index")

app.include_router(
    adjustArea.router,
    prefix="/adjustarea",
    tags=["adjustarea"],
)

# store.uploadPath = Path(r"E:\exploitation\webpython\upload")
# store.sendPath = Path(r"E:\exploitation\webpython\send")

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
    stacking_shp:str = "" # 需要堆叠融合的矢量数据
    stacking_field:str = "" # 堆叠优先级字段
    isorderly:int = 0 # 堆叠优先级字段是否有序
    stack_layer: str = '' # 堆叠融合图层

class useFile:
    value = pd.DataFrame(columns=["ip","directory", "filename", "path", "type", "name"])  # coulmns: directory,filename,path,type,name
    zipFile = []

def addUseFile(ip, directory: Path, filename: str):
    store.useFile.loc[store.useFile.shape[0]] = [
        ip,
        str(directory),
        filename,
        str(directory / filename),
        filename.split(".")[1],
        filename.split(".")[0],
    ]
    
@app.exception_handler(Exception)
async def http_exception_handler(req: Request, exc):
    return {"detail": exc.detail}

@app.post(f"{rewrite}/uploadGdbfile")
async def create_upload_gdbfile(file: UploadFile, req: Request):
    assert req.client is not None
    ip = req.client.host
    log.info(f"create_upload_file:{ip}")
    file_content = await file.read()
    filename = file.filename
    gdbzip = store.uploadPath / ip / filename
    store.addUseFile(ip, filename)
    with open(gdbzip, "wb") as buffer:
        buffer.write(file_content)
    unzip(gdbzip, store.uploadPath / ip)
    store.addUseFile(ip, f"{filename.split('.')[0]}.gdb")
    return filename
    
@app.post(f"{rewrite}/upload")
async def create_upload_file(file:UploadFile=File(),filetype:str='', req: Request=None):
    assert req.client is not None
    ip = req.client.host
    log.info(f"create_upload_file:{ip}")
    file_content = await file.read()
    filename = file.filename
    extractpath = store.uploadPath / ip / filename
    store.addUseFile(ip, filename)
    with open(extractpath, "wb") as buffer:
        buffer.write(file_content)
    if filetype == 'gdb':
        unzip(extractpath, store.uploadPath / ip,'gdb')
        store.addUseFile(ip, f"{filename.split('.')[0]}.gdb")
        return filename
    elif filetype == 'shp':
        filelist = unzip(extractpath, store.uploadPath / ip)
        for f in filelist:
            store.addUseFile(ip, f)
    return filename


@app.post(f"{rewrite}/download")
async def create_download_file(filename, req: Request):
    ip = req.client.host
    log.info(f"create_download_file:{ip}")
    # 查找要下载的文件
    path = store.useFile[
        (store.useFile.ip == ip)
        & ((store.useFile.name == filename) | (store.useFile.filename == filename))
    ]
    if path.shape[0]:
        return FileResponse(path.path.values[0], filename=path.filename.values[0])
    else:
        return 0


@app.post(f"{rewrite}/add_use")
async def add_use(req: Request):
    '''
    '''
    ip = req.client.host
    useApi[ip] = Api()
    store.use[ip] = {}
    (store.uploadPath /ip).mkdir(exist_ok=True, parents=True)
    (store.sendPath / ip).mkdir(exist_ok=True, parents=True)
    print(f"{ip}连接")
    log.info(f"{ip}连接")
    return 1


@app.get(f"{rewrite}/disconnect")
async def use_disconnect(req: Request = None):
    ip = req.client.host
    if (store.uploadPath / ip).exists():
        shutil.rmtree(store.uploadPath /ip)
    if (store.sendPath / ip).exists():
        shutil.rmtree(store.sendPath / ip)
    store.useFile = store.useFile[store.useFile.ip != ip]
    print(f"{ip}断开")
    log.info(f"{ip}断开")


@app.post(f"{rewrite}/createOwnership")
async def createOwnership(args: Args, req: Request = None):
    ip = req.client.host
    if (store.uploadPath / ip / f"{args.gdb}.gdb").exists():
        res = useApi[ip].createOwnership(store.uploadPath / ip / f"{args.gdb}.gdb")
        useApi[ip].gdb = store.uploadPath / ip / f"{args.gdb}.gdb"
        useApi[ip].jzx = useApi[ip].Ow.add_jzx_all()
        return res
    else:
        return "数据库加载失败"


@app.post(f"{rewrite}/get_zdcount")
async def get_zdcount(req: Request = None):
    ip = req.client.host
    return useApi[ip].Ow.zdcount


@app.post(f"{rewrite}/createLine")
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


@app.post(f"{rewrite}/set_jzx_excel")
async def set_jzx_excel(args: Args, req: Request = None):
    ip = req.client.host
    return useApi[ip].set_jzx_excel(args.jzxpath)


@app.post(f"{rewrite}/to_JZXexcel")
async def to_JZXexcel(req: Request = None):
    ip = req.client.host
    if not useApi[ip].Ow:
        return "没有设置数据库"
    if not useApi[ip].Ow.JZX.shape[0]:
        return "没有界址线数据"
    else:
        useApi[ip].Ow.to_JZXexcel(store.sendPath / ip/ "JZX.xlsx")
        store.addUseFile(ip, store.sendPath / ip, "JZX.xlsx")
    return "界址线数据导出成功"


@app.post(f"{rewrite}/set_zdct")
async def set_zdct(args: Args, req: Request = None):
    ip = req.client.host
    useApi[ip].jpg_zdct = args.zdct


@app.post(f"{rewrite}/generate_qjdc")
async def generate_qjdc(args: Args, req: Request = None):
    ip = req.client.host
    return useApi[ip].generate_qjdc(args.control, store.sendPath / ip)


@app.post(f"{rewrite}/handleGenerate_qjdc")
async def handleGenerate_qjdc(args: Args, req: Request = None):
    ip = req.client.host
    res = next(useApi[ip].handleGenerate_qjdc)
    store.zipFile.append(store.sendPath / ip / f"{res}.docx")
    store.addUseFile(ip, store.sendPath / ip, f"{res}.docx")
    if args.end == 1:
        zip_list(store.zipFile, store.sendPath / ip / "权籍调查表.zip")
        store.addUseFile(ip, store.sendPath / ip, "权籍调查表.zip")
        store.zipFile = []
        return useApi[ip].generate_qjdc(args.control, store.sendPath / ip)
    return res


@app.post(f"{rewrite}/get_qlrcount")
async def get_qlrcount(req: Request = None):
    ip = req.client.host
    if not useApi[ip].Ow:
        return "没有设置数据库"
    return useApi[ip].Ow.qlrcount


@app.post(f"{rewrite}/generate_rks")
async def generate_rks(args: Args, req: Request = None):
    ip = req.client.host
    jzxpath = store.useFile[store.useFile.filename == args.jzxpath].directory.values[0]
    jzx_df = pd.read_excel(jzxpath)
    jzx_df = jzx_df.fillna("")
    useApi[ip].rks = generate_jxrks_all(
        useApi[ip].Ow.ZD, useApi[ip].Ow.JZD, jzx_df, useApi[ip].savepath, args.control
    )
    return "界址线数据读取成功"


@app.post(f"{rewrite}/jxrks_all")
async def jxrks_all(args: Args, req: Request = None):
    ip = req.client.host
    if not useApi[ip].Ow.qlrcount:
        return "没有权利人信息"
    res = next(useApi[ip].rks)
    if args.end == 1:
        jzxpath = store.useFile[
            (store.useFile.id == ip) & (store.useFile.filename == args.jzxpath)
        ].path.values[0]
        jzx_df = pd.read_excel(jzxpath)
        jzx_df = jzx_df.fillna("")
        useApi[ip].rks = generate_jxrks_all(
            useApi[ip].Ow.ZD, useApi[ip].Ow.JZD, jzx_df, store.sendPath / ip, args.control
        )
    return res


@app.post(f"{rewrite}/generate_jzdcg")
async def generate_jzdcg(req: Request = None):
    ip = req.client.host
    # 创建界址点成果表生成器
    jzd = gpd.read_file(useApi[ip].gdb, layer="JZD")
    useApi[ip].jzdcg = generate_jzdcg_all(jzd, useApi[ip].Ow.ZD, store.sendPath / ip)
    return "界址点数据加载完成"


@app.post(f"{rewrite}/jzdcg_all")
async def jzdcg_all(args: Args, req: Request = None):
    # 导出所有界址点成果表
    ip = req.client.host
    if not useApi[ip].Ow.qlrcount:
        return "没有权利人信息"
    res = next(useApi[ip].jzdcg)
    store.zipFile.append(store.sendPath / ip / f"{res}.xlsx")
    store.addUseFile(ip, store.sendPath / ip, f"{res}.xlsx")
    if args.end == 1:
        jzd = gpd.read_file(useApi[ip].gdb, layer="JZD")
        zip_list(store.zipFile, store.sendPath / ip / "界址点成果表.zip")
        store.addUseFile(ip, store.sendPath / ip, "界址点成果表.zip")
        store.zipFile = []
        useApi[ip].rks = generate_jzdcg_all(jzd, useApi[ip].Ow.ZD, store.sendPath / ip)
    return res


@app.post(f"{rewrite}/generate_Area")
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
    useApi[ip].classifiedArea = Area_table_all(df, df_fda, store.sendPath / ip)
    return df.shape[0]


@app.post(f"{rewrite}/Area_table")
async def Area_table(args: Args, req: Request = None):
    ip = req.client.host
    res = next(useApi[ip].Area_table_all)
    datapath = store.useFile[
        (store.useFile.id == ip) & (store.useFile.filename == args.datapath)
    ].path.values[0]
    df_fda = store.useFile[
        (store.useFile.id == ip) & (store.useFile.filename == args.datapath)
    ].path.values[0]
    if args.end == 1:
        df = pd.read_excel(datapath)
        useApi[ip].classifiedArea = Area_table_all(df, df_fda, store.sendPath / ip)
    return res


@app.post(f"{rewrite}/to_jzxshp")
async def to_jzxshp(req: Request = None):
    ip = req.client.host
    useApi[ip].Ow.to_jzxshp(store.sendPath / ip / "JZXshp.shp")
    store.addUseFile(ip, store.sendPath / ip, "JZXshp.shp")
    return "导出界址线矢量成功"

@app.post(f"{rewrite}/stacking")
async def stacking(args: Args,req: Request = None):
    ip = req.client.host
    shp = store.uploadPath / ip / args.stacking_shp
    try:
        if args.stack_layer:
            st = Stacking(shp,args.stacking_field,args.isorderly,args.stack_layer)
        else:
            st = Stacking(shp,args.stacking_field,args.isorderly)
    except Myerr as e:
        return str(e)
    st.all_(store.sendPath / ip / '堆叠融合.shp')
    shpfile = list(Path(store.sendPath / ip).glob("堆叠融合.*"))
    for i in shpfile:
        store.addUseFile(ip, store.sendPath / ip, i.name)
    zip_list(shpfile,store.sendPath / ip / '堆叠融合.zip')
    store.addUseFile(ip, store.sendPath / ip,'堆叠融合.zip')
    return '堆叠融合处理完成'


if __name__ == "__main__":
    @app.post(f"{rewrite}/test")
    def test(req: Request):
        ip = req.client.host
        print(ip)
        return "test"
    uvicorn.run(app, host="192.168.2.194", port=23333)
