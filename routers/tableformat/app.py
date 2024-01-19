
from fastapi import APIRouter,Request
from pydantic import BaseModel
from .xmcb import xmcb
from .. import store
router = APIRouter()

class Args(BaseModel):
    filename:str= ''
    
@router.post('/xmcb')
def get_xmcb(args: Args,req:Request):
    ip = req.client.host
    directory = store.useFile[(store.useFile.ip == ip) & (store.useFile.filename == args.filename)].directory.values[0]
    xmcb(directory,store.sendPath/ip/args.filename)
    store.addUseFile(ip,store.sendPath,args.filename)
    return '完成!'