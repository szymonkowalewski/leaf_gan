# Script for extracting single leaves form a sheet with multiple samples
import cv2
import os

class InstanceExtractor():
    def __init__(self):
        self.instance_id = 0

    def extract_instances(self, sheet_image):
        # Scale down as scans are super big
        width = int(sheet_image.shape[1] * 0.4)
        height = int(sheet_image.shape[0] * 0.4)
        sheet_image = cv2.resize(sheet_image, (width, height))
        # Convert to grayscale
        gray_img = cv2.cvtColor(sheet_image, cv2.COLOR_BGR2GRAY)
        # Heavy threshold as background is supposed to be white
        ret,thresh_img = cv2.threshold(gray_img,200,255,cv2.THRESH_BINARY)
        return []

    def pad_instance(self, instance_image):
        pass

    def save_instance(self, image):
        pass

    def process_folder(self, input_path, output_path):
        self.instance_id = 0
        self.input_path = input_path
        self.output_path = output_path

        # List sheets in input folder
        sheet_paths = [os.path.join(self.input_path, fn) for fn in os.listdir(self.input_path) if fn.endswith(".jpg")]

        # Process each sheet
        for sheet_path in sheet_paths:
            # TODO Load image
            # Extract instances
            instances = self.extract_instances(sheet)
            for instance in instances:
                # Pad to equal size
                padded_instance = self.pad_instance(instance)
                # Save instance
                self.save_instance(padded_instance)