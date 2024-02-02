
from fastapi import  Request,APIRouter
from pydantic import BaseModel
from . import ZDFlyOut,ZDFlyIn
from .. import store

router = APIRouter()


class Args(BaseModel):
    FrData: str=''
    FcData: str=''
    end:int = 0 # 结束标识

    
@router.post("/fc")
async def fc(args: Args, req: Request = None):
    ip = req.client.host
    dataPath = store.useFile[store.useFile.filename == args.FcData].path
    if len(dataPath) < 1:
        return 0
    frfcDf = ZDFlyOut(dataPath.values[0])
    frfcDf.to_excel(store.sendPath / ip / 'fc.xlsx',index=False)
    store.addUseFile(ip, store.sendPath, 'fc.xlsx')
    return 1

@router.post("/fr")
async def fr(args: Args, req: Request = None):
    ip = req.client.host
    
    dataPath = store.useFile[store.useFile.filename == args.FrData].path
    if len(dataPath) < 1:
        return 0
    frfcDf = ZDFlyIn(dataPath.values[0])
    frfcDf.to_excel(store.sendPath / ip / 'fr.xlsx',index=False)
    store.addUseFile(ip, store.sendPath, 'fr.xlsx')
    return 1