
import logging, time, zipfile, os, traceback, sys
import pandas as pd
from functools import wraps
from docx.shared import Pt
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx import Document
from docxcompose.composer import Composer
from pathlib import Path


def groupby(df: pd.DataFrame, by: list[str], agg: str):
    """agg:[
        'any','all','count','cov','first','idxmax',
        'idxmin','last','max','mean','median','min',
        'nunique','prod','quantile','sem','size',
        'skew','std','sum','var'
    ]
    """
    Aggfield = agg.upper()
    df2 = df.copy()
    df2[Aggfield] = ""
    by_df = pd.DataFrame(df2.groupby(by=by)[Aggfield].agg(agg))
    by_df.reset_index(inplace=True)
    return by_df


def compose_docx_file(files, output_file_path):
    """
    合并多个word文件到一个文件中
    :param files:待合并文件的列表
    :param output_file_path 新的文件路径
    :return:
    """
    composer = Composer(Document())
    n = 0
    for file in files:
        if not Path(file).exists():
            break
        doc = Document(file)
        if n < len(files) - 1:
            # 防止最后一个文档分页
            doc.add_page_break()
        composer.append(doc)
        n += 1

    composer.save(output_file_path)
    
def zip_list(filelist: list[str|Path], zipname):
    # 多个文件压缩
    with zipfile.ZipFile(zipname, "w") as zip_file:
        for fpath in filelist:
            zip_file.write(fpath, arcname=str(fpath).split(os.sep)[-1])


class Myerr(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

