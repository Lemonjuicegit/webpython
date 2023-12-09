import geopandas as gpd
import pandas as pd
import arcpy,os


class Crop:
    def __init__(self,gdb,benchmark_lay,save_gdb,saveName) -> None:
        self.gdb_path = gdb
        self.save = save_gdb
        self.save_name = saveName
        arcpy.management.CreateFileGDB(save_gdb,saveName,"CURRENT")
        self.lay = benchmark_lay
        
        self.featureName = pd.DataFrame(columns=["directory", "setname", "featureName"])
        with arcpy.EnvManager(workspace = self.gdb_path):
            dataset_list = [""]
            datasets = arcpy.ListDatasets()
            dataset_list.extend(datasets)

            for dataset in dataset_list:
                featureclasses = arcpy.ListFeatureClasses("", "POLYGON", "NOT_RECURSIVE")
                for fc in featureclasses:
                    self.featureName[self.featureName.shape[0]] = [os.path.join( self.gdb_path, dataset),dataset,fc]
        
    
    def clip(self,row):
        
        pass
    
    def clip_all(self):
        f = self.featureName[self.featureName.featureName != self.lay].copy()
        f.applay(self.clip)
        
    def createGdb(self,path,name,datasetname):
        
        arcpy.management.CreateFileGDB(out_folder_path=path,out_name=name,out_version="CURRENT")
        
    