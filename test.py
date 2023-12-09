import fiona  
  
# 打开gdb数据库  
gdb_path = "path/to/your_gdb.gdb"  
driver = "gdal"  
gdb_database = fiona.open(gdb_path, "r", driver=driver)  
  
# 获取所有数据集名称  
dataset_names = [dataset.split("=")[1] for dataset in gdb_database.meta['DATASET']]  
  
# 打印数据集名称  
for name in dataset_names:  
    print(name)  
  
# 关闭gdb数据库  
gdb_database.close()
