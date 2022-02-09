import random
import gdal
import numpy as np
import os

def read_tif(fileName):
    '''
    read tif data using gdal
    '''
    dataset = gdal.Open(fileName)
    if dataset == None:
        print(fileName + "文件无法打开")
    return dataset
    

def write_tiff(im_data, im_geotrans, im_proj, path):
    '''
    save to tif file
    '''
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    elif len(im_data.shape) == 2:
        im_data = np.array([im_data])
        im_bands, im_height, im_width = im_data.shape
    # create gdal driver
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype)
    if(dataset!= None):
        dataset.SetGeoTransform(im_geotrans) #写入仿射变换参数
        dataset.SetProjection(im_proj) #写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
    del dataset
    

def RandomCrop(TifPath, LabelPath, IamgeSavePath, LabelSavePath, CropSize, CutNum):
    '''
    TifPath: the directory that stores tiff images
    LabelPath: the directory that sotres label images
    SavePath: the derectory that saves small patches
    LabelSavePath: the derectory that saves small label patches
    CropSize: the size of small patch
    CutNum: the number of needed patches
    '''
    dataset_img = read_tif(TifPath)
    width = dataset_img.RasterXSize
    height = dataset_img.RasterYSize
    proj = dataset_img.GetProjection()
    geotrans = dataset_img.GetGeoTransform()
    img = dataset_img.ReadAsArray(0,0,width,height)
    dataset_label = read_tif(LabelPath)
    label = dataset_label.ReadAsArray(0,0,width,height)
    
    #  get exsting number of files in savepath
    fileNum = len(os.listdir(IamgeSavePath))
    new_name = fileNum + 1
    while(new_name < CutNum + fileNum + 1):
        #  generate corrdiantes randomly without the bottom right corner
        UpperLeftX = random.randint(0, height - CropSize)    
        UpperLeftY = random.randint(0, width - CropSize)    
        if(len(img.shape) == 2):
            imgCrop = img[UpperLeftX : UpperLeftX + CropSize,
                          UpperLeftY : UpperLeftY + CropSize]
        else:
            imgCrop = img[:,
                          UpperLeftX : UpperLeftX + CropSize,
                          UpperLeftY : UpperLeftY + CropSize]
        if(len(label.shape) == 2):
            labelCrop = label[UpperLeftX : UpperLeftX + CropSize,
                              UpperLeftY : UpperLeftY + CropSize]
        else:
            labelCrop = label[:,
                              UpperLeftX : UpperLeftX + CropSize,
                              UpperLeftY : UpperLeftY + CropSize]
        write_tiff(imgCrop, geotrans, proj, IamgeSavePath + "/%d.tif"%new_name)
        write_tiff(labelCrop, geotrans, proj, LabelSavePath + "/%d.tif"%new_name)
        new_name = new_name + 1
        
# example : clip big images to samll patch randomly with spectific number of patch      
RandomCrop(r"path\that\saves\tiff.tif",
           r"path\that\saves\label.tif",
           r"path\that\saves\patches",
           r"path\that\saves\patch\labels",
           256,300)