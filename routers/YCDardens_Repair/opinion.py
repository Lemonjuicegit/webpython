from docxtpl import DocxTemplate
import docxtpl
import os
import geopandas as gpd
from docx import Document
from .. import compose_docx
from docxcompose.composer import Composer
from docx.shared import Mm
template_path = r'E:\exploitation\webpython\routers\YCDardens_Repair\template\低效园林地开发整治项目征求意见表.docx'

template_doc = DocxTemplate(template_path)

def generate_opinion(data,img_path):
    doc = template_doc
    insert_image = docxtpl.InlineImage(doc, img_path, width=Mm(130))
    context = {
        'TBBH':data['TBBH'],
        'QS':data['ZLDWMC'],
        'DL':data['DLMC'],
        'YJMJ':data['TBMJ'],
        'img':insert_image,
    }
    doc.render(context)
    return doc

def generate_opinion_all(gdb,img_path,sava):
    gdf = gpd.read_file(gdb,layer="南大街")
    composer = Composer(Document())
    docxlist = []
    def add_doc(row):
        doc = generate_opinion(row,os.path.join(img_path,f"{row.TBBH}.jpg"))
        docxlist.append(doc)
    gdf.apply(add_doc,axis=1)
    for docx in docxlist:
        composer.append(docx)
    composer.save(sava)
    
if __name__ == "__main__":
    gdb = r"E:\工作文档\模板\调查表测试.gdb"
    generate_opinion_all(gdb,r"E:\工作文档\测试导出数据\img",r"E:\工作文档\测试导出数据\测试.docx")