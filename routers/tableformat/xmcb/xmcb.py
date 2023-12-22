from openpyxl import Workbook,load_workbook
import re

def xmcb(data,savepath):
    wk = load_workbook(data)
    column_names = ['L','M','N','O','P','S','T','U','V','W','X','Y','Z','AA']
    sheet = wk.active
    dim = sheet.dimensions # 表格范围
    row_count = int(re.search(r'\d+$',dim).group())
    for name in column_names:
        sum_list = []
        for i in range(4,row_count):
            v = sheet[f"{name}{i}"].value
            if v == 0:
                continue
            sum_list.append(float(v))
            k = sheet[f"K{i}"].value
            sheet[f"{name}{i}"].value = f"{v}({(int(round(float(v)/float(k),2)*100))}%)"
        sum_k = sheet[f"K{row_count}"].value
        sheet[f"{name}{row_count}"].value = f"{int(sum(sum_list))}({(int(round(sum(sum_list)/float(sum_k),2)*100))}%)"
    wk.save(savepath)
    

