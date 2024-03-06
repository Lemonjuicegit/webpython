
from pathlib import Path
import pandas as pd
from fastapi import  Request,APIRouter
from pydantic import BaseModel
from starlette.responses import FileResponse
from .adjustArea import AdjustArea
from .. import store
from .. import zip_list
router = APIRouter()


class Args(BaseModel):
    tab_name: str=''
    shp_name: str=''
    KEY:str=''
    end:int = 0 # 结束标识

uploadPath = Path(r"E:\exploitation\webpython\upload")
sendPath = Path(r"E:\exploitation\webpython\send")

@router.post("/init")
def setAdjustArea(args:Args,req: Request):
    ip  = req.client.host
    if ip not in store.use:
        return '用户不存在'
    tab = uploadPath / ip / args.tab_name
    gdb = uploadPath / ip / args.shp_name
    store.use[ip]['AA'] = AdjustArea(tab,gdb,0.001,args.KEY)
    store.use[ip]['AA'].get_boundary()
    store.use[ip]['modify_all'] = store.use[ip]['AA'].modify_all()
    return store.use[ip]['AA'].keycount

@router.post("/modify_all")
def modify_all(args: Args,req: Request):
    ip  = req.client.host
    if ip not in store.use:
        return '用户不存在'
    res = next(store.use[ip]['modify_all'])
    if args.end == 1:
        store.use[ip]['AA'].to_shp(store.sendPath / ip / '修改面积后数据.shp')
        shpfile = list(Path(store.sendPath / ip).glob("修改面积后数据.*"))
        store.zipFile = [store.sendPath / ip / i.name for i in shpfile]
        zip_list(store.zipFile,store.sendPath / ip / '修改面积后数据.zip')
        store.addUseFile(ip,store.sendPath, '修改面积后数据.zip')
        store.zipFile = []
        for i in shpfile:
            store.addUseFile(ip,store.sendPath, i.name)
        store.use[ip]['modify_all'] = store.use[ip]['AA'].modify_all()
        
    return res