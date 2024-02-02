class Field:
    def __init__(self,name,type,len=None,jd=None) -> None:
        self.text = f"{name},{type}{f',{jd}' if jd else ''}{f',{len}' if len else ''}"
        self.name = name
        self.type = type
        self.jd = jd
        self.len = len
    
    def __str__(self) -> str:
        return self.text
    
class FieldList:
    def __init__(self,fields:list[Field]=[]):
        if fields:
            self._FieldNames = [v.name for v in fields]
            self.text = "\n".join([v.text for v in fields])
        else:
            self._FieldNames = []
            self.text = ''
        self._FieldList = fields
    def __getitem__(self, key):
        return self._FieldList[key]
    def __setitem__(self, index, value:Field):
        if value.name in [v for v in self._FieldNames if self._FieldNames[index] != v ]:
            raise ValueError(f"{value.name} 字段已存在")
        self._FieldList[index] = value
        self._FieldNames[index] = value
        self.text = '\n'.join([v.text for v in self._FieldList])
  
    def __delitem__(self, index):  
        del self._FieldList[index]
        del self._FieldNames[index]
        self.text = '\n'.join([v.text for v in self._FieldList])
  
    def append(self, value):
        if value.name in self._FieldNames:
            raise ValueError(f"{value.name} 字段已存在")
        self._FieldList.append(value)
        self._FieldNames.append(value.name)
        self.text = '\n'.join([v.text for v in self._FieldList])
        
  
    def remove(self, value):  
        self._FieldList.remove(value)
        self._FieldNames.remove(value)
        self.text = '\n'.join([v.text for v in self._FieldList])
    
    def __str__(self):
        return str(self._FieldList)

class TableStructure:
    def __init__(self,rowlist:str=[]) -> None:
        self.text = '\n'.join(rowlist)
        self._TableStructureList = {}
        if len(rowlist)>0:
            n = 0
            def field(v):
                s = v.split(',')
                if s[1] == 'Float':
                    return Field(s[0],s[1],s[3],s[2])
                elif s[1] == 'VarChar':
                    return Field(s[0],s[1])
                else:
                    return Field(s[0],s[1],s[2])
            while 1:
                row = rowlist[n].split(',')
                if row[0] == '0':
                    n += 1
                    continue
                self._TableStructureList[row[0]] = FieldList([field(v) for v in rowlist[n+1:n+int(row[1])+1]])
                n += (int(row[1])+1)
                if n >= len(rowlist)-1:
                    break
    def getText(self):
        self.text = ''
        for k,v in self._TableStructureList.items():
            self.text = f"{self.text}\n{k},{v.text}\n0"
    def __getitem__(self, key):
        return self._TableStructureList[key]

