from 签字资料 import qzb_


path = r'E:\工作文档\大足所有权\模板2.xlsx'
choose = {
        'sq':1,
    'frwt': 1,
    'zjrzm': 1,
    'zjtzs': 1,
    'zjwts': 1,
    'frzms': 1,
    'yssq': 1,
}
aa = qzb_(path,r'E:\工作文档\大足所有权',choose)

count = next(aa)
print(count)
for i in range(count):
    res = next(aa)
    print(res)