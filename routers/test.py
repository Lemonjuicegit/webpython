import asyncio
from multiprocessing import Pool


class Test:
    def __init__(self):
        self.a = 0
        
    def add(self,count):
        for i in range(count):
            self.a += i
        return self.a
temp = Test()
def add(count,id):
    temp.add(count)
    print(temp.a,id)
def test():
    print("test")

if __name__ == '__main__': 
    pool = Pool(4)
    pool.apply_async(add,(100,1))
    pool.apply_async(add,(100,2))
    pool.apply_async(add,(100,3))
    pool.close()
    pool.join()