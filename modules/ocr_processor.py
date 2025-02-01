import cv2
import pytesseract
import numpy as np
import os
from PIL import Image

class OCRProcessor:
    def __init__(self):
        # Set Tesseract path for Windows
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
    def preprocess_image(self, image):
        """
        Preprocess the image to improve OCR accuracy
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply dilation to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        gray = cv2.dilate(gray, kernel, iterations=1)
        
        # Apply median blur to remove noise
        gray = cv2.medianBlur(gray, 3)
        
        return gray
        
    def process_image(self, image_path):
        """
        Process the image and extract text using OCR
        """
        try:
            # Read image using opencv
            image = cv2.imread(image_path)
            
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Perform OCR on the processed image
            custom_config = r'--oem 3 --psm 6'
            extracted_text = pytesseract.image_to_string(processed_image, config=custom_config)
            
            return extracted_text.strip()
            
        except Exception as e:
            raise Exception(f"Error in OCR processing: {str(e)}")
