from pathlib import Path
import pandas as pd
import arcpy,os

class Crop:
    def __init__(self,gdb,benchmark_lay,save_gdb,saveName_field) -> None:
        # gdb:要分块的数据库
        # benchmark_lay:分块基准图层
        # save_gdb:分块出来的数据保存位置
        # 
        arcpy.env.workspace = gdb
        self.gdb_path = gdb
        self.save = save_gdb
        self.saveName_field = saveName_field
        self.lay_name = benchmark_lay
        self.featureName = pd.DataFrame(columns=["directory", "setname", "featureName"])
        with arcpy.EnvManager(workspace = self.gdb_path):
            dataset_list = [""]
            datasets = arcpy.ListDatasets()
            dataset_list.extend(datasets)
            for dataset in dataset_list:
                featureclasses = arcpy.ListFeatureClasses("", "POLYGON", "NOT_RECURSIVE")
                for fc in featureclasses:
                    self.featureName[self.featureName.shape[0]] = [os.path.join( self.gdb_path, dataset),dataset,fc]
        
        self.spatialReference = arcpy.Describe(os.path.join(self.featureName[self.featureName.featureName == self.lay_name].directory.values[0],self.lay_name)).spatialReference
        self.lay_apth = self.featureName[self.featureName.featureName == benchmark_lay].directory.values[0]
    def clip(self,row):
        pass
    
    def clip_all(self):
        LayerDf = self.featureName[self.featureName.featureName != self.lay_name].copy()
        setname_list = self.featureName.setname.drop_duplicates().values
        with arcpy.SearchCursor(os.path.join(self.gdb_path,self.lay_name),(self.saveName_field,"SHAPE@")) as cur:
            for row in cur:
                arcpy.management.CreateFileGDB(self.save,f"{row[0]}.gdb","CURRENT")
                for s in setname_list:
                    arcpy.management.CreateFeatureDataset(os.path.join(self.save,f"{row[0]}.gdb"),s,self.spatialReference)
                # 导出基准图形
                path = os.path.join(self.save,row[0],f"{row[0]}.gdb",Path(self.lay_path).name,self.lay_name)
                self.exportFeatures(os.path.join(self.lay_path,self.lay_name),path,f"{self.saveName_field}='{row[0]}'")
                LayerDf.apply(self.clip)
        
    def createGdb(self,path,name,datasetname):
        arcpy.management.CreateFeatureDataset(os.path.join(path,f"{name}.gdb"),datasetname,self.spatialReference)
        
    def exportFeatures(lay,save,where):
        arcpy.conversion.ExportFeatures(lay,save,where)
    
        
    