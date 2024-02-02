import os
from pathlib import Path
import pandas as pd
from docxtpl import DocxTemplate

template_path = Path(r'E:\exploitation\webpython\routers\yc_syq\template')
def real_estate_sq(date,save_path):
    doc_sq = DocxTemplate(template_path / '不动产登记申请表.docx')
    doc_sq.render({
      'qlr':date['QSDWMC'],
      'zl':date['镇村社'],
      'bdcdyh':date['不动产单元号']
    })
    doc_sq.save(os.path.join(save_path,'不动产登记申请表.docx'))

def real_estate_frwt(date,save_path):

	doc_temp = DocxTemplate(template_path / '法人授权委托书.docx')
	doc_temp.render({
		'dwmc':date['QSDWMC'],
		'dwdz':date['QSDWMC'],
		'sldw':date['QSDWMC'],
	})
	doc_temp.save(os.path.join(save_path,'法人授权委托书.docx'))
def real_estate_zjrzm(date,save_path):
  # 指界人证明
  # 1-6,1-9,1-13,4-4,4-9,4-13,
    doc_temp = DocxTemplate(template_path / '指界人证明.docx')
    doc_temp.render({
      'xzm':date['乡镇名'],
      'cm':date['村名'],
      'sm':date['社名'],
    })
    doc_temp.save(os.path.join(save_path,'指界人证明.docx'))
def real_estate_zjtzs(date,save_path):

	doc_temp = DocxTemplate(template_path / '指界通知书.docx')
	doc_temp.render({
		'zl':date['QSDWMC'],
		'jhdd':date['jhdd'],
		'qlr':date['QSDWMC']
	})
	
	doc_temp.save(os.path.join(save_path,'指界通知书.docx'))
def real_estate_zjwts(date,save_path):

  doc_temp = DocxTemplate(template_path / '指界委托书.docx')
  doc_temp.render({
    'qlr':date['QSDWMC'],
    'txdz':date['txdz']
  })

  doc_temp.save(os.path.join(save_path,'指界委托书.docx'))
  return '指界委托书.docx'
def real_estate_frzms(date,save_path):
	doc_temp = DocxTemplate(template_path / '法人证明书.docx')
	doc_temp.render({
		'qsdwmc':date['QSDWMC'],
	})
	doc_temp.save(os.path.join(save_path,'法人证明书.docx'))
def real_estate_yssq(date,save_path):

	doc_temp = DocxTemplate(template_path / '遗失申明.docx')
	doc_temp.render({
		'qlr':date['QSDWMC'],
		'zl':date['QSDWMC']
		})
	doc_temp.save(os.path.join(save_path,'遗失申明.docx'))
def qzb_(qzb_file,save_path,choose):
  date =  pd.read_excel(qzb_file)
  date_dic = {}
  for _,row in date.iterrows():
    if row['QSDWMC'] in date_dic:
      temp = date_dic[row['QSDWMC']]['不动产单元号']
      date_dic[row['QSDWMC']]['不动产单元号'] = f"{temp}、{row['不动产单元号']}"
      date_dic[row['QSDWMC']]['面积'] = date_dic[row['QSDWMC']]['面积'] + row['宗地面积']
    else:
      date_dic[row['QSDWMC']] = {'社名':row['社名'],'乡镇名':row['乡镇名'],'村名':row['村名'],'QSDWMC':row['QSDWMC'],'镇村社':row['镇村社'],'不动产单元号':row['不动产单元号'],'面积':row['宗地面积'],'txdz':row['txdz'],'jhdd':row['jhdd']}
  yield len(date_dic)
  for row in date_dic:
    save_path_ = os.path.join(save_path,'签字资料',date_dic[row]['村名'],'签字资料',date_dic[row]['QSDWMC'])
    if not os.path.exists(save_path_):
        os.makedirs(save_path_)
    if choose['sq']:
      real_estate_sq(date_dic[row],save_path_)
    if choose['frwt']:
      real_estate_frwt(date_dic[row],save_path_)
    if choose['zjrzm']:
      real_estate_zjrzm(date_dic[row],save_path_)
    if choose['zjtzs']:
      real_estate_zjtzs(date_dic[row],save_path_)
    if choose['zjwts']:
      real_estate_zjwts(date_dic[row],save_path_)
    if choose['frzms']:
      real_estate_frzms(date_dic[row],save_path_)
    if choose['yssq']:
      real_estate_yssq(date_dic[row],save_path_)
    yield f"{row}签字资料"




    