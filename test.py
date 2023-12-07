# 继承 Exception
class MyError(Exception):
     def __init__(self, msg):
         self.msg = msg
    
     def __str__(self):
         return self.msg

# 求和的方法
def add(a,b):
    # 如果a和b中有负数，就向调用处抛出异常
    if a < 0 or b < 0:
        raise MyError('自定义的异常')
             
    r = a + b
    return r

# 调用 求和的方法
try:
    print(add(-123,456))
except MyError as e:
    print(str(e))
