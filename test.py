import rasterio
import matplotlib.pyplot as plt
import geopandas as gpd

# 读取tif文件
with rasterio.open(r'E:\工作文档\公示图\佳渝\三调影像.tif') as src:
    # 获取栅格数据和元数据
    raster_data = src.read(1)  # 只读取第一波段（如有多个波段）
    transform = src.transform
    bounds = src.bounds
    crs = src.crs

# 对于大型影像，考虑裁剪或者重采样到适合可视化的大小
# 这里假设已经处理好了这个步骤，raster_data是处理过的数据

# 加载矢量数据并确保与栅格数据有相同的坐标参考系统
gdf = gpd.read_file(r'E:\工作文档\公示图\茶山竹海出图.gdb',layer='QDSJ_ZDT')
gdf = gdf.to_crs(crs)

# 创建一个新的matplotlib图像
fig, ax = plt.subplots(figsize=(10, 10))

# 使用imshow显示TIFF影像，注意这里可能需要对raster_data进行进一步缩放以适应屏幕显示
im_extent = (*bounds[0:2], *bounds[2:4])
ax.imshow(raster_data, extent=im_extent, cmap='gray', origin='upper', transform=transform)

# 设置地图轴的坐标系与geopandas数据一致
ax.set_extent(im_extent)
ax.set_aspect('equal', adjustable='datalim')

# 绘制geopandas的矢量数据
gdf.plot(ax=ax, color='red')

plt.show()