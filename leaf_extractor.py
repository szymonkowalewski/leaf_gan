# Script for extracting single leaves form a sheet with multiple samples
import cv2

class InstanceExtractor():
    def __init__(self):
        self.instance_id = 0

    def extract_instances(self, sheet_image):
        pass

    def pad_instance(self, instance_image):
        pass

    def save_instance(self, image):
        pass

    def process_folder(self, input_path, output_path):
        self.instance_id = 0
        self.input_path = input_path
        self.output_path = output_path
        ## TODO List sheets in input folder
        sheet_paths = []
        for sheet_path in sheet_paths:
            # TODO Load image
            # Extract instances
            instances = self.extract_instances(sheet)
            for instance in instances:
                # Pad to equal size
                padded_instance = self.pad_instance(instance)
                # Save instance
                self.save_instance(padded_instance)