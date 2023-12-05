import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import glob
import os

# 文件路径设置
dirpath = '../China_LC030/2000/*/' #该文件夹下存放了待拼接的栅格，/*/表示文件存在于2000的子文件里面
out_fp = os.path.join('../China_LC030/Mosic', "2020_LC030.tif") # 输出文件名
# 获取所有需要拼接文件的文件名
tif_file = glob.glob(os.path.join(dirpath, "*.tif"))
print(tif_file)

# 文件列表
src_files_to_mosaic = []
for tif_f in tif_file:
    src = rasterio.open(tif_f)
    src_files_to_mosaic.append(src)

src_files_to_mosaic


out_meta = src.meta.copy()
# 更新数据参数，“crs”参数需要结合自己的实际需求，设定相应的坐标参数
out_meta.update({"driver": "GTiff",
                 "height": mosaic.shape[1],
                 "width": mosaic.shape[2],
                 "transform": out_trans,
                 "crs": "+proj=utm +zone=49 +datum=WGS84 +units=m +no_defs"
                 }
                )
# 保存文件
with rasterio.open(out_fp, "w", **out_meta) as dest:
    dest.write(mosaic)