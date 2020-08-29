# Script for extracting single leaves form a sheet with multiple samples
import cv2
import os
import numpy as np

class InstanceExtractor():
    def __init__(self):
        self.instance_id = 0

    def extract_instances(self, sheet_image):
        extracted_instances = []
        # Scale down as scans are super big
        width = int(sheet_image.shape[1] * 0.1)
        height = int(sheet_image.shape[0] * 0.1)
        sheet_image = cv2.resize(sheet_image, (width, height))
        # Convert to grayscale
        gray_img = cv2.cvtColor(sheet_image, cv2.COLOR_BGR2GRAY)
        # Heavy threshold as background is supposed to be white
        ret,thresh_img = cv2.threshold(gray_img,200,255,cv2.THRESH_BINARY_INV)
        # Extract conneted components
        ret, label_img, stats, centroid = cv2.connectedComponentsWithStats(thresh_img)
        
        # Process only "large" components
        for idx, stat in enumerate(stats):
            # idx is 0 for background???
            if idx != 0 and stat[cv2.CC_STAT_AREA]>1000:
                print("Idx %d, pixels %d" % (idx, stat[cv2.CC_STAT_AREA]))
                # Prepare blank instance image
                instance_img = np.zeros((stat[cv2.CC_STAT_HEIGHT],
                                           stat[cv2.CC_STAT_WIDTH],3), np.uint8)
                # Find component indices
                indices = np.where(label_img == idx)
                # Copy pixels
                for indice in zip(indices[0], indices[1]):
                    instance_img[indice[0] - stat[cv2.CC_STAT_TOP],indice[1] - stat[cv2.CC_STAT_LEFT],:] = sheet_image[indice[0],indice[1],:]
                extracted_instances.append(instance_img)
        return extracted_instances

    def pad_instance(self, instance_image):
        return instance_image

    def save_instance(self, image):
        file_name = "instance_" + str(self.instance_id) + ".jpg"
        cv2.imwrite(os.path.join(self.output_path, file_name), image)
        self.instance_id +=1

    def process_folder(self, input_path, output_path):
        self.instance_id = 0
        self.input_path = input_path
        self.output_path = output_path

        # List sheets in input folder
        sheet_paths = [os.path.join(self.input_path, fn) for fn in os.listdir(self.input_path) if fn.endswith(".jpg")]

        # Process each sheet
        for sheet_path in sheet_paths:
            # Load image
            sheet = cv2.imread(sheet_path)
            # Extract instances
            instances = self.extract_instances(sheet)
            for instance in instances:
                # Pad to equal size
                padded_instance = self.pad_instance(instance)
                # Save instance
                self.save_instance(padded_instance)