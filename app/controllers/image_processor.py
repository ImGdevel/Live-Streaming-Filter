from PyQt5.QtGui import QImage
from PyQt5.QtCore import QThread, pyqtSignal
import cv2
from models import Filtering, PathManager
from models.ModelManager import ModelManager
import os
from datetime import datetime
import numpy as np

# 비디오 처리 스레드
class ImageProcessor(QThread):

    def __init__(self):
        super().__init__()
        self.filtering = Filtering()
        self.path_manager = PathManager()

    #원본 사진을 받아서 임시로 이미지 처리
    def filtering_images(self, image_paths):
        processed_images = []
        for image_path in image_paths:
            # 이미지 읽어오기
            image = cv2.imread(image_path)
            
            # 이미지 처리 
            blur_ratio = 50

            boxesList = self.filtering.filtering(image)
            processed_image = self.filtering.blur(blur_ratio, image, boxesList)
            

            
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)  # BGR을 RGB로 변환
            height, width, channel = processed_image.shape
            bytes_per_line = 3 * width
            q_img = QImage(processed_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

            processed_images.append(q_img)

        return processed_images



    def QImage_to_cv2(qimage):
        """
        QImage를 numpy 배열로 변환합니다.
        
        Args:
        - qimage: 변환할 QImage 객체
        
        Returns:
        - 변환된 numpy 배열
        """
        width = qimage.width()
        height = qimage.height()
        byte_per_line = qimage.bytesPerLine()
        image_format = qimage.format()

        # QImage를 numpy 배열로 변환
        ptr = qimage.constBits()
        ptr.setsize(qimage.byteCount())
        img_arr = np.array(ptr).reshape(height, width, int(byte_per_line / height))

        return img_arr


    def create_filtered_image(self, QImage_list):
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        save_directory = self.path_manager.save_image_path()
        sequence_number = 1
        for qimage in QImage_list:
            img = self.QImage_to_cv2(qimage)
            # # 처리된 이미지를 파일로 저장 (새로운 파일명을 만듦)
            image_name = f"{current_time}_{sequence_number}.jpg"
            output_path = os.path.join(save_directory, image_name)
            cv2.imwrite(output_path, img)
            # print(f"이미지 처리 및 저장 완료: {output_path}")
            sequence_number += 1


            