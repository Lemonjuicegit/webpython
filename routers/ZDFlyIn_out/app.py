
from pathlib import Path
import pandas as pd
from fastapi import  Request,APIRouter
from pydantic import BaseModel
from starlette.responses import FileResponse
from .ZDFlyIn_out import ZDFlyIn_out
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