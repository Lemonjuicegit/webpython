from ttkbootstrap import Style
from tkinter import Frame,Label,Entry,Button,StringVar
from tkinter.filedialog import askdirectory,askopenfilename

class LabelEntryButton(Frame):
  def __init__(self,parent,button_text="按钮",labeltext='标签：',textvariable="",click=None):
    super().__init__(parent)
    self.configure(padx=5,pady=5)
    self.label = Label(self , text=labeltext)
    self.entry = Entry(self ,textvariable=textvariable,width=50)
    self.button = Button(self , text=button_text,width=5,command=click)
    self.label.grid(row=0, column=0)
    self.entry.grid(row=0, column=1)
    self.button.grid(row=0, column=2,padx=3)  
  def get_text(self):
    return self.entry.get()

class DirectoryLabelEntry(LabelEntryButton):
  def __init__(self,parent,button_text="按钮",labeltext='标签：'):
    self.dirpath = StringVar()
    super().__init__(parent,button_text=button_text,labeltext=labeltext,textvariable=self.dirpath,click=self.openDir)
    self.bind("<Button>", self.openDir)
  def openDir(self):
      fileDir = askdirectory()  # 选择打开什么文件，返回文件名
      if fileDir.strip() != '':
          self.dirpath.set(fileDir)  # 设置变量filename的值
      else:
          print("do not choose file")
          
class FilenameLabelEntryButton(LabelEntryButton):
  def __init__(self,parent,button_text="按钮",labeltext='标签：'):
    self.filename = StringVar()
    super().__init__(parent,button_text=button_text,labeltext=labeltext,textvariable=self.filename,click=self.openFile)

  def openFile(self):
      filepath = askopenfilename()  # 选择打开什么文件，返回文件名
      if filepath.strip() != '':
          self.filename.set(filepath)  # 设置变量filename的值
      else:
          print("do not choose file")
  
def ui():
  style = Style(theme="lumen")
  win = style.master
  win.title("身份证匹配")
  win.geometry("800x300")
  win.resizable(False,False)
  head_label = Label(win,text='签字资料生成')
  filelab = FilenameLabelEntryButton(win,labeltext='数据表：',button_text='选择')
  save_widget = DirectoryLabelEntry(win,labeltext='   保存：',button_text='选择')
  button1 = Button(win,text='开始生成')
  res_label = Label(win,text='')
  head_label.grid(column=1,row=0)
  filelab.grid(column=0,row=1,columnspan=3)
  save_widget.grid(column=0,row=2,columnspan=3)
  button1.grid(column=1,row=3)
  res_label.grid(column=1,row=4)
  def ok_cilck(event):
    pass
    
  button1.bind("<Button>", ok_cilck)
  win.mainloop()
if __name__ == '__main__':
  ui()