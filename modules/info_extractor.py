import os
import base64
from typing import Dict, Any, List
import json
import requests
from PIL import Image, UnidentifiedImageError
import io
import PIL
from google import genai

class AIInfoExtractor:
    MODELS = {
        # "gemini-flash": {
        #     "name": "google/gemini-flash-1.5",  # Updated model name
        #     "url": "https://openrouter.ai/api/v1/chat/completions",
        #     "needs_key": "OPENROUTER_API_KEY"
        # },
        "gemini-flash": {
            "name": "gemini-1.5-flash",  # Google AI Studio model name
            "url": None,  # Not needed for Google AI Studio
            "needs_key": "GOOGLE_API_KEY"
        },
        "gemini-flash-2.0": {
            "name": "gemini-2.0-flash",  # Google AI Studio model name
            "url": None,  # Not needed for Google AI Studio
            "needs_key": "GOOGLE_API_KEY"
        },
        "gpt4-mini": {
            "name": "gpt-4o-mini",
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "needs_key": "OPENROUTER_API_KEY"
        },
    }

    def encode_image(self, image_path: str) -> str:
        """Convert image to base64 string"""
        if not os.path.exists(image_path):
            raise Exception("Image file not found")
            
        file_size = os.path.getsize(image_path)
        if file_size > 15 * 1024 * 1024:  # 15MB limit
            raise Exception("Image file is too large (max 15MB)")
            
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
                    img = img.resize(new_size, Image.LANCZOS)
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

    def __init__(self, model_choice="gpt4-mini"):
        if model_choice not in self.MODELS:
            raise ValueError(f"Invalid model choice. Available models: {', '.join(self.MODELS.keys())}")
            
        self.model_choice = model_choice  # Store model choice for reference
        model_config = self.MODELS[model_choice]
        self.model = model_config["name"]
        self.api_url = model_config["url"]
        
        # Get API key
        self.api_key = os.getenv(model_config["needs_key"])
        if not self.api_key:
            raise ValueError(f"{model_config['needs_key']} environment variable is required")
            
        # Configure Google AI if using Gemini models
        if "gemini" in model_choice:
             # genai.configure(api_key=self.api_key)
             self.client = genai.Client(api_key=self.api_key)
    def extract_info_google_ai(self, image_path: str, prompt: str) -> List[Dict[str, str]]:
        """Extract information using Google AI Studio approach for Gemini models"""
        try:
            
            # Set model configuration based on version
            # generation_config = {
            #     'temperature': 0.1,
            #     'top_p': 0.8,
            #     'top_k': 40,
            # }
            
            # Add specific configurations for 2.0
            # if self.model_choice == "gemini-flash-2.0":
            #     generation_config.update({
            #         'temperature': 0.05,  # More focused for 2.0
            #         'top_p': 0.9,
            #         'top_k': 50,
            #     })
            
            # Prepare the content parts
            content = [
                prompt,  # Text prompt
                Image.open(image_path)
                # genai.types.Image.from_bytes(
                #     base64.b64decode(base64_image)
                # )  # Image data
            ]
            
            # Generate response
            # response = model.generate_content(content)
            response = self.client.models.generate_content(
                model = self.model,
                contents = content
                )
            
            if not response.text:
                raise Exception("No response received from the model")
                
            content = response.text
            
            # Parse the JSON response (reuse existing JSON parsing logic)
            try:
                # Find the first '[' and last ']' to extract the JSON array
                start_idx = content.find('[')
                end_idx = content.rfind(']')
                
                if start_idx == -1 or end_idx == -1:
                    print("\nNo JSON array found in response")
                    if "```" in content:
                        raise Exception("Model returned markdown instead of JSON. Please try GPT-4 Mini model.")
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
                raise Exception("Model returned invalid JSON format. Please try GPT-4 Mini model.")
                
        except Exception as e:
            print(f"\nError in extract_info_google_ai: {str(e)}")
            raise Exception(str(e))

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

For line items (products/services):
- Extract each line item separately with sequential numbering
- For each line item, extract ALL available columns/fields present in the document, such as:
  * Product/service name
  * HSN/SAC code
  * Quantity and unit
  * Rate/price
  * Amount
  * Taxable value
  * Tax percentages (CGST%, SGST%, IGST%, etc.)
  * Tax amounts (CGST Amount, SGST Amount, IGST Amount, etc.)
  * Net amount
  * Any other columns specific to the document
- Include line number in all labels (e.g., "Line Item 1 - Product", "Line Item 1 - HSN/SAC", "Line Item 1 - CGST Amount")
- Do not combine multiple line items into a single entry
- Be thorough in capturing all columns present for each line item

For summary tables and totals:
- Extract all summary tables (e.g., HSN/SAC summary, tax summary)
- Capture row-wise details from summary tables
- Include table context in label (e.g., "HSN Summary - HSN Code", "HSN Summary - Taxable Value")
- Extract all total/subtotal rows with proper context

For party information (buyer/seller/other):
- Include party context in remarks for identifiers (PAN, GST, address)
- Clearly indicate which party each piece of information belongs to
- Distinguish between billing/shipping addresses if both present

Look for any important business information such as:
- Document identifiers (reference numbers, dates)
- Party details (with clear buyer/seller distinction)
- Contact information (with party context)
- Tax identification numbers (with party context)
- Line items (with ALL columns and details)
- Summary tables and their details
- Monetary amounts and calculations
- Payment/banking details
- Any other relevant information

Return the information as a list of JSON objects with these fields:
- label: What this information represents (include line numbers for line items)
- value: The actual value found
- remarks: Any relevant notes (include party context for identifiers)"""

            # Use Google AI Studio approach for Gemini models
            if "gemini" in self.model_choice:
                return self.extract_info_google_ai(image_path, prompt)
                
            # Use OpenRouter approach for GPT-4o-mini            
            # Prepare the OpenRouter API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
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

            print(f"\nSending request with data: {json.dumps(data, indent=2)}")
            
            # Make the API request
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            
            if response.status_code != 200:
                print(f"\nAPI Error Response: {response.text}")
                if "model not found" in response.text.lower():
                    raise Exception(f"Model '{self.model}' is not available. Please try a different model.")
                elif "unauthorized" in response.text.lower():
                    raise Exception("API key is invalid or expired. Please check your OPENROUTER_API_KEY.")
                response.raise_for_status()
            
            # Extract the response
            result = response.json()
            print("\nAPI Response received:")
            print(json.dumps(result, indent=2))
            
            # Get the content from the response
            if isinstance(result, dict) and 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                print("\nExtracted content:", content)
                
                # Try to clean the content if it contains markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                    print("\nCleaned content from markdown:", content)
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
                    if "```" in content:
                        raise Exception("Model returned markdown instead of JSON. Please try GPT-4 Mini model.")
                    raise Exception("No JSON array found in response")
                
                json_str = content[start_idx:end_idx + 1]
                print("\nExtracted JSON string:", json_str)
                
                try:
                    extracted_data = json.loads(json_str)
                except json.JSONDecodeError:
                    # Try to clean the string if initial parse fails
                    json_str = json_str.replace('\n', ' ').replace('\r', '')
                    json_str = ' '.join(json_str.split())  # Normalize whitespace
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
                raise Exception("Model returned invalid JSON format. Please try GPT-4 Mini model.")
            
        except requests.Timeout:
            print("API request timed out")
            raise Exception("Request timed out - please try again")
        except requests.RequestException as e:
            print(f"API request failed: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
        except PIL.UnidentifiedImageError:
            print("Could not identify image file")
            raise Exception("Invalid or corrupted image file")
        except Exception as e:
            print(f"\nError in extract_info: {str(e)}")
            raise Exception(str(e))
    
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
