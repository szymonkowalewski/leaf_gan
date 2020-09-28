# Script for extracting single leaves form a sheet with multiple samples
import cv2
import os
import math
import numpy as np

class InstanceExtractor():
    def __init__(self):
        self.instance_id = 0
        self.background_color = (255,255,255)        

    def direction(self, centered_instance_image):
        # TODO implement something faster
        # Convert to grayscale
        gray_img = cv2.cvtColor(centered_instance_image, cv2.COLOR_BGR2GRAY)
        # Thresh to 1 for histogram
        ret,thresh_img = cv2.threshold(gray_img,200,1,cv2.THRESH_BINARY_INV)
        # Calculate histogram and see on which padding is larger
        # This defines direction
        # Replace with some better histogram analysis 
        histogram = np.sum(thresh_img, axis=0)
        for i in range(0, int(len(histogram/2))):
            if histogram[i] != 0:
                return 1
            if histogram[len(histogram)-1-i] != 0:
                return 0

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
                # Prepare blank instance image
                instance_img = 255*np.ones((stat[cv2.CC_STAT_HEIGHT],
                                           stat[cv2.CC_STAT_WIDTH],3), np.uint8)
                # Find component indices
                indices = np.where(label_img == idx)
                # Copy pixels
                for indice in zip(indices[0], indices[1]):
                    instance_img[indice[0] - stat[cv2.CC_STAT_TOP],indice[1] - stat[cv2.CC_STAT_LEFT],:] = sheet_image[indice[0],indice[1],:]
                extracted_instances.append(instance_img)
        return extracted_instances

    def pad_center_instance(self, instance_image, target_size=(200,200)):
        # Center of target image
        img_cent_row = int(target_size[0]/2)
        img_cent_col = int(target_size[1]/2)

        # Pad to target size
        padded_image = cv2.copyMakeBorder(instance_image,target_size[0] - instance_image.shape[0], 0,
                                                         target_size[1] - instance_image.shape[1], 0,
                                                         cv2.BORDER_CONSTANT,value=self.background_color)
        
        # Extract binary mask (not optimal as this operation was already done in extract_instances)
        gray_img = cv2.cvtColor(padded_image, cv2.COLOR_BGR2GRAY)
        ret,thresh_img = cv2.threshold(gray_img,200,255,cv2.THRESH_BINARY_INV)        
        
        # Calculate moments, centroid and orientation
        moments = cv2.moments(thresh_img)
        centroid_col = moments["m10"]/moments["m00"]
        centroid_row = moments["m01"]/moments["m00"]
        orientation = 0.5*math.atan((2*moments["nu11"])/(moments["nu20"]-moments["nu02"]))
        if moments["nu20"]<moments["nu02"]:
            orientation += math.pi/2

        # Prepare affine transforms: move centroid to image center, rotate to 0
        t_matrix = np.float32([ [1,0,img_cent_col-centroid_col], [0,1,img_cent_row-centroid_row]])
        rot_matrix = cv2.getRotationMatrix2D((img_cent_col, img_cent_row),math.degrees(orientation),1)
        # Apply transformations
        t_image = cv2.warpAffine(padded_image, t_matrix, (target_size[1], target_size[0]), borderValue=self.background_color)
        t_rot_image = cv2.warpAffine(t_image, rot_matrix, (target_size[1], target_size[0]), borderValue=self.background_color)

        # Flip if wrong direction
        if self.direction(t_rot_image):
            t_rot_image = cv2.flip(t_rot_image, 1)

        return t_rot_image

    def save_instance(self, image):
        print("Finished instance " + str(self.instance_id))
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
                padded_instance = self.pad_center_instance(instance)
                # Save instance
                self.save_instance(padded_instance)