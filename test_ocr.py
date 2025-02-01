import os
from modules.ocr_processor import OCRProcessor
from modules.info_extractor import InfoExtractor
from create_test_image import create_sample_invoice

def test_ocr_extraction():
    # Create a sample invoice image
    image_path = create_sample_invoice()
    
    try:
        # Initialize processors
        ocr_processor = OCRProcessor()
        info_extractor = InfoExtractor()
        
        print("\nProcessing image:", image_path)
        print("\n1. Extracting text using OCR...")
        # Extract text using OCR
        extracted_text = ocr_processor.process_image(image_path)
        print("\nExtracted Text:")
        print("-" * 50)
        print(extracted_text)
        print("-" * 50)
        
        print("\n2. Extracting structured information...")
        # Extract structured information
        extracted_info = info_extractor.extract_info(extracted_text)
        
        print("\nExtracted Information:")
        print("-" * 50)
        print(f"{'Label':<20} | {'Value':<30} | {'Remarks'}")
        print("-" * 80)
        for item in extracted_info:
            print(f"{item['label']:<20} | {item['value']:<30} | {item['remarks']}")
        
    except Exception as e:
        print(f"\nError during processing: {str(e)}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_ocr_extraction()
