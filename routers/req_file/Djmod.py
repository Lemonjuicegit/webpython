import zipfile


def unzip(zip_path: str, unzip_path: str,filetype:str=''):
    '''解压文件'''
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(unzip_path)
        if filetype == 'gdb':
            return zip_path
        return [n.filename for n in zip_file.filelist]