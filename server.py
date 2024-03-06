import uvicorn, json, shutil
import pandas as pd
from fastapi import FastAPI, Request, UploadFile,File
from pydantic import BaseModel
from starlette.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pathlib import Path
from Api import Api
from pk.Djmod import Djlog
from pk.所有权面积分类 import Area_table_all
from pk import Myerr, zip_list, unzip,Stacking
from routers import use
from routers import adjustArea
from routers import tableformat
from routers import store
from routers import dz_syq
from routers import yc_syq
from routers import ZDFlyIn_out
from routers import test

app = FastAPI()
log = Djlog()
produce = 1

if produce:
    app.mount("/index", StaticFiles(directory="static", html=True), name="index")
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
    rewrite = '/api'
else:
    rewrite = ''
app.include_router(adjustArea.router,prefix=f"{rewrite}/adjustarea",tags=["adjustarea"],)
app.include_router(tableformat.router,prefix=f"{rewrite}/tableformat",tags=["tableformat"])
app.include_router(dz_syq.router,prefix=f"{rewrite}/dz_syq",tags=["dz_syq"])
app.include_router(yc_syq.router,prefix=f"{rewrite}/yc_syq",tags=["yc_syq"])
app.include_router(ZDFlyIn_out.router,prefix=f"{rewrite}/ZDFlyIn_out",tags=["ZDFlyIn_out"])
app.include_router(test.router,prefix=f"{rewrite}/test",tags=["test"])

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

@app.exception_handler(Exception)
async def http_exception_handler(req: Request, exc):
    log.err(str(exc))
    return 'err'

@app.post(f"{rewrite}/uploadGdbfile")
async def create_upload_gdbfile(file: UploadFile, req: Request):
    assert req.client is not None
    ip = req.client.host
    log.info(f"create_upload_file:{ip}")
    file_content = await file.read()
    filename = file.filename
    gdbzip = store.uploadPath / ip / filename
    store.addUseFile(ip,store.uploadPath, filename)
    with open(gdbzip, "wb") as buffer:
        buffer.write(file_content)
    unzip(gdbzip, store.uploadPath / ip)
    store.addUseFile(ip,store.uploadPath, f"{filename.split('.')[0]}.gdb")
    return filename
    
@app.post(f"{rewrite}/upload")
async def create_upload_file(file:UploadFile=File(),filetype:str='', req: Request=None):
    ip = req.client.host
    log.info(f"upload:{ip}-{file.filename}")
    file_content = await file.read()
    filename = file.filename
    extractpath = store.uploadPath / ip / filename
    store.addUseFile(ip,store.uploadPath, filename)
    with open(extractpath, "wb") as buffer:
        buffer.write(file_content)
    if filetype == 'gdb':
        unzip(extractpath, store.uploadPath / ip,'gdb')
        store.addUseFile(ip,store.uploadPath, f"{filename.split('.')[0]}.gdb")
        return filename
    elif filetype == 'shp':
        filelist = unzip(extractpath, store.uploadPath / ip)
        for f in filelist:
            store.addUseFile(ip,store.uploadPath, f)
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
    use.useApi[ip] = Api()
    use.useApi[ip].savepath = f"E:\\exploitation\\webpython\\send\\{ip}"
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
    use.useApi[ip].classifiedArea = Area_table_all(df, df_fda, store.sendPath / ip)
    return df.shape[0]

@app.post(f"{rewrite}/Area_table")
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
        store.addUseFile(ip, store.sendPath, i.name)
    zip_list(shpfile,store.sendPath / ip / '堆叠融合.zip')
    store.addUseFile(ip, store.sendPath,'堆叠融合.zip')
    return '堆叠融合处理完成'



if __name__ == "__main__":
    uvicorn.run(app, host="192.168.2.51", port=55554)
