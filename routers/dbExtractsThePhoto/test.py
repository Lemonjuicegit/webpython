
import sqlite3

# 连接到数据库
conn = sqlite3.connect(r'E:\工作文档\(500104)大渡口区_20231212114630062.db')

# 创建一个游标对象
cursor = conn.cursor()

# 执行查询语句
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

# 获取查询结果
results = cursor.fetchall()

# 遍历结果并打印表名
for row in results:
    print(row[0])

# 关闭游标和连接
cursor.close()
conn.close()