
import webview
from pk.Api import Api

api = Api()

def get_file_path(file_types_list=['*']):
  # 打开文件
  file_types = (f"file (*.{';*.'.join(file_types_list)})",)

  file_path = window.create_file_dialog(webview.OPEN_DIALOG,file_types=file_types)
  return file_path

def get_folder_path():
  # 打开目录
  folder_path = window.create_file_dialog(webview.FOLDER_DIALOG)
  return folder_path

def getDate(xlxs_path,save_path):
  api.getSign_date(xlxs_path)
  api.temp = api.sign_api(save_path)
  return len(api.result)

def sign():
  return next(api.temp)
  
def expose(window):
  window.evaluate_js('pywebview.api.get_file_path')
  window.evaluate_js('pywebview.api.get_folder_path')
  window.evaluate_js(f'pywebview.api.getDate')
  window.evaluate_js(f'pywebview.api.sign')


window = webview.create_window('vue-vite', 'http://localhost:5173/',resizable=False,width=900,height=580)
funlist = [
  get_file_path,
  get_folder_path,
  getDate,
  sign
]
window.expose(*funlist)

webview.start(expose,window,debug=True)


