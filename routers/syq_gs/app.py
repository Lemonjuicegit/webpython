from fastapi import APIRouter,Request
from pydantic import BaseModel
from .execute import informationGS
from .. import (
    zipDir,
    store,
    use,
    state
)


router = APIRouter()

class Args(BaseModel):
    gs_save:str = ''
    state:int = 0
    
class Global:
    gen_araeAch = None
    gen_noticeGS = None
    
router.post('/informationGS')
async def generate(args: Args, req: Request = None):
    Gs = informationGS('data.xlsx')
    ip = req.client.host
    if args.state == state.GET_READY:
        Global.gen_araeAch = Gs.araeAch_all(args.gs_save)
    elif args.state == state.RES:
        res = await Global.gen_araeAch.send(ip)