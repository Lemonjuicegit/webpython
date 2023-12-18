
from pathlib import Path
import pandas as pd
from fastapi import  Request,APIRouter
from pydantic import BaseModel
from starlette.responses import FileResponse
from .adjustArea import AdjustArea
from .. import store
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
    if ip not in store:
        return '用户不存在'
    tab = uploadPath / ip / args.tab_name
    gdb = uploadPath / ip / args.shp_name
    store.use[ip]['AA'] = AdjustArea(tab,gdb,0.0005,args.KEY)
    store[ip]['AA'].get_boundary()
    store[ip]['modify_all'] = store[ip]['AA'].modify_all(sendPath / ip / '修改后数据.shp')
    return store[ip]['AA'].keycount

@router.post("/modify_all")
def modify_all(args: Args,req: Request):
    ip  = req.client.host
    if ip not in store:
        return '用户不存在'
    res = next(store[ip]['modify_all'])
    if args.end == 1:
        shpfile = list(Path(sendPath / ip).glob("修改后数据.*"))
        for i in shpfile:
            store.addUseFile(store,ip, sendPath / ip, i.name)
        store[ip]['modify_all'] = store[ip]['AA'].modify_all(sendPath / ip / '修改后数据.shp')
    return res