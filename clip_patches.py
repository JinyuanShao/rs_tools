import os
import gdal
import numpy as np


def read_tif(fileName):
    '''
    read tif data using gdal
    '''
    dataset = gdal.Open(fileName)
    if dataset == None:
        print(fileName + "can't open tif file")
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
        dataset.SetGeoTransform(im_geotrans) 
        dataset.SetProjection(im_proj) 
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
    del dataset
    

def clip(TifPath, SavePath, CropSize, overlap_ratio):
    '''
    TifPath: the directory that store tiff images
    SavePath: th derectory that save small patches
    CropSize: the size of small patch
    overlap_ratio: the ratio between adjacent patches
    '''
    dataset_img = read_tif(TifPath)
    width = dataset_img.RasterXSize # get width of big imagery
    height = dataset_img.RasterYSize # get height of big imagery
    proj = dataset_img.GetProjection() # get geoprojection
    geotrans = dataset_img.GetGeoTransform() # get geo transform
    img = dataset_img.ReadAsArray(0, 0, width, height) # read big imagery as numpy array
    
    #  get the number of big tiff files
    new_name = len(os.listdir(SavePath)) + 1
    #  create a double loop to clip patches
    
    for i in range(int((height - CropSize * overlap_ratio) / (CropSize * (1 - overlap_ratio)))):
        for j in range(int((width - CropSize * overlap_ratio) / (CropSize * (1 - overlap_ratio)))):
            # for single band imagery 
            if(len(img.shape) == 2):
                cropped = img[int(i * CropSize * (1 - overlap_ratio)) : int(i * CropSize * (1 - overlap_ratio)) + CropSize, 
                              int(j * CropSize * (1 - overlap_ratioR)) : int(j * CropSize * (1 - overlap_ratio)) + CropSize]
            # for multi bands imagery
            else:
                cropped = img[:,
                              int(i * CropSize * (1 - overlap_ratio)) : int(i * CropSize * (1 - overlap_ratio)) + CropSize, 
                              int(j * CropSize * (1 - overlap_ratio)) : int(j * CropSize * (1 - overlap_ratio)) + CropSize]
            #  write tiff file
            write_tiff(cropped, geotrans, proj, SavePath + "/%d.tif"%new_name)
            #  name tiff file
            new_name = new_name + 1

    #  clip the last column
    for i in range(int((height-CropSize*overlap_ratio)/(CropSize*(1-overlap_ratio)))):
        if(len(img.shape) == 2):
            cropped = img[int(i * CropSize * (1 - overlap_ratio)) : int(i * CropSize * (1 - overlap_ratio)) + CropSize, (width - CropSize) : width]
        else:
            cropped = img[:,int(i * CropSize * (1 - overlap_ratio)) : int(i * CropSize * (1 - overlap_ratio)) + CropSize, (width - CropSize) : width]
  
        write_tiff(cropped, geotrans, proj, SavePath + "/%d.tif"%new_name)
        new_name = new_name + 1

    #  clip the las raw
    for j in range(int((width - CropSize * overlap_ratio) / (CropSize * (1 - overlap_ratio)))):
        if(len(img.shape) == 2):
            cropped = img[(height - CropSize) : height,
                          int(j * CropSize * (1 - overlap_ratio) : int(j * CropSize * (1 - overlap_ratio)) + CropSize]
        else:
            cropped = img[:,
                          (height - CropSize) : height,
                          int(j * CropSize * (1 - overlap_ratio)) : int(j * CropSize * (1 - overlap_ratio)) + CropSize]
        write_tiff(cropped, geotrans, proj, SavePath + "/%d.tif"%new_name)
 
        new_name = new_name + 1
    
    #  The down right corner
    if(len(img.shape) == 2):
        cropped = img[(height - CropSize) : height,
                      (width - CropSize) : width]
    else:
        cropped = img[:,
                      (height - CropSize) : height,
                      (width - CropSize) : width]
    write_tiff(cropped, geotrans, proj, SavePath + "/%d.tif"%new_name)
    new_name = new_name + 1


#  example: clip big satellite imagery to 256*256 patches with 0.1 ratio
clip(r"Tif\file\path\example.tif",
        r"patch\tiff\save\path", 256, 0.1)