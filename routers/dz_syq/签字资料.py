import os
from pathlib import Path
import pandas as pd
from docxtpl import DocxTemplate

template_path = Path(r'E:\exploitation\webpython\routers\dz_syq\template')
def real_estate_sq(data,save_path):
    doc_sq = DocxTemplate(template_path / '不动产登记申请表.docx')
    doc_sq.render({
      'qlr':data['QLR'],
      'zl':data['QSDWMC'],
      'bdcdyh':data['不动产单元号'],
      'zdmj':data['面积']
    })
    doc_sq.save(os.path.join(save_path,'不动产登记申请表.docx'))

def real_estate_frwt(data,save_path):

	doc_temp = DocxTemplate(template_path / '法人授权委托书.docx')
	doc_temp.render({
		'dwmc':data['QSDWMC'],
		'dwdz':data['QSDWMC'],
		'sldw':data['QSDWMC'],
	})
	doc_temp.save(os.path.join(save_path,'法人授权委托书.docx'))
def real_estate_zjrzm(data,save_path):
  # 指界人证明
  # 1-6,1-9,1-13,4-4,4-9,4-13,
    doc_temp = DocxTemplate(template_path / '指界人证明.docx')
    doc_temp.render({
      'xzm':data['乡镇名'],
      'cm':data['村名'],
      'sm':data['社名'],
    })
    doc_temp.save(os.path.join(save_path,'指界人证明.docx'))
def real_estate_zjtzs(data,save_path):

	doc_temp = DocxTemplate(template_path / '指界通知书.docx')
	doc_temp.render({
		'zl':data['QSDWMC'],
		'jhdd':data['jhdd'],
		'qlr':data['镇村社']
	})
	
	doc_temp.save(os.path.join(save_path,'指界通知书.docx'))
def real_estate_zjwts(data,save_path):

  doc_temp = DocxTemplate(template_path / '指界委托书.docx')
  doc_temp.render({
    'qlr':data['QSDWMC'],
    'txdz':data['txdz']
  })

  doc_temp.save(os.path.join(save_path,'指界委托书.docx'))
  return '指界委托书.docx'
def real_estate_frzms(data,save_path):
	doc_temp = DocxTemplate(template_path / '法人证明书.docx')
	doc_temp.render({
		'qsdwmc':data['QSDWMC'],
	})
	doc_temp.save(os.path.join(save_path,'法人证明书.docx'))
def real_estate_yssq(data,save_path):

	doc_temp = DocxTemplate(template_path / '遗失声明.docx')
	doc_temp.render({
		'qlr':data['QSDWMC'],
		'zl':data['QSDWMC']
		})
	doc_temp.save(os.path.join(save_path,'遗失声明.docx'))
def qzb_(qzb_file,save_path,choose):
  data =  pd.read_excel(qzb_file)
  data_dic = {}
  for _,row in data.iterrows():
    if row['QSDWMC'] in data_dic:
      temp = data_dic[row['QSDWMC']]['不动产单元号']
      data_dic[row['QSDWMC']]['不动产单元号'] = f"{temp}、{row['不动产单元号']}"
      data_dic[row['QSDWMC']]['面积'] = data_dic[row['QSDWMC']]['面积'] + row['宗地面积']
    else:
      data_dic[row['QSDWMC']] = {'社名':row['社名'],
                                 '乡镇名':row['乡镇名'],
                                 '村名':row['村名'],
                                 'QSDWMC':row['QSDWMC'],
                                 '镇村社':row['镇村社'],
                                 '不动产单元号':row['不动产单元号'],
                                 '面积':row['宗地面积'],
                                 'txdz':row['txdz'],
                                 'jhdd':row['jhdd'],
                                 'QLR':row['QLR']}
  yield len(data_dic)
  for row in data_dic:
    save_path_ = os.path.join(save_path,'签字资料',data_dic[row]['村名'],'签字资料',data_dic[row]['QSDWMC'])
    if not os.path.exists(save_path_):
        os.makedirs(save_path_)
    if choose['sq']:
      real_estate_sq(data_dic[row],save_path_)
    if choose['frwt']:
      real_estate_frwt(data_dic[row],save_path_)
    if choose['zjrzm']:
      real_estate_zjrzm(data_dic[row],save_path_)
    if choose['zjtzs']:
      real_estate_zjtzs(data_dic[row],save_path_)
    if choose['zjwts']:
      real_estate_zjwts(data_dic[row],save_path_)
    if choose['frzms']:
      real_estate_frzms(data_dic[row],save_path_)
    if choose['yssq']:
      real_estate_yssq(data_dic[row],save_path_)
    yield f"{row}签字资料"




    