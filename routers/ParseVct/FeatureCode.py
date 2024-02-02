class FeatureCode:
    def __init__(self,rowlist:str=[]) -> None:
        self.text = '\n'.join(rowlist)
        self._rowlist = rowlist
        self._FeatureCodetList = [{'要素代码':v.split(',')[0],'要素名称':v.split(',')[1],'图形类型':v.split(',')[2],'属性表名':v.split(',')[3]} for v in rowlist]
        self._FeatureNames = [v['要素名称'] for v in self._FeatureCodetList]
    def __getitem__(self, key):
        return self._FeatureCodetList[key]
    def __setitem__(self, index, value):
        if value['要素名称'] in [v for v in self._FeatureNames if v['要素名称'] != self._FeatureNames[index]['要素名称']]:
            raise ValueError(f"{value['要素名称']} 要素已存在")
        self._rowlist[index] = ','.join([v for _,v in value.items()])
        self.text = '\n'.join(self._rowlist)
        self._FeatureCodetList[index] = value  
  
    def __delitem__(self, index):  
        del self._FeatureCodetList[index]
        del self._rowlist[index]
        self.text = '\n'.join(self._rowlist)
  
    def append(self, value):
        if value['要素名称'] in self._FeatureNames:
            raise ValueError(f"{value['要素名称']} 要素已存在")
        self._FeatureCodetList.append(value)
        self._rowlist.append(','.join([v for _,v in value.items()]))
        self.text = '\n'.join(self._rowlist)
        
  
    def remove(self, value):  
        self._FeatureCodetList.remove(value)
        self._rowlist.remove(value)
        self.text = '\n'.join(self._rowlist)
    
    def __str__(self):
        return str(self._FeatureCodetList)