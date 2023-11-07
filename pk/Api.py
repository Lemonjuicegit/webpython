from . import Sign,areaClassification

class Api:
  def __init__(self) -> None:
    self.result = None
    self.temmp = None
    self.exportAreaLen = 0

  def getSign_date(self,xlsx_teb):
    self.result = Sign.get_date(xlsx_teb)
    
  def sign_api(self,save_path):
    return Sign.main(self.result,save_path)
  def exportArea(datapath,df_fda):
    return areaClassification.exportArea(datapath,df_fda)


