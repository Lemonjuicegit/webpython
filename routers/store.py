from pathlib import Path
import pandas as pd
from .Djmod import Djlog


class Store:
    def __init__(self):
        self.useFile:pd.DataFrame = pd.DataFrame(columns=["ip","directory", "filename", "path", "type", "name"])  # coulmns: directory,filename,path,type,name
        self.use:dict = {}
        self.zipFile = []
        self.uploadPath = Path(r"E:\exploitation\webpython\upload")
        self.sendPath = Path(r"E:\exploitation\webpython\send")
        self.log = Djlog()
    
    def addUseFile(self,ip ,directory,filename: str):
        self.useFile.loc[self.useFile.shape[0]] = [
            ip,
            str(directory/ip),
            filename,
            str(directory/ip / filename),
            filename.split(".")[1],
            filename.split(".")[0],
        ]
    
store = Store()