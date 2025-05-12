# Document Information Extractor

A web application that intelligently extracts key information from uploaded images of transactional documents (bills, invoices, sales orders, etc.) using AI vision capabilities.
Preview here - https://image-extractor-production.up.railway.app/

## Features

- Upload and process various image formats (PNG, JPG, JPEG, GIF, TIFF, BMP)
- AI-powered information extraction using GPT-4 Vision through OpenRouter
- Intelligent recognition of:
  - Account numbers and invoice numbers
  - Labor details (names, rates, hours, amounts)
  - Material details (items, quantities, unit costs, amounts)
  - Subtotals and total amounts
- Handles varying invoice formats and layouts
- Structured output in a tabular format
- Responsive web interface

## Prerequisites

1. Python 3.7 or higher
2. OpenRouter API key (get one from https://openrouter.ai/keys)

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

4. Set up your environment:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenRouter API key
# OPENROUTER_API_KEY=your_api_key_here
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Upload an image of a document (supported formats: PNG, JPG, JPEG, GIF, TIFF, BMP)

4. View the extracted information in a structured table format

## How It Works

1. **Image Upload**: Users upload invoice images through the web interface.

2. **AI Processing**: The application uses GPT-4 Vision through OpenRouter to:
   - Analyze the image content
   - Identify key information and data structures
   - Extract relevant details in a structured format

3. **Data Extraction**: The system intelligently extracts:
   - Document identifiers (account numbers, invoice numbers)
   - Labor information (worker details, rates, hours)
   - Material details (items, quantities, costs)
   - Financial totals and subtotals

4. **Result Display**: Extracted information is presented in a clean, organized format.

## Project Structure

```
image-extractor/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .env.example          # Example environment variables
├── modules/
│   └── info_extractor.py # AI-powered information extraction
├── static/
│   └── css/
│       └── style.css     # Application styles
├── templates/
│   ├── index.html        # Upload page template
│   └── results.html      # Results page template
└── uploads/              # Temporary folder for uploaded files
```

## Troubleshooting

1. API Key Issues:
   - Ensure your OpenRouter API key is correctly set in the .env file
   - Verify the API key has sufficient credits/permissions

2. Image Processing Issues:
   - Ensure images are clear and readable
   - Check that file size is under the 16MB limit
   - Verify the image format is supported

3. Extraction Accuracy:
   - For best results, use clear, well-lit images
   - Ensure important information is clearly visible
   - Try different angles if certain details are not being captured

## Potential Improvements

1. Add support for PDF documents
2. Implement batch processing
3. Add custom training for specific document types
4. Implement document type classification
5. Add export functionality (CSV, JSON, etc.)
6. Implement caching for better performance
7. Add user authentication and document management
8. Implement API endpoints for programmatic access
9. Add support for more document types
10. Implement result validation and correction interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.
