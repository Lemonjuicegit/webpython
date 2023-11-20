import pandas as pd
from typing import Literal
from pk.Ownership import Ownership
from pk.Djmod import groupby
from pk.不动产权籍调查表 import generate_jzjb

def jpg_pathlist(jpg_zdct):
    ct_path = {}
    for file in jpg_zdct.glob('*宗地草图.jpg'):
        ct_path[file.name[:-8]] = str(file)
    return ct_path

jpg_pathlist()


