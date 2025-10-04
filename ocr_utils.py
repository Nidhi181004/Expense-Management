"""
OCR Utilities for Receipt Processing
This module provides functionality to extract expense information from receipt images
"""

import pytesseract
from PIL import Image
import re
from datetime import datetime
import os

class ReceiptOCR:
    def __init__(self):
        # Configure tesseract path if needed (Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Common expense categories and their keywords
        self.category_keywords = {
            'meals': ['restaurant', 'cafe', 'food', 'dining', 'lunch', 'dinner', 'breakfast'],
            'travel': ['taxi', 'uber', 'lyft', 'hotel', 'airline', 'flight', 'gas', 'fuel'],
            'office_supplies': ['office', 'supplies', 'staples', 'paper', 'pen', 'printer'],
            'software': ['software', 'subscription', 'saas', 'license', 'microsoft', 'adobe'],
            'training': ['training', 'course', 'seminar', 'workshop', 'conference'],
            'other': []
        }
        
        # Currency symbols and patterns
        self.currency_patterns = {
            'USD': [r'\$', r'USD', r'US\$'],
            'EUR': [r'€', r'EUR'],
            'GBP': [r'£', r'GBP'],
            'INR': [r'₹', r'INR', r'Rs\.?'],
            'JPY': [r'¥', r'JPY'],
            'CAD': [r'CAD', r'C\$'],
            'AUD': [r'AUD', r'A\$']
        }

    def extract_text_from_image(self, image_path):
        """Extract text from image using OCR"""
        try:
            image = Image.open(image_path)
            # Preprocess image for better OCR results
            image = self.preprocess_image(image)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""

    def preprocess_image(self, image):
        """Preprocess image to improve OCR accuracy"""
        # Convert to grayscale
        image = image.convert('L')
        
        # Resize if too small
        width, height = image.size
        if width < 800:
            scale_factor = 800 / width
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image

    def extract_amount(self, text):
        """Extract monetary amount from text"""
        # Pattern to match currency amounts
        amount_patterns = [
            r'(?:total|amount|sum)[\s:]*([£$€₹¥]?\s*\d+[.,]\d{2})',
            r'([£$€₹¥]\s*\d+[.,]\d{2})',
            r'(\d+[.,]\d{2})\s*(?:USD|EUR|GBP|INR|JPY|CAD|AUD)',
            r'(?:^|\s)(\d+[.,]\d{2})(?:\s|$)'
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Clean up the amount
                amount_str = re.sub(r'[^\d.,]', '', match)
                amount_str = amount_str.replace(',', '.')
                try:
                    amount = float(amount_str)
                    if 0.01 <= amount <= 10000:  # Reasonable range
                        amounts.append(amount)
                except ValueError:
                    continue
        
        # Return the largest amount found (likely to be the total)
        return max(amounts) if amounts else None

    def extract_currency(self, text):
        """Extract currency from text"""
        for currency, patterns in self.currency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return currency
        return 'USD'  # Default currency

    def extract_date(self, text):
        """Extract date from text"""
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{2,4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(\w+\s+\d{1,2},?\s+\d{2,4})',
            r'(\d{1,2}\s+\w+\s+\d{2,4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    # Try different date formats
                    date_formats = ['%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', 
                                  '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d',
                                  '%B %d, %Y', '%d %B %Y']
                    
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(match, fmt)
                            # Check if date is reasonable (not too far in future/past)
                            if 2020 <= parsed_date.year <= datetime.now().year + 1:
                                return parsed_date.date()
                        except ValueError:
                            continue
                except:
                    continue
        
        # Default to today if no date found
        return datetime.now().date()

    def extract_merchant(self, text):
        """Extract merchant/vendor name from text"""
        lines = text.split('\n')
        # Usually the merchant name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3 and not re.match(r'^\d+', line):
                # Filter out common receipt headers
                if not any(word in line.lower() for word in ['receipt', 'invoice', 'bill', 'tax', 'total']):
                    return line
        return "Unknown Merchant"

    def categorize_expense(self, text):
        """Categorize expense based on text content"""
        text_lower = text.lower()
        
        for category, keywords in self.category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return category.replace('_', ' ').title()
        
        return "Other"

    def process_receipt(self, image_path):
        """Process receipt image and extract expense information"""
        try:
            # Extract text from image
            text = self.extract_text_from_image(image_path)
            
            if not text.strip():
                return {
                    'success': False,
                    'error': 'Could not extract text from image'
                }
            
            # Extract information
            amount = self.extract_amount(text)
            currency = self.extract_currency(text)
            date = self.extract_date(text)
            merchant = self.extract_merchant(text)
            category = self.categorize_expense(text)
            
            # Generate title
            title = f"{merchant} - {category}"
            if len(title) > 50:
                title = title[:47] + "..."
            
            # Generate description
            description = f"Expense at {merchant}"
            
            return {
                'success': True,
                'data': {
                    'title': title,
                    'description': description,
                    'amount': amount,
                    'currency': currency,
                    'expense_date': date.isoformat() if date else datetime.now().date().isoformat(),
                    'merchant': merchant,
                    'category': category,
                    'raw_text': text
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing receipt: {str(e)}'
            }

# Mock OCR for development/testing when tesseract is not available
class MockReceiptOCR:
    """Mock OCR implementation for testing purposes"""
    
    def process_receipt(self, image_path):
        """Mock receipt processing that returns sample data"""
        import random
        
        merchants = [
            "The Gourmet Restaurant",
            "Coffee Corner Cafe",
            "Office Supply Store",
            "Tech Solutions Inc",
            "Downtown Hotel",
            "City Taxi Service"
        ]
        
        categories = ["Meals", "Travel", "Office Supplies", "Software", "Training", "Other"]
        currencies = ["USD", "EUR", "GBP", "INR"]
        
        merchant = random.choice(merchants)
        category = random.choice(categories)
        currency = random.choice(currencies)
        amount = round(random.uniform(10.0, 500.0), 2)
        
        return {
            'success': True,
            'data': {
                'title': f"{merchant} - {category}",
                'description': f"Expense at {merchant}",
                'amount': amount,
                'currency': currency,
                'expense_date': datetime.now().date().isoformat(),
                'merchant': merchant,
                'category': category,
                'raw_text': f"Mock OCR text for {merchant}"
            }
        }

# Factory function to get appropriate OCR instance
def get_ocr_instance():
    """Get OCR instance based on availability of tesseract"""
    try:
        # Try to import and use real OCR
        import pytesseract
        return ReceiptOCR()
    except ImportError:
        # Fall back to mock OCR
        return MockReceiptOCR()
