import os
import base64
from typing import Dict, Any, List
import json
import requests
from PIL import Image
import io

class AIInfoExtractor:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def encode_image(self, image_path: str) -> str:
        """Convert image to base64 string"""
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large (max 2048 pixels in either dimension)
            max_size = 2048
            if img.width > max_size or img.height > max_size:
                ratio = min(max_size/img.width, max_size/img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Refilter.LANCZOS)
            
            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def extract_info(self, image_path: str) -> List[Dict[str, str]]:
        """
        Extract information from any transactional document using AI vision model
        Returns a list of dictionaries with label, value, and remarks for each extracted piece of information
        """
        try:
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Prepare the prompt
            prompt = """Analyze this transactional document (which could be an invoice, bill, sales order, purchase order, etc.) and extract all relevant information.

For each piece of information you find:
1. Identify what the information represents (the label)
2. Extract its corresponding value
3. Add any relevant remarks about the information (e.g., confidence level, data type, unit of measurement)

Present the information as a list of JSON objects, where each object has these fields:
- label: What this information represents (e.g., "Invoice Number", "Total Amount", "Customer Name", etc.)
- value: The actual value found in the document
- remarks: Any relevant notes about this information

Be intelligent in determining what information is important. Look for:
- Document identifiers (any reference numbers, dates, etc.)
- Monetary amounts and calculations
- Quantities and measurements
- Names and contact information
- Product or service details
- Any other relevant business information

Format numbers appropriately (e.g., monetary values as decimals). Include units in the remarks rather than the value field.

Example format:
[
    {
        "label": "Document Type",
        "value": "Sales Invoice",
        "remarks": "Determined from document header"
    },
    {
        "label": "Reference Number",
        "value": "INV-12345",
        "remarks": "Found in top right corner"
    }
]"""

            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/",  # Required by OpenRouter
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }

            # Make the API request
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            # Extract the response
            result = response.json()
            
            # Debug print
            print("API Response:", result)
            
            # Get the content from the response
            if isinstance(result, dict) and 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
            else:
                raise Exception("Unexpected API response format")
            
            # Parse the JSON response
            try:
                # Try to extract JSON from the response
                # Find the first '[' and last ']' to extract the JSON array
                start_idx = content.find('[')
                end_idx = content.rfind(']')
                
                if start_idx == -1 or end_idx == -1:
                    raise Exception("No JSON array found in response")
                
                json_str = content[start_idx:end_idx + 1]
                extracted_data = json.loads(json_str)
                
                if not isinstance(extracted_data, list):
                    raise Exception("Extracted data is not a list")
                
                # Validate and clean the extracted data
                return self._clean_extracted_data(extracted_data)
                
            except json.JSONDecodeError as e:
                print("JSON Decode Error:", str(e))
                print("Content:", content)
                raise Exception("Failed to parse AI response as JSON")
            
        except Exception as e:
            print(f"Error extracting information: {str(e)}")
            return []
    
    def _clean_extracted_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Clean and validate the extracted data"""
        cleaned = []
        
        try:
            for item in data:
                if isinstance(item, dict) and 'label' in item and 'value' in item:
                    cleaned_item = {
                        'label': str(item.get('label', '')).strip(),
                        'value': str(item.get('value', '')).strip(),
                        'remarks': str(item.get('remarks', '')).strip()
                    }
                    if cleaned_item['label'] and cleaned_item['value']:  # Only include items with both label and value
                        cleaned.append(cleaned_item)
            
        except Exception as e:
            print(f"Error cleaning data: {str(e)}")
        
        return cleaned
