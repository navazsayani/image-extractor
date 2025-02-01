# Document Information Extractor

A web application that intelligently extracts key information from uploaded images of transactional documents (bills, invoices, sales orders, etc.) using OCR and machine learning.

## Features

- Upload and process various image formats (PNG, JPG, JPEG, GIF, TIFF, BMP)
- Image preprocessing for improved OCR accuracy
- Text extraction using Tesseract OCR
- Intelligent information extraction using NLP and machine learning
- Structured output in a tabular format
- Responsive web interface

## Prerequisites

1. Python 3.7 or higher
2. Tesseract OCR:
   - Windows:
     1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
     2. Install Tesseract to: `C:\Program Files\Tesseract-OCR`
     3. Add the installation path to your system's PATH environment variable
   - Linux: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd image-extractor
```

2. Create a virtual environment and activate it:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Upload an image of a document (supported formats: PNG, JPG, JPEG, GIF, TIFF, BMP)

4. View the extracted information in a structured table format

## Testing

1. Create and process a test image:
```bash
python test_ocr.py
```

This will:
- Generate a sample invoice image
- Process it using OCR
- Extract structured information
- Display the results

## Project Structure

```
image-extractor/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── create_test_image.py  # Test image generator
├── test_ocr.py          # OCR testing script
├── modules/
│   ├── ocr_processor.py  # OCR processing module
│   └── info_extractor.py # Information extraction module
├── static/
│   └── css/
│       └── style.css     # Application styles
├── templates/
│   ├── index.html        # Upload page template
│   └── results.html      # Results page template
└── uploads/              # Temporary folder for uploaded files
```

## Troubleshooting

1. Tesseract OCR not found:
   - Ensure Tesseract is installed correctly
   - Verify the installation path matches the one in `modules/ocr_processor.py`
   - Add Tesseract to your system PATH
   - Windows: Set the `TESSERACT_CMD` environment variable to point to tesseract.exe

2. Model download issues:
   - Ensure you have a stable internet connection for the first run
   - The Hugging Face transformer model will be downloaded automatically

3. Memory issues:
   - Consider reducing the maximum file size in app.py
   - Adjust the image preprocessing parameters in ocr_processor.py

## Potential Improvements

1. Add support for PDF documents
2. Implement batch processing
3. Add custom training for specific document types
4. Implement document type classification
5. Add export functionality (CSV, JSON, etc.)
6. Implement caching for better performance
7. Add user authentication and document management
8. Implement API endpoints for programmatic access

## License

This project is licensed under the MIT License - see the LICENSE file for details.
