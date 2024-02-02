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