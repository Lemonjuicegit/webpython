
import re
import pandas as pd

def ZDFlyOut(xlsxpath):
    df = pd.read_excel(xlsxpath)
    df['eq'] = (df['QLRMC'] != df['QLRMC2'])
    df = df[df['eq']].copy()
    zddm_count = df.groupby(['ZDDM']).size().reset_index(name='COUNT1')
    df = pd.merge(df, zddm_count, on=['ZDDM'], how='left')
    df = df[df.COUNT1 == 1]
    grouped1 = df.groupby(['QLRMC', 'QLRMC2']).size().reset_index(name='COUNT2')
    merged = pd.merge(df, grouped1, on=['QLRMC','QLRMC2'], how='left')
    def dispose(row):
        if '村民小组' in row.QLRMC:
            merged.loc[row.name,'FC'] = f"本村民小组飞出{row.QLRMC2}{row.COUNT2}宗地"
        elif '居民组' in row.QLRMC:
            merged.loc[row.name,'FC'] = f"本居民组飞出{row.QLRMC2}{row.COUNT2}宗地"
        else:
            merged.loc[row.name,'FC'] = ''
    merged.apply(dispose,axis=1)
    fcdict = {}
    fclist = []
    def fr_dict(row):
        if row.FC and (('居民组' in row.QLRMC) or ('村民小组' in row.QLRMC)):
            if row.QLRMC not in fcdict:
                fcdict[row.QLRMC] = {row.FC}
            else:
                fcdict[row.QLRMC].add(row.FC)
    merged.apply(fr_dict, axis=1)
    for k,v in fcdict.items():
        fclist.append({'QLRMC':k,'FCQK':'、'.join(v)})
    merged = pd.merge(merged, pd.DataFrame(fclist), on=['QLRMC'], how='left')
    return merged

def ZDFlyIn(xlsxpath):
    df = pd.read_excel(xlsxpath)
    df['eq'] = (df['QLRMC'] != df['QLRMC2'])
    df = df[df['eq']].copy()
    zddm_count = df.groupby(['ZDDM']).size().reset_index(name='COUNT1')
    df = pd.merge(df, zddm_count, on=['ZDDM'], how='left')
    df = df[df.COUNT1 == 1]
    df = df[df.QLRMC.str.contains("(村民小组)|(居民组)",regex=True)]
    grouped1 = df.groupby(['QLRMC', 'QLRMC2']).size().reset_index(name='COUNT2')
    grouped2 = df.groupby(['QLRMC2', 'QLRMC']).size().reset_index(name='COUNT3')
    merged = pd.merge(df, grouped1, on=['QLRMC','QLRMC2'], how='left')
    merged = pd.merge(merged, grouped2, on=['QLRMC','QLRMC2'], how='left')
    def dispose(row):
        if '村民小组' in row.QLRMC2:
            merged.loc[row.name,'FR'] = f"{row.QLRMC}飞入本村民小组{row.COUNT3}宗地"
        elif '居民组' in row.QLRMC2:
            merged.loc[row.name,'FR'] = f"{row.QLRMC}飞入本居民组{row.COUNT3}宗地"
        else:
            merged.loc[row.name,'FR'] = ''
    merged.apply(dispose,axis=1)
    frdict = {}
    frlist = []
    def fr_dict(row):
        if row.FR and (('居民组' in row.QLRMC2) or ('村民小组' in row.QLRMC2)):
            if row.QLRMC2 not in frdict:
                frdict[row.QLRMC2] = {row.FR}
            else:
                frdict[row.QLRMC2].add(row.FR)
    merged.apply(fr_dict, axis=1)
    for k,v in frdict.items():
        frlist.append({'QLRMC2':k,'FRQK':'、'.join(v)})
    merged = pd.merge(merged, pd.DataFrame(frlist), on=['QLRMC2'], how='left')

    return merged