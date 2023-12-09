import uvicorn, json, shutil
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from Api import Api
from pk.Djmod import Djlog
from routers import syq
from routers import vectorProcessing
from routers import req_file


app = FastAPI()
useApi: dict[str, Api] = {}
log = Djlog()
app.mount("/index", StaticFiles(directory="static", html=True), name="index")

uploadPath = Path(r"E:\exploitation\webpython\upload")
sendPath = Path(r"E:\exploitation\webpython\send")


# rewrite = '/api'
rewrite = ''

app.include_router(
    syq.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)

@app.exception_handler(Exception)
async def http_exception_handler(req: Request, exc):
    return {"detail": exc.detail}


@app.post(f"{rewrite}/add_use")
async def add_use(req: Request):
    '''
    '''
    ip = req.client.host
    useApi[ip] = Api()
    (uploadPath /ip).mkdir(exist_ok=True, parents=True)
    (sendPath / ip).mkdir(exist_ok=True, parents=True)
    log.info(f"{ip}连接")
    return 1


@app.get(f"{rewrite}/disconnect")
async def use_disconnect(req: Request = None):
    ip = req.client.host
    if (uploadPath / ip).exists():
        shutil.rmtree(uploadPath /ip)
    if (sendPath / ip).exists():
        shutil.rmtree(sendPath / ip)
    useFile.value = useFile.value[useFile.value.ip != ip]
    log.info(f"{ip}断开")



if __name__ == "__main__":
    @app.post(f"{rewrite}/test")
    def test(req: Request):
        ip = req.client.host
        print(ip)
        return "test"
    uvicorn.run(app, host="192.168.2.194", port=8000)
