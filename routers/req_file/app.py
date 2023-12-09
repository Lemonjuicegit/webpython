
import pandas as pd
from fastapi import  Request, UploadFile,APIRouter
from pydantic import BaseModel
from starlette.responses import FileResponse
from pathlib import Path

from .Djmod import unzip

router = APIRouter()

uploadPath = Path(r"E:\exploitation\webpython\upload")
sendPath = Path(r"E:\exploitation\webpython\send")

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
    

@router.post("req_file/uploadGdbfile")
async def create_upload_gdbfile(file: UploadFile, req: Request):
    assert req.client is not None
    ip = req.client.host
    file_content = await file.read()
    filename = file.filename
    gdbzip = uploadPath / ip / filename
    addUseFile(ip, uploadPath / ip, filename)
    with open(gdbzip, "wb") as buffer:
        buffer.write(file_content)
    unzip(gdbzip, uploadPath / ip)
    addUseFile(ip, uploadPath / ip, f"{filename.split('.')[0]}.gdb")
    return filename
    
@router.post("req_file/upload")
async def create_upload_file(file: UploadFile,filetype:str='', req: Request=None):
    assert req.client is not None
    ip = req.client.host
    file_content = await file.read()
    filename = file.filename
    extractpath = uploadPath / ip / filename
    addUseFile(ip, uploadPath / ip, filename)
    with open(extractpath, "wb") as buffer:
        buffer.write(file_content)
    if filetype == 'gdb':
        unzip(extractpath, uploadPath / ip,'gdb')
        addUseFile(ip, uploadPath / ip, f"{filename.split('.')[0]}.gdb")
        return filename
    filelist = unzip(extractpath, uploadPath / ip)
    for f in filelist:
        addUseFile(ip, uploadPath / ip, f)
    return filename


@router.post("req_file/download")
async def create_download_file(filename, req: Request):
    ip = req.client.host
    # 查找要下载的文件
    path = useFile.value[
        (useFile.value.ip == ip)
        & ((useFile.value.name == filename) | (useFile.value.filename == filename))
    ]
    
    if path.shape[0]:
        return FileResponse(path.path.values[0], filename=path.filename.values[0])
    else:
        return 0
