import base64
import requests
import json
import cv2
import numpy as np
import os
from paddleocr import PaddleOCR
from .ocr_type import ImageBaseInfo
class OCR_Model:
    def __init__(self) -> None:
        self.ocr_engine:PaddleOCR = PaddleOCR(use_angle_cls=True,lang='ch', use_gpu=False, show_log=False)
    
    def get_ocr(self,image_base_info:ImageBaseInfo):
        img_file = image_base_info.img64
        height = image_base_info.height
        width = image_base_info.width
        channels = image_base_info.channels
        binary_data = base64.b64decode(img_file)
        img_array = np.frombuffer(binary_data, dtype=np.uint8).reshape((height, width, channels))
        # 无文件传入，返回错误
        if not img_file:
            raise ValueError("No image file uploaded")
        
        # 调用 PaddleOCR 进行识别
        result = self.ocr_engine.ocr(img_array)
        # 返回识别结果
        result = [line for line in result if line]
        ocr_result = [i[1][0] for line in result for i in line]
        return "\n".join(ocr_result)
     
    def ocr_image_by_file(self,image_path:str):
        img = cv2.imread(image_path)
        height, width, channels = img.shape
        img64 = base64.b64encode(img).decode('utf-8')
        # 构造请求数据
        data = ImageBaseInfo(img64=str(img64), height=height, width=width, channels=channels)        
        return self.get_ocr(data) 
        
    def ocr_image_by_image_bytes(self,image_bytes:str) -> str:
        # 将二进制数据转换为NumPy数组
        image_array = np.frombuffer(image_bytes, np.uint8)
        
        # 使用OpenCV将NumPy数组解码为图像
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        height, width, channels = image.shape
        img64 = base64.b64encode(image).decode('utf-8')
        # 构造请求数据
        data = ImageBaseInfo(img64=str(img64), height=height, width=width, channels=channels)        

        return self.get_ocr(data) 
if __name__ == '__main__':
    ocr_model = OCR_Model()
    image_path = "C:\\Users\\markyangkp\\Pictures\\123123123.bmp"
    ocr_result = ocr_model.ocr_image_by_file(image_path)
    print(type(ocr_result))
    print(ocr_result)