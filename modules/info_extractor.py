from transformers import pipeline
import re

class InfoExtractor:
    def __init__(self):
        # Initialize the NER pipeline for identifying entities
        self.ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
        
    def extract_info(self, text):
        """
        Extract structured information from the OCR text
        """
        try:
            # Split text into lines
            lines = text.split('\n')
            results = []
            
            # Process each line
            for line in lines:
                if not line.strip():
                    continue
                    
                # Use NER to identify potential entities
                entities = self.ner_pipeline(line)
                
                # Process the entities and create structured data
                processed_data = self._process_entities(line, entities)
                
                if processed_data:
                    results.extend(processed_data)
            
            # Add additional processing for common document fields
            self._add_common_fields(text, results)
            
            return results
            
        except Exception as e:
            raise Exception(f"Error in information extraction: {str(e)}")
    
    def _process_entities(self, line, entities):
        """
        Process identified entities and create structured data
        """
        results = []
        
        # Process entities identified by the model
        if entities:
            for entity in entities:
                results.append({
                    'label': entity['entity'],
                    'value': entity['word'],
                    'remarks': f"Confidence: {entity['score']:.2f}"
                })
        
        # Look for key-value pairs in the line
        kv_match = re.match(r'^([^:]+):\s*(.+)$', line)
        if kv_match:
            label, value = kv_match.groups()
            results.append({
                'label': label.strip(),
                'value': value.strip(),
                'remarks': 'Key-value pair'
            })
            
        return results
    
    def _add_common_fields(self, text, results):
        """
        Add common document fields like dates, amounts, invoice numbers, etc.
        """
        # Look for dates
        date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'
        dates = re.findall(date_pattern, text)
        for date in dates:
            if not any(r['label'] == 'Date' and r['value'] == date for r in results):
                results.append({
                    'label': 'Date',
                    'value': date,
                    'remarks': 'Date format detected'
                })
        
        # Look for amounts/prices
        amount_pattern = r'\$?\s*\d+(?:,\d{3})*(?:\.\d{2})?\b'
        amounts = re.findall(amount_pattern, text)
        for amount in amounts:
            if not any(r['label'] == 'Amount' and r['value'] == amount for r in results):
                results.append({
                    'label': 'Amount',
                    'value': amount,
                    'remarks': 'Currency amount detected'
                })
        
        # Look for invoice/order numbers
        invoice_pattern = r'\b(?:INV|INVOICE|ORDER|PO)[:#-]?\s*\d+\b'
        invoices = re.findall(invoice_pattern, text, re.IGNORECASE)
        for invoice in invoices:
            if not any(r['label'] == 'Reference Number' and r['value'] == invoice for r in results):
                results.append({
                    'label': 'Reference Number',
                    'value': invoice,
                    'remarks': 'Invoice/Order number detected'
                })
        
        # Look for email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in emails:
            if not any(r['label'] == 'Email' and r['value'] == email for r in results):
                results.append({
                    'label': 'Email',
                    'value': email,
                    'remarks': 'Email address detected'
                })
        
        # Look for phone numbers
        phone_pattern = r'\b(?:\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        for phone in phones:
            if not any(r['label'] == 'Phone' and r['value'] == phone for r in results):
                results.append({
                    'label': 'Phone',
                    'value': phone,
                    'remarks': 'Phone number detected'
                })
        
        return results
