from pathlib import Path
import pandas as pd



class Store:
    useFile:pd.DataFrame = pd.DataFrame(columns=["ip","directory", "filename", "path", "type", "name"])  # coulmns: directory,filename,path,type,name
    use:dict = {}
    zipFile = []
    uploadPath = Path(r"E:\exploitation\webpython\upload")
    sendPath = Path(r"E:\exploitation\webpython\send")
    
    def addUseFile(self,ip ,filename: str):
        self.useFile[self.useFile.shape[0]] = [
            ip,
            str(self.uploadPath/ip),
            filename,
            str(self.uploadPath/ip / filename),
            filename.split(".")[1],
            filename.split(".")[0],
        ]
    
store = Store()