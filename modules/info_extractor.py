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
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def encode_image(self, image_path: str) -> str:
        """Convert image to base64 string"""
        try:
            with Image.open(image_path) as img:
                print(f"Image opened successfully: {image_path}")
                print(f"Image size: {img.size}, mode: {img.mode}")
                
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    print("Converted image to RGB mode")
                
                # Resize if too large (max 2048 pixels in either dimension)
                max_size = 2048
                if img.width > max_size or img.height > max_size:
                    ratio = min(max_size/img.width, max_size/img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Refilter.LANCZOS)
                    print(f"Resized image to: {new_size}")
                
                # Convert to base64
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
                print(f"Image successfully encoded to base64 (length: {len(base64_image)})")
                return base64_image
        except Exception as e:
            print(f"Error encoding image: {str(e)}")
            raise

    def extract_info(self, image_path: str) -> List[Dict[str, str]]:
        """
        Extract information from any transactional document using AI vision model
        Returns a list of dictionaries with label, value, and remarks for each extracted piece of information
        """
        try:
            print(f"\nStarting extraction for image: {image_path}")
            
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Prepare the prompt
            prompt = """Analyze this transactional document and extract all relevant information.

For each piece of information you find:
1. Identify what the information represents (the label)
2. Extract its corresponding value
3. Add any relevant remarks about the information

Look for any important business information such as:
- Document identifiers (reference numbers, dates)
- Monetary amounts and calculations
- Names and contact information
- Product or service details
- Any other relevant information

Return the information as a list of JSON objects with these fields:
- label: What this information represents
- value: The actual value found
- remarks: Any relevant notes

Example format:
[
    {
        "label": "Document Type",
        "value": "Sales Invoice",
        "remarks": "Determined from document header"
    }
]"""

            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4o-mini",
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

            print("Making API request to OpenRouter...")
            
            # Make the API request
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            # Extract the response
            result = response.json()
            print("\nAPI Response received:")
            print(json.dumps(result, indent=2))
            
            # Get the content from the response
            if isinstance(result, dict) and 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                print("\nExtracted content:", content)
            else:
                print("\nUnexpected API response format")
                raise Exception("Unexpected API response format")
            
            # Parse the JSON response
            try:
                # Find the first '[' and last ']' to extract the JSON array
                start_idx = content.find('[')
                end_idx = content.rfind(']')
                
                if start_idx == -1 or end_idx == -1:
                    print("\nNo JSON array found in response")
                    raise Exception("No JSON array found in response")
                
                json_str = content[start_idx:end_idx + 1]
                print("\nExtracted JSON string:", json_str)
                
                extracted_data = json.loads(json_str)
                
                if not isinstance(extracted_data, list):
                    print("\nExtracted data is not a list")
                    raise Exception("Extracted data is not a list")
                
                # Validate and clean the extracted data
                cleaned_data = self._clean_extracted_data(extracted_data)
                print("\nCleaned data:", json.dumps(cleaned_data, indent=2))
                
                return cleaned_data
                
            except json.JSONDecodeError as e:
                print(f"\nJSON Decode Error: {str(e)}")
                print("Content:", content)
                raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
            
        except Exception as e:
            print(f"\nError in extract_info: {str(e)}")
            return []
    
    def _clean_extracted_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Clean and validate the extracted data"""
        cleaned = []
        
        try:
            print("\nCleaning extracted data...")
            for item in data:
                if isinstance(item, dict) and 'label' in item and 'value' in item:
                    cleaned_item = {
                        'label': str(item.get('label', '')).strip(),
                        'value': str(item.get('value', '')).strip(),
                        'remarks': str(item.get('remarks', '')).strip()
                    }
                    if cleaned_item['label'] and cleaned_item['value']:  # Only include items with both label and value
                        cleaned.append(cleaned_item)
                        print(f"Added cleaned item: {cleaned_item}")
            
        except Exception as e:
            print(f"Error cleaning data: {str(e)}")
        
        print(f"\nReturning {len(cleaned)} cleaned items")
        return cleaned
