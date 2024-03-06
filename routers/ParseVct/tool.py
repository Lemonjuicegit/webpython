import re


def reElementSplit(vct_str,node):
    # 匹配节点元素
    search_ = re.search(f'(?<={node}Begin)[\s\S]*(?={node}End)',vct_str)
    if search_:
        return search_.group().split('\n')[1:-1]
    else:
        return None

def reElement(vct_str,node):
    # 匹配节点元素
    search_ = re.search(f'(?<={node}Begin)[\s\S]*(?={node}End)',vct_str)
    if search_:
        return search_.group()
    else:
        return None
    
class ObservableDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._on_change_callbacks = []

    def register_on_change(self, callback):
        """注册一个当字典值改变时调用的回调函数"""
        self._on_change_callbacks.append(callback)

    def deregister_on_change(self, callback):
        """移除已注册的回调函数"""
        self._on_change_callbacks.remove(callback)

    def __setitem__(self, key, value):
        """重写__setitem__方法以触发回调"""
        if key in self and self[key] != value:
            # 值发生改变时触发回调
            for callback in self._on_change_callbacks:
                callback(key, self[key], value)
        super().__setitem__(key, value)

if __name__ == '__main__':
    aa = ObservableDict({'a':'a'})
    aa.register_on_change(lambda k, v, v_new: print(f'{k} changed from {v} to {v_new}'))
    aa['a'] = 'b'
