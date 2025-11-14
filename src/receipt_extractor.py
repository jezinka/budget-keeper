"""
Module for extracting item-level details from receipt emails.
"""
import logging
import re
from base64 import urlsafe_b64decode
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup


class ReceiptExtractor:
    """Extracts item descriptions and details from receipt emails"""
    
    def extract_items_from_message(self, message: Dict[str, Any]) -> List[str]:
        """
        Extract item descriptions from a receipt email message.
        
        Args:
            message: Gmail message dictionary
            
        Returns:
            List of item descriptions found in the receipt
        """
        payload = message.get('payload', {})
        
        # Try HTML parsing first (more structured)
        html_body = self._get_html_body(payload)
        if html_body:
            items = self._extract_from_html(html_body)
            if items:
                logging.info(f'Extracted {len(items)} items from HTML')
                return items
        
        # Fallback to plain text parsing
        text_body = self._get_text_body(payload)
        if text_body:
            items = self._extract_from_text(text_body)
            logging.info(f'Extracted {len(items)} items from text')
            return items
        
        return []
    
    def _get_html_body(self, payload: Dict[str, Any]) -> Optional[str]:
        """Extract HTML body from message payload"""
        # Check if body is directly in payload
        if 'body' in payload and 'data' in payload['body']:
            mime_type = payload.get('mimeType', '')
            if 'html' in mime_type.lower():
                return urlsafe_b64decode(payload['body']['data']).decode('utf-8', 'replace')
        
        # Check parts for HTML content
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                if 'html' in mime_type.lower() and 'body' in part and 'data' in part['body']:
                    return urlsafe_b64decode(part['body']['data']).decode('utf-8', 'replace')
                
                # Recursively check nested parts
                if 'parts' in part:
                    html = self._get_html_body(part)
                    if html:
                        return html
        
        return None
    
    def _get_text_body(self, payload: Dict[str, Any]) -> Optional[str]:
        """Extract plain text body from message payload"""
        # Check if body is directly in payload
        if 'body' in payload and 'data' in payload['body']:
            mime_type = payload.get('mimeType', '')
            if 'text/plain' in mime_type.lower() or 'text' in mime_type.lower():
                return urlsafe_b64decode(payload['body']['data']).decode('utf-8', 'replace')
        
        # Check parts for text content
        if 'parts' in payload:
            text_parts = []
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                if 'text/plain' in mime_type.lower() and 'body' in part and 'data' in part['body']:
                    text_parts.append(urlsafe_b64decode(part['body']['data']).decode('utf-8', 'replace'))
                
                # Recursively check nested parts
                if 'parts' in part:
                    text = self._get_text_body(part)
                    if text:
                        text_parts.append(text)
            
            if text_parts:
                return '\n'.join(text_parts)
        
        return None
    
    def _extract_from_html(self, html_body: str) -> List[str]:
        """
        Extract item descriptions from HTML using BeautifulSoup.
        
        Args:
            html_body: HTML content of email
            
        Returns:
            List of item descriptions
        """
        items = []
        
        try:
            soup = BeautifulSoup(html_body, 'html.parser')
            
            # Strategy 1: Look for table rows with product information
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    for cell in cells:
                        text = cell.get_text(strip=True)
                        # Look for product-like descriptions (longer text, not just numbers)
                        if len(text) > 15 and not self._is_just_numbers(text):
                            items.append(text)
            
            # Strategy 2: Look for paragraphs with product-like content
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Look for text that mentions product or contains descriptive content
                if len(text) > 15 and not self._is_just_numbers(text):
                    # Check if contains product keywords or looks descriptive
                    if any(kw in text.lower() for kw in ['produkt', 'nazwa', 'towar', 'artykuł']):
                        items.append(text)
                    elif re.search(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{3,}.*[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{3,}', text):
                        # Has multiple words (descriptive)
                        items.append(text)
            
            # Strategy 3: Look for list items
            list_items = soup.find_all('li')
            for li in list_items:
                text = li.get_text(strip=True)
                if len(text) > 15 and not self._is_just_numbers(text):
                    items.append(text)
            
        except Exception as e:
            logging.error(f'Error parsing HTML: {e}')
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(items))
    
    def _extract_from_text(self, text_body: str) -> List[str]:
        """
        Extract item descriptions from plain text.
        
        Args:
            text_body: Plain text content of email
            
        Returns:
            List of item descriptions
        """
        items = []
        
        # Split into lines
        lines = text_body.split('\n')
        
        # Look for lines that appear to be product descriptions
        product_keywords = ['produkt', 'nazwa', 'towar', 'artykuł', 'szczegóły', 'opis']
        
        found_product_section = False
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're in a product section
            if any(keyword in line_lower for keyword in product_keywords):
                found_product_section = True
                # Look at the next few lines for actual product info
                for j in range(i+1, min(i+10, len(lines))):
                    next_line = lines[j].strip()
                    if len(next_line) > 20 and not self._is_just_numbers(next_line):
                        items.append(next_line)
                        break
            
            # Also look for long descriptive lines (likely product names)
            elif len(line.strip()) > 30 and not self._is_just_numbers(line):
                # Check if it looks like a product description
                # (contains letters and possibly numbers, not just metadata)
                if re.search(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{3,}', line):
                    items.append(line.strip())
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(items))
    
    def _is_just_numbers(self, text: str) -> bool:
        """
        Check if text is just numbers, dates, or prices.
        
        Args:
            text: Text to check
            
        Returns:
            True if text is just numeric/date/price data
        """
        # Remove common numeric patterns
        cleaned = re.sub(r'[\d.,\s€$£¥zł\-:/]+', '', text)
        # If very little remains, it's probably just numbers
        return len(cleaned) < 5
    
    def extract_all_details(self, messages: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Extract item details from multiple messages.
        
        Args:
            messages: List of Gmail message dictionaries
            
        Returns:
            Dictionary mapping message IDs to lists of item descriptions
        """
        results = {}
        
        for message in messages:
            msg_id = message.get('id', 'unknown')
            items = self.extract_items_from_message(message)
            if items:
                results[msg_id] = items
        
        return results
